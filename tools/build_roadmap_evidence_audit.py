#!/usr/bin/env python3
"""Build the complete single-model claim-evidence screening register."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "knowledge" / "public" / "audits" / "roadmap-evidence-audit.json"


STATUS_BY_BASIS = {
    "observed": (
        "classified-primary-event",
        "official-primary-source-cited",
        "declared-event-timing",
        "独立レビューで、一次情報が出来事とその時期を実際に裏付けているか確認する必要がある。",
        "Independent review must verify that the primary source entails the event and timing.",
    ),
    "standard-release": (
        "classified-primary-event",
        "official-primary-source-cited",
        "declared-event-timing",
        "独立レビューで、標準化団体の公開履歴が版番号と公開時期を裏付けているか確認する必要がある。",
        "Independent review must verify that the standards release record supports the version and timing.",
    ),
    "as-of-baseline": (
        "as-of-baseline",
        "current-state-only",
        "baseline-only",
        "引用資料は調査基準日現在の提供状況を裏付けているが、発売開始年までは確定できない。",
        "The source supports availability as of the baseline date, not the original launch year.",
    ),
    "vendor-target": (
        "classified-forward-looking",
        "official-target-source-cited",
        "declared-target-timing",
        "ベンダーが示した将来目標であり、実績または確約とは扱わない。",
        "This is a vendor-stated target, not an observed result or binding commitment.",
    ),
    "project-target": (
        "classified-forward-looking",
        "official-target-source-cited",
        "declared-target-timing",
        "プロジェクトが示した将来目標であり、達成実績とは扱わない。",
        "This is a project-stated target, not an observed completion.",
    ),
    "policy-target": (
        "classified-forward-looking",
        "official-target-source-cited",
        "declared-target-timing",
        "政策資料が示した目標であり、予算措置または導入完了とは扱わない。",
        "This is a policy target, not proof of funding or completed deployment.",
    ),
    "no-public-date": (
        "coverage-gap",
        "absence-not-exhaustively-provable",
        "unresolved",
        "公開時期を確認できないため、推測で補わず、未確認事項として残す。",
        "No public timing was confirmed; retain the item as a Coverage Gap without extrapolation.",
    ),
    "openfs-provisional-plan": (
        "openfs-provisional",
        "openfs-design-assessment",
        "provisional-gate",
        "公開根拠を踏まえたOpenFSの暫定評価ゲートで、外部組織の公表日程ではない。",
        "This is an OpenFS provisional evaluation gate informed by public evidence, not an externally announced schedule.",
    ),
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def timing_label(milestone: dict[str, Any], language: str) -> str:
    year = milestone["year"]
    if year is None:
        return "時期未公表" if language == "ja" else "undated"
    quarter = milestone["quarter"]
    return f"{year} {quarter}" if quarter else str(year)


def build_entry(
    roadmap_id: str,
    milestone: dict[str, Any],
    source_classes: set[str],
) -> dict[str, Any]:
    internal_governance_event = (
        source_classes == {"openfs-governance"}
        and milestone["timing_basis"] not in {"openfs-provisional-plan", "no-public-date"}
    )
    if internal_governance_event:
        status = "openfs-governance-event"
        support = "openfs-governance-record"
        timing = "recorded-internal-event"
        note_ja = "OpenFS自身の公開ガバナンス記録であり、外部技術の一次情報には数えない。"
        note_en = "This is an OpenFS governance record and does not count as external primary technology evidence."
    else:
        status, support, timing, note_ja, note_en = STATUS_BY_BASIS[milestone["timing_basis"]]
    return {
        "roadmap_id": roadmap_id,
        "milestone_id": milestone["milestone_id"],
        "comparison_priority": milestone["comparison_priority"],
        "review_status": status,
        "claim_support": support,
        "timing_status": timing,
        "source_ids": milestone["source_ids"],
        "locator_hint_ja": (
            f"独立レビューでは、引用元で「{milestone['label_ja']}」と時期「{timing_label(milestone, 'ja')}」を照合する必要がある。"
        ),
        "locator_hint_en": (
            f"Cross-check '{milestone['label_en']}' and timing '{timing_label(milestone, 'en')}' in the cited source."
        ),
        "review_note_ja": note_ja,
        "review_note_en": note_en,
        "semantic_verification": "pending-independent-review",
    }


def generation_band_boundary_label(boundary: dict[str, Any]) -> str:
    if boundary["precision"] == "quarter":
        return f"{boundary['year']} {boundary['quarter']}"
    if boundary["precision"] == "half-year":
        return f"{boundary['year']} {boundary['half']}"
    return str(boundary["year"])


def generation_band_timing_label(band: dict[str, Any], language: str) -> str:
    start = generation_band_boundary_label(band["start"])
    if band["end"] is None:
        end = "終了時期未確認" if language == "ja" else "end date not confirmed"
    else:
        end = generation_band_boundary_label(band["end"])
    return f"{start} - {end}"


def generation_band_locator(band: dict[str, Any], language: str) -> str:
    if band["end"] is None:
        start = generation_band_boundary_label(band["start"])
        if language == "ja":
            return f"表示開始は{start}であり、終了時期は確認できていない。"
        return f"The displayed window starts in {start}; no end date has been confirmed."
    timing = generation_band_timing_label(band, language)
    if language == "ja":
        return f"表示範囲は{timing}である。"
    return f"The displayed window is {timing}."


def build_generation_band_entry(
    roadmap_id: str, band: dict[str, Any]
) -> dict[str, Any]:
    return {
        "roadmap_id": roadmap_id,
        "generation_band_id": band["generation_band_id"],
        "review_status": "openfs-synthesis-pending",
        "claim_support": "registered-sources-cited",
        "timing_status": "open-ended" if band["end"] is None else "bounded-window",
        "confidence": band["confidence"],
        "consensus_status": band["consensus_status"],
        "source_ids": band["source_ids"],
        "locator_hint_ja": (
            f"独立レビューでは、引用元で「{band['label_ja']}」の各境界と統合根拠を照合する必要がある。"
            f"{generation_band_locator(band, 'ja')}"
        ),
        "locator_hint_en": (
            f"Cross-check every boundary and synthesis basis for '{band['label_en']}'. "
            f"{generation_band_locator(band, 'en')}"
        ),
        "review_note_ja": "複数の公開情報を組み合わせたOpenFS暫定見通しであり、業界合意または採用判断ではない。",
        "review_note_en": "This is a provisional OpenFS synthesis of public sources, not industry consensus or an adoption decision.",
        "semantic_verification": "pending-independent-review",
    }


def build_audit(root: Path) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    generation_band_entries: list[dict[str, Any]] = []
    timing_counts: Counter[str] = Counter()
    roadmaps = [
        load_json(path)
        for path in sorted(
            (root / "knowledge" / "public" / "roadmaps").glob("*.json")
        )
    ]
    as_of_values = {roadmap["as_of"] for roadmap in roadmaps}
    # Roadmaps are updated independently; do not relabel untouched research.
    as_of = max(as_of_values)
    for roadmap in roadmaps:
        source_classes = {
            source["source_id"]: source["source_class"]
            for source in roadmap["sources"]
        }
        for lane in roadmap["lanes"]:
            for milestone in lane["milestones"]:
                milestone_source_classes = {
                    source_classes[source_id] for source_id in milestone["source_ids"]
                }
                entries.append(
                    build_entry(roadmap["roadmap_id"], milestone, milestone_source_classes)
                )
                if milestone["timing_basis"] == "openfs-provisional-plan":
                    timing_counts[f"openfs_provisional_{milestone['timing_precision'].replace('-', '_')}"] += 1
                elif milestone["timing_basis"] == "no-public-date":
                    timing_counts["undated"] += 1
                elif milestone_source_classes == {"openfs-governance"}:
                    timing_counts[f"openfs_governance_{milestone['timing_precision'].replace('-', '_')}"] += 1
                else:
                    timing_counts[f"source_supported_{milestone['timing_precision'].replace('-', '_')}"] += 1
        for track in roadmap["tracks"]:
            for band in track.get("generation_bands", []):
                generation_band_entries.append(
                    build_generation_band_entry(roadmap["roadmap_id"], band)
                )
    entries.sort(key=lambda item: (item["roadmap_id"], item["milestone_id"]))
    generation_band_entries.sort(
        key=lambda item: (item["roadmap_id"], item["generation_band_id"])
    )
    counts = Counter(item["review_status"] for item in entries)
    return {
        "schema_version": "0.1.0",
        "export_id": "ROADMAP-EVIDENCE-AUDIT-001",
        "status": "published",
        "as_of": as_of,
        "review_scope": "single-model-structured-claim-classification",
        "consensus_status": "incomplete",
        "method_ja": "6本のロードマップに含まれる全マイルストーンと世代区分について、出典IDの有無、主張の種類、時期表現の整合性を機械的に分類しました。主要な更新項目は、単一のAIモデルが一次情報と照合しています。全項目の意味内容を独立に検証した結果ではなく、URLの到達性監査とも区別しています。独立したAIモデルによる合意判定は未完了です。",
        "method_en": "Every milestone and generation band in the six roadmaps was structurally classified for source-reference presence, claim type, and timing semantics. One model checked major updates against primary sources. This audit does not independently verify the meaning of every item and is separate from URL-reachability checks. Consensus review by independent models remains incomplete.",
        "summary": {
            "milestone_count": len(entries),
            "generation_band_count": len(generation_band_entries),
            "classified_primary": counts["classified-primary-event"],
            "classified_forward_looking": counts["classified-forward-looking"],
            "as_of_baseline": counts["as-of-baseline"],
            "coverage_gap": counts["coverage-gap"],
            "openfs_provisional": counts["openfs-provisional"],
            "openfs_governance_event": counts["openfs-governance-event"],
            "independently_verified": 0,
            "pending_independent_review": len(entries) + len(generation_band_entries),
            "source_supported_quarter": timing_counts["source_supported_quarter"],
            "source_supported_half_year": timing_counts["source_supported_half_year"],
            "source_supported_year": timing_counts["source_supported_year"],
            "undated": timing_counts["undated"],
            "openfs_provisional_quarter": timing_counts["openfs_provisional_quarter"],
            "openfs_provisional_year": timing_counts["openfs_provisional_year"],
            "openfs_governance_quarter": timing_counts["openfs_governance_quarter"],
            "openfs_governance_year": timing_counts["openfs_governance_year"],
        },
        "entries": entries,
        "generation_band_entries": generation_band_entries,
        "publication": {
            "information_classification": "public",
            "publication_approved": True,
            "publication_decision_id": "PUBDEC-20260826-001",
            "human_approval_directive_id": "DIR-900006",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = build_audit(args.root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(audit["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
