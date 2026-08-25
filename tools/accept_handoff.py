#!/usr/bin/env python3
"""Accept a merged agent Handoff into trusted Run control state."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from openfs_runtime import isoformat, read_json, run_snapshot_path, sha256_file, stable_digest
from run_controller import _record_agent_execution, _run_control


ROOT = Path(__file__).resolve().parents[1]
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def _validate_usage(usage: dict[str, Any] | None) -> None:
    if usage is None:
        return
    allowed = {"input_tokens", "output_tokens", "cost_usd", "measurement_note"}
    if set(usage) - allowed:
        raise ValueError("Handoff usage contains unknown fields")
    for field in ("input_tokens", "output_tokens"):
        value = usage.get(field)
        if value is not None and (not isinstance(value, int) or value < 0):
            raise ValueError(f"invalid Handoff usage: {field}")
    cost = usage.get("cost_usd")
    if cost is not None and (
        not isinstance(cost, (int, float)) or isinstance(cost, bool) or cost < 0
    ):
        raise ValueError("invalid Handoff usage: cost_usd")


def _accept_unlocked(
    root: Path,
    *,
    run_id: str,
    handoff: dict[str, Any],
    handoff_ref: str,
    allow_disabled_pilot_agent: bool,
    now: str | None,
) -> dict[str, Any]:
    manifest = read_json(root / "runs" / run_id / "manifest.json")
    work_item_id = handoff["work_item_id"]
    work_path = root / "queue" / run_id / f"{work_item_id}.json"
    work_item = read_json(work_path)
    if work_item.get("status") == "completed":
        if work_item.get("handoff_ref") == handoff_ref:
            return work_item
        raise RuntimeError("Work Item was already completed through another path")
    if work_item.get("status") not in {"queued", "leased"}:
        raise RuntimeError("Handoff cannot complete the current Work Item state")
    if handoff.get("run_id") != run_id:
        raise ValueError("Handoff Run ID mismatch")
    if handoff.get("work_item_idempotency_key") != work_item.get("idempotency_key"):
        raise ValueError("Handoff Work Item identity mismatch")
    expected_attempt = (
        int(work_item.get("attempt", 0))
        if work_item.get("status") == "leased"
        else int(work_item.get("attempt", 0)) + 1
    )
    if handoff.get("attempt") != expected_attempt:
        raise ValueError("Handoff attempt differs from the next Work Item attempt")
    if handoff.get("base_commit") != manifest.get("base_commit"):
        raise ValueError("Handoff base commit differs from the pinned Run base")

    registry = read_json(run_snapshot_path(root, run_id, "config/agent-registry.json"))
    agents = [
        item for item in registry.get("agents", [])
        if item.get("agent_id") == handoff.get("agent_id")
    ]
    if len(agents) != 1:
        raise ValueError("Handoff agent is not registered exactly once")
    agent = agents[0]
    if not agent.get("enabled") and not (
        allow_disabled_pilot_agent and manifest.get("mode") == "pilot"
    ):
        raise RuntimeError("Handoff agent is disabled")
    if agent.get("role") != work_item.get("required_role"):
        raise ValueError("Handoff agent role does not match the Work Item")
    lease_owner = work_item.get("lease", {}).get("agent_id")
    if lease_owner and lease_owner != agent["agent_id"]:
        raise RuntimeError("Work Item is leased by another agent")

    output_refs = handoff.get("output_refs", [])
    if set(output_refs) != set(work_item.get("output_paths", [])):
        raise ValueError("Handoff outputs do not exactly match assigned output paths")
    for output_ref in output_refs:
        output_path = root / output_ref
        if not output_path.is_file():
            raise ValueError(f"merged Handoff output is missing: {output_ref}")
        if sha256_file(output_path) != handoff.get("output_digests", {}).get(output_ref):
            raise ValueError(f"merged Handoff output digest mismatch: {output_ref}")
        output = read_json(output_path)
        if output.get("run_id", run_id) != run_id:
            raise ValueError(f"merged output Run ID mismatch: {output_ref}")
        if output.get("work_item_id", work_item_id) != work_item_id:
            raise ValueError(f"merged output Work Item ID mismatch: {output_ref}")

    execution = handoff.get("worker_execution", {})
    expected_execution = {
        "model_provider": agent["provider"],
        "model_id": agent["model_family"],
        "prompt_hash": stable_digest(agent["prompt_profile"]),
    }
    for key, value in expected_execution.items():
        if execution.get(key) != value:
            raise ValueError(f"Handoff worker identity mismatch: {key}")
    tool_versions = execution.get("tool_versions", {})
    if not tool_versions:
        raise ValueError("Handoff must identify at least one worker tool")
    for digest in tool_versions.values():
        if not isinstance(digest, str) or not SHA256.fullmatch(digest):
            raise ValueError("Handoff contains an invalid tool digest")
    if (
        manifest.get("mode") == "production"
        and agent.get("provider") != "deterministic-local"
        and not execution.get("resolved_model_version")
    ):
        raise ValueError("production Handoff lacks a resolved model version")
    _validate_usage(handoff.get("usage"))

    timestamp = now or isoformat()
    work_item["status"] = "completed"
    work_item["attempt"] = expected_attempt
    work_item["output_refs"] = output_refs
    work_item["output_digests"] = handoff["output_digests"]
    work_item["completed_by_agent_id"] = agent["agent_id"]
    work_item["completion_mode"] = "merged-handoff"
    work_item["handoff_ref"] = handoff_ref
    work_item["completed_at"] = timestamp
    work_item["updated_at"] = timestamp
    if "usage" in handoff:
        work_item["usage"] = handoff["usage"]
    work_item.pop("lease", None)
    from openfs_runtime import atomic_write_json

    atomic_write_json(work_path, work_item)
    _record_agent_execution(
        root,
        run_id=run_id,
        work_item=work_item,
        agent=agent,
        executed_at=handoff["created_at"],
        declared_execution=execution,
    )
    return work_item


def accept_handoff(
    root: Path,
    *,
    handoff_ref: str,
    allow_disabled_pilot_agent: bool = False,
    now: str | None = None,
) -> dict[str, Any]:
    handoff = read_json(root / handoff_ref)
    return _run_control(
        root,
        handoff["run_id"],
        _accept_unlocked,
        handoff=handoff,
        handoff_ref=handoff_ref,
        allow_disabled_pilot_agent=allow_disabled_pilot_agent,
        now=now,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--handoff-ref", required=True)
    parser.add_argument("--allow-disabled-pilot-agent", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    item = accept_handoff(
        args.root,
        handoff_ref=args.handoff_ref,
        allow_disabled_pilot_agent=args.allow_disabled_pilot_agent,
    )
    print(json.dumps({"work_item_id": item["work_item_id"], "status": item["status"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
