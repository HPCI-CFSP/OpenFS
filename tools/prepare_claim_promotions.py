#!/usr/bin/env python3
"""Prepare canonical Claim changes from currently eligible readiness records."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json
from promote_claim import promote


ROOT = Path(__file__).resolve().parents[1]


def prepare(
    root: Path,
    *,
    promoted_at: str | None = None,
) -> dict[str, Any]:
    timestamp = promoted_at or isoformat()
    candidates: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "runs").glob("RUN-*/promotion-readiness.json")):
        report = read_json(path)
        for item in report.get("claims", []):
            if item.get("status") != "eligible":
                continue
            candidates[item["proposal_ref"]] = {
                "run_id": report["run_id"],
                "proposal_ref": item["proposal_ref"],
                "decision_ref": item["decision_ref"],
                "readiness_ref": str(path.relative_to(root)),
            }

    prepared: list[dict[str, Any]] = []
    for candidate in sorted(candidates.values(), key=lambda item: item["proposal_ref"]):
        output, canonical = promote(
            root,
            proposal_ref=candidate["proposal_ref"],
            decision_ref=candidate["decision_ref"],
            promoted_at=timestamp,
        )
        prepared.append(
            {
                **candidate,
                "canonical_claim_id": canonical["canonical_claim_id"],
                "canonical_ref": str(output.relative_to(root)),
                "promotion_digest": canonical["promotion_digest"],
            }
        )
    return {
        "schema_version": "0.1.0",
        "prepared_at": timestamp,
        "eligible_candidate_count": len(candidates),
        "prepared_count": len(prepared),
        "affected_run_ids": sorted({item["run_id"] for item in prepared}),
        "prepared": prepared,
        "outputs": sorted(
            (
                {item["canonical_ref"] for item in prepared}
                | {"knowledge/claims/index.json", "TBD.md"}
            )
            if prepared
            else []
        ),
        "caveat": (
            "These are reviewable branch changes only. This preparation does not "
            "merge, publish, or authorize a Recommendation."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--promoted-at")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    summary = prepare(args.root, promoted_at=args.promoted_at)
    output = args.output if args.output.is_absolute() else args.root / args.output
    atomic_write_json(output, summary)
    print(json.dumps({"output": str(output), **summary}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
