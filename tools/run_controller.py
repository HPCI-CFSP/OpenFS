#!/usr/bin/env python3
"""Create and operate idempotent OpenFS Runs and leased Work Items."""

from __future__ import annotations

import argparse
import fcntl
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
from check_consensus_readiness import evaluate_run, record_readiness


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
    monitor = read_json(monitor_path)
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
    subject_registry_ref = monitor.get("subject_registry_ref")
    if subject_registry_ref:
        subject_registry_path = root / subject_registry_ref
        if (
            subject_registry_path.parent != root / "config"
            or not subject_registry_path.is_file()
        ):
            raise ValueError(
                "subject_registry_ref must name an existing file directly under config/"
            )
        paths.append(subject_registry_path)
    return {
        path.relative_to(root).as_posix(): stable_digest(read_json(path))
        for path in paths
    }


def _subject_query_plan(root: Path, monitor: dict[str, Any]) -> list[dict[str, Any]]:
    registry_ref = monitor.get("subject_registry_ref")
    templates = monitor.get("subject_query_templates", [])
    if not registry_ref and not templates:
        return []
    if not registry_ref or not templates:
        raise ValueError(
            "subject_registry_ref and subject_query_templates must be configured together"
        )
    registry = _load_required(root, registry_ref)
    default_fields = registry.get("default_profile_fields", [])
    plan: list[dict[str, Any]] = []
    seen_center_ids: set[str] = set()
    for center in registry.get("centers", []):
        center_id = center.get("center_id")
        if not center_id or center_id in seen_center_ids:
            raise ValueError(f"subject registry has a duplicate or empty center_id: {center_id}")
        seen_center_ids.add(center_id)
        values = {
            "center_id": center_id,
            "name_ja": center.get("name_ja", ""),
            "name_en": center.get("name_en", ""),
            "official_url": center.get("official_url", ""),
        }
        allowed_fields = set(center.get("profile_fields", default_fields))
        for template in templates:
            template_fields = template.get("profile_fields", [])
            unknown_fields = set(template_fields) - allowed_fields
            if unknown_fields:
                raise ValueError(
                    f"subject query template {template.get('template_id')} uses unknown "
                    f"profile fields for {center_id}: {sorted(unknown_fields)}"
                )
            try:
                query = template["query"].format(**values)
            except (KeyError, ValueError) as exc:
                raise ValueError(
                    f"invalid subject query template {template.get('template_id')}: {exc}"
                ) from exc
            plan.append(
                {
                    "query": query,
                    "query_role": "subject-coverage",
                    "subject_ids": [center_id],
                    "profile_fields": template_fields,
                    "query_template_id": template["template_id"],
                }
            )
    return plan


def _latest_followup_plan(
    root: Path, monitor: dict[str, Any], *, as_of: datetime
) -> tuple[str, dict[str, Any]] | None:
    if not monitor.get("use_latest_followup_plan"):
        return None
    candidates: list[tuple[str, str, str, dict[str, Any]]] = []
    for path in sorted((root / "reviews" / "followups").glob("*.json")):
        plan = read_json(path)
        if plan.get("monitor_id") != monitor.get("monitor_id"):
            continue
        if plan.get("status") != "generated-for-research":
            continue
        base_run_id = plan.get("base_run_id")
        base_manifest_path = root / "runs" / str(base_run_id) / "manifest.json"
        if not base_manifest_path.is_file():
            continue
        base_manifest = read_json(base_manifest_path)
        if base_manifest.get("status") not in {"completed", "partial"}:
            continue
        if (
            base_manifest.get("task_id") != monitor.get("task_id")
            or base_manifest.get("monitor_id") != monitor.get("monitor_id")
        ):
            continue
        completed_at = base_manifest.get("completed_at")
        generated_at = plan.get("generated_at")
        if not completed_at or not generated_at:
            continue
        if _parse_time(completed_at) > as_of or _parse_time(generated_at) > as_of:
            continue
        brief_ref = plan.get("input_brief_ref")
        if not brief_ref or not (root / brief_ref).is_file():
            continue
        if stable_digest(read_json(root / brief_ref)) != plan.get("input_brief_digest"):
            raise ValueError(f"follow-up input Brief digest mismatch: {path}")
        source_ref = path.relative_to(root).as_posix()
        candidates.append((completed_at, generated_at, source_ref, plan))
    if not candidates:
        return None
    _, _, source_ref, plan = max(candidates, key=lambda item: item[:3])
    return source_ref, plan


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


def _evidence_ids(root: Path, refs: list[str]) -> set[str]:
    return {
        candidate["evidence_id"]
        for ref in refs
        for candidate in read_json(root / ref).get("evidence_candidates", [])
    }


def _resolve_predecessor_evidence_refs(
    root: Path,
    *,
    predecessor_profile: dict[str, Any],
    required_evidence_ids: set[str],
) -> list[str]:
    if not required_evidence_ids:
        return []
    declared_refs = predecessor_profile.get("evidence_bundle_refs", [])
    preferred = [root / ref for ref in declared_refs]
    predecessor_run_id = predecessor_profile["run_id"]
    preferred.extend(
        sorted((root / "proposals" / "evidence" / predecessor_run_id).glob("*.json"))
    )
    preferred.extend(sorted((root / "proposals" / "evidence").glob("*/*.json")))
    selected: list[str] = []
    covered: set[str] = set()
    seen_paths: set[Path] = set()
    for path in preferred:
        if path in seen_paths or not path.is_file():
            continue
        seen_paths.add(path)
        bundle_ids = {
            candidate["evidence_id"]
            for candidate in read_json(path).get("evidence_candidates", [])
        }
        if not (bundle_ids & (required_evidence_ids - covered)):
            continue
        selected.append(str(path.relative_to(root)))
        covered.update(bundle_ids & required_evidence_ids)
        if covered == required_evidence_ids:
            break
    missing = required_evidence_ids - covered
    if missing:
        raise ValueError(
            "predecessor profile references unresolved Evidence IDs: "
            + ", ".join(sorted(missing))
        )
    return sorted(selected)


def _predecessor_profile_inputs(
    root: Path,
    *,
    manifest: dict[str, Any],
    center_id: str,
    current_evidence_refs: list[str],
) -> dict[str, Any]:
    predecessor_run_id = manifest.get("followup_plan", {}).get("base_run_id")
    if not predecessor_run_id:
        return {}
    predecessor_manifest_path = root / "runs" / predecessor_run_id / "manifest.json"
    predecessor_profile_path = (
        root
        / "proposals"
        / "center-profiles"
        / predecessor_run_id
        / f"{center_id}.json"
    )
    if not predecessor_manifest_path.is_file() or not predecessor_profile_path.is_file():
        return {}
    predecessor_manifest = read_json(predecessor_manifest_path)
    if predecessor_manifest.get("status") != "completed":
        return {}
    if predecessor_manifest.get("task_id") != manifest.get("task_id"):
        return {}
    if predecessor_manifest.get("monitor_id") != manifest.get("monitor_id"):
        return {}
    predecessor_profile = read_json(predecessor_profile_path)
    if predecessor_profile.get("center_id") != center_id:
        raise ValueError("predecessor Center Profile has a mismatched center ID")
    current_ids = _evidence_ids(root, current_evidence_refs)
    required_predecessor_ids = set(predecessor_profile.get("evidence_refs", [])) - current_ids
    predecessor_evidence_refs = _resolve_predecessor_evidence_refs(
        root,
        predecessor_profile=predecessor_profile,
        required_evidence_ids=required_predecessor_ids,
    )
    profile_ref = str(predecessor_profile_path.relative_to(root))
    return {
        "predecessor_run_id": predecessor_run_id,
        "predecessor_profile_ref": profile_ref,
        "predecessor_profile_digest": stable_digest(predecessor_profile),
        "predecessor_evidence_bundle_refs": predecessor_evidence_refs,
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
    directive_hashes = {
        f"reviews/directives/{directive['directive_id']}.json": stable_digest(directive)
        for directive in directives
    }
    directive_snapshots = {
        source_ref: f"runs/{run_id}/inputs/{source_ref}"
        for source_ref in sorted(directive_hashes)
    }
    maximum_attempts = int(defaults.get("maximum_retries_per_work_item", 0)) + 1

    work_items: list[dict[str, Any]] = []
    slots_per_query = int(monitor.get("discovery_slots_per_query", 1))
    followup = _latest_followup_plan(root, monitor, as_of=created)
    followup_query_plan = []
    if followup:
        _, followup_plan = followup
        for entry in followup_plan.get("queries", []):
            followup_query_plan.append(
                {
                    "query": entry["query"],
                    "query_role": entry["query_role"],
                    "subject_ids": [entry["center_id"]],
                    "profile_fields": entry["profile_fields"],
                    "query_template_id": entry["query_id"],
                    "source_classes": entry.get("source_classes", []),
                    "followup_plan_id": followup_plan["followup_plan_id"],
                    "followup_query_id": entry["query_id"],
                }
            )
    query_plan = [
        {"query": query, "query_role": "coverage"}
        for query in monitor.get("query_families", [])
    ] + [
        {"query": query, "query_role": "falsification"}
        for query in monitor.get("falsification_queries", [])
    ] + _subject_query_plan(root, monitor) + followup_query_plan
    for query_entry in query_plan:
        for candidate_slot in range(1, slots_per_query + 1):
            sequence = len(work_items) + 1
            payload = {
                "query": query_entry["query"],
                "query_role": query_entry["query_role"],
                "candidate_slot": candidate_slot,
                "languages": monitor.get("languages", []),
                "source_classes": query_entry.get(
                    "source_classes", monitor.get("source_classes", [])
                ),
                "source_class_requirements": monitor.get(
                    "source_class_requirements", []
                ),
                "maximum_unchecked_days": monitor.get("maximum_unchecked_days"),
            }
            for key in (
                "subject_ids",
                "profile_fields",
                "query_template_id",
                "followup_plan_id",
                "followup_query_id",
            ):
                if key in query_entry:
                    payload[key] = query_entry[key]
            work_items.append(
                _work_item(
                    sequence=sequence,
                    run_id=run_id,
                    task_id=task_id,
                    monitor_id=monitor_id,
                    kind="source-discovery",
                    role="discovery",
                    payload=payload,
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
    followup_manifest = None
    if followup:
        followup_ref, followup_plan = followup
        followup_manifest = {
            "source_ref": followup_ref,
            "snapshot_ref": f"runs/{run_id}/inputs/{followup_ref}",
            "digest": stable_digest(followup_plan),
            "followup_plan_id": followup_plan["followup_plan_id"],
            "base_run_id": followup_plan["base_run_id"],
        }
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
        "coverage_status": "not-evaluated",
        "assignment_contract_version": "0.2.0",
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
        "directive_hashes": directive_hashes,
        "directive_snapshots": directive_snapshots,
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
    if followup_manifest:
        manifest["followup_plan"] = followup_manifest
    run_identity = {
        key: manifest[key]
        for key in (
            "run_id",
            "task_id",
            "monitor_id",
            "mode",
            "assignment_contract_version",
            "policy_hashes",
            "directive_ids",
            "directive_hashes",
        )
    }
    run_identity["followup_plan"] = followup_manifest
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
    for source_ref, snapshot_ref in directive_snapshots.items():
        atomic_write_json(root / snapshot_ref, read_json(root / source_ref))
    if followup_manifest:
        atomic_write_json(
            root / followup_manifest["snapshot_ref"],
            read_json(root / followup_manifest["source_ref"]),
        )
    for item in work_items:
        atomic_write_json(queue_path / f"{item['work_item_id']}.json", item)
    atomic_write_json(run_path, manifest)
    return record_readiness(root, evaluate_run(root, run_id))


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
    descriptor = os.open(path, os.O_CREAT | os.O_RDWR, 0o600)
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        os.close(descriptor)
        raise FileExistsError(f"lock is already held: {path}") from exc
    return descriptor


def _release_lock(path: Path, descriptor: int) -> None:
    fcntl.flock(descriptor, fcntl.LOCK_UN)
    os.close(descriptor)


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
    declared_execution: dict[str, Any] | None = None,
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
            "center-profile-synthesis": ["propose_center_profile.py"],
            "validation": ["create_assessment.py"],
            "consensus": ["consensus_gate.py"],
            "apply-directive": ["apply_directive.py"],
        }
        tool_paths = [Path(__file__)] + [
            ROOT / "tools" / name
            for name in tool_names_by_kind.get(work_item.get("kind"), [])
        ]
        declared = declared_execution or {}
        execution = {
            "agent_id": agent["agent_id"],
            "work_item_id": work_item["work_item_id"],
            "attempt": work_item["attempt"],
            "model_provider": declared.get("model_provider", agent["provider"]),
            "model_id": declared.get("model_id", agent["model_family"]),
            "prompt_hash": declared.get(
                "prompt_hash", stable_digest(agent["prompt_profile"])
            ),
            "tool_versions": declared.get(
                "tool_versions",
                {path.name: sha256_file(path) for path in tool_paths if path.is_file()},
            ),
            "executed_at": executed_at,
        }
        if declared.get("resolved_model_version"):
            execution["resolved_model_version"] = declared["resolved_model_version"]
        if declared.get("skill_hash"):
            execution["skill_hash"] = declared["skill_hash"]
        manifest.setdefault("agent_executions", []).append(execution)
        atomic_write_json(manifest_path, manifest)
    finally:
        _release_lock(lock, descriptor)


def _lease_next(
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
        assigned_agent_id = item.get("payload", {}).get("assigned_reviewer_agent_id")
        if assigned_agent_id and assigned_agent_id != agent_id:
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


def _complete_work_item(
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
    if set(output_refs) != expected:
        raise ValueError("output_refs must exactly match declared output_paths")
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
    item["completion_mode"] = "leased-local"
    item["completed_at"] = timestamp
    item["updated_at"] = timestamp
    item.pop("lease", None)
    atomic_write_json(path, item)
    return item


def _expand_followups(
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
    minimum_profile_evidence_sources = int(
        run_monitor.get("minimum_evidence_sources_per_profile", 2)
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
        if result.get("object_type") == "discovery_no_result":
            return "no-result"
        try:
            return result["source_receipt"]["rights"]["acquisition_decision"]
        except KeyError as exc:
            raise ValueError(
                f"Source result lacks a Rights decision: {output_refs[0]}"
            ) from exc

    def source_id(discovery_item: dict[str, Any]) -> str | None:
        output_refs = discovery_item.get("output_refs", [])
        if not output_refs:
            return None
        result = read_json(root / output_refs[0])
        if result.get("object_type") == "discovery_no_result":
            return None
        return result.get("source_receipt", {}).get("source_id")

    for parent in existing:
        if parent.get("kind") != "source-discovery" or parent.get("status") != "completed":
            continue
        decision = source_decision(parent)
        if decision == "no-result":
            continue
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
        if run_monitor.get("synthesis_product") == "center-profile":
            continue
        if not query or not all(item.get("status") == "completed" for item in discovery_group):
            continue
        evidence_eligible = [
            item
            for item in discovery_group
            if source_decision(item) in {"evidence-excerpt", "approved-snapshot"}
        ]
        if len({source_id(item) for item in evidence_eligible}) < minimum_evidence_sources or not all(
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

    if run_monitor.get("synthesis_product") == "center-profile":
        subject_groups: dict[str, list[dict[str, Any]]] = {}
        for item in discovery_items.values():
            for subject_id in item.get("payload", {}).get("subject_ids", []):
                subject_groups.setdefault(subject_id, []).append(item)
        for subject_id, discovery_group in sorted(subject_groups.items()):
            if not all(item.get("status") == "completed" for item in discovery_group):
                continue
            evidence_eligible = [
                item
                for item in discovery_group
                if source_decision(item) in {"evidence-excerpt", "approved-snapshot"}
            ]
            if len({source_id(item) for item in evidence_eligible}) < minimum_profile_evidence_sources or not all(
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
            predecessor_inputs = _predecessor_profile_inputs(
                root,
                manifest=manifest,
                center_id=subject_id,
                current_evidence_refs=evidence_refs,
            )
            evidence_refs = sorted(
                set(evidence_refs)
                | set(predecessor_inputs.get("predecessor_evidence_bundle_refs", []))
            )
            payload = {
                "center_id": subject_id,
                "profile_fields": sorted(
                    {
                        field
                        for item in discovery_group
                        for field in item.get("payload", {}).get("profile_fields", [])
                    }
                ),
                "evidence_bundle_refs": evidence_refs,
                "parent_work_item_ids": sorted(
                    evidence_by_discovery[item["work_item_id"]]["work_item_id"]
                    for item in evidence_eligible
                ),
            }
            payload.update(predecessor_inputs)
            identity = {
                "run_id": run_id,
                "task_id": manifest["task_id"],
                "monitor_id": manifest["monitor_id"],
                "kind": "center-profile-synthesis",
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
                kind="center-profile-synthesis",
                role="synthesis",
                payload=payload,
                output_paths=[
                    f"proposals/center-profiles/{run_id}/{subject_id}.json"
                ],
                maximum_attempts=maximum_attempts,
                created_at=created_at,
            )
            additions.append(item)
            existing_keys.add(idempotency_key)

    completed_proposal_items = [
        item
        for item in existing
        if item.get("kind") in {"synthesis", "center-profile-synthesis"}
        and item.get("status") == "completed"
    ]
    agent_registry = read_json(
        root
        / manifest["configuration_snapshots"]["config/agent-registry.json"]
    )
    eligible_reviewers = []
    for candidate in agent_registry.get("agents", []):
        if candidate.get("role") not in {"validator", "critic"}:
            continue
        if candidate.get("provider") in {None, "unconfigured"}:
            continue
        if candidate.get("model_family") in {None, "unconfigured"}:
            continue
        if manifest.get("mode") != "pilot" and not candidate.get("enabled"):
            continue
        eligible_reviewers.append(candidate)
    for proposal_item in completed_proposal_items:
        for proposal_ref in proposal_item.get("output_refs", []):
            proposal = read_json(root / proposal_ref)
            if not proposal.get("proposal_id") or not proposal.get("object_type"):
                continue
            for reviewer in sorted(eligible_reviewers, key=lambda item: item["agent_id"]):
                payload = {
                    "proposal_ref": proposal_ref,
                    "parent_work_item_id": proposal_item["work_item_id"],
                    "review_mode": "blind-first-review",
                    "assigned_reviewer_agent_id": reviewer["agent_id"],
                    "reviewer_independence_group": reviewer["agent_independence_group"],
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
                    role=reviewer["role"],
                    payload=payload,
                    output_paths=[
                        f"assessments/{run_id}/{proposal['proposal_id']}/{reviewer['agent_id']}.json"
                    ],
                    maximum_attempts=maximum_attempts,
                    created_at=created_at,
                )
                additions.append(item)
                existing_keys.add(idempotency_key)

    validations_by_proposal: dict[str, list[dict[str, Any]]] = {}
    for item in existing:
        if item.get("kind") != "validation":
            continue
        proposal_ref = item.get("payload", {}).get("proposal_ref")
        if proposal_ref:
            validations_by_proposal.setdefault(proposal_ref, []).append(item)
    completed_validations_by_proposal: dict[str, list[dict[str, Any]]] = {}
    for item in existing:
        if item.get("kind") != "validation" or item.get("status") != "completed":
            continue
        completed_validations_by_proposal.setdefault(
            item.get("payload", {}).get("proposal_ref"), []
        ).append(item)

    proposal_refs = sorted(
        reference
        for item in completed_proposal_items
        for reference in item.get("output_refs", [])
        if read_json(root / reference).get("proposal_id")
    )
    completed_claim_items = [
        item
        for item in existing
        if item.get("kind") == "synthesis" and item.get("status") == "completed"
    ]
    upstream_complete = bool(discovery_items) and all(
        item.get("status") == "completed" for item in discovery_items.values()
    )
    all_query_claims_complete = len(completed_claim_items) == len(query_groups)
    completed_profile_items = [
        item
        for item in completed_proposal_items
        if item.get("kind") == "center-profile-synthesis"
    ]
    all_profile_proposals_complete = (
        len(completed_profile_items) == len(subject_groups)
        if run_monitor.get("synthesis_product") == "center-profile"
        else True
    )
    all_expected_proposals_complete = (
        all_profile_proposals_complete
        if run_monitor.get("synthesis_product") == "center-profile"
        else all_query_claims_complete
    )
    if (
        proposal_refs
        and upstream_complete
        and all_expected_proposals_complete
        and all(validations_by_proposal.get(reference) for reference in proposal_refs)
        and all(
            len(completed_validations_by_proposal.get(reference, []))
            == len(validations_by_proposal[reference])
            for reference in proposal_refs
        )
    ):
        pairs = []
        output_paths = []
        for proposal_ref in proposal_refs:
            proposal = read_json(root / proposal_ref)
            assessment_refs = sorted(
                ref
                for validation in completed_validations_by_proposal[proposal_ref]
                for ref in validation.get("output_refs", [])
            )
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
    manifest["no_result_discoveries"] = sorted(
        (
            {
                "work_item_id": item["work_item_id"],
                "result_ref": item["output_refs"][0],
            }
            for item in existing
            if item.get("kind") == "source-discovery"
            and item.get("status") == "completed"
            and item.get("output_refs")
            and read_json(root / item["output_refs"][0]).get("object_type")
            == "discovery_no_result"
        ),
        key=lambda item: item["work_item_id"],
    )
    atomic_write_json(manifest_path, manifest)
    return {"created": additions, "manifest": manifest}


def _reconcile_agent_executions(root: Path, *, run_id: str) -> dict[str, Any]:
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


def _fail_work_item(
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


def _finalize_run(root: Path, *, run_id: str, now: datetime | None = None) -> dict[str, Any]:
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
    elif any(
        (root / directory / run_id).exists()
        for directory in ("proposals/claims", "proposals/center-profiles")
    ):
        manifest["research_status"] = "provisional"
    if status in {"completed", "partial", "failed", "cancelled", "stopped"}:
        manifest["completed_at"] = isoformat(now)
    atomic_write_json(path, manifest)
    if status in {"completed", "partial", "failed", "cancelled", "stopped"}:
        if manifest.get("followup_plan") and any(
            (root / "proposals" / "center-profiles" / run_id).glob("*.json")
        ):
            from evaluate_followup_effectiveness import evaluate as evaluate_followup_effectiveness
            from evaluate_followup_effectiveness import record as record_followup_effectiveness
            from evaluate_profile_continuity import evaluate as evaluate_profile_continuity
            from evaluate_profile_continuity import record as record_profile_continuity

            effectiveness = evaluate_followup_effectiveness(
                root,
                run_id=run_id,
                evaluated_at=manifest["completed_at"],
            )
            record_followup_effectiveness(root, effectiveness)
            continuity = evaluate_profile_continuity(
                root,
                run_id=run_id,
                evaluated_at=manifest["completed_at"],
            )
            record_profile_continuity(root, continuity)
        from evaluate_temporal_integrity import evaluate as evaluate_temporal_integrity
        from evaluate_temporal_integrity import record as record_temporal_integrity

        report = evaluate_temporal_integrity(
            root,
            run_id=run_id,
            evaluated_at=manifest["completed_at"],
        )
        return record_temporal_integrity(root, report)
    return manifest


def _cancel_run(
    root: Path,
    *,
    run_id: str,
    reason: str,
    actor: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    if not reason.strip() or not actor.strip():
        raise ValueError("Run cancellation requires a reason and actor")
    manifest_path = root / "runs" / run_id / "manifest.json"
    manifest = read_json(manifest_path)
    if manifest.get("status") == "cancelled":
        return manifest
    if manifest.get("status") in {"completed", "partial", "failed", "stopped"}:
        raise RuntimeError(f"cannot cancel terminal Run: {run_id}")
    timestamp = isoformat(now)
    cancellation = {
        "reason": reason.strip(),
        "actor": actor.strip(),
        "recorded_at": timestamp,
    }
    counts: dict[str, int] = {}
    items: list[dict[str, Any]] = []
    for path, item in _queue_items(root, run_id):
        if item.get("status") in {"queued", "leased"}:
            item["status"] = "cancelled"
            item["cancellation"] = cancellation
            item["updated_at"] = timestamp
            item.pop("lease", None)
            atomic_write_json(path, item)
        counts[item["status"]] = counts.get(item["status"], 0) + 1
        items.append(item)
    manifest["status"] = "cancelled"
    manifest["completed_at"] = timestamp
    manifest["cancellation"] = cancellation
    manifest["cost"] = _usage_summary(items)
    manifest.setdefault("metrics", {}).update(
        {"work_items_total": len(items), "work_items_by_status": counts}
    )
    atomic_write_json(manifest_path, manifest)
    return manifest


def _run_control(
    root: Path, run_id: str, operation: Any, **kwargs: Any
) -> Any:
    lock = _lock_path(root, run_id, "run-control")
    try:
        descriptor = _acquire_lock(lock)
    except FileExistsError as exc:
        raise RuntimeError(f"another Run control operation is active: {run_id}") from exc
    try:
        return operation(root, run_id=run_id, **kwargs)
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
    return _run_control(
        root,
        run_id,
        _lease_next,
        agent_id=agent_id,
        lease_seconds=lease_seconds,
        allow_disabled_pilot_agent=allow_disabled_pilot_agent,
        now=now,
    )


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
    return _run_control(
        root,
        run_id,
        _complete_work_item,
        work_item_id=work_item_id,
        agent_id=agent_id,
        output_refs=output_refs,
        usage=usage,
        now=now,
    )


def cancel_run(
    root: Path,
    *,
    run_id: str,
    reason: str,
    actor: str,
    now: datetime | None = None,
) -> dict[str, Any]:
    return _run_control(
        root,
        run_id,
        _cancel_run,
        reason=reason,
        actor=actor,
        now=now,
    )


def expand_followups(
    root: Path, *, run_id: str, now: datetime | None = None
) -> dict[str, Any]:
    return _run_control(root, run_id, _expand_followups, now=now)


def reconcile_agent_executions(root: Path, *, run_id: str) -> dict[str, Any]:
    return _run_control(root, run_id, _reconcile_agent_executions)


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
    return _run_control(
        root,
        run_id,
        _fail_work_item,
        work_item_id=work_item_id,
        agent_id=agent_id,
        error_kind=error_kind,
        error_message=error_message,
        retryable=retryable,
        now=now,
    )


def finalize_run(
    root: Path, *, run_id: str, now: datetime | None = None
) -> dict[str, Any]:
    return _run_control(root, run_id, _finalize_run, now=now)


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

    cancel = commands.add_parser("cancel")
    cancel.add_argument("--run-id", required=True)
    cancel.add_argument("--reason", required=True)
    cancel.add_argument("--actor", required=True)

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
    elif args.command == "cancel":
        result = cancel_run(
            args.root,
            run_id=args.run_id,
            reason=args.reason,
            actor=args.actor,
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
