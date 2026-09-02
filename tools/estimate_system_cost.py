#!/usr/bin/env python3
"""Offline cost arithmetic. Allocations never stand in for estimated prices."""

from __future__ import annotations

import argparse
import json
from calendar import monthrange
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def number(value: Any) -> Decimal:
    if isinstance(value, bool):
        raise ValueError("boolean is not a cost")
    try:
        result = Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError("cost must be a number") from exc
    if not result.is_finite() or result < 0:
        raise ValueError("costs must be finite and nonnegative")
    return result


def normalize_amount(amount: dict[str, Any]) -> Decimal:
    """Return a tax-exclusive total only when all conversions are explicit."""
    if amount["kind"] not in {"contract", "award"}:
        raise ValueError("program budgets and planned prices are not contract costs")
    value = number(amount["value_jpy"])
    basis = amount["payment_basis"]
    if basis == "monthly":
        months = amount.get("period_months")
        if not isinstance(months, int) or isinstance(months, bool) or months <= 0:
            raise ValueError("monthly amounts require a known contract period")
        value *= months
    elif basis != "total":
        raise ValueError("unsupported payment basis")
    if amount["tax_basis"] == "including-tax":
        if amount.get("tax_rate") is None:
            raise ValueError("tax rate is unknown")
        rate = number(amount["tax_rate"])
        if rate > 1:
            raise ValueError("tax rate must be a fraction")
        value /= 1 + rate
    elif amount["tax_basis"] != "excluding-tax":
        raise ValueError("tax basis is unknown")
    return value


def lease_period_total(case: dict[str, Any]) -> dict[str, Any] | None:
    """Arithmetic over the evidenced billing window, not equipment price or TCO."""
    amount = case.get("amount")
    window = case.get("contract_window")
    if not amount or amount["payment_basis"] != "monthly" or not window:
        return None
    start, end = (date.fromisoformat(window[key]) for key in ("start", "end"))
    months = (end.year - start.year) * 12 + end.month - start.month + 1
    if end < start or start.day != 1 or end.day != monthrange(end.year, end.month)[1]:
        raise ValueError("monthly arithmetic requires an explicit whole-month window")
    if amount["period_months"] != months:
        raise ValueError("billing months disagree with the evidenced window")
    return {"value_jpy": float(number(amount["value_jpy"]) * months),
            "months": months, "tax_basis": amount["tax_basis"],
            "basis": "constant-monthly-rate-arithmetic", "window_basis": window["basis"]}


def five_year_known_cost_floor(case: dict[str, Any]) -> dict[str, Any] | None:
    """Return only a five-year contractual subtotal supported by explicit billing evidence."""
    amount = case.get("amount")
    if not amount or amount.get("payment_basis") != "monthly":
        return None
    months = amount.get("period_months")
    if not isinstance(months, int) or isinstance(months, bool) or months < 60:
        return None
    return {
        "value_jpy": float(number(amount["value_jpy"]) * 60),
        "months": 60,
        "tax_basis": amount["tax_basis"],
        "basis": "first-60-months-at-published-monthly-rate",
        "tco_complete": False,
        "excluded_costs": [
            "contract-amendments",
            "electricity",
            "facility-shared-cost-allocation",
            "staffing",
            "later-expansion",
        ],
    }


def contract_breakdown(case: dict[str, Any]) -> dict[str, Any]:
    """Keep residual cost unallocated, in the ORIGINAL contract's tax basis."""
    amount = case.get("amount")
    if amount and amount["kind"] not in {"contract", "award"}:
        raise ValueError("a budget is not an observed contract cost")
    if not amount or amount["payment_basis"] != "total":
        return {"observed_total_jpy": None, "itemized_jpy": None, "unallocated_jpy": None}
    total = number(amount["value_jpy"])
    allocated = Decimal(0)
    ids: set[str] = set()
    for line in case["itemized_costs"]:
        if line["line_id"] in ids:
            raise ValueError("duplicate cost line")
        ids.add(line["line_id"])
        if line["tax_basis"] != amount["tax_basis"]:
            raise ValueError("itemized costs must use the original contract tax basis")
        if line["basis"] != "observed" or not line["source_refs"]:
            raise ValueError("contract itemization requires observed public evidence")
        allocated += number(line["value_jpy"])
    if allocated > total:
        raise ValueError("itemized costs exceed contract total")
    return {"observed_total_jpy": float(total), "itemized_jpy": float(allocated),
            "unallocated_jpy": float(total - allocated)}


def estimate_configuration(lines: list[dict[str, Any]], years: int = 5) -> dict[str, Any]:
    """Sum explicit cost intervals; refuse double counting and incomplete TCO."""
    if not isinstance(years, int) or isinstance(years, bool) or years <= 0:
        raise ValueError("TCO period must be a positive integer")
    totals = {key: Decimal(0) for key in ("lower", "central", "upper")}
    missing: list[str] = []
    ids: set[str] = set()
    scopes: set[str] = set()
    phases: set[str] = set()
    for line in lines:
        if not line["scope_ids"] or len(set(line["scope_ids"])) != len(line["scope_ids"]):
            raise ValueError("cost lines require unique, nonempty scope IDs")
        if line["line_id"] in ids or scopes.intersection(line["scope_ids"]):
            raise ValueError("duplicate line or overlapping cost scope")
        ids.add(line["line_id"])
        scopes.update(line["scope_ids"])
        phase = line["phase"]
        if phase not in {"initial", "annual"}:
            raise ValueError("unsupported cost phase")
        phases.add(phase)
        values = line.get("cost_jpy")
        if values is None:
            missing.append(line["line_id"])
            continue
        if not line.get("source_refs") or line["basis"] not in {"observed", "estimated"}:
            raise ValueError("cost intervals require explicit evidence and basis")
        if line.get("tax_basis") != "excluding-tax":
            raise ValueError("normalize taxes before combining cost intervals")
        lower, central, upper = (number(values[key]) for key in totals)
        if not lower <= central <= upper:
            raise ValueError("unordered cost interval")
        for key, value in zip(totals, (lower, central, upper)):
            totals[key] += value * (years if phase == "annual" else 1)
    if "annual" not in phases:
        missing.append("annual-costs")
    if "initial" not in phases:
        missing.append("initial-costs")
    subtotal = {key: float(value) for key, value in totals.items()}
    return {"years": years, "known_subtotal_jpy": subtotal,
            "tco_jpy": None if missing else subtotal, "missing": missing,
            "consensus_status": "incomplete", "procurement_ready": False}


def allocate_budget(config: dict[str, Any], scenario_id: str, budget: float,
                    deployment_year: int) -> dict[str, Any]:
    ceiling = number(budget)
    if ceiling <= 0 or ceiling > 100000:
        raise ValueError("budget must be in (0, 100000] hundred-million JPY")
    if isinstance(deployment_year, bool) or not isinstance(deployment_year, int) or deployment_year not in config["deployment_years"]:
        raise ValueError("deployment year is outside the declared planning horizon")
    profile = next((p for p in config["profiles"] if p["scenario_id"] == scenario_id), None)
    if profile is None:
        raise ValueError("unknown planning profile")
    shares = profile["shares_percent"]
    if set(shares) != {c["id"] for c in config["components"]}:
        raise ValueError("allocation components do not match")
    if sum(number(value) for value in shares.values()) != 100:
        raise ValueError("allocation shares must total 100 percent")
    return {
        "budget_ceiling_oku_jpy": float(ceiling), "deployment_year": deployment_year,
        "price_basis_year": config["price_basis_year"], "tax_basis": config["tax_basis"],
        "basis": "openfs-planning-assumption", "feasibility_status": "unverified",
        "allocations": [{**component, "share_percent": shares[component["id"]],
                         "allocation_oku_jpy": float(ceiling * number(shares[component["id"]]) / 100),
                         "estimated_cost_oku_jpy": None, "quantity": None}
                        for component in config["components"]],
        "tco_years": config["tco_years"], "tco_oku_jpy": None,
        "gap_ids": ["PCG-001", "PCG-002", "PCG-003", "PCG-004"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario-id", default="SCN-HPCI-BALANCED-001")
    parser.add_argument("--budget-oku-jpy", type=float, default=100)
    parser.add_argument("--deployment-year", type=int, default=2030)
    parser.add_argument("--cost-lines", type=Path, help="Optional normalized cost lines for interval TCO arithmetic")
    args = parser.parse_args()
    config = json.loads((ROOT / "config/budget-planning.json").read_text())
    result = allocate_budget(config, args.scenario_id, args.budget_oku_jpy, args.deployment_year)
    if args.cost_lines:
        result["cost_arithmetic"] = estimate_configuration(json.loads(args.cost_lines.read_text()), config["tco_years"])
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
