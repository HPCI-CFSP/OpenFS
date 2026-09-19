/* Browser-local conceptual estimates; independent of the strict procurement engine. */
(function (root) {
  "use strict";
  const PRICE_CASES = ["optimistic", "baseline", "conservative"];
  function dateWindow(date) {
    const year = Number(date.value.slice(0, 4));
    const month = Number(date.value.slice(5, 7));
    const span = {month: 1, quarter: 3, "half-year": 6, year: 12}[date.precision];
    if (!span) return {start: date.value, end: date.value};
    const first = date.precision === "year" ? 1 : Math.floor((month - 1) / span) * span + 1;
    return {start: `${year}-${String(first).padStart(2, "0")}-01`,
      end: new Date(Date.UTC(year, first + span - 1, 0)).toISOString().slice(0, 10)};
  }
  function matchingPackage(model, product, preferences) {
    const matches = p => p.product_id === product.product_id &&
      (preferences.cpu_architecture === "auto" || p.cpu_architecture === preferences.cpu_architecture);
    const priced = model.packages.find(matches);
    if (priced) return priced;
    const a = (model.rack_analogies || []).find(matches);
    if (!a) return null;
    const anchor = model.packages.find(p => p.package_id === a.anchor_package_id);
    if (!anchor || anchor.gpus_per_node * a.anchor_packages_per_rack !== a.trays_per_rack * a.gpus_per_tray)
      throw new Error("Invalid rack analogy anchor");
    // Internal arithmetic uses trays; procurement always uses complete racks.
    return {product_id: a.product_id, package_id: a.analogy_id, analogy: a,
      cpu_architecture: a.cpu_architecture, cpu_model: a.cpu_model,
      cpus_per_node: a.cpus_per_tray, gpus_per_node: a.gpus_per_tray,
      hbm_gb_per_gpu: a.hbm_gb_per_gpu, host_memory_gb: a.host_memory_gb_per_tray,
      local_nvme_tb: 0, bundled_nvme_drives: 0, local_nvme_bays: a.local_nvme_bays_per_tray,
      node_kw: a.rack_power_kw / a.trays_per_rack,
      price_usd: anchor.price_usd * a.anchor_packages_per_rack / a.trays_per_rack,
      price_basis_date: a.price_basis_date, source_ids: a.source_ids,
      fabrics: ["InfiniBand", "RoCE"], included_ja: a.explanation_ja, included_en: a.explanation_en};
  }
  function compatible(product, preferences, model) {
    const p = [...model.packages, ...(model.rack_analogies || [])].find(p => p.product_id === product.product_id);
    const knownCpu = p?.cpu_architecture || (product.family === "GB200" || product.family === "Vera Rubin" ? "arm" : null);
    return preferences.cpu_architecture === "auto" || !knownCpu || preferences.cpu_architecture === knownCpu;
  }
  function gap(id, ja, en, missing = []) {
    return {gap_id: id, scope: "planning-estimate", statement_ja: ja, statement_en: en, missing_items: missing};
  }
  function emptyCase(priceCase, gaps) {
    return {price_case: priceCase, status: "blocked", quantities: null, power: null,
      costs: {configuration_cost_jpy: null, contingency_jpy: null, unused_budget_jpy: null, line_items: []},
      tco: {total_tco_jpy: null}, gap_ids: gaps.map(g => g.gap_id)};
  }
  function physicalBom(units, blocks, model) {
    const b = model.bom_assumptions;
    for (const [key, value] of Object.entries(b)) {
      if (!Number.isFinite(value) || value <= 0 ||
          (!["rack_footprint_m2", "aisle_multiplier"].includes(key) && !Number.isSafeInteger(value))) {
        throw new Error("Invalid BOM assumption: " + key);
      }
    }
    if (b.leaf_down_ports + b.leaf_up_ports > b.switch_ports) throw new Error("Leaf port budget exceeded");
    const endpoints = units * b.nic_ports_per_compute_unit;
    const leaves = Math.ceil(endpoints / b.leaf_down_ports);
    // Integer full-mesh leaf/spine reference; no breakout or third tier is assumed.
    let spines = 0, linksPerPair = 0, supported = leaves <= 1;
    if (leaves > 1) {
      for (let count = 2; count <= b.leaf_up_ports; count++) {
        if (b.leaf_up_ports % count) continue;
        const links = b.leaf_up_ports / count;
        if (leaves * links <= b.switch_ports) {
          spines = count; linksPerPair = links; supported = true; break;
        }
      }
    }
    const groups = Math.ceil(units / b.compute_units_per_service_group);
    const login = groups * b.login_nodes, management = groups * b.management_quorum_nodes;
    const scheduler = groups * b.scheduler_nodes, authentication = groups * b.authentication_nodes;
    const services = login + management + scheduler + authentication;
    const controllers = blocks * b.controllers_per_storage_block;
    const convergedEndpoints = (units + services + controllers) * b.converged_ports_per_endpoint;
    const convergedSwitches = Math.ceil(convergedEndpoints / b.leaf_down_ports);
    const oobEndpoints = units * b.oob_ports_per_compute_unit + services + controllers + leaves + spines + convergedSwitches;
    const oobSwitches = Math.ceil(oobEndpoints / b.leaf_down_ports);
    const switches = leaves + spines + convergedSwitches + oobSwitches;
    const computeRacks = Math.ceil(units / model.defaults.compute_units_per_rack);
    const storageRacks = Math.ceil(blocks / b.storage_blocks_per_rack);
    const serviceRacks = Math.ceil(services / b.service_nodes_per_rack);
    const networkRacks = Math.ceil(switches / b.switches_per_rack);
    const rackCount = computeRacks + storageRacks + serviceRacks + networkRacks;
    const fabricLinks = endpoints + leaves * spines * linksPerPair;
    return {basis: "planning-assumption", compute_fabric_supported: supported,
      compute_nic_ports: endpoints, compute_leaf_switches: leaves, compute_spine_switches: spines,
      links_per_leaf_spine_pair: linksPerPair, compute_fabric_cables: fabricLinks,
      compute_fabric_optics: 2 * fabricLinks, converged_endpoint_ports: convergedEndpoints,
      converged_access_switches: convergedSwitches, oob_endpoint_ports: oobEndpoints,
      oob_access_switches: oobSwitches, login_nodes: login, management_nodes: management,
      scheduler_nodes: scheduler, authentication_nodes: authentication,
      storage_blocks: blocks, storage_controllers: controllers,
      compute_racks: computeRacks, storage_racks: storageRacks, service_racks: serviceRacks,
      network_racks: networkRacks, rack_count: rackCount,
      floor_area_m2: rackCount * b.rack_footprint_m2 * b.aisle_multiplier,
      facility_fit: "unverified", component_unit_prices: null};
  }
  function demandRequirements(request, pkg) {
    const work = request.workloads || {}, a = work.absolute_demand || {};
    const storage = request.storage || {};
    const nonnegative = (value, key) => {
      if (value != null && (!Number.isFinite(value) || value < 0)) throw new Error("Invalid demand: " + key);
      return value;
    };
    for (const [key, value] of Object.entries(a)) nonnegative(value, key);
    for (const key of ["shared_fast_capacity_pb", "checkpoint_write_gb_s", "training_read_gb_s"]) nonnegative(storage[key], key);
    const total = a.annual_accelerator_hours;
    const training = a.training_accelerator_hours_per_year, hpc = a.hpc_accelerator_hours_per_year;
    // Aggregate and component totals are alternative representations, never additive.
    const hours = total ?? (training != null && hpc != null ? training + hpc : null);
    const utilization = work.utilization_target_percent, headroom = work.headroom_percent;
    if (utilization != null && (!Number.isFinite(utilization) || utilization <= 0 || utilization > 100)) throw new Error("Invalid utilization");
    if (headroom != null && (!Number.isFinite(headroom) || headroom < 0 || headroom >= 100)) throw new Error("Invalid headroom");
    const minUnits = hours != null && utilization != null && headroom != null
      ? Math.ceil(hours / (8760 * utilization / 100 * (1 - headroom / 100) * pkg.gpus_per_node)) : null;
    return {annual_accelerator_hours: hours, minimum_compute_units: minUnits,
      aggregate_hours_override_components: total != null,
      shared_fast_capacity_pb: storage.shared_fast_capacity_pb ?? null,
      checkpoint_write_gb_s: storage.checkpoint_write_gb_s ?? null,
      training_read_gb_s: storage.training_read_gb_s ?? null,
      storage_bandwidth_fit: "unverified", inference_slo_fit: "unverified",
      basis: "requested-hours-on-selected-product-not-cross-generation-speedup"};
  }
  function evaluate(request, product, model, architecture = {}) {
    const prefs = request.basic_preferences;
    const p = matchingPackage(model, product, prefs);
    const candidate = {vendor: product.vendor, product_id: product.product_id, product_name: product.model,
      status: "partial", availability_status: "conditional", procurement_use: "prohibited",
      software_profile: structuredClone(architecture.vendor_profiles?.find(p => p.vendor === product.vendor) || null),
      software_qualification: {status: "unverified", porting_person_hours: null, support_cost_jpy: null},
      estimate_method: "published-package-plus-explicit-allowances", gaps: [], cases: []};
    if (!p) {
      candidate.status = "blocked";
      candidate.gaps.push(gap("GAP-EST-PACKAGE", "この製品の価格付き構成は未確認です。下記の参照構成を予算規模の比較に使えますが、別世代の価格・GPU数は転用しません。", "No priced configuration is available for this product. Use the reference packages below for budget context, not as this generation's price or GPU count.", ["priced-package", "CPU/fabric compatibility", "delivery quote"]));
      candidate.cases = PRICE_CASES.map(c => emptyCase(c, candidate.gaps));
      return candidate;
    }
    const d = structuredClone(model.defaults);
    const analogy = p.analogy;
    const increment = analogy?.trays_per_rack || 1;
    const bomModel = structuredClone(model);
    if (analogy) {
      d.compute_units_per_rack = increment;
      bomModel.bom_assumptions.nic_ports_per_compute_unit = analogy.nic_ports_per_tray;
      bomModel.bom_assumptions.oob_ports_per_compute_unit = 2;
      candidate.estimate_method = "explicit-rack-price-analogy";
      candidate.price_analogy = structuredClone(analogy);
      candidate.gaps.push(gap("GAP-EST-RUBIN-QUOTE", "Rubin価格と4/6/9か月の納期は未検証の仮定です。2027年の数量範囲はこの仮定に条件付きで、国内納入を保証しません。液冷・受電・床荷重の適合、保守、性能には個別確認が必要です。",
        "Rubin prices and 4/6/9-month lead times are unvalidated assumptions. The 2027 quantity range is conditional, not a Japan delivery guarantee. Liquid cooling, power, floor load, support and performance need qualification."));
    }
    const a = request.estimate_assumptions || {};
    for (const key of ["fx_jpy_per_usd", "storage_tb_per_node", "storage_block_jpy"]) {
      if (a[key] != null) d[key] = a[key];
      if (!Number.isFinite(d[key]) || d[key] < 0 || (key !== "storage_tb_per_node" && d[key] === 0)) throw new Error(`Invalid ${key}`);
    }
    if (a.baseline_annual_change != null) {
      if (!Number.isFinite(a.baseline_annual_change) || Math.abs(a.baseline_annual_change) > 0.5) throw new Error("Annual sensitivity must be between -50% and +50%");
      d.annual_change = {optimistic: a.baseline_annual_change - 0.1, baseline: a.baseline_annual_change, conservative: a.baseline_annual_change + 0.1};
    }
    const budget = Math.round(request.budget.capex_ceiling_oku_jpy * 1e8);
    if (!Number.isSafeInteger(budget) || budget <= 0) throw new Error("Invalid budget");
    const manual = request.manual_overrides || {};
    const demand = demandRequirements(request, p);
    candidate.demand_requirements = demand;
    if (manual.compute_units != null && (!Number.isSafeInteger(manual.compute_units) || manual.compute_units < 1)) throw new Error("Compute units must be a positive integer");
    for (const key of ["shared_fast_capacity_pb", "local_nvme_tb_per_compute_unit"]) {
      if (manual[key] != null && (!Number.isFinite(manual[key]) || manual[key] < 0)) throw new Error(`Invalid ${key}`);
    }
    const fabric = prefs.scale_out_fabric === "roce" ? "RoCE" : "InfiniBand";
    if (!p.fabrics.includes(fabric)) throw new Error("Unsupported fabric");
    candidate.package_id = p.package_id;
    candidate.source_ids = p.source_ids;
    candidate.package_scope_ja = p.included_ja;
    candidate.package_scope_en = p.included_en;
    candidate.assumptions = d;
    for (const note of p.qualification_notes || []) {
      candidate.gaps.push({...gap(note.gap_id, note.statement_ja, note.statement_en), source_ids: note.source_ids});
    }
    candidate.gaps.push(gap("GAP-EST-CONFIG", "補助ラックを含む整数BOMは参照仮定です。計算網のポート数を検査しますが、収束網・管理網の上位接続、障害時帯域、NIC搭載可否、機器別価格と電力は未確認です。ストレージのコントローラーは筐体内蔵と仮定し、別途二重計上しません。", "The integer BOM including auxiliary racks is a reference assumption. Compute-fabric port counts are checked, but converged/OOB uplinks, failure-mode bandwidth, NIC fit, per-device prices and power remain unverified. Storage controllers are assumed bundled in appliances, not costed twice."));
    candidate.gaps.push(gap("GAP-EST-VALIDATION", "公開提示価格と計画用仮定による概算です。学術割引・納期・設備適合・アプリ性能は未検証で、調達には使用できません。価格区間は信頼区間ではありません。", "This estimate combines asking prices and planning assumptions. Academic discounts, delivery, facility fit and application performance are unvalidated. It is not for procurement; scenario ranges are not confidence intervals."));
    candidate.gaps.push(gap("GAP-EST-TCO", "5年間のCAPEX＋電力量料金のみ部分集計します。保守・人件費・基本料金・ホスティング等が未確定のため、完全なTCOは未算定です。", "Only CAPEX plus five-year energy charges are subtotalled. Full TCO is unknown pending maintenance, staffing, demand charges and hosting fees."));
    candidate.gaps.push(gap("GAP-EST-DEMAND", "GPU時間は選択製品で必要な時間として扱う下限計算です。別GPUの利用実績から性能を換算しません。需要未入力時の比率は参照値であり、チェックポイント帯域・推論SLO・アプリケーション性能の適合は未検証です。", "GPU-hours bound capacity only if expressed for the selected product, without converting another GPU's usage into performance. Without absolute demand, ratios are references; checkpoint bandwidth, inference SLOs and application performance remain unverified."));
    const years = Math.max(0, (Date.parse(request.schedule.required_acceptance_date) - Date.parse(p.price_basis_date)) / (365.25 * 86400000));
    candidate.cases = PRICE_CASES.map(priceCase => {
      const annualFactor = (1 + d.annual_change[priceCase]) ** years;
      const factor = d.price_factor[priceCase] * annualFactor;
      const usd = d.fx_jpy_per_usd * factor * (1 + d.tax_rate);
      const allowance = factor * (1 + d.tax_rate);
      const computeFactor = analogy ? analogy.rack_price_multiplier[priceCase] * annualFactor : factor;
      const unitCost = Math.round(p.price_usd * d.fx_jpy_per_usd * computeFactor * (1 + d.tax_rate));
      let assumedDelivery = null;
      if (analogy) {
        const date = new Date(analogy.price_basis_date + "T00:00:00Z");
        date.setUTCMonth(date.getUTCMonth() + analogy.assumed_lead_time_months[priceCase]);
        assumedDelivery = date.toISOString().slice(0, 10);
        if (assumedDelivery > request.schedule.required_acceptance_date) {
          return {...emptyCase(priceCase, candidate.gaps), reason: "assumed-lead-time-exceeds-acceptance",
            assumed_delivery_date: assumedDelivery};
        }
      }
      const reserve = request.budget.contingency_percent / 100;
      if (!(reserve >= 0 && reserve < 1)) throw new Error("Invalid contingency");
      const fixed = d.management_fixed_jpy + d.installation_fixed_jpy;
      const at = n => {
        const storageTarget = manual.shared_fast_capacity_pb != null ? manual.shared_fast_capacity_pb * 1000
          : Math.max(1000, n * d.storage_tb_per_node, (demand.shared_fast_capacity_pb ?? 0) * 1000);
        const blocks = Math.ceil(storageTarget / d.storage_block_tb);
        const bom = physicalBom(n, blocks, {...bomModel, defaults: d});
        const racks = bom.rack_count;
        const requestedLocal = manual.local_nvme_tb_per_compute_unit ?? Math.max(p.local_nvme_tb, 7.68);
        // Never subtract a bundled disk without a separately evidenced credit.
        const modules = Math.ceil(Math.max(0, requestedLocal - p.local_nvme_tb) / d.local_nvme_module_tb);
        const lines = [
          ["compute-package", n, unitCost, analogy ? "planning-assumption" : "published-package"],
          ["local-nvme-additions", n * modules, Math.round(d.local_nvme_module_usd * usd), "planning-assumption"],
          ["scale-out-fabric", n, Math.round(d.network_per_node_jpy[fabric] * allowance * (analogy?.network_allowance_multiplier || 1)), "planning-assumption"],
          ["shared-storage-100TB", blocks, Math.round(d.storage_block_jpy * allowance), "planning-assumption"],
          ["management-and-installation", 1, Math.round(fixed * allowance), "planning-assumption"],
          ["racks-and-facility", 1, Math.round((racks + bom.compute_racks * ((analogy?.facility_allowance_multiplier || 1) - 1)) * d.rack_initial_jpy[request.deployment_mode] * allowance), "planning-assumption"]
        ].map(([component_id, quantity, unit_price_jpy, evidence_status]) => ({component_id, quantity, unit_price_jpy, total_jpy: quantity * unit_price_jpy, evidence_status}));
        const cost = lines.reduce((sum, row) => sum + row.total_jpy, 0);
        const contingency = Math.round(cost * reserve);
        const pa = model.power_assumptions;
        for (const [key, value] of Object.entries(pa)) {
          if (!Number.isFinite(value) || value <= 0) throw new Error("Invalid power assumption: " + key);
        }
        const computePower = n * p.node_kw;
        const auxiliaryPower = (analogy ? 0 : bom.compute_nic_ports * pa.compute_nic_port_kw) +
          (bom.compute_leaf_switches + bom.compute_spine_switches + bom.converged_access_switches + bom.oob_access_switches) * pa.switch_kw +
          blocks * pa.storage_block_kw + (bom.login_nodes + bom.management_nodes + bom.scheduler_nodes + bom.authentication_nodes) * pa.service_node_kw;
        const power = (computePower + auxiliaryPower) * (1 + d.extra_it_power_fraction);
        const f = request.facility || {};
        const rackDensity = Math.max(p.node_kw * Math.min(n, d.compute_units_per_rack),
          pa.storage_block_kw * Math.min(blocks, model.bom_assumptions.storage_blocks_per_rack),
          pa.switch_kw * Math.min(bom.compute_leaf_switches + bom.compute_spine_switches + bom.converged_access_switches + bom.oob_access_switches, model.bom_assumptions.switches_per_rack),
          pa.service_node_kw * Math.min(bom.login_nodes + bom.management_nodes + bom.scheduler_nodes + bom.authentication_nodes, model.bom_assumptions.service_nodes_per_rack));
        const within = (value, limit) => limit == null || value <= limit;
        const fits = n % increment === 0 && bom.compute_fabric_supported && modules + p.bundled_nvme_drives <= p.local_nvme_bays &&
          cost + contingency <= budget && within(power, f.it_power_limit_mw == null ? null : f.it_power_limit_mw * 1000)
          && within(power, f.cooling_capacity_mw == null ? null : f.cooling_capacity_mw * 1000) &&
          within(racks, f.rack_limit) && within(bom.floor_area_m2, f.floor_area_m2) && within(rackDensity, f.rack_density_kw);
        return {n, racks, blocks, bom, modules, requestedLocal, lines, cost, contingency, power, computePower, auxiliaryPower, fits};
      };
      let lo = 0, hi = Math.floor(budget / Math.max(unitCost * increment, 1)) + 1;
      while (hi - lo > 1) {const mid = Math.floor((lo + hi) / 2); if (at(mid * increment).fits) lo = mid; else hi = mid;}
      const v = at(manual.compute_units ?? lo * increment);
      const demandConflict = (demand.minimum_compute_units != null && v.n < demand.minimum_compute_units) ||
        (demand.shared_fast_capacity_pb != null && v.blocks * d.storage_block_tb < demand.shared_fast_capacity_pb * 1000);
      if (v.n < 1 || !v.fits || demandConflict) {
        const failure = emptyCase(priceCase, candidate.gaps);
        failure.reason = v.n % increment !== 0 ? "whole-rack-purchase-required" : demandConflict ? "absolute-demand-exceeds-budget-or-manual-lock" : "budget-facility-drive-bay-or-manual-lock-conflict";
        return failure;
      }
      const pue = request.facility?.pue ?? d.pue;
      const tcoYears = request.budget.tco_years;
      if (!Number.isFinite(pue) || pue < 1 || !Number.isSafeInteger(tcoYears) || tcoYears < 1 ||
          !Number.isFinite(d.load_factor) || d.load_factor < 0 || d.load_factor > 1) throw new Error("Invalid TCO assumptions");
      const annualEnergy = Math.round(v.power * pue * d.load_factor * 8760 * d.electricity_jpy_per_kwh);
      const energy = annualEnergy * tcoYears;
      const capex = v.cost + v.contingency;
      return {price_case: priceCase, status: "partial", gap_ids: candidate.gaps.map(g => g.gap_id),
        quantities: {compute_units: v.n, compute_unit_type: analogy ? "tray" : "node",
          procurement_unit_type: analogy ? "rack" : "node", procurement_units: v.n / increment,
          compute_units_per_procurement_unit: increment,
          gpu_count: v.n * p.gpus_per_node, host_cpu_count: v.n * p.cpus_per_node,
          host_memory_gb: v.n * p.host_memory_gb, hbm_capacity_gb: v.n * p.gpus_per_node * p.hbm_gb_per_gpu,
          local_nvme_tb: v.n * (p.local_nvme_tb + v.modules * d.local_nvme_module_tb), shared_fast_capacity_pb: v.blocks * d.storage_block_tb / 1000,
          rack_count: v.racks, fabric, cpu_model: p.cpu_model, physical_bom: v.bom},
        power: {total_kw: v.power, compute_kw: v.computePower, auxiliary_kw: v.auxiliaryPower,
          margin_fraction: d.extra_it_power_fraction, basis: "configurator-plus-itemized-auxiliary-assumptions", facility_fit: "unverified"},
        costs: {line_items: v.lines, configuration_cost_jpy: v.cost, contingency_jpy: v.contingency, unused_budget_jpy: budget - capex,
          budget_ceiling_jpy: budget, identity_verified: v.cost + v.contingency + (budget - capex) === budget},
        tco: {total_tco_jpy: null, capex_plus_energy_jpy: capex + energy, energy_jpy: energy,
          annual_energy_jpy: annualEnergy, years: tcoYears, pue, completeness: "partial",
          basis: "undiscounted-nominal-sensitivity-not-forecast",
          missing_cost_scopes: ["demand-charges", "staffing", "software-support", "out-of-warranty-maintenance", "hosting", "major-facility-works", "decommissioning"],
          yearly_costs: Array.from({length: tcoYears}, (_, i) => ({year: i + 1, energy_jpy: annualEnergy,
            maintenance_jpy: null, staffing_jpy: null, hosting_jpy: null, total_opex_jpy: null}))},
        price_basis_date: p.price_basis_date, sensitivity_factor: computeFactor, extrapolation_years: years,
        assumed_delivery_date: assumedDelivery};
    });
    if (candidate.cases.every(c => c.status === "blocked")) candidate.status = "blocked";
    return candidate;
  }
  const api = {ENGINE_VERSION: "concept-estimate-0.3.0", evaluate, compatible, dateWindow, physicalBom, demandRequirements};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.OpenFSGpuEstimates = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
