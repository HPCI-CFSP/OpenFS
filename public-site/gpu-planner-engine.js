(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.OpenFSGpuPlanner = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const ENGINE_VERSION = "0.2.0";
  const PRICE_CASES = ["optimistic", "baseline", "conservative"];
  const BENCHMARKS = [
    "HPL", "HPL-MxP", "HPCG", "Graph500", "OSU Micro-Benchmarks",
    "GROMACS", "OpenFOAM", "MLPerf Training", "MLPerf Inference Datacenter",
    "MLPerf Storage"
  ];
  const REQUIRED_INITIAL = ["compute", "scale-up", "scale-out", "network", "fast-storage", "archive-storage", "management", "software", "integration"];
  const REQUIRED_ANNUAL = ["maintenance", "spares", "energy", "operations"];

  const clone = (value) => JSON.parse(JSON.stringify(value));
  const number = (value) => value == null || value === "" || !Number.isFinite(Number(value)) ? null : Number(value);
  const ceilDiv = (value, divisor) => divisor > 0 ? Math.ceil(value / divisor) : null;
  const vendors = (mode) => mode === "compare" || mode === "auto-pareto" ? ["NVIDIA", "AMD"] : [mode];

  function lastEvent(product) {
    return (product.events || []).map((item) => item.date.value).sort().at(-1) || "0000-00-00";
  }

  function productUnitComplete(product) {
    return (product.procurement_units || []).some((unit) =>
      unit.gpus_per_unit != null && unit.host_cpus_per_unit != null && unit.units_per_rack != null
    );
  }

  function selectProduct(vendor, catalog, availability, request) {
    const requiredDate = request.schedule.required_acceptance_date;
    const selected = request.product_selection?.[vendor.toLowerCase()] || "auto";
    const assessments = Object.fromEntries((availability.assessments || []).map((item) => [item.product_id, item]));
    const candidates = catalog.products.filter((item) => item.vendor === vendor);
    if (selected !== "auto") {
      const product = candidates.find((item) => item.product_id === selected) || null;
      return [product, product ? assessments[product.product_id] || null : null];
    }
    const hpcWeight = request.workloads.mix_percent.ai_for_science_hpc || 0;
    const score = (product) => {
      const assessment = assessments[product.product_id];
      const dated = lastEvent(product) <= requiredDate ? 1 : 0;
      const eligible = assessment?.availability_status === "eligible" &&
        (!assessment.latest_delivery_date || assessment.latest_delivery_date <= requiredDate) ? 8 : 0;
      const unit = productUnitComplete(product) ? 4 : 0;
      const fp64 = hpcWeight > 0 && product.technical_specs?.fp64_tflops != null ? 2 : 0;
      const hbm = product.technical_specs?.hbm_capacity_gib != null ? 1 : 0;
      return [eligible + unit + fp64 + hbm + dated, product.generation_rank || 0, lastEvent(product)];
    };
    candidates.sort((left, right) => {
      const a = score(left); const b = score(right);
      return b[0] - a[0] || b[1] - a[1] || b[2].localeCompare(a[2]);
    });
    const product = candidates[0] || null;
    return [product, product ? assessments[product.product_id] || null : null];
  }

  function requiredCostCategories(deploymentMode) {
    const initial = [...REQUIRED_INITIAL];
    const annual = [...REQUIRED_ANNUAL];
    if (deploymentMode === "on-premises" || deploymentMode === "hybrid") initial.push("facility");
    if (deploymentMode === "external-hosting" || deploymentMode === "hybrid") annual.push("hosting");
    return {initial, annual, end: ["decommissioning"]};
  }

  function missingCostScopes(packageInfo, deploymentMode) {
    if (!packageInfo) return ["component-cost-package"];
    const required = requiredCostCategories(deploymentMode);
    const missing = [];
    for (const [periodKey, categories] of Object.entries(required)) {
      const period = periodKey === "end" ? "end-of-horizon" : periodKey;
      for (const category of categories) {
        const line = (packageInfo.cost_lines || []).find((item) => item.period === period && item.category === category);
        if (!line || PRICE_CASES.some((name) => number(line[name + "_jpy"]) == null)) missing.push(period + ":" + category);
      }
    }
    return missing;
  }

  function demandMissing(request) {
    const mix = request.workloads.mix_percent;
    const demand = request.workloads.absolute_demand;
    const keys = ["annual_accelerator_hours"];
    if (mix.ai_training > 0) keys.push("training_tokens_per_year", "training_jobs_per_year");
    if (mix.ai_inference > 0) keys.push("inference_requests_per_year", "peak_requests_per_second");
    if (mix.ai_for_science_hpc > 0) keys.push("hpc_jobs_per_year", "hpc_accelerators_per_job", "hpc_mean_runtime_hours");
    if (mix.data_analytics > 0) keys.push("data_ingest_pb_per_year");
    return [...new Set(keys)].filter((key) => number(demand[key]) == null);
  }

  function storageMissing(request) {
    const required = ["shared_fast_capacity_pb", "archive_capacity_pb", "training_read_gb_s", "checkpoint_write_gb_s", "metadata_million_inodes", "retention_years", "rto_hours", "local_nvme_tb_per_compute_unit"];
    return required.filter((key) => number(request.storage[key]) == null);
  }

  function inferenceMissing(request) {
    if ((request.workloads.mix_percent.ai_inference || 0) <= 0) return [];
    const required = ["model_name", "parameter_count_billion", "quantization", "input_tokens", "output_tokens", "context_tokens", "concurrent_users", "request_rate_per_second", "ttft_p50_ms", "ttft_p95_ms", "ttft_p99_ms", "tpot_p50_ms", "tpot_p95_ms", "tpot_p99_ms", "offline_throughput_target", "server_throughput_target", "quality_target_id"];
    return required.filter((key) => request.inference[key] == null || request.inference[key] === "");
  }

  function packageMissing(packageInfo) {
    if (!packageInfo) return ["package"];
    const required = ["unit_type", "gpus_per_unit", "host_cpus_per_unit", "units_per_rack", "power_kw_per_unit", "hbm_gib_per_gpu", "host_memory_gib_per_unit", "local_nvme_tb_per_unit", "rack_footprint_m2", "rack_weight_kg"];
    const missing = required.filter((key) => packageInfo[key] == null);
    const nested = {
      network: ["topology", "endpoint_ports_per_unit", "nics_per_unit", "switch_ports", "max_port_utilization", "redundant_switches", "optics_per_endpoint", "cables_per_endpoint", "blocking_ratio"],
      storage_capability: ["fast_capacity_pb_per_appliance", "fast_read_gb_s_per_appliance", "fast_write_gb_s_per_appliance", "metadata_million_inodes_per_appliance", "archive_capacity_pb_per_appliance", "minimum_controller_count", "controllers_per_appliance", "appliances_per_rack"],
      service_sizing: ["login_min_nodes", "concurrent_users_per_login_node", "management_min_nodes", "compute_units_per_management_node", "monitoring_min_nodes", "compute_units_per_monitoring_node", "provisioning_min_nodes", "compute_units_per_provisioning_node", "scheduler_min_nodes", "authentication_min_nodes", "nodes_per_rack"],
      power_profile: ["switch_kw", "nic_kw", "fast_storage_appliance_kw", "archive_storage_appliance_kw", "service_node_kw"]
    };
    for (const [group, keys] of Object.entries(nested)) {
      for (const key of keys) {
        const value = packageInfo[group]?.[key];
        if (value == null || (key === "topology" && value === "")) missing.push(group + "." + key);
      }
    }
    return missing;
  }

  function gapRecords(request, assessment, packageInfo, availabilityMatchesDate) {
    const records = [];
    const add = (id, scope, ja, en, missing) => records.push({gap_id: id, scope, statement_ja: ja, statement_en: en, missing_items: missing});
    const costs = missingCostScopes(packageInfo, request.deployment_mode);
    if (costs.length) add("GAP-GPUCFG-001", "cost", "構成要素別の価格区間が不足しています。", "Component price intervals are incomplete.", costs);
    const availabilityOk = assessment?.availability_status === "eligible" && (!assessment.latest_delivery_date || assessment.latest_delivery_date <= request.schedule.required_acceptance_date);
    if (!availabilityMatchesDate || !availabilityOk) add("GAP-GPUCFG-002", "availability", "指定地域・受入日における調達可能性、納期、保守が確認できません。", "Procurement eligibility, delivery, and support are unconfirmed for the requested jurisdiction and acceptance date.", ["procurement-eligible date", "delivery lead time", "support status"]);
    const demands = demandMissing(request);
    if (demands.length) add("GAP-GPUCFG-003", "demand", "ワークロードの絶対需要が不足しています。", "Absolute workload demand is incomplete.", demands);
    const facility = request.facility;
    if (number(facility.it_power_limit_mw) == null || ["unknown", "unconfirmed"].includes(facility.it_power_limit_status)) add("GAP-GPUCFG-004", "facility", "利用可能なIT電力が確認されていません。", "Available IT power is unconfirmed.", ["it_power_limit_mw"]);
    if (number(facility.cooling_capacity_mw) == null || ["unknown", "unconfirmed"].includes(facility.cooling_capacity_status)) add("GAP-GPUCFG-005", "facility", "冷却能力が確認されていません。", "Cooling capacity is unconfirmed.", ["cooling_capacity_mw"]);
    const floor = ["rack_limit", "floor_area_m2", "floor_loading_kg_m2", "rack_density_kw", "pue"].filter((key) => number(facility[key]) == null);
    if (floor.length) add("GAP-GPUCFG-006", "facility", "ラック数、床面積または床荷重が不足しています。", "Rack, floor-area, or floor-loading limits are incomplete.", floor);
    const storage = storageMissing(request);
    if (storage.length) add("GAP-GPUCFG-007", "storage", "ストレージ容量、帯域または保護要件が不足しています。", "Storage capacity, bandwidth, or protection requirements are incomplete.", storage);
    const inference = inferenceMissing(request);
    if (inference.length) add("GAP-GPUCFG-008", "inference", "推論需要、待ち時間または品質条件が不足しています。", "Inference demand, latency, or quality requirements are incomplete.", inference);
    if (!request.performance_model?.phase_baseline) add("GAP-GPUCFG-009", "performance", "再現可能な実測基準と性能モデルがありません。", "A reproducible measured baseline and performance model are unavailable.", ["phase_baseline"]);
    const pkg = packageMissing(packageInfo);
    if (pkg.length) add("GAP-GPUCFG-011", "package", "最小調達単位の構成情報が不足しています。", "The minimum procurement-unit configuration is incomplete.", pkg);
    return records;
  }

  function quantitiesForUnits(request, packageInfo, units) {
    const network = packageInfo.network || {};
    const storage = packageInfo.storage_capability || {};
    const services = packageInfo.service_sizing || {};
    const computeRacks = ceilDiv(units, packageInfo.units_per_rack) || 0;
    const endpointPorts = Math.ceil(units * (number(network.endpoint_ports_per_unit) || 0));
    const usablePorts = Math.floor((number(network.switch_ports) || 0) * (number(network.max_port_utilization) || 1));
    const switchCount = endpointPorts > 0 && usablePorts > 0
      ? Math.ceil(endpointPorts / usablePorts) + Math.ceil(number(network.redundant_switches) || 0)
      : 0;
    const fastRequirements = [
      [request.storage.shared_fast_capacity_pb, storage.fast_capacity_pb_per_appliance],
      [request.storage.training_read_gb_s, storage.fast_read_gb_s_per_appliance],
      [request.storage.checkpoint_write_gb_s, storage.fast_write_gb_s_per_appliance],
      [request.storage.metadata_million_inodes, storage.metadata_million_inodes_per_appliance]
    ];
    const fastCounts = fastRequirements.map(([required, capacity]) =>
      number(required) === 0 ? 0 : (number(required) != null && number(capacity) > 0 ? Math.ceil(required / capacity) : null)
    );
    const fastAppliances = fastCounts.some((value) => value == null) ? null : Math.max(0, ...fastCounts);
    const archiveAppliances = number(request.storage.archive_capacity_pb) === 0
      ? 0
      : (number(storage.archive_capacity_pb_per_appliance) > 0 ? Math.ceil(request.storage.archive_capacity_pb / storage.archive_capacity_pb_per_appliance) : null);
    const concurrent = number(request.workloads.absolute_demand.concurrent_users) || number(request.inference.concurrent_users) || 0;
    const serviceNodes = (minimum, perLoad, load) => Math.max(Math.ceil(number(minimum) || 0), load > 0 && number(perLoad) > 0 ? Math.ceil(load / perLoad) : 0);
    const loginNodes = serviceNodes(services.login_min_nodes ?? 2, services.concurrent_users_per_login_node ?? 100, concurrent);
    const managementNodes = Math.max(Math.ceil(number(services.management_min_nodes) || 3), Math.ceil(units / (number(services.compute_units_per_management_node) || 1000)));
    const monitoringNodes = Math.max(Math.ceil(number(services.monitoring_min_nodes) || 2), Math.ceil(units / (number(services.compute_units_per_monitoring_node) || 1000)));
    const provisioningNodes = Math.max(Math.ceil(number(services.provisioning_min_nodes) || 2), Math.ceil(units / (number(services.compute_units_per_provisioning_node) || 1000)));
    const schedulerNodes = Math.max(Math.ceil(number(services.scheduler_min_nodes) || 2), 2);
    const authenticationNodes = Math.max(Math.ceil(number(services.authentication_min_nodes) || 2), 2);
    const storageControllers = (fastAppliances == null || archiveAppliances == null)
      ? null
      : Math.max(Math.ceil(number(storage.minimum_controller_count) || 2), Math.ceil((fastAppliances + archiveAppliances) * (number(storage.controllers_per_appliance) || 0)));
    const serviceNodeCount = loginNodes + managementNodes + monitoringNodes + provisioningNodes + schedulerNodes + authenticationNodes + (storageControllers || 0);
    const serviceRacks = Math.ceil(serviceNodeCount / (number(services.nodes_per_rack) || 40));
    const storageRacks = fastAppliances == null || archiveAppliances == null
      ? null
      : Math.ceil((fastAppliances + archiveAppliances) / (number(storage.appliances_per_rack) || 4));
    const rackCount = storageRacks == null
      ? null
      : computeRacks + (packageInfo.include_auxiliary_racks ? serviceRacks + storageRacks : 0);
    return {
      compute_units: units,
      compute_nodes: packageInfo.unit_type === "node" ? units : number(packageInfo.nodes_per_unit) == null ? null : units * packageInfo.nodes_per_unit,
      compute_trays: packageInfo.unit_type === "tray" ? units : number(packageInfo.trays_per_unit) == null ? null : units * packageInfo.trays_per_unit,
      compute_racks: computeRacks,
      gpu_count: units * packageInfo.gpus_per_unit,
      host_cpu_count: units * packageInfo.host_cpus_per_unit,
      total_hbm_gib: units * packageInfo.gpus_per_unit * packageInfo.hbm_gib_per_gpu,
      host_memory_gib: units * packageInfo.host_memory_gib_per_unit,
      local_nvme_tb: units * packageInfo.local_nvme_tb_per_unit,
      network_endpoints: endpointPorts,
      nic_count: Math.ceil(units * (number(network.nics_per_unit) || 0)),
      switch_count: switchCount,
      optic_count: Math.ceil(endpointPorts * (number(network.optics_per_endpoint) || 0)),
      cable_count: Math.ceil(endpointPorts * (number(network.cables_per_endpoint) || 0)),
      fast_storage_appliances: fastAppliances,
      archive_storage_appliances: archiveAppliances,
      storage_controller_count: storageControllers,
      login_node_count: loginNodes,
      management_node_count: managementNodes,
      monitoring_node_count: monitoringNodes,
      provisioning_node_count: provisioningNodes,
      scheduler_node_count: schedulerNodes,
      authentication_node_count: authenticationNodes,
      service_node_count: serviceNodeCount,
      service_racks: serviceRacks,
      storage_racks: storageRacks,
      rack_count: rackCount,
      spare_compute_units: Math.ceil(units * (number(packageInfo.spare_percent) || 0) / 100)
    };
  }

  function powerForQuantities(q, packageInfo) {
    const p = packageInfo.power_profile || {};
    const values = {
      compute_kw: q.compute_units * packageInfo.power_kw_per_unit,
      network_kw: q.switch_count * (number(p.switch_kw) || 0) + q.nic_count * (number(p.nic_kw) || 0),
      storage_kw: (q.fast_storage_appliances || 0) * (number(p.fast_storage_appliance_kw) || 0) +
        (q.archive_storage_appliances || 0) * (number(p.archive_storage_appliance_kw) || 0),
      service_kw: q.service_node_count * (number(p.service_node_kw) || 0)
    };
    values.total_kw = Object.values(values).reduce((sum, value) => sum + value, 0);
    return values;
  }

  function quantityForBasis(line, q, request, packageInfo) {
    const map = {
      fixed: 1,
      "per-compute-unit": q.compute_units,
      "per-rack": q.rack_count,
      "per-fast-storage-appliance": q.fast_storage_appliances,
      "per-archive-storage-appliance": q.archive_storage_appliances,
      "per-network-switch": q.switch_count,
      "per-nic": q.nic_count,
      "per-optic": q.optic_count,
      "per-cable": q.cable_count,
      "per-service-node": q.service_node_count,
      "per-storage-controller": q.storage_controller_count,
      "per-fast-storage-pb": request.storage.shared_fast_capacity_pb,
      "per-archive-storage-pb": request.storage.archive_capacity_pb
    };
    if (line.basis === "per-it-kw") return powerForQuantities(q, packageInfo).total_kw;
    if (!(line.basis in map)) throw new Error("Unsupported cost basis: " + line.basis);
    return number(map[line.basis]);
  }

  function itemizedCost(packageInfo, q, request, priceCase, period) {
    const rows = [];
    for (const line of packageInfo.cost_lines || []) {
      if (line.period !== period) continue;
      const unitPrice = number(line[priceCase + "_jpy"]);
      const quantity = quantityForBasis(line, q, request, packageInfo);
      if (unitPrice == null || quantity == null) return {total: null, rows, missing: line.scope_id};
      rows.push({
        scope_id: line.scope_id,
        category: line.category,
        basis: line.basis,
        quantity,
        unit_price_jpy: unitPrice,
        subtotal_jpy: unitPrice * quantity,
        evidence_status: line.evidence_status,
        source_ids: line.source_ids || []
      });
    }
    return {total: rows.reduce((sum, row) => sum + row.subtotal_jpy, 0), rows, missing: null};
  }

  function constraint(status, actual, limit, unit, shortfall, detail) {
    return {status, actual, limit, unit, shortfall, detail};
  }

  function constraintsFor(request, packageInfo, q, assessment) {
    const power = powerForQuantities(q, packageInfo);
    const facility = request.facility;
    const network = packageInfo.network || {};
    const storage = packageInfo.storage_capability || {};
    const floorArea = q.rack_count == null ? null : q.rack_count * packageInfo.rack_footprint_m2;
    const floorLoad = packageInfo.rack_footprint_m2 > 0 ? packageInfo.rack_weight_kg / packageInfo.rack_footprint_m2 : null;
    const deliveryDate = assessment?.latest_delivery_date || packageInfo.procurement_assumption?.latest_delivery_date || null;
    const deliveryEligible = assessment?.availability_status === "eligible" || packageInfo.procurement_assumption?.eligible === true;
    const maxSwitches = number(network.max_switch_count);
    const fastCap = q.fast_storage_appliances == null ? null : q.fast_storage_appliances * (number(storage.fast_capacity_pb_per_appliance) || 0);
    const fastRead = q.fast_storage_appliances == null ? null : q.fast_storage_appliances * (number(storage.fast_read_gb_s_per_appliance) || 0);
    const fastWrite = q.fast_storage_appliances == null ? null : q.fast_storage_appliances * (number(storage.fast_write_gb_s_per_appliance) || 0);
    const metadata = q.fast_storage_appliances == null ? null : q.fast_storage_appliances * (number(storage.metadata_million_inodes_per_appliance) || 0);
    const archiveCap = q.archive_storage_appliances == null ? null : q.archive_storage_appliances * (number(storage.archive_capacity_pb_per_appliance) || 0);
    const demandHours = number(request.workloads.absolute_demand.annual_accelerator_hours);
    const utilization = (number(request.workloads.utilization_target_percent) || 0) / 100;
    const headroom = (number(request.workloads.headroom_percent) || 0) / 100;
    const availableHours = q.gpu_count * 8760 * utilization * Math.max(0, 1 - headroom);
    const compare = (actual, limit, unit, detail, direction = "max") => {
      if (actual == null || limit == null) return constraint("unknown", actual, limit, unit, null, detail);
      const pass = direction === "max" ? actual <= limit : actual >= limit;
      const shortfall = direction === "max" ? Math.max(0, actual - limit) : Math.max(0, limit - actual);
      return constraint(pass ? "pass" : "fail", actual, limit, unit, shortfall, detail);
    };
    return {power, values: {
      it_power: compare(power.total_kw, facility.it_power_limit_mw * 1000, "kW", "All modeled IT components"),
      cooling: compare(power.total_kw, facility.cooling_capacity_mw * 1000, "kW", request.deployment_mode),
      rack_count: compare(q.rack_count, facility.rack_limit, "rack", "Compute, storage, and service racks"),
      floor_area: compare(floorArea, facility.floor_area_m2, "m2", "Rack footprint"),
      floor_loading: compare(floorLoad, facility.floor_loading_kg_m2, "kg/m2", "Maximum modeled rack load"),
      rack_density: compare(
        packageInfo.power_kw_per_unit * packageInfo.units_per_rack,
        facility.rack_density_kw,
        "kW/rack",
        "Compute-package rack density"
      ),
      network_ports: maxSwitches == null ? constraint("pass", q.switch_count, null, "switch", 0, "No user limit") : compare(q.switch_count, maxSwitches, "switch", "Endpoint, port-utilization, and redundancy sizing"),
      fast_storage_appliances: number(storage.max_fast_storage_appliances) == null
        ? constraint("pass", q.fast_storage_appliances, null, "appliance", 0, "No user limit")
        : compare(q.fast_storage_appliances, storage.max_fast_storage_appliances, "appliance", "Fast-storage appliance limit"),
      archive_storage_appliances: number(storage.max_archive_storage_appliances) == null
        ? constraint("pass", q.archive_storage_appliances, null, "appliance", 0, "No user limit")
        : compare(q.archive_storage_appliances, storage.max_archive_storage_appliances, "appliance", "Archive-storage appliance limit"),
      fast_capacity: compare(fastCap, request.storage.shared_fast_capacity_pb, "PB", "Fast shared storage", "min"),
      archive_capacity: compare(archiveCap, request.storage.archive_capacity_pb, "PB", "Archive storage", "min"),
      storage_read: compare(fastRead, request.storage.training_read_gb_s, "GB/s", "Training/data read", "min"),
      storage_write: compare(fastWrite, request.storage.checkpoint_write_gb_s, "GB/s", "Checkpoint write", "min"),
      metadata: compare(metadata, request.storage.metadata_million_inodes, "million inodes", "Metadata capacity", "min"),
      demand: demandHours == null ? constraint("unknown", availableHours, null, "accelerator-hour/year", null, "Demand missing") : compare(availableHours, demandHours, "accelerator-hour/year", "Utilization and headroom adjusted", "min"),
      delivery: constraint(
        deliveryEligible && deliveryDate && deliveryDate <= request.schedule.required_acceptance_date
          ? "pass"
          : deliveryDate && deliveryDate > request.schedule.required_acceptance_date ? "fail" : "unknown",
        deliveryDate,
        request.schedule.required_acceptance_date,
        "date",
        null,
        "Jurisdiction/date-specific assessment"
      )
    }};
  }

  function erlangC(arrival, service, servers) {
    if (!(arrival >= 0 && service > 0 && servers >= 1) || arrival >= servers * service) return null;
    const offeredLoad = arrival / service;
    let term = 1;
    let sum = 1;
    for (let count = 1; count < servers; count += 1) {
      term *= offeredLoad / count;
      sum += term;
    }
    term *= offeredLoad / servers;
    const tail = term / (1 - offeredLoad / servers);
    return tail / (sum + tail);
  }

  function inferencePerformance(request, quantities, baseline) {
    if (!baseline || !quantities?.gpu_count || number(request.inference.request_rate_per_second) == null) {
      return {status: "not-computable", queue_model: "M/M/c (Erlang C)", reason: "inference baseline or arrival rate missing"};
    }
    const arrival = request.inference.request_rate_per_second;
    const service = number(baseline.service_rate_rps_per_gpu);
    const servers = quantities.gpu_count;
    const utilization = service > 0 ? arrival / (servers * service) : null;
    const waitProbability = erlangC(arrival, service, servers);
    if (waitProbability == null) {
      return {status: "infeasible", queue_model: "M/M/c (Erlang C)", utilization, reason: "arrival rate reaches or exceeds modeled service capacity"};
    }
    const waitMs = (percentile) =>
      waitProbability <= 1 - percentile
        ? 0
        : -Math.log((1 - percentile) / waitProbability) / (servers * service - arrival) * 1000;
    const slowdown = 1 + Math.max(0, utilization) * 0.1 / Math.max(0.01, 1 - utilization);
    return {
      status: baseline.status || "provisional",
      queue_model: "M/M/c (Erlang C)",
      calibrated: baseline.status === "validated",
      arrival_rate_rps: arrival,
      service_rate_rps_per_gpu: service,
      servers,
      utilization,
      wait_probability: waitProbability,
      offline_throughput_rps: servers * service,
      server_throughput_rps: Math.min(arrival, servers * service),
      ttft_ms: {
        p50: baseline.base_ttft_ms + waitMs(0.50),
        p95: baseline.base_ttft_ms + waitMs(0.95),
        p99: baseline.base_ttft_ms + waitMs(0.99)
      },
      tpot_ms: {
        p50: baseline.base_tpot_ms * slowdown,
        p95: baseline.base_tpot_ms * slowdown * 1.1,
        p99: baseline.base_tpot_ms * slowdown * 1.25
      },
      quality_target_id: request.inference.quality_target_id,
      note: baseline.status === "validated" ? "calibrated baseline" : "illustrative and uncalibrated"
    };
  }

  function performance(request, quantities, priceCase) {
    const baseline = request.performance_model?.phase_baseline;
    const inference = request.performance_model?.inference_baseline;
    if (!baseline || !quantities?.compute_units) {
      return {
        status: "not-computable",
        model: "phase-overlap",
        bounds: null,
        benchmark: null,
        inference_queue: inferencePerformance(request, quantities, inference),
        procurement_use: "prohibited",
        reason: "measured baseline missing"
      };
    }
    const efficiencies = baseline.scaling_efficiency || {};
    const errors = baseline.error_percent || {};
    const build = (name) => {
      const efficiency = number(efficiencies[name]);
      if (!(efficiency > 0)) return null;
      const scale = baseline.measured_compute_units / quantities.compute_units / efficiency;
      const compute = baseline.compute_time_s * scale;
      const memory = baseline.memory_time_s * scale;
      const communication = baseline.communication_time_s * scale;
      const io = baseline.io_time_s * scale;
      const phase = Math.max(compute, memory, communication, io);
      const nonOverlap = baseline.non_overlappable_time_s * scale;
      const synchronization = baseline.synchronization_time_s * scale;
      const predicted = phase + nonOverlap + synchronization;
      const errorPercent = number(errors[name]) || 0;
      return {
        case: name,
        compute_time_s: compute,
        memory_time_s: memory,
        communication_time_s: communication,
        io_time_s: io,
        overlappable_phase_time_s: phase,
        non_overlappable_time_s: nonOverlap,
        synchronization_time_s: synchronization,
        predicted_time_s: predicted,
        prediction_interval_s: [
          predicted * Math.max(0, 1 - errorPercent / 100),
          predicted * (1 + errorPercent / 100)
        ],
        extrapolation_ratio: quantities.compute_units / baseline.measured_compute_units,
        scaling_efficiency: efficiency,
        error_percent: errorPercent
      };
    };
    return {
      status: baseline.status || "provisional",
      model: "T_phase=max(T_compute,T_memory,T_communication,T_IO); T_pred=T_phase+T_nonoverlap+T_synchronization",
      bounds: Object.fromEntries(PRICE_CASES.map((name) => [name, build(name)])),
      selected_bound: priceCase,
      benchmark: baseline.benchmark || null,
      software_stack: baseline.software_stack || [],
      measured_configuration: baseline.measured_configuration || null,
      source_kind: baseline.source_kind || "user-assumption",
      source_ids: baseline.source_ids || [],
      inference_queue: inferencePerformance(request, quantities, inference),
      procurement_use: "prohibited"
    };
  }

  function evaluateCase(vendor, request, packageInfo, assessment, priceCase, gaps) {
    const budget = request.budget.capex_ceiling_oku_jpy * 100000000;
    const reserveRatio = request.budget.contingency_percent / 100;
    const blocked = (reason, quantities = null, constraints = {}) => ({
      case_ref: vendor + "-" + priceCase,
      price_case: priceCase,
      status: "blocked",
      blocking_reason: reason,
      unit_type: packageInfo?.unit_type || null,
      quantities,
      power: null,
      costs: {
        configuration_cost_jpy: null,
        contingency_jpy: null,
        unused_budget_jpy: null,
        budget_ceiling_jpy: budget,
        identity_verified: null,
        line_items: []
      },
      tco: {
        years: request.budget.tco_years,
        initial_capex_jpy: null,
        recurring_cost_jpy: null,
        end_of_horizon_cost_jpy: null,
        total_tco_jpy: null,
        complete: false,
        annual_breakdown: []
      },
      constraints,
      performance: performance(request, quantities, priceCase),
      gap_ids: gaps.map((item) => item.gap_id)
    });
    if (!packageInfo) return blocked("component-cost-package-missing");
    if (missingCostScopes(packageInfo, request.deployment_mode).length || packageMissing(packageInfo).length) {
      return blocked("required-package-or-price-input-missing");
    }

    let best = null;
    let last = null;
    const computeLine = (packageInfo.cost_lines || []).find((line) => line.category === "compute" && line.period === "initial");
    const perUnit = number(computeLine?.[priceCase + "_jpy"]) || budget;
    const hardUpper = Math.min(100000, Math.max(1, Math.floor(budget / Math.max(1, perUnit)) + 100));
    for (let units = 1; units <= hardUpper; units += 1) {
      const quantities = quantitiesForUnits(request, packageInfo, units);
      const evaluated = constraintsFor(request, packageInfo, quantities, assessment);
      const initial = itemizedCost(packageInfo, quantities, request, priceCase, "initial");
      const contingency = initial.total == null ? null : initial.total * reserveRatio;
      evaluated.values.budget = constraint(
        initial.total != null && initial.total + contingency <= budget ? "pass" : "fail",
        initial.total == null ? null : initial.total + contingency,
        budget,
        "JPY",
        initial.total == null ? null : Math.max(0, initial.total + contingency - budget),
        "Configuration plus contingency"
      );
      const state = {quantities, evaluated, initial, contingency};
      last = state;
      if (Object.values(evaluated.values).every((item) => item.status === "pass")) best = state;
      if (["budget", "it_power", "cooling", "rack_count", "floor_area", "floor_loading", "rack_density", "network_ports", "fast_storage_appliances", "archive_storage_appliances"]
        .some((key) => evaluated.values[key].status === "fail")) break;
    }
    if (!best) {
      return blocked(
        "no-integer-configuration-satisfies-all-constraints",
        last?.quantities || null,
        last?.evaluated.values || {}
      );
    }

    const {quantities, evaluated, initial, contingency} = best;
    const unused = budget - initial.total - contingency;
    const annual = itemizedCost(packageInfo, quantities, request, priceCase, "annual");
    const end = itemizedCost(packageInfo, quantities, request, priceCase, "end-of-horizon");
    const tcoComplete = annual.total != null && end.total != null &&
      missingCostScopes(packageInfo, request.deployment_mode).length === 0;
    const recurring = tcoComplete ? annual.total * request.budget.tco_years : null;
    const totalTco = tcoComplete ? initial.total + contingency + recurring + end.total : null;
    const modeledPerformance = performance(request, quantities, priceCase);
    return {
      case_ref: vendor + "-" + priceCase,
      price_case: priceCase,
      status: gaps.length || modeledPerformance.status !== "validated" ? "partial" : "feasible",
      blocking_reason: null,
      unit_type: packageInfo.unit_type,
      quantities,
      power: evaluated.power,
      costs: {
        configuration_cost_jpy: initial.total,
        contingency_jpy: contingency,
        unused_budget_jpy: unused,
        budget_ceiling_jpy: budget,
        identity_verified: Math.abs(initial.total + contingency + unused - budget) < 0.01,
        line_items: initial.rows
      },
      tco: {
        years: request.budget.tco_years,
        initial_capex_jpy: initial.total + contingency,
        recurring_cost_jpy: recurring,
        end_of_horizon_cost_jpy: end.total,
        total_tco_jpy: totalTco,
        complete: tcoComplete,
        annual_breakdown: annual.rows
      },
      constraints: evaluated.values,
      performance: modeledPerformance,
      gap_ids: gaps.map((item) => item.gap_id)
    };
  }

  function pareto(request, candidates) {
    const objectives = request.objectives || [];
    const baselineCases = candidates
      .map((candidate) => [candidate, candidate.cases.find((value) => value.price_case === "baseline")])
      .filter(([, value]) => value && value.status !== "blocked");
    if (request.vendor_mode !== "auto-pareto") {
      return {
        status: "not-requested",
        objectives,
        candidate_refs: [],
        reason_ja: "Pareto表示は選択されていません。",
        reason_en: "Pareto display was not selected."
      };
    }
    const extractor = {
      "validated-workload-throughput": (_candidate, value) =>
        value.performance.status === "validated"
          ? 1 / value.performance.bounds.baseline.predicted_time_s
          : null,
      "capex-jpy": (_candidate, value) =>
        value.costs.configuration_cost_jpy + value.costs.contingency_jpy,
      "tco-jpy": (_candidate, value) => value.tco.total_tco_jpy,
      "it-power-kw": (_candidate, value) => value.power.total_kw,
      "delivery-risk": (candidate) => ({
        eligible: 0,
        conditional: 1,
        unknown: 2,
        ineligible: 3,
        "not-assessed": 3,
        "user-assumption": 2
      })[candidate.availability_status],
      "portability-risk": (candidate) => number(candidate.portability_risk_score)
    };
    const unsupported = objectives.filter((item) => !extractor[item.metric]).map((item) => item.metric);
    if (unsupported.length) {
      return {
        status: "not-evaluable",
        objectives,
        candidate_refs: [],
        reason_ja: "未対応の目的関数: " + unsupported.join(", "),
        reason_en: "Unsupported objectives: " + unsupported.join(", ")
      };
    }
    const vectors = baselineCases.map(([candidate, value]) => ({
      ref: value.case_ref,
      values: objectives.map((item) => extractor[item.metric](candidate, value))
    }));
    const missing = objectives
      .filter((_item, index) => vectors.some((value) => value.values[index] == null))
      .map((item) => item.metric);
    if (!vectors.length || missing.length) {
      return {
        status: "not-evaluable",
        objectives,
        candidate_refs: [],
        reason_ja: "検証済みの値がない目的関数: " + (missing.join(", ") || "候補なし"),
        reason_en: "Objectives without validated values: " + (missing.join(", ") || "no candidates")
      };
    }
    const dominates = (left, right) => {
      let strict = false;
      for (let index = 0; index < objectives.length; index += 1) {
        const maximize = objectives[index].direction === "maximize";
        if ((maximize && left[index] < right[index]) || (!maximize && left[index] > right[index])) return false;
        if ((maximize && left[index] > right[index]) || (!maximize && left[index] < right[index])) strict = true;
      }
      return strict;
    };
    const front = vectors
      .filter((item) => !vectors.some((other) => other.ref !== item.ref && dominates(other.values, item.values)))
      .map((item) => item.ref);
    return {
      status: "computed",
      objectives,
      candidate_refs: front,
      reason_ja: "明示した目的関数による重みなし非劣解です。単一の最適解ではありません。",
      reason_en: "This is an unweighted non-dominated set for the explicit objectives, not a single optimum."
    };
  }

  function evaluate(requestInput, architecture, catalog, availability, costInput, generatedAt) {
    const request = clone(requestInput);
    request.run_mode = request.run_mode || "public-evidence";
    const mixTotal = Object.values(request.workloads.mix_percent)
      .reduce((sum, value) => sum + Number(value), 0);
    if (Math.abs(mixTotal - 100) > 1e-9) {
      throw new Error("Workload mix must total 100, got " + mixTotal);
    }
    if (request.architecture_id !== architecture.architecture_id) {
      throw new Error("Architecture mismatch");
    }
    const packages = new Map(
      (costInput?.packages || []).map((item) => [item.vendor + "/" + item.product_id, item])
    );
    const availabilityMatchesDate =
      availability.required_acceptance_date === request.schedule.required_acceptance_date;
    const candidates = vendors(request.vendor_mode).map((vendor) => {
      const [product, rawAssessment] = selectProduct(vendor, catalog, availability, request);
      const assessment = availabilityMatchesDate ? rawAssessment : null;
      const packageInfo = product
        ? packages.get(vendor + "/" + product.product_id) ||
          (costInput?.packages || []).find((item) => item.vendor === vendor && item.allow_product_override)
        : null;
      const gaps = gapRecords(request, assessment, packageInfo, availabilityMatchesDate);
      const blockingIds = request.run_mode === "public-evidence"
        ? gaps.filter((item) => item.gap_id !== "GAP-GPUCFG-009").map((item) => item.gap_id)
        : gaps
          .filter((item) => [
            "GAP-GPUCFG-001", "GAP-GPUCFG-003", "GAP-GPUCFG-004",
            "GAP-GPUCFG-005", "GAP-GPUCFG-006", "GAP-GPUCFG-007",
            "GAP-GPUCFG-008", "GAP-GPUCFG-011"
          ].includes(item.gap_id))
          .map((item) => item.gap_id);
      const effectivePackage = blockingIds.length ? null : packageInfo;
      const effectiveGaps = gaps.filter((item) =>
        item.gap_id === "GAP-GPUCFG-009" ||
        (item.gap_id === "GAP-GPUCFG-002" && request.run_mode === "public-evidence")
      );
      const cases = PRICE_CASES.map((priceCase) =>
        evaluateCase(
          vendor,
          request,
          effectivePackage,
          assessment,
          priceCase,
          blockingIds.length ? gaps : effectiveGaps
        )
      );
      const availabilityStatus = assessment?.availability_status ||
        (packageInfo?.procurement_assumption?.eligible ? "user-assumption" : "not-assessed");
      return {
        vendor,
        product_id: product?.product_id || packageInfo?.product_id || null,
        product_name: product?.model || packageInfo?.product_label || null,
        availability_status: availabilityStatus,
        status: cases.every((item) => item.status === "blocked") ? "blocked" : "partial",
        software_profile: architecture.vendor_profiles.find((item) => item.vendor === vendor) || null,
        portability_risk_score: packageInfo?.portability_risk_score ?? null,
        cases,
        gaps
      };
    });
    return {
      schema_version: "0.2.0",
      result_id: "CFGRESULT-" + request.request_id.replace(/^PLANREQ-/, ""),
      status: candidates.every((item) => item.status === "blocked") ? "blocked" : "partial",
      research_status: "provisional",
      consensus_status: "incomplete",
      procurement_use: "prohibited",
      calculation_mode: request.run_mode,
      request_id: request.request_id,
      architecture_id: architecture.architecture_id,
      product_catalog_id: catalog.catalog_id,
      availability_assessment_id: availability.assessment_id,
      cost_input_id: costInput?.cost_input_id || null,
      generated_at: generatedAt || new Date().toISOString(),
      engine_version: ENGINE_VERSION,
      vendor_candidates: candidates,
      pareto_result: pareto(request, candidates),
      benchmark_candidates: BENCHMARKS,
      messages_ja: [
        "単一のAIモデル・単一のAIエージェントによる暫定Candidateで、Consensus Gateは未完了です。",
        request.run_mode === "what-if"
          ? "利用者入力による試算です。調達判断には使用できません。"
          : "公開根拠が不足する値は補間しません。"
      ],
      messages_en: [
        "This is a provisional Candidate produced by one model and one agent; the Consensus Gate is incomplete.",
        request.run_mode === "what-if"
          ? "This is a user-input what-if estimate and must not be used for procurement."
          : "Values unsupported by public evidence are not interpolated."
      ]
    };
  }

  return {
    ENGINE_VERSION,
    PRICE_CASES,
    BENCHMARKS,
    evaluate,
    selectProduct,
    quantitiesForUnits,
    itemizedCost,
    performance,
    erlangC
  };
});
