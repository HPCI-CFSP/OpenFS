#!/usr/bin/env python3
"""Enforce registered role permissions for OpenFS agent pull-request branches."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any

from check_agent_permissions import check_paths, load_config


ROOT = Path(__file__).resolve().parents[1]


def parse_agent_id(branch: str) -> str | None:
    parts = branch.split("/")
    if len(parts) == 4 and parts[0] == "agent" and all(parts[1:]):
        return parts[1]
    return None


def load_agent_registry(path: Path = ROOT / "config" / "agent-registry.json") -> dict[str, Any]:
    registry = json.loads(path.read_text(encoding="utf-8"))
    return {agent["agent_id"]: agent for agent in registry.get("agents", [])}


def changed_paths(base_sha: str, head_sha: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "-z", "--no-renames", base_sha, head_sha],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return [
        path.decode("utf-8", errors="surrogateescape")
        for path in result.stdout.split(b"\0")
        if path
    ]


def main() -> int:
    branch = os.environ.get("OPENFS_HEAD_REF", "")
    if not branch.startswith("agent/"):
        print("Non-agent branch: role path enforcement skipped.")
        return 0

    agent_id = parse_agent_id(branch)
    if agent_id is None:
        print(f"Invalid agent branch name: {branch}")
        return 1

    agent = load_agent_registry().get(agent_id)
    if agent is None:
        print(f"Agent is not registered: {agent_id}")
        return 1
    if agent.get("enabled") is not True:
        print(f"Agent is disabled: {agent_id}")
        return 1

    base_sha = os.environ.get("OPENFS_BASE_SHA")
    head_sha = os.environ.get("OPENFS_HEAD_SHA")
    if not base_sha or not head_sha:
        print("Missing pull-request base or head SHA.")
        return 1

    paths = changed_paths(base_sha, head_sha)
    allowed, denied = check_paths(agent["role"], paths, load_config())
    for path in allowed:
        print(f"ALLOW {agent['role']} {path}")
    for path in denied:
        print(f"DENY  {agent['role']} {path}")
    return 1 if denied else 0


if __name__ == "__main__":
    raise SystemExit(main())
