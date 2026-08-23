#!/usr/bin/env python3
"""Validate and record application of an approved Directive to one Run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json, stable_digest


ROOT = Path(__file__).resolve().parents[1]


def apply(
    *,
    directive: dict[str, Any],
    manifest: dict[str, Any],
    work_item: dict[str, Any],
    agent_id: str,
    applied_at: str | None = None,
) -> dict[str, Any]:
    if work_item.get("kind") != "apply-directive":
        raise ValueError("Work Item is not an apply-directive item")
    if work_item.get("run_id") != manifest.get("run_id"):
        raise ValueError("Work Item and Run identities differ")
    directive_id = work_item.get("payload", {}).get("directive_id")
    if directive.get("directive_id") != directive_id:
        raise ValueError("Directive identity differs from the Work Item")
    if directive.get("status") not in {"approved", "scheduled"}:
        raise ValueError("Directive is not approved for application")
    scope = directive.get("scope", [])
    if scope and manifest.get("task_id") not in scope:
        raise ValueError("Directive scope does not include the Run Task")
    instruction_digest = stable_digest(directive["instruction"])
    if instruction_digest != work_item["payload"].get("instruction_digest"):
        raise ValueError("Directive instruction changed after Run creation")
    directive_type = directive.get("directive_type", "research-instruction")
    return {
        "schema_version": "0.1.0",
        "directive_id": directive_id,
        "run_id": manifest["run_id"],
        "work_item_id": work_item["work_item_id"],
        "created_by_agent_id": agent_id,
        "applied_at": applied_at or isoformat(),
        "directive_digest": stable_digest(directive),
        "instruction_digest": instruction_digest,
        "scope": scope,
        "authorization_bounds": {
            "information_plane": "public",
            "publication_approved": directive_type == "publication-approval",
            "high_impact_recommendation_approved": False,
            "policy_change_approved": directive_type == "governance",
        },
        "status": "applied",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--work-item-id", required=True)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    work_item = read_json(
        args.root / "queue" / args.run_id / f"{args.work_item_id}.json"
    )
    manifest = read_json(args.root / "runs" / args.run_id / "manifest.json")
    directive_id = work_item.get("payload", {}).get("directive_id")
    source_ref = f"reviews/directives/{directive_id}.json"
    directive_ref = manifest.get("directive_snapshots", {}).get(source_ref)
    if not directive_ref:
        raise ValueError("Run has no pinned Directive snapshot")
    receipt = apply(
        directive=read_json(args.root / directive_ref),
        manifest=manifest,
        work_item=work_item,
        agent_id=args.agent_id,
        applied_at=work_item.get("lease", {}).get("acquired_at")
        or work_item.get("updated_at"),
    )
    if args.output.exists():
        if read_json(args.output) != receipt:
            raise RuntimeError("Directive application receipt already differs")
    else:
        atomic_write_json(args.output, receipt)
    print(json.dumps({"output": str(args.output), "directive_id": directive_id}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
