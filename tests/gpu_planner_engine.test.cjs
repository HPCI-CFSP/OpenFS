const assert = require("node:assert/strict");
const {readFileSync} = require("node:fs");
const {test} = require("node:test");

const engine = require("../site/gpu-planner-engine.js");
const load = (path) => JSON.parse(readFileSync(path, "utf8"));
const clone = (value) => JSON.parse(JSON.stringify(value));
const requestBase = load("proposals/planning-requests/PLANREQ-GPUAI4S-2027-ONPREM-001.json");
const architecture = load("proposals/reference-architectures/ARCH-GPU-CENTRIC-AI4S-001.json");
const catalog = load("proposals/gpu-product-catalogs/GPUCAT-001.json");
const availabilityBase = load("proposals/procurement-availability/AVAIL-2027-JP-001.json");
const costs = load("tests/fixtures/gpu-planner-priced-components.json");

function complete(budget = 125, power = 4) {
  const request = clone(requestBase);
  request.budget.capex_ceiling_oku_jpy = budget;
  Object.assign(request.facility, {it_power_limit_mw: power, it_power_limit_status: "confirmed", cooling_method: "direct-liquid", cooling_capacity_mw: power, cooling_capacity_status: "confirmed", rack_limit: 40, floor_area_m2: 500, floor_loading_kg_m2: 2500});
  Object.assign(request.workloads.absolute_demand, {hpc_jobs_per_year: 10000, hpc_accelerator_hours_per_year: 1000000});
  Object.assign(request.storage, {shared_fast_capacity_pb: 5, archive_capacity_pb: 10, checkpoint_write_gb_s: 1000, training_read_gb_s: 2000});
  const availability = clone(availabilityBase);
  for (const item of availability.assessments) if (["GPU-NVIDIA-VERA-RUBIN", "GPU-AMD-MI430X"].includes(item.product_id)) Object.assign(item, {availability_status: "eligible", earliest_delivery_date: "2027-06-30", latest_delivery_date: "2027-09-30", sales_channel_status: "confirmed", support_status: "confirmed"});
  return [request, availability];
}

test("missing public prices stay blocked", () => {
  const result = engine.evaluate(requestBase, architecture, catalog, availabilityBase, null);
  assert.equal(result.status, "blocked");
  assert.ok(result.vendor_candidates.every((item) => item.cases.every((candidate) => candidate.gpu_count === null)));
});

test("browser engine preserves integer counts and the budget identity", () => {
  const [request, availability] = complete();
  const result = engine.evaluate(request, architecture, catalog, availability, costs);
  for (const candidate of result.vendor_candidates) {
    const value = candidate.cases[1];
    assert.ok(Number.isInteger(value.compute_units));
    assert.ok(Number.isInteger(value.gpu_count));
    assert.equal(value.costs.identity_verified, true);
    assert.equal(value.costs.configuration_cost_jpy + value.costs.contingency_jpy + value.costs.unused_budget_jpy, value.costs.budget_ceiling_jpy);
    assert.ok(value.tco.total_tco_jpy > value.tco.initial_capex_jpy);
  }
});

test("budget growth is monotonic under fixed product and constraints", () => {
  const counts = [10, 30, 100, 125, 300].map((budget) => {
    const [request, availability] = complete(budget, 10);
    return engine.evaluate(request, architecture, catalog, availability, costs).vendor_candidates[0].cases[1].gpu_count || 0;
  });
  assert.deepEqual(counts, [...counts].sort((a, b) => a - b));
});
