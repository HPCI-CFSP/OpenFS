#!/usr/bin/env python3
"""Evaluate a Run against its Monitor's explicitly declared search scope."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json, stable_digest


ROOT = Path(__file__).resolve().parents[1]
NON_BLOCKING_FAILURE_KINDS = {"rights-excluded"}
GLOBAL_COVERAGE_DIMENSIONS = (
    "world_regions",
    "technology_categories",
    "organization_types",
    "maturity_signals",
    "result_signals",
)


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


def _snapshotted_config(
    root: Path, manifest: dict[str, Any], relative: str
) -> dict[str, Any]:
    snapshot_ref = manifest.get("configuration_snapshots", {}).get(relative)
    if not snapshot_ref:
        raise ValueError(f"Run does not snapshot required configuration: {relative}")
    return read_json(root / snapshot_ref)


def evaluate_coverage(root: Path, *, run_id: str, evaluated_at: str | None = None) -> dict[str, Any]:
    manifest = read_json(root / "runs" / run_id / "manifest.json")
    monitor_relative, monitor = _monitor(root, manifest)
    discovery_items = []
    for path in sorted((root / "queue" / run_id).glob("WORK-*.json")):
        item = read_json(path)
        if item.get("kind") == "source-discovery":
            discovery_items.append(item)
    discovery_results = []
    for path in sorted((root / "proposals" / "sources" / run_id).glob("*.json")):
        discovery_results.append(read_json(path))
    source_results = [
        result for result in discovery_results if result.get("object_type", "source") == "source"
    ]
    queries = [result["query_receipt"]["query"] for result in discovery_results]
    all_sources = [result["source_receipt"] for result in source_results]
    unique_sources = {source["source_id"]: source for source in all_sources}
    sources = list(unique_sources.values())
    expected_coverage_queries = set(monitor.get("query_families", []))
    expected_falsification_queries = set(monitor.get("falsification_queries", []))
    assigned_queries = {
        item.get("payload", {}).get("query")
        for item in discovery_items
        if item.get("payload", {}).get("query")
    }
    expected_queries = (
        expected_coverage_queries | expected_falsification_queries | assigned_queries
    )
    expected_languages = set(monitor.get("languages", []))
    observed_queries = set(queries)
    observed_classes = {source["source_class"] for source in sources}
    observed_languages = {source["language"] for source in sources}
    global_scope_ref = monitor.get("scope_ref")
    global_scope_id = None
    expected_global_coverage: dict[str, list[str]] = {}
    observed_global_coverage: dict[str, set[str]] = {
        dimension: set() for dimension in GLOBAL_COVERAGE_DIMENSIONS
    }
    unknown_global_tags = []
    untagged_source_ids = []
    if global_scope_ref:
        global_scope = _snapshotted_config(root, manifest, global_scope_ref)
        global_scope_id = global_scope.get("scope_id")
        taxonomy = global_scope.get("coverage_taxonomy", {})
        expected_global_coverage = taxonomy.get("required_for_initial_cycle", {})
        for source in sources:
            tags = source.get("coverage_tags")
            if not tags:
                untagged_source_ids.append(source["source_id"])
                continue
            for dimension in GLOBAL_COVERAGE_DIMENSIONS:
                values = set(tags.get(dimension, []))
                observed_global_coverage[dimension].update(values)
                for value in sorted(values - set(taxonomy.get(dimension, []))):
                    unknown_global_tags.append(
                        {
                            "source_id": source["source_id"],
                            "dimension": dimension,
                            "value": value,
                        }
                    )
    expected_subject_fields: dict[str, set[str]] = {}
    subject_registry_ref = monitor.get("subject_registry_ref")
    subject_registry_id = None
    if subject_registry_ref:
        registry = _snapshotted_config(root, manifest, subject_registry_ref)
        subject_registry_id = registry.get("registry_id")
        default_fields = set(registry.get("default_profile_fields", []))
        expected_subject_fields = {
            center["center_id"]: set(center.get("profile_fields", default_fields))
            for center in registry.get("centers", [])
        }
    observed_subject_fields: dict[str, set[str]] = {}
    for source in all_sources:
        assignment_scope = source.get("assignment_scope", {})
        for subject_id in assignment_scope.get("subject_ids", []):
            observed_subject_fields.setdefault(subject_id, set()).update(
                assignment_scope.get("profile_fields", [])
            )
    for result in discovery_results:
        assignment_scope = result.get("assignment_scope", {})
        for subject_id in assignment_scope.get("subject_ids", []):
            observed_subject_fields.setdefault(subject_id, set()).update(
                assignment_scope.get("profile_fields", [])
            )
    failures = [
        failure
        for result in discovery_results
        for failure in result["query_receipt"].get("failures", [])
    ]
    blocking_failures = [
        failure
        for failure in failures
        if failure.get("coverage_impact") == "blocking"
        or (
            "coverage_impact" not in failure
            and failure.get("kind") not in NON_BLOCKING_FAILURE_KINDS
        )
    ]
    query_warnings = [failure for failure in failures if failure not in blocking_failures]
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
    missing_subject_searches = sorted(
        set(expected_subject_fields) - set(observed_subject_fields)
    )
    unexpected_subject_searches = sorted(
        set(observed_subject_fields) - set(expected_subject_fields)
    )
    missing_subject_profile_queries = [
        {
            "subject_id": subject_id,
            "missing_profile_fields": sorted(
                fields - observed_subject_fields.get(subject_id, set())
            ),
        }
        for subject_id, fields in sorted(expected_subject_fields.items())
        if fields - observed_subject_fields.get(subject_id, set())
    ]
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
        "missing_subject_searches": missing_subject_searches,
        "unexpected_subject_searches": unexpected_subject_searches,
        "missing_subject_profile_queries": missing_subject_profile_queries,
        "query_failures": blocking_failures,
    }
    if global_scope_ref:
        for dimension in GLOBAL_COVERAGE_DIMENSIONS:
            gaps[f"missing_{dimension}"] = sorted(
                set(expected_global_coverage.get(dimension, []))
                - observed_global_coverage[dimension]
            )
        gaps["untagged_global_sources"] = sorted(untagged_source_ids)
        gaps["unknown_global_coverage_tags"] = unknown_global_tags
    snapshot_match = manifest.get("policy_hashes", {}).get(monitor_relative) == stable_digest(
        monitor
    )
    if not snapshot_match:
        gaps["monitor_snapshot_mismatch"] = [monitor_relative]
    status = (
        "met-declared-scope"
        if not any(gaps.values()) and len(discovery_results) >= len(expected_queries)
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
            "subject_registry_ref": subject_registry_ref,
            "subject_registry_id": subject_registry_id,
            "subject_count": len(expected_subject_fields),
            "subject_profile_fields": {
                subject_id: sorted(fields)
                for subject_id, fields in sorted(expected_subject_fields.items())
            },
            "global_scope_ref": global_scope_ref,
            "global_scope_id": global_scope_id,
            "global_coverage": expected_global_coverage,
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
            "reused_source_ids": duplicate_source_ids,
            "subject_count": len(observed_subject_fields),
            "subject_profile_query_fields": {
                subject_id: sorted(fields)
                for subject_id, fields in sorted(observed_subject_fields.items())
            },
            "query_warnings": query_warnings,
            "global_coverage": {
                dimension: sorted(values)
                for dimension, values in observed_global_coverage.items()
            },
            "no_result_query_count": sum(
                result.get("object_type") == "discovery_no_result"
                for result in discovery_results
            ),
        },
        "gaps": gaps,
        "caveat": (
            "This status measures only the declared Monitor scope. It never means that "
            "the Web or the research domain was searched completely. Subject profile "
            "query coverage records assigned searches, not verified evidence completeness."
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
    manifest["coverage_status"] = report["coverage_status"]
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
