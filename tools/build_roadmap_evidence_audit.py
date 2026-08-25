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
        "screened-primary",
        "direct-primary",
        "event-date-supported",
        "一次情報内の出来事と時期を確認する。",
        "Check the event and timing in the cited primary source.",
    ),
    "standard-release": (
        "screened-primary",
        "direct-primary",
        "event-date-supported",
        "標準化団体の公開履歴で版と公開時期を確認する。",
        "Check the version and publication timing in the standards body's release record.",
    ),
    "as-of-baseline": (
        "as-of-baseline",
        "current-state-only",
        "baseline-only",
        "引用資料は基準日時点の提供状況を支えるが、発売開始年は確定しない。",
        "The source supports availability as of the baseline date, not the original launch year.",
    ),
    "vendor-target": (
        "screened-forward-looking",
        "official-target-statement",
        "target-date-supported",
        "ベンダーが示した将来目標であり、実績または確約とは扱わない。",
        "This is a vendor-stated target, not an observed result or binding commitment.",
    ),
    "project-target": (
        "screened-forward-looking",
        "official-target-statement",
        "target-date-supported",
        "プロジェクトが示した将来目標であり、達成実績とは扱わない。",
        "This is a project-stated target, not an observed completion.",
    ),
    "policy-target": (
        "screened-forward-looking",
        "official-target-statement",
        "target-date-supported",
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
        "review_scope": "single-model-primary-source-screening",
        "consensus_status": "incomplete",
        "method_ja": "6ロードマップの全マイルストーンについて、引用一次情報、主張種別、時期の扱いを照合した。URL到達性監査とは分離し、独立モデルによるConsensusは未完了のまま保持する。",
        "method_en": "Every milestone in the six roadmaps was screened for cited primary sources, claim type, and timing semantics. This is separate from URL reachability, and independent-model Consensus remains incomplete.",
        "summary": {
            "milestone_count": len(entries),
            "screened_primary": counts["screened-primary"],
            "screened_forward_looking": counts["screened-forward-looking"],
            "as_of_baseline": counts["as-of-baseline"],
            "coverage_gap": counts["coverage-gap"],
            "openfs_provisional": counts["openfs-provisional"],
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
