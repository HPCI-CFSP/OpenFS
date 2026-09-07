const {readFileSync} = require("node:fs");
const engine = require("../site/gpu-planner-engine.js");
const load = (path) => JSON.parse(readFileSync(path, "utf8"));
const request = load("proposals/planning-requests/PLANREQ-GPUAI4S-2027-ONPREM-001.json");
const architecture = load("proposals/reference-architectures/ARCH-GPU-CENTRIC-AI4S-001.json");
const catalog = load("proposals/gpu-product-catalogs/GPUCAT-001.json");
const availability = load("proposals/procurement-availability/AVAIL-2027-JP-001.json");
const costs = load("tests/fixtures/gpu-planner-priced-components.json");

request.run_mode = "what-if";
request.vendor_mode = "compare";
request.product_selection = {nvidia: "GPU-NVIDIA-VERA-RUBIN", amd: "GPU-AMD-MI455X"};
Object.assign(request.facility, {it_power_limit_mw: 4, it_power_limit_status: "user-input", cooling_method: "direct-liquid", cooling_capacity_mw: 4, cooling_capacity_status: "user-input", rack_limit: 20, floor_area_m2: 1000, floor_loading_kg_m2: 2500, rack_density_kw: 500, pue: 1.1, power_redundancy: "N+1", cooling_redundancy: "N+1", facility_work_in_capex: true});
request.workloads.utilization_target_percent = 80;
request.workloads.headroom_percent = 10;
Object.assign(request.workloads.absolute_demand, {annual_accelerator_hours: 100000, hpc_jobs_per_year: 1000, hpc_accelerator_hours_per_year: 16000, hpc_accelerators_per_job: 8, hpc_mean_runtime_hours: 2, concurrent_users: 100});
Object.assign(request.storage, {shared_fast_capacity_pb: 0, archive_capacity_pb: 0, checkpoint_write_gb_s: 0, training_read_gb_s: 0, metadata_million_inodes: 0, backup_copies: 0, retention_years: 1, rto_hours: 24, local_nvme_tb_per_compute_unit: 0});

const result = engine.evaluate(request, architecture, catalog, availability, costs, "2026-09-07T00:00:00Z");
console.log(JSON.stringify(result.vendor_candidates.map((item) => {
  const value = item.cases.find((candidate) => candidate.price_case === "baseline");
  return {
    vendor: item.vendor,
    product_id: item.product_id,
    compute_units: value.quantities.compute_units,
    gpu_count: value.quantities.gpu_count,
    rack_count: value.quantities.rack_count,
    configuration_cost_jpy: value.costs.configuration_cost_jpy,
    contingency_jpy: value.costs.contingency_jpy,
    unused_budget_jpy: value.costs.unused_budget_jpy,
    total_tco_jpy: value.tco.total_tco_jpy
  };
})));
