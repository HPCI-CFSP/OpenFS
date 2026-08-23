#!/usr/bin/env python3
"""Check whether a Run has enough configured independent review capacity."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json, stable_digest


ROOT = Path(__file__).resolve().parents[1]


def _usable(agent: dict[str, Any], *, pilot: bool) -> bool:
    return bool(
        (agent.get("enabled") or pilot)
        and agent.get("provider") not in {None, "unconfigured", "deterministic-local"}
        and agent.get("model_family") not in {None, "unconfigured", "none"}
        and agent.get("agent_independence_group")
        not in {None, "non-voting-control-plane"}
    )


def evaluate_readiness(
    *,
    run_id: str,
    registry: dict[str, Any],
    policy: dict[str, Any],
    object_types: list[str],
    pilot: bool,
    evaluated_at: str | None = None,
) -> dict[str, Any]:
    agents = registry.get("agents", [])
    authors = [
        agent
        for agent in agents
        if agent.get("role") == "synthesis" and _usable(agent, pilot=pilot)
    ]
    author_groups = {
        agent["agent_independence_group"] for agent in authors
    }
    reviewers = [
        agent
        for agent in agents
        if agent.get("role") in {"validator", "critic"}
        and _usable(agent, pilot=pilot)
    ]
    independent_reviewers = [
        agent
        for agent in reviewers
        if agent["agent_independence_group"] not in author_groups
    ]
    independent_groups = {
        agent["agent_independence_group"] for agent in independent_reviewers
    }
    independent_critics = [
        agent for agent in independent_reviewers if agent.get("role") == "critic"
    ]
    results: list[dict[str, Any]] = []
    unmet: list[str] = []
    for object_type in object_types:
        rule = policy.get("rules", {}).get(object_type)
        if not rule:
            raise ValueError(f"No consensus rule for object type: {object_type}")
        checks = {
            "assessment_capacity": len(reviewers) >= int(rule["minimum_assessments"]),
            "independent_support_group_capacity": len(independent_groups)
            >= int(rule["minimum_support_independence_groups"]),
            "falsification_capacity": bool(independent_critics)
            if rule.get("require_falsification_review")
            else True,
        }
        for name, passed in checks.items():
            if not passed:
                unmet.append(f"{object_type}:{name}")
        results.append(
            {
                "object_type": object_type,
                "status": "ready" if all(checks.values()) else "incomplete",
                "checks": checks,
                "required": {
                    "minimum_assessments": rule["minimum_assessments"],
                    "minimum_support_independence_groups": rule[
                        "minimum_support_independence_groups"
                    ],
                    "require_falsification_review": bool(
                        rule.get("require_falsification_review")
                    ),
                },
                "available": {
                    "reviewer_agent_ids": sorted(
                        agent["agent_id"] for agent in reviewers
                    ),
                    "author_independence_groups": sorted(author_groups),
                    "independent_reviewer_agent_ids": sorted(
                        agent["agent_id"] for agent in independent_reviewers
                    ),
                    "independent_reviewer_groups": sorted(independent_groups),
                    "independent_critic_agent_ids": sorted(
                        agent["agent_id"] for agent in independent_critics
                    ),
                },
            }
        )
    return {
        "schema_version": "0.1.0",
        "run_id": run_id,
        "evaluated_at": evaluated_at or isoformat(),
        "status": "ready" if not unmet else "incomplete",
        "pilot_mode": pilot,
        "registry_digest": stable_digest(registry),
        "policy_id": policy["policy_id"],
        "object_type_results": results,
        "unmet_requirements": sorted(set(unmet)),
        "effect": (
            "An incomplete preflight permits provisional research, but no proposal "
            "may be treated as formally accepted until the Consensus Gate passes."
        ),
    }


def record_readiness(root: Path, report: dict[str, Any]) -> dict[str, Any]:
    run_id = report["run_id"]
    report_ref = f"runs/{run_id}/consensus-readiness.json"
    atomic_write_json(root / report_ref, report)
    manifest_path = root / "runs" / run_id / "manifest.json"
    manifest = read_json(manifest_path)
    manifest["consensus_readiness_ref"] = report_ref
    manifest.setdefault("metrics", {})["consensus_readiness"] = report["status"]
    atomic_write_json(manifest_path, manifest)
    exception_path = root / "reviews" / "exceptions" / run_id / "CONSENSUS-READINESS.json"
    if report["status"] == "incomplete":
        atomic_write_json(
            exception_path,
            {
                "schema_version": "0.1.0",
                "exception_id": f"EXC-{run_id}-CONSENSUS-READINESS",
                "run_id": run_id,
                "status": "open",
                "recorded_at": report["evaluated_at"],
                "exception_kind": "consensus-capacity",
                "unmet_requirements": report["unmet_requirements"],
                "requires_owner_action": True,
                "suggested_action": (
                    "Configure and enable genuinely independent validator and critic "
                    "agents, then start a new Run with the updated registry snapshot."
                ),
            },
        )
    else:
        exception_path.unlink(missing_ok=True)
    return manifest


def evaluate_run(root: Path, run_id: str) -> dict[str, Any]:
    manifest = read_json(root / "runs" / run_id / "manifest.json")
    snapshots = manifest.get("configuration_snapshots", {})
    registry = read_json(
        root / snapshots.get("config/agent-registry.json", "config/agent-registry.json")
    )
    policy = read_json(
        root
        / snapshots.get("config/consensus-policy.json", "config/consensus-policy.json")
    )
    monitor_source = next(
        key for key in manifest.get("policy_hashes", {}) if key.startswith("config/monitors/")
    )
    monitor = read_json(root / snapshots.get(monitor_source, monitor_source))
    return evaluate_readiness(
        run_id=run_id,
        registry=registry,
        policy=policy,
        object_types=monitor.get("consensus_object_types", ["claim"]),
        pilot=manifest.get("mode") == "pilot",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = evaluate_run(args.root, args.run_id)
    record_readiness(args.root, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
