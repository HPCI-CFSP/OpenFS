#!/usr/bin/env python3
"""Create a registry-bound assessment for an OpenFS proposal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import (
    atomic_write_json,
    isoformat,
    read_json,
    run_snapshot_path,
    stable_digest,
)


ROOT = Path(__file__).resolve().parents[1]


def resolve_reviewer(
    agent_id: str,
    registry: dict[str, Any],
    *,
    allow_disabled_pilot_agent: bool = False,
) -> dict[str, Any]:
    matches = [item for item in registry.get("agents", []) if item.get("agent_id") == agent_id]
    if len(matches) != 1:
        raise ValueError(f"agent_id is not uniquely registered: {agent_id}")
    agent = matches[0]
    if agent.get("role") not in {"validator", "critic"}:
        raise ValueError(f"agent role cannot create an Assessment: {agent.get('role')}")
    if not agent.get("enabled") and not allow_disabled_pilot_agent:
        raise RuntimeError(f"agent is disabled: {agent_id}")
    for field in ("provider", "model_family", "prompt_profile", "agent_independence_group"):
        if not agent.get(field) or agent[field] == "unconfigured":
            raise ValueError(f"agent has unconfigured {field}: {agent_id}")
    return agent


def create(
    proposal: dict[str, Any],
    *,
    reviewer_agent_id: str,
    verdict: str,
    confidence: float | None,
    checks: dict[str, Any],
    objections: list[dict[str, str]],
    registry: dict[str, Any],
    base_commit: str,
    work_item_id: str | None = None,
    proposal_ref: str | None = None,
    allow_disabled_pilot_agent: bool = False,
    reviewed_at: str | None = None,
) -> dict[str, Any]:
    reviewer = resolve_reviewer(
        reviewer_agent_id,
        registry,
        allow_disabled_pilot_agent=allow_disabled_pilot_agent,
    )
    if verdict not in {"support", "refute", "uncertain"}:
        raise ValueError(f"unsupported verdict: {verdict}")
    if confidence is not None and not 0 <= confidence <= 1:
        raise ValueError("confidence must be between zero and one")
    if proposal.get("created_by_agent_id") == reviewer_agent_id:
        raise ValueError("proposal author cannot assess its own proposal")
    identity = {
        "proposal_id": proposal["proposal_id"],
        "reviewer_agent_id": reviewer_agent_id,
        "verdict": verdict,
        "checks": checks,
        "objections": objections,
    }
    number = int(stable_digest(identity)[:12], 16) % 1_000_000
    assessment = {
        "schema_version": "0.1.0",
        "assessment_id": f"ASM-{number:06d}",
        "proposal_id": proposal["proposal_id"],
        "reviewer_agent_id": reviewer_agent_id,
        "agent_independence_group": reviewer["agent_independence_group"],
        "reviewer_identity": {
            "provider": reviewer["provider"],
            "model_family": reviewer["model_family"],
            "prompt_profile": reviewer["prompt_profile"],
            "role": reviewer["role"],
        },
        "agent_registry_digest": stable_digest(registry),
        "run_id": proposal["run_id"],
        "base_commit": base_commit,
        "verdict": verdict,
        "checks": checks,
        "objections": objections,
        "reviewed_at": reviewed_at or isoformat(),
    }
    if confidence is not None:
        assessment["confidence"] = confidence
    if work_item_id is not None:
        assessment["work_item_id"] = work_item_id
    if proposal_ref is not None:
        assessment["proposal_ref"] = proposal_ref
    return assessment


def validate_assignment(
    work_item: dict[str, Any],
    *,
    proposal_ref: str,
    agent_id: str,
    output_ref: str,
) -> None:
    if work_item.get("kind") != "validation":
        raise ValueError("Work Item is not assigned to validation")
    lease = work_item.get("lease", {})
    if work_item.get("status") != "leased" or lease.get("agent_id") != agent_id:
        raise RuntimeError("Assessment creation requires the current Work Item lease")
    if work_item.get("payload", {}).get("proposal_ref") != proposal_ref:
        raise ValueError("Proposal reference differs from the assigned Work Item")
    assigned_reviewer = work_item.get("payload", {}).get("assigned_reviewer_agent_id")
    if assigned_reviewer and assigned_reviewer != agent_id:
        raise ValueError("Reviewer differs from the assigned Work Item")
    if output_ref not in work_item.get("output_paths", []):
        raise ValueError("Assessment output is outside the Work Item's declared paths")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposal", required=True, type=Path)
    parser.add_argument("--proposal-ref", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--work-item-id", required=True)
    parser.add_argument("--reviewer-agent-id", required=True)
    parser.add_argument("--verdict", required=True, choices=("support", "refute", "uncertain"))
    parser.add_argument("--confidence", type=float)
    parser.add_argument("--checks", required=True, type=Path)
    parser.add_argument("--objections", required=True, type=Path)
    parser.add_argument("--agent-registry", type=Path)
    parser.add_argument("--allow-disabled-pilot-agent", action="store_true")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    manifest = read_json(args.root / "runs" / args.run_id / "manifest.json")
    work_item = read_json(
        args.root / "queue" / args.run_id / f"{args.work_item_id}.json"
    )
    proposal_path = args.root / args.proposal_ref
    supplied_path = args.proposal if args.proposal.is_absolute() else args.root / args.proposal
    if supplied_path.resolve() != proposal_path.resolve():
        raise ValueError("Proposal path differs from proposal-ref")
    output_path = args.output if args.output.is_absolute() else args.root / args.output
    output_ref = str(output_path.relative_to(args.root))
    validate_assignment(
        work_item,
        proposal_ref=args.proposal_ref,
        agent_id=args.reviewer_agent_id,
        output_ref=output_ref,
    )
    registry_path = args.agent_registry or run_snapshot_path(
        args.root, args.run_id, "config/agent-registry.json"
    )
    assessment = create(
        read_json(proposal_path),
        reviewer_agent_id=args.reviewer_agent_id,
        verdict=args.verdict,
        confidence=args.confidence,
        checks=read_json(args.checks),
        objections=read_json(args.objections),
        registry=read_json(registry_path),
        base_commit=manifest["base_commit"],
        work_item_id=args.work_item_id,
        proposal_ref=args.proposal_ref,
        allow_disabled_pilot_agent=args.allow_disabled_pilot_agent,
        reviewed_at=work_item.get("lease", {}).get("acquired_at")
        or work_item.get("updated_at"),
    )
    if output_path.exists():
        if read_json(output_path) != assessment:
            raise RuntimeError("Assessment already exists with different content")
    else:
        atomic_write_json(output_path, assessment)
    print(json.dumps({"assessment_id": assessment["assessment_id"], "output": output_ref}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
