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
    return model.packages.find(p => p.product_id === product.product_id &&
      (preferences.cpu_architecture === "auto" || p.cpu_architecture === preferences.cpu_architecture));
  }
  function compatible(product, preferences, model) {
    const p = model.packages.find(p => p.product_id === product.product_id);
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
  function evaluate(request, product, model) {
    const prefs = request.basic_preferences;
    const p = matchingPackage(model, product, prefs);
    const candidate = {vendor: product.vendor, product_id: product.product_id, product_name: product.model,
      status: "partial", availability_status: "conditional", procurement_use: "prohibited", software_profile: null,
      estimate_method: "published-package-plus-explicit-allowances", gaps: [], cases: []};
    if (!p) {
      candidate.status = "blocked";
      candidate.gaps.push(gap("GAP-EST-PACKAGE", "この製品の価格付き構成は未確認です。下記の参照構成を予算規模の比較に使えますが、別世代の価格・GPU数は転用しません。", "No priced configuration is available for this product. Use the reference packages below for budget context, not as this generation's price or GPU count.", ["priced-package", "CPU/fabric compatibility", "delivery quote"]));
      candidate.cases = PRICE_CASES.map(c => emptyCase(c, candidate.gaps));
      return candidate;
    }
    const d = structuredClone(model.defaults);
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
    if (manual.compute_units != null && (!Number.isSafeInteger(manual.compute_units) || manual.compute_units < 1)) throw new Error("Compute units must be a positive integer");
    for (const key of ["shared_fast_capacity_pb", "local_nvme_tb_per_compute_unit"]) {
      if (manual[key] != null && (!Number.isFinite(manual[key]) || manual[key] < 0)) throw new Error(`Invalid ${key}`);
    }
    const fabric = prefs.scale_out_fabric === "roce" ? "RoCE" : "InfiniBand";
    candidate.package_id = p.package_id;
    candidate.source_ids = p.source_ids;
    candidate.package_scope_ja = p.included_ja;
    candidate.package_scope_en = p.included_en;
    candidate.assumptions = d;
    candidate.gaps.push(gap("GAP-EST-CONFIG", "ラック数は計算サーバー分のみです。追加NVMe費用は公開オプション価格からの仮定で、部品互換性、NIC数・トポロジー、ストレージ用ラックと電力の詳細は別途確認が必要です。", "Rack count covers compute servers only. Added NVMe cost is an allowance derived from a public option price. Component compatibility, NIC count, topology, storage racks and detailed power need separate qualification."));
    candidate.gaps.push(gap("GAP-EST-VALIDATION", "公開提示価格と計画用仮定による概算です。学術割引・納期・設備適合・アプリ性能は未検証で、調達には使用できません。価格区間は信頼区間ではありません。", "This estimate combines asking prices and planning assumptions. Academic discounts, delivery, facility fit and application performance are unvalidated. It is not for procurement; scenario ranges are not confidence intervals."));
    candidate.gaps.push(gap("GAP-EST-TCO", "5年間のCAPEX＋電力量料金のみ部分集計します。保守・人件費・基本料金・ホスティング等が未確定のため、完全なTCOは未算定です。", "Only CAPEX plus five-year energy charges are subtotalled. Full TCO is unknown pending maintenance, staffing, demand charges and hosting fees."));
    const years = Math.max(0, (Date.parse(request.schedule.required_acceptance_date) - Date.parse(p.price_basis_date)) / (365.25 * 86400000));
    candidate.cases = PRICE_CASES.map(priceCase => {
      const factor = d.price_factor[priceCase] * (1 + d.annual_change[priceCase]) ** years;
      const usd = d.fx_jpy_per_usd * factor * (1 + d.tax_rate);
      const allowance = factor * (1 + d.tax_rate);
      const unitCost = Math.round(p.price_usd * usd);
      const reserve = request.budget.contingency_percent / 100;
      if (!(reserve >= 0 && reserve < 1)) throw new Error("Invalid contingency");
      const fixed = d.management_fixed_jpy + d.installation_fixed_jpy;
      const at = n => {
        const racks = Math.ceil(n / d.compute_units_per_rack);
        const storageTarget = manual.shared_fast_capacity_pb != null ? manual.shared_fast_capacity_pb * 1000 : Math.max(1000, n * d.storage_tb_per_node);
        const blocks = Math.ceil(storageTarget / d.storage_block_tb);
        const requestedLocal = manual.local_nvme_tb_per_compute_unit ?? Math.max(p.local_nvme_tb, 7.68);
        // Never subtract a bundled disk without a separately evidenced credit.
        const modules = Math.ceil(Math.max(0, requestedLocal - p.local_nvme_tb) / d.local_nvme_module_tb);
        const lines = [
          ["compute-package", n, unitCost, "published-package"],
          ["local-nvme-additions", n * modules, Math.round(d.local_nvme_module_usd * usd), "planning-assumption"],
          ["scale-out-fabric", n, Math.round(d.network_per_node_jpy[fabric] * allowance), "planning-assumption"],
          ["shared-storage-100TB", blocks, Math.round(d.storage_block_jpy * allowance), "planning-assumption"],
          ["management-and-installation", 1, Math.round(fixed * allowance), "planning-assumption"],
          ["racks-and-facility", racks, Math.round(d.rack_initial_jpy[request.deployment_mode] * allowance), "planning-assumption"]
        ].map(([component_id, quantity, unit_price_jpy, evidence_status]) => ({component_id, quantity, unit_price_jpy, total_jpy: quantity * unit_price_jpy, evidence_status}));
        const cost = lines.reduce((sum, row) => sum + row.total_jpy, 0);
        const contingency = Math.round(cost * reserve);
        const power = n * p.node_kw * (1 + d.extra_it_power_fraction);
        const f = request.facility || {};
        const within = (value, limit) => limit == null || value <= limit;
        const fits = modules + p.bundled_nvme_drives <= p.local_nvme_bays && cost + contingency <= budget && within(power, f.it_power_limit_mw == null ? null : f.it_power_limit_mw * 1000)
          && within(power, f.cooling_capacity_mw == null ? null : f.cooling_capacity_mw * 1000) && within(racks, f.rack_limit);
        return {n, racks, blocks, modules, requestedLocal, lines, cost, contingency, power, fits};
      };
      let lo = 0, hi = Math.floor(budget / Math.max(unitCost, 1)) + 1;
      while (hi - lo > 1) {const mid = Math.floor((lo + hi) / 2); if (at(mid).fits) lo = mid; else hi = mid;}
      const v = at(manual.compute_units ?? lo);
      if (v.n < 1 || !v.fits) {
        const failure = emptyCase(priceCase, candidate.gaps);
        failure.reason = "budget-facility-drive-bay-or-manual-lock-conflict";
        return failure;
      }
      const energy = Math.round(v.power * d.pue * d.load_factor * 8760 * d.electricity_jpy_per_kwh * request.budget.tco_years);
      const capex = v.cost + v.contingency;
      return {price_case: priceCase, status: "partial", gap_ids: candidate.gaps.map(g => g.gap_id),
        quantities: {compute_units: v.n, gpu_count: v.n * p.gpus_per_node, host_cpu_count: v.n * p.cpus_per_node,
          host_memory_gb: v.n * p.host_memory_gb, hbm_capacity_gb: v.n * p.gpus_per_node * p.hbm_gb_per_gpu,
          local_nvme_tb: v.n * (p.local_nvme_tb + v.modules * d.local_nvme_module_tb), shared_fast_capacity_pb: v.blocks * d.storage_block_tb / 1000,
          rack_count: v.racks, fabric, cpu_model: p.cpu_model},
        power: {total_kw: v.power, basis: "configurator-plus-overhead-assumption", facility_fit: "unverified"},
        costs: {line_items: v.lines, configuration_cost_jpy: v.cost, contingency_jpy: v.contingency, unused_budget_jpy: budget - capex,
          budget_ceiling_jpy: budget, identity_verified: v.cost + v.contingency + (budget - capex) === budget},
        tco: {total_tco_jpy: null, capex_plus_energy_jpy: capex + energy, energy_jpy: energy, years: request.budget.tco_years, completeness: "partial"},
        price_basis_date: p.price_basis_date, sensitivity_factor: factor, extrapolation_years: years};
    });
    if (candidate.cases.every(c => c.status === "blocked")) candidate.status = "blocked";
    return candidate;
  }
  const api = {ENGINE_VERSION: "concept-estimate-0.1.0", evaluate, compatible, dateWindow};
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  root.OpenFSGpuEstimates = api;
})(typeof globalThis !== "undefined" ? globalThis : this);
