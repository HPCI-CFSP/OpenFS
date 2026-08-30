#!/usr/bin/env python3
"""Validate public procurement lineage and conservative budget arithmetic."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from estimate_system_cost import allocate_budget, contract_breakdown, lease_period_total

ROOT = Path(__file__).resolve().parents[1]


def validate_register(payload: dict, config: dict) -> None:
    def unique(items, key):
        values = [item[key] for item in items]
        if len(values) != len(set(values)):
            raise ValueError(f"duplicate {key}")
        return set(values)

    sources = unique(payload["sources"], "source_id")
    source_records = {s["source_id"]: s for s in payload["sources"]}
    cases = unique(payload["cases"], "case_id")
    gaps = unique(payload["coverage_gaps"], "gap_id")
    unique(config["components"], "id")
    unique(config["profiles"], "scenario_id")
    levels = config["budget_ceilings_oku_jpy"]
    if len(levels) != 5 or levels != sorted(set(levels)) or levels[0] <= 0:
        raise ValueError("five increasing positive budget levels are required")
    if config["default_budget_oku_jpy"] not in levels:
        raise ValueError("default budget must be a declared level")
    for source in payload["sources"]:
        url = urlparse(source["url"])
        if url.scheme != "https" or not url.hostname or url.username or url.password:
            raise ValueError("sources require anonymous HTTPS URLs")
    for case in payload["cases"]:
        refs = {doc["source_id"] for doc in case["documents"]}
        refs.update(ref for line in case["itemized_costs"] for ref in line["source_refs"])
        if case["amount"]:
            refs.update(case["amount"]["source_refs"])
        for field in ("contract_window", "configuration_observation"):
            if case.get(field):
                refs.update(case[field]["source_refs"])
        if refs - sources or set(case["related_case_ids"]) - cases or set(case["gap_ids"]) - gaps:
            raise ValueError(f"unresolved references: {case['case_id']}")
        if case["case_id"] in case["related_case_ids"]:
            raise ValueError("a procurement must not be related to itself")
        if not case["gap_ids"] and case["configuration_match"] == "unconfirmed":
            raise ValueError("unconfirmed configuration needs a gap")
        for field in ("amount", "contract_window", "configuration_observation"):
            if case.get(field) and any(source_records[r]["retrieval_status"] != "read"
                                       for r in case[field]["source_refs"]):
                raise ValueError(f"{field} must cite checked public sources")
        if case.get("contract_window"):
            window = case["contract_window"]
            if date.fromisoformat(window["start"]) > date.fromisoformat(window["end"]):
                raise ValueError("reversed contract window")
        if case["configuration_match"] == "confirmed" and not (
            case.get("configuration_observation") and any(
                d["kind"] == "final-specification" and d["access_status"] == "public-read"
                for d in case["documents"])):
            raise ValueError("confirmed configuration requires public final specifications and a match record")
        lease_period_total(case)
        contract_breakdown(case)
    for profile in config["profiles"]:
        for budget in levels:
            allocate_budget(config, profile["scenario_id"], budget, config["default_deployment_year"])


def main() -> int:
    payload = json.loads((ROOT / "knowledge/public/procurement-cost-register.json").read_text())
    config = json.loads((ROOT / "config/budget-planning.json").read_text())
    validate_register(payload, config)
    print(f"PASS procurement register: {len(payload['cases'])} cases; 5 budget levels; unverified estimates remain gated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
