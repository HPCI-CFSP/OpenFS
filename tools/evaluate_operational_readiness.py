#!/usr/bin/env python3
"""Aggregate local and owner-attested gates for unattended OpenFS operation."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from evaluate_monitor_readiness import evaluate as evaluate_monitor
from openfs_runtime import atomic_write_json, isoformat, read_json


ROOT = Path(__file__).resolve().parents[1]


def _instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("readiness timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def _repository_path(root: Path, ref: str) -> Path:
    relative = PurePosixPath(ref)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"activation reference is not repository-relative: {ref}")
    return root.joinpath(*relative.parts)


def evaluate(root: Path, *, evaluated_at: str | None = None) -> dict[str, Any]:
    timestamp = evaluated_at or isoformat()
    now = _instant(timestamp)
    policy = read_json(root / "config" / "activation-policy.json")
    attestations = read_json(root / "config" / "owner-controls.json")

    workflow_gates = []
    for item in policy["required_workflow_gates"]:
        path = _repository_path(root, item["workflow_ref"])
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        passed = path.is_file() and item["variable"] in text
        workflow_gates.append(
            {
                "control_id": item["control_id"],
                "ref": item["workflow_ref"],
                "passed": passed,
                "reason": (
                    f"workflow declares the {item['variable']} activation gate"
                    if passed
                    else f"workflow or {item['variable']} activation gate is missing"
                ),
            }
        )

    production_components = []
    for item in policy["required_production_components"]:
        component_path = _repository_path(root, item["path"])
        text = component_path.read_text(encoding="utf-8") if component_path.is_file() else ""
        missing_markers = [
            marker for marker in item["required_markers"] if marker not in text
        ]
        size = component_path.stat().st_size if component_path.is_file() else 0
        present = (
            component_path.is_file()
            and size >= int(item["minimum_size_bytes"])
            and not missing_markers
        )
        if not component_path.is_file():
            reason = f"missing: {item['purpose']}"
        elif size < int(item["minimum_size_bytes"]):
            reason = (
                f"component is too small for the declared contract: {size} < "
                f"{item['minimum_size_bytes']} bytes"
            )
        elif missing_markers:
            reason = "component lacks required contract markers: " + ", ".join(
                missing_markers
            )
        else:
            reason = item["purpose"]
        production_components.append(
            {
                "control_id": item["control_id"],
                "ref": item["path"],
                "passed": present,
                "reason": reason,
            }
        )

    by_id = {item["control_id"]: item for item in attestations["controls"]}
    owner_controls = []
    for control_id in policy["required_owner_controls"]:
        item = by_id.get(control_id, {})
        expiry = item.get("expires_at")
        verified = (
            item.get("status") == "verified"
            and bool(item.get("verified_by"))
            and bool(item.get("verified_at"))
            and bool(item.get("evidence_note"))
            and isinstance(expiry, str)
            and _instant(expiry) > now
        )
        if verified:
            reason = "owner attestation is complete and unexpired"
        elif item.get("status") == "verified" and expiry:
            reason = "owner attestation is expired or incomplete"
        else:
            reason = "owner verification is required"
        owner_controls.append(
            {
                "control_id": control_id,
                "status": item.get("status", "missing"),
                "verified": verified,
                "expires_at": expiry,
                "reason": reason,
            }
        )

    minimum_runs = int(policy["production_monitor_minimum_manual_runs"])
    monitor_results = []
    for path in sorted((root / "config" / "monitors").glob("*.json")):
        monitor = read_json(path)
        if int(monitor.get("manual_run_requirement") or 0) < minimum_runs:
            continue
        report = evaluate_monitor(
            root, monitor_id=monitor["monitor_id"], evaluated_at=timestamp
        )
        monitor_results.append(
            {
                "monitor_id": monitor["monitor_id"],
                "enabled": monitor.get("enabled") is True,
                "status": report["status"],
                "blockers": report["blockers"],
            }
        )
    enabled = [item for item in monitor_results if item["enabled"]]
    ready_enabled = [item for item in enabled if item["status"] == "ready"]

    checks = {
        "workflow_gates_present": all(item["passed"] for item in workflow_gates),
        "production_components_present": all(
            item["passed"] for item in production_components
        ),
        "owner_controls_verified": all(item["verified"] for item in owner_controls),
        "research_monitor_enabled": bool(enabled),
        "enabled_monitors_ready": bool(enabled) and len(ready_enabled) == len(enabled),
    }
    blockers = sorted(name for name, passed in checks.items() if not passed)
    owner_actions = []
    for item in workflow_gates:
        if not item["passed"]:
            owner_actions.append(
                {
                    "action_id": f"repair-{item['control_id']}",
                    "summary": "Restore and review the missing workflow activation gate.",
                    "refs": [item["ref"]],
                }
            )
    for item in production_components:
        if not item["passed"]:
            owner_actions.append(
                {
                    "action_id": f"implement-{item['control_id']}",
                    "summary": "Implement and review the required production component.",
                    "refs": [item["ref"]],
                }
            )
    for item in owner_controls:
        if not item["verified"]:
            owner_actions.append(
                {
                    "action_id": f"verify-{item['control_id']}",
                    "summary": (
                        "Verify the external control and record a non-secret, "
                        "expiring owner attestation."
                    ),
                    "refs": ["config/owner-controls.json"],
                }
            )
    if not enabled:
        owner_actions.append(
            {
                "action_id": "enable-reviewed-research-monitor",
                "summary": (
                    "After its local readiness gates pass, enable at least one "
                    "reviewed recurring research Monitor."
                ),
                "refs": ["config/monitors"],
            }
        )
    for item in enabled:
        if item["status"] != "ready":
            owner_actions.append(
                {
                    "action_id": f"resolve-{item['monitor_id'].lower()}-readiness",
                    "summary": "Resolve the enabled Monitor's reported readiness blockers.",
                    "refs": [f"config/monitors/{item['monitor_id']}.json"],
                }
            )
    return {
        "schema_version": "0.1.0",
        "evaluated_at": timestamp,
        "status": "ready" if not blockers else "blocked",
        "checks": checks,
        "blockers": blockers,
        "owner_actions": owner_actions,
        "workflow_gates": workflow_gates,
        "production_components": production_components,
        "owner_controls": owner_controls,
        "monitors": {
            "eligible_count": len(monitor_results),
            "enabled_count": len(enabled),
            "ready_enabled_count": len(ready_enabled),
            "results": monitor_results,
        },
        "effect": policy["effect"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluated-at")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--require-ready", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = evaluate(args.root, evaluated_at=args.evaluated_at)
    if args.output:
        output = args.output if args.output.is_absolute() else args.root / args.output
        atomic_write_json(output, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 2 if args.require_ready and report["status"] != "ready" else 0


if __name__ == "__main__":
    raise SystemExit(main())
