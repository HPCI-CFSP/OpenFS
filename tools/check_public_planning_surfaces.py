#!/usr/bin/env python3
"""Validate cross-artifact invariants for public HPCI planning surfaces."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    from .check_performance_model_card import evaluate as evaluate_performance_model_card
    from .estimate_system_cost import five_year_known_cost_floor
except ImportError:  # pragma: no cover - direct script execution
    from check_performance_model_card import evaluate as evaluate_performance_model_card
    from estimate_system_cost import five_year_known_cost_floor


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SCALES = [1, 4, 32, 128, 1024, 10000]
EXPECTED_INFRASTRUCTURE_DIMENSIONS = [
    "compute-throughput",
    "memory-capacity-bandwidth",
    "scale-up-interconnect",
    "scale-out-interconnect",
    "storage-io",
    "workflow-latency",
    "software-portability",
    "data-governance",
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def quarter_ordinal(boundary: dict[str, Any]) -> int:
    return boundary["year"] * 4 + int(boundary["quarter"][1]) - 1


def duplicate_values(values: list[str]) -> list[str]:
    return sorted({value for value in values if values.count(value) > 1})


def validate_source_corrections(sources: list[dict[str, Any]]) -> list[str]:
    """Keep metadata revisions traceable without deleting earlier source records."""
    errors = []
    source_ids = {source["source_id"] for source in sources}
    predecessors = {}
    successors = {}
    for source in sources:
        correction = source.get("correction")
        if correction is None:
            continue
        sid = source["source_id"]
        previous = correction.get("supersedes_source_id")
        if previous not in source_ids:
            errors.append(f"{sid} corrects an unknown source: {previous}")
        if previous == sid:
            errors.append(f"{sid} cannot correct itself")
        if previous in successors:
            errors.append(f"source correction forks at {previous}")
        successors[previous] = sid
        predecessors[sid] = previous
        if any(not isinstance(correction.get(key), str) or not correction[key].strip()
               for key in ("reason_ja", "reason_en")):
            errors.append(f"{sid} lacks bilingual source correction reasons")
    for start in predecessors:
        seen = set()
        current = start
        while current in predecessors:
            if current in seen:
                errors.append(f"cyclic source correction involving {start}")
                break
            seen.add(current)
            current = predecessors[current]
    return errors


def validate_topic_decision_support(root: Path) -> list[str]:
    """Validate cross-references and publication semantics not expressible in JSON Schema."""
    path = root / "knowledge/public/topic-decision-support.json"
    if not path.exists():
        return []
    errors: list[str] = []
    artifact = load_json(path)
    baseline = load_json(root / "config/research-baseline.json")
    topic_ids = {item["topic_id"] for item in baseline["topics"]}
    retired_topic_ids = {
        item["topic_id"] for item in baseline["topics"] if item.get("retirement")
    }
    partial_topic_ids = {
        item["topic_id"]
        for item in baseline["topics"]
        if item["status"] == "partial" and item["topic_id"] not in retired_topic_ids
    }
    source_ids = {item["source_id"] for item in artifact["sources"]}
    errors.extend(validate_source_corrections(artifact["sources"]))
    superseded_source_ids = {
        item["correction"]["supersedes_source_id"]
        for item in artifact["sources"] if item.get("correction")
    }
    region_ids = {item["region_id"] for item in artifact["regions"]}
    actor_ids = {item["actor_id"] for item in artifact["actors"]}
    gaps = {item["gap_id"]: item for item in artifact["coverage_gaps"]}

    def check_duplicates(label: str, values: list[str]) -> None:
        if duplicates := duplicate_values(values):
            errors.append(f"duplicate {label}: {duplicates}")

    def check_sources(label: str, refs: list[str], *, historical: bool = False) -> None:
        if unknown := set(refs) - source_ids:
            errors.append(f"{label} has unknown sources {sorted(unknown)}")
        if not historical and (superseded := set(refs) & superseded_source_ids):
            errors.append(f"{label} uses superseded source metadata {sorted(superseded)}")

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
                check_sources(item["item_id"], item["source_ids"], historical=(
                    section["section_id"] in profile.get("archived_section_ids", [])
                    or profile["topic_id"] in retired_topic_ids))

        stages = {
            item["stage"]
            for section in profile["sections"]
            if section["section_id"] not in profile.get("archived_section_ids", [])
            for item in section["items"]
        }
        if set(profile.get("archived_section_ids", [])) - {s["section_id"] for s in profile["sections"]}:
            errors.append(f"{profile['topic_id']} archives a missing section")
        if "current" not in stages:
            errors.append(f"{profile['topic_id']} lacks a current-state item")
        if not stages & {"near-term", "research", "contested"}:
            errors.append(f"{profile['topic_id']} lacks a future or unresolved item")
        if not profile["coverage_gap_ids"]:
            errors.append(f"{profile['topic_id']} lacks an explicit Coverage Gap")

    check_duplicates("topic profile IDs", profile_ids)
    check_duplicates("topic decision section IDs", section_ids)
    check_duplicates("topic decision item IDs", technology_item_ids)
    active_profile_ids = set(profile_ids) - retired_topic_ids
    if active_profile_ids != partial_topic_ids:
        errors.append(
            "active topic decision profiles must exactly cover active partial catalog Topics; "
            f"missing={sorted(partial_topic_ids - active_profile_ids)}, "
            f"extra={sorted(active_profile_ids - partial_topic_ids)}"
        )
    specialized = next((item for item in artifact["topic_profiles"] if item["topic_id"] == "ARCH-12"), None)
    if specialized and not any(
        "MN-Core" in item["name_en"]
        for section in specialized["sections"]
        for item in section["items"]
    ):
        errors.append("ARCH-12 must include MN-Core")

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


def validate_inventory_links(inventory: dict, register: dict, roadmaps: list[dict]) -> list[str]:
    """Keep lifecycle dates in roadmaps and procurement amounts in the register."""
    errors = []
    systems = {system["system_id"] for system in inventory["systems"]}
    milestones = {(roadmap["roadmap_id"], milestone["milestone_id"])
                  for roadmap in roadmaps for lane in roadmap["lanes"]
                  for milestone in lane["milestones"]}
    for case in register["cases"]:
        if unknown := set(case.get("linked_system_ids", [])) - systems:
            errors.append(f"{case['case_id']} links unknown HPCI systems: {sorted(unknown)}")
    for system in inventory["systems"]:
        if note := system.get("performance_note"):
            source_ids = {source["source_id"] for source in inventory["sources"]}
            if not note.get("source_ids") or set(note["source_ids"]) - source_ids:
                errors.append(f"{system['system_id']} performance note needs registered sources")
            if not note.get("note_ja", "").strip() or not note.get("note_en", "").strip():
                errors.append(f"{system['system_id']} performance note needs both languages")
        for ref in system.get("lifecycle_milestone_refs", []):
            if (ref["roadmap_id"], ref["milestone_id"]) not in milestones:
                errors.append(f"{system['system_id']} links unknown lifecycle milestone: {ref}")
    source_ids = {source["source_id"] for source in inventory["sources"]}
    observation_ids = [item["observation_id"] for item in inventory["operational_observations"]]
    product_ids = [item["product_id"] for item in inventory["operational_data_products"]]
    if duplicates := duplicate_values(observation_ids + product_ids):
        errors.append(f"duplicate HPCI operational evidence IDs: {duplicates}")
    for item in [*inventory["operational_observations"], *inventory["operational_data_products"]]:
        item_id = item.get("observation_id", item.get("product_id"))
        if unknown := set(item["system_ids"]) - systems:
            errors.append(f"{item_id} links unknown HPCI systems: {sorted(unknown)}")
        if unknown := set(item["source_ids"]) - source_ids:
            errors.append(f"{item_id} has unknown sources: {sorted(unknown)}")
    for item in inventory["operational_observations"]:
        value = item["value"]
        if value["kind"] in {"exact", "approximate"}:
            if value["value"] is None or value["lower"] is not None or value["upper"] is not None:
                errors.append(f"{item['observation_id']} has an invalid scalar operational value")
        elif (value["value"] is not None or value["lower"] is None or value["upper"] is None
              or value["lower"] > value["upper"]):
            errors.append(f"{item['observation_id']} has an invalid operational range")
    return errors


def validate(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    center_registry = load_json(root / "config/hpci-center-registry.json")
    inventory = load_json(root / "knowledge/public/hpci-system-inventory.json")
    forecasts = load_json(root / "knowledge/public/application-performance-forecasts.json")
    register_path = root / "knowledge/public/procurement-cost-register.json"
    register = None
    if register_path.exists():
        register = load_json(register_path)
        roadmaps = [load_json(path) for path in sorted((root / "knowledge/public/roadmaps").glob("*.json"))]
        errors.extend(validate_inventory_links(inventory, register, roadmaps))

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

    measured_platform_ids = [item["platform_id"] for item in forecasts["measured_platforms"]]
    if duplicates := duplicate_values(measured_platform_ids):
        errors.append(f"duplicate measured platform IDs: {duplicates}")
    known_measured_platform_ids = set(measured_platform_ids)
    for platform in forecasts["measured_platforms"]:
        if unknown := set(platform["source_ids"]) - forecast_source_ids:
            errors.append(f"{platform['platform_id']} has unknown sources {sorted(unknown)}")

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

    known_observation_ids = set(observation_ids)
    observations = {
        item["observation_id"]: item for item in forecasts["baseline_observations"]
    }
    cross_observation_ids = [
        item["observation_id"] for item in forecasts["cross_platform_observations"]
    ]
    if duplicates := duplicate_values(cross_observation_ids):
        errors.append(f"duplicate cross-platform observation IDs: {duplicates}")
    for observation in forecasts["cross_platform_observations"]:
        item_id = observation["observation_id"]
        if observation["application_id"] not in known_application_ids:
            errors.append(f"{item_id} references unknown application")
        if observation["platform_id"] not in known_measured_platform_ids:
            errors.append(f"{item_id} references unknown measured platform")
        if unknown := set(observation["source_ids"]) - forecast_source_ids:
            errors.append(f"{item_id} has unknown sources {sorted(unknown)}")

    requirement_ids = [item["requirement_id"] for item in forecasts["quantitative_requirements"]]
    if duplicates := duplicate_values(requirement_ids):
        errors.append(f"duplicate quantitative requirement IDs: {duplicates}")
    covered_requirements = set()
    for requirement in forecasts["quantitative_requirements"]:
        item_id = requirement["requirement_id"]
        covered_requirements.add(requirement["application_id"])
        if requirement["application_id"] not in known_application_ids:
            errors.append(f"{item_id} references unknown application")
        if unknown := set(requirement["source_ids"]) - forecast_source_ids:
            errors.append(f"{item_id} has unknown sources {sorted(unknown)}")
        numeric = [requirement[key] for key in ("lower", "value", "upper")]
        if requirement["evidence_class"] == "measurement-gap":
            if any(value is not None for value in numeric) or requirement["unit"] is not None:
                errors.append(f"{item_id} fills a measurement gap with an unsupported number")
        elif requirement["unit"] is None or all(value is None for value in numeric):
            errors.append(f"{item_id} lacks a measured or published numerical basis")
        if (requirement["lower"] is not None and requirement["upper"] is not None
                and requirement["lower"] > requirement["upper"]):
            errors.append(f"{item_id} has a reversed range")
    if covered_requirements != known_application_ids:
        errors.append("quantitative requirements must cover every declared application")
    calibration_candidate_ids = [
        item["calibration_candidate_id"]
        for item in forecasts["calibration_candidates"]
    ]
    if duplicates := duplicate_values(calibration_candidate_ids):
        errors.append(f"duplicate calibration-candidate IDs: {duplicates}")
    for calibration in forecasts["calibration_candidates"]:
        item_id = calibration["calibration_candidate_id"]
        if calibration["application_id"] not in known_application_ids:
            errors.append(
                f"{item_id} references unknown application {calibration['application_id']}"
            )
        unknown_sources = set(calibration["source_ids"]) - forecast_source_ids
        if unknown_sources:
            errors.append(f"{item_id} has unknown sources {sorted(unknown_sources)}")
        calibration_ids = set(calibration["calibration_observation_ids"])
        validation_ids = {
            item["observation_id"] for item in calibration["validation_results"]
        }
        if unknown := (calibration_ids | validation_ids) - known_observation_ids:
            errors.append(f"{item_id} has unknown observations {sorted(unknown)}")
        if overlap := calibration_ids & validation_ids:
            errors.append(f"{item_id} reuses calibration data for validation: {sorted(overlap)}")
        relative_errors = []
        for result in calibration["validation_results"]:
            observation = observations.get(result["observation_id"])
            if observation is None:
                continue
            if observation["application_id"] != calibration["application_id"]:
                errors.append(
                    f"{item_id} validates an observation from another application"
                )
            if observation["status"] != "measured":
                errors.append(f"{item_id} validates a non-measured observation")
            if observation["unit"] != calibration["unit"]:
                errors.append(f"{item_id} mixes validation units")
            if abs(result["observed_value"] - observation["value"]) > 1e-9:
                errors.append(f"{item_id} does not preserve the observed value")
            expected_absolute = abs(
                result["predicted_value"] - result["observed_value"]
            )
            if abs(result["absolute_error"] - expected_absolute) > 1e-6:
                errors.append(f"{item_id} has an inconsistent absolute error")
            expected_relative = (
                expected_absolute / result["observed_value"]
                if result["observed_value"] else 0
            )
            if abs(result["relative_error"] - expected_relative) > 1e-6:
                errors.append(f"{item_id} has an inconsistent relative error")
            relative_errors.append(result["relative_error"])
        if relative_errors and abs(
            calibration["maximum_relative_error"] - max(relative_errors)
        ) > 1e-9:
            errors.append(f"{item_id} has an inconsistent maximum relative error")
        readiness = calibration["readiness"]
        if all(
            readiness["observed_counts"][key] >= readiness["required_minimums"][key]
            for key in readiness["required_minimums"]
        ):
            errors.append(f"{item_id} is labeled unready despite meeting every minimum")
        if (
            readiness["candidate_ready_for_consensus"]
            or calibration["consensus_status"] != "incomplete"
            or calibration["procurement_eligible"]
        ):
            errors.append(
                f"{item_id} must remain unready, Consensus-incomplete, and procurement-ineligible"
            )

    infrastructure = forecasts["infrastructure_requirements_matrix"]
    dimension_ids = [item["dimension_id"] for item in infrastructure["dimensions"]]
    if dimension_ids != EXPECTED_INFRASTRUCTURE_DIMENSIONS:
        errors.append(
            "application infrastructure dimensions must be stable and in the declared order"
        )
    row_ids = [item["application_id"] for item in infrastructure["rows"]]
    if duplicates := duplicate_values(row_ids):
        errors.append(f"duplicate application infrastructure rows: {duplicates}")
    if set(row_ids) != known_application_ids:
        errors.append(
            "application infrastructure matrix must cover every declared application exactly once"
        )
    for row in infrastructure["rows"]:
        cell_ids = [item["dimension_id"] for item in row["cells"]]
        if cell_ids != EXPECTED_INFRASTRUCTURE_DIMENSIONS:
            errors.append(
                f"{row['application_id']} infrastructure cells must cover every dimension in order"
            )
        for cell in row["cells"]:
            if unknown := set(cell["source_ids"]) - forecast_source_ids:
                errors.append(
                    f"{row['application_id']} {cell['dimension_id']} has unknown sources "
                    f"{sorted(unknown)}"
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

    illustration_ids = [item["illustration_id"] for item in forecasts["illustrations"]]
    if duplicates := duplicate_values(illustration_ids):
        errors.append(f"duplicate performance-illustration IDs: {duplicates}")
    legacy_forecast_ids = [
        item["legacy_forecast_id"] for item in forecasts["illustrations"]
    ]
    if duplicates := duplicate_values(legacy_forecast_ids):
        errors.append(f"duplicate legacy forecast IDs: {duplicates}")
    for illustration in forecasts["illustrations"]:
        item_id = illustration["illustration_id"]
        if illustration["application_id"] not in known_application_ids:
            errors.append(
                f"{item_id} references unknown application "
                f"{illustration['application_id']}"
            )
        if illustration["fugaku_nodes"] not in EXPECTED_SCALES:
            errors.append(
                f"{item_id} uses a non-standard Fugaku scale"
            )
        if illustration["candidate_system_id"] not in known_candidate_system_ids:
            errors.append(
                f"{item_id} references unknown candidate system "
                f"{illustration['candidate_system_id']}"
            )
        if illustration["model_card_id"] != forecasts["model_contract"]["model_card_id"]:
            errors.append(f"{item_id} references an unknown model card")
        unknown_assumptions = (
            set(illustration["assumption_ids"]) - known_assumption_ids
        )
        if unknown_assumptions:
            errors.append(
                f"{item_id} has unknown assumptions "
                f"{sorted(unknown_assumptions)}"
            )
        unknown_sources = set(illustration["basis_source_ids"]) - forecast_source_ids
        if unknown_sources:
            errors.append(
                f"{item_id} has unknown basis sources "
                f"{sorted(unknown_sources)}"
            )
        estimate = illustration["estimate"]
        if not estimate["lower"] <= estimate["base"] <= estimate["upper"]:
            errors.append(
                f"{item_id} estimate must satisfy lower <= base <= upper"
            )
        if (
            illustration["confidence"] != "low"
            or illustration["consensus_status"] != "incomplete"
            or illustration["procurement_eligible"]
        ):
            errors.append(
                f"{item_id} must remain low-confidence, Consensus-incomplete, "
                "and procurement-ineligible"
            )
        if len(illustration["assumption_ids"]) == 1 and model_limit_ratio is not None:
            assumption = assumptions.get(illustration["assumption_ids"][0])
            if assumption and assumption["application_id"] == illustration["application_id"]:
                fraction = assumption["accelerator_eligible_fraction"]
                local_speedup = 1 / ((1 - fraction) + fraction / model_limit_ratio)
                retention = next(
                    (
                        item["factor"]
                        for item in assumption["scale_retention"]
                        if item["fugaku_nodes"] == illustration["fugaku_nodes"]
                    ),
                    None,
                )
                if retention is not None:
                    expected_base = local_speedup * retention
                    if abs(estimate["base"] - expected_base) > 0.11:
                        errors.append(
                            f"{item_id} base estimate is not reproducible "
                            "from the declared model"
                        )
                    if abs(estimate["lower"] - expected_base * 0.5) > 0.11:
                        errors.append(
                            f"{item_id} lower bound is not the declared 0.5x"
                        )
                    if abs(estimate["upper"] - expected_base * 1.5) > 0.11:
                        errors.append(
                            f"{item_id} upper bound is not the declared 1.5x"
                        )

    illustration_cells = [
        (item["application_id"], item["fugaku_nodes"])
        for item in forecasts["illustrations"]
    ]
    if duplicates := duplicate_values(
        [f"{app}:{scale}" for app, scale in illustration_cells]
    ):
        errors.append(f"duplicate application-scale illustrations: {duplicates}")
    expected_cells = {
        (application_id, scale)
        for application_id in known_application_ids
        for scale in EXPECTED_SCALES
    }
    missing_cells = expected_cells - set(illustration_cells)
    if missing_cells:
        errors.append(
            "legacy illustrations must cover every declared application-scale cell: "
            f"{sorted(missing_cells)}"
        )

    validated_model_card_ids = [
        item["model_card_id"] for item in forecasts["validated_model_cards"]
    ]
    if duplicates := duplicate_values(validated_model_card_ids):
        errors.append(f"duplicate validated performance-model card IDs: {duplicates}")
    validated_model_cards = {
        item["model_card_id"]: item for item in forecasts["validated_model_cards"]
    }
    for model_card in forecasts["validated_model_cards"]:
        model_card_id = model_card["model_card_id"]
        result = evaluate_performance_model_card(model_card)
        if not result["candidate_ready_for_consensus"]:
            errors.append(
                f"{model_card_id} fails deterministic performance-model validation: "
                f"{result['calculation_errors']}"
            )
        if (
            model_card["status"] != "accepted"
            or model_card["consensus_status"] != "accepted"
        ):
            errors.append(
                f"{model_card_id} must be accepted by independent Consensus before "
                "supporting a formal forecast"
            )

    forecast_ids = [item["forecast_id"] for item in forecasts["forecasts"]]
    if duplicates := duplicate_values(forecast_ids):
        errors.append(f"duplicate forecast IDs: {duplicates}")
    if overlapping_ids := set(forecast_ids) & set(legacy_forecast_ids):
        errors.append(
            "formal forecast IDs must not reuse legacy forecast IDs: "
            f"{sorted(overlapping_ids)}"
        )
    for forecast in forecasts["forecasts"]:
        item_id = forecast["forecast_id"]
        if forecast["application_id"] not in known_application_ids:
            errors.append(
                f"{item_id} references unknown application "
                f"{forecast['application_id']}"
            )
        if forecast["fugaku_nodes"] not in EXPECTED_SCALES:
            errors.append(f"{item_id} uses a non-standard Fugaku scale")
        if forecast["candidate_system_id"] not in known_candidate_system_ids:
            errors.append(
                f"{item_id} references unknown candidate system "
                f"{forecast['candidate_system_id']}"
            )
        model_card = validated_model_cards.get(forecast["model_card_id"])
        if model_card is None:
            errors.append(
                f"{item_id} references a model card that is not validated and "
                "Consensus-accepted"
            )
        unknown_assumptions = set(forecast["assumption_ids"]) - known_assumption_ids
        if unknown_assumptions:
            errors.append(
                f"{item_id} has unknown assumptions {sorted(unknown_assumptions)}"
            )
        unknown_sources = set(forecast["basis_source_ids"]) - forecast_source_ids
        if unknown_sources:
            errors.append(
                f"{item_id} has unknown basis sources {sorted(unknown_sources)}"
            )
        estimate = forecast["estimate"]
        if not estimate["lower"] <= estimate["base"] <= estimate["upper"]:
            errors.append(
                f"{item_id} estimate must satisfy lower <= base <= upper"
            )
        if set(forecast["calibration_dataset_ids"]) & set(
            forecast["validation_dataset_ids"]
        ):
            errors.append(f"{item_id} reuses calibration data for validation")
        if model_card is not None:
            card_calibration_ids = set(model_card["calibration_dataset_ids"])
            card_validation_ids = {
                item["dataset_id"] for item in model_card["validations"]
            }
            if not set(forecast["calibration_dataset_ids"]).issubset(
                card_calibration_ids
            ):
                errors.append(
                    f"{item_id} uses calibration data absent from its model card"
                )
            if not set(forecast["validation_dataset_ids"]).issubset(
                card_validation_ids
            ):
                errors.append(
                    f"{item_id} uses validation data absent from its model card"
                )
        if (
            forecast["forecast_class"] != "validated"
            or not forecast["calibration_dataset_ids"]
            or not forecast["validation_dataset_ids"]
            or forecast["confidence"] not in {"medium", "high"}
            or forecast["consensus_status"] != "accepted"
        ):
            errors.append(
                f"{item_id} must be calibrated, independently validated, "
                "Consensus-accepted, and at least medium confidence"
            )

    if forecasts["model_contract"]["procurement_use"] == "validated":
        if forecasts["consensus_status"] != "accepted" or not forecasts["forecasts"]:
            errors.append(
                "procurement use requires accepted Consensus and published forecasts"
            )

    readiness_path = root / "knowledge/public/planning-evidence-readiness.json"
    if readiness_path.exists() and register is not None:
        readiness = load_json(readiness_path)
        dimension_ids = [item["dimension_id"] for item in readiness["dimensions"]]
        expected_dimension_ids = [
            "system-lifecycle", "operations", "five-year-cost",
            "application-performance", "quantitative-requirements",
        ]
        if dimension_ids != expected_dimension_ids:
            errors.append("planning evidence dimensions must use the stable declared order")
        dimensions = {item["dimension_id"]: item for item in readiness["dimensions"]}
        milestone_records = {
            (roadmap["roadmap_id"], milestone["milestone_id"]): milestone
            for roadmap in roadmaps
            for lane in roadmap["lanes"]
            for milestone in lane["milestones"]
        }
        future_lifecycle_systems = {
            system["system_id"]
            for system in inventory["systems"]
            if any(
                milestone_records[(ref["roadmap_id"], ref["milestone_id"])][
                    "timing_basis"
                ]
                == "project-target"
                and milestone_records[(ref["roadmap_id"], ref["milestone_id"])][
                    "year"
                ]
                is not None
                for ref in system.get("lifecycle_milestone_refs", [])
            )
        }
        observed_lifecycle_systems = {
            system["system_id"]
            for system in inventory["systems"]
            if any(
                milestone_records[(ref["roadmap_id"], ref["milestone_id"])][
                    "timing_basis"
                ]
                == "observed"
                for ref in system.get("lifecycle_milestone_refs", [])
            )
        }
        operational_systems = {
            system_id
            for item in [
                *inventory["operational_observations"],
                *inventory["operational_data_products"],
            ]
            for system_id in item["system_ids"]
        }
        observations_by_metric = {
            metric: {
                system_id
                for item in inventory["operational_observations"]
                if item["metric"] in metrics
                for system_id in item["system_ids"]
            }
            for metric, metrics in {
                "utilization": {"utilization"},
                "power": {"design-power", "operating-power"},
                "availability-downtime": {
                    "system-availability",
                    "scheduled-maintenance",
                    "unplanned-downtime",
                    "service-hours",
                },
                "jobs-history": {"job-count"},
            }.items()
        }
        observations_by_metric["jobs-history"].update(
            system_id
            for item in inventory["operational_data_products"]
            if item["product_type"] == "public-dataset"
            for system_id in item["system_ids"]
        )
        actual_coverage = {
            "system-lifecycle": len(future_lifecycle_systems),
            "operations": len(operational_systems),
            "five-year-cost": len([
                item for item in register["cases"] if five_year_known_cost_floor(item)
            ]),
            "application-performance": len({
                item["application_id"] for item in forecasts["cross_platform_observations"]
            }),
            "quantitative-requirements": len({
                item["application_id"] for item in forecasts["quantitative_requirements"]
                if item["evidence_class"] != "measurement-gap"
            }),
        }
        expected_denominators = {
            "system-lifecycle": len(inventory["systems"]),
            "operations": len(inventory["systems"]),
            "five-year-cost": len(register["cases"]),
            "application-performance": len(forecasts["applications"]),
            "quantitative-requirements": len(forecasts["applications"]),
        }
        for dimension_id in expected_dimension_ids:
            coverage = dimensions[dimension_id]["coverage"]
            if coverage["numerator"] != actual_coverage[dimension_id]:
                errors.append(f"{dimension_id} planning evidence numerator is stale")
            if coverage["denominator"] != expected_denominators[dimension_id]:
                errors.append(f"{dimension_id} planning evidence denominator is stale")
        expected_supporting = {
            "system-lifecycle": {
                "observed-start": len(observed_lifecycle_systems),
                "any-lifecycle": sum(
                    bool(item.get("lifecycle_milestone_refs"))
                    for item in inventory["systems"]
                ),
            },
            "operations": {
                key: len(value) for key, value in observations_by_metric.items()
            },
            "five-year-cost": {
                "complete-tco": sum(
                    case["five_year_cost_assessment"]["complete_tco"]
                    for case in register["cases"]
                ),
                "public-total": sum(
                    case.get("amount") is not None for case in register["cases"]
                ),
                "component-itemization": sum(
                    bool(case["itemized_costs"]) for case in register["cases"]
                ),
            },
            "application-performance": {},
            "quantitative-requirements": {},
        }
        for dimension_id, expected in expected_supporting.items():
            rows = dimensions[dimension_id]["supporting_coverages"]
            actual = {row["coverage_id"]: row for row in rows}
            if set(actual) != set(expected):
                errors.append(f"{dimension_id} supporting coverage IDs are stale")
                continue
            for coverage_id, numerator in expected.items():
                if actual[coverage_id]["numerator"] != numerator:
                    errors.append(
                        f"{dimension_id}:{coverage_id} numerator is stale"
                    )
                if (
                    actual[coverage_id]["denominator"]
                    != expected_denominators[dimension_id]
                ):
                    errors.append(
                        f"{dimension_id}:{coverage_id} denominator is stale"
                    )
        scenario_payload = load_json(root / "roadmaps/scenarios/accepted/hpci-p0-scenarios.json")
        known_scenarios = {item["scenario_id"] for item in scenario_payload["scenarios"]}
        assessed_scenarios = {item["scenario_id"] for item in readiness["scenario_assessments"]}
        if assessed_scenarios != known_scenarios:
            errors.append("planning evidence readiness must assess every published scenario")
        if readiness["consensus_status"] != "incomplete" or readiness["research_status"] != "provisional":
            errors.append("planning evidence readiness must remain provisional and Consensus-incomplete")
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
