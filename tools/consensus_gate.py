#!/usr/bin/env python3
"""Evaluate an OpenFS proposal against a deterministic consensus policy."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openfs_runtime import stable_digest


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def evaluate(
    proposal: dict[str, Any],
    assessments: list[dict[str, Any]],
    policy: dict[str, Any],
    agent_registry: dict[str, Any],
) -> dict[str, Any]:
    proposal_id = proposal["proposal_id"]
    object_type = proposal["object_type"]
    try:
        rule = policy["rules"][object_type]
    except KeyError as exc:
        raise ValueError(f"No consensus rule for object type: {object_type}") from exc

    registry_digest = stable_digest(agent_registry)
    agents = {
        item["agent_id"]: item
        for item in agent_registry.get("agents", [])
        if item.get("agent_id")
    }
    author = agents.get(proposal.get("created_by_agent_id"))
    author_group = author.get("agent_independence_group") if author else None

    matching = [item for item in assessments if item.get("proposal_id") == proposal_id]
    unique_by_reviewer: dict[str, dict[str, Any]] = {}
    duplicate_reviewers: list[str] = []
    for assessment in matching:
        reviewer = assessment["reviewer_agent_id"]
        if reviewer in unique_by_reviewer:
            duplicate_reviewers.append(reviewer)
            continue
        unique_by_reviewer[reviewer] = assessment

    valid: list[dict[str, Any]] = []
    invalid_assessments: list[dict[str, str]] = []
    for assessment in unique_by_reviewer.values():
        reviewer_id = assessment["reviewer_agent_id"]
        reviewer = agents.get(reviewer_id)
        reasons: list[str] = []
        if reviewer is None:
            reasons.append("reviewer-not-registered")
        else:
            if reviewer.get("role") not in {"validator", "critic"}:
                reasons.append("reviewer-role-not-eligible")
            if reviewer.get("provider") in {None, "unconfigured"}:
                reasons.append("reviewer-provider-unconfigured")
            if reviewer.get("model_family") in {None, "unconfigured"}:
                reasons.append("reviewer-model-unconfigured")
            if assessment.get("agent_independence_group") != reviewer.get(
                "agent_independence_group"
            ):
                reasons.append("independence-group-mismatch")
            expected_identity = {
                "provider": reviewer.get("provider"),
                "model_family": reviewer.get("model_family"),
                "prompt_profile": reviewer.get("prompt_profile"),
                "role": reviewer.get("role"),
            }
            if assessment.get("reviewer_identity") != expected_identity:
                reasons.append("reviewer-identity-mismatch")
            if assessment.get("agent_registry_digest") != registry_digest:
                reasons.append("agent-registry-digest-mismatch")
        if assessment.get("run_id") != proposal.get("run_id"):
            reasons.append("run-id-mismatch")
        if reviewer_id == proposal.get("created_by_agent_id"):
            reasons.append("self-review")
        if reasons:
            invalid_assessments.append(
                {"assessment_id": assessment["assessment_id"], "reason": ",".join(reasons)}
            )
        else:
            valid.append(assessment)

    support = [item for item in valid if item["verdict"] == "support"]
    refute = [item for item in valid if item["verdict"] == "refute"]
    support_groups = {
        item["agent_independence_group"]
        for item in support
        if item["agent_independence_group"] != author_group
        and item["agent_independence_group"] != "non-voting-control-plane"
    }
    origin_groups = set(proposal.get("origin_group_ids", []))

    critical_objections = [
        {
            "assessment_id": item["assessment_id"],
            "message": objection["message"],
        }
        for item in valid
        for objection in item.get("objections", [])
        if objection.get("severity") == "critical"
    ]
    has_falsification_review = any(
        item.get("checks", {}).get("falsification_review") is True for item in valid
    )

    checks = {
        "minimum_assessments": len(valid) >= rule["minimum_assessments"],
        "minimum_support": len(support) >= rule["minimum_support"],
        "minimum_support_independence_groups": (
            len(support_groups) >= rule["minimum_support_independence_groups"]
        ),
        "minimum_origin_groups": len(origin_groups) >= rule["minimum_origin_groups"],
        "primary_source": (
            proposal.get("has_primary_source") is True
            if rule.get("require_primary_source", False)
            else True
        ),
        "falsification_review": (
            has_falsification_review
            if rule.get("require_falsification_review", False)
            else True
        ),
        "human_decision": (
            proposal.get("human_decision", False) is True
            if rule.get("require_human_decision", False)
            else True
        ),
        "no_critical_objection": (
            not critical_objections
            if rule.get("block_on_critical_objection", True)
            else True
        ),
        "unique_reviewers": not duplicate_reviewers,
        "registered_proposal_author": author is not None,
        "valid_assessment_identities": not invalid_assessments,
    }

    if critical_objections:
        outcome = "contested"
    elif all(checks.values()):
        outcome = "accepted"
    elif len(support) == 0 and len(refute) >= rule["minimum_support"]:
        outcome = "rejected"
    else:
        outcome = "provisional"

    return {
        "schema_version": "0.1.0",
        "decision_id": f"DEC-{proposal_id}",
        "proposal_id": proposal_id,
        "object_type": object_type,
        "outcome": outcome,
        "policy_id": policy["policy_id"],
        "agent_registry_digest": registry_digest,
        "policy_result": {
            "checks": checks,
            "counts": {
                "assessments": len(valid),
                "support": len(support),
                "refute": len(refute),
                "support_independence_groups": len(support_groups),
                "origin_groups": len(origin_groups),
            },
            "support_independence_groups": sorted(support_groups),
            "origin_group_ids": sorted(origin_groups),
            "duplicate_reviewer_agent_ids": sorted(set(duplicate_reviewers)),
            "proposal_author_independence_group": author_group,
            "invalid_assessments": invalid_assessments,
            "critical_objections": critical_objections,
        },
        "assessment_ids": [item["assessment_id"] for item in valid],
        "dissent_assessment_ids": [
            item["assessment_id"] for item in valid if item["verdict"] != "support"
        ],
        "decided_at": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposal", required=True, type=Path)
    assessment_inputs = parser.add_mutually_exclusive_group(required=True)
    assessment_inputs.add_argument("--assessments", type=Path)
    assessment_inputs.add_argument("--assessment", action="append", type=Path)
    parser.add_argument("--policy", required=True, type=Path)
    parser.add_argument(
        "--agent-registry",
        type=Path,
        default=ROOT / "config/agent-registry.json",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    if args.assessment:
        assessments = [load_json(path) for path in args.assessment]
    else:
        assessments = load_json(args.assessments)
        if isinstance(assessments, dict):
            assessments = [assessments]
    decision = evaluate(
        load_json(args.proposal),
        assessments,
        load_json(args.policy),
        load_json(args.agent_registry),
    )
    rendered = json.dumps(decision, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
