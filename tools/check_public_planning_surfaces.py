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


def validate_topic_decision_support(root: Path) -> list[str]:
    """Validate cross-references and publication semantics not expressible in JSON Schema."""
    path = root / "knowledge/public/topic-decision-support.json"
    if not path.exists():
        return []
    errors: list[str] = []
    artifact = load_json(path)
    baseline = load_json(root / "config/research-baseline.json")
    topic_ids = {item["topic_id"] for item in baseline["topics"]}
    partial_topic_ids = {
        item["topic_id"] for item in baseline["topics"] if item["status"] == "partial"
    }
    source_ids = {item["source_id"] for item in artifact["sources"]}
    region_ids = {item["region_id"] for item in artifact["regions"]}
    actor_ids = {item["actor_id"] for item in artifact["actors"]}
    gaps = {item["gap_id"]: item for item in artifact["coverage_gaps"]}

    def check_duplicates(label: str, values: list[str]) -> None:
        if duplicates := duplicate_values(values):
            errors.append(f"duplicate {label}: {duplicates}")

    def check_sources(label: str, refs: list[str]) -> None:
        if unknown := set(refs) - source_ids:
            errors.append(f"{label} has unknown sources {sorted(unknown)}")

    check_duplicates("topic decision source IDs", [item["source_id"] for item in artifact["sources"]])
    check_duplicates("topic decision region IDs", [item["region_id"] for item in artifact["regions"]])
    check_duplicates("topic decision actor IDs", [item["actor_id"] for item in artifact["actors"]])
    check_duplicates("topic decision gap IDs", list(gaps))

    for actor in artifact["actors"]:
        if unknown := set(actor["region_ids"]) - region_ids:
            errors.append(f"{actor['actor_id']} has unknown regions {sorted(unknown)}")
        if len(actor["roles_ja"]) != len(actor["roles_en"]):
            errors.append(f"{actor['actor_id']} has unpaired bilingual roles")
        check_sources(actor["actor_id"], actor["source_ids"])

    profile_ids: list[str] = []
    section_ids: list[str] = []
    technology_item_ids: list[str] = []
    for profile in artifact["topic_profiles"]:
        profile_ids.append(profile["topic_id"])
        if profile["topic_id"] not in topic_ids:
            errors.append(f"topic profile references unknown Topic {profile['topic_id']}")
        for gap_id in profile["coverage_gap_ids"]:
            gap = gaps.get(gap_id)
            if not gap:
                errors.append(f"{profile['topic_id']} references unknown gap {gap_id}")
            elif profile["topic_id"] not in gap["topic_ids"]:
                errors.append(f"{gap_id} does not include profile Topic {profile['topic_id']}")
        for section in profile["sections"]:
            section_ids.append(section["section_id"])
            for item in section["items"]:
                technology_item_ids.append(item["item_id"])
                if item["consensus_status"] != "incomplete":
                    errors.append(f"{item['item_id']} must remain Consensus-incomplete")
                if len(item["adoption_conditions_ja"]) != len(item["adoption_conditions_en"]):
                    errors.append(f"{item['item_id']} has unpaired adoption conditions")
                if unknown := set(item["actor_ids"]) - actor_ids:
                    errors.append(f"{item['item_id']} has unknown actors {sorted(unknown)}")
                check_sources(item["item_id"], item["source_ids"])

        stages = {
            item["stage"]
            for section in profile["sections"]
            for item in section["items"]
        }
        if "current" not in stages:
            errors.append(f"{profile['topic_id']} lacks a current-state item")
        if not stages & {"near-term", "research", "contested"}:
            errors.append(f"{profile['topic_id']} lacks a future or unresolved item")
        if not profile["coverage_gap_ids"]:
            errors.append(f"{profile['topic_id']} lacks an explicit Coverage Gap")

    check_duplicates("topic profile IDs", profile_ids)
    check_duplicates("topic decision section IDs", section_ids)
    check_duplicates("topic decision item IDs", technology_item_ids)
    if set(profile_ids) != partial_topic_ids:
        errors.append(
            "topic decision profiles must exactly cover partial catalog Topics; "
            f"missing={sorted(partial_topic_ids - set(profile_ids))}, "
            f"extra={sorted(set(profile_ids) - partial_topic_ids)}"
        )
    arch02 = next((item for item in artifact["topic_profiles"] if item["topic_id"] == "ARCH-02"), None)
    if arch02 and not any(
        "MN-Core" in item["name_en"]
        for section in arch02["sections"]
        for item in section["items"]
    ):
        errors.append("ARCH-02 must include MN-Core")

    platforms = artifact["platform_matrix"]["platforms"]
    platform_ids = {item["platform_id"] for item in platforms}
    check_duplicates("platform IDs", [item["platform_id"] for item in platforms])
    for platform in platforms:
        if unknown := set(platform["region_ids"]) - region_ids:
            errors.append(f"{platform['platform_id']} has unknown regions {sorted(unknown)}")
        check_sources(platform["platform_id"], platform["source_ids"])
    capability_ids: list[str] = []
    software_entry_ids: list[str] = []
    for capability in artifact["platform_matrix"]["capabilities"]:
        capability_ids.append(capability["capability_id"])
        for entry in capability["entries"]:
            software_entry_ids.append(entry["entry_id"])
            if unknown := set(entry["platform_ids"]) - platform_ids:
                errors.append(f"{entry['entry_id']} has unknown platforms {sorted(unknown)}")
            check_sources(entry["entry_id"], entry["source_ids"])
    check_duplicates("platform capability IDs", capability_ids)
    check_duplicates("software capability entry IDs", software_entry_ids)

    method_ids: list[str] = []
    implementation_ids: list[str] = []
    for method in artifact["numerical_method_matrix"]["methods"]:
        method_ids.append(method["method_id"])
        for implementation in method["implementations"]:
            implementation_ids.append(implementation["implementation_id"])
            if unknown := set(implementation["platform_ids"]) - platform_ids:
                errors.append(
                    f"{implementation['implementation_id']} has unknown platforms {sorted(unknown)}"
                )
            check_sources(implementation["implementation_id"], implementation["source_ids"])
    check_duplicates("numerical method IDs", method_ids)
    check_duplicates("numerical implementation IDs", implementation_ids)

    for gap in gaps.values():
        if unknown := set(gap["topic_ids"]) - topic_ids:
            errors.append(f"{gap['gap_id']} has unknown Topics {sorted(unknown)}")
    if artifact["consensus_status"] != "incomplete" or artifact["research_status"] != "provisional":
        errors.append("topic decision support must remain provisional and Consensus-incomplete")
    return errors


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
    unknown_model_sources = set(forecasts["model_contract"]["source_ids"]) - forecast_source_ids
    if unknown_model_sources:
        errors.append(
            f"performance model contract has unknown sources {sorted(unknown_model_sources)}"
        )

    candidate_system_ids = [
        item["candidate_system_id"] for item in forecasts["candidate_systems"]
    ]
    if duplicates := duplicate_values(candidate_system_ids):
        errors.append(f"duplicate forecast candidate-system IDs: {duplicates}")
    known_candidate_system_ids = set(candidate_system_ids)
    candidate_systems = {
        item["candidate_system_id"]: item for item in forecasts["candidate_systems"]
    }
    for candidate in forecasts["candidate_systems"]:
        unknown_sources = set(candidate["source_ids"]) - forecast_source_ids
        if unknown_sources:
            errors.append(
                f"{candidate['candidate_system_id']} has unknown sources "
                f"{sorted(unknown_sources)}"
            )

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
        unknown_code_sources = (
            set(application["code_availability"]["source_ids"])
            - forecast_source_ids
        )
        if unknown_code_sources:
            errors.append(
                f"{application['application_id']} code availability has unknown sources "
                f"{sorted(unknown_code_sources)}"
            )
        for hint in application["observed_scale_hints"]:
            unknown_hint_sources = set(hint["source_ids"]) - forecast_source_ids
            if unknown_hint_sources:
                errors.append(
                    f"{application['application_id']} scale hint has unknown sources "
                    f"{sorted(unknown_hint_sources)}"
                )

    observation_ids = [
        item["observation_id"] for item in forecasts["baseline_observations"]
    ]
    if duplicates := duplicate_values(observation_ids):
        errors.append(f"duplicate baseline observation IDs: {duplicates}")
    for observation in forecasts["baseline_observations"]:
        if observation["application_id"] not in known_application_ids:
            errors.append(
                f"{observation['observation_id']} references unknown application "
                f"{observation['application_id']}"
            )
        unknown_sources = set(observation["source_ids"]) - forecast_source_ids
        if unknown_sources:
            errors.append(
                f"{observation['observation_id']} has unknown sources "
                f"{sorted(unknown_sources)}"
            )
        if observation["status"] == "measured" and (
            observation["value"] is None or observation["unit"] is None
        ):
            errors.append(
                f"{observation['observation_id']} measured observation lacks value or unit"
            )
        if observation["status"] == "unavailable" and (
            observation["value"] is not None or observation["unit"] is not None
        ):
            errors.append(
                f"{observation['observation_id']} unavailable observation must not have value or unit"
            )

    assumption_ids = [item["assumption_id"] for item in forecasts["assumptions"]]
    if duplicates := duplicate_values(assumption_ids):
        errors.append(f"duplicate performance assumption IDs: {duplicates}")
    known_assumption_ids = set(assumption_ids)
    assumptions = {item["assumption_id"]: item for item in forecasts["assumptions"]}
    for assumption in forecasts["assumptions"]:
        if assumption["application_id"] not in known_application_ids:
            errors.append(
                f"{assumption['assumption_id']} references unknown application "
                f"{assumption['application_id']}"
            )
        scales = [item["fugaku_nodes"] for item in assumption["scale_retention"]]
        if scales != EXPECTED_SCALES:
            errors.append(
                f"{assumption['assumption_id']} scale retention must match "
                f"{EXPECTED_SCALES}, in order"
            )
        unknown_sources = set(assumption["source_ids"]) - forecast_source_ids
        if unknown_sources:
            errors.append(
                f"{assumption['assumption_id']} has unknown sources "
                f"{sorted(unknown_sources)}"
            )

    baseline = candidate_systems.get("FUGAKU-A64FX-BASELINE")
    candidate = candidate_systems.get("FUGAKUNEXT-PUBLIC-DESIGN-PROXY")
    model_limit_ratio: float | None = None
    if baseline and candidate:
        baseline_metrics = {item["metric_id"]: item["value"] for item in baseline["metrics"]}
        candidate_metrics = {item["metric_id"]: item["value"] for item in candidate["metrics"]}
        required_metrics = {"node-fp64-peak", "node-memory-bandwidth"}
        if required_metrics <= baseline_metrics.keys() and required_metrics <= candidate_metrics.keys():
            model_limit_ratio = min(
                candidate_metrics["node-fp64-peak"] / baseline_metrics["node-fp64-peak"],
                candidate_metrics["node-memory-bandwidth"]
                / baseline_metrics["node-memory-bandwidth"],
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
        if forecast["candidate_system_id"] not in known_candidate_system_ids:
            errors.append(
                f"{forecast['forecast_id']} references unknown candidate system "
                f"{forecast['candidate_system_id']}"
            )
        unknown_assumptions = set(forecast["assumption_ids"]) - known_assumption_ids
        if unknown_assumptions:
            errors.append(
                f"{forecast['forecast_id']} has unknown assumptions "
                f"{sorted(unknown_assumptions)}"
            )
        unknown_sources = set(forecast["basis_source_ids"]) - forecast_source_ids
        if unknown_sources:
            errors.append(
                f"{forecast['forecast_id']} has unknown basis sources "
                f"{sorted(unknown_sources)}"
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
        if forecast["forecast_class"] == "analytical-provisional":
            if (
                forecast["confidence"] != "low"
                or forecast["consensus_status"] != "incomplete"
                or forecast["procurement_eligible"]
                or forecast["calibration_dataset_ids"]
                or forecast["validation_dataset_ids"]
            ):
                errors.append(
                    f"{forecast['forecast_id']} analytical forecast must remain "
                    "low-confidence, unvalidated, and procurement-ineligible"
                )
            if len(forecast["assumption_ids"]) == 1 and model_limit_ratio is not None:
                assumption = assumptions.get(forecast["assumption_ids"][0])
                if assumption and assumption["application_id"] == forecast["application_id"]:
                    fraction = assumption["accelerator_eligible_fraction"]
                    local_speedup = 1 / ((1 - fraction) + fraction / model_limit_ratio)
                    retention = next(
                        (
                            item["factor"]
                            for item in assumption["scale_retention"]
                            if item["fugaku_nodes"] == forecast["fugaku_nodes"]
                        ),
                        None,
                    )
                    if retention is not None:
                        expected_base = local_speedup * retention
                        if abs(estimate["base"] - expected_base) > 0.11:
                            errors.append(
                                f"{forecast['forecast_id']} base estimate is not reproducible "
                                "from the declared model"
                            )
                        if abs(estimate["lower"] - expected_base * 0.5) > 0.11:
                            errors.append(
                                f"{forecast['forecast_id']} lower bound is not the declared 0.5x"
                            )
                        if abs(estimate["upper"] - expected_base * 1.5) > 0.11:
                            errors.append(
                                f"{forecast['forecast_id']} upper bound is not the declared 1.5x"
                            )

    forecast_cells = [
        (item["application_id"], item["fugaku_nodes"])
        for item in forecasts["forecasts"]
    ]
    if duplicates := duplicate_values([f"{app}:{scale}" for app, scale in forecast_cells]):
        errors.append(f"duplicate application-scale forecasts: {duplicates}")
    expected_cells = {
        (application_id, scale)
        for application_id in known_application_ids
        for scale in EXPECTED_SCALES
    }
    missing_cells = expected_cells - set(forecast_cells)
    if missing_cells:
        errors.append(
            "application forecasts must cover every declared application-scale cell: "
            f"{sorted(missing_cells)}"
        )

    if forecasts["model_contract"]["procurement_use"] == "validated":
        if forecasts["consensus_status"] != "accepted" or not forecasts["forecasts"]:
            errors.append(
                "procurement use requires accepted Consensus and published forecasts"
            )
    errors.extend(validate_topic_decision_support(root))
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
