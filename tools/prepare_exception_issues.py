#!/usr/bin/env python3
"""Prepare sanitized, deduplicable GitHub Issue payloads for open Exceptions."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json, stable_digest


ROOT = Path(__file__).resolve().parents[1]


def issue_payload(
    exception: dict[str, Any], *, exception_ref: str, generated_at: str
) -> dict[str, Any]:
    exception_id = exception["exception_id"]
    run_id = exception["run_id"]
    kind = exception.get(
        "exception_kind", exception.get("error", {}).get("kind", "work-item-failure")
    )
    marker = f"<!-- openfs-exception:{exception_id} -->"
    safe_details = [
        marker,
        "",
        "This Issue was prepared from a structured OpenFS Exception.",
        "",
        f"- Run: `{run_id}`",
        f"- Exception: `{exception_id}`",
        f"- Kind: `{kind}`",
        f"- Repository record: `{exception_ref}`",
    ]
    if exception.get("reason"):
        safe_details.append(f"- Stop reason: `{exception['reason']}`")
    if exception.get("observed") is not None:
        safe_details.append(f"- Observed: `{exception['observed']}`")
    if exception.get("limit") is not None:
        safe_details.append(f"- Limit: `{exception['limit']}`")
    if exception.get("unmet_requirements"):
        safe_details.append(
            "- Unmet requirements: "
            + ", ".join(f"`{item}`" for item in exception["unmet_requirements"])
        )
    safe_details.extend(
        [
            "",
            "Review the repository record before taking action. Raw external-content "
            "error messages are intentionally excluded from this Issue body.",
        ]
    )
    return {
        "schema_version": "0.1.0",
        "payload_id": f"ISSUE-{stable_digest(exception_id)[:12].upper()}",
        "exception_id": exception_id,
        "exception_ref": exception_ref,
        "title": f"[OpenFS] {run_id} requires action: {kind}"[:256],
        "body": "\n".join(safe_details),
        "labels": ["openfs-exception", "needs-owner-action"],
        "deduplication_marker": marker,
        "generated_at": generated_at,
        "publication_status": "prepared",
    }


def prepare(root: Path, *, generated_at: str | None = None) -> list[Path]:
    generated_at = generated_at or isoformat()
    outputs: list[Path] = []
    for path in sorted((root / "reviews" / "exceptions").glob("RUN-*/*.json")):
        exception = read_json(path)
        if exception.get("status") != "open" or not exception.get(
            "requires_owner_action", True
        ):
            continue
        payload = issue_payload(
            exception,
            exception_ref=str(path.relative_to(root)),
            generated_at=generated_at,
        )
        safe_id = re.sub(r"[^A-Za-z0-9_.-]", "-", exception["exception_id"])
        output = root / "reviews" / "issues" / exception["run_id"] / f"{safe_id}.json"
        if output.exists():
            existing = read_json(output)
            if existing.get("exception_id") != payload["exception_id"]:
                raise RuntimeError(f"Issue payload identity collision: {output}")
            payload["publication_status"] = existing.get(
                "publication_status", "prepared"
            )
            payload["generated_at"] = existing.get("generated_at", generated_at)
            for key in ("github_issue_number", "github_issue_url"):
                if key in existing:
                    payload[key] = existing[key]
        atomic_write_json(output, payload)
        outputs.append(output)
    return outputs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--generated-at")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    outputs = prepare(args.root, generated_at=args.generated_at)
    print(json.dumps({"prepared": [str(path) for path in outputs]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
