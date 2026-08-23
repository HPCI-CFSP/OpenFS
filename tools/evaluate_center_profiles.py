#!/usr/bin/env python3
"""Measure accepted, current, field-level HPCI center profile coverage."""

from __future__ import annotations

import argparse
import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json


ROOT = Path(__file__).resolve().parents[1]
COMPLETE_FIELD_STATES = {"verified", "not-applicable"}


def _date(value: str) -> date:
    return date.fromisoformat(value)


def _evaluation_date(value: str | None) -> tuple[str, date]:
    if value:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
            timezone.utc
        )
        return isoformat(parsed), parsed.date()
    now = datetime.now(timezone.utc)
    return isoformat(now), now.date()


def _pinned(root: Path, manifest: dict[str, Any], source_ref: str) -> dict[str, Any]:
    snapshot_ref = manifest.get("configuration_snapshots", {}).get(source_ref)
    if not snapshot_ref:
        raise ValueError(f"Run does not snapshot required configuration: {source_ref}")
    return read_json(root / snapshot_ref)


def evaluate(
    root: Path, *, run_id: str, evaluated_at: str | None = None
) -> dict[str, Any]:
    manifest = read_json(root / "runs" / run_id / "manifest.json")
    monitor_ref = next(
        ref for ref in manifest["policy_hashes"] if ref.startswith("config/monitors/")
    )
    monitor = _pinned(root, manifest, monitor_ref)
    registry_ref = monitor.get("subject_registry_ref")
    if not registry_ref:
        raise ValueError("Center profile coverage requires a subject_registry_ref")
    registry = _pinned(root, manifest, registry_ref)
    evaluated_timestamp, evaluated_date = _evaluation_date(evaluated_at)
    maximum_age_days = int(monitor.get("profile_max_age_days", 90))
    default_fields = registry.get("default_profile_fields", [])
    centers = {center["center_id"]: center for center in registry.get("centers", [])}

    profiles: dict[str, dict[str, Any]] = {}
    duplicate_profiles: list[str] = []
    for path in sorted(
        (root / "proposals" / "center-profiles" / run_id).glob("*.json")
    ):
        profile = read_json(path)
        center_id = profile.get("center_id")
        if center_id in profiles:
            duplicate_profiles.append(center_id)
        profiles[center_id] = profile

    missing_profiles = sorted(set(centers) - set(profiles))
    unexpected_profiles = sorted(set(profiles) - set(centers))
    non_accepted_profiles: list[dict[str, str]] = []
    stale_profiles: list[dict[str, Any]] = []
    field_gaps: list[dict[str, Any]] = []
    accepted_current = 0
    evidence_complete = 0
    profile_results: list[dict[str, Any]] = []
    for center_id, center in sorted(centers.items()):
        profile = profiles.get(center_id)
        if not profile:
            continue
        required_fields = center.get("profile_fields", default_fields)
        missing_fields: list[str] = []
        partial_fields: list[str] = []
        stale_fields: list[str] = []
        for field in required_fields:
            value = profile.get(field, {})
            status = value.get("status", "unknown")
            evidence_refs = value.get("evidence_refs", [])
            as_of = value.get("as_of")
            if status not in COMPLETE_FIELD_STATES or not evidence_refs or not as_of:
                if status == "partial":
                    partial_fields.append(field)
                else:
                    missing_fields.append(field)
                continue
            age_days = (evaluated_date - _date(as_of)).days
            if age_days < 0 or age_days > maximum_age_days:
                stale_fields.append(field)
        complete = not missing_fields and not partial_fields and not stale_fields
        if complete:
            evidence_complete += 1
        if profile.get("profile_status") != "accepted":
            non_accepted_profiles.append(
                {
                    "center_id": center_id,
                    "profile_status": profile.get("profile_status", "missing"),
                }
            )
        profile_age_days = (evaluated_date - _date(profile["evidence_as_of"])).days
        if profile_age_days < 0 or profile_age_days > maximum_age_days:
            stale_profiles.append(
                {"center_id": center_id, "age_days": profile_age_days}
            )
        if missing_fields or partial_fields or stale_fields:
            field_gaps.append(
                {
                    "center_id": center_id,
                    "missing_fields": missing_fields,
                    "partial_fields": partial_fields,
                    "stale_fields": stale_fields,
                }
            )
        current_and_accepted = (
            complete
            and profile.get("profile_status") == "accepted"
            and 0 <= profile_age_days <= maximum_age_days
        )
        accepted_current += int(current_and_accepted)
        profile_results.append(
            {
                "center_id": center_id,
                "profile_status": profile.get("profile_status"),
                "profile_age_days": profile_age_days,
                "field_evidence_complete": complete,
                "accepted_current": current_and_accepted,
            }
        )

    gaps = {
        "missing_profiles": missing_profiles,
        "unexpected_profiles": unexpected_profiles,
        "duplicate_profiles": sorted(set(duplicate_profiles)),
        "non_accepted_profiles": non_accepted_profiles,
        "stale_profiles": stale_profiles,
        "field_gaps": field_gaps,
    }
    status = (
        "accepted-current"
        if accepted_current == len(centers) and not any(gaps.values())
        else "incomplete"
    )
    return {
        "schema_version": "0.1.0",
        "run_id": run_id,
        "monitor_id": manifest["monitor_id"],
        "evaluated_at": evaluated_timestamp,
        "profile_coverage_status": status,
        "expected": {
            "registry_id": registry["registry_id"],
            "center_count": len(centers),
            "profile_max_age_days": maximum_age_days,
            "required_profile_status": "accepted",
            "complete_field_states": sorted(COMPLETE_FIELD_STATES),
        },
        "observed": {
            "profile_count": len(profiles),
            "field_evidence_complete_count": evidence_complete,
            "accepted_current_count": accepted_current,
            "profiles": profile_results,
        },
        "gaps": gaps,
        "caveat": (
            "Complete profile coverage means every registered center has current, "
            "field-level Evidence and accepted status. It does not by itself establish "
            "that a proposed HPCI-wide scenario is feasible or preferred."
        ),
    }


def record(root: Path, report: dict[str, Any]) -> dict[str, Any]:
    manifest_path = root / "runs" / report["run_id"] / "manifest.json"
    manifest = read_json(manifest_path)
    report_ref = f"runs/{report['run_id']}/center-profile-coverage.json"
    manifest["center_profile_coverage_ref"] = report_ref
    manifest.setdefault("metrics", {})["center_profile_coverage"] = {
        "status": report["profile_coverage_status"],
        "profile_count": report["observed"]["profile_count"],
        "accepted_current_count": report["observed"]["accepted_current_count"],
        "expected_center_count": report["expected"]["center_count"],
    }
    atomic_write_json(manifest_path, manifest)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--evaluated-at")
    args = parser.parse_args()
    report = evaluate(args.root, run_id=args.run_id, evaluated_at=args.evaluated_at)
    output = args.root / "runs" / args.run_id / "center-profile-coverage.json"
    atomic_write_json(output, report)
    record(args.root, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
