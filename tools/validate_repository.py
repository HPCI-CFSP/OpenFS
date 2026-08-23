#!/usr/bin/env python3
"""Run dependency-free structural checks for the OpenFS repository."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    "docs/architecture.md",
    "docs/policies/claim-acceptance.md",
    "docs/policies/information-boundary.md",
    "docs/policies/consensus-policy.md",
    "docs/security/threat-model.md",
    "config/consensus-policy.json",
    "config/agent-registry.json",
    "schemas/proposal.schema.json",
    "schemas/claim.schema.json",
    "schemas/source-lineage.schema.json",
    "schemas/assessment.schema.json",
    "schemas/decision.schema.json",
    "schemas/run.schema.json",
]
ACTION_PATTERN = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)", re.MULTILINE)
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def validate_json_files(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(root.rglob("*.json")):
        if ".git" in path.parts:
            continue
        try:
            load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON: {path.relative_to(root)}: {exc}")
    return errors


def validate_jsonl_files(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(root.rglob("*.jsonl")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(
                    f"invalid JSONL: {path.relative_to(root)}:{line_number}: {exc}"
                )
    return errors


def validate_schema_headers(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted((root / "schemas").glob("*.schema.json")):
        schema = load_json(path)
        for key in ("$schema", "$id", "title", "type"):
            if key not in schema:
                errors.append(f"schema missing {key}: {path.relative_to(root)}")
    return errors


def validate_workflow_action_pins(root: Path) -> list[str]:
    errors: list[str] = []
    workflow_dir = root / ".github" / "workflows"
    if not workflow_dir.exists():
        return errors
    for path in sorted(workflow_dir.glob("*.yml")):
        for reference in ACTION_PATTERN.findall(path.read_text(encoding="utf-8")):
            if reference.startswith("./"):
                continue
            if "@" not in reference:
                errors.append(f"action has no version: {path.relative_to(root)}: {reference}")
                continue
            action, revision = reference.rsplit("@", 1)
            if not FULL_SHA.fullmatch(revision):
                errors.append(
                    f"action is not pinned to a full SHA: {path.relative_to(root)}: "
                    f"{action}@{revision}"
                )
    return errors


def validate_required_files(root: Path) -> list[str]:
    return [f"missing required file: {path}" for path in REQUIRED_FILES if not (root / path).is_file()]


def validate_consensus_configuration(root: Path) -> list[str]:
    policy = load_json(root / "config" / "consensus-policy.json")
    required_rule_fields = {
        "minimum_assessments",
        "minimum_support",
        "minimum_support_independence_groups",
        "minimum_origin_groups",
    }
    errors: list[str] = []
    for object_type, rule in policy.get("rules", {}).items():
        missing = required_rule_fields - set(rule)
        if missing:
            errors.append(f"consensus rule {object_type} missing: {sorted(missing)}")
        if rule.get("minimum_support", 0) > rule.get("minimum_assessments", 0):
            errors.append(f"consensus rule {object_type} requires more support than assessments")
    return errors


def run(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_required_files(root))
    errors.extend(validate_json_files(root))
    errors.extend(validate_jsonl_files(root))
    if (root / "schemas").exists():
        errors.extend(validate_schema_headers(root))
    errors.extend(validate_workflow_action_pins(root))
    if (root / "config" / "consensus-policy.json").exists():
        errors.extend(validate_consensus_configuration(root))
    return errors


def main() -> int:
    errors = run()
    if errors:
        print("OpenFS repository validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("OpenFS repository validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
