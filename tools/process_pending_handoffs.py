#!/usr/bin/env python3
"""Accept all pending merged Handoffs and expand their Runs deterministically."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from accept_handoff import accept_handoff
from openfs_runtime import atomic_write_json, isoformat, read_json
from run_controller import expand_followups


ROOT = Path(__file__).resolve().parents[1]


def process(
    root: Path,
    *,
    allow_disabled_pilot_agent: bool = False,
    processed_at: str | None = None,
) -> dict[str, Any]:
    processed_at = processed_at or isoformat()
    accepted = []
    already_accepted = []
    affected_runs = set()
    for path in sorted((root / "handoffs").glob("RUN-*/WORK-*.json")):
        handoff = read_json(path)
        handoff_ref = str(path.relative_to(root))
        work_path = (
            root
            / "queue"
            / handoff["run_id"]
            / f"{handoff['work_item_id']}.json"
        )
        work_item = read_json(work_path)
        if work_item.get("status") == "completed":
            if work_item.get("handoff_ref") == handoff_ref:
                already_accepted.append(handoff_ref)
                continue
            raise RuntimeError(
                f"completed Work Item has a different completion path: {work_path}"
            )
        accept_handoff(
            root,
            handoff_ref=handoff_ref,
            allow_disabled_pilot_agent=allow_disabled_pilot_agent,
            now=processed_at,
        )
        accepted.append(handoff_ref)
        affected_runs.add(handoff["run_id"])

    expansions = []
    for run_id in sorted(affected_runs):
        result = expand_followups(root, run_id=run_id)
        expansions.append(
            {
                "run_id": run_id,
                "created_work_item_ids": [
                    item["work_item_id"] for item in result["created"]
                ],
                "run_status": result["manifest"]["status"],
            }
        )
    return {
        "schema_version": "0.1.0",
        "processed_at": processed_at,
        "accepted_handoff_refs": accepted,
        "already_accepted_handoff_refs": already_accepted,
        "affected_run_ids": sorted(affected_runs),
        "expansions": expansions,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--allow-disabled-pilot-agent", action="store_true")
    parser.add_argument("--processed-at")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    result = process(
        args.root,
        allow_disabled_pilot_agent=args.allow_disabled_pilot_agent,
        processed_at=args.processed_at,
    )
    output = args.output if args.output.is_absolute() else args.root / args.output
    atomic_write_json(output, result)
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
