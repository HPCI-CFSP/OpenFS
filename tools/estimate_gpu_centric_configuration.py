#!/usr/bin/env python3
"""Estimate candidate GPU-centric configurations without inventing missing inputs."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PRICE_CASES = ("optimistic", "reference", "conservative")
BENCHMARKS = [
    "HPL",
    "HPL-MxP",
    "HPCG",
    "Graph500",
    "OSU Micro-Benchmarks",
    "GROMACS",
    "OpenFOAM",
    "MLPerf Training",
    "MLPerf Inference Datacenter",
    "MLPerf Storage",
]


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def canonical_digest(payloads: list[dict[str, Any]]) -> str:
    serialized = json.dumps(payloads, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def requested_vendors(mode: str) -> list[str]:
    if mode in {"compare", "auto-pareto"}:
        return ["NVIDIA", "AMD"]
    return [mode]


def latest_event_date(product: dict[str, Any]) -> str:
    dates = [event["date"]["value"] for event in product.get("events", [])]
    return max(dates, default="0000-00-00")


def select_product(
    vendor: str,
    product_catalog: dict[str, Any],
    availability: dict[str, Any],
    required_date: str,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    assessments = {
        item["product_id"]: item for item in availability["assessments"]
    }
    candidates = [
        product
        for product in product_catalog["products"]
        if product["vendor"] == vendor and latest_event_date(product) <= required_date
    ]
    if not candidates:
        candidates = [
            product for product in product_catalog["products"] if product["vendor"] == vendor
        ]
    if not candidates:
        return None, None
    candidates.sort(
        key=lambda item: (item["generation_rank"], latest_event_date(item)),
        reverse=True,
    )
    eligible = [
        product
        for product in candidates
        if assessments.get(product["product_id"], {}).get("availability_status") == "eligible"
        and (
            assessments[product["product_id"]].get("latest_delivery_date") is None
            or assessments[product["product_id"]]["latest_delivery_date"] <= required_date
        )
    ]
    eligible.sort(
        key=lambda item: (item["generation_rank"], latest_event_date(item)),
        reverse=True,
    )
    product = eligible[0] if eligible else candidates[0]
    return product, assessments.get(product["product_id"])


def workload_gaps(request: dict[str, Any]) -> list[str]:
    mix = request["workloads"]["mix_percent"]
    demand = request["workloads"]["absolute_demand"]
    required = []
    if mix["ai_training"] > 0:
        required.extend(("training_accelerator_hours_per_year", "training_tokens_per_year"))
    if mix["ai_for_science_hpc"] > 0:
        required.extend(("hpc_jobs_per_year", "hpc_accelerator_hours_per_year"))
    if mix["data_analytics"] > 0:
        required.append("data_ingest_pb_per_year")
    return [key for key in required if demand.get(key) is None]


def input_gaps(
    request: dict[str, Any],
    availability_item: dict[str, Any] | None,
    package: dict[str, Any] | None,
) -> tuple[list[str], list[str], list[str]]:
    gap_ids: list[str] = []
    ja: list[str] = []
    en: list[str] = []

    def add(gap_id: str, ja_text: str, en_text: str) -> None:
        if gap_id not in gap_ids:
            gap_ids.append(gap_id)
            ja.append(ja_text)
            en.append(en_text)

    if package is None:
        add(
            "GAP-GPUCFG-001",
            "構成要素別の追跡可能な価格区間がないため算定不能です。要ベンダー見積です。",
            "No traceable component price interval is available. Calculation is unavailable and a vendor quote is required.",
        )
    if availability_item is None or availability_item["availability_status"] != "eligible":
        add(
            "GAP-GPUCFG-002",
            "指定地域・受入日における調達可能性と納期が確認できていません。",
            "Procurement eligibility and delivery timing for the requested jurisdiction and acceptance date are unconfirmed.",
        )
    missing_demands = workload_gaps(request)
    if missing_demands:
        add(
            "GAP-GPUCFG-003",
            "ワークロードの絶対需要が未入力です: " + ", ".join(missing_demands),
            "Absolute workload demand is missing: " + ", ".join(missing_demands),
        )
    facility = request["facility"]
    if facility["it_power_limit_mw"] is None or facility["it_power_limit_status"] != "confirmed":
        add(
            "GAP-GPUCFG-004",
            "使用可能IT電力が確認済み条件ではありません。",
            "Available IT power is not a confirmed constraint.",
        )
    if facility["cooling_capacity_mw"] is None or facility["cooling_capacity_status"] != "confirmed":
        add(
            "GAP-GPUCFG-005",
            "冷却能力が確認済み条件ではありません。",
            "Cooling capacity is not a confirmed constraint.",
        )
    if facility["rack_limit"] is None:
        add(
            "GAP-GPUCFG-006",
            "利用可能ラック数が未入力です。",
            "The available rack count is missing.",
        )
    if any(value is None for value in request["storage"].values()):
        add(
            "GAP-GPUCFG-007",
            "共有・アーカイブ容量またはチェックポイント・読出し帯域が未入力です。",
            "Shared/archive capacity or checkpoint/read bandwidth is missing.",
        )
    if request["workloads"]["mix_percent"]["ai_inference"] > 0 and any(
        value is None for value in request["inference"].values()
    ):
        add(
            "GAP-GPUCFG-008",
            "推論の同時利用数、要求率、TTFT、TPOTまたは品質条件が未入力です。",
            "Inference concurrency, request rate, TTFT, TPOT, or quality target is missing.",
        )
    add(
        "GAP-GPUCFG-009",
        "対象アプリケーションの検証済み性能モデルがないため、性能予測は調達評価に使用できません。",
        "No validated performance model exists for the target applications, so performance projections cannot be used for procurement evaluation.",
    )
    return gap_ids, ja, en


def line_multiplier(line: dict[str, Any], units: int, racks: int, request: dict[str, Any]) -> float:
    basis = line["basis"]
    if basis == "fixed":
        return 1
    if basis == "per-compute-unit":
        return units
    if basis == "per-rack":
        return racks
    if basis == "per-fast-storage-pb":
        return request["storage"]["shared_fast_capacity_pb"] or 0
    if basis == "per-archive-storage-pb":
        return request["storage"]["archive_capacity_pb"] or 0
    raise ValueError(f"unsupported cost basis: {basis}")


def package_cost(
    package: dict[str, Any], units: int, request: dict[str, Any], price_case: str, period: str
) -> float:
    racks = math.ceil(units / package["units_per_rack"])
    field = f"{price_case}_jpy"
    return sum(
        line[field] * line_multiplier(line, units, racks, request)
        for line in package["cost_lines"]
        if line["period"] == period
    )


def tco_scope_complete(package: dict[str, Any], deployment_mode: str) -> bool:
    initial = {
        line["category"] for line in package["cost_lines"] if line["period"] == "initial"
    }
    annual = {
        line["category"] for line in package["cost_lines"] if line["period"] == "annual"
    }
    end_of_horizon = {
        line["category"]
        for line in package["cost_lines"]
        if line["period"] == "end-of-horizon"
    }
    required_initial = {"compute", "network", "storage", "management", "integration"}
    if deployment_mode in {"on-premises", "hybrid"}:
        required_initial.add("facility")
    required_annual = {"maintenance", "energy", "staffing"}
    if deployment_mode in {"external-hosting", "hybrid"}:
        required_annual.add("hosting")
    return (
        required_initial <= initial
        and required_annual <= annual
        and "decommissioning" in end_of_horizon
    )


def max_units_for_case(
    request: dict[str, Any], package: dict[str, Any], price_case: str
) -> int:
    budget = request["budget"]["capex_ceiling_oku_jpy"] * 100_000_000
    contingency_ratio = request["budget"]["contingency_percent"] / 100
    facility = request["facility"]
    power_limit_kw = facility["it_power_limit_mw"] * 1000
    cooling_limit_kw = facility["cooling_capacity_mw"] * 1000
    upper = min(
        int(power_limit_kw // package["power_kw_per_unit"]),
        int(cooling_limit_kw // package["power_kw_per_unit"]),
        facility["rack_limit"] * package["units_per_rack"],
    )

    def affordable(units: int) -> bool:
        initial = package_cost(package, units, request, price_case, "initial")
        return initial * (1 + contingency_ratio) <= budget

    low, high = 0, max(0, upper)
    while low < high:
        middle = (low + high + 1) // 2
        if affordable(middle):
            low = middle
        else:
            high = middle - 1
    return low


def performance_stub(request: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "not-computable",
        "compute_time_s": None,
        "memory_time_s": None,
        "communication_time_s": None,
        "io_time_s": None,
        "overlappable_time_s": None,
        "non_overlappable_time_s": None,
        "synchronization_time_s": None,
        "predicted_time_s": None,
        "inference_queue": {
            "status": "not-computable",
            "concurrent_users": request["inference"]["concurrent_users"],
            "ttft_p95_ms": None,
            "tpot_p95_ms": None,
        },
        "benchmark_candidates": BENCHMARKS,
        "procurement_use": "prohibited",
    }


def blocked_case(
    vendor: str,
    product: dict[str, Any] | None,
    request: dict[str, Any],
    price_case: str,
    gap_ids: list[str],
    availability_status: str,
) -> dict[str, Any]:
    budget = request["budget"]["capex_ceiling_oku_jpy"] * 100_000_000
    delivery = "fail" if availability_status == "ineligible" else "unknown"
    return {
        "case_ref": f"{vendor}-{price_case}",
        "price_case": price_case,
        "status": "blocked",
        "unit_type": None,
        "compute_units": None,
        "gpu_count": None,
        "host_cpu_count": None,
        "rack_count": None,
        "total_hbm_gib": None,
        "it_power_kw": None,
        "costs": {
            "configuration_cost_jpy": None,
            "contingency_jpy": None,
            "unused_budget_jpy": None,
            "budget_ceiling_jpy": budget,
            "identity_verified": None,
        },
        "tco": {
            "years": request["budget"]["tco_years"],
            "initial_capex_jpy": None,
            "recurring_cost_jpy": None,
            "end_of_horizon_cost_jpy": None,
            "total_tco_jpy": None,
            "complete": False,
        },
        "constraints": {
            "budget": "unknown",
            "it_power": "unknown",
            "cooling": "unknown",
            "rack_count": "unknown",
            "delivery": delivery,
        },
        "performance": performance_stub(request),
        "gap_ids": gap_ids,
    }


def priced_case(
    vendor: str,
    product: dict[str, Any],
    request: dict[str, Any],
    package: dict[str, Any],
    price_case: str,
    gap_ids: list[str],
) -> dict[str, Any]:
    units = max_units_for_case(request, package, price_case)
    if units < 1:
        return blocked_case(vendor, product, request, price_case, gap_ids, "eligible")
    racks = math.ceil(units / package["units_per_rack"])
    initial = package_cost(package, units, request, price_case, "initial")
    tco_complete = tco_scope_complete(package, request["deployment_mode"])
    recurring = (
        package_cost(package, units, request, price_case, "annual")
        * request["budget"]["tco_years"]
        if tco_complete
        else None
    )
    end_of_horizon = (
        package_cost(package, units, request, price_case, "end-of-horizon")
        if tco_complete
        else None
    )
    contingency = initial * request["budget"]["contingency_percent"] / 100
    budget = request["budget"]["capex_ceiling_oku_jpy"] * 100_000_000
    unused = budget - initial - contingency
    identity = math.isclose(initial + contingency + unused, budget, abs_tol=0.01)
    hbm = package["hbm_gib_per_gpu"] * package["gpus_per_unit"] * units
    power = package["power_kw_per_unit"] * units
    return {
        "case_ref": f"{vendor}-{price_case}",
        "price_case": price_case,
        "status": "partial" if gap_ids else "feasible",
        "unit_type": package["unit_type"],
        "compute_units": units,
        "gpu_count": package["gpus_per_unit"] * units,
        "host_cpu_count": package["host_cpus_per_unit"] * units,
        "rack_count": racks,
        "total_hbm_gib": hbm,
        "it_power_kw": power,
        "costs": {
            "configuration_cost_jpy": initial,
            "contingency_jpy": contingency,
            "unused_budget_jpy": unused,
            "budget_ceiling_jpy": budget,
            "identity_verified": identity,
        },
        "tco": {
            "years": request["budget"]["tco_years"],
            "initial_capex_jpy": initial + contingency,
            "recurring_cost_jpy": recurring,
            "end_of_horizon_cost_jpy": end_of_horizon,
            "total_tco_jpy": (
                initial + contingency + recurring + end_of_horizon
                if recurring is not None and end_of_horizon is not None
                else None
            ),
            "complete": tco_complete,
        },
        "constraints": {
            "budget": "pass",
            "it_power": "pass",
            "cooling": "pass",
            "rack_count": "pass",
            "delivery": "pass",
        },
        "performance": performance_stub(request),
        "gap_ids": gap_ids,
    }


def compute_pareto(
    request: dict[str, Any], vendor_candidates: list[dict[str, Any]]
) -> dict[str, Any]:
    cases = [
        (item, item["cases"][1])
        for item in vendor_candidates
        if item["cases"][1]["status"] != "blocked"
    ]
    if request["vendor_mode"] != "auto-pareto" or not cases:
        return {
            "status": "not-evaluable",
            "candidate_refs": [],
            "reason_ja": "価格、納期、施設条件または検証済み性能指標が不足しているためPareto比較はできません。",
            "reason_en": "Pareto comparison is unavailable because price, delivery, facility constraints, or validated performance metrics are missing.",
        }
    extractors = {
        "total-hbm-gib": lambda vendor, case: case["total_hbm_gib"],
        "capex-jpy": lambda vendor, case: case["costs"]["configuration_cost_jpy"],
        "it-power-kw": lambda vendor, case: case["it_power_kw"],
        "delivery-risk": lambda vendor, case: {
            "eligible": 0,
            "conditional": 1,
            "unknown": 2,
            "ineligible": 3,
            "not-assessed": 3,
        }[vendor["availability_status"]],
    }
    objectives = request["objectives"]
    unsupported = [item["metric"] for item in objectives if item["metric"] not in extractors]
    if unsupported:
        return {
            "status": "not-evaluable",
            "candidate_refs": [],
            "reason_ja": "目的関数に検証済みの値がありません: " + ", ".join(unsupported),
            "reason_en": "Validated values are unavailable for objectives: " + ", ".join(unsupported),
        }
    vectors = []
    for vendor, case in cases:
        vector = [extractors[item["metric"]](vendor, case) for item in objectives]
        if any(value is None for value in vector):
            return {
                "status": "not-evaluable",
                "candidate_refs": [],
                "reason_ja": "目的関数に欠損値があるためPareto比較はできません。",
                "reason_en": "Pareto comparison is unavailable because an objective contains a missing value.",
            }
        vectors.append((case["case_ref"], vector))

    def dominates(left: list[float], right: list[float]) -> bool:
        no_worse = True
        strictly_better = False
        for index, objective in enumerate(objectives):
            if objective["direction"] == "maximize":
                no_worse &= left[index] >= right[index]
                strictly_better |= left[index] > right[index]
            else:
                no_worse &= left[index] <= right[index]
                strictly_better |= left[index] < right[index]
        return no_worse and strictly_better

    frontier = [
        ref
        for ref, vector in vectors
        if not any(dominates(other, vector) for other_ref, other in vectors if other_ref != ref)
    ]
    metrics = ", ".join(item["metric"] for item in objectives)
    return {
        "status": "computed",
        "candidate_refs": frontier,
        "reason_ja": f"明示した目的関数（{metrics}）による非劣解であり、単一の推奨順位ではありません。",
        "reason_en": f"These are non-dominated candidates for the explicit objectives ({metrics}), not a single recommendation ranking.",
    }


def evaluate(
    request: dict[str, Any],
    architecture: dict[str, Any],
    product_catalog: dict[str, Any],
    availability: dict[str, Any],
    cost_input: dict[str, Any] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    mix_total = sum(request["workloads"]["mix_percent"].values())
    if not math.isclose(mix_total, 100, abs_tol=1e-9):
        raise ValueError(f"workload mix must total 100, got {mix_total}")
    if request["architecture_id"] != architecture["architecture_id"]:
        raise ValueError("planning request and reference architecture differ")
    if request["catalog_snapshot"]["product_catalog_id"] != product_catalog["catalog_id"]:
        raise ValueError("planning request and product catalog differ")
    if request["catalog_snapshot"]["availability_assessment_id"] != availability["assessment_id"]:
        raise ValueError("planning request and availability assessment differ")

    packages = {
        (item["vendor"], item["product_id"]): item
        for item in (cost_input or {}).get("packages", [])
    }
    vendor_candidates = []
    for vendor in requested_vendors(request["vendor_mode"]):
        product, assessment = select_product(
            vendor,
            product_catalog,
            availability,
            request["schedule"]["required_acceptance_date"],
        )
        if availability["required_acceptance_date"] != request["schedule"]["required_acceptance_date"]:
            assessment = None
        package = packages.get((vendor, product["product_id"])) if product else None
        gaps, warnings_ja, warnings_en = input_gaps(request, assessment, package)
        availability_status = assessment["availability_status"] if assessment else "not-assessed"
        blocking = any(gap != "GAP-GPUCFG-009" for gap in gaps)
        if blocking:
            cases = [
                blocked_case(vendor, product, request, price_case, gaps, availability_status)
                for price_case in PRICE_CASES
            ]
            status = "blocked"
        else:
            cases = [
                priced_case(vendor, product, request, package, price_case, gaps)
                for price_case in PRICE_CASES
            ]
            status = "partial" if gaps else "feasible"
        vendor_candidates.append(
            {
                "vendor": vendor,
                "product_id": product["product_id"] if product else None,
                "availability_status": availability_status,
                "status": status,
                "cases": cases,
                "warnings_ja": warnings_ja or ["未解決の警告はありません。"],
                "warnings_en": warnings_en or ["No unresolved warnings."],
                "gap_ids": gaps or ["GAP-GPUCFG-009"],
            }
        )

    pareto = compute_pareto(request, vendor_candidates)
    statuses = {item["status"] for item in vendor_candidates}
    overall_status = "blocked" if statuses == {"blocked"} else "partial" if "blocked" in statuses or "partial" in statuses else "feasible"
    payloads = [request, architecture, product_catalog, availability]
    if cost_input is not None:
        payloads.append(cost_input)
    result_suffix = request["request_id"].removeprefix("PLANREQ-")
    return {
        "schema_version": "0.1.0",
        "result_id": f"CFGRESULT-{result_suffix}",
        "status": overall_status,
        "research_status": "provisional",
        "consensus_status": "incomplete",
        "procurement_use": "prohibited",
        "request_id": request["request_id"],
        "architecture_id": architecture["architecture_id"],
        "product_catalog_id": product_catalog["catalog_id"],
        "availability_assessment_id": availability["assessment_id"],
        "cost_input_id": cost_input["cost_input_id"] if cost_input else None,
        "generated_at": generated_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "engine_version": "0.1.0",
        "input_digest": canonical_digest(payloads),
        "vendor_candidates": vendor_candidates,
        "pareto_result": pareto,
        "messages_ja": [
            "本結果は単一のAIモデル・単一のAIエージェントによる暫定Candidateで、Consensus Gateは未完了です。",
            "公開根拠が不足する値は補間せず、算定不能または要ベンダー見積として扱います。",
        ],
        "messages_en": [
            "This is a provisional Candidate produced by one model and one agent; the Consensus Gate is incomplete.",
            "Values unsupported by public evidence are not interpolated and remain unavailable or require a vendor quote.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--architecture", type=Path, required=True)
    parser.add_argument("--product-catalog", type=Path, required=True)
    parser.add_argument("--availability", type=Path, required=True)
    parser.add_argument("--cost-input", type=Path)
    parser.add_argument("--generated-at")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = evaluate(
        load_json(args.request),
        load_json(args.architecture),
        load_json(args.product_catalog),
        load_json(args.availability),
        load_json(args.cost_input) if args.cost_input else None,
        args.generated_at,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {args.output}: status={result['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
