#!/usr/bin/env python3
"""Evaluate whether Claim Proposals are eligible for canonical promotion."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json
from promote_claim import unresolved_dependency_impacts


ROOT = Path(__file__).resolve().parents[1]


def evaluate(
    root: Path,
    *,
    run_id: str,
    evaluated_at: str | None = None,
) -> dict[str, Any]:
    policy_path = (
        root / "runs" / run_id / "inputs" / "config" / "consensus-policy.json"
    )
    policy = read_json(
        policy_path if policy_path.is_file() else root / "config" / "consensus-policy.json"
    )
    decisions = {
        item["proposal_id"]: item
        for item in (
            read_json(path)
            for path in sorted((root / "decisions" / run_id).glob("*.json"))
        )
    }
    promoted_proposals = {
        read_json(path).get("provenance", {}).get("proposal_ref")
        for path in sorted((root / "knowledge" / "claims").glob("CLM-*.json"))
    }
    items: list[dict[str, Any]] = []
    for path in sorted((root / "proposals" / "claims" / run_id).glob("*.json")):
        proposal = read_json(path)
        proposal_ref = str(path.relative_to(root))
        decision = decisions.get(proposal.get("proposal_id"))
        dependency_blocks = unresolved_dependency_impacts(root, proposal_ref)
        if proposal_ref in promoted_proposals:
            status = "already-promoted"
            reasons = ["A canonical Claim already pins this Proposal."]
        elif decision is None:
            status = "missing-decision"
            reasons = ["No Decision exists for this Claim Proposal."]
        elif decision.get("outcome") != "accepted":
            status = "decision-not-accepted"
            reasons = [f"Decision outcome is {decision.get('outcome', 'missing')}."]
        elif not decision.get("policy_result", {}).get("checks") or not all(
            decision["policy_result"]["checks"].values()
        ):
            status = "decision-checks-failed"
            reasons = ["The accepted Decision does not contain all passing checks."]
        elif decision.get("policy_id") != policy.get("policy_id"):
            status = "policy-mismatch"
            reasons = ["Decision Policy differs from the Run-pinned Consensus Policy."]
        elif policy.get("calibration_status") != "calibrated":
            status = "policy-uncalibrated"
            reasons = ["The Run-pinned Consensus Policy is not calibrated."]
        elif proposal.get("claim_candidate", {}).get("claim_kind") == "recommendation":
            status = "recommendation-gate-required"
            reasons = ["Recommendation Claims require the human Recommendation Gate."]
        elif dependency_blocks:
            status = "dependency-impact-blocked"
            reasons = ["One or more later Source changes require dependency revalidation."]
        else:
            status = "eligible"
            reasons = ["The Claim satisfies the deterministic promotion preflight."]
        items.append(
            {
                "proposal_id": proposal["proposal_id"],
                "claim_id": proposal["claim_candidate"]["claim_id"],
                "claim_kind": proposal["claim_candidate"]["claim_kind"],
                "proposal_ref": proposal_ref,
                "decision_ref": (
                    f"decisions/{run_id}/{proposal['proposal_id']}.json"
                    if decision
                    else None
                ),
                "status": status,
                "dependency_impact_refs": sorted(
                    {item["dependency_impact_ref"] for item in dependency_blocks}
                ),
                "reasons": reasons,
            }
        )
    counts = {
        status: sum(item["status"] == status for item in items)
        for status in sorted({item["status"] for item in items})
    }
    return {
        "schema_version": "0.1.0",
        "run_id": run_id,
        "evaluated_at": evaluated_at or isoformat(),
        "policy_id": policy.get("policy_id"),
        "policy_calibration_status": policy.get("calibration_status", "missing"),
        "summary": {
            "claim_proposal_count": len(items),
            "eligible_count": counts.get("eligible", 0),
            "already_promoted_count": counts.get("already-promoted", 0),
            "blocked_count": len(items)
            - counts.get("eligible", 0)
            - counts.get("already-promoted", 0),
            "status_counts": counts,
        },
        "claims": items,
        "caveat": (
            "Eligibility is a deterministic preflight, not an automatic merge or "
            "publication decision. Recommendation Claims remain human-accountable."
        ),
    }


def record(root: Path, report: dict[str, Any]) -> Path:
    path = root / "runs" / report["run_id"] / "promotion-readiness.json"
    atomic_write_json(path, report)
    manifest_path = root / "runs" / report["run_id"] / "manifest.json"
    manifest = read_json(manifest_path)
    manifest["promotion_readiness_ref"] = str(path.relative_to(root))
    manifest.setdefault("metrics", {})["promotion_readiness"] = report["summary"]
    atomic_write_json(manifest_path, manifest)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = evaluate(args.root, run_id=args.run_id)
    output = record(args.root, report)
    print(json.dumps({"output": str(output), "summary": report["summary"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
