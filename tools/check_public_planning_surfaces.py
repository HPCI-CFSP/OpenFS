#!/usr/bin/env python3
"""Validate cross-artifact invariants for public HPCI planning surfaces."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SCALES = [1, 4, 32, 128, 1024, 10000]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def quarter_ordinal(boundary: dict[str, Any]) -> int:
    return boundary["year"] * 4 + int(boundary["quarter"][1]) - 1


def duplicate_values(values: list[str]) -> list[str]:
    return sorted({value for value in values if values.count(value) > 1})


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    center_registry = load_json(root / "config/hpci-center-registry.json")
    inventory = load_json(root / "knowledge/public/hpci-system-inventory.json")
    forecasts = load_json(root / "knowledge/public/application-performance-forecasts.json")

    center_ids = {center["center_id"] for center in center_registry["centers"]}
    inventory_source_ids = {source["source_id"] for source in inventory["sources"]}
    system_ids = [system["system_id"] for system in inventory["systems"]]
    if duplicates := duplicate_values(system_ids):
        errors.append(f"duplicate HPCI system IDs: {duplicates}")
    window_ids: list[str] = []
    for system in inventory["systems"]:
        if system["center_id"] not in center_ids:
            errors.append(
                f"{system['system_id']} references unknown center {system['center_id']}"
            )
        unknown_sources = set(system["source_ids"]) - inventory_source_ids
        if unknown_sources:
            errors.append(
                f"{system['system_id']} has unknown sources {sorted(unknown_sources)}"
            )
        for window in system["availability_windows"]:
            window_ids.append(window["window_id"])
            if quarter_ordinal(window["start"]) > quarter_ordinal(window["end"]):
                errors.append(f"{window['window_id']} ends before it starts")
            unknown_window_sources = set(window["source_ids"]) - inventory_source_ids
            if unknown_window_sources:
                errors.append(
                    f"{window['window_id']} has unknown sources "
                    f"{sorted(unknown_window_sources)}"
                )
    if duplicates := duplicate_values(window_ids):
        errors.append(f"duplicate HPCI availability-window IDs: {duplicates}")

    if forecasts["standard_fugaku_node_scales"] != EXPECTED_SCALES:
        errors.append(
            "application forecast standard scales must be "
            f"{EXPECTED_SCALES}, in order"
        )
    primary_metrics = set(forecasts["metric_policy"]["primary_metric_ids"])
    secondary_metrics = set(forecasts["metric_policy"]["secondary_metric_ids"])
    if "achieved-flops" in primary_metrics or "achieved-flops" not in secondary_metrics:
        errors.append("achieved-flops must remain a secondary metric")

    forecast_source_ids = {source["source_id"] for source in forecasts["sources"]}
    application_ids = [item["application_id"] for item in forecasts["applications"]]
    if duplicates := duplicate_values(application_ids):
        errors.append(f"duplicate forecast application IDs: {duplicates}")
    known_application_ids = set(application_ids)
    for application in forecasts["applications"]:
        scales = [item["fugaku_nodes"] for item in application["scale_readiness"]]
        if scales != EXPECTED_SCALES:
            errors.append(
                f"{application['application_id']} scale readiness must match "
                f"{EXPECTED_SCALES}, in order"
            )
        unknown_sources = set(application["source_ids"]) - forecast_source_ids
        if unknown_sources:
            errors.append(
                f"{application['application_id']} has unknown sources "
                f"{sorted(unknown_sources)}"
            )
        for hint in application["observed_scale_hints"]:
            unknown_hint_sources = set(hint["source_ids"]) - forecast_source_ids
            if unknown_hint_sources:
                errors.append(
                    f"{application['application_id']} scale hint has unknown sources "
                    f"{sorted(unknown_hint_sources)}"
                )

    forecast_ids = [item["forecast_id"] for item in forecasts["forecasts"]]
    if duplicates := duplicate_values(forecast_ids):
        errors.append(f"duplicate forecast IDs: {duplicates}")
    for forecast in forecasts["forecasts"]:
        if forecast["application_id"] not in known_application_ids:
            errors.append(
                f"{forecast['forecast_id']} references unknown application "
                f"{forecast['application_id']}"
            )
        if forecast["fugaku_nodes"] not in EXPECTED_SCALES:
            errors.append(
                f"{forecast['forecast_id']} uses a non-standard Fugaku scale"
            )
        estimate = forecast["estimate"]
        if not estimate["lower"] <= estimate["base"] <= estimate["upper"]:
            errors.append(
                f"{forecast['forecast_id']} estimate must satisfy lower <= base <= upper"
            )
        if set(forecast["calibration_dataset_ids"]) & set(
            forecast["validation_dataset_ids"]
        ):
            errors.append(
                f"{forecast['forecast_id']} reuses calibration data for validation"
            )

    if forecasts["model_contract"]["procurement_use"] == "validated":
        if forecasts["consensus_status"] != "accepted" or not forecasts["forecasts"]:
            errors.append(
                "procurement use requires accepted Consensus and published forecasts"
            )
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("Public planning surface validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Public planning surface validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
