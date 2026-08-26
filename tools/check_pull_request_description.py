#!/usr/bin/env python3
"""Reject placeholder pull-request titles and descriptions."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any


REQUIRED_HEADINGS = (
    "## Purpose",
    "## Provenance",
    "## Boundary and risk",
    "## Validation",
    "## Review notes",
)
PLACEHOLDER_PHRASES = (
    "Describe the work item and expected outcome.",
    "State the user-visible problem, the chosen change, and the expected outcome.",
    "Delete this guidance and write the concrete purpose before requesting review.",
    "<!-- required -->",
    "<!-- required for public or canonical changes -->",
    "<!-- use N/A only",
    "<!-- list each",
    "<!-- full SHA -->",
)
REQUIRED_CHECKS = (
    "Public information only",
    "No secrets, personal data, or private run logs",
    "External content was treated as untrusted data",
    "Changed paths pass `tools/check_agent_permissions.py` for the declared role",
    "Canonical changes are covered by a human Directive or an authorized promotion workflow",
    "`python3 tools/validate_repository.py`",
    "`python3 -m unittest discover -s tests -v`",
    "Dissent and unresolved exceptions are linked",
    "Coverage Gaps and provisional/Consensus state are visible",
    "Rollback or supersession path is described below",
)
REQUIRED_PROVENANCE_LABELS = (
    "Agent ID / role, or human maintainer",
    "Human Directive ID(s)",
    "Task / Monitor / Work Item IDs",
    "Run ID",
    "Proposal / Assessment / Decision IDs",
    "Base commit",
)
REQUIRED_REVIEW_LABELS = (
    "Coverage Gaps / dissent",
    "Security-boundary effect",
    "Rollback or supersession path",
    "Pages paths to inspect",
)


def _value_after_label(body: str, label: str) -> str | None:
    match = re.search(
        rf"^[ \t]*-[ \t]*{re.escape(label)}[ \t]*:[ \t]*(.*?)[ \t]*$",
        body,
        flags=re.MULTILINE,
    )
    return match.group(1).strip() if match else None


def validate_pull_request(payload: dict[str, Any]) -> list[str]:
    pull_request = payload.get("pull_request", payload)
    title = str(pull_request.get("title", "")).strip()
    body = str(pull_request.get("body") or "")
    errors: list[str] = []

    if not title:
        errors.append("pull-request title is empty")
    normalized_title = re.sub(r"[-_/]+", " ", title).strip().lower()
    if normalized_title in {
        "maintainer system planning security",
        "update",
        "openfs update",
    }:
        errors.append("pull-request title is a generic branch-derived title")

    if len(body.strip()) < 400:
        errors.append("pull-request description is too short to record the required review context")
    for heading in REQUIRED_HEADINGS:
        if heading not in body:
            errors.append(f"missing required heading: {heading}")
    for phrase in PLACEHOLDER_PHRASES:
        if phrase in body:
            errors.append(f"template guidance remains in description: {phrase}")

    for label in (*REQUIRED_PROVENANCE_LABELS, *REQUIRED_REVIEW_LABELS):
        value = _value_after_label(body, label)
        if value is None:
            errors.append(f"missing required field: {label}")
        elif not value:
            errors.append(f"required field is empty: {label}")

    base_commit = _value_after_label(body, "Base commit") or ""
    if not re.search(r"\b[0-9a-f]{40}\b", base_commit):
        errors.append("Base commit must contain a full 40-character commit SHA")

    for label in REQUIRED_CHECKS:
        checked = re.search(
            rf"^\s*-\s*\[[xX]\]\s*{re.escape(label)}\s*$",
            body,
            flags=re.MULTILINE,
        )
        if not checked:
            errors.append(f"required completed check is missing: {label}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", type=Path)
    args = parser.parse_args()
    event_path = args.event or Path(os.environ.get("GITHUB_EVENT_PATH", ""))
    if not str(event_path) or not event_path.is_file():
        raise SystemExit("GitHub pull-request event JSON is required")
    payload = json.loads(event_path.read_text(encoding="utf-8"))
    errors = validate_pull_request(payload)
    if errors:
        print("Pull-request description validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Pull-request title and description are complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
