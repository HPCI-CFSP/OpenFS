#!/usr/bin/env python3
"""Promote one accepted non-recommendation Claim into canonical knowledge."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from pathlib import Path, PurePosixPath
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json, stable_digest


ROOT = Path(__file__).resolve().parents[1]


def unresolved_dependency_impacts(
    root: Path, proposal_ref: str
) -> list[dict[str, str]]:
    impacts: list[dict[str, str]] = []
    for path in sorted((root / "runs").glob("RUN-*/dependency-impact.json")):
        report = read_json(path)
        for item in report.get("impacts", []):
            if not item.get("promotion_blocked"):
                continue
            if proposal_ref in item.get("claim_proposal_refs", []):
                impacts.append(
                    {
                        "dependency_impact_ref": str(path.relative_to(root)),
                        "canonical_url": item["canonical_url"],
                        "classification": item["classification"],
                    }
                )
    return impacts


def prepare_canonical_claim(
    proposal: dict[str, Any],
    decision: dict[str, Any],
    policy: dict[str, Any],
    bundles: list[dict[str, Any]],
    *,
    proposal_ref: str,
    decision_ref: str,
    dependency_impact_refs_checked: list[str],
    promoted_at: str,
) -> dict[str, Any]:
    if proposal.get("object_type") != "claim":
        raise ValueError("proposal object_type must be claim")
    if decision.get("object_type") != "claim":
        raise ValueError("decision object_type must be claim")
    if decision.get("proposal_id") != proposal.get("proposal_id"):
        raise ValueError("Decision does not match Claim Proposal")
    if decision.get("outcome") != "accepted":
        raise ValueError("only an accepted Decision can promote a Claim")
    checks = decision.get("policy_result", {}).get("checks", {})
    if not checks or not all(checks.values()):
        raise ValueError("accepted Decision must contain passing Policy checks")
    if policy.get("policy_id") != decision.get("policy_id"):
        raise ValueError("Decision Policy differs from the pinned Consensus Policy")
    if policy.get("calibration_status") != "calibrated":
        raise ValueError("uncalibrated Consensus Policy cannot authorize promotion")

    candidate = deepcopy(proposal.get("claim_candidate", {}))
    if candidate.get("claim_kind") == "recommendation":
        raise ValueError("Recommendation Claims require the human Recommendation Gate")
    if not bundles or len(bundles) != len(proposal.get("evidence_bundle_refs", [])):
        raise ValueError("Claim promotion requires every declared Evidence bundle")
    expected_evidence = {
        evidence["evidence_id"]
        for bundle in bundles
        for evidence in bundle.get("evidence_candidates", [])
    }
    expected_lineages = {
        evidence["source_lineage_id"]
        for bundle in bundles
        for evidence in bundle.get("evidence_candidates", [])
    }
    if set(candidate.get("evidence_ids", [])) != expected_evidence:
        raise ValueError("Claim Evidence IDs differ from its bundles")
    if set(candidate.get("source_lineage_ids", [])) != expected_lineages:
        raise ValueError("Claim Source Lineages differ from its bundles")
    if any(bundle.get("run_id") != proposal.get("run_id") for bundle in bundles):
        raise ValueError("Claim Evidence belongs to a different Run")

    candidate["status"] = "accepted"
    provenance = {
        "proposal_ref": proposal_ref,
        "proposal_digest": stable_digest(proposal),
        "decision_ref": decision_ref,
        "decision_digest": stable_digest(decision),
        "policy_id": policy["policy_id"],
        "evidence_bundle_refs": proposal["evidence_bundle_refs"],
        "evidence_bundle_digests": {
            ref: stable_digest(bundle)
            for ref, bundle in zip(
                proposal["evidence_bundle_refs"], bundles, strict=True
            )
        },
        "dependency_impact_refs_checked": sorted(
            set(dependency_impact_refs_checked)
        ),
    }
    return {
        "schema_version": "0.1.0",
        "canonical_claim_id": candidate["claim_id"],
        "claim": candidate,
        "provenance": provenance,
        "promoted_at": promoted_at,
        "promotion_digest": stable_digest(
            {"claim": candidate, "provenance": provenance}
        ),
    }


def promote(
    root: Path,
    *,
    proposal_ref: str,
    decision_ref: str,
    promoted_at: str | None = None,
) -> tuple[Path, dict[str, Any]]:
    for ref in (proposal_ref, decision_ref):
        relative = PurePosixPath(ref)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("promotion inputs must be repository-relative")
    proposal = read_json(root / proposal_ref)
    decision = read_json(root / decision_ref)
    run_id = proposal.get("run_id", "")
    if not proposal_ref.startswith(f"proposals/claims/{run_id}/"):
        raise ValueError("Claim Proposal path differs from its Run identity")
    if not decision_ref.startswith(f"decisions/{run_id}/"):
        raise ValueError("Decision path differs from the Claim Run identity")
    blocks = unresolved_dependency_impacts(root, proposal_ref)
    if blocks:
        refs = sorted({item["dependency_impact_ref"] for item in blocks})
        raise RuntimeError(
            "Claim promotion is blocked by unresolved dependency impact: "
            + ", ".join(refs)
        )

    output = root / "knowledge" / "claims" / f"{proposal['artifact_id']}.json"
    if output.is_file():
        existing = read_json(output)
        provenance = existing.get("provenance", {})
        if (
            provenance.get("proposal_ref") != proposal_ref
            or provenance.get("decision_ref") != decision_ref
        ):
            raise RuntimeError("canonical Claim ID already exists with different provenance")
        return output, existing

    policy_path = (
        root / "runs" / run_id / "inputs" / "config" / "consensus-policy.json"
    )
    policy = read_json(
        policy_path if policy_path.is_file() else root / "config" / "consensus-policy.json"
    )
    bundle_refs = proposal.get("evidence_bundle_refs", [])
    bundles = [read_json(root / ref) for ref in bundle_refs]
    checked_refs = [
        str(path.relative_to(root))
        for path in sorted((root / "runs").glob("RUN-*/dependency-impact.json"))
    ]
    canonical = prepare_canonical_claim(
        proposal,
        decision,
        policy,
        bundles,
        proposal_ref=proposal_ref,
        decision_ref=decision_ref,
        dependency_impact_refs_checked=checked_refs,
        promoted_at=promoted_at or isoformat(),
    )
    atomic_write_json(output, canonical)
    return output, canonical


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposal-ref", required=True)
    parser.add_argument("--decision-ref", required=True)
    parser.add_argument("--promoted-at")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    output, canonical = promote(
        args.root,
        proposal_ref=args.proposal_ref,
        decision_ref=args.decision_ref,
        promoted_at=args.promoted_at,
    )
    print(
        json.dumps(
            {"output": str(output), "canonical_claim_id": canonical["canonical_claim_id"]}
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
