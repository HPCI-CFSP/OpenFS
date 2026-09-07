const assert = require("node:assert/strict");
const {readFileSync} = require("node:fs");
const {test} = require("node:test");

const engine = require("../site/gpu-planner-engine.js");
const load = (path) => JSON.parse(readFileSync(path, "utf8"));
const clone = (value) => JSON.parse(JSON.stringify(value));
const requestBase = load("proposals/planning-requests/PLANREQ-GPUAI4S-2027-ONPREM-001.json");
const architecture = load("proposals/reference-architectures/ARCH-GPU-CENTRIC-AI4S-001.json");
const catalog = load("proposals/gpu-product-catalogs/GPUCAT-001.json");
const availability = load("proposals/procurement-availability/AVAIL-2027-JP-001.json");
const costs = load("tests/fixtures/gpu-planner-priced-components.json");

function complete(budget = 125, power = 4) {
  const request = clone(requestBase);
  request.run_mode = "what-if";
  request.vendor_mode = "compare";
  request.product_selection = {nvidia: "GPU-NVIDIA-VERA-RUBIN", amd: "GPU-AMD-MI455X"};
  request.budget.capex_ceiling_oku_jpy = budget;
  Object.assign(request.facility, {
    it_power_limit_mw: power, it_power_limit_status: "user-input",
    cooling_method: "direct-liquid", cooling_capacity_mw: power,
    cooling_capacity_status: "user-input", rack_limit: 20,
    floor_area_m2: 1000, floor_loading_kg_m2: 2500,
    rack_density_kw: 500, pue: 1.1, power_redundancy: "N+1",
    cooling_redundancy: "N+1", facility_work_in_capex: true
  });
  request.workloads.utilization_target_percent = 80;
  request.workloads.headroom_percent = 10;
  Object.assign(request.workloads.absolute_demand, {
    annual_accelerator_hours: 100000, hpc_jobs_per_year: 1000,
    hpc_accelerator_hours_per_year: 16000, hpc_accelerators_per_job: 8,
    hpc_mean_runtime_hours: 2, concurrent_users: 100
  });
  Object.assign(request.storage, {
    shared_fast_capacity_pb: 0, archive_capacity_pb: 0,
    checkpoint_write_gb_s: 0, training_read_gb_s: 0,
    metadata_million_inodes: 0, backup_copies: 0,
    retention_years: 1, rto_hours: 24, local_nvme_tb_per_compute_unit: 0
  });
  return request;
}

function baseline(result, vendor = "NVIDIA") {
  const candidate = result.vendor_candidates.find((item) => item.vendor === vendor);
  return candidate.cases.find((item) => item.price_case === "baseline");
}

test("public evidence mode leaves unsupported estimates blocked", () => {
  const result = engine.evaluate(requestBase, architecture, catalog, availability, null, "2026-09-07T00:00:00Z");
  assert.equal(result.status, "blocked");
  assert.equal(result.calculation_mode, "public-evidence");
  assert.ok(result.vendor_candidates.every((item) => item.cases.every((candidate) => candidate.quantities === null)));
});

test("125 oku deterministic case yields 9 racks and 648 GPUs", () => {
  const result = engine.evaluate(complete(), architecture, catalog, availability, costs, "2026-09-07T00:00:00Z");
  for (const candidate of result.vendor_candidates) {
    const value = candidate.cases.find((item) => item.price_case === "baseline");
    assert.equal(value.quantities.compute_units, 9);
    assert.equal(value.quantities.rack_count, 9);
    assert.equal(value.quantities.gpu_count, 648);
    assert.equal(value.costs.configuration_cost_jpy, 10500000000);
    assert.equal(value.costs.contingency_jpy, 1050000000);
    assert.equal(value.costs.unused_budget_jpy, 950000000);
    assert.equal(value.costs.identity_verified, true);
  }
});

test("300 oku remains capped at 10 racks by 4 MW", () => {
  const value = baseline(engine.evaluate(complete(300, 4), architecture, catalog, availability, costs));
  assert.equal(value.quantities.rack_count, 10);
  assert.equal(value.quantities.gpu_count, 720);
});

test("2 MW caps the configuration at 5 racks", () => {
  const value = baseline(engine.evaluate(complete(300, 2), architecture, catalog, availability, costs));
  assert.equal(value.quantities.rack_count, 5);
  assert.equal(value.quantities.gpu_count, 360);
});

test("price cases reoptimize integer procurement quantities", () => {
  const priced = clone(costs);
  for (const pkg of priced.packages) {
    const line = pkg.cost_lines.find((item) => item.category === "compute");
    Object.assign(line, {optimistic_jpy: 800000000, baseline_jpy: 1000000000, conservative_jpy: 1200000000});
  }
  const request = complete(125, 20);
  request.facility.rack_limit = 100;
  const candidate = engine.evaluate(request, architecture, catalog, availability, priced).vendor_candidates[0];
  const values = Object.fromEntries(candidate.cases.map((item) => [item.price_case, item.quantities.compute_units]));
  assert.ok(values.optimistic > values.baseline);
  assert.ok(values.baseline > values.conservative);
});

test("inference queue responds to higher request rate", () => {
  const request = complete();
  request.inference.request_rate_per_second = 10;
  const quantities = {gpu_count: 8};
  const model = {status: "provisional", service_rate_rps_per_gpu: 10, base_ttft_ms: 100, base_tpot_ms: 20};
  const low = engine.performance({...request, performance_model: {phase_baseline: null, inference_baseline: model}}, quantities, "baseline").inference_queue;
  request.inference.request_rate_per_second = 70;
  const high = engine.performance({...request, performance_model: {phase_baseline: null, inference_baseline: model}}, quantities, "baseline").inference_queue;
  assert.ok(low.utilization < high.utilization);
  assert.ok(low.ttft_ms.p99 < high.ttft_ms.p99);
});
