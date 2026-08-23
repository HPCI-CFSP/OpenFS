#!/usr/bin/env python3
"""Check planned OpenFS write paths against default-deny role permissions."""

from __future__ import annotations

import argparse
import fnmatch
import json
from pathlib import Path, PurePosixPath
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "role-permissions.json"


def load_config(path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_repository_path(raw_path: str) -> str:
    normalized = raw_path.replace("\\", "/").removeprefix("./")
    path = PurePosixPath(normalized)
    if (
        not normalized
        or path.is_absolute()
        or ".." in path.parts
        or any(ord(character) < 32 for character in normalized)
    ):
        raise ValueError(f"Path must be repository-relative without traversal: {raw_path}")
    return path.as_posix()


def check_paths(
    role: str,
    paths: list[str],
    config: dict[str, Any],
    *,
    human_authorized: bool = False,
) -> tuple[list[str], list[str]]:
    role_config = config.get("roles", {}).get(role)
    if role_config is None:
        return [], [f"unknown role: {role}"]
    if role_config.get("interactive_human_authorization_required") and not human_authorized:
        return [], [f"role requires explicit interactive human authorization: {role}"]

    patterns = role_config.get("allowed_write_patterns", [])
    allowed: list[str] = []
    denied: list[str] = []
    for raw_path in paths:
        try:
            path = normalize_repository_path(raw_path)
        except ValueError as exc:
            denied.append(str(exc))
            continue
        if any(fnmatch.fnmatchcase(path, pattern) for pattern in patterns):
            allowed.append(path)
        else:
            denied.append(path)
    return allowed, denied


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", required=True)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--human-authorized", action="store_true")
    parser.add_argument("paths", nargs="+")
    args = parser.parse_args()

    allowed, denied = check_paths(
        args.role,
        args.paths,
        load_config(args.config),
        human_authorized=args.human_authorized,
    )
    for path in allowed:
        print(f"ALLOW {path}")
    for path in denied:
        print(f"DENY  {path}")
    return 1 if denied else 0


if __name__ == "__main__":
    raise SystemExit(main())
