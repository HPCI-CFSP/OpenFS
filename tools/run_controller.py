#!/usr/bin/env python3
"""Create and operate idempotent OpenFS Runs and leased Work Items."""

from __future__ import annotations

import argparse
import json
import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path, PurePosixPath
from typing import Any

from openfs_runtime import (
    atomic_write_json,
    git_head,
    isoformat,
    read_json,
    sha256_file,
    stable_digest,
    utc_now,
)


ROOT = Path(__file__).resolve().parents[1]
RUN_ID = re.compile(r"^RUN-[A-Z0-9][A-Z0-9-]{2,63}$")


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _load_required(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    if not path.is_file():
        raise ValueError(f"required configuration is missing: {relative}")
    return read_json(path)


def _monitor_path(root: Path, monitor_id: str) -> Path:
    matches = [
        path
        for path in sorted((root / "config" / "monitors").glob("*.json"))
        if read_json(path).get("monitor_id") == monitor_id
    ]
    if len(matches) != 1:
        raise ValueError(f"monitor must resolve to exactly one configuration: {monitor_id}")
    return matches[0]


def _policy_hashes(root: Path, monitor_path: Path) -> dict[str, str]:
    paths = [
        root / "config" / "acquisition-policy.json",
        root / "config" / "agent-registry.json",
        root / "config" / "autonomy-policy.json",
        root / "config" / "budgets.json",
        root / "config" / "consensus-policy.json",
        root / "config" / "role-permissions.json",
        root / "config" / "source-registry.json",
        monitor_path,
    ]
    return {
        path.relative_to(root).as_posix(): stable_digest(read_json(path))
        for path in paths
    }


def _configuration_snapshot_refs(
    run_id: str, policy_hashes: dict[str, str]
) -> dict[str, str]:
    return {
        source: f"runs/{run_id}/inputs/{source}"
        for source in sorted(policy_hashes)
    }


def _approved_directives(root: Path, task_id: str) -> list[dict[str, Any]]:
    directives: list[dict[str, Any]] = []
    for path in sorted((root / "reviews" / "directives").glob("DIR-*.json")):
        directive = read_json(path)
        if directive.get("directive_type") != "research-instruction":
            continue
        if directive.get("status") not in {"approved", "scheduled"}:
            continue
        scope = directive.get("scope", [])
        if scope and task_id not in scope:
            continue
        directives.append(directive)
    return directives


def _work_item(
    *,
    sequence: int,
    run_id: str,
    task_id: str,
    monitor_id: str,
    kind: str,
    role: str,
    payload: dict[str, Any],
    output_paths: list[str],
    maximum_attempts: int,
    created_at: str,
) -> dict[str, Any]:
    identity = {
        "run_id": run_id,
        "task_id": task_id,
        "monitor_id": monitor_id,
        "kind": kind,
        "payload": payload,
    }
    return {
        "schema_version": "0.1.0",
        "work_item_id": f"WORK-{sequence:06d}",
        "run_id": run_id,
        "task_id": task_id,
        "monitor_id": monitor_id,
        "kind": kind,
        "required_role": role,
        "status": "queued",
        "idempotency_key": stable_digest(identity),
        "payload": payload,
        "output_paths": output_paths,
        "attempt": 0,
        "maximum_attempts": maximum_attempts,
        "created_at": created_at,
        "updated_at": created_at,
    }


def create_run(
    root: Path,
    *,
    run_id: str,
    task_id: str,
    monitor_id: str,
    pilot: bool = False,
    now: datetime | None = None,
    maximum_work_items: int | None = None,
) -> dict[str, Any]:
    if not RUN_ID.fullmatch(run_id):
        raise ValueError(f"invalid Run ID: {run_id}")
    budgets = _load_required(root, "config/budgets.json")
    kill_switch = budgets.get("kill_switch", {})
    if kill_switch.get("enabled") and (root / kill_switch.get("control_path", "state/STOP")).exists():
        raise RuntimeError("OpenFS kill switch is active")

    monitor_path = _monitor_path(root, monitor_id)
    monitor = read_json(monitor_path)
    if monitor.get("task_id") != task_id:
        raise ValueError(f"monitor {monitor_id} does not belong to task {task_id}")
    if not monitor.get("enabled") and not pilot:
        raise RuntimeError(f"monitor is disabled: {monitor_id}")

    defaults = budgets.get("defaults", {})
    configured_limit = int(defaults.get("maximum_work_items", 0))
    requested_limit = maximum_work_items or configured_limit
    if requested_limit < 1 or requested_limit > configured_limit:
        raise ValueError(
            f"maximum_work_items must be between 1 and configured limit {configured_limit}"
        )

    run_path = root / "runs" / run_id / "manifest.json"
    queue_path = root / "queue" / run_id
    created = now or utc_now()
    created_at = isoformat(created)
    directives = _approved_directives(root, task_id)
    maximum_attempts = int(defaults.get("maximum_retries_per_work_item", 0)) + 1

    work_items: list[dict[str, Any]] = []
    slots_per_query = int(monitor.get("discovery_slots_per_query", 1))
    query_plan = [
        (query, "coverage") for query in monitor.get("query_families", [])
    ] + [
        (query, "falsification") for query in monitor.get("falsification_queries", [])
    ]
    for query, query_role in query_plan:
        for candidate_slot in range(1, slots_per_query + 1):
            sequence = len(work_items) + 1
            work_items.append(
                _work_item(
                    sequence=sequence,
                    run_id=run_id,
                    task_id=task_id,
                    monitor_id=monitor_id,
                    kind="source-discovery",
                    role="discovery",
                    payload={
                        "query": query,
                        "query_role": query_role,
                        "candidate_slot": candidate_slot,
                        "languages": monitor.get("languages", []),
                        "source_classes": monitor.get("source_classes", []),
                        "source_class_requirements": monitor.get(
                            "source_class_requirements", []
                        ),
                        "maximum_unchecked_days": monitor.get("maximum_unchecked_days"),
                    },
                    output_paths=[f"proposals/sources/{run_id}/WORK-{sequence:06d}.json"],
                    maximum_attempts=maximum_attempts,
                    created_at=created_at,
                )
            )
    for directive in directives:
        sequence = len(work_items) + 1
        work_items.append(
            _work_item(
                sequence=sequence,
                run_id=run_id,
                task_id=task_id,
                monitor_id=monitor_id,
                kind="apply-directive",
                role="orchestrator",
                payload={
                    "directive_id": directive["directive_id"],
                    "instruction_digest": stable_digest(directive["instruction"]),
                },
                output_paths=[f"runs/{run_id}/directives/{directive['directive_id']}.json"],
                maximum_attempts=maximum_attempts,
                created_at=created_at,
            )
        )
    if len(work_items) > requested_limit:
        raise RuntimeError(
            f"Run requires {len(work_items)} Work Items but limit is {requested_limit}"
        )

    policy_hashes = _policy_hashes(root, monitor_path)
    snapshot_refs = _configuration_snapshot_refs(run_id, policy_hashes)
    manifest = {
        "schema_version": "0.1.0",
        "run_id": run_id,
        "task_id": task_id,
        "monitor_id": monitor_id,
        "mode": "pilot" if pilot else "production",
        "base_commit": git_head(root),
        "started_at": created_at,
        "status": "created",
        "research_status": "not-evaluated",
        "policy_hashes": policy_hashes,
        "configuration_snapshots": snapshot_refs,
        "budget": {
            "maximum_run_minutes": defaults.get("maximum_run_minutes"),
            "maximum_work_items": requested_limit,
            "maximum_retries_per_work_item": defaults.get("maximum_retries_per_work_item"),
            "maximum_parallel_agents": defaults.get("maximum_parallel_agents"),
            "maximum_sources_per_monitor": defaults.get("maximum_sources_per_monitor"),
            "maximum_cost_usd": defaults.get("maximum_cost_usd"),
        },
        "directive_ids": [directive["directive_id"] for directive in directives],
        "work_item_ids": [item["work_item_id"] for item in work_items],
        "agent_executions": [],
        "query_receipts": [],
        "expansion_events": [],
        "cost": {
            "currency": "USD",
            "measurement_status": "unreported",
            "reported_total_usd": None,
            "reported_executions": 0,
            "unreported_executions": 0,
        },
        "metrics": {"work_items_total": len(work_items)},
    }
    run_identity = {
        key: manifest[key]
        for key in ("run_id", "task_id", "monitor_id", "mode", "policy_hashes", "directive_ids")
    }
    run_identity["work_item_idempotency_keys"] = [
        item["idempotency_key"] for item in work_items
    ]
    manifest["run_identity_hash"] = stable_digest(run_identity)

    if run_path.exists():
        existing = read_json(run_path)
        if existing.get("run_identity_hash") != manifest["run_identity_hash"]:
            raise RuntimeError(f"Run ID already exists with different inputs: {run_id}")
        return existing

    queue_path.mkdir(parents=True, exist_ok=True)
    for source_ref, snapshot_ref in snapshot_refs.items():
        atomic_write_json(root / snapshot_ref, read_json(root / source_ref))
    for item in work_items:
        atomic_write_json(queue_path / f"{item['work_item_id']}.json", item)
    atomic_write_json(run_path, manifest)
    return manifest


def _agent(root: Path, agent_id: str, *, run_id: str | None = None) -> dict[str, Any]:
    registry_path = root / "config" / "agent-registry.json"
    if run_id:
        manifest_path = root / "runs" / run_id / "manifest.json"
        if manifest_path.is_file():
            manifest = read_json(manifest_path)
            snapshot_ref = manifest.get("configuration_snapshots", {}).get(
                "config/agent-registry.json"
            )
            if snapshot_ref:
                registry_path = root / snapshot_ref
    registry = read_json(registry_path)
    matches = [item for item in registry.get("agents", []) if item.get("agent_id") == agent_id]
    if len(matches) != 1:
        raise ValueError(f"agent is not registered exactly once: {agent_id}")
    return matches[0]


def _lock_path(root: Path, run_id: str, work_item_id: str) -> Path:
    return root / "state" / "locks" / run_id / f"{work_item_id}.lock"


def _acquire_lock(path: Path) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    return os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)


def _release_lock(path: Path, descriptor: int) -> None:
    os.close(descriptor)
    path.unlink(missing_ok=True)


def _queue_items(root: Path, run_id: str) -> list[tuple[Path, dict[str, Any]]]:
    return [
        (path, read_json(path))
        for path in sorted((root / "queue" / run_id).glob("WORK-*.json"))
    ]


def _usage_summary(items: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [item for item in items if item.get("status") == "completed"]
    cost_values = [
        item.get("usage", {}).get("cost_usd")
        for item in completed
        if item.get("usage", {}).get("cost_usd") is not None
    ]
    reported = len(cost_values)
    if not completed or reported == 0:
        measurement_status = "unreported"
    elif reported == len(completed):
        measurement_status = "complete"
    else:
        measurement_status = "partial"

    def token_total(name: str) -> int | None:
        values = [
            item.get("usage", {}).get(name)
            for item in completed
            if item.get("usage", {}).get(name) is not None
        ]
        return sum(values) if values else None

    return {
        "currency": "USD",
        "measurement_status": measurement_status,
        "reported_total_usd": sum(cost_values) if cost_values else None,
        "reported_executions": reported,
        "unreported_executions": len(completed) - reported,
        "reported_input_tokens": token_total("input_tokens"),
        "reported_output_tokens": token_total("output_tokens"),
    }


def _budget_violation(
    manifest: dict[str, Any],
    items: list[dict[str, Any]],
    current: datetime,
) -> tuple[str, Any, Any] | None:
    budget = manifest.get("budget", {})
    maximum_minutes = budget.get("maximum_run_minutes")
    if maximum_minutes is not None:
        elapsed_seconds = (current - _parse_time(manifest["started_at"])).total_seconds()
        if elapsed_seconds >= float(maximum_minutes) * 60:
            return "maximum-run-minutes", elapsed_seconds / 60, maximum_minutes
    maximum_work_items = budget.get("maximum_work_items")
    if maximum_work_items is not None and len(items) > int(maximum_work_items):
        return "maximum-work-items", len(items), maximum_work_items
    maximum_sources = budget.get("maximum_sources_per_monitor")
    source_items = sum(item.get("kind") == "source-discovery" for item in items)
    if maximum_sources is not None and source_items > int(maximum_sources):
        return "maximum-sources-per-monitor", source_items, maximum_sources
    maximum_cost = budget.get("maximum_cost_usd")
    usage = _usage_summary(items)
    reported_cost = usage["reported_total_usd"]
    if (
        maximum_cost is not None
        and reported_cost is not None
        and reported_cost > float(maximum_cost)
    ):
        return "maximum-cost-usd", reported_cost, maximum_cost
    return None


def _stop_run(
    root: Path,
    *,
    manifest: dict[str, Any],
    reason: str,
    observed: Any,
    limit: Any,
    now: datetime,
) -> dict[str, Any]:
    if manifest.get("status") == "stopped":
        return manifest
    timestamp = isoformat(now)
    counts: dict[str, int] = {}
    items: list[dict[str, Any]] = []
    for path, item in _queue_items(root, manifest["run_id"]):
        if item.get("status") in {"queued", "leased"}:
            item["status"] = "cancelled"
            item["cancellation"] = {
                "reason": reason,
                "recorded_at": timestamp,
            }
            item["updated_at"] = timestamp
            item.pop("lease", None)
            atomic_write_json(path, item)
        counts[item["status"]] = counts.get(item["status"], 0) + 1
        items.append(item)
    manifest["status"] = "stopped"
    manifest["stopped_at"] = timestamp
    manifest["completed_at"] = timestamp
    manifest["stop"] = {
        "reason": reason,
        "observed": observed,
        "limit": limit,
        "requires_owner_action": True,
    }
    manifest["cost"] = _usage_summary(items)
    manifest.setdefault("metrics", {}).update(
        {"work_items_total": len(items), "work_items_by_status": counts}
    )
    manifest_path = root / "runs" / manifest["run_id"] / "manifest.json"
    atomic_write_json(manifest_path, manifest)
    atomic_write_json(
        root
        / "reviews"
        / "exceptions"
        / manifest["run_id"]
        / f"STOP-{reason.upper()}.json",
        {
            "schema_version": "0.1.0",
            "exception_id": f"EXC-{manifest['run_id']}-{reason.upper()}",
            "run_id": manifest["run_id"],
            "status": "open",
            "recorded_at": timestamp,
            "exception_kind": "run-stop",
            "reason": reason,
            "observed": observed,
            "limit": limit,
            "requires_owner_action": True,
        },
    )
    return manifest


def _recover_expired_leases(
    root: Path, run_id: str, current: datetime
) -> list[tuple[Path, dict[str, Any]]]:
    recovered: list[tuple[Path, dict[str, Any]]] = []
    for path, item in _queue_items(root, run_id):
        if item.get("status") == "leased":
            lease = item.get("lease", {})
            if lease.get("expires_at") and _parse_time(lease["expires_at"]) <= current:
                item["status"] = "queued"
                item["last_error"] = {
                    "kind": "lease-expired",
                    "recorded_at": isoformat(current),
                }
                item.pop("lease", None)
                atomic_write_json(path, item)
        recovered.append((path, item))
    return recovered


def _record_agent_execution(
    root: Path,
    *,
    run_id: str,
    work_item: dict[str, Any],
    agent: dict[str, Any],
    executed_at: str,
) -> None:
    manifest_path = root / "runs" / run_id / "manifest.json"
    lock = _lock_path(root, run_id, "manifest-agent-executions")
    descriptor = _acquire_lock(lock)
    try:
        manifest = read_json(manifest_path)
        identity = (
            agent["agent_id"],
            work_item["work_item_id"],
            work_item["attempt"],
        )
        existing = {
            (item["agent_id"], item["work_item_id"], item["attempt"])
            for item in manifest.get("agent_executions", [])
        }
        if identity in existing:
            return
        tool_names_by_kind = {
            "source-discovery": ["register_source.py"],
            "evidence-extraction": ["extract_evidence.py"],
            "synthesis": ["propose_claim.py"],
            "validation": ["create_assessment.py"],
            "consensus": ["consensus_gate.py"],
            "apply-directive": ["ingest_directive.py"],
        }
        tool_paths = [Path(__file__)] + [
            ROOT / "tools" / name
            for name in tool_names_by_kind.get(work_item.get("kind"), [])
        ]
        manifest.setdefault("agent_executions", []).append(
            {
                "agent_id": agent["agent_id"],
                "work_item_id": work_item["work_item_id"],
                "attempt": work_item["attempt"],
                "model_provider": agent["provider"],
                "model_id": agent["model_family"],
                "prompt_hash": stable_digest(agent["prompt_profile"]),
                "tool_versions": {
                    path.name: sha256_file(path) for path in tool_paths if path.is_file()
                },
                "executed_at": executed_at,
            }
        )
        atomic_write_json(manifest_path, manifest)
    finally:
        _release_lock(lock, descriptor)


def lease_next(
    root: Path,
    *,
    run_id: str,
    agent_id: str,
    lease_seconds: int = 900,
    allow_disabled_pilot_agent: bool = False,
    now: datetime | None = None,
) -> dict[str, Any] | None:
    manifest = read_json(root / "runs" / run_id / "manifest.json")
    if manifest.get("status") in {"completed", "failed", "cancelled", "stopped"}:
        return None
    current = now or utc_now()
    budgets = _load_required(root, "config/budgets.json")
    kill_switch = budgets.get("kill_switch", {})
    if kill_switch.get("enabled") and (
        root / kill_switch.get("control_path", "state/STOP")
    ).exists():
        _stop_run(
            root,
            manifest=manifest,
            reason="kill-switch",
            observed=True,
            limit=False,
            now=current,
        )
        return None
    queue_entries = _recover_expired_leases(root, run_id, current)
    violation = _budget_violation(
        manifest, [item for _, item in queue_entries], current
    )
    if violation:
        reason, observed, limit = violation
        _stop_run(
            root,
            manifest=manifest,
            reason=reason,
            observed=observed,
            limit=limit,
            now=current,
        )
        return None
    active_leases = sum(item.get("status") == "leased" for _, item in queue_entries)
    maximum_parallel = manifest.get("budget", {}).get("maximum_parallel_agents")
    if maximum_parallel is not None and active_leases >= int(maximum_parallel):
        return None
    agent = _agent(root, agent_id, run_id=run_id)
    if not agent.get("enabled"):
        if not (allow_disabled_pilot_agent and manifest.get("mode") == "pilot"):
            raise RuntimeError(f"agent is disabled: {agent_id}")
    role = agent.get("role")
    for path, item in queue_entries:
        if item.get("required_role") != role:
            continue
        if item.get("status") != "queued":
            continue
        lock = _lock_path(root, run_id, item["work_item_id"])
        try:
            descriptor = _acquire_lock(lock)
        except FileExistsError:
            continue
        try:
            item = read_json(path)
            if item.get("status") != "queued":
                continue
            item["status"] = "leased"
            item["attempt"] = int(item.get("attempt", 0)) + 1
            item["lease"] = {
                "agent_id": agent_id,
                "acquired_at": isoformat(current),
                "expires_at": isoformat(current + timedelta(seconds=lease_seconds)),
            }
            item["updated_at"] = isoformat(current)
            atomic_write_json(path, item)
            _record_agent_execution(
                root,
                run_id=run_id,
                work_item=item,
                agent=agent,
                executed_at=isoformat(current),
            )
            return item
        finally:
            _release_lock(lock, descriptor)
    return None


def complete_work_item(
    root: Path,
    *,
    run_id: str,
    work_item_id: str,
    agent_id: str,
    output_refs: list[str],
    usage: dict[str, Any] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    path = root / "queue" / run_id / f"{work_item_id}.json"
    item = read_json(path)
    lease = item.get("lease", {})
    if item.get("status") != "leased" or lease.get("agent_id") != agent_id:
        raise RuntimeError("only the current lease owner can complete a Work Item")
    expected = set(item.get("output_paths", []))
    if not output_refs or not set(output_refs).issubset(expected):
        raise ValueError("output_refs must be a non-empty subset of declared output_paths")
    output_digests: dict[str, str] = {}
    for output_ref in output_refs:
        relative = PurePosixPath(output_ref)
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError(f"output_ref must be repository-relative: {output_ref}")
        output_path = root.joinpath(*relative.parts)
        if not output_path.is_file():
            raise ValueError(f"declared output does not exist: {output_ref}")
        output_digests[output_ref] = sha256_file(output_path)
    if usage is not None:
        allowed_usage = {"input_tokens", "output_tokens", "cost_usd", "measurement_note"}
        unknown = set(usage) - allowed_usage
        if unknown:
            raise ValueError(f"unknown usage fields: {sorted(unknown)}")
        for key in ("input_tokens", "output_tokens"):
            value = usage.get(key)
            if value is not None and (not isinstance(value, int) or value < 0):
                raise ValueError(f"{key} must be a non-negative integer or null")
        cost = usage.get("cost_usd")
        if cost is not None and (
            not isinstance(cost, (int, float)) or isinstance(cost, bool) or cost < 0
        ):
            raise ValueError("cost_usd must be a non-negative number or null")
    timestamp = isoformat(now)
    item["status"] = "completed"
    item["output_refs"] = output_refs
    item["output_digests"] = output_digests
    if usage is not None:
        item["usage"] = usage
    item["completed_by_agent_id"] = agent_id
    item["completed_at"] = timestamp
    item["updated_at"] = timestamp
    item.pop("lease", None)
    atomic_write_json(path, item)
    return item


def expand_followups(
    root: Path,
    *,
    run_id: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    manifest_path = root / "runs" / run_id / "manifest.json"
    manifest = read_json(manifest_path)
    if manifest.get("status") in {"completed", "failed", "cancelled", "stopped"}:
        return {"created": [], "manifest": manifest}
    queue_path = root / "queue" / run_id
    existing = [read_json(path) for path in sorted(queue_path.glob("WORK-*.json"))]
    current = now or utc_now()
    violation = _budget_violation(manifest, existing, current)
    if violation:
        reason, observed, limit = violation
        stopped = _stop_run(
            root,
            manifest=manifest,
            reason=reason,
            observed=observed,
            limit=limit,
            now=current,
        )
        return {"created": [], "manifest": stopped}
    existing_keys = {item["idempotency_key"] for item in existing}
    sequence = len(existing)
    created_at = isoformat(current)
    maximum_attempts = int(manifest["budget"]["maximum_retries_per_work_item"]) + 1
    additions: list[dict[str, Any]] = []
    monitor_source_ref = next(
        (
            source_ref
            for source_ref in manifest.get("policy_hashes", {})
            if source_ref.startswith("config/monitors/")
        ),
        None,
    )
    if not monitor_source_ref:
        raise ValueError("Run manifest has no pinned Monitor reference")
    monitor_ref = manifest.get("configuration_snapshots", {}).get(
        monitor_source_ref, monitor_source_ref
    )
    run_monitor = read_json(root / monitor_ref)
    minimum_evidence_sources = int(
        run_monitor.get("minimum_evidence_sources_per_claim", 2)
    )
    skipped_evidence_sources = {
        item.get("source_result_ref"): item
        for item in manifest.get("skipped_evidence_sources", [])
    }

    def source_decision(discovery_item: dict[str, Any]) -> str | None:
        output_refs = discovery_item.get("output_refs", [])
        if not output_refs:
            return None
        result = read_json(root / output_refs[0])
        try:
            return result["source_receipt"]["rights"]["acquisition_decision"]
        except KeyError as exc:
            raise ValueError(
                f"Source result lacks a Rights decision: {output_refs[0]}"
            ) from exc

    for parent in existing:
        if parent.get("kind") != "source-discovery" or parent.get("status") != "completed":
            continue
        decision = source_decision(parent)
        if decision not in {"evidence-excerpt", "approved-snapshot"}:
            for source_result_ref in parent.get("output_refs", []):
                skipped_evidence_sources[source_result_ref] = {
                    "source_result_ref": source_result_ref,
                    "parent_work_item_id": parent["work_item_id"],
                    "acquisition_decision": decision,
                    "reason": "Rights decision does not permit Evidence extraction",
                    "recorded_at": created_at,
                }
            parent_payload = parent.get("payload", {})
            replacement_generation = int(
                parent_payload.get("replacement_generation", 0)
            ) + 1
            original_candidate_slot = int(
                parent_payload.get(
                    "original_candidate_slot",
                    parent_payload.get("candidate_slot", 1),
                )
            )
            replacement_payload = dict(parent_payload)
            replacement_payload.update(
                {
                    "candidate_slot": original_candidate_slot
                    + 1000 * replacement_generation,
                    "original_candidate_slot": original_candidate_slot,
                    "replacement_for_work_item_id": parent["work_item_id"],
                    "replacement_generation": replacement_generation,
                    "replacement_reason": "source-not-evidence-eligible",
                }
            )
            identity = {
                "run_id": run_id,
                "task_id": manifest["task_id"],
                "monitor_id": manifest["monitor_id"],
                "kind": "source-discovery",
                "payload": replacement_payload,
            }
            idempotency_key = stable_digest(identity)
            if idempotency_key not in existing_keys:
                sequence += 1
                item = _work_item(
                    sequence=sequence,
                    run_id=run_id,
                    task_id=manifest["task_id"],
                    monitor_id=manifest["monitor_id"],
                    kind="source-discovery",
                    role="discovery",
                    payload=replacement_payload,
                    output_paths=[
                        f"proposals/sources/{run_id}/WORK-{sequence:06d}.json"
                    ],
                    maximum_attempts=maximum_attempts,
                    created_at=created_at,
                )
                additions.append(item)
                existing_keys.add(idempotency_key)
            continue
        for source_result_ref in parent.get("output_refs", []):
            payload = {
                "source_result_ref": source_result_ref,
                "parent_work_item_id": parent["work_item_id"],
            }
            identity = {
                "run_id": run_id,
                "task_id": manifest["task_id"],
                "monitor_id": manifest["monitor_id"],
                "kind": "evidence-extraction",
                "payload": payload,
            }
            idempotency_key = stable_digest(identity)
            if idempotency_key in existing_keys:
                continue
            sequence += 1
            item = _work_item(
                sequence=sequence,
                run_id=run_id,
                task_id=manifest["task_id"],
                monitor_id=manifest["monitor_id"],
                kind="evidence-extraction",
                role="extraction",
                payload=payload,
                output_paths=[f"proposals/evidence/{run_id}/WORK-{sequence:06d}.json"],
                maximum_attempts=maximum_attempts,
                created_at=created_at,
            )
            additions.append(item)
            existing_keys.add(idempotency_key)

    discovery_items = {
        item["work_item_id"]: item
        for item in existing
        if item.get("kind") == "source-discovery"
    }
    evidence_by_discovery: dict[str, dict[str, Any]] = {}
    for item in existing:
        if item.get("kind") != "evidence-extraction" or item.get("status") != "completed":
            continue
        parent_id = item.get("payload", {}).get("parent_work_item_id")
        if parent_id:
            evidence_by_discovery[parent_id] = item
    query_groups: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for item in discovery_items.values():
        payload = item.get("payload", {})
        key = (payload.get("query", ""), payload.get("query_role", "coverage"))
        query_groups.setdefault(key, []).append(item)
    for (query, query_role), discovery_group in sorted(query_groups.items()):
        if not query or not all(item.get("status") == "completed" for item in discovery_group):
            continue
        evidence_eligible = [
            item
            for item in discovery_group
            if source_decision(item) in {"evidence-excerpt", "approved-snapshot"}
        ]
        if len(evidence_eligible) < minimum_evidence_sources or not all(
            item["work_item_id"] in evidence_by_discovery for item in evidence_eligible
        ):
            continue
        evidence_refs = sorted(
            reference
            for item in evidence_eligible
            for reference in evidence_by_discovery[item["work_item_id"]].get(
                "output_refs", []
            )
        )
        payload = {
            "query": query,
            "query_role": query_role,
            "evidence_bundle_refs": evidence_refs,
            "parent_work_item_ids": sorted(
                evidence_by_discovery[item["work_item_id"]]["work_item_id"]
                for item in evidence_eligible
            ),
        }
        identity = {
            "run_id": run_id,
            "task_id": manifest["task_id"],
            "monitor_id": manifest["monitor_id"],
            "kind": "synthesis",
            "payload": payload,
        }
        idempotency_key = stable_digest(identity)
        if idempotency_key in existing_keys:
            continue
        sequence += 1
        item = _work_item(
            sequence=sequence,
            run_id=run_id,
            task_id=manifest["task_id"],
            monitor_id=manifest["monitor_id"],
            kind="synthesis",
            role="synthesis",
            payload=payload,
            output_paths=[f"proposals/claims/{run_id}/WORK-{sequence:06d}.json"],
            maximum_attempts=maximum_attempts,
            created_at=created_at,
        )
        additions.append(item)
        existing_keys.add(idempotency_key)

    completed_claim_items = [
        item
        for item in existing
        if item.get("kind") == "synthesis" and item.get("status") == "completed"
    ]
    for claim_item in completed_claim_items:
        for proposal_ref in claim_item.get("output_refs", []):
            payload = {
                "proposal_ref": proposal_ref,
                "parent_work_item_id": claim_item["work_item_id"],
                "review_mode": "blind-first-review",
            }
            identity = {
                "run_id": run_id,
                "task_id": manifest["task_id"],
                "monitor_id": manifest["monitor_id"],
                "kind": "validation",
                "payload": payload,
            }
            idempotency_key = stable_digest(identity)
            if idempotency_key in existing_keys:
                continue
            sequence += 1
            item = _work_item(
                sequence=sequence,
                run_id=run_id,
                task_id=manifest["task_id"],
                monitor_id=manifest["monitor_id"],
                kind="validation",
                role="validator",
                payload=payload,
                output_paths=[f"assessments/{run_id}/WORK-{sequence:06d}.json"],
                maximum_attempts=maximum_attempts,
                created_at=created_at,
            )
            additions.append(item)
            existing_keys.add(idempotency_key)

    completed_validations = {
        item.get("payload", {}).get("proposal_ref"): item
        for item in existing
        if item.get("kind") == "validation" and item.get("status") == "completed"
    }
    claim_refs = sorted(
        reference
        for item in completed_claim_items
        for reference in item.get("output_refs", [])
    )
    upstream_complete = bool(discovery_items) and all(
        item.get("status") == "completed" for item in discovery_items.values()
    )
    all_query_claims_complete = len(completed_claim_items) == len(query_groups)
    if (
        claim_refs
        and upstream_complete
        and all_query_claims_complete
        and all(reference in completed_validations for reference in claim_refs)
    ):
        pairs = []
        output_paths = []
        for proposal_ref in claim_refs:
            proposal = read_json(root / proposal_ref)
            assessment_refs = completed_validations[proposal_ref].get("output_refs", [])
            pairs.append(
                {"proposal_ref": proposal_ref, "assessment_refs": assessment_refs}
            )
            output_paths.append(
                f"decisions/{run_id}/{proposal['proposal_id']}.json"
            )
        payload = {"proposal_assessment_pairs": pairs}
        identity = {
            "run_id": run_id,
            "task_id": manifest["task_id"],
            "monitor_id": manifest["monitor_id"],
            "kind": "consensus",
            "payload": payload,
        }
        idempotency_key = stable_digest(identity)
        if idempotency_key not in existing_keys:
            sequence += 1
            item = _work_item(
                sequence=sequence,
                run_id=run_id,
                task_id=manifest["task_id"],
                monitor_id=manifest["monitor_id"],
                kind="consensus",
                role="consensus",
                payload=payload,
                output_paths=output_paths,
                maximum_attempts=maximum_attempts,
                created_at=created_at,
            )
            additions.append(item)
            existing_keys.add(idempotency_key)

    limit = int(manifest["budget"]["maximum_work_items"])
    if len(existing) + len(additions) > limit:
        stopped = _stop_run(
            root,
            manifest=manifest,
            reason="maximum-work-items",
            observed=len(existing) + len(additions),
            limit=limit,
            now=current,
        )
        return {"created": [], "manifest": stopped}
    source_limit = manifest["budget"].get("maximum_sources_per_monitor")
    prospective_sources = sum(
        item.get("kind") == "source-discovery" for item in existing + additions
    )
    if source_limit is not None and prospective_sources > int(source_limit):
        stopped = _stop_run(
            root,
            manifest=manifest,
            reason="maximum-sources-per-monitor",
            observed=prospective_sources,
            limit=source_limit,
            now=current,
        )
        return {"created": [], "manifest": stopped}
    for item in additions:
        atomic_write_json(queue_path / f"{item['work_item_id']}.json", item)
    if additions:
        manifest["work_item_ids"].extend(item["work_item_id"] for item in additions)
        manifest["expansion_events"].append(
            {
                "expanded_at": created_at,
                "created_work_item_ids": [item["work_item_id"] for item in additions],
                "reason": "completed-upstream-work-items",
            }
        )
        manifest["metrics"]["work_items_total"] = len(existing) + len(additions)
    manifest["skipped_evidence_sources"] = sorted(
        skipped_evidence_sources.values(), key=lambda item: item["source_result_ref"]
    )
    atomic_write_json(manifest_path, manifest)
    return {"created": additions, "manifest": manifest}


def reconcile_agent_executions(root: Path, *, run_id: str) -> dict[str, Any]:
    repaired: list[str] = []
    for path in sorted((root / "queue" / run_id).glob("WORK-*.json")):
        item = read_json(path)
        if item.get("status") != "completed":
            continue
        agent_id = item.get("completed_by_agent_id")
        if not agent_id:
            for output_ref in item.get("output_refs", []):
                output = read_json(root / output_ref)
                agent_id = output.get("created_by_agent_id")
                if agent_id:
                    break
        if not agent_id:
            continue
        if not item.get("completed_by_agent_id"):
            item["completed_by_agent_id"] = agent_id
            atomic_write_json(path, item)
            repaired.append(item["work_item_id"])
        _record_agent_execution(
            root,
            run_id=run_id,
            work_item=item,
            agent=_agent(root, agent_id, run_id=run_id),
            executed_at=item.get("completed_at", item["updated_at"]),
        )
    return {
        "repaired_work_item_ids": repaired,
        "manifest": read_json(root / "runs" / run_id / "manifest.json"),
    }


def fail_work_item(
    root: Path,
    *,
    run_id: str,
    work_item_id: str,
    agent_id: str,
    error_kind: str,
    error_message: str,
    retryable: bool,
    now: datetime | None = None,
) -> dict[str, Any]:
    path = root / "queue" / run_id / f"{work_item_id}.json"
    item = read_json(path)
    lease = item.get("lease", {})
    if item.get("status") != "leased" or lease.get("agent_id") != agent_id:
        raise RuntimeError("only the current lease owner can fail a Work Item")
    timestamp = isoformat(now)
    item["last_error"] = {
        "kind": error_kind,
        "message": error_message,
        "retryable": retryable,
        "recorded_at": timestamp,
    }
    can_retry = retryable and item["attempt"] < item["maximum_attempts"]
    item["status"] = "queued" if can_retry else "dead-letter"
    item["updated_at"] = timestamp
    item.pop("lease", None)
    atomic_write_json(path, item)
    if not can_retry:
        exception = {
            "schema_version": "0.1.0",
            "exception_id": f"EXC-{run_id}-{work_item_id}",
            "run_id": run_id,
            "work_item_id": work_item_id,
            "status": "open",
            "recorded_at": timestamp,
            "error": item["last_error"],
        }
        atomic_write_json(
            root / "reviews" / "exceptions" / run_id / f"{work_item_id}.json",
            exception,
        )
    return item


def finalize_run(root: Path, *, run_id: str, now: datetime | None = None) -> dict[str, Any]:
    path = root / "runs" / run_id / "manifest.json"
    manifest = read_json(path)
    items = [read_json(item) for item in sorted((root / "queue" / run_id).glob("WORK-*.json"))]
    counts: dict[str, int] = {}
    for item in items:
        counts[item["status"]] = counts.get(item["status"], 0) + 1
    if manifest.get("status") == "stopped":
        status = "stopped"
    elif any(item["status"] in {"queued", "leased"} for item in items):
        status = "running"
    elif items and all(item["status"] == "completed" for item in items):
        status = "completed"
    elif any(item["status"] == "completed" for item in items):
        status = "partial"
    else:
        status = "failed"
    manifest["status"] = status
    manifest.setdefault("metrics", {}).update(
        {"work_items_total": len(items), "work_items_by_status": counts}
    )
    manifest["cost"] = _usage_summary(items)
    decisions = [
        read_json(decision_path)
        for decision_path in sorted((root / "decisions" / run_id).glob("*.json"))
    ]
    if decisions:
        decision_counts: dict[str, int] = {}
        for decision in decisions:
            outcome = decision["outcome"]
            decision_counts[outcome] = decision_counts.get(outcome, 0) + 1
        manifest["metrics"]["consensus_outcomes"] = decision_counts
        if "contested" in decision_counts:
            manifest["research_status"] = "contested"
        elif decision_counts.get("accepted") == len(decisions):
            manifest["research_status"] = "accepted"
        else:
            manifest["research_status"] = "provisional"
    if status in {"completed", "partial", "failed", "cancelled", "stopped"}:
        manifest["completed_at"] = isoformat(now)
    atomic_write_json(path, manifest)
    return manifest


def _print(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    commands = parser.add_subparsers(dest="command", required=True)

    start = commands.add_parser("start")
    start.add_argument("--run-id", required=True)
    start.add_argument("--task-id", required=True)
    start.add_argument("--monitor-id", required=True)
    start.add_argument("--pilot", action="store_true")
    start.add_argument("--maximum-work-items", type=int)

    lease = commands.add_parser("lease")
    lease.add_argument("--run-id", required=True)
    lease.add_argument("--agent-id", required=True)
    lease.add_argument("--lease-seconds", type=int, default=900)
    lease.add_argument("--allow-disabled-pilot-agent", action="store_true")

    complete = commands.add_parser("complete")
    complete.add_argument("--run-id", required=True)
    complete.add_argument("--work-item-id", required=True)
    complete.add_argument("--agent-id", required=True)
    complete.add_argument("--output-ref", action="append", required=True)
    complete.add_argument("--input-tokens", type=int)
    complete.add_argument("--output-tokens", type=int)
    complete.add_argument("--cost-usd", type=float)
    complete.add_argument("--usage-note")

    fail = commands.add_parser("fail")
    fail.add_argument("--run-id", required=True)
    fail.add_argument("--work-item-id", required=True)
    fail.add_argument("--agent-id", required=True)
    fail.add_argument("--error-kind", required=True)
    fail.add_argument("--error-message", required=True)
    fail.add_argument("--retryable", action="store_true")

    finalize = commands.add_parser("finalize")
    finalize.add_argument("--run-id", required=True)
    expand = commands.add_parser("expand")
    expand.add_argument("--run-id", required=True)
    reconcile = commands.add_parser("reconcile")
    reconcile.add_argument("--run-id", required=True)
    args = parser.parse_args()

    if args.command == "start":
        result = create_run(
            args.root,
            run_id=args.run_id,
            task_id=args.task_id,
            monitor_id=args.monitor_id,
            pilot=args.pilot,
            maximum_work_items=args.maximum_work_items,
        )
    elif args.command == "lease":
        result = lease_next(
            args.root,
            run_id=args.run_id,
            agent_id=args.agent_id,
            lease_seconds=args.lease_seconds,
            allow_disabled_pilot_agent=args.allow_disabled_pilot_agent,
        )
    elif args.command == "complete":
        usage_values = {
            "input_tokens": args.input_tokens,
            "output_tokens": args.output_tokens,
            "cost_usd": args.cost_usd,
        }
        if args.usage_note is not None:
            usage_values["measurement_note"] = args.usage_note
        usage = (
            usage_values
            if any(value is not None for value in usage_values.values())
            else None
        )
        result = complete_work_item(
            args.root,
            run_id=args.run_id,
            work_item_id=args.work_item_id,
            agent_id=args.agent_id,
            output_refs=args.output_ref,
            usage=usage,
        )
    elif args.command == "fail":
        result = fail_work_item(
            args.root,
            run_id=args.run_id,
            work_item_id=args.work_item_id,
            agent_id=args.agent_id,
            error_kind=args.error_kind,
            error_message=args.error_message,
            retryable=args.retryable,
        )
    elif args.command == "expand":
        result = expand_followups(args.root, run_id=args.run_id)
    elif args.command == "reconcile":
        result = reconcile_agent_executions(args.root, run_id=args.run_id)
    else:
        result = finalize_run(args.root, run_id=args.run_id)
    _print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
