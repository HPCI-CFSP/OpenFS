#!/usr/bin/env python3
"""Expand decision-oriented catalog profiles from reviewed public roadmaps.

This generator deliberately reuses the roadmap tracks as the evidence-bearing
source of truth.  It does not invent missing dates: an absent public milestone
becomes a contested item and an explicit Coverage Gap.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = ROOT / "knowledge/public/topic-decision-support.json"
BASELINE_PATH = ROOT / "config/research-baseline.json"
I18N_PATH = ROOT / "config/publication-i18n.json"
ROADMAP_DIR = ROOT / "knowledge/public/roadmaps"

PROTECTED_PROFILES = {"ARCH-02", "ARCH-03", "SSW-01", "SSW-02", "SSW-04"}

# Every partially researched catalog item must map to reviewed roadmap tracks.
# Existing hand-curated profiles remain authoritative and are not regenerated.
TOPIC_TRACKS: dict[str, list[str]] = {
    "ARCH-01": ["COMPUTE-CPU", "COMPUTE-GPU", "COMPUTE-RACK"],
    "ARCH-04": ["NET-ETHERNET", "NET-SCALEUP", "NET-CPO"],
    "ARCH-05": ["COMPUTE-RACK", "NET-IOFABRIC"],
    "ARCH-06": ["BLUE-FACILITY", "COMPUTE-HPCI-EVAL"],
    "SSW-03": ["PORT-COMMS"],
    "SSW-05": ["BLUE-ESTATE", "NET-IOWN"],
    "SSW-06": ["BLUE-POLICY", "BLUE-HPCI-GATES"],
    "SSW-07": ["WORK-CB", "WORK-MODELS"],
    "SSW-08": ["PORT-HPCI-EVAL", "BLUE-HPCI-GATES"],
    "SSW-09": ["WORK-AI", "BLUE-POLICY"],
    "APP-01": ["WORK-EEA", "WORK-HPCI-EVAL"],
    "APP-02": ["WORK-SYSTEM", "WORK-CB", "WORK-MODELS"],
    "APP-03": ["WORK-AI", "WORK-EEA"],
    "APP-04": ["WORK-AGENT"],
    "APP-05": ["PORT-AUTO"],
    "APP-06": ["WORK-AI", "PORT-AUTO"],
    "CROSS-01": ["BLUE-POLICY", "BLUE-RB", "BLUE-ESTATE", "BLUE-FN", "BLUE-FACILITY"],
    "CROSS-02": ["WORK-CB", "WORK-SYSTEM", "WORK-AI", "WORK-AGENT"],
    "CROSS-03": ["BLUE-ESTATE", "NET-HPCI-EVAL", "NET-IOWN"],
    "CROSS-06": ["BLUE-HPCI-GATES", "BLUE-POLICY", "BLUE-FN"],
    "CROSS-07": ["BLUE-DEPENDENCIES", "BLUE-HPCI-GATES"],
    "ARCH-12": ["COMPUTE-WAFER-SCALE", "COMPUTE-DATAFLOW"],
}

ACTORS_BY_PUBLISHER = {
    "AMD": ["ACT-AMD"],
    "Fujitsu": ["ACT-FUJITSU"],
    "NVIDIA": ["ACT-NVIDIA"],
    "UALink Consortium": ["ACT-UALINK"],
    "Ultra Ethernet Consortium": ["ACT-UEC"],
}

SOURCE_CLASS_MAP = {
    "vendor-official": "official-vendor",
    "standards-body": "official-standard",
    "government-official": "official-project",
    "project-official": "official-project",
    "research-organization": "research-artifact",
    "academic-primary": "peer-reviewed",
    "openfs-governance": "research-artifact",
}

TRACK_CURRENT_MATURITY = {
    "NET-IOWN": "prototype",
    "NET-HPCI-EVAL": "uncertain",
    "BLUE-POLICY": "announced",
    "BLUE-RB": "research",
    "BLUE-ESTATE": "deployed",
    "BLUE-FN": "announced",
    "BLUE-FACILITY": "announced",
    "BLUE-DEPENDENCIES": "uncertain",
    "BLUE-HPCI-GATES": "uncertain",
    "PORT-APIS": "standardized",
    "PORT-COMMS": "standardized",
    "PORT-LLVM": "standardized",
    "PORT-KOKKOS": "deployed",
    "PORT-VENDOR": "commercial",
    "PORT-AUTO": "prototype",
    "PORT-HPCI-EVAL": "uncertain",
    "WORK-EEA": "prototype",
    "WORK-SYSTEM": "deployed",
    "WORK-AI": "deployed",
    "WORK-AGENT": "research",
    "WORK-CB": "prototype",
    "WORK-MODELS": "research",
    "WORK-HPCI-EVAL": "research",
}

DOMAIN_CONDITIONS = {
    "architecture": (
        ["代表アプリの実効性能・電力", "供給・RAS・保守", "ソフトウェアと施設の適合"],
        ["Delivered application performance and power", "Supply, RAS, and service", "Software and facility fit"],
    ),
    "system-software": (
        ["代表アプリの正当性と性能", "複数プラットフォームでの再現性", "版管理・保守責任・セキュリティ"],
        ["Application correctness and performance", "Reproducibility across platforms", "Versioning, maintenance ownership, and security"],
    ),
    "applications": (
        ["利用分野と規模の代表性", "正当性・再現性・公開可能性", "性能・電力・費用・移植工数"],
        ["Representativeness across domains and scales", "Correctness, reproducibility, and publishability", "Performance, power, cost, and porting effort"],
    ),
    "cross-cutting": (
        ["センター別の公開根拠", "予算・調達・運用条件", "依存関係と責任ある人の判断"],
        ["Public evidence by center", "Budget, procurement, and operational conditions", "Dependencies and accountable human decision"],
    ),
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compact(value: str) -> str:
    return "".join(character for character in value.upper() if character.isalnum())


def milestone_sort_key(item: dict[str, Any]) -> tuple[int, int, str]:
    year = item.get("year") or 9999
    quarter = int(item["quarter"][1]) if item.get("quarter") else 5
    return year, quarter, item["milestone_id"]


def timing_text(item: dict[str, Any], language: str) -> str:
    if item.get("year") is None:
        return "時期未公表" if language == "ja" else "No public timing"
    quarter = f" {item['quarter']}" if item.get("quarter") else ""
    suffix = "（四半期未公表）" if language == "ja" and not quarter else ""
    if language == "en" and not quarter:
        suffix = " (quarter not public)"
    return f"{item['year']}{quarter}{suffix}"


def maturity(item: dict[str, Any]) -> str:
    return {
        "commercial": "commercial",
        "deployment": "deployed",
        "standard": "standardized",
        "published": "standardized",
        "pilot": "prototype",
        "target": "announced",
        "decision-gate": "uncertain",
        "undated": "uncertain",
    }.get(item.get("maturity"), "uncertain")


def next_milestone(track_id: str, lanes: list[dict[str, Any]]) -> dict[str, Any] | None:
    milestones = [
        milestone
        for lane in lanes
        if lane["track_id"] == track_id
        for milestone in lane["milestones"]
        if milestone.get("timing_basis") not in {"observed", "as-of-baseline", "openfs-provisional-plan"}
    ]
    return min(milestones, key=milestone_sort_key) if milestones else None


def source_actor_ids(source_ids: list[str], source_index: dict[str, dict[str, Any]]) -> list[str]:
    return sorted({
        actor_id
        for source_id in source_ids
        for actor_id in ACTORS_BY_PUBLISHER.get(source_index[source_id]["publisher"], [])
    })


def import_source(source: dict[str, Any]) -> dict[str, str]:
    date_value = source.get("published_at") or source.get("updated_at") or "accessed 2026-08-27"
    return {
        "source_id": source["source_id"],
        "title": source["title"],
        "publisher": source["publisher"],
        "url": source["url"],
        "source_class": SOURCE_CLASS_MAP[source["source_class"]],
        "published_or_updated": date_value,
    }


def dimensions(topic_id: str, domain: str) -> list[dict[str, str]]:
    prefix = compact(topic_id)
    common = [
        ("VALUE", "導入価値", "Deployment value", "代表的な利用で現在方式より有意な価値を示すか。", "Does it show material value over the current approach for representative use?"),
        ("READY", "導入可能性", "Readiness", "製品、標準、供給、運用支援が必要時期に揃うか。", "Will products, standards, supply, and operational support align with the required date?"),
        ("RISK", "残存リスク", "Residual risk", "未確認条件を実測・契約・fallbackで管理できるか。", "Can unknowns be managed through measurement, contracts, and fallback?"),
    ]
    if domain == "applications":
        common[0] = ("REP", "代表性", "Representativeness", "利用分野、規模、実行形態を十分に代表するか。", "Does it represent relevant domains, scales, and execution modes?")
    return [
        {
            "dimension_id": f"DIM-{prefix}-{suffix}",
            "label_ja": label_ja,
            "label_en": label_en,
            "question_ja": question_ja,
            "question_en": question_en,
        }
        for suffix, label_ja, label_en, question_ja, question_en in common
    ]


def generated_profile(
    topic: dict[str, Any],
    title_en: str,
    tracks: dict[str, dict[str, Any]],
    lanes: list[dict[str, Any]],
    source_index: dict[str, dict[str, Any]],
    gap_id: str,
) -> tuple[dict[str, Any], dict[str, Any], set[str]]:
    topic_id = topic["topic_id"]
    topic_key = compact(topic_id)
    current_items: list[dict[str, Any]] = []
    future_items: list[dict[str, Any]] = []
    used_sources: set[str] = set()
    conditions_ja, conditions_en = DOMAIN_CONDITIONS[topic["domain"]]

    for track_id in TOPIC_TRACKS[topic_id]:
        track = tracks[track_id]
        current_source_ids = track["source_ids"]
        used_sources.update(current_source_ids)
        track_key = compact(track_id)
        current_items.append({
            "item_id": f"TDI-{topic_key}-{track_key}-CURRENT",
            "name_ja": track["name_ja"],
            "name_en": track["name_en"],
            "stage": "current",
            "maturity": TRACK_CURRENT_MATURITY.get(track_id, "commercial"),
            "timing_ja": "2026年8月時点の公開情報",
            "timing_en": "Public information as of August 2026",
            "statement_ja": track["current_state_ja"],
            "statement_en": track["current_state_en"],
            "hpci_relevance_ja": track["hpci_implications_ja"],
            "hpci_relevance_en": track["hpci_implications_en"],
            "adoption_conditions_ja": conditions_ja,
            "adoption_conditions_en": conditions_en,
            "actor_ids": source_actor_ids(current_source_ids, source_index),
            "source_ids": current_source_ids,
            "confidence": "medium",
            "consensus_status": "incomplete",
        })

        milestone = next_milestone(track_id, lanes)
        if milestone:
            future_source_ids = milestone["source_ids"]
            used_sources.update(future_source_ids)
            future_items.append({
                "item_id": f"TDI-{topic_key}-{track_key}-FUTURE",
                "name_ja": milestone["label_ja"],
                "name_en": milestone["label_en"],
                "stage": "contested" if milestone.get("year") is None else "near-term",
                "maturity": maturity(milestone),
                "timing_ja": timing_text(milestone, "ja"),
                "timing_en": timing_text(milestone, "en"),
                "statement_ja": milestone["detail_ja"],
                "statement_en": milestone["detail_en"],
                "hpci_relevance_ja": track["hpci_implications_ja"],
                "hpci_relevance_en": track["hpci_implications_en"],
                "adoption_conditions_ja": conditions_ja,
                "adoption_conditions_en": conditions_en,
                "actor_ids": source_actor_ids(future_source_ids, source_index),
                "source_ids": future_source_ids,
                "confidence": "low" if milestone.get("year") is None else "medium",
                "consensus_status": "incomplete",
            })
        else:
            future_items.append({
                "item_id": f"TDI-{topic_key}-{track_key}-FUTURE",
                "name_ja": f"{track['name_ja']}の次期導入条件",
                "name_en": f"Next adoption conditions for {track['name_en']}",
                "stage": "contested",
                "maturity": "uncertain",
                "timing_ja": "時期未公表",
                "timing_en": "No public timing",
                "statement_ja": "公開一次情報だけでは次期の導入時期と成立条件を確定できないため、推測で埋めず継続調査する。",
                "statement_en": "Public primary sources do not yet establish the next deployment date and conditions; OpenFS leaves them unresolved rather than inferring them.",
                "hpci_relevance_ja": track["hpci_implications_ja"],
                "hpci_relevance_en": track["hpci_implications_en"],
                "adoption_conditions_ja": conditions_ja,
                "adoption_conditions_en": conditions_en,
                "actor_ids": source_actor_ids(current_source_ids, source_index),
                "source_ids": current_source_ids,
                "confidence": "low",
                "consensus_status": "incomplete",
            })

    profile = {
        "topic_id": topic_id,
        "summary_ja": f"現在利用・公開されている方式と近い将来の候補を分け、{topic['title_ja']}を採用判断に必要な条件、根拠、未確認事項まで整理する。",
        "summary_en": f"Separates currently used or publicly documented approaches from near-term candidates and organizes {title_en} around evidence, adoption conditions, and unresolved questions.",
        "sections": [
            {
                "section_id": f"TDS-{topic_key}-CURRENT",
                "title_ja": "現在利用・確認できる方式",
                "title_en": "Currently used or verified approaches",
                "summary_ja": "公開一次情報で現在の製品、標準、運用または評価実績を確認できる項目を示す。",
                "summary_en": "Shows products, standards, operations, or evaluations supported by current public primary sources.",
                "items": current_items,
            },
            {
                "section_id": f"TDS-{topic_key}-FUTURE",
                "title_ja": "近い将来の候補と未確定事項",
                "title_en": "Near-term candidates and unresolved points",
                "summary_ja": "将来時期は公開された目標だけを記載し、未公表の時期や成立条件はCoverage Gapに残す。",
                "summary_en": "Uses only published targets for future timing and leaves undisclosed dates or conditions as Coverage Gaps.",
                "items": future_items,
            },
        ],
        "hpci_decision_dimensions": dimensions(topic_id, topic["domain"]),
        "related_surface_ids": ["platform-software"] if topic_id.startswith("SSW-") else [],
        "coverage_gap_ids": [gap_id],
    }
    gap = {
        "gap_id": gap_id,
        "topic_ids": [topic_id],
        "priority": "P0" if topic_id in {"ARCH-01", "ARCH-04", "ARCH-06", "APP-01", "APP-02", "CROSS-01", "CROSS-02", "CROSS-03", "CROSS-06"} else "P1",
        "question_ja": topic["research_questions"][0],
        "question_en": f"Which evidence is still required to make a deployment decision for {title_en}?",
        "next_action_ja": f"{topic['evidence_expected'][0]}を追加収集し、代表条件で比較して更新する。",
        "next_action_en": "Collect the missing primary evidence and update the comparison under representative conditions.",
        "status": "open",
    }
    return profile, gap, used_sources


def main() -> int:
    artifact = load_json(ARTIFACT_PATH)
    baseline = load_json(BASELINE_PATH)
    i18n = load_json(I18N_PATH)
    roadmaps = [load_json(path) for path in sorted(ROADMAP_DIR.glob("*.json"))]
    tracks = {track["track_id"]: track for roadmap in roadmaps for track in roadmap["tracks"]}
    lanes = [lane for roadmap in roadmaps for lane in roadmap["lanes"]]
    roadmap_sources = {source["source_id"]: source for roadmap in roadmaps for source in roadmap["sources"]}

    partial_topics = [topic for topic in baseline["topics"] if topic["status"] == "partial"]
    missing_mappings = {topic["topic_id"] for topic in partial_topics} - PROTECTED_PROFILES - set(TOPIC_TRACKS)
    unknown_tracks = {track_id for values in TOPIC_TRACKS.values() for track_id in values} - set(tracks)
    if missing_mappings or unknown_tracks:
        raise ValueError(f"profile mapping incomplete: topics={sorted(missing_mappings)}, tracks={sorted(unknown_tracks)}")

    profiles_by_id = {profile["topic_id"]: profile for profile in artifact["topic_profiles"] if profile["topic_id"] in PROTECTED_PROFILES}
    preserved_gaps = [gap for gap in artifact["coverage_gaps"] if set(gap["topic_ids"]) & PROTECTED_PROFILES]
    new_gaps: list[dict[str, Any]] = []
    used_sources: set[str] = set()
    gap_number = 9
    for topic in partial_topics:
        topic_id = topic["topic_id"]
        if topic_id in PROTECTED_PROFILES:
            continue
        gap_id = f"GAP-TDS-{gap_number:03d}"
        gap_number += 1
        profile, gap, profile_sources = generated_profile(
            topic,
            i18n["topic_titles_en"][topic_id],
            tracks,
            lanes,
            roadmap_sources,
            gap_id,
        )
        profiles_by_id[topic_id] = profile
        new_gaps.append(gap)
        used_sources.update(profile_sources)

    existing_sources = {source["source_id"]: source for source in artifact["sources"]}
    for source_id in used_sources:
        if source_id not in existing_sources:
            existing_sources[source_id] = import_source(roadmap_sources[source_id])

    artifact["schema_version"] = "0.2.0"
    artifact["as_of"] = "2026-08-27"
    artifact["topic_profiles"] = [profiles_by_id[topic["topic_id"]] for topic in partial_topics]
    artifact["sources"] = sorted(existing_sources.values(), key=lambda item: item["source_id"])
    artifact["coverage_gaps"] = preserved_gaps + new_gaps
    artifact["publication"] = {
        "information_classification": "public",
        "publication_approved": True,
        "publication_decision_id": "PUBDEC-20260827-002",
        "human_approval_directive_id": "DIR-900012",
    }
    ARTIFACT_PATH.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
