#!/usr/bin/env python3
"""Parse every GitHub Actions workflow and reject duplicate mapping keys."""

from __future__ import annotations

from pathlib import Path
from typing import Any

try:
    import yaml
except ModuleNotFoundError as exc:  # pragma: no cover - exercised by CI setup
    raise SystemExit(
        "Workflow validation dependency is missing; install "
        "requirements-validation.txt"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]


def _mapping_errors(node: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(node, yaml.MappingNode):
        seen: set[str] = set()
        for key_node, value_node in node.value:
            key = str(getattr(key_node, "value", "<complex-key>"))
            if key in seen:
                errors.append(f"{path}: duplicate mapping key: {key}")
            seen.add(key)
            errors.extend(_mapping_errors(value_node, f"{path}/{key}"))
    elif isinstance(node, yaml.SequenceNode):
        for index, child in enumerate(node.value):
            errors.extend(_mapping_errors(child, f"{path}/{index}"))
    return errors


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    paths = sorted((root / ".github" / "workflows").glob("*.yml"))
    paths.extend(sorted((root / ".github" / "workflows").glob("*.yaml")))
    if not paths:
        return ["no GitHub Actions workflows found"]
    for path in paths:
        relative = path.relative_to(root)
        try:
            node = yaml.compose(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            errors.append(f"{relative}: YAML parse failed: {exc}")
            continue
        if not isinstance(node, yaml.MappingNode):
            errors.append(f"{relative}: workflow root must be a mapping")
            continue
        root_keys = {str(key.value) for key, _ in node.value}
        for required in ("name", "on", "jobs"):
            if required not in root_keys:
                errors.append(f"{relative}: workflow root lacks {required}")
        errors.extend(f"{relative}: {item}" for item in _mapping_errors(node))
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("GitHub Actions workflow validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("GitHub Actions workflow validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
