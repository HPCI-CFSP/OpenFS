#!/usr/bin/env python3
"""Recompute performance-model validation errors and assess review readiness."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:  # pragma: no cover - production validation installs requirements-validation.txt
    Draft202012Validator = None
    FormatChecker = None


TOLERANCE = 1e-9


def _close(left: float, right: float) -> bool:
    return math.isclose(left, right, rel_tol=TOLERANCE, abs_tol=TOLERANCE)


def evaluate(card: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if card["applicability"]["scale_max"] <= card["applicability"]["scale_min"]:
        errors.append("applicability: scale_max must be greater than scale_min")
    input_ids = [item["quantity_id"] for item in card["inputs"]]
    output_ids = [item["quantity_id"] for item in card["outputs"]]
    if len(input_ids) != len(set(input_ids)):
        errors.append("inputs: quantity_id values must be unique")
    if len(output_ids) != len(set(output_ids)):
        errors.append("outputs: quantity_id values must be unique")
    output_units = {item["quantity_id"]: item["unit"] for item in card["outputs"]}
    thresholds = {
        item["output_id"]: item["maximum_relative_error"]
        for item in card["acceptance"]["metric_thresholds"]
    }
    threshold_ids = [item["output_id"] for item in card["acceptance"]["metric_thresholds"]]
    if len(threshold_ids) != len(set(threshold_ids)):
        errors.append("acceptance: output thresholds must be unique")
    for output_id in output_ids:
        if output_id not in thresholds:
            errors.append(f"acceptance: no threshold declared for {output_id}")
    for output_id in thresholds:
        if output_id not in output_units:
            errors.append(f"acceptance: threshold refers to unknown output {output_id}")
    calibration_ids = set(card["calibration_dataset_ids"])
    systems: set[str] = set()
    workloads: set[str] = set()
    origin_groups: set[str] = set()

    for item in card["validations"]:
        measurement_id = item["measurement_id"]
        systems.add(item["system_id"])
        workloads.add(item["workload_id"])
        origin_groups.add(item["origin_group_id"])
        if item["dataset_id"] in calibration_ids:
            errors.append(f"{measurement_id}: validation dataset overlaps calibration")
        output_id = item["output_id"]
        if output_id not in output_units:
            errors.append(f"{measurement_id}: unknown output_id {output_id}")
            continue
        if item["unit"] != output_units[output_id]:
            errors.append(f"{measurement_id}: unit disagrees with {output_id}")
        absolute_error = abs(item["predicted"] - item["observed"])
        if not _close(item["absolute_error"], absolute_error):
            errors.append(f"{measurement_id}: absolute_error is not reproducible")
        relative_error = None if item["observed"] == 0 else absolute_error / abs(item["observed"])
        if relative_error is None:
            if item["relative_error"] is not None:
                errors.append(f"{measurement_id}: relative_error must be null for zero observation")
        elif item["relative_error"] is None or not _close(item["relative_error"], relative_error):
            errors.append(f"{measurement_id}: relative_error is not reproducible")
        threshold = thresholds.get(output_id)
        if threshold is None:
            errors.append(f"{measurement_id}: no acceptance threshold for {output_id}")
        elif relative_error is None or relative_error > threshold + TOLERANCE:
            errors.append(f"{measurement_id}: relative_error exceeds acceptance threshold")

    acceptance = card["acceptance"]
    counts = {
        "systems": len(systems),
        "workloads": len(workloads),
        "origin_groups": len(origin_groups),
        "measurements": len(card["validations"]),
    }
    for key, minimum_key in (
        ("systems", "minimum_systems"),
        ("workloads", "minimum_workloads"),
        ("origin_groups", "minimum_origin_groups"),
    ):
        if counts[key] < acceptance[minimum_key]:
            errors.append(f"{key}: {counts[key]} is below {acceptance[minimum_key]}")

    candidate_ready = not errors
    return {
        "model_card_id": card["model_card_id"],
        "roadmap_gap_ref": "GAP-WORK-003",
        "counts": counts,
        "calculation_errors": errors,
        "candidate_ready_for_consensus": candidate_ready,
        "consensus_status": card["consensus_status"],
        "gap_remains_open": True,
        "note": (
            "Validator success only makes the card eligible for independent Consensus review; "
            "it never closes the Coverage Gap."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("card", type=Path)
    args = parser.parse_args()
    card = json.loads(args.card.read_text(encoding="utf-8"))
    if Draft202012Validator is None:
        parser.error("jsonschema is required; install requirements-validation.txt")
    schema_path = Path(__file__).resolve().parents[1] / "schemas" / "performance-model-card.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema_errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(card),
        key=lambda item: list(item.path),
    )
    if schema_errors:
        for error in schema_errors:
            location = "/".join(str(item) for item in error.absolute_path) or "$"
            print(f"{location}: {error.message}")
        return 1
    result = evaluate(card)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["candidate_ready_for_consensus"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
