#!/usr/bin/env python3
"""Prepare a default-deny human review record for a completed Pilot Run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json, stable_digest


ROOT = Path(__file__).resolve().parents[1]
CHECKS = (
    "public_information_boundary",
    "citation_sample",
    "coverage",
    "false_positive_review",
    "dissent_review",
    "cost_review",
)


def prepare(
    root: Path, *, run_id: str, prepared_at: str | None = None
) -> tuple[dict[str, Any], Path]:
    manifest_path = root / "runs" / run_id / "manifest.json"
    brief_path = root / "reviews" / "briefs" / f"{run_id}.json"
    if not manifest_path.is_file() or not brief_path.is_file():
        raise ValueError("Run approval requires a final manifest and generated review Brief")
    manifest = read_json(manifest_path)
    brief = read_json(brief_path)
    if manifest.get("mode") != "pilot" or manifest.get("status") != "completed":
        raise ValueError("Run approval drafts may be prepared only for completed Pilot Runs")
    identity = {
        "run_id": run_id,
        "manifest_digest": stable_digest(manifest),
        "brief_digest": stable_digest(brief),
    }
    approval = {
        "schema_version": "0.1.0",
        "approval_id": f"RUNAPP-{stable_digest(identity)[:12].upper()}",
        "run_id": run_id,
        "monitor_id": manifest["monitor_id"],
        "status": "draft",
        "manifest_digest": identity["manifest_digest"],
        "brief_ref": str(brief_path.relative_to(root)),
        "brief_digest": identity["brief_digest"],
        "prepared_at": prepared_at or isoformat(),
        "reviewed_by": None,
        "reviewed_at": None,
        "checks": {name: False for name in CHECKS},
        "notes": "",
    }
    output = root / "reviews" / "run-approvals" / f"{run_id}.json"
    if output.is_file():
        existing = read_json(output)
        if existing == approval:
            return existing, output
        raise FileExistsError(
            "Run approval record already exists; review or revoke it instead of overwriting"
        )
    atomic_write_json(output, approval)
    return approval, output


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--prepared-at")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    approval, output = prepare(
        args.root, run_id=args.run_id, prepared_at=args.prepared_at
    )
    print(
        json.dumps(
            {
                "output": str(output),
                "approval_id": approval["approval_id"],
                "status": approval["status"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
