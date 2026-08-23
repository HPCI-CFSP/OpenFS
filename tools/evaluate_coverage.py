#!/usr/bin/env python3
"""Evaluate a Run against its Monitor's explicitly declared search scope."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json, sha256_file


ROOT = Path(__file__).resolve().parents[1]


def _monitor(root: Path, monitor_id: str) -> tuple[Path, dict[str, Any]]:
    matches = [
        path
        for path in sorted((root / "config" / "monitors").glob("*.json"))
        if read_json(path).get("monitor_id") == monitor_id
    ]
    if len(matches) != 1:
        raise ValueError(f"monitor must resolve exactly once: {monitor_id}")
    return matches[0], read_json(matches[0])


def evaluate_coverage(root: Path, *, run_id: str, evaluated_at: str | None = None) -> dict[str, Any]:
    manifest = read_json(root / "runs" / run_id / "manifest.json")
    monitor_path, monitor = _monitor(root, manifest["monitor_id"])
    source_results = []
    for path in sorted((root / "proposals" / "sources" / run_id).glob("*.json")):
        source_results.append(read_json(path))
    queries = [result["query_receipt"]["query"] for result in source_results]
    sources = [result["source_receipt"] for result in source_results]
    expected_queries = set(monitor.get("query_families", []))
    expected_classes = set(monitor.get("source_classes", []))
    expected_languages = set(monitor.get("languages", []))
    observed_queries = set(queries)
    observed_classes = {source["source_class"] for source in sources}
    observed_languages = {source["language"] for source in sources}
    failures = [
        failure
        for result in source_results
        for failure in result["query_receipt"].get("failures", [])
    ]
    gaps = {
        "missing_queries": sorted(expected_queries - observed_queries),
        "missing_source_classes": sorted(expected_classes - observed_classes),
        "missing_languages": sorted(expected_languages - observed_languages),
        "query_failures": failures,
    }
    monitor_relative = monitor_path.relative_to(root).as_posix()
    snapshot_match = manifest.get("policy_hashes", {}).get(monitor_relative) == sha256_file(
        monitor_path
    )
    if not snapshot_match:
        gaps["monitor_snapshot_mismatch"] = [monitor_relative]
    status = (
        "met-declared-scope"
        if not any(gaps.values()) and len(source_results) >= len(expected_queries)
        else "incomplete"
    )
    rights_counts: dict[str, int] = {}
    for source in sources:
        decision = source["rights"]["acquisition_decision"]
        rights_counts[decision] = rights_counts.get(decision, 0) + 1
    return {
        "schema_version": "0.1.0",
        "run_id": run_id,
        "monitor_id": monitor["monitor_id"],
        "evaluated_at": evaluated_at or isoformat(),
        "coverage_status": status,
        "monitor_snapshot_match": snapshot_match,
        "expected": {
            "query_families": sorted(expected_queries),
            "source_classes": sorted(expected_classes),
            "languages": sorted(expected_languages),
        },
        "observed": {
            "source_count": len(sources),
            "primary_source_count": sum(source["primary_source"] for source in sources),
            "origin_group_count": len({source["origin_group_id"] for source in sources}),
            "query_families": sorted(observed_queries),
            "source_classes": sorted(observed_classes),
            "languages": sorted(observed_languages),
            "rights_decisions": rights_counts,
        },
        "gaps": gaps,
        "caveat": (
            "This status measures only the declared Monitor scope. It never means that "
            "the Web or the research domain was searched completely."
        ),
    }


def record_coverage(root: Path, report: dict[str, Any]) -> dict[str, Any]:
    run_id = report["run_id"]
    manifest_path = root / "runs" / run_id / "manifest.json"
    manifest = read_json(manifest_path)
    receipts = []
    for path in sorted((root / "proposals" / "sources" / run_id).glob("*.json")):
        receipts.append(read_json(path)["query_receipt"])
    manifest["query_receipts"] = receipts
    manifest["research_status"] = (
        "ready-for-independent-review"
        if report["coverage_status"] == "met-declared-scope"
        else "coverage-incomplete"
    )
    manifest.setdefault("metrics", {})["coverage"] = {
        "status": report["coverage_status"],
        "source_count": report["observed"]["source_count"],
        "origin_group_count": report["observed"]["origin_group_count"],
        "gap_count": sum(len(value) for value in report["gaps"].values()),
    }
    atomic_write_json(manifest_path, manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = evaluate_coverage(args.root, run_id=args.run_id)
    output = args.output or args.root / "runs" / args.run_id / "coverage.json"
    atomic_write_json(output, report)
    record_coverage(args.root, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
