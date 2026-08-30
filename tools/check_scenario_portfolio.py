#!/usr/bin/env python3
"""Check that published system planning options are comparable and gap-complete."""

from __future__ import annotations

import argparse
import itertools
import json
import re
from datetime import date
from pathlib import Path
from typing import Any


REQUIRED_DOMAINS = {
    "compute",
    "memory",
    "interconnect",
    "system-software",
    "applications",
}
REQUIRED_CRITERIA = {
    "application-coverage",
    "time-to-solution",
    "power-facility-fit",
    "lifecycle-cost",
    "maturity-schedule",
    "software-migration",
    "operations-security",
    "hpci-interoperability",
    "technology-origin-and-ecosystem",
    "center-fit",
    "reversibility",
}
DOMAIN_ROADMAPS = {
    "compute": "RM-HW-COMPUTE",
    "memory": "RM-HW-MEMORY",
    "interconnect": "RM-HW-INTERCONNECT",
    "system-software": "RM-SSW-PORTABILITY",
    "applications": "RM-APP-WORKLOADS",
}
DECISION_GATE_PATTERN = re.compile(r"^(\d{4}) Q([1-4]):\s+\S")
TIMELINE_DOMAINS = {
    "portfolio",
    "compute",
    "memory",
    "interconnect",
    "storage-data",
    "system-software",
    "applications",
    "facility-operations",
    "procurement-governance",
}


def _duplicates(values: list[str]) -> set[str]:
    return {value for value in values if values.count(value) > 1}


def _normalized_text(value: str | None) -> str:
    return " ".join((value or "").split()).casefold()


def _p0_gaps(roadmaps: list[dict[str, Any]]) -> set[str]:
    return {
        gap["gap_id"]
        for roadmap in roadmaps
        for gap in roadmap.get("coverage_gaps", [])
        if gap.get("priority") == "P0" and gap.get("status") == "open"
    }


def _reference_index(
    roadmaps: list[dict[str, Any]], repository_root: Path, errors: list[str]
) -> set[str]:
    references: set[str] = set()
    for roadmap in roadmaps:
        references.add(roadmap["roadmap_id"])
        references.update(source["source_id"] for source in roadmap.get("sources", []))
        references.update(gap["gap_id"] for gap in roadmap.get("coverage_gaps", []))
        references.update(
            milestone["milestone_id"]
            for lane in roadmap.get("lanes", [])
            for milestone in lane.get("milestones", [])
        )
        references.update(
            dependency["dependency_id"]
            for dependency in roadmap.get("dependencies", [])
        )

    dependency_path = (
        repository_root / "knowledge/public/dependencies/p0-roadmap-dependencies.json"
    )
    if not dependency_path.is_file():
        errors.append("scenario references: dependency register is missing")
    else:
        dependency_register = json.loads(dependency_path.read_text(encoding="utf-8"))
        references.add(dependency_register["export_id"])
        references.update(
            item["dependency_id"] for item in dependency_register.get("dependencies", [])
        )
        references.update(
            item["constraint_id"]
            for item in dependency_register.get("external_constraints", [])
        )

    for path in sorted((repository_root / "knowledge/public/audits").glob("*.json")):
        artifact = json.loads(path.read_text(encoding="utf-8"))
        if artifact.get("export_id"):
            references.add(artifact["export_id"])
    return references


def _decision_gate_periods(
    scenario_id: str, language: str, values: list[str], errors: list[str]
) -> list[tuple[int, int]]:
    periods: list[tuple[int, int]] = []
    for value in values:
        match = DECISION_GATE_PATTERN.match(value)
        if not match:
            errors.append(f"{scenario_id}: malformed {language} decision gate {value!r}")
            continue
        periods.append((int(match.group(1)), int(match.group(2))))
    if periods != sorted(set(periods)):
        errors.append(f"{scenario_id}: {language} decision gates are duplicate or out of order")
    return periods


def _quarter_ordinal(point: dict[str, Any]) -> int:
    return int(point["year"]) * 4 + int(str(point["quarter"])[1]) - 1


def _validate_implementation_path(
    scenario: dict[str, Any], known_references: set[str], errors: list[str]
) -> int:
    scenario_id = scenario["scenario_id"]
    path = scenario.get("implementation_path", {})
    start_year = path.get("start_year")
    end_year = path.get("end_year")
    if not isinstance(start_year, int) or not isinstance(end_year, int) or start_year > end_year:
        errors.append(f"{scenario_id}: invalid implementation-path horizon")
        return 0
    if path.get("timeline_granularity") != "quarter":
        errors.append(f"{scenario_id}: implementation path must use quarter granularity")

    phases = path.get("phases", [])
    phase_ids = [phase.get("phase_id") for phase in phases]
    for value in sorted(_duplicates(phase_ids)):
        errors.append(f"{scenario_id}: duplicate implementation phase {value}")
    known_phase_ids = set(phase_ids)
    domains = {phase.get("domain") for phase in phases}
    if domains != TIMELINE_DOMAINS:
        errors.append(
            f"{scenario_id}: timeline domains mismatch; "
            f"missing={sorted(TIMELINE_DOMAINS - domains)}, "
            f"extra={sorted(domains - TIMELINE_DOMAINS)}"
        )
    lower = start_year * 4
    upper = end_year * 4 + 3
    for phase in phases:
        phase_id = phase.get("phase_id", "<missing>")
        try:
            start = _quarter_ordinal(phase["start"])
            end = _quarter_ordinal(phase["end"])
        except (KeyError, TypeError, ValueError, IndexError):
            errors.append(f"{scenario_id}:{phase_id}: malformed phase timing")
            continue
        if start > end:
            errors.append(f"{scenario_id}:{phase_id}: phase ends before it starts")
        if start < lower or end > upper:
            errors.append(f"{scenario_id}:{phase_id}: phase is outside the implementation horizon")
        if phase.get("timing_basis") != "openfs-provisional-plan":
            errors.append(f"{scenario_id}:{phase_id}: phase is not labeled as an OpenFS provisional plan")
        unknown_evidence = set(phase.get("evidence_refs", [])) - known_references
        if unknown_evidence:
            errors.append(
                f"{scenario_id}:{phase_id}: unresolved phase evidence references "
                f"{sorted(unknown_evidence)}"
            )
        unknown_dependencies = set(phase.get("dependency_refs", [])) - (
            known_phase_ids | known_references
        )
        if unknown_dependencies:
            errors.append(
                f"{scenario_id}:{phase_id}: unresolved phase dependencies "
                f"{sorted(unknown_dependencies)}"
            )
    return len(phases)


def evaluate(
    scenario_set: dict[str, Any],
    roadmaps: list[dict[str, Any]],
    repository_root: Path,
    scenario_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    scenarios = scenario_set["scenarios"]
    from estimate_system_cost import allocate_budget
    budget_config = json.loads((repository_root / "config/budget-planning.json").read_text())
    budget_levels = budget_config["budget_ceilings_oku_jpy"]
    p0_gaps = _p0_gaps(roadmaps)
    known_references = _reference_index(roadmaps, repository_root, errors)
    scenario_policy = scenario_policy or {}
    minimum_candidate_differences = scenario_policy.get(
        "minimum_pairwise_candidate_domain_differences", 3
    )
    minimum_fallback_differences = scenario_policy.get(
        "minimum_pairwise_fallback_domain_differences", 3
    )
    for name, value in (
        ("minimum_pairwise_candidate_domain_differences", minimum_candidate_differences),
        ("minimum_pairwise_fallback_domain_differences", minimum_fallback_differences),
    ):
        if not isinstance(value, int) or not 1 <= value <= len(REQUIRED_DOMAINS):
            errors.append(f"scenario policy: invalid {name}={value}")

    scenario_ids = [item["scenario_id"] for item in scenarios]
    budget_references = scenario_set.get("budget_reference_cases", [])
    budget_reference_ids = [item.get("case_id") for item in budget_references]
    if len(budget_reference_ids) != len(set(budget_reference_ids)):
        errors.append("budget reference cases contain duplicate IDs")
    known_budget_references = set(budget_reference_ids)
    if len(known_budget_references) < 3:
        errors.append("at least three public budget reference cases are required")
    if len(scenarios) != 3:
        errors.append(f"scenarios: expected exactly 3, found {len(scenarios)}")
    for value in sorted(_duplicates(scenario_ids)):
        errors.append(f"scenarios: duplicate scenario_id {value}")

    candidates_by_domain: dict[str, set[str]] = {domain: set() for domain in REQUIRED_DOMAINS}
    implementation_phase_count = 0
    for scenario in scenarios:
        scenario_id = scenario["scenario_id"]
        budget_options = scenario.get("budget_options", [])
        tiers = [item.get("tier") for item in budget_options]
        if tiers != [f"jpy-{value}" for value in budget_levels]:
            errors.append(f"{scenario_id}: budget tiers must be ordered by the five numeric ceilings")
        references_by_tier: list[float] = []
        for option in budget_options:
            option_id = option.get("option_id", "unknown")
            budget_range = option.get("budget_range_oku_jpy", {})
            lower = budget_range.get("lower", -1)
            reference = budget_range.get("reference", -1)
            upper = budget_range.get("upper", -1)
            if not lower <= reference <= upper:
                errors.append(f"{scenario_id}:{option_id}: invalid budget range")
            references_by_tier.append(reference)
            try:
                expected = allocate_budget(budget_config, scenario_id, reference,
                                           budget_config["default_deployment_year"])
                if option.get("budget_allocation") != expected:
                    errors.append(f"{scenario_id}:{option_id}: budget allocation does not match config")
            except (ValueError, KeyError, TypeError) as exc:
                errors.append(f"{scenario_id}:{option_id}: invalid allocation: {exc}")
            if any(option.get("aggregate", {}).get(key) is not None
                   for key in ("cpu_nodes", "accelerator_nodes", "accelerators", "storage_pb")):
                errors.append(f"{scenario_id}:{option_id}: unvalidated system totals must remain unknown")
            unknown_budget_refs = set(option.get("reference_case_ids", [])) - known_budget_references
            if unknown_budget_refs:
                errors.append(
                    f"{scenario_id}:{option_id}: unknown budget references {sorted(unknown_budget_refs)}"
                )
            component_ids = [item.get("component_id") for item in option.get("components", [])]
            if len(component_ids) != len(set(component_ids)):
                errors.append(f"{scenario_id}:{option_id}: duplicate architecture component IDs")
            known_components = set(component_ids)
            for component_item in option.get("components", []):
                if component_item.get("quantity") is not None:
                    errors.append(f"{scenario_id}:{option_id}: unvalidated quantities must remain unknown")
                unknown_connections = set(component_item.get("connection_ids", [])) - known_components
                if unknown_connections:
                    errors.append(
                        f"{scenario_id}:{option_id}:{component_item.get('component_id')}: "
                        f"unknown connections {sorted(unknown_connections)}"
                    )
        if references_by_tier != budget_levels:
            errors.append(f"{scenario_id}: budget reference values must increase by tier")
        try:
            effective_from = date.fromisoformat(scenario["effective_from"])
            review_due = date.fromisoformat(scenario["review_due"])
            if review_due <= effective_from:
                errors.append(f"{scenario_id}: review_due must be after effective_from")
        except (KeyError, TypeError, ValueError):
            errors.append(f"{scenario_id}: invalid plan effective or review date")
        note_scopes = {note.get("scope") for note in scenario.get("context_notes", [])}
        if note_scopes != {"reusable", "hpci-specific"}:
            errors.append(
                f"{scenario_id}: context notes must distinguish reusable and HPCI-specific conditions"
            )
        for note in scenario.get("context_notes", []):
            unknown_note_refs = set(note.get("evidence_refs", [])) - known_references
            if unknown_note_refs:
                errors.append(
                    f"{scenario_id}:{note.get('note_id')}: unresolved context-note evidence "
                    f"{sorted(unknown_note_refs)}"
                )
        implementation_phase_count += _validate_implementation_path(
            scenario, known_references, errors
        )
        evaluation_keys = set(scenario.get("evaluation", {}))
        if evaluation_keys != REQUIRED_CRITERIA:
            missing = sorted(REQUIRED_CRITERIA - evaluation_keys)
            extra = sorted(evaluation_keys - REQUIRED_CRITERIA)
            errors.append(f"{scenario_id}: evaluation mismatch; missing={missing}, extra={extra}")
        scored = [
            criterion
            for criterion, value in scenario.get("evaluation", {}).items()
            if value.get("score") is not None
        ]
        if scored:
            errors.append(f"{scenario_id}: scores require approved weights; scored={sorted(scored)}")

        options = scenario.get("technology_options", [])
        option_ids = [item["option_id"] for item in options]
        for value in sorted(_duplicates(option_ids)):
            errors.append(f"{scenario_id}: duplicate option_id {value}")
        domains = {item["domain"] for item in options}
        if domains != REQUIRED_DOMAINS:
            errors.append(
                f"{scenario_id}: option domains mismatch; "
                f"missing={sorted(REQUIRED_DOMAINS - domains)}, extra={sorted(domains - REQUIRED_DOMAINS)}"
            )
        for option in options:
            candidates_by_domain.setdefault(option["domain"], set()).add(
                _normalized_text(option["candidate_en"])
            )
            expected_roadmap = DOMAIN_ROADMAPS[option["domain"]]
            option_refs = set(option.get("evidence_refs", []))
            if expected_roadmap not in option_refs:
                errors.append(
                    f"{scenario_id}:{option['option_id']}: missing domain roadmap {expected_roadmap}"
                )
            for reference in sorted(option_refs - known_references):
                errors.append(
                    f"{scenario_id}:{option['option_id']}: unresolved evidence reference {reference}"
                )

        for reference in sorted(set(scenario.get("evidence_refs", [])) - known_references):
            errors.append(f"{scenario_id}: unresolved scenario evidence reference {reference}")
        for criterion, evaluation in scenario.get("evaluation", {}).items():
            for reference in sorted(set(evaluation.get("evidence_refs", [])) - known_references):
                errors.append(
                    f"{scenario_id}:{criterion}: unresolved evaluation evidence reference {reference}"
                )

        blocker_gaps = set(scenario.get("decision_blocking_gap_refs", []))
        if blocker_gaps != p0_gaps:
            errors.append(
                f"{scenario_id}: decision blockers do not equal open P0 Gaps; "
                f"missing={sorted(p0_gaps - blocker_gaps)}, extra={sorted(blocker_gaps - p0_gaps)}"
            )
        if len(scenario.get("uncertainties", [])) != len(scenario.get("uncertainties_en", [])):
            errors.append(f"{scenario_id}: uncertainty translations are not one-to-one")
        if len(scenario.get("decision_gates", [])) != len(scenario.get("decision_gates_en", [])):
            errors.append(f"{scenario_id}: decision-gate translations are not one-to-one")
        ja_periods = _decision_gate_periods(
            scenario_id, "Japanese", scenario.get("decision_gates", []), errors
        )
        en_periods = _decision_gate_periods(
            scenario_id, "English", scenario.get("decision_gates_en", []), errors
        )
        if ja_periods != en_periods:
            errors.append(f"{scenario_id}: decision-gate periods differ between Japanese and English")

    for domain in sorted(REQUIRED_DOMAINS):
        if len(candidates_by_domain.get(domain, set())) < 2:
            errors.append(f"{domain}: fewer than two distinct candidates across scenarios")

    pairwise_candidate_differences: list[int] = []
    pairwise_fallback_differences: list[int] = []
    for left, right in itertools.combinations(scenarios, 2):
        left_options = {item["domain"]: item for item in left.get("technology_options", [])}
        right_options = {item["domain"]: item for item in right.get("technology_options", [])}
        candidate_differences = sum(
            _normalized_text(left_options.get(domain, {}).get("candidate_en"))
            != _normalized_text(right_options.get(domain, {}).get("candidate_en"))
            for domain in REQUIRED_DOMAINS
        )
        fallback_differences = sum(
            _normalized_text(left_options.get(domain, {}).get("fallback_en"))
            != _normalized_text(right_options.get(domain, {}).get("fallback_en"))
            for domain in REQUIRED_DOMAINS
        )
        pairwise_candidate_differences.append(candidate_differences)
        pairwise_fallback_differences.append(fallback_differences)
        pair = f"{left['scenario_id']} vs {right['scenario_id']}"
        if candidate_differences < minimum_candidate_differences:
            errors.append(
                f"{pair}: only {candidate_differences} candidate domains differ; "
                f"minimum={minimum_candidate_differences}"
            )
        if fallback_differences < minimum_fallback_differences:
            errors.append(
                f"{pair}: only {fallback_differences} fallback domains differ; "
                f"minimum={minimum_fallback_differences}"
            )

    contracts = scenario_set.get("decision_evidence_contracts", [])
    contract_ids = [item["contract_id"] for item in contracts]
    for value in sorted(_duplicates(contract_ids)):
        errors.append(f"decision_evidence_contracts: duplicate contract_id {value}")
    contract_gaps: set[str] = set()
    gap_contract_counts: dict[str, int] = {}
    for contract in contracts:
        contract_id = contract["contract_id"]
        if contract.get("acceptance_effect") != "candidate-only":
            errors.append(f"{contract_id}: acceptance_effect must be candidate-only")
        for key in ("schema_paths", "validator_paths"):
            for relative_path in contract.get(key, []):
                if not (repository_root / relative_path).is_file():
                    errors.append(f"{contract_id}: missing repository path {relative_path}")
        for gap_id in contract.get("gap_refs", []):
            contract_gaps.add(gap_id)
            gap_contract_counts[gap_id] = gap_contract_counts.get(gap_id, 0) + 1
    if contract_gaps != p0_gaps:
        errors.append(
            "decision_evidence_contracts: Gap coverage mismatch; "
            f"missing={sorted(p0_gaps - contract_gaps)}, extra={sorted(contract_gaps - p0_gaps)}"
        )
    for gap_id, count in sorted(gap_contract_counts.items()):
        if count != 1:
            errors.append(f"{gap_id}: assigned to {count} decision evidence contracts")

    return {
        "set_id": scenario_set["set_id"],
        "counts": {
            "scenarios": len(scenarios),
            "criteria_per_scenario": len(REQUIRED_CRITERIA),
            "option_domains": len(REQUIRED_DOMAINS),
            "open_p0_gaps": len(p0_gaps),
            "decision_evidence_contracts": len(contracts),
            "known_evidence_references": len(known_references),
            "implementation_phases": implementation_phase_count,
            "minimum_pairwise_candidate_domain_differences": min(
                pairwise_candidate_differences, default=0
            ),
            "minimum_pairwise_fallback_domain_differences": min(
                pairwise_fallback_differences, default=0
            ),
        },
        "calculation_errors": errors,
        "candidate_ready_for_consensus": not errors,
        "consensus_status": scenario_set["consensus_status"],
        "gaps_remain_open": True,
        "note": (
            "Validator success establishes structural comparability, configured option separation, "
            "and complete P0 Gap assignment only; "
            "it does not validate scenario claims, close a Gap, satisfy Consensus, or authorize adoption."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "scenario_set",
        nargs="?",
        type=Path,
        default=Path("roadmaps/scenarios/accepted/hpci-p0-scenarios.json"),
    )
    parser.add_argument(
        "--roadmap-dir",
        type=Path,
        default=Path("knowledge/public/roadmaps"),
    )
    args = parser.parse_args()
    repository_root = Path(__file__).resolve().parents[1]
    scenario_path = args.scenario_set
    if not scenario_path.is_absolute():
        scenario_path = repository_root / scenario_path
    roadmap_dir = args.roadmap_dir
    if not roadmap_dir.is_absolute():
        roadmap_dir = repository_root / roadmap_dir
    scenario_set = json.loads(scenario_path.read_text(encoding="utf-8"))
    roadmaps = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(roadmap_dir.glob("*.json"))
    ]
    scenario_policy = json.loads(
        (repository_root / "config" / "scenario-policy.json").read_text(encoding="utf-8")
    )
    result = evaluate(scenario_set, roadmaps, repository_root, scenario_policy)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["candidate_ready_for_consensus"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
