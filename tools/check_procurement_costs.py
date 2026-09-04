#!/usr/bin/env python3
"""Validate public procurement lineage and conservative budget arithmetic."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from estimate_system_cost import (
    allocate_budget,
    contract_breakdown,
    five_year_known_cost_floor,
    lease_period_total,
    number,
)

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
    tco_scopes = [item["scope_id"] for item in payload["tco_scope_catalog"]]
    if len(tco_scopes) != 12 or len(tco_scopes) != len(set(tco_scopes)):
        raise ValueError("TCO scope catalog must contain 12 unique scopes")
    unique([entry for case in payload["cases"] for entry in case.get("storage_capacity_observations", [])],
           "observation_id")
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
        for field in ("contract_window", "configuration_observation", "reported_period_total"):
            if case.get(field):
                refs.update(case[field]["source_refs"])
        refs.update(case.get("contract_date_source_refs", []))
        capacities = case.get("storage_capacity_observations", [])
        refs.update(ref for entry in capacities for ref in entry["source_refs"])
        assessment = case["five_year_cost_assessment"]
        scope_rows = assessment["scope_coverage"]
        if [row["scope_id"] for row in scope_rows] != tco_scopes:
            raise ValueError(
                f"TCO scope coverage must follow the complete catalog: {case['case_id']}"
            )
        for row in scope_rows:
            row_refs = set(row["source_refs"])
            if row["evidence_status"] == "unknown" and row_refs:
                raise ValueError("unknown TCO scope must not cite evidence")
            if row["evidence_status"] != "unknown" and not row_refs:
                raise ValueError("evidenced TCO scope requires source references")
            if row_refs - sources or any(
                source_records[ref]["retrieval_status"] != "read" for ref in row_refs
            ):
                raise ValueError("TCO scope must cite checked public sources")
        floor = five_year_known_cost_floor(case)
        if assessment["status"] == "known-contractual-floor":
            if not floor or assessment["complete_tco"]:
                raise ValueError(
                    "known contractual floor must remain distinct from complete TCO"
                )
            if (
                number(assessment["known_cost_floor_jpy"])
                != number(floor["value_jpy"])
                or assessment["tax_basis"] != floor["tax_basis"]
            ):
                raise ValueError(
                    "stored five-year floor disagrees with contractual arithmetic"
                )
        elif (
            assessment["known_cost_floor_jpy"] is not None
            or assessment["tax_basis"] is not None
            or floor is not None
        ):
            raise ValueError(
                "non-computable five-year assessment cannot carry a cost floor"
            )
        if refs - sources or set(case["related_case_ids"]) - cases or set(case["gap_ids"]) - gaps:
            raise ValueError(f"unresolved references: {case['case_id']}")
        if case["case_id"] in case["related_case_ids"]:
            raise ValueError("a procurement must not be related to itself")
        if not case["gap_ids"] and case["configuration_match"] == "unconfirmed":
            raise ValueError("unconfirmed configuration needs a gap")
        for field in ("amount", "contract_window", "configuration_observation", "reported_period_total"):
            if case.get(field) and any(source_records[r]["retrieval_status"] != "read"
                                       for r in case[field]["source_refs"]):
                raise ValueError(f"{field} must cite checked public sources")
        for entry in capacities:
            if not entry["source_refs"] or any(source_records[r]["retrieval_status"] != "read"
                                               for r in entry["source_refs"]):
                raise ValueError("storage capacity must cite checked public sources")
        contract_sources = {doc["source_id"] for doc in case["documents"]
                            if doc["kind"] == "contract-result" and doc["access_status"] == "public-read"}
        date_refs = set(case.get("contract_date_source_refs", []))
        amount = case.get("amount")
        if case["contract_date"] and not date_refs and amount and amount["kind"] == "contract":
            # Legacy records cite the same contract disclosure for date and amount.
            date_refs = set(amount["source_refs"])
        if case["contract_date"] and not date_refs:
            raise ValueError("contract date requires an explicit checked contract result")
        if date_refs and (not case["contract_date"] or not date_refs <= contract_sources
                          or any(source_records[r]["retrieval_status"] != "read" for r in date_refs)):
            raise ValueError("contract date must cite a checked contract result")
        reported = case.get("reported_period_total")
        if reported:
            months = reported["period_months"]
            if not isinstance(months, int) or isinstance(months, bool) or months <= 0:
                raise ValueError("reported period total requires an explicit positive month count")
            if (reported["kind"] != "contract" or reported["payment_basis"] != "total"
                    or not reported["source_refs"] or not set(reported["source_refs"]) <= contract_sources):
                raise ValueError("reported period total requires an explicit public contract result")
            arithmetic = lease_period_total(case)
            if arithmetic and (number(reported["value_jpy"]) != number(arithmetic["value_jpy"])
                               or reported["period_months"] != arithmetic["months"]
                               or reported["tax_basis"] != arithmetic["tax_basis"]):
                raise ValueError("reported period total disagrees with billing arithmetic; reconcile the evidence")
            monthly = case.get("amount")
            if monthly and monthly["payment_basis"] == "monthly" and monthly["period_months"] is not None:
                if (monthly["period_months"] != months
                        or number(reported["value_jpy"]) != number(monthly["value_jpy"]) * months
                        or reported["tax_basis"] != monthly["tax_basis"]):
                    raise ValueError("reported period total disagrees with the evidenced monthly amount or duration")
            if (monthly and monthly["payment_basis"] == "monthly"
                    and monthly["tax_rate"] is not None and reported["tax_rate"] is not None
                    and number(monthly["tax_rate"]) != number(reported["tax_rate"])):
                raise ValueError("reported period total disagrees with the monthly tax rate")
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
