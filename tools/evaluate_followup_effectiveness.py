#!/usr/bin/env python3
"""Measure whether a consumed Center follow-up plan improved its target fields."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json


ROOT = Path(__file__).resolve().parents[1]
STATE_STRENGTH = {"unknown": 0, "partial": 1, "verified": 2, "not-applicable": 2}


def _profiles(root: Path, run_id: str) -> dict[str, tuple[str, dict[str, Any]]]:
    result = {}
    for path in sorted((root / "proposals" / "center-profiles" / run_id).glob("*.json")):
        profile = read_json(path)
        result[profile["center_id"]] = (str(path.relative_to(root)), profile)
    return result


def _field_outcome(previous: dict[str, Any], current: dict[str, Any]) -> str:
    previous_status = previous.get("status", "unknown")
    current_status = current.get("status", "unknown")
    previous_strength = STATE_STRENGTH.get(previous_status, -1)
    current_strength = STATE_STRENGTH.get(current_status, -1)
    if current_strength > previous_strength:
        return "improved"
    if current_strength < previous_strength:
        return "regressed"
    if current != previous:
        return "refreshed"
    return "unchanged"


def evaluate(
    root: Path, *, run_id: str, evaluated_at: str | None = None
) -> dict[str, Any]:
    manifest = read_json(root / "runs" / run_id / "manifest.json")
    followup = manifest.get("followup_plan")
    if not followup:
        raise ValueError("follow-up effectiveness requires a consumed follow-up plan")
    plan = read_json(root / followup["snapshot_ref"])
    if not plan.get("queries"):
        raise ValueError("follow-up effectiveness requires at least one query")
    predecessor_run_id = followup["base_run_id"]
    previous_profiles = _profiles(root, predecessor_run_id)
    current_profiles = _profiles(root, run_id)
    query_results = []
    totals = {name: 0 for name in ("improved", "refreshed", "unchanged", "regressed")}
    for query in plan.get("queries", []):
        center_id = query["center_id"]
        previous_entry = previous_profiles.get(center_id)
        current_entry = current_profiles.get(center_id)
        field_results = []
        if previous_entry and current_entry:
            for field in query.get("profile_fields", []):
                previous = previous_entry[1].get(field, {"status": "unknown"})
                current = current_entry[1].get(field, {"status": "unknown"})
                outcome = _field_outcome(previous, current)
                totals[outcome] += 1
                field_results.append(
                    {
                        "field": field,
                        "previous_status": previous.get("status", "unknown"),
                        "current_status": current.get("status", "unknown"),
                        "outcome": outcome,
                    }
                )
        elif previous_entry:
            for field in query.get("profile_fields", []):
                previous = previous_entry[1].get(field, {"status": "unknown"})
                totals["regressed"] += 1
                field_results.append(
                    {
                        "field": field,
                        "previous_status": previous.get("status", "unknown"),
                        "current_status": "missing-profile",
                        "outcome": "regressed",
                    }
                )
        effective = any(
            item["outcome"] in {"improved", "refreshed"} for item in field_results
        )
        query_results.append(
            {
                "query_id": query["query_id"],
                "center_id": center_id,
                "search_generation": query.get("search_generation", 1),
                "effective": effective,
                "previous_profile_ref": previous_entry[0] if previous_entry else None,
                "current_profile_ref": current_entry[0] if current_entry else None,
                "field_results": field_results,
            }
        )
    effective_count = sum(item["effective"] for item in query_results)
    ineffective_count = len(query_results) - effective_count
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
        "predecessor_run_id": predecessor_run_id,
        "followup_plan_id": plan["followup_plan_id"],
        "followup_plan_snapshot_ref": followup["snapshot_ref"],
        "evaluated_at": evaluated_at or isoformat(),
        "status": status,
        "query_count": len(query_results),
        "effective_query_count": effective_count,
        "ineffective_query_count": ineffective_count,
        "field_outcomes": totals,
        "queries": query_results,
    }


def record(root: Path, report: dict[str, Any]) -> dict[str, Any]:
    run_id = report["run_id"]
    report_ref = f"runs/{run_id}/followup-effectiveness.json"
    atomic_write_json(root / report_ref, report)
    manifest_path = root / "runs" / run_id / "manifest.json"
    manifest = read_json(manifest_path)
    manifest["followup_effectiveness_ref"] = report_ref
    manifest.setdefault("metrics", {})["followup_effectiveness"] = {
        "status": report["status"],
        "effective_query_count": report["effective_query_count"],
        "ineffective_query_count": report["ineffective_query_count"],
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
