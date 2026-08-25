#!/usr/bin/env python3
"""Evaluate whether a Monitor may enter unattended production operation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from check_consensus_readiness import evaluate_readiness, monitor_object_types
from openfs_runtime import atomic_write_json, isoformat, read_json, stable_digest


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_HUMAN_CHECKS = {
    "public_information_boundary",
    "citation_sample",
    "coverage",
    "false_positive_review",
    "dissent_review",
    "cost_review",
}


def _reviewed_runs(
    root: Path, monitor: dict[str, Any]
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []
    for path in sorted((root / "reviews" / "run-approvals").glob("RUN-*.json")):
        approval = read_json(path)
        if approval.get("monitor_id") != monitor["monitor_id"]:
            continue
        reasons: list[str] = []
        run_id = approval.get("run_id", "")
        manifest_path = root / "runs" / run_id / "manifest.json"
        brief_path = root / approval.get("brief_ref", "")
        if approval.get("status") != "reviewed-pass":
            reasons.append("approval-status-is-not-reviewed-pass")
        if not manifest_path.is_file():
            reasons.append("run-manifest-missing")
        if not brief_path.is_file():
            reasons.append("review-brief-missing")
        checks = approval.get("checks", {})
        if set(checks) != REQUIRED_HUMAN_CHECKS or not all(checks.values()):
            reasons.append("required-human-checks-incomplete")
        if manifest_path.is_file():
            manifest = read_json(manifest_path)
            if stable_digest(manifest) != approval.get("manifest_digest"):
                reasons.append("run-manifest-digest-mismatch")
            if manifest.get("monitor_id") != monitor["monitor_id"]:
                reasons.append("run-monitor-mismatch")
            if manifest.get("mode") != "pilot" or manifest.get("status") != "completed":
                reasons.append("run-is-not-a-completed-pilot")
            if manifest.get("coverage_status") != "met-declared-scope":
                reasons.append("run-coverage-incomplete")
            if manifest.get("research_status") != "accepted":
                reasons.append("run-research-not-accepted")
            temporal = manifest.get("metrics", {}).get("temporal_integrity", {})
            if temporal.get("status") != "passed":
                reasons.append("run-temporal-integrity-not-passed")
        if brief_path.is_file() and stable_digest(read_json(brief_path)) != approval.get(
            "brief_digest"
        ):
            reasons.append("review-brief-digest-mismatch")
        summary = {
            "approval_ref": str(path.relative_to(root)),
            "approval_id": approval.get("approval_id"),
            "run_id": run_id,
            "reviewed_by": approval.get("reviewed_by"),
            "reviewed_at": approval.get("reviewed_at"),
            "valid": not reasons,
            "reasons": reasons,
        }
        (accepted if not reasons else rejected).append(summary)
    return accepted, rejected


def evaluate(
    root: Path,
    *,
    monitor_id: str,
    evaluated_at: str | None = None,
) -> dict[str, Any]:
    matches = [
        read_json(path)
        for path in sorted((root / "config" / "monitors").glob("*.json"))
        if read_json(path).get("monitor_id") == monitor_id
    ]
    if len(matches) != 1:
        raise ValueError(f"Monitor must resolve to exactly one configuration: {monitor_id}")
    monitor = matches[0]
    budgets = read_json(root / "config" / "budgets.json")
    registry = read_json(root / "config" / "agent-registry.json")
    policy = read_json(root / "config" / "consensus-policy.json")
    consensus = evaluate_readiness(
        run_id=f"PRODUCTION-{monitor_id}",
        registry=registry,
        policy=policy,
        object_types=monitor_object_types(monitor),
        pilot=False,
        evaluated_at=evaluated_at,
    )
    reviewed, invalid = _reviewed_runs(root, monitor)
    required_runs = int(monitor.get("manual_run_requirement", 0))
    maximum_cost = budgets.get("defaults", {}).get("maximum_cost_usd")
    checks = {
        "monitor_enabled": monitor.get("enabled") is True,
        "budget_approved": budgets.get("status") == "approved",
        "maximum_cost_configured": isinstance(maximum_cost, (int, float))
        and not isinstance(maximum_cost, bool)
        and maximum_cost > 0,
        "consensus_policy_calibrated": policy.get("calibration_status") == "calibrated",
        "consensus_capacity_ready": consensus["status"] == "ready",
        "reviewed_manual_runs_complete": required_runs > 0
        and len(reviewed) >= required_runs,
    }
    blockers = sorted(name for name, passed in checks.items() if not passed)
    return {
        "schema_version": "0.1.0",
        "monitor_id": monitor_id,
        "task_id": monitor["task_id"],
        "evaluated_at": evaluated_at or isoformat(),
        "status": "ready" if not blockers else "blocked",
        "checks": checks,
        "blockers": blockers,
        "manual_runs": {
            "required": required_runs,
            "valid_reviewed_count": len(reviewed),
            "valid": reviewed,
            "invalid": invalid,
        },
        "consensus": {
            "status": consensus["status"],
            "unmet_requirements": consensus["unmet_requirements"],
            "registry_digest": consensus["registry_digest"],
            "policy_id": consensus["policy_id"],
        },
        "configuration_digests": {
            "monitor": stable_digest(monitor),
            "budgets": stable_digest(budgets),
            "agent_registry": stable_digest(registry),
            "consensus_policy": stable_digest(policy),
        },
        "effect": (
            "Only a ready report permits unattended production scheduling. Pilot "
            "planning remains available for calibration while this report is blocked."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--monitor-id", required=True)
    parser.add_argument("--evaluated-at")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = evaluate(
        args.root, monitor_id=args.monitor_id, evaluated_at=args.evaluated_at
    )
    if args.output:
        output = args.output if args.output.is_absolute() else args.root / args.output
        atomic_write_json(output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["status"] == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
