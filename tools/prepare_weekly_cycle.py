#!/usr/bin/env python3
"""Prepare a deterministic weekly OpenFS coordination plan and Issue payload."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json
from evaluate_monitor_readiness import evaluate as evaluate_monitor_readiness


ROOT = Path(__file__).resolve().parents[1]
WEEK = re.compile(r"^[0-9]{4}-W[0-9]{2}$")
MONITOR_ID = re.compile(r"^MON-[A-Z0-9-]+$")


def _last_run(root: Path, monitor_id: str) -> dict[str, Any] | None:
    candidates = []
    for path in sorted((root / "runs").glob("RUN-*/manifest.json")):
        manifest = read_json(path)
        if manifest.get("monitor_id") == monitor_id:
            candidates.append(manifest)
    return max(candidates, key=lambda item: item.get("started_at", "")) if candidates else None


def _pending_directives(root: Path, task_id: str) -> list[str]:
    result = []
    for path in sorted((root / "reviews" / "directives").glob("DIR-*.json")):
        directive = read_json(path)
        if directive.get("status") not in {"approved", "scheduled"}:
            continue
        if task_id in directive.get("scope", []):
            result.append(directive["directive_id"])
    return result


def build_plan(
    root: Path,
    *,
    week: str,
    monitor_ids: list[str] | None = None,
    pilot: bool = False,
    generated_at: str | None = None,
) -> dict[str, Any]:
    if not WEEK.fullmatch(week):
        raise ValueError(f"invalid ISO week: {week}")
    requested = set(monitor_ids or [])
    if any(not MONITOR_ID.fullmatch(item) for item in requested):
        raise ValueError("invalid monitor ID")
    timestamp = generated_at or isoformat()
    monitors = []
    blockers = []
    known = set()
    for path in sorted((root / "config" / "monitors").glob("*.json")):
        monitor = read_json(path)
        monitor_id = monitor["monitor_id"]
        known.add(monitor_id)
        if requested and monitor_id not in requested:
            continue
        if not monitor.get("enabled") and not (pilot and monitor_id in requested):
            continue
        previous = _last_run(root, monitor_id)
        run_suffix = monitor_id.removeprefix("MON-")
        production_readiness = None
        if not pilot:
            production_readiness = evaluate_monitor_readiness(
                root,
                monitor_id=monitor_id,
                evaluated_at=timestamp,
            )
            if production_readiness["status"] != "ready":
                blockers.append(f"monitor-not-production-ready:{monitor_id}")
        plan = {
            "monitor_id": monitor_id,
            "task_id": monitor["task_id"],
            "mode": "pilot" if pilot else "production",
            "suggested_run_id": f"RUN-{week.replace('-', '')}-{run_suffix}",
            "previous_run_id": previous.get("run_id") if previous else None,
            "previous_run_status": previous.get("status") if previous else None,
            "pending_directive_ids": _pending_directives(root, monitor["task_id"]),
        }
        if production_readiness:
            plan["production_readiness"] = production_readiness
        monitors.append(plan)
    unknown = sorted(requested - known)
    if unknown:
        raise ValueError(f"unknown monitor IDs: {unknown}")

    if not monitors:
        blockers.append("no-eligible-monitors")
    if (root / "state" / "STOP").exists():
        blockers.append("repository-kill-switch")
    cycle_id = f"CYCLE-{week}"
    marker = f"<!-- openfs-weekly-cycle:{cycle_id} -->"
    lines = [
        marker,
        "",
        f"OpenFS weekly coordination plan for `{week}`.",
        "",
        "This Issue contains identifiers and control status only. It does not contain Web excerpts.",
        "",
        f"- Cycle: `{cycle_id}`",
        f"- Status: `{'blocked' if blockers else 'ready'}`",
        f"- Mode: `{'pilot' if pilot else 'production'}`",
    ]
    if blockers:
        lines.append("- Blockers: " + ", ".join(f"`{item}`" for item in blockers))
    lines.extend(["", "## Monitor plans", ""])
    if monitors:
        for monitor in monitors:
            lines.append(
                f"- `{monitor['monitor_id']}` / `{monitor['task_id']}` -> "
                f"`{monitor['suggested_run_id']}`; previous: "
                f"`{monitor['previous_run_id'] or 'none'}`; readiness: "
                f"`{monitor.get('production_readiness', {}).get('status', 'pilot')}`"
            )
    else:
        lines.append("- None.")
    lines.extend(
        [
            "",
            "A research Worker may claim this cycle only after re-running repository, budget, "
            "information-boundary, and Consensus-capacity preflights.",
            "The Worker must create a branch and pull request; it must not push to `main`, "
            "accept its own findings, or publish candidate artifacts.",
        ]
    )
    return {
        "schema_version": "0.1.0",
        "cycle_id": cycle_id,
        "week": week,
        "generated_at": timestamp,
        "mode": "pilot" if pilot else "production",
        "status": "blocked" if blockers else "ready",
        "blockers": blockers,
        "monitors": monitors,
        "issue": {
            "title": f"[OpenFS] Weekly research cycle {week}",
            "body": "\n".join(lines),
            "labels": ["openfs-weekly-cycle"],
            "deduplication_marker": marker,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--week", required=True)
    parser.add_argument("--monitor-id", action="append")
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--generated-at")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    plan = build_plan(
        args.root,
        week=args.week,
        monitor_ids=args.monitor_id,
        pilot=args.pilot,
        generated_at=args.generated_at,
    )
    output = args.output if args.output.is_absolute() else args.root / args.output
    atomic_write_json(output, plan)
    print(json.dumps({"output": str(output), "status": plan["status"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
