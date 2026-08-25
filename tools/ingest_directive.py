#!/usr/bin/env python3
"""Convert a structured public GitHub Issue export into an OpenFS Directive."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, read_json, stable_digest


ROOT = Path(__file__).resolve().parents[1]
PRIORITIES = {"low", "normal", "high", "urgent"}


def ingest_issue(issue: dict[str, Any]) -> dict[str, Any]:
    required = {
        "issue_number",
        "html_url",
        "title",
        "author",
        "created_at",
        "objective",
        "scope",
        "expected_output",
        "priority",
        "public_information_confirmed",
        "labels",
    }
    missing = required - set(issue)
    if missing:
        raise ValueError(f"Issue export is missing fields: {sorted(missing)}")
    issue_number = issue["issue_number"]
    if not isinstance(issue_number, int) or issue_number < 1 or issue_number > 999999:
        raise ValueError("issue_number must be an integer between 1 and 999999")
    if issue["priority"] not in PRIORITIES:
        raise ValueError(f"invalid Directive priority: {issue['priority']}")
    if issue["public_information_confirmed"] is not True:
        raise ValueError("Directive ingestion requires explicit public-information confirmation")
    labels = set(issue["labels"])
    if "research-directive" not in labels:
        raise ValueError("Issue lacks the research-directive label")
    status = "approved" if "directive-approved" in labels else "proposed"
    scope = issue["scope"]
    if not isinstance(scope, list) or not all(isinstance(item, str) and item for item in scope):
        raise ValueError("scope must be a list of non-empty Task or Topic IDs")

    instruction_sections = [
        f"Objective: {issue['objective'].strip()}",
        f"Expected output: {issue['expected_output'].strip()}",
    ]
    if issue.get("suggested_sources"):
        instruction_sections.append(
            "Suggested public sources: " + "; ".join(issue["suggested_sources"])
        )
    directive_id = f"DIR-{issue_number:06d}"
    source_record = {
        "kind": "github-issue",
        "issue_number": issue_number,
        "url": issue["html_url"],
        "content_digest": stable_digest(issue),
        "untrusted_input": True,
    }
    return {
        "schema_version": "0.1.0",
        "directive_id": directive_id,
        "directive_type": "research-instruction",
        "application_mode": "once",
        "title": issue["title"].strip(),
        "instruction": "\n".join(instruction_sections),
        "priority": issue["priority"],
        "status": status,
        "submitted_by": issue["author"],
        "submitted_at": issue["created_at"],
        "scope": scope,
        "processed_run_ids": [],
        "result_decision_ids": [],
        "source": source_record,
    }


def write_directive(output_dir: Path, directive: dict[str, Any]) -> Path:
    path = output_dir / f"{directive['directive_id']}.json"
    if path.exists():
        existing = read_json(path)
        if existing != directive:
            raise RuntimeError(f"Directive already exists with different content: {path.name}")
        return path
    atomic_write_json(path, directive)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "reviews" / "directives",
    )
    args = parser.parse_args()
    directive = ingest_issue(read_json(args.input))
    path = write_directive(args.output_dir, directive)
    print(json.dumps({"directive_id": directive["directive_id"], "path": str(path)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
