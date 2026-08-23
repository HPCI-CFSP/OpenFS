#!/usr/bin/env python3
"""Create a registry-bound assessment for an OpenFS proposal."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, git_head, isoformat, read_json, stable_digest


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
    confidence: float,
    checks: dict[str, Any],
    objections: list[dict[str, str]],
    registry: dict[str, Any],
    base_commit: str,
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
    if not 0 <= confidence <= 1:
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
    return {
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
        "confidence": confidence,
        "checks": checks,
        "objections": objections,
        "reviewed_at": reviewed_at or isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposal", required=True, type=Path)
    parser.add_argument("--reviewer-agent-id", required=True)
    parser.add_argument("--verdict", required=True, choices=("support", "refute", "uncertain"))
    parser.add_argument("--confidence", required=True, type=float)
    parser.add_argument("--checks", required=True, type=Path)
    parser.add_argument("--objections", required=True, type=Path)
    parser.add_argument("--agent-registry", type=Path, default=ROOT / "config/agent-registry.json")
    parser.add_argument("--allow-disabled-pilot-agent", action="store_true")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    assessment = create(
        read_json(args.proposal),
        reviewer_agent_id=args.reviewer_agent_id,
        verdict=args.verdict,
        confidence=args.confidence,
        checks=read_json(args.checks),
        objections=read_json(args.objections),
        registry=read_json(args.agent_registry),
        base_commit=git_head(ROOT),
        allow_disabled_pilot_agent=args.allow_disabled_pilot_agent,
    )
    atomic_write_json(args.output, assessment)
    print(json.dumps({"assessment_id": assessment["assessment_id"], "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
