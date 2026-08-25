#!/usr/bin/env python3
"""Evaluate an OpenFS proposal against a deterministic consensus policy."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, read_json, run_snapshot_path, stable_digest


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def evaluate(
    proposal: dict[str, Any],
    assessments: list[dict[str, Any]],
    policy: dict[str, Any],
    agent_registry: dict[str, Any],
    decided_at: str | None = None,
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
            if reviewer.get("enabled") is not True:
                reasons.append("reviewer-not-enabled")
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
    support_model_families = {
        (item["reviewer_identity"]["provider"], item["reviewer_identity"]["model_family"])
        for item in support
    }
    support_providers = {
        item["reviewer_identity"]["provider"] for item in support
    }
    origin_groups = set(proposal.get("origin_group_ids", []))
    publisher_groups = set(proposal.get("publisher_group_ids", []))

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
        "minimum_model_families": (
            len(support_model_families) >= rule.get("minimum_model_families", 0)
        ),
        "minimum_providers": len(support_providers) >= rule.get("minimum_providers", 0),
        "minimum_publisher_groups": (
            len(publisher_groups) >= rule.get("minimum_publisher_groups", 0)
        ),
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
                "publisher_groups": len(publisher_groups),
            },
            "support_independence_groups": sorted(support_groups),
            "origin_group_ids": sorted(origin_groups),
            "publisher_group_ids": sorted(publisher_groups),
            "duplicate_reviewer_agent_ids": sorted(set(duplicate_reviewers)),
            "proposal_author_independence_group": author_group,
            "invalid_assessments": invalid_assessments,
            "critical_objections": critical_objections,
        },
        "assessment_ids": [item["assessment_id"] for item in valid],
        "dissent_assessment_ids": [
            item["assessment_id"] for item in valid if item["verdict"] != "support"
        ],
        "decided_at": decided_at or proposal["created_at"],
    }


def validate_assignment(
    work_item: dict[str, Any],
    *,
    agent_id: str,
    proposal_ref: str,
    assessment_refs: list[str],
    output_ref: str,
) -> None:
    if work_item.get("kind") != "consensus":
        raise ValueError("Work Item is not assigned to consensus")
    lease = work_item.get("lease", {})
    if work_item.get("status") != "leased" or lease.get("agent_id") != agent_id:
        raise RuntimeError("Consensus evaluation requires the current Work Item lease")
    assigned_pairs = work_item.get("payload", {}).get("proposal_assessment_pairs", [])
    matching = [item for item in assigned_pairs if item.get("proposal_ref") == proposal_ref]
    if len(matching) != 1:
        raise ValueError("Proposal reference differs from the assigned Work Item")
    if sorted(matching[0].get("assessment_refs", [])) != sorted(assessment_refs):
        raise ValueError("Assessment references differ from the assigned Work Item")
    if output_ref not in work_item.get("output_paths", []):
        raise ValueError("Decision output is outside the Work Item's declared paths")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposal", required=True, type=Path)
    parser.add_argument("--proposal-ref", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--work-item-id", required=True)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--assessment", action="append", required=True, type=Path)
    parser.add_argument("--policy", type=Path)
    parser.add_argument("--agent-registry", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()

    work_item = read_json(
        args.root / "queue" / args.run_id / f"{args.work_item_id}.json"
    )
    proposal_path = args.root / args.proposal_ref
    supplied_proposal_path = (
        args.proposal if args.proposal.is_absolute() else args.root / args.proposal
    )
    if supplied_proposal_path.resolve() != proposal_path.resolve():
        raise ValueError("Proposal path differs from proposal-ref")
    output_path = args.output if args.output.is_absolute() else args.root / args.output
    output_ref = str(output_path.relative_to(args.root))
    assessment_paths = [
        path if path.is_absolute() else args.root / path
        for path in (args.assessment or [])
    ]
    assessment_refs = [str(path.relative_to(args.root)) for path in assessment_paths]
    validate_assignment(
        work_item,
        agent_id=args.agent_id,
        proposal_ref=args.proposal_ref,
        assessment_refs=assessment_refs,
        output_ref=output_ref,
    )

    policy_path = args.policy or run_snapshot_path(
        args.root, args.run_id, "config/consensus-policy.json"
    )
    registry_path = args.agent_registry or run_snapshot_path(
        args.root, args.run_id, "config/agent-registry.json"
    )

    assessments = [load_json(path) for path in assessment_paths]
    decision = evaluate(
        load_json(proposal_path),
        assessments,
        load_json(policy_path),
        load_json(registry_path),
        decided_at=work_item.get("lease", {}).get("acquired_at")
        or work_item.get("updated_at"),
    )
    if output_path.exists():
        if read_json(output_path) != decision:
            raise RuntimeError("Decision already exists with different content")
    else:
        atomic_write_json(output_path, decision)
    print(json.dumps({"decision_id": decision["decision_id"], "output": output_ref}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
