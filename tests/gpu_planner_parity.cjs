const {readFileSync} = require("node:fs");
const engine = require("../site/gpu-planner-engine.js");
const load = (path) => JSON.parse(readFileSync(path, "utf8"));
const request = load("proposals/planning-requests/PLANREQ-GPUAI4S-2027-ONPREM-001.json");
const architecture = load("proposals/reference-architectures/ARCH-GPU-CENTRIC-AI4S-001.json");
const catalog = load("proposals/gpu-product-catalogs/GPUCAT-001.json");
const availability = load("proposals/procurement-availability/AVAIL-2027-JP-001.json");
const costs = load("tests/fixtures/gpu-planner-priced-components.json");

Object.assign(request.facility, {it_power_limit_mw: 4, it_power_limit_status: "confirmed", cooling_method: "direct-liquid", cooling_capacity_mw: 4, cooling_capacity_status: "confirmed", rack_limit: 40, floor_area_m2: 500, floor_loading_kg_m2: 2500});
Object.assign(request.workloads.absolute_demand, {hpc_jobs_per_year: 10000, hpc_accelerator_hours_per_year: 1000000});
Object.assign(request.storage, {shared_fast_capacity_pb: 5, archive_capacity_pb: 10, checkpoint_write_gb_s: 1000, training_read_gb_s: 2000});
for (const item of availability.assessments) if (["GPU-NVIDIA-VERA-RUBIN", "GPU-AMD-MI430X"].includes(item.product_id)) Object.assign(item, {availability_status: "eligible", earliest_delivery_date: "2027-06-30", latest_delivery_date: "2027-09-30", sales_channel_status: "confirmed", support_status: "confirmed"});

const result = engine.evaluate(request, architecture, catalog, availability, costs);
console.log(JSON.stringify(result.vendor_candidates.map((item) => {
  const value = item.cases[1];
  return {vendor: item.vendor, product_id: item.product_id, compute_units: value.compute_units, gpu_count: value.gpu_count, rack_count: value.rack_count, configuration_cost_jpy: value.costs.configuration_cost_jpy, contingency_jpy: value.costs.contingency_jpy, unused_budget_jpy: value.costs.unused_budget_jpy, total_tco_jpy: value.tco.total_tco_jpy};
})));
