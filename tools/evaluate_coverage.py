#!/usr/bin/env python3
"""Evaluate a Run against its Monitor's explicitly declared search scope."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json, stable_digest


ROOT = Path(__file__).resolve().parents[1]


def _monitor(root: Path, manifest: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    monitor_id = manifest["monitor_id"]
    matches = [
        path
        for path in sorted((root / "config" / "monitors").glob("*.json"))
        if read_json(path).get("monitor_id") == monitor_id
    ]
    if len(matches) != 1:
        raise ValueError(f"monitor must resolve exactly once: {monitor_id}")
    relative = matches[0].relative_to(root).as_posix()
    snapshot_ref = manifest.get("configuration_snapshots", {}).get(relative)
    if snapshot_ref:
        return relative, read_json(root / snapshot_ref)
    return relative, read_json(matches[0])


def evaluate_coverage(root: Path, *, run_id: str, evaluated_at: str | None = None) -> dict[str, Any]:
    manifest = read_json(root / "runs" / run_id / "manifest.json")
    monitor_relative, monitor = _monitor(root, manifest)
    source_results = []
    for path in sorted((root / "proposals" / "sources" / run_id).glob("*.json")):
        source_results.append(read_json(path))
    queries = [result["query_receipt"]["query"] for result in source_results]
    all_sources = [result["source_receipt"] for result in source_results]
    unique_sources = {source["source_id"]: source for source in all_sources}
    sources = list(unique_sources.values())
    expected_coverage_queries = set(monitor.get("query_families", []))
    expected_falsification_queries = set(monitor.get("falsification_queries", []))
    expected_queries = expected_coverage_queries | expected_falsification_queries
    expected_languages = set(monitor.get("languages", []))
    observed_queries = set(queries)
    observed_classes = {source["source_class"] for source in sources}
    observed_languages = {source["language"] for source in sources}
    failures = [
        failure
        for result in source_results
        for failure in result["query_receipt"].get("failures", [])
    ]
    query_source_counts = {
        query: len(
            {
                result["source_receipt"]["source_id"]
                for result in source_results
                if result["query_receipt"]["query"] == query
            }
        )
        for query in sorted(expected_queries)
    }
    minimum_sources_per_query = int(monitor.get("minimum_sources_per_query", 1))
    below_minimum_queries = [
        {"query": query, "observed": count, "minimum": minimum_sources_per_query}
        for query, count in query_source_counts.items()
        if count < minimum_sources_per_query
    ]
    class_requirements = monitor.get("source_class_requirements", [])
    if not class_requirements:
        class_requirements = [
            {"requirement_id": item, "one_of": [item], "minimum_count": 1}
            for item in monitor.get("source_classes", [])
        ]
    class_requirement_results = []
    for requirement in class_requirements:
        observed_count = sum(
            source["source_class"] in set(requirement["one_of"])
            for source in sources
        )
        class_requirement_results.append(
            {
                "requirement_id": requirement["requirement_id"],
                "one_of": requirement["one_of"],
                "minimum_count": requirement["minimum_count"],
                "observed_count": observed_count,
                "met": observed_count >= requirement["minimum_count"],
            }
        )
    missing_requirements = [
        item["requirement_id"] for item in class_requirement_results if not item["met"]
    ]
    minimum_total_sources = int(monitor.get("minimum_total_sources", len(expected_queries)))
    minimum_origin_groups = int(monitor.get("minimum_origin_groups", 1))
    observed_origin_groups = {source["origin_group_id"] for source in sources}
    duplicate_source_ids = sorted(
        source_id
        for source_id in unique_sources
        if sum(source["source_id"] == source_id for source in all_sources) > 1
    )
    gaps = {
        "missing_queries": sorted(expected_queries - observed_queries),
        "below_minimum_queries": below_minimum_queries,
        "missing_source_requirements": missing_requirements,
        "missing_languages": sorted(expected_languages - observed_languages),
        "minimum_total_sources": (
            []
            if len(sources) >= minimum_total_sources
            else [{"observed": len(sources), "minimum": minimum_total_sources}]
        ),
        "minimum_origin_groups": (
            []
            if len(observed_origin_groups) >= minimum_origin_groups
            else [
                {
                    "observed": len(observed_origin_groups),
                    "minimum": minimum_origin_groups,
                }
            ]
        ),
        "duplicate_source_selections": duplicate_source_ids,
        "query_failures": failures,
    }
    snapshot_match = manifest.get("policy_hashes", {}).get(monitor_relative) == stable_digest(
        monitor
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
            "coverage_queries": sorted(expected_coverage_queries),
            "falsification_queries": sorted(expected_falsification_queries),
            "source_class_requirements": class_requirements,
            "languages": sorted(expected_languages),
            "minimum_sources_per_query": minimum_sources_per_query,
            "minimum_total_sources": minimum_total_sources,
            "minimum_origin_groups": minimum_origin_groups,
        },
        "observed": {
            "source_count": len(sources),
            "primary_source_count": sum(source["primary_source"] for source in sources),
            "origin_group_count": len(observed_origin_groups),
            "query_families": sorted(observed_queries),
            "query_source_counts": query_source_counts,
            "source_classes": sorted(observed_classes),
            "source_class_requirement_results": class_requirement_results,
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
