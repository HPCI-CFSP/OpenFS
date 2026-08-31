#!/usr/bin/env python3
"""Expand decision-oriented catalog profiles from reviewed public roadmaps.

This generator deliberately reuses the roadmap tracks as the evidence-bearing
source of truth.  It does not invent missing dates: an absent public milestone
becomes a contested item and an explicit Coverage Gap.
"""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

if __package__:
    from .roadmap_timing import milestone_quarter_window
else:
    from roadmap_timing import milestone_quarter_window


ROOT = Path(__file__).resolve().parents[1]
ARTIFACT_PATH = ROOT / "knowledge/public/topic-decision-support.json"
BASELINE_PATH = ROOT / "config/research-baseline.json"
I18N_PATH = ROOT / "config/publication-i18n.json"
ROADMAP_DIR = ROOT / "knowledge/public/roadmaps"

PROTECTED_PROFILES = {"ARCH-02", "ARCH-03", "SSW-01", "SSW-02", "SSW-04"}

# Every partially researched catalog item must map to reviewed roadmap tracks.
# Existing hand-curated profiles remain authoritative and are not regenerated.
TOPIC_TRACKS: dict[str, list[str]] = {
    "ARCH-01": ["COMPUTE-CPU", "COMPUTE-GPU", "COMPUTE-MATRIX-CUSTOM", "COMPUTE-RACK"],
    "ARCH-04": ["NET-ETHERNET", "NET-HPC-FABRICS", "NET-SCALEUP", "NET-CPO"],
    "ARCH-05": ["COMPUTE-RACK", "NET-IOFABRIC"],
    "ARCH-06": ["BLUE-FACILITY", "COMPUTE-HPCI-EVAL"],
    "SSW-03": ["PORT-COMMS"],
    "SSW-05": ["BLUE-ESTATE", "BLUE-DATA-PLATFORMS", "NET-IOWN"],
    "SSW-06": ["BLUE-POLICY", "BLUE-HPCI-GATES"],
    "SSW-07": ["WORK-CB", "WORK-MODELS"],
    "SSW-08": ["PORT-HPCI-EVAL", "BLUE-HPCI-GATES"],
    "SSW-09": ["WORK-AI", "PORT-AI-TRAINING", "BLUE-POLICY"],
    "APP-01": ["WORK-EEA", "WORK-HPCI-EVAL"],
    "APP-02": ["WORK-SYSTEM", "WORK-CB", "WORK-MODELS"],
    "APP-03": ["WORK-AI", "WORK-EEA"],
    "APP-04": ["WORK-AGENT", "COMPUTE-AGENTIC-CPU", "PORT-AI-INFERENCE"],
    "APP-05": ["PORT-AUTO"],
    "APP-06": ["WORK-AI", "PORT-AUTO"],
    "CROSS-01": ["BLUE-POLICY", "BLUE-RB", "BLUE-ESTATE", "BLUE-DATA-PLATFORMS", "BLUE-FN", "BLUE-FACILITY"],
    "CROSS-02": ["WORK-CB", "WORK-SYSTEM", "WORK-AI", "WORK-AGENT"],
    "CROSS-03": ["BLUE-ESTATE", "BLUE-DATA-PLATFORMS", "NET-HPCI-EVAL", "NET-IOWN"],
    "CROSS-06": ["BLUE-HPCI-GATES", "BLUE-POLICY", "BLUE-FN"],
    "CROSS-07": ["BLUE-DEPENDENCIES", "BLUE-HPCI-GATES"],
    "ARCH-12": ["COMPUTE-WAFER-SCALE", "COMPUTE-DATAFLOW"],
    "ARCH-14": ["COMPUTE-AGENTIC-CPU", "WORK-AGENT"],
    "SSW-17": ["PORT-AI-INFERENCE"],
    "APP-10": ["PORT-AI-INFERENCE", "WORK-AI", "WORK-AGENT"],
}

ACTORS_BY_PUBLISHER = {
    "AMD": ["ACT-AMD"],
    "Fujitsu": ["ACT-FUJITSU"],
    "NVIDIA": ["ACT-NVIDIA"],
    "UALink Consortium": ["ACT-UALINK"],
    "Ultra Ethernet Consortium": ["ACT-UEC"],
    "Cornelis Networks": ["ACT-CORNELIS"],
    "vLLM Project": ["ACT-VLLM"],
    "ggml-org": ["ACT-GGML"],
    "SGLang Project": ["ACT-SGLANG"],
    "Hugging Face": ["ACT-HUGGINGFACE"],
    "Microsoft": ["ACT-MICROSOFT"],
}

GENERATED_ACTORS = [
    {"actor_id": "ACT-CORNELIS", "name": "Cornelis Networks", "region_ids": ["REG-US"], "region_basis_ja": "米国を拠点とするHPCインターコネクト開発主体。", "region_basis_en": "US-based HPC interconnect developer.", "roles_ja": ["Omni-Path、CN5000・CN6000、OPXソフトウェア"], "roles_en": ["Omni-Path, CN5000 and CN6000, and OPX software"], "source_ids": ["SRC-NET027", "SRC-NET028", "SRC-NET029"]},
    {"actor_id": "ACT-VLLM", "name": "vLLM Project", "region_ids": ["REG-MULTI"], "region_basis_ja": "複数地域の開発者が参加するオープンソースプロジェクト。", "region_basis_en": "Multi-region open-source project.", "roles_ja": ["LLM推論サービング"], "roles_en": ["LLM inference serving"], "source_ids": ["SRC-PORT038"]},
    {"actor_id": "ACT-GGML", "name": "ggml-org", "region_ids": ["REG-MULTI"], "region_basis_ja": "複数地域の開発者が参加するオープンソースプロジェクト。", "region_basis_en": "Multi-region open-source project.", "roles_ja": ["llama.cpp、GGUF、ローカル推論"], "roles_en": ["llama.cpp, GGUF, and local inference"], "source_ids": ["SRC-PORT039", "SRC-PORT040"]},
    {"actor_id": "ACT-SGLANG", "name": "SGLang Project", "region_ids": ["REG-MULTI"], "region_basis_ja": "複数地域の開発者が参加するオープンソースプロジェクト。", "region_basis_en": "Multi-region open-source project.", "roles_ja": ["生成AIプログラム、LLM推論サービング"], "roles_en": ["Generative-AI programs and LLM inference serving"], "source_ids": ["SRC-PORT041"]},
    {"actor_id": "ACT-HUGGINGFACE", "name": "Hugging Face", "region_ids": ["REG-MULTI"], "region_basis_ja": "複数地域でモデル・データ・ソフトウェア基盤を提供する開発主体。", "region_basis_en": "Developer of model, data, and software infrastructure operating across regions.", "roles_ja": ["Text Generation Inference"], "roles_en": ["Text Generation Inference"], "source_ids": ["SRC-PORT043"]},
    {"actor_id": "ACT-MICROSOFT", "name": "Microsoft", "region_ids": ["REG-US"], "region_basis_ja": "米国に本社を置くソフトウェア・クラウド開発主体。", "region_basis_en": "US-headquartered software and cloud developer.", "roles_ja": ["ONNX Runtime GenAI"], "roles_en": ["ONNX Runtime GenAI"], "source_ids": ["SRC-PORT044"]},
]

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
    "BLUE-DATA-PLATFORMS": "commercial",
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
    "PORT-AI-TRAINING": "deployed",
    "WORK-EEA": "prototype",
    "WORK-SYSTEM": "deployed",
    "WORK-AI": "deployed",
    "WORK-AGENT": "research",
    "WORK-CB": "prototype",
    "WORK-MODELS": "research",
    "WORK-HPCI-EVAL": "research",
    "COMPUTE-MATRIX-CUSTOM": "announced",
    "COMPUTE-AGENTIC-CPU": "research",
    "NET-HPC-FABRICS": "commercial",
    "PORT-AI-INFERENCE": "deployed",
}

DOMAIN_CONDITIONS = {
    "architecture": (
        ["代表アプリケーションの実効性能・消費電力", "供給・RAS・保守", "ソフトウェアと施設の適合"],
        ["Delivered application performance and power", "Supply, RAS, and service", "Software and facility fit"],
    ),
    "system-software": (
        ["代表アプリケーションの計算結果の妥当性と性能", "複数プラットフォームでの再現性", "版管理・保守責任・セキュリティ"],
        ["Validity and performance of application results", "Reproducibility across platforms", "Versioning, maintenance ownership, and security"],
    ),
    "applications": (
        ["利用分野と規模の代表性", "計算結果の妥当性・再現性・公開可能性", "性能・電力・費用・移植工数"],
        ["Representativeness across domains and scales", "Result validity, reproducibility, and publishability", "Performance, power, cost, and porting effort"],
    ),
    "cross-cutting": (
        ["センター別の公開根拠", "予算・調達・運用条件", "依存関係と判断責任者による決定"],
        ["Public evidence by center", "Budget, procurement, and operational conditions", "Dependencies and a decision by an accountable human"],
    ),
}

DOMAIN_PROFILE_SCOPE = {
    "architecture": (
        "調査基準日現在、公開情報で確認できる製品、標準、導入実績、公開計画",
        "products, standards, documented deployments, and announced plans confirmed as of the research date",
        "導入条件",
        "adoption conditions",
    ),
    "system-software": (
        "調査基準日現在、公開情報で確認できるソフトウェア、標準、導入実績、公開計画",
        "software, standards, documented deployments, and announced plans confirmed as of the research date",
        "移行・運用条件",
        "migration and operational conditions",
    ),
    "applications": (
        "調査基準日現在、公開情報で確認できるベンチマーク、ワークフロー、評価実績、公開計画",
        "benchmarks, workflows, documented evaluations, and announced plans confirmed as of the research date",
        "評価・利用条件",
        "evaluation and use conditions",
    ),
    "cross-cutting": (
        "調査基準日現在、公開情報で確認できる制度、運用方式、実施状況、公開計画",
        "policies, operational practices, documented implementations, and announced plans confirmed as of the research date",
        "実施・運用条件",
        "implementation and operational conditions",
    ),
}

DOMAIN_CURRENT_SECTION_SUMMARY = {
    "architecture": (
        "調査基準日現在、公開情報で確認できる製品、標準、導入実績、公開計画を、成熟度とともに示します。",
        "This section presents products, standards, documented deployments, and announced plans confirmed by public evidence as of the research date, together with their maturity.",
    ),
    "system-software": (
        "調査基準日現在、公開情報で確認できるソフトウェア、標準、導入実績、公開計画を、成熟度とともに示します。",
        "This section presents software, standards, documented deployments, and announced plans confirmed by public evidence as of the research date, together with their maturity.",
    ),
    "applications": (
        "調査基準日現在、公開情報で確認できるベンチマーク、ワークフロー、評価実績、公開計画を、成熟度とともに示します。",
        "This section presents benchmarks, workflows, documented evaluations, and announced plans confirmed by public evidence as of the research date, together with their maturity.",
    ),
    "cross-cutting": (
        "調査基準日現在、公開情報で確認できる制度、運用方式、実施状況、公開計画を、成熟度とともに示します。",
        "This section presents policies, operational practices, documented implementations, and announced plans confirmed by public evidence as of the research date, together with their maturity.",
    ),
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def compact(value: str) -> str:
    return "".join(character for character in value.upper() if character.isalnum())


def latest_research_date(artifact: dict[str, Any], roadmaps: list[dict[str, Any]]) -> date:
    return max(
        date.fromisoformat(artifact["as_of"]),
        *(date.fromisoformat(roadmap["as_of"]) for roadmap in roadmaps),
    )


def milestone_sort_key(item: dict[str, Any]) -> tuple[int, int, str]:
    if item.get("timing_precision") == "quarter-range":
        end = milestone_quarter_window(item)[1]
        return end // 4, end % 4 + 1, item["milestone_id"]
    year = item.get("year") or 9999
    if item.get("quarter"):
        period = int(item["quarter"][1])
    elif item.get("half") == "H1":
        period = 2
    elif item.get("half") == "H2":
        period = 4
    else:
        period = 4
    return year, period, item["milestone_id"]


def timing_text(item: dict[str, Any], language: str) -> str:
    if item.get("timing_precision") == "quarter-range":
        milestone_quarter_window(item)
        if language == "ja":
            return f"{item['year']}年{item['quarter']}〜{item['end_year']}年{item['end_quarter']}"
        return f"{item['year']} {item['quarter']} - {item['end_year']} {item['end_quarter']}"
    if item.get("year") is None:
        return "時期未公表" if language == "ja" else "No public timing"
    if item.get("quarter"):
        return (
            f"{item['year']}年{item['quarter']}"
            if language == "ja"
            else f"{item['quarter']} {item['year']}"
        )
    if item.get("half"):
        half_ja = "前半" if item["half"] == "H1" else "後半"
        return (
            f"{item['year']}年{half_ja}（{item['half']}）"
            if language == "ja"
            else f"{item['half']} {item['year']}"
        )
    return (
        f"{item['year']}年（四半期未公表）"
        if language == "ja"
        else f"{item['year']} (quarter not public)"
    )


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


def next_milestone(
    track_id: str,
    lanes: list[dict[str, Any]],
    research_as_of: date,
) -> dict[str, Any] | None:
    current_quarter = (research_as_of.month - 1) // 3 + 1

    def remains_future(item: dict[str, Any]) -> bool:
        if item.get("timing_precision") == "quarter-range":
            return milestone_quarter_window(item)[1] > research_as_of.year * 4 + current_quarter - 1
        year = item.get("year")
        if year is None:
            return True
        if year != research_as_of.year:
            return year > research_as_of.year
        if item.get("quarter"):
            return int(item["quarter"][1]) > current_quarter
        if item.get("half") == "H1":
            return 2 > current_quarter
        if item.get("half") == "H2":
            return 4 > current_quarter
        # A year-only target still spans the remaining quarters of the year.
        return current_quarter < 4

    milestones = [
        milestone
        for lane in lanes
        if lane["track_id"] == track_id
        for milestone in lane["milestones"]
        if milestone.get("timing_basis") not in {"observed", "as-of-baseline", "openfs-provisional-plan"}
        and remains_future(milestone)
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
        ("VALUE", "導入価値", "Deployment value", "代表的な利用条件において、現行方式よりも有意な価値を示すか。", "Does it show material value over the current approach for representative use?"),
        ("READY", "導入可能性", "Readiness", "製品、標準、供給、運用支援が必要な時期に揃うか。", "Will products, standards, supply, and operational support align with the required date?"),
        ("RISK", "残存リスク", "Residual risk", "未確認事項を実測、契約、代替策によって管理できるか。", "Can unknowns be managed through measurement, contracts, and fallback options?"),
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
    research_as_of: date,
) -> tuple[dict[str, Any], dict[str, Any], set[str]]:
    topic_id = topic["topic_id"]
    topic_key = compact(topic_id)
    current_items: list[dict[str, Any]] = []
    future_items: list[dict[str, Any]] = []
    used_sources: set[str] = set()
    conditions_ja, conditions_en = DOMAIN_CONDITIONS[topic["domain"]]
    current_scope_ja, current_scope_en, decision_scope_ja, decision_scope_en = (
        DOMAIN_PROFILE_SCOPE[topic["domain"]]
    )
    current_summary_ja, current_summary_en = DOMAIN_CURRENT_SECTION_SUMMARY[
        topic["domain"]
    ]
    as_of_ja = f"{research_as_of.year}年{research_as_of.month}月{research_as_of.day}日時点の公開情報"
    as_of_en = (
        f"Public information as of {research_as_of.strftime('%B')} "
        f"{research_as_of.day}, {research_as_of.year}"
    )

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
            "timing_ja": as_of_ja,
            "timing_en": as_of_en,
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

        milestone = next_milestone(track_id, lanes, research_as_of)
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
        "summary_ja": f"{topic['title_ja']}について、{current_scope_ja}を最新状況として整理し、将来候補と区別して示します。計画・導入判断に必要な{decision_scope_ja}、根拠、未確認事項も併せて整理します。",
        "summary_en": f"This profile of {title_en} separates the latest status verified as of the research date from future candidates. It also records the evidence, {decision_scope_en}, and unresolved questions needed for planning and adoption decisions.",
        "sections": [
            {
                "section_id": f"TDS-{topic_key}-CURRENT",
                "title_ja": f"{topic['title_ja']}の最新状況（調査基準日現在）",
                "title_en": f"Status as of the research date: {title_en}",
                "summary_ja": current_summary_ja,
                "summary_en": current_summary_en,
                "items": current_items,
            },
            {
                "section_id": f"TDS-{topic_key}-FUTURE",
                "title_ja": f"{topic['title_ja']}の将来候補",
                "title_en": f"Future candidates for {title_en}",
                "summary_ja": "将来の時期は公表された目標だけを記載し、公表されていない時期や成立条件は未確認事項として残します。",
                "summary_en": "This section uses only published targets for future timing and explicitly records any undisclosed dates or conditions as coverage gaps.",
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
        "question_en": f"Which evidence is still required to make a planning or adoption decision for {title_en}?",
        "next_action_ja": f"不足している一次情報（{topic['evidence_expected'][0]}）を追加で収集し、代表的な条件で比較した上で更新する。",
        "next_action_en": "Collect the missing primary evidence and update the comparison under representative conditions.",
        "status": "open",
    }
    return profile, gap, used_sources


def main() -> int:
    artifact = load_json(ARTIFACT_PATH)
    baseline = load_json(BASELINE_PATH)
    if baseline.get("catalog_revision", 0) >= 5:
        raise ValueError(
            "Legacy whole-profile generation is disabled for catalog revision 5+. "
            "Update assigned research units with preserved Evidence IDs; see "
            "docs/operations/catalog-maintenance.md."
        )
    i18n = load_json(I18N_PATH)
    roadmaps = [load_json(path) for path in sorted(ROADMAP_DIR.glob("*.json"))]
    research_as_of = latest_research_date(artifact, roadmaps)
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
            research_as_of,
        )
        profiles_by_id[topic_id] = profile
        new_gaps.append(gap)
        used_sources.update(profile_sources)

    existing_sources = {source["source_id"]: source for source in artifact["sources"]}
    for source_id in used_sources:
        if source_id not in existing_sources:
            existing_sources[source_id] = import_source(roadmap_sources[source_id])

    artifact["schema_version"] = "0.2.0"
    artifact["as_of"] = research_as_of.isoformat()
    artifact["topic_profiles"] = [profiles_by_id[topic["topic_id"]] for topic in partial_topics]
    actors_by_id = {actor["actor_id"]: actor for actor in artifact["actors"]}
    actors_by_id.update({actor["actor_id"]: actor for actor in GENERATED_ACTORS})
    artifact["actors"] = sorted(actors_by_id.values(), key=lambda item: item["actor_id"])
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
