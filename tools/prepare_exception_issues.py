#!/usr/bin/env python3
"""Prepare sanitized, deduplicable GitHub Issue payloads for open Exceptions."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from openfs_runtime import (
    atomic_write_json,
    exception_group_key,
    isoformat,
    read_json,
    stable_digest,
)


ROOT = Path(__file__).resolve().parents[1]


def grouped_issue_payload(
    exceptions: list[tuple[str, dict[str, Any]]], *, generated_at: str
) -> dict[str, Any]:
    if not exceptions:
        raise ValueError("Issue group requires at least one Exception")
    fingerprints = {exception_group_key(exception) for _, exception in exceptions}
    if len(fingerprints) != 1:
        raise ValueError("Issue group contains Exceptions with different owner actions")
    kind, unmet_requirements, publication_blocked = fingerprints.pop()
    group_identity = {
        "exception_kind": kind,
        "unmet_requirements": list(unmet_requirements),
        "publication_blocked": publication_blocked,
    }
    group_id = f"EXCGRP-{stable_digest(group_identity)[:12].upper()}"
    marker = f"<!-- openfs-exception-group:{group_id} -->"
    exception_refs = sorted(ref for ref, _ in exceptions)
    exception_ids = sorted(exception["exception_id"] for _, exception in exceptions)
    run_ids = sorted({exception["run_id"] for _, exception in exceptions})
    safe_details = [
        marker,
        "",
        "This Issue was prepared from structured OpenFS Exceptions that require the same owner action.",
        "",
        f"- Exception group: `{group_id}`",
        f"- Kind: `{kind}`",
        f"- Runs: {', '.join(f'`{item}`' for item in run_ids)}",
        f"- Publication blocked: `{'yes' if publication_blocked else 'no'}`",
    ]
    if unmet_requirements:
        safe_details.append(
            "- Unmet requirements: "
            + ", ".join(f"`{item}`" for item in unmet_requirements)
        )
    safe_details.extend(["", "Repository records:"])
    safe_details.extend(f"- `{item}`" for item in exception_refs[:50])
    if len(exception_refs) > 50:
        safe_details.append(
            f"- {len(exception_refs) - 50} additional records are retained in the grouped payload."
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
        "payload_id": f"ISSUE-{stable_digest(group_id)[:12].upper()}",
        "exception_id": group_id,
        "exception_ref": exception_refs[0],
        "exception_group_id": group_id,
        "exception_ids": exception_ids,
        "exception_refs": exception_refs,
        "run_ids": run_ids,
        "exception_kind": kind,
        "unmet_requirements": list(unmet_requirements),
        "publication_blocked": publication_blocked,
        "title": f"[OpenFS] Owner action required: {kind}"[:256],
        "body": "\n".join(safe_details),
        "labels": ["openfs-exception", "needs-owner-action"],
        "deduplication_marker": marker,
        "generated_at": generated_at,
        "publication_status": "prepared",
    }


def issue_payload(
    exception: dict[str, Any], *, exception_ref: str, generated_at: str
) -> dict[str, Any]:
    """Compatibility wrapper for callers preparing one Exception."""
    return grouped_issue_payload(
        [(exception_ref, exception)], generated_at=generated_at
    )


def prepare(root: Path, *, generated_at: str | None = None) -> list[Path]:
    generated_at = generated_at or isoformat()
    grouped: dict[
        tuple[str, tuple[str, ...], bool], list[tuple[str, dict[str, Any]]]
    ] = {}
    for path in sorted((root / "reviews" / "exceptions").glob("RUN-*/*.json")):
        exception = read_json(path)
        if exception.get("status") != "open" or not exception.get(
            "requires_owner_action", True
        ):
            continue
        grouped.setdefault(exception_group_key(exception), []).append(
            (str(path.relative_to(root)), exception)
        )
    outputs: list[Path] = []
    for exceptions in grouped.values():
        payload = grouped_issue_payload(exceptions, generated_at=generated_at)
        safe_id = re.sub(r"[^A-Za-z0-9_.-]", "-", payload["exception_group_id"])
        output = root / "reviews" / "issues" / "groups" / f"{safe_id}.json"
        if output.exists():
            existing = read_json(output)
            if existing.get("exception_group_id") != payload["exception_group_id"]:
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
