#!/usr/bin/env python3
"""Prepare one deduplicated GitHub Issue for high-priority roadmap freshness work."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, read_json


ROOT = Path(__file__).resolve().parents[1]
GROUP_ID = "ROADMAP-FRESHNESS-P0"
MARKER = "<!-- openfs-managed-issue:roadmap-freshness-p0 -->"
AUDIT_REF = "_automation/roadmap-freshness-audit.json"


def build_payload(audit: dict[str, Any]) -> dict[str, Any]:
    attention = [
        item
        for item in audit.get("attention_items", [])
        if item.get("severity") in {"critical", "high"}
    ]
    attention.sort(
        key=lambda item: (
            0 if item["severity"] == "critical" else 1,
            item["roadmap_id"],
            item["object_id"],
        )
    )
    desired_state = "open" if attention else "closed"
    summary = audit.get("summary", {})
    lines = [
        MARKER,
        "",
        "This managed Issue is refreshed by the weekly OpenFS review workflow.",
        "It lists only critical or high-priority roadmap freshness attention; lower-priority items remain in the audit artifact and GitHub Pages.",
        "Freshness attention is a recheck queue, not a finding that a roadmap claim is wrong.",
        "",
        f"- Audit: `{audit.get('audit_id', 'unknown')}`",
        f"- Generated at: `{audit.get('generated_at', 'unknown')}`",
        f"- Desired Issue state: `{desired_state}`",
        f"- Roadmaps: `{summary.get('roadmap_count', 0)}`",
        f"- Milestones: `{summary.get('milestone_count', 0)}`",
        f"- Critical/high attention: `{len(attention)}`",
        "",
    ]
    if attention:
        lines.extend(
            [
                "Priority recheck queue:",
                "",
                "| Severity | Roadmap | Object | Reason |",
                "|---|---|---|---|",
            ]
        )
        lines.extend(
            f"| {item['severity']} | `{item['roadmap_id']}` | `{item['object_id']}` | {item['reason']} |"
            for item in attention
        )
        lines.extend(
            [
                "",
                "The next automated research loop should recheck these objects against official project, standards, and vendor sources. Human intervention is required only for policy, access, or interpretation exceptions that automation cannot resolve.",
            ]
        )
    else:
        lines.append(
            "No critical or high-priority roadmap freshness attention remains in this audit."
        )

    return {
        "schema_version": "0.1.0",
        "payload_id": "ISSUE-ROADMAP-FRESHNESS-P0",
        "exception_id": GROUP_ID,
        "exception_ref": AUDIT_REF,
        "exception_group_id": GROUP_ID,
        "exception_ids": [item["attention_id"] for item in attention]
        or ["RFAI-NONE"],
        "exception_refs": [AUDIT_REF],
        "run_ids": [audit.get("audit_id", "RFA-UNKNOWN")],
        "exception_kind": "roadmap-freshness-attention",
        "unmet_requirements": sorted({item["reason"] for item in attention}),
        "publication_blocked": False,
        "desired_issue_state": desired_state,
        "title": (
            f"[OpenFS] P0 roadmap freshness recheck queue ({len(attention)})"
            if attention
            else "[OpenFS] P0 roadmap freshness recheck queue resolved"
        ),
        "body": "\n".join(lines),
        "labels": [],
        "deduplication_marker": MARKER,
        "generated_at": audit["generated_at"],
        "publication_status": "prepared",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    atomic_write_json(args.output, build_payload(read_json(args.audit)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
