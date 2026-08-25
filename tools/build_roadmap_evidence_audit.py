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
        "独立Reviewで、一次情報内の出来事と時期の含意を確認する必要がある。",
        "Independent review must verify that the primary source entails the event and timing.",
    ),
    "standard-release": (
        "classified-primary-event",
        "official-primary-source-cited",
        "declared-event-timing",
        "独立Reviewで、標準化団体の公開履歴が版と公開時期を支えるか確認する必要がある。",
        "Independent review must verify that the standards release record supports the version and timing.",
    ),
    "as-of-baseline": (
        "as-of-baseline",
        "current-state-only",
        "baseline-only",
        "引用資料は基準日時点の提供状況を支えるが、発売開始年は確定しない。",
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
        "公開時期を確認できないため、推測せずCoverage Gapとして残す。",
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


def build_entry(roadmap_id: str, milestone: dict[str, Any]) -> dict[str, Any]:
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
            f"引用元で「{milestone['label_ja']}」と時期「{timing_label(milestone, 'ja')}」を照合。"
        ),
        "locator_hint_en": (
            f"Cross-check '{milestone['label_en']}' and timing '{timing_label(milestone, 'en')}' in the cited source."
        ),
        "review_note_ja": note_ja,
        "review_note_en": note_en,
        "semantic_verification": "pending-independent-review",
    }


def build_audit(root: Path) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for path in sorted((root / "knowledge" / "public" / "roadmaps").glob("*.json")):
        roadmap = load_json(path)
        for lane in roadmap["lanes"]:
            for milestone in lane["milestones"]:
                entries.append(build_entry(roadmap["roadmap_id"], milestone))
    entries.sort(key=lambda item: (item["roadmap_id"], item["milestone_id"]))
    counts = Counter(item["review_status"] for item in entries)
    return {
        "schema_version": "0.1.0",
        "export_id": "ROADMAP-EVIDENCE-AUDIT-001",
        "status": "published",
        "as_of": "2026-08-26",
        "review_scope": "single-model-structured-claim-classification",
        "consensus_status": "incomplete",
        "method_ja": "6ロードマップの全マイルストーンについて、引用IDの存在、主張種別、時期表現の整合を機械的に分類し、主要な更新項目を単一モデルで一次情報と照合した。全件の独立した意味検証を示すものではなく、URL到達性監査とも分離している。独立モデルによるConsensusは未完了。",
        "method_en": "Every milestone in the six roadmaps was structurally classified for source-reference presence, claim type, and timing semantics, and major updates were checked by one model against primary sources. This is not independent semantic verification of every item and is separate from URL reachability. Independent-model Consensus remains incomplete.",
        "summary": {
            "milestone_count": len(entries),
            "classified_primary": counts["classified-primary-event"],
            "classified_forward_looking": counts["classified-forward-looking"],
            "as_of_baseline": counts["as-of-baseline"],
            "coverage_gap": counts["coverage-gap"],
            "openfs_provisional": counts["openfs-provisional"],
            "independently_verified": 0,
            "pending_independent_review": len(entries),
        },
        "entries": entries,
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
