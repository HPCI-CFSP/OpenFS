#!/usr/bin/env python3
"""Check that the published HPCI scenario portfolio is comparable and gap-complete."""

from __future__ import annotations

import argparse
import json
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


def _duplicates(values: list[str]) -> set[str]:
    return {value for value in values if values.count(value) > 1}


def _p0_gaps(roadmaps: list[dict[str, Any]]) -> set[str]:
    return {
        gap["gap_id"]
        for roadmap in roadmaps
        for gap in roadmap.get("coverage_gaps", [])
        if gap.get("priority") == "P0" and gap.get("status") == "open"
    }


def evaluate(
    scenario_set: dict[str, Any],
    roadmaps: list[dict[str, Any]],
    repository_root: Path,
) -> dict[str, Any]:
    errors: list[str] = []
    scenarios = scenario_set["scenarios"]
    p0_gaps = _p0_gaps(roadmaps)

    scenario_ids = [item["scenario_id"] for item in scenarios]
    if len(scenarios) != 3:
        errors.append(f"scenarios: expected exactly 3, found {len(scenarios)}")
    for value in sorted(_duplicates(scenario_ids)):
        errors.append(f"scenarios: duplicate scenario_id {value}")

    candidates_by_domain: dict[str, set[str]] = {domain: set() for domain in REQUIRED_DOMAINS}
    for scenario in scenarios:
        scenario_id = scenario["scenario_id"]
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
            candidates_by_domain.setdefault(option["domain"], set()).add(option["candidate_en"])

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

    for domain in sorted(REQUIRED_DOMAINS):
        if len(candidates_by_domain.get(domain, set())) < 2:
            errors.append(f"{domain}: fewer than two distinct candidates across scenarios")

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
        },
        "calculation_errors": errors,
        "candidate_ready_for_consensus": not errors,
        "consensus_status": scenario_set["consensus_status"],
        "gaps_remain_open": True,
        "note": (
            "Validator success establishes structural comparability and complete P0 Gap assignment only; "
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
    result = evaluate(scenario_set, roadmaps, repository_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["candidate_ready_for_consensus"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
