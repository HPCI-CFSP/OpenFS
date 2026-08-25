#!/usr/bin/env python3
"""Measure whether a consumed worldwide follow-up plan closed its Coverage gaps."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json


ROOT = Path(__file__).resolve().parents[1]


def evaluate(
    root: Path, *, run_id: str, evaluated_at: str | None = None
) -> dict[str, Any]:
    manifest = read_json(root / "runs" / run_id / "manifest.json")
    followup = manifest.get("followup_plan")
    if not followup:
        raise ValueError("global follow-up effectiveness requires a consumed plan")
    plan = read_json(root / followup["snapshot_ref"])
    queries = [
        query for query in plan.get("queries", []) if query.get("coverage_targets")
    ]
    if not queries:
        raise ValueError("consumed plan has no worldwide Coverage targets")
    coverage = read_json(root / "runs" / run_id / "coverage.json")
    results = []
    resolved_count = 0
    unresolved_count = 0
    for query in queries:
        target_results = []
        for target in query["coverage_targets"]:
            missing = coverage.get("gaps", {}).get(target["dimension"], [])
            resolved = target["value"] not in missing
            resolved_count += int(resolved)
            unresolved_count += int(not resolved)
            target_results.append({**target, "outcome": "resolved" if resolved else "unresolved"})
        results.append(
            {
                "query_id": query["query_id"],
                "search_generation": query.get("search_generation", 1),
                "effective": all(
                    target["outcome"] == "resolved" for target in target_results
                ),
                "target_results": target_results,
            }
        )
    effective_count = sum(query["effective"] for query in results)
    ineffective_count = len(results) - effective_count
    status = (
        "effective"
        if ineffective_count == 0
        else "ineffective"
        if effective_count == 0
        else "partially-effective"
    )
    return {
        "schema_version": "0.1.0",
        "run_id": run_id,
        "predecessor_run_id": followup["base_run_id"],
        "followup_plan_id": plan["followup_plan_id"],
        "followup_plan_snapshot_ref": followup["snapshot_ref"],
        "evaluated_at": evaluated_at or isoformat(),
        "status": status,
        "query_count": len(results),
        "effective_query_count": effective_count,
        "ineffective_query_count": ineffective_count,
        "resolved_target_count": resolved_count,
        "unresolved_target_count": unresolved_count,
        "queries": results,
    }


def record(root: Path, report: dict[str, Any]) -> dict[str, Any]:
    run_id = report["run_id"]
    report_ref = f"runs/{run_id}/global-followup-effectiveness.json"
    atomic_write_json(root / report_ref, report)
    manifest_path = root / "runs" / run_id / "manifest.json"
    manifest = read_json(manifest_path)
    manifest["global_followup_effectiveness_ref"] = report_ref
    manifest.setdefault("metrics", {})["global_followup_effectiveness"] = {
        "status": report["status"],
        "effective_query_count": report["effective_query_count"],
        "ineffective_query_count": report["ineffective_query_count"],
        "resolved_target_count": report["resolved_target_count"],
        "unresolved_target_count": report["unresolved_target_count"],
    }
    atomic_write_json(manifest_path, manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--evaluated-at")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = evaluate(args.root, run_id=args.run_id, evaluated_at=args.evaluated_at)
    record(args.root, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
