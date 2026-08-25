#!/usr/bin/env python3
"""Build an explicit, deterministic work queue from public roadmap Coverage Gaps."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "knowledge" / "public" / "audits" / "roadmap-gap-queue.json"

DEFAULT_MONITORS = {
    "RM-HW-MEMORY": "MON-MEMORY-001",
    "RM-X-BLUEPRINT": "MON-HPCI-CENTERS-001",
}
SPECIAL_ASSIGNMENTS = {
    "GAP-BLUE-002": "MON-FS-BASELINE-001",
    "GAP-BLUE-006": "CRP-P0-ROADMAPS-V02",
}
CADENCE = {"P0": "weekly", "P1": "monthly", "P2": "quarterly"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _monitor_index(root: Path) -> dict[str, dict[str, Any]]:
    monitors = [
        load_json(path)
        for path in sorted((root / "config" / "monitors").glob("*.json"))
    ]
    return {monitor["monitor_id"]: monitor for monitor in monitors}


def _query_overrides(root: Path) -> dict[str, dict[str, Any]]:
    path = root / "config/roadmap-gap-query-overrides.json"
    if not path.is_file():
        return {}
    entries = load_json(path).get("entries", [])
    by_gap = {entry["gap_id"]: entry for entry in entries}
    if len(by_gap) != len(entries):
        raise ValueError("roadmap Gap query overrides contain duplicate Gap IDs")
    return by_gap


def _assignment_ref(roadmap_id: str, gap_id: str) -> str:
    return SPECIAL_ASSIGNMENTS.get(
        gap_id,
        DEFAULT_MONITORS.get(roadmap_id, "MON-GLOBAL-TECH-001"),
    )


def build(root: Path, generated_at: str | None = None) -> dict[str, Any]:
    roadmaps = [
        load_json(path)
        for path in sorted((root / "knowledge/public/roadmaps").glob("*.json"))
    ]
    if not roadmaps:
        raise ValueError("no public roadmaps found")
    as_of_values = {roadmap["as_of"] for roadmap in roadmaps}
    if len(as_of_values) != 1:
        raise ValueError(f"roadmap as_of values disagree: {sorted(as_of_values)}")
    as_of = as_of_values.pop()
    monitors = _monitor_index(root)
    overrides = _query_overrides(root)

    assignments: list[dict[str, Any]] = []
    seen_gap_ids: set[str] = set()
    for roadmap in roadmaps:
        for gap in roadmap["coverage_gaps"]:
            gap_id = gap["gap_id"]
            if gap_id in seen_gap_ids:
                raise ValueError(f"duplicate Coverage Gap ID: {gap_id}")
            seen_gap_ids.add(gap_id)
            assignment_ref = _assignment_ref(roadmap["roadmap_id"], gap_id)
            cadence = CADENCE[gap["priority"]]
            if assignment_ref.startswith("CRP-"):
                assignment = {
                    "gap_id": gap_id,
                    "roadmap_id": roadmap["roadmap_id"],
                    "priority": gap["priority"],
                    "workstream": "consensus-review",
                    "cadence": "continuous-until-quorum",
                    "assignment_ref": assignment_ref,
                    "task_id": None,
                    "monitor_enabled": None,
                    "execution_state": "awaiting-independent-review",
                    "scope_ja": gap["scope_ja"],
                    "scope_en": gap["scope_en"],
                    "impact_ja": gap["impact_ja"],
                    "impact_en": gap["impact_en"],
                    "next_action_ja": gap["next_action_ja"],
                    "next_action_en": gap["next_action_en"],
                    "query_seeds": [],
                    "required_source_classes": [],
                    "query_plan_origin": "not-applicable",
                    "status": gap["status"],
                }
            else:
                monitor = monitors.get(assignment_ref)
                if monitor is None:
                    raise ValueError(f"Coverage Gap references unknown Monitor: {assignment_ref}")
                enabled = monitor.get("enabled") is True
                override = overrides.get(gap_id)
                if override:
                    unknown_classes = set(override["source_classes"]) - set(
                        monitor.get("source_classes", [])
                    )
                    if unknown_classes:
                        raise ValueError(
                            f"Coverage Gap {gap_id} query override uses Source classes "
                            f"outside {assignment_ref}: {sorted(unknown_classes)}"
                        )
                    query_seeds = override["query_seeds"]
                    required_source_classes = override["source_classes"]
                    query_plan_origin = "explicit-override"
                else:
                    query_seeds = [
                        {
                            "language": "ja",
                            "query": f"{gap['scope_ja']} {gap['next_action_ja']} 公式 一次情報",
                        },
                        {
                            "language": "en",
                            "query": f"{gap['scope_en']} {gap['next_action_en']} official primary source",
                        },
                    ]
                    required_source_classes = monitor.get("source_classes", [])
                    query_plan_origin = "generated-fallback"
                assignment = {
                    "gap_id": gap_id,
                    "roadmap_id": roadmap["roadmap_id"],
                    "priority": gap["priority"],
                    "workstream": "source-discovery",
                    "cadence": cadence,
                    "assignment_ref": assignment_ref,
                    "task_id": monitor["task_id"],
                    "monitor_enabled": enabled,
                    "execution_state": (
                        "ready-for-scheduled-discovery"
                        if enabled
                        else "staged-monitor-disabled"
                    ),
                    "scope_ja": gap["scope_ja"],
                    "scope_en": gap["scope_en"],
                    "impact_ja": gap["impact_ja"],
                    "impact_en": gap["impact_en"],
                    "next_action_ja": gap["next_action_ja"],
                    "next_action_en": gap["next_action_en"],
                    "query_seeds": query_seeds,
                    "required_source_classes": required_source_classes,
                    "query_plan_origin": query_plan_origin,
                    "status": gap["status"],
                }
            assignments.append(assignment)

    orphan_overrides = set(overrides) - seen_gap_ids
    if orphan_overrides:
        raise ValueError(
            f"roadmap Gap query overrides reference unknown Gaps: {sorted(orphan_overrides)}"
        )

    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    assignments.sort(
        key=lambda item: (
            priority_order[item["priority"]],
            item["roadmap_id"],
            item["gap_id"],
        )
    )
    for index, assignment in enumerate(assignments, 1):
        assignment["queue_item_id"] = f"RGQ-{index:04d}"

    priorities = Counter(item["priority"] for item in assignments)
    states = Counter(item["execution_state"] for item in assignments)
    workstreams = Counter(item["workstream"] for item in assignments)
    query_origins = Counter(item["query_plan_origin"] for item in assignments)
    p0_query_origins = Counter(
        item["query_plan_origin"]
        for item in assignments
        if item["priority"] == "P0"
    )
    generated = generated_at or datetime.now(timezone.utc).replace(
        microsecond=0
    ).isoformat().replace("+00:00", "Z")
    return {
        "schema_version": "0.1.0",
        "export_id": "ROADMAP-GAP-QUEUE-001",
        "status": "published",
        "queue_id": f"RGQ-{as_of.replace('-', '')}-001",
        "as_of": as_of,
        "generated_at": generated,
        "method_ja": "6ロードマップの全Coverage Gapを優先度順に収集し、既存Monitorまたは独立Consensusパッケージへ明示的に割り当てた。P0は毎週、P1は毎月、P2は四半期ごとの再調査を原則とし、明示query planがあるGapでは生成fallbackより優先する。",
        "method_en": "Collects every Coverage Gap from the six roadmaps, orders them by priority, and assigns each to an existing Monitor or the independent Consensus package. P0 is normally rechecked weekly, P1 monthly, and P2 quarterly; an explicit query plan takes precedence over the generated fallback.",
        "caveat_ja": "このキューは調査の割当であり、Gapが解消したことを示さない。生成fallbackは探索開始点にすぎない。Monitorが無効の項目は本番準備ゲートを通過するまで自動検索されない。",
        "caveat_en": "This queue assigns research; it does not establish that a Gap is resolved, and a generated fallback is only a discovery starting point. Items assigned to disabled Monitors are not searched automatically until production-readiness gates pass.",
        "summary": {
            "roadmap_count": len(roadmaps),
            "gap_count": len(assignments),
            "p0": priorities["P0"],
            "p1": priorities["P1"],
            "p2": priorities["P2"],
            "source_discovery": workstreams["source-discovery"],
            "consensus_review": workstreams["consensus-review"],
            "ready_for_scheduled_discovery": states["ready-for-scheduled-discovery"],
            "staged_monitor_disabled": states["staged-monitor-disabled"],
            "awaiting_independent_review": states["awaiting-independent-review"],
            "explicit_query_overrides": query_origins["explicit-override"],
            "generated_query_fallbacks": query_origins["generated-fallback"],
            "p0_explicit_query_overrides": p0_query_origins["explicit-override"],
            "p0_generated_query_fallbacks": p0_query_origins["generated-fallback"],
        },
        "assignments": assignments,
        "publication": {
            "information_classification": "public",
            "publication_approved": True,
            "publication_decision_id": "PUBDEC-20260826-005",
            "human_approval_directive_id": "DIR-900006",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--generated-at")
    args = parser.parse_args()
    result = build(args.root, args.generated_at)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
