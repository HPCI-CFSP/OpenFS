#!/usr/bin/env python3
"""Recompute benchmark aggregates and assess eligibility for independent review."""

from __future__ import annotations

import argparse
import json
import math
import statistics
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:  # pragma: no cover
    Draft202012Validator = None
    FormatChecker = None


TOLERANCE = 1e-9
ENERGY_GAPS = {"GAP-COMP-004", "GAP-MEM003"}
FAILURE_GAPS = {"GAP-COMP-004", "GAP-MEM003", "GAP-PORT-006"}


def _close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=TOLERANCE, abs_tol=TOLERANCE)


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def evaluate(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    gap_refs = set(bundle["roadmap_gap_refs"])
    acceptance = bundle["acceptance"]
    workload_tolerance = bundle["workload"]["correctness_tolerance"]
    if acceptance["maximum_correctness_error"] > workload_tolerance:
        errors.append("acceptance: correctness threshold cannot exceed workload tolerance")
    correctness_threshold = min(acceptance["maximum_correctness_error"], workload_tolerance)
    configurations = bundle["configurations"]
    config_ids = [item["configuration_id"] for item in configurations]
    known_configs = set(config_ids)
    if len(config_ids) != len(known_configs):
        errors.append("configurations: configuration_id values must be unique")

    run_ids: set[str] = set()
    repetitions: set[tuple[str, int]] = set()
    valid_by_config: dict[str, list[dict[str, Any]]] = {item: [] for item in known_configs}
    for run in bundle["runs"]:
        run_id = run["run_id"]
        if run_id in run_ids:
            errors.append(f"{run_id}: duplicate run_id")
        run_ids.add(run_id)
        config_id = run["configuration_id"]
        repetition = (config_id, run["repetition"])
        if repetition in repetitions:
            errors.append(f"{run_id}: duplicate repetition for {config_id}")
        repetitions.add(repetition)
        if config_id not in known_configs:
            errors.append(f"{run_id}: unknown configuration_id {config_id}")
            continue
        if _parse_time(run["ended_at"]) <= _parse_time(run["started_at"]):
            errors.append(f"{run_id}: ended_at must follow started_at")
        expected_pass = run["correctness_error"] <= correctness_threshold
        if run["correctness_pass"] != expected_pass:
            errors.append(f"{run_id}: correctness_pass disagrees with the declared threshold")
        if run["success"] and run["correctness_pass"]:
            valid_by_config[config_id].append(run)

    counts = {
        "configurations": len(known_configs),
        "institutions": len({item["institution_id"] for item in configurations}),
        "origin_groups": len({item["origin_group_id"] for item in configurations}),
        "runs": len(bundle["runs"]),
        "valid_runs": sum(len(items) for items in valid_by_config.values()),
    }
    for key, minimum_key in (
        ("configurations", "minimum_configurations"),
        ("institutions", "minimum_institutions"),
        ("origin_groups", "minimum_origin_groups"),
    ):
        if counts[key] < acceptance[minimum_key]:
            errors.append(f"{key}: {counts[key]} is below {acceptance[minimum_key]}")
    for config_id in sorted(known_configs):
        if len(valid_by_config[config_id]) < acceptance["minimum_runs_per_configuration"]:
            errors.append(
                f"{config_id}: {len(valid_by_config[config_id])} valid runs is below "
                f"{acceptance['minimum_runs_per_configuration']}"
            )

    aggregates = {item["configuration_id"]: item for item in bundle["aggregates"]}
    if len(aggregates) != len(bundle["aggregates"]):
        errors.append("aggregates: configuration_id values must be unique")
    if set(aggregates) != known_configs:
        errors.append("aggregates: must cover every and only declared configuration")
    require_energy = bool(gap_refs & ENERGY_GAPS)
    if require_energy and len({item["measurement_boundary"] for item in configurations}) > 1:
        errors.append("configurations: energy measurement boundaries must match")
    for config_id, runs in valid_by_config.items():
        if require_energy and any(run["energy_joules"] is None for run in runs):
            errors.append(f"{config_id}: every valid run requires system energy for selected Gap")
        aggregate = aggregates.get(config_id)
        if aggregate is None or not runs:
            continue
        expected_elapsed = statistics.median(run["elapsed_seconds"] for run in runs)
        energies = [run["energy_joules"] for run in runs if run["energy_joules"] is not None]
        expected_energy = statistics.median(energies) if len(energies) == len(runs) else None
        if aggregate["valid_run_count"] != len(runs):
            errors.append(f"{config_id}: valid_run_count is not reproducible")
        if not _close(aggregate["median_elapsed_seconds"], expected_elapsed):
            errors.append(f"{config_id}: median_elapsed_seconds is not reproducible")
        if expected_energy is None:
            if aggregate["median_energy_joules"] is not None:
                errors.append(f"{config_id}: median_energy_joules must be null")
        elif aggregate["median_energy_joules"] is None or not _close(
            aggregate["median_energy_joules"], expected_energy
        ):
            errors.append(f"{config_id}: median_energy_joules is not reproducible")

    trials_by_config: dict[str, list[dict[str, Any]]] = {item: [] for item in known_configs}
    for trial in bundle["failure_recovery_trials"]:
        config_id = trial["configuration_id"]
        if config_id not in known_configs:
            errors.append(f"{trial['trial_id']}: unknown configuration_id {config_id}")
            continue
        trials_by_config[config_id].append(trial)
        if trial["recovered"] and trial["recovery_seconds"] is None:
            errors.append(f"{trial['trial_id']}: recovered trial requires recovery_seconds")
        if not trial["recovered"] and trial["recovery_seconds"] is not None:
            errors.append(f"{trial['trial_id']}: unrecovered trial requires null recovery_seconds")
    if gap_refs & FAILURE_GAPS:
        for config_id in sorted(known_configs):
            if not trials_by_config[config_id]:
                errors.append(f"{config_id}: failure/recovery trial required for selected Gap")
            elif not any(
                trial["detected"] and trial["recovered"] and trial["correct_result"]
                for trial in trials_by_config[config_id]
            ):
                errors.append(f"{config_id}: no successful detection/recovery/correctness trial")

    porting_ids = [item["configuration_id"] for item in bundle["porting_records"]]
    porting_configs = set(porting_ids)
    if any(config_id not in known_configs for config_id in porting_ids):
        errors.append("porting_records: unknown configuration_id")
    if len(porting_ids) != len(porting_configs):
        errors.append("porting_records: configuration_id values must be unique")
    if "GAP-PORT-004" in gap_refs and porting_configs != known_configs:
        errors.append("porting_records: must cover every configuration for GAP-PORT-004")

    if "GAP-PORT-006" in gap_refs:
        mpi_implementations = {item["software"]["mpi"] for item in configurations}
        providers = {item["software"]["fabric_provider"] for item in configurations}
        if len(mpi_implementations) < 2:
            errors.append("GAP-PORT-006: at least two MPI implementations are required")
        if len(providers) < 2:
            errors.append("GAP-PORT-006: at least two fabric providers are required")

    return {
        "bundle_id": bundle["bundle_id"],
        "roadmap_gap_refs": bundle["roadmap_gap_refs"],
        "counts": counts,
        "calculation_errors": errors,
        "candidate_ready_for_consensus": not errors,
        "consensus_status": bundle["consensus_status"],
        "gaps_remain_open": True,
        "note": (
            "Validator success only makes the bundle eligible for independent Consensus review; "
            "it never closes a Coverage Gap."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.bundle.read_text(encoding="utf-8"))
    if Draft202012Validator is None:
        parser.error("jsonschema is required; install requirements-validation.txt")
    schema_path = Path(__file__).resolve().parents[1] / "schemas" / "benchmark-result-bundle.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema_errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload),
        key=lambda item: list(item.path),
    )
    if schema_errors:
        for error in schema_errors:
            location = "/".join(str(item) for item in error.absolute_path) or "$"
            print(f"{location}: {error.message}")
        return 1
    result = evaluate(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["candidate_ready_for_consensus"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
