#!/usr/bin/env python3
"""Trace changed Source observations to dependent OpenFS review artifacts."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json


ROOT = Path(__file__).resolve().parents[1]
ACTIONABLE_CLASSIFICATIONS = {"changed", "unavailable"}


def _load_objects(directory: Path, root: Path) -> list[tuple[str, dict[str, Any]]]:
    return [
        (str(path.relative_to(root)), read_json(path))
        for path in sorted(directory.glob("RUN-*/*.json"))
    ]


def dependency_index(root: Path) -> dict[str, dict[str, set[str]]]:
    evidence = _load_objects(root / "proposals" / "evidence", root)
    claims = _load_objects(root / "proposals" / "claims", root)
    profiles = _load_objects(root / "proposals" / "center-profiles", root)
    decisions = _load_objects(root / "decisions", root)

    evidence_by_source: dict[str, set[str]] = {}
    for ref, item in evidence:
        evidence_by_source.setdefault(item.get("source_result_ref", ""), set()).add(ref)

    claims_by_evidence: dict[str, set[str]] = {}
    proposal_ids_by_ref: dict[str, str] = {}
    for ref, item in claims:
        proposal_ids_by_ref[ref] = item.get("proposal_id", "")
        for evidence_ref in item.get("evidence_bundle_refs", []):
            claims_by_evidence.setdefault(evidence_ref, set()).add(ref)

    profiles_by_evidence: dict[str, set[str]] = {}
    for ref, item in profiles:
        proposal_ids_by_ref[ref] = item.get("proposal_id", "")
        for evidence_ref in item.get("evidence_bundle_refs", []):
            profiles_by_evidence.setdefault(evidence_ref, set()).add(ref)

    decisions_by_proposal: dict[str, set[str]] = {}
    for ref, item in decisions:
        decisions_by_proposal.setdefault(item.get("proposal_id", ""), set()).add(ref)

    return {
        "evidence_by_source": evidence_by_source,
        "claims_by_evidence": claims_by_evidence,
        "profiles_by_evidence": profiles_by_evidence,
        "decisions_by_proposal": decisions_by_proposal,
        "proposal_ids_by_ref": {
            ref: {proposal_id} for ref, proposal_id in proposal_ids_by_ref.items()
        },
    }


def analyze(
    root: Path,
    *,
    run_id: str,
    change_report: dict[str, Any] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    report = change_report or read_json(root / "runs" / run_id / "changes.json")
    if report.get("run_id") != run_id:
        raise ValueError("Source Change Report belongs to a different Run")
    index = dependency_index(root)
    impacts: list[dict[str, Any]] = []

    for change in report.get("changes", []):
        source_refs = sorted(
            {
                ref
                for ref in (
                    change.get("previous_source_ref"),
                    change.get("current_source_ref"),
                )
                if ref
            }
        )
        evidence_refs = sorted(
            {
                evidence_ref
                for source_ref in source_refs
                for evidence_ref in index["evidence_by_source"].get(source_ref, set())
            }
        )
        claim_refs = sorted(
            {
                proposal_ref
                for evidence_ref in evidence_refs
                for proposal_ref in index["claims_by_evidence"].get(evidence_ref, set())
            }
        )
        profile_refs = sorted(
            {
                proposal_ref
                for evidence_ref in evidence_refs
                for proposal_ref in index["profiles_by_evidence"].get(evidence_ref, set())
            }
        )
        proposal_refs = claim_refs + profile_refs
        decision_refs = sorted(
            {
                decision_ref
                for proposal_ref in proposal_refs
                for proposal_id in index["proposal_ids_by_ref"].get(proposal_ref, set())
                for decision_ref in index["decisions_by_proposal"].get(proposal_id, set())
            }
        )
        classification = change["classification"]
        has_dependents = bool(evidence_refs or proposal_refs or decision_refs)
        if classification == "not-observed":
            action = "reobserve"
            reasons = [
                "The previous observation was not selected; availability and content were not retested."
            ]
        elif classification == "unavailable" and has_dependents:
            action = "verify-unavailable-and-revalidate"
            reasons = [
                "A dependent Source observation is currently unavailable; verify status and revalidate its dependents."
            ]
        elif classification == "changed" and has_dependents:
            action = "revalidate-dependents"
            reasons = [
                "A dependent Source fingerprint or access state changed; prior entailment cannot be assumed."
            ]
        else:
            action = "none"
            reasons = ["No dependent artifact requires automatic review from this observation."]

        impacts.append(
            {
                "canonical_url": change["canonical_url"],
                "observation_query": change.get("observation_query"),
                "classification": classification,
                "source_refs": source_refs,
                "evidence_bundle_refs": evidence_refs,
                "claim_proposal_refs": claim_refs,
                "center_profile_refs": profile_refs,
                "decision_refs": decision_refs,
                "action": action,
                "promotion_blocked": (
                    classification in ACTIONABLE_CLASSIFICATIONS and has_dependents
                ),
                "reasons": reasons,
            }
        )

    blocked = [item for item in impacts if item["promotion_blocked"]]
    reobservation = [item for item in impacts if item["action"] == "reobserve"]
    return {
        "schema_version": "0.1.0",
        "run_id": run_id,
        "previous_run_id": report.get("previous_run_id"),
        "generated_at": generated_at or isoformat(),
        "summary": {
            "source_changes": len(impacts),
            "actionable_source_changes": len(blocked),
            "reobservation_gaps": len(reobservation),
            "impacted_evidence_bundles": len(
                {ref for item in blocked for ref in item["evidence_bundle_refs"]}
            ),
            "impacted_claim_proposals": len(
                {ref for item in blocked for ref in item["claim_proposal_refs"]}
            ),
            "impacted_center_profiles": len(
                {ref for item in blocked for ref in item["center_profile_refs"]}
            ),
            "impacted_decisions": len(
                {ref for item in blocked for ref in item["decision_refs"]}
            ),
            "promotion_blocked": bool(blocked),
        },
        "impacts": impacts,
        "caveat": (
            "changed and unavailable observations block promotion only when a recorded "
            "dependent artifact exists. not-observed creates a reobservation gap and is "
            "not evidence of withdrawal. This report queues review; it does not mutate "
            "append-only Claims or Decisions."
        ),
    }


def write_report(root: Path, report: dict[str, Any]) -> Path:
    path = root / "runs" / report["run_id"] / "dependency-impact.json"
    atomic_write_json(path, report)
    manifest_path = root / "runs" / report["run_id"] / "manifest.json"
    manifest = read_json(manifest_path)
    manifest["dependency_impact_ref"] = str(path.relative_to(root))
    manifest.setdefault("metrics", {})["dependency_impact"] = report["summary"]
    atomic_write_json(manifest_path, manifest)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = analyze(args.root, run_id=args.run_id)
    output = write_report(args.root, report)
    print(json.dumps({"output": str(output), "summary": report["summary"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
