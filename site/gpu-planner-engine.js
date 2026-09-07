(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.OpenFSGpuPlanner = api;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  const PRICE_CASES = ["optimistic", "reference", "conservative"];

  function vendors(mode) {
    return mode === "compare" || mode === "auto-pareto" ? ["NVIDIA", "AMD"] : [mode];
  }

  function lastEvent(product) {
    return (product.events || []).map((item) => item.date.value).sort().at(-1) || "0000-00-00";
  }

  function selectProduct(vendor, catalog, availability, requiredDate) {
    const assessments = Object.fromEntries(availability.assessments.map((item) => [item.product_id, item]));
    let products = catalog.products.filter((item) => item.vendor === vendor && lastEvent(item) <= requiredDate);
    if (!products.length) products = catalog.products.filter((item) => item.vendor === vendor);
    products.sort((left, right) => right.generation_rank - left.generation_rank || lastEvent(right).localeCompare(lastEvent(left)));
    const eligible = products.filter((item) => {
      const assessment = assessments[item.product_id];
      return assessment?.availability_status === "eligible" &&
        (!assessment.latest_delivery_date || assessment.latest_delivery_date <= requiredDate);
    });
    eligible.sort((left, right) => right.generation_rank - left.generation_rank || lastEvent(right).localeCompare(lastEvent(left)));
    const product = eligible[0] || products[0] || null;
    return [product, product ? assessments[product.product_id] || null : null];
  }

  function workloadMissing(request) {
    const mix = request.workloads.mix_percent;
    const demand = request.workloads.absolute_demand;
    const keys = [];
    if (mix.ai_training > 0) keys.push("training_accelerator_hours_per_year", "training_tokens_per_year");
    if (mix.ai_for_science_hpc > 0) keys.push("hpc_jobs_per_year", "hpc_accelerator_hours_per_year");
    if (mix.data_analytics > 0) keys.push("data_ingest_pb_per_year");
    return keys.filter((key) => demand[key] == null);
  }

  function gaps(request, assessment, packageInfo) {
    const values = [];
    if (!packageInfo) values.push("GAP-GPUCFG-001");
    if (!assessment || assessment.availability_status !== "eligible") values.push("GAP-GPUCFG-002");
    if (workloadMissing(request).length) values.push("GAP-GPUCFG-003");
    const facility = request.facility;
    if (facility.it_power_limit_mw == null || facility.it_power_limit_status !== "confirmed") values.push("GAP-GPUCFG-004");
    if (facility.cooling_capacity_mw == null || facility.cooling_capacity_status !== "confirmed") values.push("GAP-GPUCFG-005");
    if (facility.rack_limit == null) values.push("GAP-GPUCFG-006");
    if (Object.values(request.storage).some((value) => value == null)) values.push("GAP-GPUCFG-007");
    if (request.workloads.mix_percent.ai_inference > 0 && Object.values(request.inference).some((value) => value == null)) values.push("GAP-GPUCFG-008");
    values.push("GAP-GPUCFG-009");
    return [...new Set(values)];
  }

  function multiplier(line, units, racks, request) {
    if (line.basis === "fixed") return 1;
    if (line.basis === "per-compute-unit") return units;
    if (line.basis === "per-rack") return racks;
    if (line.basis === "per-fast-storage-pb") return request.storage.shared_fast_capacity_pb || 0;
    if (line.basis === "per-archive-storage-pb") return request.storage.archive_capacity_pb || 0;
    throw new Error(`Unsupported cost basis: ${line.basis}`);
  }

  function packageCost(packageInfo, units, request, priceCase, period) {
    const racks = Math.ceil(units / packageInfo.units_per_rack);
    return packageInfo.cost_lines.filter((line) => line.period === period)
      .reduce((sum, line) => sum + line[`${priceCase}_jpy`] * multiplier(line, units, racks, request), 0);
  }

  function tcoComplete(packageInfo, deploymentMode) {
    const initial = new Set(packageInfo.cost_lines.filter((line) => line.period === "initial").map((line) => line.category));
    const annual = new Set(packageInfo.cost_lines.filter((line) => line.period === "annual").map((line) => line.category));
    const end = new Set(packageInfo.cost_lines.filter((line) => line.period === "end-of-horizon").map((line) => line.category));
    const requiredInitial = ["compute", "network", "storage", "management", "integration"];
    if (["on-premises", "hybrid"].includes(deploymentMode)) requiredInitial.push("facility");
    const requiredAnnual = ["maintenance", "energy", "staffing"];
    if (["external-hosting", "hybrid"].includes(deploymentMode)) requiredAnnual.push("hosting");
    return requiredInitial.every((item) => initial.has(item)) && requiredAnnual.every((item) => annual.has(item)) && end.has("decommissioning");
  }

  function maxUnits(request, packageInfo, priceCase) {
    const ceiling = request.budget.capex_ceiling_oku_jpy * 100000000;
    const ratio = request.budget.contingency_percent / 100;
    const upper = Math.max(0, Math.min(
      Math.floor(request.facility.it_power_limit_mw * 1000 / packageInfo.power_kw_per_unit),
      Math.floor(request.facility.cooling_capacity_mw * 1000 / packageInfo.power_kw_per_unit),
      request.facility.rack_limit * packageInfo.units_per_rack
    ));
    let low = 0;
    let high = upper;
    while (low < high) {
      const middle = Math.floor((low + high + 1) / 2);
      const cost = packageCost(packageInfo, middle, request, priceCase, "initial");
      if (cost * (1 + ratio) <= ceiling) low = middle;
      else high = middle - 1;
    }
    return low;
  }

  function performance(request) {
    return {
      status: "not-computable",
      compute_time_s: null,
      memory_time_s: null,
      communication_time_s: null,
      io_time_s: null,
      overlappable_time_s: null,
      non_overlappable_time_s: null,
      synchronization_time_s: null,
      predicted_time_s: null,
      inference_queue: {status: "not-computable", concurrent_users: request.inference.concurrent_users, ttft_p95_ms: null, tpot_p95_ms: null},
      procurement_use: "prohibited"
    };
  }

  function blockedCase(vendor, request, priceCase, gapIds, availabilityStatus) {
    return {
      case_ref: `${vendor}-${priceCase}`,
      price_case: priceCase,
      status: "blocked",
      unit_type: null,
      compute_units: null,
      gpu_count: null,
      host_cpu_count: null,
      rack_count: null,
      total_hbm_gib: null,
      it_power_kw: null,
      costs: {configuration_cost_jpy: null, contingency_jpy: null, unused_budget_jpy: null, budget_ceiling_jpy: request.budget.capex_ceiling_oku_jpy * 100000000, identity_verified: null},
      tco: {years: request.budget.tco_years, initial_capex_jpy: null, recurring_cost_jpy: null, end_of_horizon_cost_jpy: null, total_tco_jpy: null, complete: false},
      constraints: {budget: "unknown", it_power: "unknown", cooling: "unknown", rack_count: "unknown", delivery: availabilityStatus === "ineligible" ? "fail" : "unknown"},
      performance: performance(request),
      gap_ids: gapIds
    };
  }

  function pricedCase(vendor, request, packageInfo, priceCase, gapIds) {
    const units = maxUnits(request, packageInfo, priceCase);
    if (units < 1) return blockedCase(vendor, request, priceCase, gapIds, "eligible");
    const racks = Math.ceil(units / packageInfo.units_per_rack);
    const initial = packageCost(packageInfo, units, request, priceCase, "initial");
    const contingency = initial * request.budget.contingency_percent / 100;
    const budget = request.budget.capex_ceiling_oku_jpy * 100000000;
    const unused = budget - initial - contingency;
    const complete = tcoComplete(packageInfo, request.deployment_mode);
    const recurring = complete ? packageCost(packageInfo, units, request, priceCase, "annual") * request.budget.tco_years : null;
    const end = complete ? packageCost(packageInfo, units, request, priceCase, "end-of-horizon") : null;
    return {
      case_ref: `${vendor}-${priceCase}`,
      price_case: priceCase,
      status: gapIds.length ? "partial" : "feasible",
      unit_type: packageInfo.unit_type,
      compute_units: units,
      gpu_count: units * packageInfo.gpus_per_unit,
      host_cpu_count: units * packageInfo.host_cpus_per_unit,
      rack_count: racks,
      total_hbm_gib: units * packageInfo.gpus_per_unit * packageInfo.hbm_gib_per_gpu,
      it_power_kw: units * packageInfo.power_kw_per_unit,
      costs: {configuration_cost_jpy: initial, contingency_jpy: contingency, unused_budget_jpy: unused, budget_ceiling_jpy: budget, identity_verified: Math.abs(initial + contingency + unused - budget) < 0.01},
      tco: {years: request.budget.tco_years, initial_capex_jpy: initial + contingency, recurring_cost_jpy: recurring, end_of_horizon_cost_jpy: end, total_tco_jpy: recurring == null || end == null ? null : initial + contingency + recurring + end, complete},
      constraints: {budget: "pass", it_power: "pass", cooling: "pass", rack_count: "pass", delivery: "pass"},
      performance: performance(request),
      gap_ids: gapIds
    };
  }

  function pareto(request, candidates) {
    const cases = candidates.filter((item) => item.cases[1].status !== "blocked").map((item) => [item, item.cases[1]]);
    if (request.vendor_mode !== "auto-pareto" || !cases.length) return {status: "not-evaluable", candidate_refs: []};
    const extractors = {
      "total-hbm-gib": (_vendor, value) => value.total_hbm_gib,
      "capex-jpy": (_vendor, value) => value.costs.configuration_cost_jpy,
      "it-power-kw": (_vendor, value) => value.it_power_kw,
      "delivery-risk": (vendor) => ({eligible: 0, conditional: 1, unknown: 2, ineligible: 3, "not-assessed": 3})[vendor.availability_status]
    };
    if (request.objectives.some((item) => !extractors[item.metric])) return {status: "not-evaluable", candidate_refs: []};
    const vectors = cases.map(([vendor, value]) => [value.case_ref, request.objectives.map((item) => extractors[item.metric](vendor, value))]);
    if (vectors.some(([, vector]) => vector.some((value) => value == null))) return {status: "not-evaluable", candidate_refs: []};
    const dominates = (left, right) => {
      let strict = false;
      for (let index = 0; index < request.objectives.length; index += 1) {
        const maximize = request.objectives[index].direction === "maximize";
        if ((maximize && left[index] < right[index]) || (!maximize && left[index] > right[index])) return false;
        if ((maximize && left[index] > right[index]) || (!maximize && left[index] < right[index])) strict = true;
      }
      return strict;
    };
    return {status: "computed", candidate_refs: vectors.filter(([ref, vector]) => !vectors.some(([otherRef, other]) => otherRef !== ref && dominates(other, vector))).map(([ref]) => ref)};
  }

  function evaluate(request, architecture, catalog, availability, costInput) {
    const total = Object.values(request.workloads.mix_percent).reduce((sum, value) => sum + value, 0);
    if (Math.abs(total - 100) > 1e-9) throw new Error(`Workload mix must total 100, got ${total}`);
    if (request.architecture_id !== architecture.architecture_id) throw new Error("Architecture mismatch");
    const packages = new Map((costInput?.packages || []).map((item) => [`${item.vendor}/${item.product_id}`, item]));
    const candidates = vendors(request.vendor_mode).map((vendor) => {
      const [product, assessment] = selectProduct(vendor, catalog, availability, request.schedule.required_acceptance_date);
      const datedAssessment = availability.required_acceptance_date === request.schedule.required_acceptance_date ? assessment : null;
      const packageInfo = product ? packages.get(`${vendor}/${product.product_id}`) : null;
      const gapIds = gaps(request, datedAssessment, packageInfo);
      const blocking = gapIds.some((item) => item !== "GAP-GPUCFG-009");
      const availabilityStatus = datedAssessment?.availability_status || "not-assessed";
      const cases = PRICE_CASES.map((priceCase) => blocking
        ? blockedCase(vendor, request, priceCase, gapIds, availabilityStatus)
        : pricedCase(vendor, request, packageInfo, priceCase, gapIds));
      return {vendor, product_id: product?.product_id || null, availability_status: availabilityStatus, status: blocking ? "blocked" : "partial", cases, gap_ids: gapIds};
    });
    return {
      status: candidates.every((item) => item.status === "blocked") ? "blocked" : "partial",
      vendor_candidates: candidates,
      pareto_result: pareto(request, candidates)
    };
  }

  return {PRICE_CASES, evaluate, packageCost, maxUnits, selectProduct};
});
