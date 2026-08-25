#!/usr/bin/env python3
"""Validate P0 cross-roadmap dependency direction, references, and Gap propagation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


BLUEPRINT_ID = "RM-X-BLUEPRINT"


def _duplicates(values: list[Any]) -> set[Any]:
    return {value for value in values if values.count(value) > 1}


def evaluate(register: dict[str, Any], roadmaps: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    roadmap_ids = {item["roadmap_id"] for item in roadmaps}
    source_owners = {
        source["source_id"]: item["roadmap_id"]
        for item in roadmaps
        for source in item["sources"]
    }
    source_ids = set(source_owners)
    milestone_owners = {
        milestone["milestone_id"]: item["roadmap_id"]
        for item in roadmaps
        for lane in item["lanes"]
        for milestone in lane["milestones"]
    }
    milestone_ids = set(milestone_owners)
    gaps = {gap["gap_id"]: gap for item in roadmaps for gap in item["coverage_gaps"]}
    p0_gaps = {
        gap_id
        for gap_id, gap in gaps.items()
        if gap["priority"] == "P0" and gap["status"] == "open"
    }
    source_dependency_owners = {
        dependency["dependency_id"]: item["roadmap_id"]
        for item in roadmaps
        for dependency in item["dependencies"]
    }
    source_dependency_ids = set(source_dependency_owners)
    gap_owners = {
        gap["gap_id"]: item["roadmap_id"]
        for item in roadmaps
        for gap in item["coverage_gaps"]
    }

    dependencies = register["dependencies"]
    dependency_ids = [item["dependency_id"] for item in dependencies]
    for value in sorted(_duplicates(dependency_ids)):
        errors.append(f"dependencies: duplicate dependency_id {value}")
    pairs = [
        (item["upstream_roadmap_id"], item["downstream_roadmap_id"])
        for item in dependencies
    ]
    for value in sorted(_duplicates(pairs)):
        errors.append(f"dependencies: duplicate directed pair {value[0]} -> {value[1]}")

    graph: dict[str, set[str]] = {roadmap_id: set() for roadmap_id in roadmap_ids}
    edge_gap_refs: set[str] = set()
    for dependency in dependencies:
        dependency_id = dependency["dependency_id"]
        upstream = dependency["upstream_roadmap_id"]
        downstream = dependency["downstream_roadmap_id"]
        if upstream not in roadmap_ids or downstream not in roadmap_ids:
            errors.append(f"{dependency_id}: unknown roadmap endpoint")
            continue
        if upstream == downstream:
            errors.append(f"{dependency_id}: self-dependency is not allowed")
        graph[upstream].add(downstream)
        endpoint_roadmaps = {upstream, downstream}
        for label, refs, known in (
            ("source_ids", set(dependency["source_ids"]), source_ids),
            ("source_dependency_ids", set(dependency["source_dependency_ids"]), source_dependency_ids),
            ("gate_refs", set(dependency["gate_refs"]), milestone_ids),
            ("coverage_gap_refs", set(dependency["coverage_gap_refs"]), set(gaps)),
        ):
            unknown = refs - known
            if unknown:
                errors.append(f"{dependency_id}: unknown {label} {sorted(unknown)}")
        for label, refs, owners, allowed_owners in (
            ("source_ids", dependency["source_ids"], source_owners, endpoint_roadmaps),
            (
                "source_dependency_ids",
                dependency["source_dependency_ids"],
                source_dependency_owners,
                endpoint_roadmaps,
            ),
            (
                "gate_refs",
                dependency["gate_refs"],
                milestone_owners,
                endpoint_roadmaps | {BLUEPRINT_ID},
            ),
            ("coverage_gap_refs", dependency["coverage_gap_refs"], gap_owners, endpoint_roadmaps),
        ):
            unrelated = [
                ref for ref in refs
                if ref in owners and owners[ref] not in allowed_owners
            ]
            if unrelated:
                errors.append(
                    f"{dependency_id}: {label} belong to unrelated roadmaps {sorted(unrelated)}"
                )
        edge_gap_refs.update(dependency["coverage_gap_refs"])

    indegree = {node: 0 for node in graph}
    for downstreams in graph.values():
        for downstream in downstreams:
            indegree[downstream] += 1
    ready = [node for node, count in indegree.items() if count == 0]
    visited: list[str] = []
    while ready:
        node = ready.pop()
        visited.append(node)
        for downstream in graph[node]:
            indegree[downstream] -= 1
            if indegree[downstream] == 0:
                ready.append(downstream)
    if set(visited) != roadmap_ids:
        errors.append(f"dependency graph contains a cycle involving {sorted(roadmap_ids - set(visited))}")

    for roadmap_id in sorted(roadmap_ids - {BLUEPRINT_ID}):
        frontier = [roadmap_id]
        reached: set[str] = set()
        while frontier:
            node = frontier.pop()
            if node in reached:
                continue
            reached.add(node)
            frontier.extend(graph.get(node, set()))
        if BLUEPRINT_ID not in reached:
            errors.append(f"{roadmap_id}: no directed path reaches {BLUEPRINT_ID}")

    portfolio_gate_gaps = set(register["portfolio_gate_gap_refs"])
    if edge_gap_refs & portfolio_gate_gaps:
        errors.append(
            "portfolio_gate_gap_refs: a non-causal portfolio gate must not also be assigned to an edge"
        )
    represented_p0 = (edge_gap_refs & p0_gaps) | portfolio_gate_gaps
    if represented_p0 != p0_gaps:
        errors.append(
            "P0 Gap propagation mismatch; "
            f"missing={sorted(p0_gaps - represented_p0)}, extra={sorted(represented_p0 - p0_gaps)}"
        )
    unknown_portfolio_gaps = portfolio_gate_gaps - p0_gaps
    if unknown_portfolio_gaps:
        errors.append(f"portfolio_gate_gap_refs: not open P0 Gaps {sorted(unknown_portfolio_gaps)}")

    return {
        "export_id": register["export_id"],
        "counts": {
            "roadmaps": len(roadmap_ids),
            "dependencies": len(dependencies),
            "high_criticality": sum(item["criticality"] == "high" for item in dependencies),
            "open_p0_gaps": len(p0_gaps),
            "edge_propagated_p0_gaps": len(edge_gap_refs & p0_gaps),
            "portfolio_gate_p0_gaps": len(portfolio_gate_gaps),
        },
        "calculation_errors": errors,
        "candidate_ready_for_consensus": not errors,
        "consensus_status": register["consensus_status"],
        "gaps_remain_open": True,
        "note": (
            "Validator success establishes structural dependency integrity and P0 Gap propagation only; "
            "it does not validate causal claims, close a Gap, satisfy Consensus, or authorize adoption."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "register",
        nargs="?",
        type=Path,
        default=Path("knowledge/public/dependencies/p0-roadmap-dependencies.json"),
    )
    parser.add_argument(
        "--roadmap-dir", type=Path, default=Path("knowledge/public/roadmaps")
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    register_path = args.register if args.register.is_absolute() else root / args.register
    roadmap_dir = args.roadmap_dir if args.roadmap_dir.is_absolute() else root / args.roadmap_dir
    register = json.loads(register_path.read_text(encoding="utf-8"))
    roadmaps = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(roadmap_dir.glob("*.json"))
    ]
    result = evaluate(register, roadmaps)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["candidate_ready_for_consensus"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
