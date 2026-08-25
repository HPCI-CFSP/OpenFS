#!/usr/bin/env python3
"""Create an immutable Handoff for one agent Work Item branch."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import (
    atomic_write_json,
    isoformat,
    read_json,
    run_snapshot_path,
    sha256_file,
    stable_digest,
)


ROOT = Path(__file__).resolve().parents[1]


def _agent(registry: dict[str, Any], agent_id: str) -> dict[str, Any]:
    matches = [item for item in registry.get("agents", []) if item.get("agent_id") == agent_id]
    if len(matches) != 1:
        raise ValueError(f"agent is not registered exactly once: {agent_id}")
    return matches[0]


def create_handoff(
    root: Path,
    *,
    run_id: str,
    work_item_id: str,
    agent_id: str,
    resolved_model_version: str | None = None,
    tool_paths: list[Path] | None = None,
    usage: dict[str, Any] | None = None,
    created_at: str | None = None,
    allow_disabled_pilot_agent: bool = False,
) -> dict[str, Any]:
    manifest = read_json(root / "runs" / run_id / "manifest.json")
    work_item = read_json(root / "queue" / run_id / f"{work_item_id}.json")
    registry = read_json(run_snapshot_path(root, run_id, "config/agent-registry.json"))
    agent = _agent(registry, agent_id)
    if not agent.get("enabled") and not (
        allow_disabled_pilot_agent and manifest.get("mode") == "pilot"
    ):
        raise RuntimeError(f"agent is disabled: {agent_id}")
    if work_item.get("required_role") != agent.get("role"):
        raise ValueError("agent role does not match the Work Item")
    if work_item.get("status") not in {"queued", "leased"}:
        raise RuntimeError("Handoff requires a queued or leased Work Item")
    lease_owner = work_item.get("lease", {}).get("agent_id")
    if lease_owner and lease_owner != agent_id:
        raise RuntimeError("Work Item is leased by another agent")
    if (
        manifest.get("mode") == "production"
        and agent.get("provider") != "deterministic-local"
        and not resolved_model_version
    ):
        raise ValueError("production Handoff requires a resolved model version")

    output_refs = list(work_item.get("output_paths", []))
    output_digests = {}
    for output_ref in output_refs:
        output_path = root / output_ref
        if not output_path.is_file():
            raise ValueError(f"assigned output is missing: {output_ref}")
        output_digests[output_ref] = sha256_file(output_path)
    tool_names_by_kind = {
        "source-discovery": "register_source.py",
        "evidence-extraction": "extract_evidence.py",
        "synthesis": "propose_claim.py",
        "validation": "create_assessment.py",
        "consensus": "consensus_gate.py",
        "apply-directive": "apply_directive.py",
    }
    default_tools = [Path(__file__)]
    kind_tool = tool_names_by_kind.get(work_item.get("kind"))
    if kind_tool:
        default_tools.append(root / "tools" / kind_tool)
    tools = sorted(set(default_tools + (tool_paths or [])))
    tool_versions = {
        (
            str(path.relative_to(root))
            if path.is_relative_to(root)
            else path.name
        ): sha256_file(path)
        for path in tools
        if path.is_file()
    }
    execution = {
        "model_provider": agent["provider"],
        "model_id": agent["model_family"],
        "prompt_hash": stable_digest(agent["prompt_profile"]),
        "tool_versions": tool_versions,
    }
    if resolved_model_version:
        execution["resolved_model_version"] = resolved_model_version
    identity = {
        "run_id": run_id,
        "work_item_id": work_item_id,
        "agent_id": agent_id,
        "attempt": (
            int(work_item.get("attempt", 0))
            if work_item.get("status") == "leased"
            else int(work_item.get("attempt", 0)) + 1
        ),
        "work_item_idempotency_key": work_item["idempotency_key"],
        "output_digests": output_digests,
    }
    handoff = {
        "schema_version": "0.1.0",
        "handoff_id": f"HANDOFF-{stable_digest(identity)[:16].upper()}",
        **identity,
        "base_commit": manifest["base_commit"],
        "output_refs": output_refs,
        "worker_execution": execution,
        "created_at": created_at or isoformat(),
        "status": "submitted",
    }
    if usage is not None:
        handoff["usage"] = usage
    return handoff


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--work-item-id", required=True)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--resolved-model-version")
    parser.add_argument("--tool-path", action="append", type=Path)
    parser.add_argument("--input-tokens", type=int)
    parser.add_argument("--output-tokens", type=int)
    parser.add_argument("--cost-usd", type=float)
    parser.add_argument("--usage-note")
    parser.add_argument("--created-at")
    parser.add_argument("--allow-disabled-pilot-agent", action="store_true")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    usage_values = {
        "input_tokens": args.input_tokens,
        "output_tokens": args.output_tokens,
        "cost_usd": args.cost_usd,
    }
    if args.usage_note:
        usage_values["measurement_note"] = args.usage_note
    usage = usage_values if any(value is not None for value in usage_values.values()) else None
    tool_paths = [
        path if path.is_absolute() else args.root / path
        for path in (args.tool_path or [])
    ]
    handoff = create_handoff(
        args.root,
        run_id=args.run_id,
        work_item_id=args.work_item_id,
        agent_id=args.agent_id,
        resolved_model_version=args.resolved_model_version,
        tool_paths=tool_paths,
        usage=usage,
        created_at=args.created_at,
        allow_disabled_pilot_agent=args.allow_disabled_pilot_agent,
    )
    output = args.root / "handoffs" / args.run_id / f"{args.work_item_id}.json"
    if output.exists():
        if read_json(output) != handoff:
            raise RuntimeError("Handoff already exists with different content")
    else:
        atomic_write_json(output, handoff)
    print(json.dumps({"handoff_id": handoff["handoff_id"], "output": str(output.relative_to(args.root))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
