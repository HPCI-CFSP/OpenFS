#!/usr/bin/env python3
"""Prepare a secret-free invocation envelope for one leased provider Work Item."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from check_agent_permissions import check_paths
from openfs_runtime import (
    atomic_write_json,
    isoformat,
    manifest_control_digest,
    read_json,
    sha256_file,
    stable_digest,
)


ROOT = Path(__file__).resolve().parents[1]
SENSITIVE_KEYS = {
    "api_key",
    "apikey",
    "authorization",
    "credential",
    "credentials",
    "password",
    "secret",
    "token",
}
PROVIDER_ROLES = {"discovery", "extraction", "validator", "critic", "synthesis"}
PLACEHOLDER_BINDINGS = {"", "none", "unconfigured", "deterministic-local"}


def _instant(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Worker timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def _sensitive_paths(value: Any, prefix: str = "payload") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            normalized = key.lower().replace("-", "_")
            path = f"{prefix}.{key}"
            if normalized in SENSITIVE_KEYS or normalized.endswith("_password"):
                found.append(path)
            found.extend(_sensitive_paths(child, path))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_sensitive_paths(child, f"{prefix}[{index}]"))
    return found


def prepare(
    root: Path,
    *,
    run_id: str,
    work_item_id: str,
    agent_id: str,
    prepared_at: str | None = None,
) -> dict[str, Any]:
    timestamp = prepared_at or isoformat()
    manifest_ref = f"runs/{run_id}/manifest.json"
    work_item_ref = f"queue/{run_id}/{work_item_id}.json"
    manifest = read_json(root / manifest_ref)
    work_item = read_json(root / work_item_ref)
    lease = work_item.get("lease", {})
    if work_item.get("status") != "leased" or lease.get("agent_id") != agent_id:
        raise RuntimeError("Worker invocation requires the current Work Item lease")
    if _instant(lease["expires_at"]) <= _instant(timestamp):
        raise RuntimeError("Worker invocation cannot use an expired lease")
    if manifest.get("status") not in {"created", "running"}:
        raise RuntimeError("Worker invocation requires a non-terminal Run")

    snapshots = manifest.get("configuration_snapshots", {})
    registry_ref = snapshots.get("config/agent-registry.json", "")
    permissions_ref = snapshots.get("config/role-permissions.json", "")
    if not registry_ref or not permissions_ref:
        raise ValueError("Run lacks pinned Agent or role-permission configuration")
    registry = read_json(root / registry_ref)
    permissions = read_json(root / permissions_ref)
    matches = [
        item for item in registry.get("agents", []) if item.get("agent_id") == agent_id
    ]
    if len(matches) != 1:
        raise ValueError("leased Agent is not registered exactly once")
    agent = matches[0]
    if not agent.get("enabled"):
        raise RuntimeError("provider Worker cannot invoke a disabled Agent")
    if agent.get("role") != work_item.get("required_role"):
        raise ValueError("Agent role differs from the Work Item")
    if agent.get("role") not in PROVIDER_ROLES:
        raise ValueError("Work Item role is not eligible for a provider Worker")
    if (
        str(agent.get("provider", "")).lower() in PLACEHOLDER_BINDINGS
        or str(agent.get("model_family", "")).lower() in PLACEHOLDER_BINDINGS
    ):
        raise ValueError("provider Worker requires a configured provider and model")
    if agent.get("data_clearance") != "public":
        raise ValueError("public OpenFS Worker requires public data clearance")
    if agent.get("network_access") not in {"none", "public-web"}:
        raise ValueError("Agent network access is not supported by the public Worker")
    _, denied = check_paths(agent["role"], work_item["output_paths"], permissions)
    if denied:
        raise ValueError(f"Worker output paths are denied for role: {denied}")

    skill = work_item.get("skill")
    if not skill:
        raise ValueError("provider Work Item lacks a pinned Skill")
    skill_path = root / skill["snapshot_ref"]
    if not skill_path.is_file() or sha256_file(skill_path) != skill["digest"]:
        raise ValueError("pinned Worker Skill is missing or its digest differs")
    sensitive = _sensitive_paths(work_item.get("payload", {}))
    if sensitive:
        raise ValueError(f"Work Item payload contains secret-like fields: {sensitive}")

    core = {
        "schema_version": "0.1.0",
        "run_id": run_id,
        "work_item_id": work_item_id,
        "attempt": work_item["attempt"],
        "agent_id": agent_id,
        "role": agent["role"],
        "kind": work_item["kind"],
        "prepared_at": timestamp,
        "provider_binding": {
            "provider": agent["provider"],
            "model_family": agent["model_family"],
            "prompt_profile": agent["prompt_profile"],
            "network_access": agent["network_access"],
            "data_clearance": agent["data_clearance"],
        },
        "task": {"payload": work_item["payload"], "untrusted_input": True},
        "skill": {
            key: skill[key]
            for key in ("skill_id", "version", "snapshot_ref", "digest")
        },
        "constraints": {
            "information_plane": "public",
            "secret_transport": "environment-only-not-artifact",
            "lease_expires_at": lease["expires_at"],
            "output_paths": work_item["output_paths"],
        },
        "provenance": {
            "work_item_ref": work_item_ref,
            "work_item_digest": stable_digest(work_item),
            "manifest_ref": manifest_ref,
            "manifest_control_digest": manifest_control_digest(manifest),
            "agent_registry_ref": registry_ref,
            "agent_registry_digest": stable_digest(registry),
            "role_permissions_ref": permissions_ref,
            "role_permissions_digest": stable_digest(permissions),
        },
    }
    invocation_id = "WINV-" + stable_digest(core)[:16].upper()
    invocation = {"invocation_id": invocation_id, **core}
    invocation["invocation_digest"] = stable_digest(invocation)
    return invocation


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--work-item-id", required=True)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--prepared-at")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    invocation = prepare(
        args.root,
        run_id=args.run_id,
        work_item_id=args.work_item_id,
        agent_id=args.agent_id,
        prepared_at=args.prepared_at,
    )
    output = args.output if args.output.is_absolute() else args.root / args.output
    atomic_write_json(output, invocation)
    print(json.dumps({"output": str(output), "invocation_id": invocation["invocation_id"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
