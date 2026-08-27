#!/usr/bin/env python3
"""Gate production Agents on exact, current, independently reviewed evaluations."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from check_agent_evaluation_bundle import evaluate as evaluate_bundle
from check_agent_evaluation_task_suite import evaluate as evaluate_suite
from openfs_runtime import atomic_write_json, isoformat, read_json, stable_digest


ROOT = Path(__file__).resolve().parents[1]
COMMIT = re.compile(r"^[0-9a-f]{40}$")
HARNESS = re.compile(r"^HAR-[A-Z0-9-]+$")


def _instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("evaluation readiness timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def _path(root: Path, ref: str) -> Path:
    relative = PurePosixPath(ref)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"evaluation reference is not repository-relative: {ref}")
    return root.joinpath(*relative.parts)


def _unconfigured(value: Any) -> bool:
    return str(value or "").strip().lower() in {"", "none", "unconfigured"}


def _matching_bundle_refs(
    *,
    agent: dict[str, Any],
    policy: dict[str, Any],
    as_of: datetime,
    bundle_paths: list[tuple[str, Path]],
) -> list[str]:
    matches: list[str] = []
    maximum_age = timedelta(days=int(policy["maximum_bundle_age_days"]))
    for source_ref, path in bundle_paths:
        bundle = read_json(path)
        system = bundle.get("system_under_test", {})
        model = system.get("model", {})
        harness = system.get("harness", {})
        if system.get("agent_id") != agent.get("agent_id"):
            continue
        if system.get("role") != agent.get("role"):
            continue
        if system.get("origin_group") != agent.get("agent_independence_group"):
            continue
        if system.get("prompt_profile") != agent.get("prompt_profile"):
            continue
        if model.get("provider") != agent.get("provider"):
            continue
        if model.get("model_id") != agent.get("model_id"):
            continue
        if harness.get("harness_id") != agent.get("harness_id"):
            continue
        if harness.get("repository_url") != agent.get("harness_repository_url"):
            continue
        if harness.get("commit") != agent.get("harness_commit"):
            continue
        if bundle.get("status") != policy["required_bundle_status"]:
            continue
        if bundle.get("consensus_status") != policy["required_consensus_status"]:
            continue
        holdout = policy["formal_holdout"]
        if bundle.get("benchmark", {}).get("task_set_digest") != holdout.get(
            "task_set_digest"
        ):
            continue
        dataset = bundle.get("dataset_control", {})
        if dataset.get("reference_answer_digest") != holdout.get(
            "answer_set_digest"
        ):
            continue
        if dataset.get("holdout_attestation_ref") != holdout.get("attestation_ref"):
            continue
        created_at = bundle.get("provenance", {}).get("created_at")
        if not created_at:
            continue
        created = _instant(created_at)
        if created > as_of or as_of - created > maximum_age:
            continue
        if len(bundle.get("runs", [])) < int(policy["minimum_repetitions"]):
            continue
        result = evaluate_bundle(bundle)
        if not result["candidate_ready_for_consensus"]:
            continue
        matches.append(source_ref)
    return matches


def _pinned_payload(
    root: Path,
    manifest: dict[str, Any],
    source_ref: str,
) -> tuple[dict[str, Any], Path]:
    snapshot_ref = manifest.get("configuration_snapshots", {}).get(source_ref)
    expected_digest = manifest.get("policy_hashes", {}).get(source_ref)
    if not snapshot_ref or not expected_digest:
        raise ValueError(f"Run lacks pinned evaluation input: {source_ref}")
    path = _path(root, snapshot_ref)
    payload = read_json(path)
    if stable_digest(payload) != expected_digest:
        raise ValueError(f"pinned evaluation input digest differs: {source_ref}")
    return payload, path


def evaluate(
    root: Path,
    *,
    agent_ids: list[str] | None = None,
    run_id: str | None = None,
    evaluated_at: str | None = None,
) -> dict[str, Any]:
    timestamp = evaluated_at or isoformat()
    as_of = _instant(timestamp)
    if run_id:
        manifest = read_json(root / "runs" / run_id / "manifest.json")
        policy, _ = _pinned_payload(
            root, manifest, "config/agent-evaluation-policy.json"
        )
        registry, _ = _pinned_payload(root, manifest, "config/agent-registry.json")
        suite, suite_path = _pinned_payload(
            root, manifest, policy["development_suite_ref"]
        )
        bundle_paths = []
        for source_ref in sorted(manifest.get("configuration_snapshots", {})):
            if not source_ref.startswith("proposals/agent-evaluations/AEVAL-"):
                continue
            _, path = _pinned_payload(root, manifest, source_ref)
            bundle_paths.append((source_ref, path))
    else:
        policy = read_json(root / "config" / "agent-evaluation-policy.json")
        registry = read_json(root / "config" / "agent-registry.json")
        suite_path = _path(root, policy["development_suite_ref"])
        suite = read_json(suite_path)
        bundle_paths = [
            (str(path.relative_to(root)), path)
            for path in sorted(
                (root / "proposals" / "agent-evaluations").glob("AEVAL-*.json")
            )
        ]
    suite_result = evaluate_suite(suite, root)

    by_id = {agent["agent_id"]: agent for agent in registry.get("agents", [])}
    if agent_ids:
        unknown = sorted(set(agent_ids) - set(by_id))
        if unknown:
            raise ValueError(f"unknown Agent IDs: {unknown}")
        selected = [by_id[agent_id] for agent_id in agent_ids]
    else:
        selected = [
            agent
            for agent in registry.get("agents", [])
            if agent.get("enabled")
            and agent.get("role") in set(policy["applicable_roles"])
        ]

    holdout = policy["formal_holdout"]
    formal_holdout_available = (
        holdout["status"] == "available"
        and not _unconfigured(holdout["custodian_id"])
        and isinstance(holdout["task_set_digest"], str)
        and isinstance(holdout["answer_set_digest"], str)
        and isinstance(holdout["attestation_ref"], str)
    )
    agent_reports = []
    for agent in selected:
        blockers: list[str] = []
        if not agent.get("enabled"):
            blockers.append("agent-not-enabled")
        if agent.get("role") not in policy["applicable_roles"]:
            blockers.append("agent-role-not-covered")
        if _unconfigured(agent.get("model_id")):
            blockers.append("model-id-unconfigured")
        if not HARNESS.fullmatch(str(agent.get("harness_id", ""))):
            blockers.append("harness-id-unconfigured-or-invalid")
        if not str(agent.get("harness_repository_url", "")).startswith("https://"):
            blockers.append("harness-repository-unconfigured-or-invalid")
        if not COMMIT.fullmatch(str(agent.get("harness_commit", ""))):
            blockers.append("harness-commit-unconfigured-or-invalid")
        bundle_refs = []
        if not blockers:
            bundle_refs = _matching_bundle_refs(
                agent=agent,
                policy=policy,
                as_of=as_of,
                bundle_paths=bundle_paths,
            )
            if not bundle_refs:
                blockers.append("current-accepted-evaluation-bundle-missing")
        if not suite_result["ready_for_public_development_runs"]:
            blockers.append("public-development-suite-invalid")
        if not formal_holdout_available:
            blockers.append("formal-holdout-unavailable")
        agent_reports.append(
            {
                "agent_id": agent["agent_id"],
                "enabled": agent.get("enabled") is True,
                "role": str(agent.get("role", "unconfigured")),
                "model_id": str(agent.get("model_id", "unconfigured")),
                "harness_id": str(agent.get("harness_id", "unconfigured")),
                "status": "ready" if not blockers else "blocked",
                "blockers": sorted(set(blockers)),
                "accepted_bundle_refs": bundle_refs,
            }
        )

    checks = {
        "policy_enforced": policy["status"] == "enforced",
        "public_development_suite_valid": suite_result[
            "ready_for_public_development_runs"
        ],
        "formal_holdout_available": formal_holdout_available,
        "requested_agents_present": bool(selected),
        "all_requested_agents_ready": bool(selected)
        and all(agent["status"] == "ready" for agent in agent_reports),
    }
    blockers = sorted(name for name, passed in checks.items() if not passed)
    return {
        "schema_version": "0.1.0",
        "policy_id": policy["policy_id"],
        "evaluated_at": timestamp,
        "status": "ready" if not blockers else "blocked",
        "checks": checks,
        "blockers": blockers,
        "agents": agent_reports,
        "configuration_digests": {
            "policy": stable_digest(policy),
            "agent_registry": stable_digest(registry),
            "development_suite": stable_digest(suite),
        },
        "effect": policy["effect"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--agent-id", action="append")
    parser.add_argument("--run-id")
    parser.add_argument("--evaluated-at")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-ready", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = evaluate(
        args.root,
        agent_ids=args.agent_id,
        run_id=args.run_id,
        evaluated_at=args.evaluated_at,
    )
    if args.output:
        output = args.output if args.output.is_absolute() else args.root / args.output
        atomic_write_json(output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if args.require_ready and report["status"] != "ready" else 0


if __name__ == "__main__":
    raise SystemExit(main())
