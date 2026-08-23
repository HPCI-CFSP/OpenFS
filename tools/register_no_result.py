#!/usr/bin/env python3
"""Record an executed Discovery query that found no eligible responsive Source."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json, stable_digest
from register_source import canonicalize_url


ROOT = Path(__file__).resolve().parents[1]


def create(
    record: dict[str, Any],
    *,
    work_item: dict[str, Any],
    agent_id: str,
    acquisition_policy: dict[str, Any],
) -> dict[str, Any]:
    if work_item.get("kind") != "source-discovery":
        raise ValueError("Work Item is not assigned to Source discovery")
    lease = work_item.get("lease", {})
    if work_item.get("status") != "leased" or lease.get("agent_id") != agent_id:
        raise RuntimeError("No-result registration requires the current Work Item lease")
    payload = work_item.get("payload", {})
    query = record.get("query", {})
    if query.get("text") != payload.get("query"):
        raise ValueError("No-result query differs from the assigned Monitor query")
    if query.get("language") not in payload.get("languages", []):
        raise ValueError("No-result language is outside the assigned Monitor scope")
    failures = query.get("failures", [])
    if not failures:
        raise ValueError("No-result registration requires at least one failure reason")
    for failure in failures:
        if failure.get("coverage_impact") not in {"warning", "blocking"}:
            raise ValueError("No-result failures require an explicit coverage impact")
    candidates = []
    for candidate in query.get("candidates", []):
        candidates.append(
            {
                "url": canonicalize_url(candidate["url"], acquisition_policy),
                "rank": int(candidate["rank"]),
                "selected": False,
            }
        )
    timestamp = query.get("executed_at") or lease.get("acquired_at") or isoformat()
    identity = {
        "run_id": work_item["run_id"],
        "work_item_id": work_item["work_item_id"],
        "query": query["text"],
        "executed_at": timestamp,
    }
    assignment_scope = {
        key: payload[key]
        for key in ("subject_ids", "profile_fields", "query_template_id")
        if key in payload
    }
    return {
        "schema_version": "0.1.0",
        "result_id": f"NORESULT-{stable_digest(identity)[:12].upper()}",
        "object_type": "discovery_no_result",
        "run_id": work_item["run_id"],
        "work_item_id": work_item["work_item_id"],
        "created_by_agent_id": agent_id,
        "created_at": timestamp,
        "query_receipt": {
            "schema_version": "0.1.0",
            "query_receipt_id": f"QRY-{stable_digest(identity)[:12].upper()}",
            "run_id": work_item["run_id"],
            "work_item_id": work_item["work_item_id"],
            "query": query["text"],
            "language": query["language"],
            "retrieval_method": query["retrieval_method"],
            "executed_at": timestamp,
            "results": candidates,
            "failures": failures,
        },
        "assignment_scope": assignment_scope,
        "disposition": "no-eligible-responsive-source",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--work-item-id", required=True)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    work_item = read_json(
        args.root / "queue" / args.run_id / f"{args.work_item_id}.json"
    )
    output = args.output if args.output.is_absolute() else args.root / args.output
    output_ref = str(output.relative_to(args.root))
    if output_ref not in work_item.get("output_paths", []):
        raise ValueError("No-result output is outside the Work Item's declared paths")
    result = create(
        read_json(args.record),
        work_item=work_item,
        agent_id=args.agent_id,
        acquisition_policy=read_json(
            args.root / "runs" / args.run_id / "inputs/config/acquisition-policy.json"
        ),
    )
    if output.exists() and read_json(output) != result:
        raise RuntimeError("No-result output already exists with different content")
    atomic_write_json(output, result)
    print(json.dumps({"result_id": result["result_id"], "output": output_ref}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
