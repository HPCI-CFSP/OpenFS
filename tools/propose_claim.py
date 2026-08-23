#!/usr/bin/env python3
"""Create an atomic Claim proposal from one or more Evidence bundles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json, stable_digest


ROOT = Path(__file__).resolve().parents[1]


def _numeric_id(prefix: str, value: Any) -> str:
    number = int(stable_digest(value)[:12], 16) % 1_000_000
    return f"{prefix}-{number:06d}"


def _registered_synthesis_agent(agent_id: str, registry: dict[str, Any]) -> dict[str, Any]:
    matches = [item for item in registry.get("agents", []) if item.get("agent_id") == agent_id]
    if len(matches) != 1:
        raise ValueError(f"agent_id is not uniquely registered: {agent_id}")
    agent = matches[0]
    if agent.get("role") != "synthesis":
        raise ValueError(f"agent is not registered for synthesis: {agent_id}")
    if agent.get("provider") == "unconfigured" or agent.get("model_family") == "unconfigured":
        raise ValueError(f"agent identity is unconfigured: {agent_id}")
    return agent


def propose(
    bundles: list[dict[str, Any]],
    *,
    bundle_refs: list[str],
    run_id: str,
    agent_id: str,
    statement: str,
    claim_kind: str,
    temporal_scope: str,
    conditions: list[str] | None = None,
    registry: dict[str, Any],
    created_at: str | None = None,
) -> dict[str, Any]:
    _registered_synthesis_agent(agent_id, registry)
    if len(bundles) != len(bundle_refs) or not bundles:
        raise ValueError("Evidence bundles and references must be non-empty and aligned")
    if claim_kind not in {
        "observed_fact", "reported_claim", "forecast", "interpretation", "recommendation"
    }:
        raise ValueError(f"unsupported claim kind: {claim_kind}")

    evidence_ids: list[str] = []
    lineage_ids: list[str] = []
    origin_group_ids: list[str] = []
    has_primary_source = False
    for bundle in bundles:
        if bundle.get("object_type") != "evidence":
            raise ValueError("all inputs must be Evidence bundles")
        if bundle.get("run_id") != run_id:
            raise ValueError("Evidence bundle belongs to a different Run")
        evidence_ids.extend(item["evidence_id"] for item in bundle["evidence_candidates"])
        lineage_ids.extend(item["source_lineage_id"] for item in bundle["evidence_candidates"])
        origin_group_ids.extend(bundle["origin_group_ids"])
        has_primary_source = has_primary_source or bundle["has_primary_source"]

    identity = {
        "run_id": run_id,
        "statement": statement.strip(),
        "claim_kind": claim_kind,
        "temporal_scope": temporal_scope.strip(),
        "evidence_ids": sorted(set(evidence_ids)),
    }
    claim_id = _numeric_id("CLM", identity)
    proposal_id = _numeric_id("PRP-CLM", identity)
    timestamp = created_at or isoformat()
    claim = {
        "schema_version": "0.1.0",
        "claim_id": claim_id,
        "statement": statement.strip(),
        "claim_kind": claim_kind,
        "temporal_scope": temporal_scope.strip(),
        "conditions": conditions or [],
        "evidence_ids": sorted(set(evidence_ids)),
        "source_lineage_ids": sorted(set(lineage_ids)),
        "status": "candidate",
    }
    return {
        "schema_version": "0.1.0",
        "proposal_id": proposal_id,
        "object_type": "claim",
        "run_id": run_id,
        "origin_group_ids": sorted(set(origin_group_ids)),
        "has_primary_source": has_primary_source,
        "artifact_id": claim_id,
        "created_by_agent_id": agent_id,
        "created_at": timestamp,
        "evidence_bundle_refs": bundle_refs,
        "claim_candidate": claim,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence-bundle", action="append", required=True, type=Path)
    parser.add_argument("--evidence-bundle-ref", action="append", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--statement", required=True)
    parser.add_argument("--claim-kind", required=True)
    parser.add_argument("--temporal-scope", required=True)
    parser.add_argument("--condition", action="append", default=[])
    parser.add_argument("--agent-registry", type=Path, default=ROOT / "config/agent-registry.json")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    proposal = propose(
        [read_json(path) for path in args.evidence_bundle],
        bundle_refs=args.evidence_bundle_ref,
        run_id=args.run_id,
        agent_id=args.agent_id,
        statement=args.statement,
        claim_kind=args.claim_kind,
        temporal_scope=args.temporal_scope,
        conditions=args.condition,
        registry=read_json(args.agent_registry),
    )
    atomic_write_json(args.output, proposal)
    print(json.dumps({"proposal_id": proposal["proposal_id"], "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
