#!/usr/bin/env python3
"""Validate the public AI-agent development suite and its fail-closed boundaries."""

from __future__ import annotations

import argparse
import json
import math
import subprocess
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:  # pragma: no cover
    Draft202012Validator = None
    FormatChecker = None


REQUIRED_CATEGORIES = {
    "evidence-traceability",
    "timing-classification",
    "information-boundary",
    "consensus-integrity",
    "bilingual-link-integrity",
    "benchmark-planning",
}
REQUIRED_DENIALS = {
    "read-secrets",
    "direct-network",
    "write-outside-allowlist",
    "publish-without-consensus",
}


def evaluate(suite: dict[str, Any], root: Path) -> dict[str, Any]:
    errors: list[str] = []
    rubric_ids = [item["rubric_id"] for item in suite["rubrics"]]
    if len(rubric_ids) != len(set(rubric_ids)):
        errors.append("rubrics: rubric_id values must be unique")
    if not math.isclose(sum(item["weight"] for item in suite["rubrics"]), 1.0):
        errors.append("rubrics: weights must sum to 1.0")
    known_rubrics = set(rubric_ids)

    tasks = suite["tasks"]
    task_ids = [task["task_id"] for task in tasks]
    if len(task_ids) != len(set(task_ids)):
        errors.append("tasks: task_id values must be unique")
    categories = {task["category"] for task in tasks}
    missing_categories = sorted(REQUIRED_CATEGORIES - categories)
    if missing_categories:
        errors.append(f"tasks: missing required categories {missing_categories}")

    referenced_paths: set[str] = set()
    for task in tasks:
        task_id = task["task_id"]
        unknown_rubrics = sorted(set(task["rubric_refs"]) - known_rubrics)
        if unknown_rubrics:
            errors.append(f"{task_id}: unknown rubric references {unknown_rubrics}")
        missing_denials = sorted(REQUIRED_DENIALS - set(task["forbidden_actions"]))
        if missing_denials:
            errors.append(f"{task_id}: missing required forbidden actions {missing_denials}")
        if len(task["expected_facts_ja"]) != len(task["expected_facts_en"]):
            errors.append(f"{task_id}: Japanese and English expected facts differ in count")
        if task["network_mode"] == "none" and any(
            token in tool.lower() for tool in task["allowed_tools"] for token in ("browser", "fetch", "network")
        ):
            errors.append(f"{task_id}: network-disabled task declares a network-capable tool")
        for raw_path in task["input_paths"]:
            path = PurePosixPath(raw_path)
            if path.is_absolute() or ".." in path.parts or ":" in raw_path:
                errors.append(f"{task_id}: unsafe input path {raw_path}")
                continue
            referenced_paths.add(raw_path)
            if not (root / path).is_file():
                errors.append(f"{task_id}: input path does not exist: {raw_path}")
                continue
            pinned = subprocess.run(
                ["git", "cat-file", "-e", f"{suite['source_commit']}:{raw_path}"],
                cwd=root,
                capture_output=True,
                text=True,
                check=False,
            )
            if pinned.returncode != 0:
                errors.append(f"{task_id}: input path is absent from source_commit: {raw_path}")

    output_path = root / suite["output_schema_path"]
    if not output_path.is_file():
        errors.append("output_schema_path: file does not exist")
    if suite["formal_holdout_status"]["available"] is not False:
        errors.append("formal_holdout_status: public development suite cannot claim a hidden holdout")

    return {
        "suite_id": suite["suite_id"],
        "counts": {
            "tasks": len(tasks),
            "categories": len(categories),
            "rubrics": len(rubric_ids),
            "input_paths": len(referenced_paths),
        },
        "control_errors": errors,
        "ready_for_public_development_runs": not errors,
        "formal_holdout_available": False,
        "note": (
            "A passing public suite supports development and regression testing only. "
            "It cannot establish generalization or replace an independently controlled hidden holdout."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("suite", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    payload = json.loads(args.suite.read_text(encoding="utf-8"))
    if Draft202012Validator is None:
        parser.error("jsonschema is required; install requirements-validation.txt")
    schema_path = args.root / "schemas" / "agent-evaluation-task-suite.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema_errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload),
        key=lambda item: list(item.path),
    )
    if schema_errors:
        for error in schema_errors:
            location = "/".join(str(item) for item in error.absolute_path) or "$"
            print(f"{location}: {error.message}")
        return 1
    result = evaluate(payload, args.root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ready_for_public_development_runs"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
