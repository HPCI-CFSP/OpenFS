#!/usr/bin/env python3
"""Detect loss of still-current Center Profile knowledge between follow-up Runs."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json


ROOT = Path(__file__).resolve().parents[1]
STATE_STRENGTH = {"unknown": 0, "partial": 1, "verified": 2, "not-applicable": 2}
DATE_ONLY_TIMEZONE_GRACE_DAYS = 1


def _evaluation_time(value: str | None) -> tuple[str, date]:
    parsed = (
        datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
        if value
        else datetime.now(timezone.utc)
    )
    return isoformat(parsed), parsed.date()


def _profiles(root: Path, run_id: str) -> dict[str, tuple[str, dict[str, Any]]]:
    profiles: dict[str, tuple[str, dict[str, Any]]] = {}
    for path in sorted((root / "proposals" / "center-profiles" / run_id).glob("*.json")):
        profile = read_json(path)
        center_id = profile["center_id"]
        if center_id in profiles:
            raise ValueError(f"duplicate Center Profile in Run {run_id}: {center_id}")
        profiles[center_id] = (str(path.relative_to(root)), profile)
    return profiles


def _pinned(root: Path, manifest: dict[str, Any], source_ref: str) -> dict[str, Any]:
    snapshot_ref = manifest.get("configuration_snapshots", {}).get(source_ref)
    if not snapshot_ref:
        raise ValueError(f"Run does not snapshot required configuration: {source_ref}")
    return read_json(root / snapshot_ref)


def evaluate(
    root: Path, *, run_id: str, evaluated_at: str | None = None
) -> dict[str, Any]:
    manifest = read_json(root / "runs" / run_id / "manifest.json")
    followup = manifest.get("followup_plan")
    if not followup:
        raise ValueError("Profile continuity requires a consumed follow-up plan")
    predecessor_run_id = followup["base_run_id"]
    predecessor_manifest = read_json(root / "runs" / predecessor_run_id / "manifest.json")
    if (
        predecessor_manifest.get("task_id") != manifest.get("task_id")
        or predecessor_manifest.get("monitor_id") != manifest.get("monitor_id")
    ):
        raise ValueError("predecessor Run differs in task or monitor identity")
    monitor_ref = next(
        ref for ref in manifest["policy_hashes"] if ref.startswith("config/monitors/")
    )
    monitor = _pinned(root, manifest, monitor_ref)
    maximum_age_days = int(monitor.get("profile_max_age_days", 90))
    registry = _pinned(root, manifest, monitor["subject_registry_ref"])
    default_fields = registry.get("default_profile_fields", [])
    fields_by_center = {
        item["center_id"]: item.get("profile_fields", default_fields)
        for item in registry.get("centers", [])
    }
    evaluated_timestamp, evaluated_date = _evaluation_time(evaluated_at)
    predecessor_profiles = _profiles(root, predecessor_run_id)
    current_profiles = _profiles(root, run_id)
    regressions: list[dict[str, Any]] = []
    compared_field_count = 0

    for center_id, (predecessor_ref, predecessor) in sorted(predecessor_profiles.items()):
        current_entry = current_profiles.get(center_id)
        if not current_entry:
            regressions.append(
                {
                    "center_id": center_id,
                    "field": None,
                    "reason": "missing-profile",
                    "predecessor_status": None,
                    "current_status": None,
                    "predecessor_ref": predecessor_ref,
                    "current_ref": None,
                }
            )
            continue
        current_ref, current = current_entry
        for field in fields_by_center.get(center_id, default_fields):
            predecessor_value = predecessor.get(field, {})
            predecessor_status = predecessor_value.get("status", "unknown")
            predecessor_as_of = predecessor_value.get("as_of")
            if predecessor_status == "unknown" or not predecessor_as_of:
                continue
            age_days = (evaluated_date - date.fromisoformat(predecessor_as_of)).days
            if age_days < -DATE_ONLY_TIMEZONE_GRACE_DAYS or age_days > maximum_age_days:
                continue
            compared_field_count += 1
            current_status = current.get(field, {}).get("status", "unknown")
            if STATE_STRENGTH.get(current_status, -1) < STATE_STRENGTH[predecessor_status]:
                regressions.append(
                    {
                        "center_id": center_id,
                        "field": field,
                        "reason": "weaker-current-state",
                        "predecessor_status": predecessor_status,
                        "current_status": current_status,
                        "predecessor_ref": predecessor_ref,
                        "current_ref": current_ref,
                    }
                )

    status = "failed" if regressions else "passed"
    return {
        "schema_version": "0.1.0",
        "run_id": run_id,
        "predecessor_run_id": predecessor_run_id,
        "evaluated_at": evaluated_timestamp,
        "status": status,
        "publication_blocked": status == "failed",
        "maximum_age_days": maximum_age_days,
        "predecessor_profile_count": len(predecessor_profiles),
        "current_profile_count": len(current_profiles),
        "compared_field_count": compared_field_count,
        "regression_count": len(regressions),
        "regressions": regressions,
    }


def record(root: Path, report: dict[str, Any]) -> dict[str, Any]:
    run_id = report["run_id"]
    report_ref = f"runs/{run_id}/profile-continuity.json"
    atomic_write_json(root / report_ref, report)
    manifest_path = root / "runs" / run_id / "manifest.json"
    manifest = read_json(manifest_path)
    manifest["profile_continuity_ref"] = report_ref
    manifest.setdefault("metrics", {})["profile_continuity"] = {
        "status": report["status"],
        "regression_count": report["regression_count"],
        "publication_blocked": report["publication_blocked"],
    }
    atomic_write_json(manifest_path, manifest)
    exception_path = root / "reviews" / "exceptions" / run_id / "PROFILE-CONTINUITY.json"
    if report["status"] == "failed":
        atomic_write_json(
            exception_path,
            {
                "schema_version": "0.1.0",
                "exception_id": f"EXC-{run_id}-PROFILE-CONTINUITY",
                "run_id": run_id,
                "status": "open",
                "recorded_at": report["evaluated_at"],
                "exception_kind": "profile-continuity",
                "report_ref": report_ref,
                "regression_count": report["regression_count"],
                "publication_blocked": True,
                "requires_owner_action": True,
            },
        )
    elif exception_path.is_file():
        exception = read_json(exception_path)
        exception["status"] = "resolved"
        exception["resolved_at"] = report["evaluated_at"]
        exception["publication_blocked"] = False
        atomic_write_json(exception_path, exception)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--evaluated-at")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = evaluate(args.root, run_id=args.run_id, evaluated_at=args.evaluated_at)
    record(args.root, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
