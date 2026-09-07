#!/usr/bin/env python3
"""Estimate provisional GPU-centric configurations without inventing missing inputs."""

from __future__ import annotations

import argparse
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ENGINE_VERSION = "0.2.0"
PRICE_CASES = ("optimistic", "baseline", "conservative")
BENCHMARKS = (
    "HPL", "HPL-MxP", "HPCG", "Graph500", "OSU Micro-Benchmarks",
    "GROMACS", "OpenFOAM", "MLPerf Training", "MLPerf Inference Datacenter",
    "MLPerf Storage",
)
REQUIRED_INITIAL = (
    "compute", "scale-up", "scale-out", "network", "fast-storage",
    "archive-storage", "management", "software", "integration",
)
REQUIRED_ANNUAL = ("maintenance", "spares", "energy", "operations")


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def as_number(value: Any) -> float | None:
    if value is None or value == "" or isinstance(value, bool):
        return None
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def requested_vendors(mode: str) -> list[str]:
    return ["NVIDIA", "AMD"] if mode in {"compare", "auto-pareto"} else [mode]


def latest_event_date(product: dict[str, Any]) -> str:
    return max((event["date"]["value"] for event in product.get("events", [])), default="0000-00-00")


def product_unit_complete(product: dict[str, Any]) -> bool:
    return any(
        unit.get("gpus_per_unit") is not None
        and unit.get("host_cpus_per_unit") is not None
        and unit.get("units_per_rack") is not None
        for unit in product.get("procurement_units", [])
    )


def select_product(
    vendor: str,
    catalog: dict[str, Any],
    availability: dict[str, Any],
    request: dict[str, Any],
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    required_date = request["schedule"]["required_acceptance_date"]
    selected = request.get("product_selection", {}).get(vendor.lower(), "auto")
    assessments = {item["product_id"]: item for item in availability.get("assessments", [])}
    candidates = [item for item in catalog["products"] if item["vendor"] == vendor]
    if selected != "auto":
        product = next((item for item in candidates if item["product_id"] == selected), None)
        return product, assessments.get(product["product_id"]) if product else None

    hpc_weight = request["workloads"]["mix_percent"].get("ai_for_science_hpc", 0)

    def score(product: dict[str, Any]) -> tuple[int, int, str]:
        assessment = assessments.get(product["product_id"], {})
        eligible = (
            assessment.get("availability_status") == "eligible"
            and (
                assessment.get("latest_delivery_date") is None
                or assessment["latest_delivery_date"] <= required_date
            )
        )
        technical = product.get("technical_specs", {})
        return (
            (8 if eligible else 0)
            + (4 if product_unit_complete(product) else 0)
            + (2 if hpc_weight > 0 and technical.get("fp64_tflops") is not None else 0)
            + (1 if technical.get("hbm_capacity_gib") is not None else 0)
            + (1 if latest_event_date(product) <= required_date else 0),
            product.get("generation_rank", 0),
            latest_event_date(product),
        )

    candidates.sort(key=score, reverse=True)
    product = candidates[0] if candidates else None
    return product, assessments.get(product["product_id"]) if product else None


def required_cost_categories(deployment_mode: str) -> dict[str, list[str]]:
    initial = list(REQUIRED_INITIAL)
    annual = list(REQUIRED_ANNUAL)
    if deployment_mode in {"on-premises", "hybrid"}:
        initial.append("facility")
    if deployment_mode in {"external-hosting", "hybrid"}:
        annual.append("hosting")
    return {"initial": initial, "annual": annual, "end-of-horizon": ["decommissioning"]}


def missing_cost_scopes(package: dict[str, Any] | None, deployment_mode: str) -> list[str]:
    if package is None:
        return ["component-cost-package"]
    missing: list[str] = []
    for period, categories in required_cost_categories(deployment_mode).items():
        for category in categories:
            line = next(
                (
                    item
                    for item in package.get("cost_lines", [])
                    if item["period"] == period and item["category"] == category
                ),
                None,
            )
            if line is None or any(as_number(line.get(f"{case}_jpy")) is None for case in PRICE_CASES):
                missing.append(f"{period}:{category}")
    return missing


def demand_missing(request: dict[str, Any]) -> list[str]:
    mix = request["workloads"]["mix_percent"]
    demand = request["workloads"]["absolute_demand"]
    keys = ["annual_accelerator_hours"]
    if mix["ai_training"] > 0:
        keys.extend(("training_tokens_per_year", "training_jobs_per_year"))
    if mix["ai_inference"] > 0:
        keys.extend(("inference_requests_per_year", "peak_requests_per_second"))
    if mix["ai_for_science_hpc"] > 0:
        keys.extend(("hpc_jobs_per_year", "hpc_accelerators_per_job", "hpc_mean_runtime_hours"))
    if mix["data_analytics"] > 0:
        keys.append("data_ingest_pb_per_year")
    return list(dict.fromkeys(key for key in keys if as_number(demand.get(key)) is None))


def storage_missing(request: dict[str, Any]) -> list[str]:
    required = (
        "shared_fast_capacity_pb", "archive_capacity_pb", "training_read_gb_s",
        "checkpoint_write_gb_s", "metadata_million_inodes", "retention_years",
        "rto_hours", "local_nvme_tb_per_compute_unit",
    )
    return [key for key in required if as_number(request["storage"].get(key)) is None]


def inference_missing(request: dict[str, Any]) -> list[str]:
    if request["workloads"]["mix_percent"]["ai_inference"] <= 0:
        return []
    required = (
        "model_name", "parameter_count_billion", "quantization", "input_tokens",
        "output_tokens", "context_tokens", "concurrent_users",
        "request_rate_per_second", "ttft_p50_ms", "ttft_p95_ms", "ttft_p99_ms",
        "tpot_p50_ms", "tpot_p95_ms", "tpot_p99_ms",
        "offline_throughput_target", "server_throughput_target", "quality_target_id",
    )
    return [key for key in required if request["inference"].get(key) in {None, ""}]


def package_missing(package: dict[str, Any] | None) -> list[str]:
    if package is None:
        return ["package"]
    required = (
        "unit_type", "gpus_per_unit", "host_cpus_per_unit", "units_per_rack",
        "power_kw_per_unit", "hbm_gib_per_gpu", "host_memory_gib_per_unit",
        "local_nvme_tb_per_unit", "rack_footprint_m2", "rack_weight_kg",
    )
    missing = [key for key in required if package.get(key) is None]
    nested = {
        "network": (
            "topology", "endpoint_ports_per_unit", "nics_per_unit", "switch_ports",
            "max_port_utilization", "redundant_switches", "optics_per_endpoint",
            "cables_per_endpoint", "blocking_ratio",
        ),
        "storage_capability": (
            "fast_capacity_pb_per_appliance", "fast_read_gb_s_per_appliance",
            "fast_write_gb_s_per_appliance", "metadata_million_inodes_per_appliance",
            "archive_capacity_pb_per_appliance", "minimum_controller_count",
            "controllers_per_appliance", "appliances_per_rack",
        ),
        "service_sizing": (
            "login_min_nodes", "concurrent_users_per_login_node", "management_min_nodes",
            "compute_units_per_management_node", "monitoring_min_nodes",
            "compute_units_per_monitoring_node", "provisioning_min_nodes",
            "compute_units_per_provisioning_node", "scheduler_min_nodes",
            "authentication_min_nodes", "nodes_per_rack",
        ),
        "power_profile": (
            "switch_kw", "nic_kw", "fast_storage_appliance_kw",
            "archive_storage_appliance_kw", "service_node_kw",
        ),
    }
    for group, keys in nested.items():
        values = package.get(group, {})
        for key in keys:
            value = values.get(key)
            if value is None or (key == "topology" and value == ""):
                missing.append(f"{group}.{key}")
    return missing


def gap_records(
    request: dict[str, Any],
    assessment: dict[str, Any] | None,
    package: dict[str, Any] | None,
    availability_matches_date: bool,
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []

    def add(gap_id: str, scope: str, ja: str, en: str, missing: list[str]) -> None:
        records.append({
            "gap_id": gap_id, "scope": scope, "statement_ja": ja,
            "statement_en": en, "missing_items": missing,
        })

    costs = missing_cost_scopes(package, request["deployment_mode"])
    if costs:
        add("GAP-GPUCFG-001", "cost", "構成要素別の価格区間が不足しています。", "Component price intervals are incomplete.", costs)
    availability_ok = (
        assessment is not None
        and assessment["availability_status"] == "eligible"
        and (
            assessment.get("latest_delivery_date") is None
            or assessment["latest_delivery_date"] <= request["schedule"]["required_acceptance_date"]
        )
    )
    if not availability_matches_date or not availability_ok:
        add("GAP-GPUCFG-002", "availability", "指定地域・受入日における調達可能性、納期、保守が確認できません。", "Procurement eligibility, delivery, and support are unconfirmed for the requested jurisdiction and acceptance date.", ["procurement-eligible date", "delivery lead time", "support status"])
    demands = demand_missing(request)
    if demands:
        add("GAP-GPUCFG-003", "demand", "ワークロードの絶対需要が不足しています。", "Absolute workload demand is incomplete.", demands)
    facility = request["facility"]
    if as_number(facility.get("it_power_limit_mw")) is None or facility.get("it_power_limit_status") in {"unknown", "unconfirmed"}:
        add("GAP-GPUCFG-004", "facility", "利用可能なIT電力が確認されていません。", "Available IT power is unconfirmed.", ["it_power_limit_mw"])
    if as_number(facility.get("cooling_capacity_mw")) is None or facility.get("cooling_capacity_status") in {"unknown", "unconfirmed"}:
        add("GAP-GPUCFG-005", "facility", "冷却能力が確認されていません。", "Cooling capacity is unconfirmed.", ["cooling_capacity_mw"])
    floor = [key for key in ("rack_limit", "floor_area_m2", "floor_loading_kg_m2", "rack_density_kw", "pue") if as_number(facility.get(key)) is None]
    if floor:
        add("GAP-GPUCFG-006", "facility", "ラック数、床面積または床荷重が不足しています。", "Rack, floor-area, or floor-loading limits are incomplete.", floor)
    storage = storage_missing(request)
    if storage:
        add("GAP-GPUCFG-007", "storage", "ストレージ容量、帯域または保護要件が不足しています。", "Storage capacity, bandwidth, or protection requirements are incomplete.", storage)
    inference = inference_missing(request)
    if inference:
        add("GAP-GPUCFG-008", "inference", "推論需要、待ち時間または品質条件が不足しています。", "Inference demand, latency, or quality requirements are incomplete.", inference)
    if not request.get("performance_model", {}).get("phase_baseline"):
        add("GAP-GPUCFG-009", "performance", "再現可能な実測基準と性能モデルがありません。", "A reproducible measured baseline and performance model are unavailable.", ["phase_baseline"])
    package_fields = package_missing(package)
    if package_fields:
        add("GAP-GPUCFG-011", "package", "最小調達単位の構成情報が不足しています。", "The minimum procurement-unit configuration is incomplete.", package_fields)
    return records


def quantities_for_units(
    request: dict[str, Any], package: dict[str, Any], units: int
) -> dict[str, Any]:
    network = package.get("network", {})
    storage = package.get("storage_capability", {})
    services = package.get("service_sizing", {})
    compute_racks = math.ceil(units / package["units_per_rack"])
    endpoint_ports = math.ceil(units * (as_number(network.get("endpoint_ports_per_unit")) or 0))
    usable_ports = math.floor(
        (as_number(network.get("switch_ports")) or 0)
        * (as_number(network.get("max_port_utilization")) or 1)
    )
    switch_count = (
        math.ceil(endpoint_ports / usable_ports)
        + math.ceil(as_number(network.get("redundant_switches")) or 0)
        if endpoint_ports > 0 and usable_ports > 0 else 0
    )
    fast_requirements = (
        (request["storage"]["shared_fast_capacity_pb"], storage.get("fast_capacity_pb_per_appliance")),
        (request["storage"]["training_read_gb_s"], storage.get("fast_read_gb_s_per_appliance")),
        (request["storage"]["checkpoint_write_gb_s"], storage.get("fast_write_gb_s_per_appliance")),
        (request["storage"]["metadata_million_inodes"], storage.get("metadata_million_inodes_per_appliance")),
    )
    fast_counts: list[int | None] = []
    for required, capacity in fast_requirements:
        if as_number(required) == 0:
            fast_counts.append(0)
        elif as_number(required) is not None and (as_number(capacity) or 0) > 0:
            fast_counts.append(math.ceil(required / capacity))
        else:
            fast_counts.append(None)
    fast_appliances = None if any(value is None for value in fast_counts) else max([0, *fast_counts])
    archive_capacity = as_number(storage.get("archive_capacity_pb_per_appliance"))
    archive_appliances = (
        0 if as_number(request["storage"]["archive_capacity_pb"]) == 0
        else math.ceil(request["storage"]["archive_capacity_pb"] / archive_capacity)
        if archive_capacity and archive_capacity > 0 else None
    )
    concurrent = (
        as_number(request["workloads"]["absolute_demand"].get("concurrent_users"))
        or as_number(request["inference"].get("concurrent_users"))
        or 0
    )

    def service_nodes(minimum: Any, per_load: Any, load: float) -> int:
        return max(
            math.ceil(as_number(minimum) or 0),
            math.ceil(load / per_load) if load > 0 and (as_number(per_load) or 0) > 0 else 0,
        )

    login_nodes = service_nodes(
        services.get("login_min_nodes", 2),
        services.get("concurrent_users_per_login_node", 100),
        concurrent,
    )
    management_nodes = max(
        math.ceil(as_number(services.get("management_min_nodes")) or 3),
        math.ceil(units / (as_number(services.get("compute_units_per_management_node")) or 1000)),
    )
    monitoring_nodes = max(
        math.ceil(as_number(services.get("monitoring_min_nodes")) or 2),
        math.ceil(units / (as_number(services.get("compute_units_per_monitoring_node")) or 1000)),
    )
    provisioning_nodes = max(
        math.ceil(as_number(services.get("provisioning_min_nodes")) or 2),
        math.ceil(units / (as_number(services.get("compute_units_per_provisioning_node")) or 1000)),
    )
    scheduler_nodes = max(math.ceil(as_number(services.get("scheduler_min_nodes")) or 2), 2)
    authentication_nodes = max(math.ceil(as_number(services.get("authentication_min_nodes")) or 2), 2)
    storage_controllers = (
        None if fast_appliances is None or archive_appliances is None else max(
            math.ceil(as_number(storage.get("minimum_controller_count")) or 2),
            math.ceil(
                (fast_appliances + archive_appliances)
                * (as_number(storage.get("controllers_per_appliance")) or 0)
            ),
        )
    )
    service_node_count = (
        login_nodes + management_nodes + monitoring_nodes + provisioning_nodes
        + scheduler_nodes + authentication_nodes + (storage_controllers or 0)
    )
    service_racks = math.ceil(service_node_count / (as_number(services.get("nodes_per_rack")) or 40))
    storage_racks = (
        None if fast_appliances is None or archive_appliances is None
        else math.ceil(
            (fast_appliances + archive_appliances)
            / (as_number(storage.get("appliances_per_rack")) or 4)
        )
    )
    rack_count = (
        None
        if storage_racks is None
        else compute_racks
        + (service_racks + storage_racks if package.get("include_auxiliary_racks") else 0)
    )
    return {
        "compute_units": units,
        "compute_nodes": units if package["unit_type"] == "node" else (
            None if as_number(package.get("nodes_per_unit")) is None
            else units * package["nodes_per_unit"]
        ),
        "compute_trays": units if package["unit_type"] == "tray" else (
            None if as_number(package.get("trays_per_unit")) is None
            else units * package["trays_per_unit"]
        ),
        "compute_racks": compute_racks,
        "gpu_count": units * package["gpus_per_unit"],
        "host_cpu_count": units * package["host_cpus_per_unit"],
        "total_hbm_gib": units * package["gpus_per_unit"] * package["hbm_gib_per_gpu"],
        "host_memory_gib": units * package["host_memory_gib_per_unit"],
        "local_nvme_tb": units * package["local_nvme_tb_per_unit"],
        "network_endpoints": endpoint_ports,
        "nic_count": math.ceil(units * (as_number(network.get("nics_per_unit")) or 0)),
        "switch_count": switch_count,
        "optic_count": math.ceil(endpoint_ports * (as_number(network.get("optics_per_endpoint")) or 0)),
        "cable_count": math.ceil(endpoint_ports * (as_number(network.get("cables_per_endpoint")) or 0)),
        "fast_storage_appliances": fast_appliances,
        "archive_storage_appliances": archive_appliances,
        "storage_controller_count": storage_controllers,
        "login_node_count": login_nodes,
        "management_node_count": management_nodes,
        "monitoring_node_count": monitoring_nodes,
        "provisioning_node_count": provisioning_nodes,
        "scheduler_node_count": scheduler_nodes,
        "authentication_node_count": authentication_nodes,
        "service_node_count": service_node_count,
        "service_racks": service_racks,
        "storage_racks": storage_racks,
        "rack_count": rack_count,
        "spare_compute_units": math.ceil(units * (as_number(package.get("spare_percent")) or 0) / 100),
    }


def power_for_quantities(quantities: dict[str, Any], package: dict[str, Any]) -> dict[str, float]:
    profile = package.get("power_profile", {})
    values = {
        "compute_kw": quantities["compute_units"] * package["power_kw_per_unit"],
        "network_kw": (
            quantities["switch_count"] * (as_number(profile.get("switch_kw")) or 0)
            + quantities["nic_count"] * (as_number(profile.get("nic_kw")) or 0)
        ),
        "storage_kw": (
            (quantities["fast_storage_appliances"] or 0)
            * (as_number(profile.get("fast_storage_appliance_kw")) or 0)
            + (quantities["archive_storage_appliances"] or 0)
            * (as_number(profile.get("archive_storage_appliance_kw")) or 0)
        ),
        "service_kw": (
            quantities["service_node_count"]
            * (as_number(profile.get("service_node_kw")) or 0)
        ),
    }
    values["total_kw"] = sum(values.values())
    return values


def quantity_for_basis(
    line: dict[str, Any],
    quantities: dict[str, Any],
    request: dict[str, Any],
    package: dict[str, Any],
) -> float | None:
    values = {
        "fixed": 1,
        "per-compute-unit": quantities["compute_units"],
        "per-rack": quantities["rack_count"],
        "per-fast-storage-appliance": quantities["fast_storage_appliances"],
        "per-archive-storage-appliance": quantities["archive_storage_appliances"],
        "per-network-switch": quantities["switch_count"],
        "per-nic": quantities["nic_count"],
        "per-optic": quantities["optic_count"],
        "per-cable": quantities["cable_count"],
        "per-service-node": quantities["service_node_count"],
        "per-storage-controller": quantities["storage_controller_count"],
        "per-fast-storage-pb": request["storage"]["shared_fast_capacity_pb"],
        "per-archive-storage-pb": request["storage"]["archive_capacity_pb"],
    }
    if line["basis"] == "per-it-kw":
        return power_for_quantities(quantities, package)["total_kw"]
    if line["basis"] not in values:
        raise ValueError(f"unsupported cost basis: {line['basis']}")
    return as_number(values[line["basis"]])


def itemized_cost(
    package: dict[str, Any],
    quantities: dict[str, Any],
    request: dict[str, Any],
    price_case: str,
    period: str,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for line in package.get("cost_lines", []):
        if line["period"] != period:
            continue
        unit_price = as_number(line.get(f"{price_case}_jpy"))
        quantity = quantity_for_basis(line, quantities, request, package)
        if unit_price is None or quantity is None:
            return {"total": None, "rows": rows, "missing": line["scope_id"]}
        rows.append({
            "scope_id": line["scope_id"],
            "category": line["category"],
            "basis": line["basis"],
            "quantity": quantity,
            "unit_price_jpy": unit_price,
            "subtotal_jpy": unit_price * quantity,
            "evidence_status": line["evidence_status"],
            "source_ids": line.get("source_ids", []),
        })
    return {"total": sum(row["subtotal_jpy"] for row in rows), "rows": rows, "missing": None}


def constraint(
    status: str,
    actual: Any,
    limit: Any,
    unit: str,
    shortfall: Any,
    detail: str,
) -> dict[str, Any]:
    return {
        "status": status, "actual": actual, "limit": limit,
        "unit": unit, "shortfall": shortfall, "detail": detail,
    }


def compare_constraint(
    actual: float | None,
    limit: float | None,
    unit: str,
    detail: str,
    direction: str = "max",
) -> dict[str, Any]:
    if actual is None or limit is None:
        return constraint("unknown", actual, limit, unit, None, detail)
    passed = actual <= limit if direction == "max" else actual >= limit
    shortfall = max(0, actual - limit) if direction == "max" else max(0, limit - actual)
    return constraint("pass" if passed else "fail", actual, limit, unit, shortfall, detail)


def constraints_for(
    request: dict[str, Any],
    package: dict[str, Any],
    quantities: dict[str, Any],
    assessment: dict[str, Any] | None,
) -> tuple[dict[str, dict[str, Any]], dict[str, float]]:
    power = power_for_quantities(quantities, package)
    facility = request["facility"]
    network = package.get("network", {})
    storage = package.get("storage_capability", {})
    floor_area = (
        None if quantities["rack_count"] is None
        else quantities["rack_count"] * package["rack_footprint_m2"]
    )
    floor_load = (
        package["rack_weight_kg"] / package["rack_footprint_m2"]
        if package["rack_footprint_m2"] > 0 else None
    )
    procurement = package.get("procurement_assumption", {})
    delivery_date = (
        assessment.get("latest_delivery_date") if assessment else None
    ) or procurement.get("latest_delivery_date")
    delivery_eligible = (
        (assessment is not None and assessment["availability_status"] == "eligible")
        or procurement.get("eligible") is True
    )
    max_switches = as_number(network.get("max_switch_count"))
    fast_appliances = quantities["fast_storage_appliances"]
    archive_appliances = quantities["archive_storage_appliances"]
    fast_capacity = (
        None if fast_appliances is None else fast_appliances
        * (as_number(storage.get("fast_capacity_pb_per_appliance")) or 0)
    )
    fast_read = (
        None if fast_appliances is None else fast_appliances
        * (as_number(storage.get("fast_read_gb_s_per_appliance")) or 0)
    )
    fast_write = (
        None if fast_appliances is None else fast_appliances
        * (as_number(storage.get("fast_write_gb_s_per_appliance")) or 0)
    )
    metadata = (
        None if fast_appliances is None else fast_appliances
        * (as_number(storage.get("metadata_million_inodes_per_appliance")) or 0)
    )
    archive_capacity = (
        None if archive_appliances is None else archive_appliances
        * (as_number(storage.get("archive_capacity_pb_per_appliance")) or 0)
    )
    demand_hours = as_number(
        request["workloads"]["absolute_demand"].get("annual_accelerator_hours")
    )
    utilization = (as_number(request["workloads"].get("utilization_target_percent")) or 0) / 100
    headroom = (as_number(request["workloads"].get("headroom_percent")) or 0) / 100
    available_hours = quantities["gpu_count"] * 8760 * utilization * max(0, 1 - headroom)
    delivery_status = (
        "pass"
        if delivery_eligible
        and delivery_date
        and delivery_date <= request["schedule"]["required_acceptance_date"]
        else "fail"
        if delivery_date and delivery_date > request["schedule"]["required_acceptance_date"]
        else "unknown"
    )
    values = {
        "it_power": compare_constraint(power["total_kw"], facility["it_power_limit_mw"] * 1000, "kW", "All modeled IT components"),
        "cooling": compare_constraint(power["total_kw"], facility["cooling_capacity_mw"] * 1000, "kW", request["deployment_mode"]),
        "rack_count": compare_constraint(quantities["rack_count"], facility["rack_limit"], "rack", "Compute, storage, and service racks"),
        "floor_area": compare_constraint(floor_area, facility["floor_area_m2"], "m2", "Rack footprint"),
        "floor_loading": compare_constraint(floor_load, facility["floor_loading_kg_m2"], "kg/m2", "Maximum modeled rack load"),
        "rack_density": compare_constraint(
            package["power_kw_per_unit"] * package["units_per_rack"],
            facility["rack_density_kw"],
            "kW/rack",
            "Compute-package rack density",
        ),
        "network_ports": (
            constraint("pass", quantities["switch_count"], None, "switch", 0, "No user limit")
            if max_switches is None else compare_constraint(
                quantities["switch_count"], max_switches, "switch",
                "Endpoint, port-utilization, and redundancy sizing",
            )
        ),
        "fast_storage_appliances": (
            constraint("pass", fast_appliances, None, "appliance", 0, "No user limit")
            if as_number(storage.get("max_fast_storage_appliances")) is None
            else compare_constraint(
                fast_appliances,
                storage["max_fast_storage_appliances"],
                "appliance",
                "Fast-storage appliance limit",
            )
        ),
        "archive_storage_appliances": (
            constraint("pass", archive_appliances, None, "appliance", 0, "No user limit")
            if as_number(storage.get("max_archive_storage_appliances")) is None
            else compare_constraint(
                archive_appliances,
                storage["max_archive_storage_appliances"],
                "appliance",
                "Archive-storage appliance limit",
            )
        ),
        "fast_capacity": compare_constraint(fast_capacity, request["storage"]["shared_fast_capacity_pb"], "PB", "Fast shared storage", "min"),
        "archive_capacity": compare_constraint(archive_capacity, request["storage"]["archive_capacity_pb"], "PB", "Archive storage", "min"),
        "storage_read": compare_constraint(fast_read, request["storage"]["training_read_gb_s"], "GB/s", "Training/data read", "min"),
        "storage_write": compare_constraint(fast_write, request["storage"]["checkpoint_write_gb_s"], "GB/s", "Checkpoint write", "min"),
        "metadata": compare_constraint(metadata, request["storage"]["metadata_million_inodes"], "million inodes", "Metadata capacity", "min"),
        "demand": (
            constraint("unknown", available_hours, None, "accelerator-hour/year", None, "Demand missing")
            if demand_hours is None else compare_constraint(
                available_hours, demand_hours, "accelerator-hour/year",
                "Utilization and headroom adjusted", "min",
            )
        ),
        "delivery": constraint(
            delivery_status, delivery_date,
            request["schedule"]["required_acceptance_date"],
            "date", None, "Jurisdiction/date-specific assessment",
        ),
    }
    return values, power


def erlang_c(arrival: float, service: float, servers: int) -> float | None:
    if arrival < 0 or service <= 0 or servers < 1 or arrival >= servers * service:
        return None
    offered_load = arrival / service
    term = 1.0
    total = 1.0
    for count in range(1, servers):
        term *= offered_load / count
        total += term
    term *= offered_load / servers
    tail = term / (1 - offered_load / servers)
    return tail / (total + tail)


def inference_performance(
    request: dict[str, Any],
    quantities: dict[str, Any] | None,
    baseline: dict[str, Any] | None,
) -> dict[str, Any]:
    arrival = as_number(request["inference"].get("request_rate_per_second"))
    if baseline is None or not quantities or not quantities["gpu_count"] or arrival is None:
        return {
            "status": "not-computable",
            "queue_model": "M/M/c (Erlang C)",
            "reason": "inference baseline or arrival rate missing",
        }
    service = as_number(baseline.get("service_rate_rps_per_gpu"))
    servers = quantities["gpu_count"]
    utilization = arrival / (servers * service) if service and service > 0 else None
    wait_probability = erlang_c(arrival, service, servers) if service else None
    if wait_probability is None:
        return {
            "status": "infeasible",
            "queue_model": "M/M/c (Erlang C)",
            "utilization": utilization,
            "reason": "arrival rate reaches or exceeds modeled service capacity",
        }

    def wait_ms(percentile: float) -> float:
        if wait_probability <= 1 - percentile:
            return 0
        return (
            -math.log((1 - percentile) / wait_probability)
            / (servers * service - arrival) * 1000
        )

    slowdown = 1 + max(0, utilization) * 0.1 / max(0.01, 1 - utilization)
    return {
        "status": baseline.get("status", "provisional"),
        "queue_model": "M/M/c (Erlang C)",
        "calibrated": baseline.get("status") == "validated",
        "arrival_rate_rps": arrival,
        "service_rate_rps_per_gpu": service,
        "servers": servers,
        "utilization": utilization,
        "wait_probability": wait_probability,
        "offline_throughput_rps": servers * service,
        "server_throughput_rps": min(arrival, servers * service),
        "ttft_ms": {
            "p50": baseline["base_ttft_ms"] + wait_ms(0.50),
            "p95": baseline["base_ttft_ms"] + wait_ms(0.95),
            "p99": baseline["base_ttft_ms"] + wait_ms(0.99),
        },
        "tpot_ms": {
            "p50": baseline["base_tpot_ms"] * slowdown,
            "p95": baseline["base_tpot_ms"] * slowdown * 1.1,
            "p99": baseline["base_tpot_ms"] * slowdown * 1.25,
        },
        "quality_target_id": request["inference"].get("quality_target_id"),
        "note": (
            "calibrated baseline"
            if baseline.get("status") == "validated"
            else "illustrative and uncalibrated"
        ),
    }


def performance(
    request: dict[str, Any],
    quantities: dict[str, Any] | None,
    price_case: str,
) -> dict[str, Any]:
    model = request.get("performance_model", {})
    baseline = model.get("phase_baseline")
    inference = model.get("inference_baseline")
    if baseline is None or not quantities or not quantities["compute_units"]:
        return {
            "status": "not-computable",
            "model": "phase-overlap",
            "bounds": None,
            "benchmark": None,
            "inference_queue": inference_performance(request, quantities, inference),
            "procurement_use": "prohibited",
            "reason": "measured baseline missing",
        }

    def build(name: str) -> dict[str, Any] | None:
        efficiency = as_number(baseline.get("scaling_efficiency", {}).get(name))
        if not efficiency or efficiency <= 0:
            return None
        scale = baseline["measured_compute_units"] / quantities["compute_units"] / efficiency
        compute = baseline["compute_time_s"] * scale
        memory = baseline["memory_time_s"] * scale
        communication = baseline["communication_time_s"] * scale
        io = baseline["io_time_s"] * scale
        phase = max(compute, memory, communication, io)
        non_overlap = baseline["non_overlappable_time_s"] * scale
        synchronization = baseline["synchronization_time_s"] * scale
        predicted = phase + non_overlap + synchronization
        error_percent = as_number(baseline.get("error_percent", {}).get(name)) or 0
        return {
            "case": name,
            "compute_time_s": compute,
            "memory_time_s": memory,
            "communication_time_s": communication,
            "io_time_s": io,
            "overlappable_phase_time_s": phase,
            "non_overlappable_time_s": non_overlap,
            "synchronization_time_s": synchronization,
            "predicted_time_s": predicted,
            "prediction_interval_s": [
                predicted * max(0, 1 - error_percent / 100),
                predicted * (1 + error_percent / 100),
            ],
            "extrapolation_ratio": quantities["compute_units"] / baseline["measured_compute_units"],
            "scaling_efficiency": efficiency,
            "error_percent": error_percent,
        }

    return {
        "status": baseline.get("status", "provisional"),
        "model": "T_phase=max(T_compute,T_memory,T_communication,T_IO); T_pred=T_phase+T_nonoverlap+T_synchronization",
        "bounds": {name: build(name) for name in PRICE_CASES},
        "selected_bound": price_case,
        "benchmark": baseline.get("benchmark"),
        "software_stack": baseline.get("software_stack", []),
        "measured_configuration": baseline.get("measured_configuration"),
        "source_kind": baseline.get("source_kind", "user-assumption"),
        "source_ids": baseline.get("source_ids", []),
        "inference_queue": inference_performance(request, quantities, inference),
        "procurement_use": "prohibited",
    }


def evaluate_case(
    vendor: str,
    request: dict[str, Any],
    package: dict[str, Any] | None,
    assessment: dict[str, Any] | None,
    price_case: str,
    gaps: list[dict[str, Any]],
) -> dict[str, Any]:
    budget = request["budget"]["capex_ceiling_oku_jpy"] * 100_000_000
    reserve_ratio = request["budget"]["contingency_percent"] / 100

    def blocked(
        reason: str,
        quantities: dict[str, Any] | None = None,
        constraints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        return {
            "case_ref": f"{vendor}-{price_case}",
            "price_case": price_case,
            "status": "blocked",
            "blocking_reason": reason,
            "unit_type": package.get("unit_type") if package else None,
            "quantities": quantities,
            "power": None,
            "costs": {
                "configuration_cost_jpy": None,
                "contingency_jpy": None,
                "unused_budget_jpy": None,
                "budget_ceiling_jpy": budget,
                "identity_verified": None,
                "line_items": [],
            },
            "tco": {
                "years": request["budget"]["tco_years"],
                "initial_capex_jpy": None,
                "recurring_cost_jpy": None,
                "end_of_horizon_cost_jpy": None,
                "total_tco_jpy": None,
                "complete": False,
                "annual_breakdown": [],
            },
            "constraints": constraints or {},
            "performance": performance(request, quantities, price_case),
            "gap_ids": [item["gap_id"] for item in gaps],
        }

    if package is None:
        return blocked("component-cost-package-missing")
    if missing_cost_scopes(package, request["deployment_mode"]) or package_missing(package):
        return blocked("required-package-or-price-input-missing")

    compute_line = next(
        (
            line for line in package["cost_lines"]
            if line["category"] == "compute" and line["period"] == "initial"
        ),
        None,
    )
    per_unit = as_number(compute_line.get(f"{price_case}_jpy")) if compute_line else budget
    hard_upper = min(100_000, max(1, math.floor(budget / max(1, per_unit or budget)) + 100))
    best: dict[str, Any] | None = None
    last: dict[str, Any] | None = None
    stop_constraints = {
        "budget", "it_power", "cooling", "rack_count",
        "floor_area", "floor_loading", "rack_density", "network_ports",
        "fast_storage_appliances", "archive_storage_appliances",
    }
    for units in range(1, hard_upper + 1):
        quantities = quantities_for_units(request, package, units)
        constraints, power = constraints_for(request, package, quantities, assessment)
        initial = itemized_cost(package, quantities, request, price_case, "initial")
        contingency = (
            None if initial["total"] is None else initial["total"] * reserve_ratio
        )
        constraints["budget"] = constraint(
            "pass"
            if initial["total"] is not None
            and initial["total"] + contingency <= budget
            else "fail",
            None if initial["total"] is None else initial["total"] + contingency,
            budget,
            "JPY",
            None
            if initial["total"] is None
            else max(0, initial["total"] + contingency - budget),
            "Configuration plus contingency",
        )
        state = {
            "quantities": quantities,
            "constraints": constraints,
            "power": power,
            "initial": initial,
            "contingency": contingency,
        }
        last = state
        if all(item["status"] == "pass" for item in constraints.values()):
            best = state
        if any(
            constraints[key]["status"] == "fail"
            for key in stop_constraints
        ):
            break

    if best is None:
        return blocked(
            "no-integer-configuration-satisfies-all-constraints",
            last["quantities"] if last else None,
            last["constraints"] if last else {},
        )

    quantities = best["quantities"]
    initial = best["initial"]
    contingency = best["contingency"]
    unused = budget - initial["total"] - contingency
    annual = itemized_cost(package, quantities, request, price_case, "annual")
    end = itemized_cost(package, quantities, request, price_case, "end-of-horizon")
    tco_complete = (
        annual["total"] is not None
        and end["total"] is not None
        and not missing_cost_scopes(package, request["deployment_mode"])
    )
    recurring = annual["total"] * request["budget"]["tco_years"] if tco_complete else None
    total_tco = (
        initial["total"] + contingency + recurring + end["total"]
        if tco_complete else None
    )
    modeled_performance = performance(request, quantities, price_case)
    return {
        "case_ref": f"{vendor}-{price_case}",
        "price_case": price_case,
        "status": (
            "partial"
            if gaps or modeled_performance["status"] != "validated"
            else "feasible"
        ),
        "blocking_reason": None,
        "unit_type": package["unit_type"],
        "quantities": quantities,
        "power": best["power"],
        "costs": {
            "configuration_cost_jpy": initial["total"],
            "contingency_jpy": contingency,
            "unused_budget_jpy": unused,
            "budget_ceiling_jpy": budget,
            "identity_verified": math.isclose(
                initial["total"] + contingency + unused,
                budget,
                abs_tol=0.01,
            ),
            "line_items": initial["rows"],
        },
        "tco": {
            "years": request["budget"]["tco_years"],
            "initial_capex_jpy": initial["total"] + contingency,
            "recurring_cost_jpy": recurring,
            "end_of_horizon_cost_jpy": end["total"],
            "total_tco_jpy": total_tco,
            "complete": tco_complete,
            "annual_breakdown": annual["rows"],
        },
        "constraints": best["constraints"],
        "performance": modeled_performance,
        "gap_ids": [item["gap_id"] for item in gaps],
    }


def compute_pareto(
    request: dict[str, Any],
    candidates: list[dict[str, Any]],
) -> dict[str, Any]:
    objectives = request.get("objectives", [])
    if request["vendor_mode"] != "auto-pareto":
        return {
            "status": "not-requested", "objectives": objectives,
            "candidate_refs": [], "reason_ja": "Pareto表示は選択されていません。",
            "reason_en": "Pareto display was not selected.",
        }
    baseline_cases = [
        (candidate, next(case for case in candidate["cases"] if case["price_case"] == "baseline"))
        for candidate in candidates
        if any(case["price_case"] == "baseline" and case["status"] != "blocked" for case in candidate["cases"])
    ]

    def metric_value(metric: str, candidate: dict[str, Any], case: dict[str, Any]) -> float | None:
        if metric == "validated-workload-throughput":
            return (
                1 / case["performance"]["bounds"]["baseline"]["predicted_time_s"]
                if case["performance"]["status"] == "validated" else None
            )
        if metric == "capex-jpy":
            return case["costs"]["configuration_cost_jpy"] + case["costs"]["contingency_jpy"]
        if metric == "tco-jpy":
            return case["tco"]["total_tco_jpy"]
        if metric == "it-power-kw":
            return case["power"]["total_kw"]
        if metric == "delivery-risk":
            return {
                "eligible": 0, "conditional": 1, "unknown": 2,
                "ineligible": 3, "not-assessed": 3, "user-assumption": 2,
            }[candidate["availability_status"]]
        if metric == "portability-risk":
            return as_number(candidate.get("portability_risk_score"))
        raise KeyError(metric)

    supported = {
        "validated-workload-throughput", "capex-jpy", "tco-jpy",
        "it-power-kw", "delivery-risk", "portability-risk",
    }
    unsupported = [item["metric"] for item in objectives if item["metric"] not in supported]
    if unsupported:
        return {
            "status": "not-evaluable", "objectives": objectives, "candidate_refs": [],
            "reason_ja": "未対応の目的関数: " + ", ".join(unsupported),
            "reason_en": "Unsupported objectives: " + ", ".join(unsupported),
        }
    vectors = [
        (case["case_ref"], [metric_value(item["metric"], candidate, case) for item in objectives])
        for candidate, case in baseline_cases
    ]
    missing = [
        item["metric"]
        for index, item in enumerate(objectives)
        if any(vector[index] is None for _, vector in vectors)
    ]
    if not vectors or missing:
        suffix = ", ".join(missing) if missing else "no candidates"
        return {
            "status": "not-evaluable", "objectives": objectives, "candidate_refs": [],
            "reason_ja": "検証済みの値がない目的関数: " + suffix,
            "reason_en": "Objectives without validated values: " + suffix,
        }

    def dominates(left: list[float], right: list[float]) -> bool:
        strict = False
        for index, objective in enumerate(objectives):
            maximize = objective["direction"] == "maximize"
            if (maximize and left[index] < right[index]) or (
                not maximize and left[index] > right[index]
            ):
                return False
            if (maximize and left[index] > right[index]) or (
                not maximize and left[index] < right[index]
            ):
                strict = True
        return strict

    frontier = [
        reference
        for reference, vector in vectors
        if not any(
            other_reference != reference and dominates(other, vector)
            for other_reference, other in vectors
        )
    ]
    return {
        "status": "computed", "objectives": objectives,
        "candidate_refs": frontier,
        "reason_ja": "明示した目的関数による重みなし非劣解です。単一の最適解ではありません。",
        "reason_en": "This is an unweighted non-dominated set for the explicit objectives, not a single optimum.",
    }


def evaluate(
    request: dict[str, Any],
    architecture: dict[str, Any],
    catalog: dict[str, Any],
    availability: dict[str, Any],
    cost_input: dict[str, Any] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    request = json.loads(json.dumps(request))
    request.setdefault("run_mode", "public-evidence")
    mix_total = sum(request["workloads"]["mix_percent"].values())
    if not math.isclose(mix_total, 100, abs_tol=1e-9):
        raise ValueError(f"workload mix must total 100, got {mix_total}")
    if request["architecture_id"] != architecture["architecture_id"]:
        raise ValueError("architecture mismatch")
    packages = {
        (item["vendor"], item["product_id"]): item
        for item in (cost_input or {}).get("packages", [])
    }
    availability_matches_date = (
        availability["required_acceptance_date"]
        == request["schedule"]["required_acceptance_date"]
    )
    candidates: list[dict[str, Any]] = []
    for vendor in requested_vendors(request["vendor_mode"]):
        product, raw_assessment = select_product(vendor, catalog, availability, request)
        assessment = raw_assessment if availability_matches_date else None
        package = packages.get((vendor, product["product_id"])) if product else None
        if package is None:
            package = next(
                (
                    item for item in (cost_input or {}).get("packages", [])
                    if item["vendor"] == vendor and item.get("allow_product_override")
                ),
                None,
            )
        gaps = gap_records(
            request, assessment, package, availability_matches_date
        )
        if request["run_mode"] == "public-evidence":
            blocking_ids = [
                item["gap_id"] for item in gaps if item["gap_id"] != "GAP-GPUCFG-009"
            ]
        else:
            what_if_blockers = {
                "GAP-GPUCFG-001", "GAP-GPUCFG-003", "GAP-GPUCFG-004",
                "GAP-GPUCFG-005", "GAP-GPUCFG-006", "GAP-GPUCFG-007",
                "GAP-GPUCFG-008", "GAP-GPUCFG-011",
            }
            blocking_ids = [
                item["gap_id"] for item in gaps if item["gap_id"] in what_if_blockers
            ]
        effective_package = None if blocking_ids else package
        effective_gaps = [
            item for item in gaps
            if item["gap_id"] == "GAP-GPUCFG-009"
            or (
                item["gap_id"] == "GAP-GPUCFG-002"
                and request["run_mode"] == "public-evidence"
            )
        ]
        cases = [
            evaluate_case(
                vendor,
                request,
                effective_package,
                assessment,
                price_case,
                gaps if blocking_ids else effective_gaps,
            )
            for price_case in PRICE_CASES
        ]
        availability_status = (
            assessment["availability_status"]
            if assessment else
            "user-assumption"
            if package and package.get("procurement_assumption", {}).get("eligible")
            else "not-assessed"
        )
        candidates.append({
            "vendor": vendor,
            "product_id": (
                product["product_id"] if product else
                package.get("product_id") if package else None
            ),
            "product_name": (
                product["model"] if product else
                package.get("product_label") if package else None
            ),
            "availability_status": availability_status,
            "status": (
                "blocked" if all(item["status"] == "blocked" for item in cases)
                else "partial"
            ),
            "software_profile": next(
                (
                    item for item in architecture["vendor_profiles"]
                    if item["vendor"] == vendor
                ),
                None,
            ),
            "portability_risk_score": (
                package.get("portability_risk_score") if package else None
            ),
            "cases": cases,
            "gaps": gaps,
        })
    return {
        "schema_version": "0.2.0",
        "result_id": "CFGRESULT-" + request["request_id"].removeprefix("PLANREQ-"),
        "status": (
            "blocked"
            if all(item["status"] == "blocked" for item in candidates)
            else "partial"
        ),
        "research_status": "provisional",
        "consensus_status": "incomplete",
        "procurement_use": "prohibited",
        "calculation_mode": request["run_mode"],
        "request_id": request["request_id"],
        "architecture_id": architecture["architecture_id"],
        "product_catalog_id": catalog["catalog_id"],
        "availability_assessment_id": availability["assessment_id"],
        "cost_input_id": cost_input["cost_input_id"] if cost_input else None,
        "generated_at": generated_at or datetime.now(timezone.utc).replace(
            microsecond=0
        ).isoformat().replace("+00:00", "Z"),
        "engine_version": ENGINE_VERSION,
        "vendor_candidates": candidates,
        "pareto_result": compute_pareto(request, candidates),
        "benchmark_candidates": list(BENCHMARKS),
        "messages_ja": [
            "単一のAIモデル・単一のAIエージェントによる暫定Candidateで、Consensus Gateは未完了です。",
            (
                "利用者入力による試算です。調達判断には使用できません。"
                if request["run_mode"] == "what-if"
                else "公開根拠が不足する値は補間しません。"
            ),
        ],
        "messages_en": [
            "This is a provisional Candidate produced by one model and one agent; the Consensus Gate is incomplete.",
            (
                "This is a user-input what-if estimate and must not be used for procurement."
                if request["run_mode"] == "what-if"
                else "Values unsupported by public evidence are not interpolated."
            ),
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
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {args.output}: status={result['status']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
