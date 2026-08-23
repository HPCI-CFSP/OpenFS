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
        root / "config" / "autonomy-policy.json",
        root / "config" / "budgets.json",
        root / "config" / "consensus-policy.json",
        root / "config" / "role-permissions.json",
        monitor_path,
    ]
    return {path.relative_to(root).as_posix(): sha256_file(path) for path in paths}


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
    for query in monitor.get("query_families", []):
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
                    "languages": monitor.get("languages", []),
                    "source_classes": monitor.get("source_classes", []),
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

    manifest = {
        "schema_version": "0.1.0",
        "run_id": run_id,
        "task_id": task_id,
        "monitor_id": monitor_id,
        "mode": "pilot" if pilot else "production",
        "base_commit": git_head(root),
        "started_at": created_at,
        "status": "created",
        "policy_hashes": _policy_hashes(root, monitor_path),
        "budget": {
            "maximum_run_minutes": defaults.get("maximum_run_minutes"),
            "maximum_work_items": requested_limit,
            "maximum_retries_per_work_item": defaults.get("maximum_retries_per_work_item"),
            "maximum_cost_usd": defaults.get("maximum_cost_usd"),
        },
        "directive_ids": [directive["directive_id"] for directive in directives],
        "work_item_ids": [item["work_item_id"] for item in work_items],
        "agent_executions": [],
        "query_receipts": [],
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
    for item in work_items:
        atomic_write_json(queue_path / f"{item['work_item_id']}.json", item)
    atomic_write_json(run_path, manifest)
    return manifest


def _agent(root: Path, agent_id: str) -> dict[str, Any]:
    registry = _load_required(root, "config/agent-registry.json")
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
    agent = _agent(root, agent_id)
    if not agent.get("enabled"):
        if not (allow_disabled_pilot_agent and manifest.get("mode") == "pilot"):
            raise RuntimeError(f"agent is disabled: {agent_id}")
    role = agent.get("role")
    current = now or utc_now()
    for path in sorted((root / "queue" / run_id).glob("WORK-*.json")):
        item = read_json(path)
        if item.get("required_role") != role:
            continue
        if item.get("status") == "leased":
            lease = item.get("lease", {})
            if lease.get("expires_at") and _parse_time(lease["expires_at"]) <= current:
                item["status"] = "queued"
                item["last_error"] = {"kind": "lease-expired", "recorded_at": isoformat(current)}
                item.pop("lease", None)
                atomic_write_json(path, item)
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
    timestamp = isoformat(now)
    item["status"] = "completed"
    item["output_refs"] = output_refs
    item["output_digests"] = output_digests
    item["completed_at"] = timestamp
    item["updated_at"] = timestamp
    item.pop("lease", None)
    atomic_write_json(path, item)
    return item


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
    if any(item["status"] in {"queued", "leased"} for item in items):
        status = "running"
    elif items and all(item["status"] == "completed" for item in items):
        status = "completed"
    elif any(item["status"] == "completed" for item in items):
        status = "partial"
    else:
        status = "failed"
    manifest["status"] = status
    manifest["metrics"] = {"work_items_total": len(items), "work_items_by_status": counts}
    if status in {"completed", "partial", "failed", "cancelled"}:
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

    fail = commands.add_parser("fail")
    fail.add_argument("--run-id", required=True)
    fail.add_argument("--work-item-id", required=True)
    fail.add_argument("--agent-id", required=True)
    fail.add_argument("--error-kind", required=True)
    fail.add_argument("--error-message", required=True)
    fail.add_argument("--retryable", action="store_true")

    finalize = commands.add_parser("finalize")
    finalize.add_argument("--run-id", required=True)
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
        result = complete_work_item(
            args.root,
            run_id=args.run_id,
            work_item_id=args.work_item_id,
            agent_id=args.agent_id,
            output_refs=args.output_ref,
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
    else:
        result = finalize_run(args.root, run_id=args.run_id)
    _print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
