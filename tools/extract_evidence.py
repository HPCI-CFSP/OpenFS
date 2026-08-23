#!/usr/bin/env python3
"""Create candidate Evidence records from a rights-cleared Source result."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json, stable_digest


ROOT = Path(__file__).resolve().parents[1]


def _identifier(prefix: str, value: Any) -> str:
    return f"{prefix}-{stable_digest(value)[:12].upper()}"


def _numeric_proposal_id(value: Any) -> str:
    number = int(stable_digest(value)[:12], 16) % 1_000_000
    return f"PRP-EVD-{number:06d}"


def extract(
    source_result: dict[str, Any],
    *,
    source_result_ref: str,
    run_id: str,
    work_item_id: str,
    agent_id: str,
    created_at: str | None = None,
) -> dict[str, Any]:
    if source_result.get("object_type") != "source":
        raise ValueError("input must be a Source discovery result")
    if source_result.get("run_id") != run_id:
        raise ValueError("Source result belongs to a different Run")
    receipt = source_result["source_receipt"]
    rights = receipt["rights"]
    if rights["acquisition_decision"] not in {"evidence-excerpt", "approved-snapshot"}:
        raise RuntimeError("Source rights do not permit Evidence extraction")
    security = receipt["security"]
    if security.get("prompt_injection_suspected"):
        raise RuntimeError("Source is quarantined for suspected prompt injection")
    passages = source_result.get("candidate_passages", [])
    if not passages:
        raise ValueError("Source result has no candidate passages")

    timestamp = created_at or isoformat()
    candidates = []
    for passage in passages:
        claim = passage.get("candidate_claim")
        if not claim:
            raise ValueError(f"candidate passage has no candidate_claim: {passage['passage_id']}")
        if passage.get("passage_kind") not in {"quote", "paraphrase", "structured-field"}:
            raise ValueError(f"invalid passage_kind: {passage.get('passage_kind')}")
        evidence_identity = {
            "source_id": receipt["source_id"],
            "locator": passage["locator"],
            "text": passage["text"],
            "statement_supported": claim,
        }
        candidates.append(
            {
                "schema_version": "0.1.0",
                "evidence_id": _identifier("EVD", evidence_identity),
                "run_id": run_id,
                "work_item_id": work_item_id,
                "source_id": receipt["source_id"],
                "source_lineage_id": source_result["source_lineage"]["lineage_id"],
                "source_locator": passage["locator"],
                "excerpt": passage["text"],
                "excerpt_kind": passage["passage_kind"],
                "statement_supported": claim,
                "status": "candidate",
                "extracted_by_agent_id": agent_id,
                "extracted_at": timestamp,
                "evidence_hash": stable_digest(evidence_identity),
            }
        )
    return {
        "schema_version": "0.1.0",
        "proposal_id": _numeric_proposal_id(
            {"run_id": run_id, "source_id": receipt["source_id"], "evidence": candidates}
        ),
        "object_type": "evidence",
        "run_id": run_id,
        "work_item_id": work_item_id,
        "source_result_ref": source_result_ref,
        "source_id": receipt["source_id"],
        "origin_group_ids": [receipt["origin_group_id"]],
        "has_primary_source": receipt["primary_source"],
        "created_by_agent_id": agent_id,
        "created_at": timestamp,
        "evidence_candidates": candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-result", required=True, type=Path)
    parser.add_argument("--source-result-ref", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--work-item-id", required=True)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    bundle = extract(
        read_json(args.source_result),
        source_result_ref=args.source_result_ref,
        run_id=args.run_id,
        work_item_id=args.work_item_id,
        agent_id=args.agent_id,
    )
    atomic_write_json(args.output, bundle)
    print(json.dumps({"proposal_id": bundle["proposal_id"], "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
