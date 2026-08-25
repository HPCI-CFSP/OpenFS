#!/usr/bin/env python3
"""Enforce registered role permissions for OpenFS agent pull-request branches."""

from __future__ import annotations

import json
import os
import hashlib
import re
import subprocess
from pathlib import Path
from typing import Any

from check_agent_permissions import check_paths, load_config
from openfs_runtime import stable_digest


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = re.compile(r"^RUN-[A-Z0-9][A-Z0-9-]{2,63}$")
WORK_ITEM_ID = re.compile(r"^WORK-[0-9]{6}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def parse_agent_branch(branch: str) -> tuple[str, str, str] | None:
    parts = branch.split("/")
    if (
        len(parts) == 4
        and parts[0] == "agent"
        and parts[1]
        and RUN_ID.fullmatch(parts[2])
        and WORK_ITEM_ID.fullmatch(parts[3])
    ):
        return parts[1], parts[2], parts[3]
    return None


def parse_agent_id(branch: str) -> str | None:
    parsed = parse_agent_branch(branch)
    return parsed[0] if parsed else None


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


def validate_branch_paths(
    root: Path,
    *,
    branch: str,
    paths: list[str],
    registry: dict[str, Any],
    permissions: dict[str, Any],
) -> tuple[list[str], list[str]]:
    parsed = parse_agent_branch(branch)
    if parsed is None:
        return [], [f"invalid agent branch name: {branch}"]
    agent_id, run_id, work_item_id = parsed
    agent = registry.get(agent_id)
    if agent is None:
        return [], [f"agent is not registered: {agent_id}"]
    work_path = root / "queue" / run_id / f"{work_item_id}.json"
    if not work_path.is_file():
        return [], [f"assigned Work Item is absent from trusted base: {work_path.relative_to(root)}"]
    work_item = json.loads(work_path.read_text(encoding="utf-8"))
    manifest_path = root / "runs" / run_id / "manifest.json"
    if not manifest_path.is_file():
        return [], [f"Run manifest is absent from trusted base: {manifest_path.relative_to(root)}"]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if agent.get("enabled") is not True and manifest.get("mode") != "pilot":
        return [], [f"agent is disabled outside Pilot mode: {agent_id}"]
    if work_item.get("run_id") != run_id or work_item.get("work_item_id") != work_item_id:
        return [], ["Work Item identity differs from the agent branch"]
    if work_item.get("required_role") != agent.get("role"):
        return [], [
            f"Work Item requires role {work_item.get('required_role')}, not {agent.get('role')}"
        ]
    handoff_ref = f"handoffs/{run_id}/{work_item_id}.json"
    expected = set(work_item.get("output_paths", [])) | {handoff_ref}
    observed = set(paths)
    errors = []
    if observed != expected:
        for path in sorted(expected - observed):
            errors.append(f"missing assigned path: {path}")
        for path in sorted(observed - expected):
            errors.append(f"path is outside branch assignment: {path}")
    _, denied = check_paths(agent["role"], sorted(observed), permissions)
    errors.extend(f"role path denied: {item}" for item in denied)
    return sorted(observed - set(denied)) if not errors else [], errors


def _git_blob(head_sha: str, path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{head_sha}:{path}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return result.stdout


def validate_handoff_at_head(
    root: Path,
    *,
    branch: str,
    head_sha: str,
) -> list[str]:
    parsed = parse_agent_branch(branch)
    if parsed is None:
        return [f"invalid agent branch name: {branch}"]
    agent_id, run_id, work_item_id = parsed
    work_item = json.loads(
        (root / "queue" / run_id / f"{work_item_id}.json").read_text(encoding="utf-8")
    )
    manifest = json.loads(
        (root / "runs" / run_id / "manifest.json").read_text(encoding="utf-8")
    )
    handoff_ref = f"handoffs/{run_id}/{work_item_id}.json"
    try:
        handoff = json.loads(_git_blob(head_sha, handoff_ref))
    except (subprocess.CalledProcessError, json.JSONDecodeError) as exc:
        return [f"invalid Handoff at {handoff_ref}: {exc}"]
    errors = []
    expected_identity = {
        "run_id": run_id,
        "work_item_id": work_item_id,
        "agent_id": agent_id,
        "attempt": (
            int(work_item.get("attempt", 0))
            if work_item.get("status") == "leased"
            else int(work_item.get("attempt", 0)) + 1
        ),
        "work_item_idempotency_key": work_item["idempotency_key"],
    }
    for key, value in expected_identity.items():
        if handoff.get(key) != value:
            errors.append(f"Handoff {key} does not match the assigned Work Item")
    if handoff.get("base_commit") != manifest.get("base_commit"):
        errors.append("Handoff base commit differs from the pinned Run base")
    if handoff.get("status") != "submitted":
        errors.append("Handoff status must be submitted")
    if set(handoff.get("output_refs", [])) != set(work_item.get("output_paths", [])):
        errors.append("Handoff outputs do not exactly match assigned output paths")
    digests = handoff.get("output_digests", {})
    if set(digests) != set(work_item.get("output_paths", [])):
        errors.append("Handoff digest keys do not exactly match assigned outputs")
    for output_ref in work_item.get("output_paths", []):
        try:
            digest = hashlib.sha256(_git_blob(head_sha, output_ref)).hexdigest()
        except subprocess.CalledProcessError:
            errors.append(f"assigned output is absent from branch: {output_ref}")
            continue
        if digests.get(output_ref) != digest:
            errors.append(f"Handoff digest mismatch: {output_ref}")
    manifest_registry_ref = manifest.get("configuration_snapshots", {}).get(
        "config/agent-registry.json", "config/agent-registry.json"
    )
    registry = json.loads((root / manifest_registry_ref).read_text(encoding="utf-8"))
    agents = [item for item in registry.get("agents", []) if item.get("agent_id") == agent_id]
    if len(agents) != 1:
        errors.append("Handoff agent does not resolve once in the pinned registry")
    else:
        agent = agents[0]
        execution = handoff.get("worker_execution", {})
        expected_execution = {
            "model_provider": agent.get("provider"),
            "model_id": agent.get("model_family"),
            "prompt_hash": stable_digest(agent.get("prompt_profile")),
        }
        for key, value in expected_execution.items():
            if execution.get(key) != value:
                errors.append(f"Handoff worker identity mismatch: {key}")
        tool_versions = execution.get("tool_versions", {})
        if not tool_versions:
            errors.append("Handoff must identify at least one worker tool")
        elif any(
            not isinstance(digest, str) or not SHA256.fullmatch(digest)
            for digest in tool_versions.values()
        ):
            errors.append("Handoff contains an invalid tool digest")
        if (
            manifest.get("mode") == "production"
            and agent.get("provider") != "deterministic-local"
            and not execution.get("resolved_model_version")
        ):
            errors.append("production Handoff lacks a resolved model version")
    return errors


def main() -> int:
    branch = os.environ.get("OPENFS_HEAD_REF", "")
    if not branch.startswith("agent/"):
        print("Non-agent branch: role path enforcement skipped.")
        return 0

    base_sha = os.environ.get("OPENFS_BASE_SHA")
    head_sha = os.environ.get("OPENFS_HEAD_SHA")
    if not base_sha or not head_sha:
        print("Missing pull-request base or head SHA.")
        return 1

    paths = changed_paths(base_sha, head_sha)
    allowed, denied = validate_branch_paths(
        ROOT,
        branch=branch,
        paths=paths,
        registry=load_agent_registry(),
        permissions=load_config(),
    )
    if not denied:
        denied.extend(
            validate_handoff_at_head(ROOT, branch=branch, head_sha=head_sha)
        )
    for path in allowed:
        print(f"ALLOW {path}")
    for path in denied:
        print(f"DENY  {path}")
    return 1 if denied else 0


if __name__ == "__main__":
    raise SystemExit(main())
