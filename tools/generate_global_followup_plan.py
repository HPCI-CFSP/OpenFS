#!/usr/bin/env python3
"""Turn worldwide Coverage gaps into a bounded next-Run discovery plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json, stable_digest


ROOT = Path(__file__).resolve().parents[1]
GAP_PRIORITY = (
    "missing_source_requirements",
    "missing_organization_types",
    "missing_world_regions",
    "missing_technology_categories",
    "missing_maturity_signals",
    "missing_result_signals",
    "missing_languages",
)


def _query_text(target: str, dimensions: set[str], generation: int) -> str:
    if target == "standards-body":
        base = (
            "HPC AI systems interoperability standard specification memory "
            "interconnect storage software standards organization"
        )
    elif target == "peer-reviewed-research":
        base = (
            "HPC AI for Science system architecture performance energy evaluation "
            "peer reviewed conference paper"
        )
    elif "missing_world_regions" in dimensions:
        base = f'"{target}" national HPC AI for Science infrastructure roadmap official'
    elif "missing_technology_categories" in dimensions:
        base = f'"{target}" HPC AI for Science architecture benchmark roadmap'
    elif "missing_maturity_signals" in dimensions:
        base = f'HPC AI for Science "{target}" prototype procurement deployment record'
    elif "missing_result_signals" in dimensions:
        base = f'HPC AI for Science "{target}" failed discontinued limitation evaluation'
    elif "missing_languages" in dimensions:
        base = f'HPC AI for Science infrastructure roadmap language:{target}'
    else:
        base = f'HPC AI for Science "{target}" primary source'
    if generation == 1:
        return base
    if generation == 2:
        return base + " native language site:gov OR site:edu OR standards"
    return base + " independent evaluation negative results procurement record"


def _source_classes(target: str, monitor: dict[str, Any]) -> list[str]:
    configured = set(monitor.get("source_classes", []))
    if target in configured:
        return [target]
    if target == "standards-body" and "standards-body" in configured:
        return ["standards-body"]
    return sorted(configured)


def build_plan(
    root: Path,
    *,
    run_id: str,
    maximum_queries: int = 8,
    generated_at: str | None = None,
) -> dict[str, Any]:
    if maximum_queries < 1:
        raise ValueError("maximum_queries must be positive")
    manifest = read_json(root / "runs" / run_id / "manifest.json")
    if manifest.get("status") not in {"completed", "partial"}:
        raise ValueError("follow-up planning requires a durable completed or partial Run")
    coverage_ref = f"runs/{run_id}/coverage.json"
    brief_ref = f"reviews/briefs/{run_id}.json"
    coverage = read_json(root / coverage_ref)
    brief = read_json(root / brief_ref)
    monitor_ref = next(
        key
        for key in manifest.get("configuration_snapshots", {})
        if key.startswith("config/monitors/")
    )
    monitor = read_json(root / manifest["configuration_snapshots"][monitor_ref])
    if not monitor.get("scope_ref"):
        raise ValueError("global follow-up planning requires a scoped worldwide Monitor")

    targets: dict[str, set[str]] = {}
    for dimension in GAP_PRIORITY:
        for target in coverage.get("gaps", {}).get(dimension, []):
            if not isinstance(target, str):
                continue
            targets.setdefault(target, set()).add(dimension)

    predecessor_ref = manifest.get("followup_plan", {}).get("source_ref")
    predecessor = read_json(root / predecessor_ref) if predecessor_ref else None
    previous_by_targets = {
        tuple(sorted((item["dimension"], item["value"]) for item in query.get("coverage_targets", []))): query
        for query in (predecessor or {}).get("queries", [])
    }
    queries = []
    ordered_targets = sorted(
        targets.items(),
        key=lambda item: (
            min(GAP_PRIORITY.index(value) for value in item[1]),
            item[0],
        ),
    )
    for target, dimensions in ordered_targets[:maximum_queries]:
        coverage_targets = [
            {"dimension": dimension, "value": target}
            for dimension in GAP_PRIORITY
            if dimension in dimensions
        ]
        identity = tuple(
            sorted((item["dimension"], item["value"]) for item in coverage_targets)
        )
        previous = previous_by_targets.get(identity)
        generation = int((previous or {}).get("search_generation", 0)) + 1
        query_id = f"GLOBAL-FOLLOWUP-{len(queries) + 1:03d}"
        query = {
            "query_id": query_id,
            "query": _query_text(target, dimensions, generation),
            "query_role": "coverage-followup",
            "source_classes": _source_classes(target, monitor),
            "coverage_targets": coverage_targets,
            "search_generation": generation,
            "search_strategy": (
                "targeted-primary"
                if generation == 1
                else "cross-domain-native-language"
                if generation == 2
                else "independent-negative-records"
            ),
            "rationale": "Unmet worldwide Coverage requirement from the preceding Run.",
        }
        if previous and predecessor_ref:
            query["previous_query_ref"] = (
                f"{predecessor_ref}#{previous['query_id']}"
            )
            query["previous_query_digest"] = stable_digest(previous)
        queries.append(query)

    timestamp = generated_at or isoformat()
    identity = {
        "base_run_id": run_id,
        "coverage_digest": stable_digest(coverage),
        "brief_digest": stable_digest(brief),
        "queries": queries,
    }
    return {
        "schema_version": "0.1.0",
        "followup_plan_id": f"GFP-{stable_digest(identity)[:12].upper()}",
        "monitor_id": manifest["monitor_id"],
        "task_id": manifest["task_id"],
        "base_run_id": run_id,
        "base_run_status": manifest["status"],
        "generated_at": timestamp,
        "status": "generated-for-research" if queries else "no-followup-required",
        "publication_status": "internal-review-only",
        "input_brief_ref": brief_ref,
        "input_brief_digest": stable_digest(brief),
        "input_coverage_ref": coverage_ref,
        "input_coverage_digest": stable_digest(coverage),
        "predecessor_plan": {
            "plan_ref": predecessor_ref,
            "plan_id": predecessor["followup_plan_id"],
            "plan_digest": stable_digest(predecessor),
        }
        if predecessor
        else None,
        "limits": {"maximum_queries": maximum_queries},
        "queries": queries,
        "caveats": [
            "Follow-up queries are internal discovery instructions, not findings.",
            "Each query remains subject to Source rights, Evidence, and Consensus gates.",
            "The next Run must snapshot this plan before execution.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--maximum-queries", type=int, default=8)
    parser.add_argument("--generated-at")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    plan = build_plan(
        args.root,
        run_id=args.run_id,
        maximum_queries=args.maximum_queries,
        generated_at=args.generated_at,
    )
    output = args.output or Path(
        f"reviews/followups/{args.run_id}-global-coverage.json"
    )
    output = output if output.is_absolute() else args.root / output
    atomic_write_json(output, plan)
    print(
        json.dumps(
            {
                "output": str(output),
                "followup_plan_id": plan["followup_plan_id"],
                "query_count": len(plan["queries"]),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
