(() => {
  "use strict";

  const PRICE_CASES = ["optimistic", "baseline", "conservative"];
  const DATA_PATHS = ["request.json", "architecture.json", "product-catalog.json", "availability.json", "what-if-template.json"];
  const state = {language: "ja", mode: "public-evidence", source: null, latest: null, latestRequest: null, latestCost: null};

  const copy = {
    modePublic: {
      ja: "公開根拠だけを使用します。価格、調達時期、施設条件、需要または性能の根拠が不足する場合は「算定不能」とCoverage Gapを表示します。",
      en: "Uses public evidence only. Missing price, procurement, facility, demand, or performance evidence remains unavailable and is reported as a Coverage Gap."
    },
    modeWhatIf: {
      ja: "利用者が入力した仮定から3価格ケースを再計算します。結果は仮定に依存する試算であり、調達判断には使用できません。",
      en: "Recalculates three price cases from user-entered assumptions. Results depend on those assumptions and cannot be used for procurement decisions."
    },
    unavailable: {ja: "算定不能", en: "Unavailable"},
    vendorQuote: {ja: "算定不能 / 要ベンダー見積", en: "Unavailable / vendor quote required"},
    publicMode: {ja: "公開根拠", en: "Public evidence"},
    whatIfMode: {ja: "What-if（利用者入力）", en: "What-if (user input)"},
    status: {ja: "状態", en: "Status"},
    product: {ja: "候補製品", en: "Candidate product"},
    availability: {ja: "調達可能性", en: "Procurement availability"},
    priceCase: {ja: "価格ケース", en: "Price case"},
    procurementUnit: {ja: "最小調達単位", en: "Procurement unit"},
    computeUnits: {ja: "計算単位数", en: "Compute units"},
    gpuCount: {ja: "総GPU数", en: "Total GPUs"},
    computeRackCount: {ja: "計算ラック数", en: "Compute racks"},
    rackCount: {ja: "制約対象ラック数", en: "Racks counted toward limit"},
    hbm: {ja: "総HBM", en: "Total HBM"},
    hostCpu: {ja: "ホストCPU", en: "Host CPUs"},
    hostMemory: {ja: "ホストメモリ", en: "Host memory"},
    localNvme: {ja: "ローカルNVMe", en: "Local NVMe"},
    power: {ja: "IT電力", en: "IT power"},
    configCost: {ja: "構成費用", en: "Configuration cost"},
    contingency: {ja: "予備費", en: "Contingency"},
    unused: {ja: "未使用予算", en: "Unused budget"},
    tco: {ja: "複数年TCO", en: "Multi-year TCO"},
    constraints: {ja: "制約判定", en: "Constraint checks"},
    bom: {ja: "初期整備費BOM", en: "Initial CAPEX BOM"},
    performance: {ja: "性能予測", en: "Performance prediction"},
    software: {ja: "ソフトウェアスタック", en: "Software stack"},
    architecture: {ja: "構成図", en: "Architecture"},
    gaps: {ja: "Coverage Gap", en: "Coverage Gaps"},
    noPareto: {ja: "Pareto候補は算定されていません。", en: "Pareto candidates were not computed."},
    userAssumption: {ja: "利用者仮定", en: "User assumption"},
    publicEvidence: {ja: "公開根拠", en: "Public evidence"},
    pass: {ja: "適合", en: "Pass"},
    fail: {ja: "不適合", en: "Fail"},
    unknown: {ja: "未確認", en: "Unknown"},
    blocked: {ja: "算定不能", en: "Blocked"},
    partial: {ja: "暫定試算", en: "Provisional estimate"},
    feasible: {ja: "制約適合（暫定）", en: "Constraint-feasible (provisional)"},
    optimistic: {ja: "楽観価格", en: "Optimistic"},
    baseline: {ja: "基準価格", en: "Baseline"},
    conservative: {ja: "保守価格", en: "Conservative"},
    detail: {ja: "内訳・制約・根拠", en: "BOM, constraints, and evidence"},
    inputError: {ja: "入力値を確認してください。", en: "Review the input values."},
    loadedTest: {ja: "合成受入例を入力しました。公開根拠ではありません。", en: "Loaded the synthetic acceptance example. It is not public evidence."},
    importDone: {ja: "ローカルJSONを読み込みました。データは外部へ送信されていません。", en: "Loaded local JSON. No data was transmitted externally."}
  };

  const text = (key) => copy[key] ? copy[key][state.language] : key;
  const clone = (value) => JSON.parse(JSON.stringify(value));
  const byId = (id) => document.getElementById(id);
  const number = (id) => {
    const value = byId(id).value.trim();
    return value === "" || !Number.isFinite(Number(value)) ? null : Number(value);
  };
  const string = (id) => byId(id).value.trim() || null;
  const formatNumber = (value, digits = 0) => value == null
    ? text("unavailable")
    : new Intl.NumberFormat(state.language === "ja" ? "ja-JP" : "en-US", {maximumFractionDigits: digits}).format(value);
  const formatOku = (value) => value == null ? text("unavailable") : formatNumber(value / 100000000, 2) + (state.language === "ja" ? " 億円" : " x JPY 100m");
  const formatStatus = (value) => copy[value] ? text(value) : value || text("unknown");

  function applyLanguage(language) {
    state.language = language;
    document.documentElement.lang = language;
    document.body.dataset.language = language;
    document.querySelectorAll("[data-ja][data-en]").forEach((node) => {
      node.textContent = node.dataset[language];
    });
    document.querySelectorAll("[data-language]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.language === language));
    });
    const url = new URL(location.href);
    url.searchParams.set("lang", language);
    history.replaceState(null, "", url);
    document.title = (language === "ja"
      ? "GPU集中型AI for Science構成算定 Candidate"
      : "GPU-Centric AI for Science Configuration Candidate") + " | OpenFS";
    renderMode();
    if (state.latest) renderResult(state.latest);
  }

  function element(name, className, value) {
    const node = document.createElement(name);
    if (className) node.className = className;
    if (value != null) node.textContent = value;
    return node;
  }

  function createInput(id, type = "number", options = {}) {
    const input = document.createElement("input");
    input.id = id;
    input.type = type;
    if (type === "number") {
      input.min = options.min == null ? "0" : String(options.min);
      input.step = options.step == null ? "any" : String(options.step);
    }
    input.placeholder = options.placeholder || "unknown";
    return input;
  }

  function createField(parent, id, ja, en, type = "number", options = {}) {
    const label = element("label");
    const title = element("span", null, state.language === "ja" ? ja : en);
    title.dataset.ja = ja;
    title.dataset.en = en;
    const input = createInput(id, type, options);
    label.append(title, input);
    parent.append(label);
    return input;
  }

  const packageFields = [
    ["gpus_per_unit", "GPU数 / 計算単位", "GPUs per unit"],
    ["host_cpus_per_unit", "CPU数 / 計算単位", "Host CPUs per unit"],
    ["units_per_rack", "計算単位数 / ラック", "Units per rack"],
    ["nodes_per_unit", "ノード数 / 計算単位", "Nodes per unit"],
    ["trays_per_unit", "トレイ数 / 計算単位", "Trays per unit"],
    ["power_kw_per_unit", "電力（kW）/ 計算単位", "Power (kW) per unit"],
    ["hbm_gib_per_gpu", "HBM（GiB）/ GPU", "HBM (GiB) per GPU"],
    ["host_memory_gib_per_unit", "ホストメモリ（GiB）/ 計算単位", "Host memory (GiB) per unit"],
    ["local_nvme_tb_per_unit", "ローカルNVMe（TB）/ 計算単位", "Local NVMe (TB) per unit"],
    ["rack_footprint_m2", "ラック占有面積（m²）", "Rack footprint (m²)"],
    ["rack_weight_kg", "ラック重量（kg）", "Rack weight (kg)"],
    ["spare_percent", "予備計算単位（%）", "Spare compute units (%)"],
    ["portability_risk_score", "移植性リスク（0-1）", "Portability risk (0-1)"]
  ];
  const networkFields = [
    ["endpoint_ports_per_unit", "エンドポイント数 / 計算単位", "Endpoints per unit"],
    ["nics_per_unit", "NIC数 / 計算単位", "NICs per unit"],
    ["switch_ports", "スイッチポート数", "Switch ports"],
    ["max_port_utilization", "最大ポート利用率（0-1）", "Maximum port utilization (0-1)"],
    ["redundant_switches", "冗長スイッチ数", "Redundant switches"],
    ["max_switch_count", "スイッチ数上限", "Switch-count limit"],
    ["optics_per_endpoint", "光モジュール数 / エンドポイント", "Optics per endpoint"],
    ["cables_per_endpoint", "ケーブル数 / エンドポイント", "Cables per endpoint"],
    ["blocking_ratio", "ネットワーク非閉塞率", "Network nonblocking ratio"]
  ];
  const storageFields = [
    ["fast_capacity_pb_per_appliance", "高速容量（PB）/ 装置", "Fast capacity (PB) per appliance"],
    ["fast_read_gb_s_per_appliance", "読込（GB/s）/ 装置", "Read (GB/s) per appliance"],
    ["fast_write_gb_s_per_appliance", "書込（GB/s）/ 装置", "Write (GB/s) per appliance"],
    ["metadata_million_inodes_per_appliance", "メタデータ（百万inode）/ 装置", "Metadata (million inodes) per appliance"],
    ["archive_capacity_pb_per_appliance", "アーカイブ容量（PB）/ 装置", "Archive capacity (PB) per appliance"],
    ["minimum_controller_count", "最小コントローラ数", "Minimum controllers"],
    ["max_fast_storage_appliances", "高速装置数上限", "Fast-appliance limit"],
    ["max_archive_storage_appliances", "アーカイブ装置数上限", "Archive-appliance limit"],
    ["controllers_per_appliance", "コントローラ数 / 装置", "Controllers per appliance"],
    ["appliances_per_rack", "装置数 / ラック", "Appliances per rack"]
  ];
  const serviceFields = [
    ["login_min_nodes", "最小ログインノード数", "Minimum login nodes"],
    ["concurrent_users_per_login_node", "同時利用者数 / ログインノード", "Concurrent users per login node"],
    ["management_min_nodes", "最小管理ノード数", "Minimum management nodes"],
    ["compute_units_per_management_node", "計算単位数 / 管理ノード", "Compute units per management node"],
    ["monitoring_min_nodes", "最小監視ノード数", "Minimum monitoring nodes"],
    ["compute_units_per_monitoring_node", "計算単位数 / 監視ノード", "Compute units per monitoring node"],
    ["provisioning_min_nodes", "最小プロビジョニングノード数", "Minimum provisioning nodes"],
    ["compute_units_per_provisioning_node", "計算単位数 / プロビジョニングノード", "Compute units per provisioning node"],
    ["scheduler_min_nodes", "最小スケジューラノード数", "Minimum scheduler nodes"],
    ["authentication_min_nodes", "最小認証ノード数", "Minimum authentication nodes"],
    ["nodes_per_rack", "サービスノード数 / ラック", "Service nodes per rack"]
  ];
  const powerFields = [
    ["switch_kw", "スイッチ電力（kW）", "Switch power (kW)"],
    ["nic_kw", "NIC電力（kW）", "NIC power (kW)"],
    ["fast_storage_appliance_kw", "高速ストレージ電力（kW）", "Fast-storage power (kW)"],
    ["archive_storage_appliance_kw", "アーカイブ電力（kW）", "Archive-storage power (kW)"],
    ["service_node_kw", "サービスノード電力（kW）", "Service-node power (kW)"]
  ];

  function renderPackageInputs() {
    const root = byId("package-inputs");
    root.replaceChildren();
    for (const vendor of ["NVIDIA", "AMD"]) {
      const key = vendor.toLowerCase();
      const card = element("section", "planner-vendor-input");
      card.append(element("h3", null, vendor));
      const core = element("div", "planner-field-grid compact");
      const unitLabel = element("label");
      const unitTitle = element("span", null, state.language === "ja" ? "最小調達単位" : "Minimum procurement unit");
      unitTitle.dataset.ja = "最小調達単位"; unitTitle.dataset.en = "Minimum procurement unit";
      const unit = element("select"); unit.id = key + "-unit_type";
      [["", "unknown", "unknown"], ["node", "ノード", "Node"], ["tray", "トレイ", "Tray"], ["rack", "ラック", "Rack"]].forEach(([value, ja, en]) => {
        const option = new Option(state.language === "ja" ? ja : en, value);
        option.dataset.ja = ja; option.dataset.en = en; unit.add(option);
      });
      unitLabel.append(unitTitle, unit); core.append(unitLabel);
      const rackScopeLabel = element("label");
      const rackScopeTitle = element("span", null, state.language === "ja" ? "ラック上限制約の対象" : "Rack-limit scope");
      rackScopeTitle.dataset.ja = "ラック上限制約の対象"; rackScopeTitle.dataset.en = "Rack-limit scope";
      const rackScope = element("select"); rackScope.id = key + "-include-auxiliary-racks";
      [["true", "計算・サービス・ストレージラック", "Compute, service, and storage racks"], ["false", "計算ラックのみ", "Compute racks only"]].forEach(([value, ja, en]) => {
        const option = new Option(state.language === "ja" ? ja : en, value);
        option.dataset.ja = ja; option.dataset.en = en; rackScope.add(option);
      });
      rackScopeLabel.append(rackScopeTitle, rackScope); core.append(rackScopeLabel);
      packageFields.forEach(([field, ja, en]) => createField(core, key + "-" + field, ja, en));
      card.append(core);
      const sections = [
        ["ネットワーク構成", "Network sizing", networkFields, "network"],
        ["ストレージ能力", "Storage capability", storageFields, "storage_capability"],
        ["サービスノード算定", "Service-node sizing", serviceFields, "service_sizing"],
        ["付帯電力", "Auxiliary power", powerFields, "power_profile"]
      ];
      sections.forEach(([ja, en, fields, prefix]) => {
        const details = element("details", "planner-nested-input");
        const summary = element("summary", null, state.language === "ja" ? ja : en);
        summary.dataset.ja = ja; summary.dataset.en = en;
        const grid = element("div", "planner-field-grid compact");
        fields.forEach(([field, labelJa, labelEn]) => createField(grid, key + "-" + prefix + "-" + field, labelJa, labelEn));
        if (prefix === "network") createField(grid, key + "-network-topology", "トポロジー", "Topology", "text");
        details.append(summary, grid); card.append(details);
      });
      const procurement = element("div", "planner-field-grid compact");
      const eligibleLabel = element("label");
      const eligibleTitle = element("span", null, state.language === "ja" ? "受入日までの調達を仮定" : "Assume procurement by acceptance date");
      eligibleTitle.dataset.ja = "受入日までの調達を仮定"; eligibleTitle.dataset.en = "Assume procurement by acceptance date";
      const eligible = element("select"); eligible.id = key + "-eligible";
      [["", "未確認", "Unknown"], ["true", "はい（利用者仮定）", "Yes (user assumption)"], ["false", "いいえ", "No"]].forEach(([value, ja, en]) => {
        const option = new Option(state.language === "ja" ? ja : en, value);
        option.dataset.ja = ja; option.dataset.en = en; eligible.add(option);
      });
      eligibleLabel.append(eligibleTitle, eligible); procurement.append(eligibleLabel);
      createField(procurement, key + "-delivery-date", "最遅納入日", "Latest delivery date", "date");
      createField(procurement, key + "-support-status", "保守状態", "Support status", "text");
      card.append(procurement);
      root.append(card);
    }
  }

  function renderCostInputs() {
    const root = byId("cost-inputs");
    root.replaceChildren();
    const template = state.source[4];
    for (const templatePackage of template.packages) {
      const key = templatePackage.vendor.toLowerCase();
      const card = element("section", "planner-vendor-input");
      card.append(element("h3", null, templatePackage.vendor));
      const wrap = element("div", "table-wrap");
      const table = element("table", "planner-cost-table");
      const head = element("thead"); const row = element("tr");
      [["費目", "Cost item"], ["基準", "Basis"], [copy.optimistic.ja, copy.optimistic.en], [copy.baseline.ja, copy.baseline.en], [copy.conservative.ja, copy.conservative.en]].forEach(([ja, en]) => {
        const heading = element("th", null, state.language === "ja" ? ja : en);
        heading.dataset.ja = ja; heading.dataset.en = en; row.append(heading);
      });
      head.append(row);
      const body = element("tbody");
      templatePackage.cost_lines.forEach((line, index) => {
        const tr = element("tr");
        tr.append(element("th", null, state.language === "ja" ? line.label_ja : line.label_en));
        tr.append(element("td", "mono-list", line.basis + " / " + line.period));
        PRICE_CASES.forEach((priceCase) => {
          const td = element("td");
          const input = createInput(key + "-cost-" + index + "-" + priceCase);
          input.setAttribute("aria-label", (state.language === "ja" ? line.label_ja : line.label_en) + " " + text(priceCase));
          td.append(input); tr.append(td);
        });
        body.append(tr);
      });
      table.append(head, body); wrap.append(table); card.append(wrap); root.append(card);
    }
  }

  function renderDynamicInputLabels() {
    renderPackageInputs();
    renderCostInputs();
  }

  function renderProductOptions() {
    const catalog = state.source[2];
    for (const vendor of ["NVIDIA", "AMD"]) {
      const select = byId("product-" + vendor.toLowerCase());
      const previous = select.value;
      const automatic = new Option(state.language === "ja" ? "自動選択" : "Automatic", "auto");
      automatic.dataset.ja = "自動選択"; automatic.dataset.en = "Automatic";
      select.replaceChildren(automatic);
      catalog.products.filter((product) => product.vendor === vendor).forEach((product) => {
        const event = (product.events || []).at(-1);
        const date = event ? event.date.value : (state.language === "ja" ? "時期未確認" : "date unknown");
        select.add(new Option(product.model + " (" + date + ")", product.product_id));
      });
      select.value = previous && [...select.options].some((option) => option.value === previous) ? previous : "auto";
    }
  }

  function renderMode() {
    const isWhatIf = state.mode === "what-if";
    byId("mode-public").classList.toggle("active", !isWhatIf);
    byId("mode-public").setAttribute("aria-pressed", String(!isWhatIf));
    byId("mode-whatif").classList.toggle("active", isWhatIf);
    byId("mode-whatif").setAttribute("aria-pressed", String(isWhatIf));
    byId("mode-description").textContent = isWhatIf ? text("modeWhatIf") : text("modePublic");
    document.querySelectorAll(".whatif-only").forEach((node) => { node.hidden = !isWhatIf; });
    document.querySelectorAll("#planner-form input, #planner-form select").forEach((control) => {
      control.disabled = !isWhatIf;
    });
    byId("reset-inputs").disabled = false;
    byId("calculate").disabled = false;
  }

  function populatePublicInputs() {
    const request = state.source[0];
    const values = {
      capex: request.budget.capex_ceiling_oku_jpy,
      "acceptance-date": request.schedule.required_acceptance_date,
      "vendor-mode": request.vendor_mode,
      deployment: request.deployment_mode,
      "tco-years": request.budget.tco_years,
      contingency: request.budget.contingency_percent,
      "product-nvidia": request.product_selection.nvidia,
      "product-amd": request.product_selection.amd,
      "mix-training": request.workloads.mix_percent.ai_training,
      "mix-inference": request.workloads.mix_percent.ai_inference,
      "mix-hpc": request.workloads.mix_percent.ai_for_science_hpc,
      "mix-data": request.workloads.mix_percent.data_analytics,
      utilization: request.workloads.utilization_target_percent,
      headroom: request.workloads.headroom_percent,
      "annual-gpu-hours": request.workloads.absolute_demand.annual_accelerator_hours,
      "training-tokens": request.workloads.absolute_demand.training_tokens_per_year,
      "training-jobs": request.workloads.absolute_demand.training_jobs_per_year,
      "hpc-jobs": request.workloads.absolute_demand.hpc_jobs_per_year,
      "hpc-gpus": request.workloads.absolute_demand.hpc_accelerators_per_job,
      "hpc-runtime": request.workloads.absolute_demand.hpc_mean_runtime_hours,
      "inference-requests": request.workloads.absolute_demand.inference_requests_per_year,
      "peak-rps": request.workloads.absolute_demand.peak_requests_per_second,
      "data-ingest": request.workloads.absolute_demand.data_ingest_pb_per_year,
      "concurrent-users": request.workloads.absolute_demand.concurrent_users,
      "power-mw": request.facility.it_power_limit_mw,
      "cooling-mw": request.facility.cooling_capacity_mw,
      "cooling-method": request.facility.cooling_method,
      "rack-limit": request.facility.rack_limit,
      "floor-area": request.facility.floor_area_m2,
      "floor-loading": request.facility.floor_loading_kg_m2,
      "rack-density": request.facility.rack_density_kw,
      pue: request.facility.pue,
      "power-redundancy": request.facility.power_redundancy === "unknown" ? null : request.facility.power_redundancy,
      "cooling-redundancy": request.facility.cooling_redundancy === "unknown" ? null : request.facility.cooling_redundancy,
      "fast-pb": request.storage.shared_fast_capacity_pb,
      "archive-pb": request.storage.archive_capacity_pb,
      "read-gbs": request.storage.training_read_gb_s,
      "write-gbs": request.storage.checkpoint_write_gb_s,
      "metadata-m": request.storage.metadata_million_inodes,
      "backup-copies": request.storage.backup_copies,
      "retention-years": request.storage.retention_years,
      "rto-hours": request.storage.rto_hours,
      "local-nvme-required": request.storage.local_nvme_tb_per_compute_unit
    };
    Object.entries(values).forEach(([id, value]) => {
      if (byId(id)) byId(id).value = value == null ? "" : String(value);
    });
  }

  function packageFromInputs(templatePackage) {
    const result = clone(templatePackage);
    const key = result.vendor.toLowerCase();
    const productId = byId("product-" + key).value;
    result.product_id = productId === "auto" ? templatePackage.product_id : productId;
    const product = state.source[2].products.find((item) => item.product_id === result.product_id);
    result.product_label = product ? product.model : templatePackage.product_label;
    result.allow_product_override = true;
    result.unit_type = byId(key + "-unit_type").value || null;
    packageFields.forEach(([field]) => { result[field] = number(key + "-" + field); });
    networkFields.forEach(([field]) => { result.network[field] = number(key + "-network-" + field); });
    result.network.topology = string(key + "-network-topology") || "";
    storageFields.forEach(([field]) => { result.storage_capability[field] = number(key + "-storage_capability-" + field); });
    serviceFields.forEach(([field]) => { result.service_sizing[field] = number(key + "-service_sizing-" + field); });
    powerFields.forEach(([field]) => { result.power_profile[field] = number(key + "-power_profile-" + field); });
    const eligible = byId(key + "-eligible").value;
    result.procurement_assumption = {
      eligible: eligible === "" ? null : eligible === "true",
      latest_delivery_date: string(key + "-delivery-date"),
      support_status: string(key + "-support-status") || "unconfirmed"
    };
    result.include_auxiliary_racks = byId(key + "-include-auxiliary-racks").value !== "false";
    result.cost_lines.forEach((line, index) => {
      PRICE_CASES.forEach((priceCase) => {
        const value = number(key + "-cost-" + index + "-" + priceCase);
        line[priceCase + "_jpy"] = value == null ? null : value * 100000000;
      });
      line.evidence_status = "user-assumption";
      line.as_of = new Date().toISOString().slice(0, 10);
      line.tax_basis = "unknown";
      line.scope_note = "Browser-local user assumption; not public evidence.";
      line.source_ids = [];
    });
    result.source_ids = [];
    return result;
  }

  function performanceInput(request) {
    const fields = ["perf-units", "perf-compute", "perf-memory", "perf-communication", "perf-io", "perf-nonoverlap", "perf-sync", "perf-efficiency", "perf-error"];
    if (fields.some((id) => number(id) == null) || !string("perf-benchmark")) {
      request.performance_model.phase_baseline = null;
    } else {
      const efficiency = number("perf-efficiency");
      const error = number("perf-error");
      request.performance_model.phase_baseline = {
        status: "provisional",
        benchmark: string("perf-benchmark"),
        measured_compute_units: number("perf-units"),
        compute_time_s: number("perf-compute"),
        memory_time_s: number("perf-memory"),
        communication_time_s: number("perf-communication"),
        io_time_s: number("perf-io"),
        non_overlappable_time_s: number("perf-nonoverlap"),
        synchronization_time_s: number("perf-sync"),
        scaling_efficiency: {optimistic: Math.min(1, efficiency * 1.05), baseline: efficiency, conservative: Math.max(0.01, efficiency * 0.9)},
        error_percent: {optimistic: error, baseline: error, conservative: error},
        measured_configuration: "Browser-local user input",
        software_stack: [],
        source_kind: "user-assumption",
        source_ids: []
      };
    }
    if ([number("queue-service-rate"), number("queue-ttft"), number("queue-tpot")].some((value) => value == null)) {
      request.performance_model.inference_baseline = null;
    } else {
      request.performance_model.inference_baseline = {
        status: "provisional",
        service_rate_rps_per_gpu: number("queue-service-rate"),
        base_ttft_ms: number("queue-ttft"),
        base_tpot_ms: number("queue-tpot")
      };
    }
  }

  function requestFromInputs() {
    if (state.mode !== "what-if") return clone(state.source[0]);
    const request = clone(state.source[0]);
    request.run_mode = "what-if";
    request.information_classification = "public";
    request.budget.capex_ceiling_oku_jpy = number("capex");
    request.budget.tco_years = number("tco-years");
    request.budget.contingency_percent = number("contingency");
    request.schedule.required_acceptance_date = byId("acceptance-date").value;
    request.schedule.acceptance_year = Number(request.schedule.required_acceptance_date.slice(0, 4));
    request.vendor_mode = byId("vendor-mode").value;
    request.product_selection = {nvidia: byId("product-nvidia").value, amd: byId("product-amd").value};
    request.deployment_mode = byId("deployment").value;
    Object.assign(request.facility, {
      it_power_limit_mw: number("power-mw"),
      it_power_limit_status: number("power-mw") == null ? "unknown" : "user-input",
      cooling_method: byId("cooling-method").value,
      cooling_capacity_mw: number("cooling-mw"),
      cooling_capacity_status: number("cooling-mw") == null ? "unknown" : "user-input",
      rack_limit: number("rack-limit"),
      floor_area_m2: number("floor-area"),
      floor_loading_kg_m2: number("floor-loading"),
      rack_density_kw: number("rack-density"),
      pue: number("pue"),
      power_redundancy: string("power-redundancy") || "unknown",
      cooling_redundancy: string("cooling-redundancy") || "unknown",
      facility_work_in_capex: null
    });
    request.workloads.mix_percent = {
      ai_training: number("mix-training"),
      ai_inference: number("mix-inference"),
      ai_for_science_hpc: number("mix-hpc"),
      data_analytics: number("mix-data")
    };
    request.workloads.utilization_target_percent = number("utilization");
    request.workloads.headroom_percent = number("headroom");
    const hpcHours = [number("hpc-jobs"), number("hpc-gpus"), number("hpc-runtime")].every((value) => value != null)
      ? number("hpc-jobs") * number("hpc-gpus") * number("hpc-runtime") : null;
    Object.assign(request.workloads.absolute_demand, {
      annual_accelerator_hours: number("annual-gpu-hours"),
      training_accelerator_hours_per_year: null,
      training_tokens_per_year: number("training-tokens"),
      training_jobs_per_year: number("training-jobs"),
      hpc_jobs_per_year: number("hpc-jobs"),
      hpc_accelerator_hours_per_year: hpcHours,
      hpc_accelerators_per_job: number("hpc-gpus"),
      hpc_mean_runtime_hours: number("hpc-runtime"),
      inference_requests_per_year: number("inference-requests"),
      peak_requests_per_second: number("peak-rps"),
      data_ingest_pb_per_year: number("data-ingest"),
      concurrent_users: number("concurrent-users")
    });
    Object.assign(request.storage, {
      shared_fast_capacity_pb: number("fast-pb"),
      archive_capacity_pb: number("archive-pb"),
      checkpoint_write_gb_s: number("write-gbs"),
      training_read_gb_s: number("read-gbs"),
      metadata_million_inodes: number("metadata-m"),
      backup_copies: number("backup-copies"),
      retention_years: number("retention-years"),
      rto_hours: number("rto-hours"),
      local_nvme_tb_per_compute_unit: number("local-nvme-required")
    });
    Object.assign(request.inference, {
      model_name: string("model-name"),
      parameter_count_billion: number("parameter-b"),
      quantization: string("quantization"),
      input_tokens: number("input-tokens"),
      output_tokens: number("output-tokens"),
      context_tokens: number("context-tokens"),
      concurrent_users: number("concurrent-users"),
      request_rate_per_second: number("peak-rps"),
      ttft_p50_ms: number("ttft-p50"),
      ttft_p95_ms: number("ttft-p95"),
      ttft_p99_ms: number("ttft-p99"),
      tpot_p50_ms: number("tpot-p50"),
      tpot_p95_ms: number("tpot-p95"),
      tpot_p99_ms: number("tpot-p99"),
      offline_throughput_target: number("offline-throughput"),
      server_throughput_target: number("server-throughput"),
      quality_target_id: string("quality-id")
    });
    performanceInput(request);
    return request;
  }

  function costFromInputs() {
    if (state.mode !== "what-if") return null;
    const cost = clone(state.source[4]);
    cost.cost_input_id = "COSTINPUT-BROWSER-LOCAL-USER-001";
    cost.status = "candidate";
    cost.information_classification = "local-user-input";
    cost.input_mode = "user-input";
    cost.as_of = new Date().toISOString().slice(0, 10);
    cost.packages = cost.packages.map(packageFromInputs);
    return cost;
  }

  function validateRequest(request) {
    const mix = Object.values(request.workloads.mix_percent);
    if (mix.some((value) => value == null) || Math.abs(mix.reduce((sum, value) => sum + value, 0) - 100) > 1e-9) {
      throw new Error(state.language === "ja" ? "ワークロード比率の合計を100%にしてください。" : "Workload percentages must total 100%.");
    }
    if (!request.schedule.required_acceptance_date || request.budget.capex_ceiling_oku_jpy == null) throw new Error(text("inputError"));
  }

  function evaluate() {
    try {
      byId("form-error").textContent = "";
      const request = requestFromInputs();
      validateRequest(request);
      const cost = costFromInputs();
      state.latestRequest = request;
      state.latestCost = cost;
      state.latest = OpenFSGpuPlanner.evaluate(request, state.source[1], state.source[2], state.source[3], cost);
      renderResult(state.latest);
    } catch (error) {
      byId("form-error").textContent = error.message || text("inputError");
    }
  }

  function definitionList(rows) {
    const dl = element("dl", "planner-metrics");
    rows.forEach(([term, value]) => {
      const group = element("div");
      group.append(element("dt", null, term), element("dd", null, value));
      dl.append(group);
    });
    return dl;
  }

  function baselineCase(candidate) {
    return candidate.cases.find((item) => item.price_case === "baseline") || candidate.cases[0];
  }

  function summaryCard(candidate) {
    const value = baselineCase(candidate);
    const q = value.quantities || {};
    const card = element("article", "planner-result");
    const head = element("div", "planner-result-head");
    head.append(element("h3", null, candidate.vendor), element("span", "status-badge status-" + candidate.status, formatStatus(candidate.status)));
    card.append(head);
    card.append(definitionList([
      [text("product"), candidate.product_name || candidate.product_id || text("unavailable")],
      [text("availability"), formatStatus(candidate.availability_status)],
      [text("gpuCount"), formatNumber(q.gpu_count)],
      [text("computeRackCount"), formatNumber(q.compute_racks)],
      [text("rackCount"), formatNumber(q.rack_count)],
      [text("power"), value.power ? formatNumber(value.power.total_kw, 1) + " kW" : text("unavailable")],
      [text("configCost"), formatOku(value.costs.configuration_cost_jpy)],
      [text("tco"), formatOku(value.tco.total_tco_jpy)]
    ]));
    if (value.status === "blocked") card.append(element("p", "planner-blocking", text("vendorQuote") + ": " + value.blocking_reason));
    return card;
  }

  function comparisonTable(candidates) {
    const table = element("table", "planner-comparison-table");
    const head = element("thead"); const hr = element("tr"); hr.append(element("th", null, state.language === "ja" ? "項目" : "Item"));
    candidates.forEach((candidate) => hr.append(element("th", null, candidate.vendor + " / " + text("baseline"))));
    head.append(hr);
    const rows = [
      [text("product"), (candidate) => candidate.product_name || candidate.product_id || text("unavailable")],
      [text("procurementUnit"), (candidate) => baselineCase(candidate).unit_type || text("unavailable")],
      [text("computeUnits"), (candidate) => formatNumber(baselineCase(candidate).quantities?.compute_units)],
      [text("gpuCount"), (candidate) => formatNumber(baselineCase(candidate).quantities?.gpu_count)],
      [text("hbm"), (candidate) => baselineCase(candidate).quantities?.total_hbm_gib == null ? text("unavailable") : formatNumber(baselineCase(candidate).quantities.total_hbm_gib / 1024, 1) + " TiB"],
      [text("computeRackCount"), (candidate) => formatNumber(baselineCase(candidate).quantities?.compute_racks)],
      [text("rackCount"), (candidate) => formatNumber(baselineCase(candidate).quantities?.rack_count)],
      [text("power"), (candidate) => baselineCase(candidate).power ? formatNumber(baselineCase(candidate).power.total_kw, 1) + " kW" : text("unavailable")],
      [text("configCost"), (candidate) => formatOku(baselineCase(candidate).costs.configuration_cost_jpy)],
      [text("contingency"), (candidate) => formatOku(baselineCase(candidate).costs.contingency_jpy)],
      [text("unused"), (candidate) => formatOku(baselineCase(candidate).costs.unused_budget_jpy)],
      [text("tco"), (candidate) => formatOku(baselineCase(candidate).tco.total_tco_jpy)]
    ];
    const body = element("tbody");
    rows.forEach(([label, getter]) => {
      const row = element("tr"); row.append(element("th", null, label));
      candidates.forEach((candidate) => row.append(element("td", null, getter(candidate))));
      body.append(row);
    });
    table.append(head, body);
    return table;
  }

  function architectureDiagram(candidate, value) {
    const q = value.quantities;
    const figure = element("figure", "gpu-architecture-diagram");
    if (!q) {
      figure.append(element("p", "planner-blocking", text("vendorQuote")));
      return figure;
    }
    const service = element("div", "gpu-arch-row service");
    service.append(element("span", null, (state.language === "ja" ? "管理・サービス " : "Management & services ") + formatNumber(q.service_node_count)));
    const compute = element("div", "gpu-arch-row compute");
    compute.append(
      element("span", null, candidate.vendor + " " + (candidate.product_name || "")),
      element("strong", null, formatNumber(q.gpu_count) + " GPU"),
      element("span", null, formatNumber(q.host_cpu_count) + " CPU")
    );
    const network = element("div", "gpu-arch-row network");
    network.append(element("span", null, (state.language === "ja" ? "スケールアウト " : "Scale-out ") + formatNumber(q.switch_count) + " switches / " + formatNumber(q.network_endpoints) + " endpoints"));
    const storage = element("div", "gpu-arch-row storage");
    storage.append(element("span", null, (state.language === "ja" ? "高速 / アーカイブ装置 " : "Fast / archive appliances ") + formatNumber(q.fast_storage_appliances) + " / " + formatNumber(q.archive_storage_appliances)));
    figure.append(service, element("div", "gpu-arch-connector", "↓"), compute, element("div", "gpu-arch-connector", "↓"), network, element("div", "gpu-arch-connector", "↓"), storage);
    return figure;
  }

  function costTable(value) {
    const table = element("table", "planner-bom-table");
    const head = element("thead"); const hr = element("tr");
    [state.language === "ja" ? "費目" : "Scope", state.language === "ja" ? "数量" : "Quantity", state.language === "ja" ? "単価" : "Unit price", state.language === "ja" ? "小計" : "Subtotal"].forEach((v) => hr.append(element("th", null, v)));
    head.append(hr); const body = element("tbody");
    (value.costs.line_items || []).forEach((line) => {
      const row = element("tr");
      row.append(element("th", null, line.category), element("td", null, formatNumber(line.quantity, 2)), element("td", null, formatOku(line.unit_price_jpy)), element("td", null, formatOku(line.subtotal_jpy)));
      body.append(row);
    });
    table.append(head, body); return table;
  }

  function constraintTable(value) {
    const table = element("table", "planner-constraint-table");
    const head = element("thead"); const hr = element("tr");
    [state.language === "ja" ? "制約" : "Constraint", text("status"), state.language === "ja" ? "実績" : "Actual", state.language === "ja" ? "上限・要求" : "Limit / requirement", state.language === "ja" ? "不足・超過" : "Shortfall / excess"].forEach((v) => hr.append(element("th", null, v)));
    head.append(hr); const body = element("tbody");
    Object.entries(value.constraints || {}).forEach(([name, check]) => {
      const row = element("tr");
      row.append(
        element("th", null, name),
        element("td", "constraint-" + check.status, formatStatus(check.status)),
        element("td", null, check.actual == null ? text("unavailable") : String(check.actual) + " " + check.unit),
        element("td", null, check.limit == null ? text("unavailable") : String(check.limit) + " " + check.unit),
        element("td", null, check.shortfall == null ? "—" : String(check.shortfall) + " " + check.unit)
      );
      body.append(row);
    });
    table.append(head, body); return table;
  }

  function performancePanel(value) {
    const root = element("div", "planner-performance");
    const performance = value.performance;
    root.append(element("p", null, (state.language === "ja" ? "モデル: " : "Model: ") + performance.model));
    if (!performance.bounds) {
      root.append(element("p", "planner-blocking", state.language === "ja" ? "再現可能な実測基準がないため算定できません。" : "A reproducible measured baseline is unavailable."));
    } else {
      const selected = performance.bounds[value.price_case];
      root.append(definitionList([
        [state.language === "ja" ? "予測時間" : "Predicted time", formatNumber(selected.predicted_time_s, 3) + " s"],
        [state.language === "ja" ? "外挿倍率" : "Extrapolation ratio", formatNumber(selected.extrapolation_ratio, 2)],
        [state.language === "ja" ? "スケーリング効率" : "Scaling efficiency", formatNumber(selected.scaling_efficiency, 3)],
        [state.language === "ja" ? "誤差" : "Error", formatNumber(selected.error_percent, 1) + "%"]
      ]));
    }
    const queue = performance.inference_queue;
    const queueDetails = element("details");
    queueDetails.append(element("summary", null, state.language === "ja" ? "推論待ち行列モデル（M/M/c）" : "Inference queue model (M/M/c)"));
    queueDetails.append(element("pre", "planner-json", JSON.stringify(queue, null, 2)));
    root.append(queueDetails);
    return root;
  }

  function vendorDetails(candidate) {
    const card = element("section", "planner-vendor-result");
    card.append(element("h3", null, candidate.vendor + " — " + (candidate.product_name || candidate.product_id || text("unavailable"))));
    const baseline = baselineCase(candidate);
    const architecture = element("details"); architecture.open = true;
    architecture.append(element("summary", null, text("architecture")), architectureDiagram(candidate, baseline));
    card.append(architecture);
    const priceTable = element("table", "planner-price-case-table");
    const head = element("thead"); const hr = element("tr");
    [text("priceCase"), text("status"), text("gpuCount"), text("rackCount"), text("configCost"), text("tco")].forEach((v) => hr.append(element("th", null, v)));
    head.append(hr); const body = element("tbody");
    candidate.cases.forEach((value) => {
      const row = element("tr"); const q = value.quantities || {};
      row.append(element("th", null, text(value.price_case)), element("td", null, formatStatus(value.status)), element("td", null, formatNumber(q.gpu_count)), element("td", null, formatNumber(q.rack_count)), element("td", null, formatOku(value.costs.configuration_cost_jpy)), element("td", null, formatOku(value.tco.total_tco_jpy)));
      body.append(row);
    });
    priceTable.append(head, body); const priceWrap = element("div", "table-wrap"); priceWrap.append(priceTable); card.append(priceWrap);
    if (baseline.quantities) {
      card.append(definitionList([
        [text("hostCpu"), formatNumber(baseline.quantities.host_cpu_count)],
        [text("hostMemory"), formatNumber(baseline.quantities.host_memory_gib / 1024, 1) + " TiB"],
        [text("localNvme"), formatNumber(baseline.quantities.local_nvme_tb, 1) + " TB"],
        [state.language === "ja" ? "ログインノード" : "Login nodes", formatNumber(baseline.quantities.login_node_count)],
        [state.language === "ja" ? "管理 / 監視 / 配備" : "Management / monitoring / provisioning", [baseline.quantities.management_node_count, baseline.quantities.monitoring_node_count, baseline.quantities.provisioning_node_count].join(" / ")],
        [state.language === "ja" ? "スケジューラ / 認証" : "Scheduler / authentication", [baseline.quantities.scheduler_node_count, baseline.quantities.authentication_node_count].join(" / ")]
      ]));
    }
    const details = element("details"); details.append(element("summary", null, text("detail")));
    const constraintHeading = element("h4", null, text("constraints")); details.append(constraintHeading, constraintTable(baseline));
    const bomHeading = element("h4", null, text("bom")); details.append(bomHeading, costTable(baseline));
    const perfHeading = element("h4", null, text("performance")); details.append(perfHeading, performancePanel(baseline));
    const software = candidate.software_profile;
    if (software) details.append(element("p", null, text("software") + ": " + [...software.compute_stack, ...software.communication_stack, ...software.software_stack].join(", ")));
    card.append(details);
    return card;
  }

  function renderPareto(result) {
    const root = byId("pareto-result"); root.replaceChildren();
    const card = element("aside", "planner-pareto");
    const title = element("strong", null, state.language === "ja" ? "Pareto候補" : "Pareto candidates");
    const reason = element("p", null, state.language === "ja" ? result.pareto_result.reason_ja : result.pareto_result.reason_en);
    card.append(title, reason);
    if (result.pareto_result.candidate_refs.length) card.append(element("p", "mono-list", result.pareto_result.candidate_refs.join(" · ")));
    root.append(card);
  }

  function publicSourceIndex() {
    const index = new Map();
    const seen = new WeakSet();
    const visit = (value) => {
      if (!value || typeof value !== "object" || seen.has(value)) return;
      seen.add(value);
      if (typeof value.source_id === "string" && typeof value.url === "string" && !index.has(value.source_id)) index.set(value.source_id, value);
      Object.values(value).forEach(visit);
    };
    visit(window.OPENFS_PUBLIC_DATA);
    return index;
  }

  function sourceReferences(sourceIds) {
    const cell = element("td");
    const list = element("ul", "source-list planner-source-list");
    const index = publicSourceIndex();
    [...new Set(sourceIds)].forEach((sourceId) => {
      const item = element("li");
      const source = index.get(sourceId);
      if (source && /^https:\/\//.test(source.url)) {
        const link = element("a", null, source.title || sourceId);
        link.href = source.url; link.target = "_blank"; link.rel = "noopener noreferrer";
        item.append(link, element("span", "mono-list", sourceId));
      } else {
        item.append(element("span", "mono-list", sourceId));
      }
      list.append(item);
    });
    if (!list.childElementCount) list.append(element("li", null, text("unknown")));
    cell.append(list);
    return cell;
  }

  function renderEvidence(result) {
    const status = byId("evidence-status"); status.replaceChildren();
    status.append(definitionList([
      [state.language === "ja" ? "算定モード" : "Calculation mode", result.calculation_mode === "what-if" ? text("whatIfMode") : text("publicMode")],
      [state.language === "ja" ? "製品カタログ基準日" : "Product catalog as of", state.source[2].as_of],
      [state.language === "ja" ? "調達可能性確認日" : "Procurement evidence checked", state.source[3].as_of],
      [state.language === "ja" ? "調達利用" : "Procurement use", state.language === "ja" ? "禁止" : "Prohibited"],
      [state.language === "ja" ? "Consensus Gate" : "Consensus Gate", state.language === "ja" ? "未完了" : "Incomplete"]
    ]));
    const evidenceRoot = byId("product-evidence"); evidenceRoot.replaceChildren();
    const details = element("details");
    const detailsSummary = element("summary", null, state.language === "ja" ? "製品・調達可能性の公開根拠" : "Public product and procurement evidence");
    const wrap = element("div", "table-wrap");
    const table = element("table", "planner-evidence-table");
    const head = element("thead"); const headingRow = element("tr");
    [state.language === "ja" ? "製品" : "Product", state.language === "ja" ? "製品状況・最新イベント" : "Lifecycle and latest event", state.language === "ja" ? "調達可能性" : "Procurement availability", state.language === "ja" ? "確認日" : "Checked", state.language === "ja" ? "公開根拠" : "Public sources"].forEach((label) => headingRow.append(element("th", null, label)));
    head.append(headingRow); const body = element("tbody");
    const assessments = new Map(state.source[3].assessments.map((entry) => [entry.product_id, entry]));
    state.source[2].products.forEach((product) => {
      const assessment = assessments.get(product.product_id);
      const latestEvent = (product.events || []).at(-1);
      const row = element("tr");
      row.append(
        element("th", null, product.vendor + " " + product.model),
        element("td", null, product.lifecycle_status + (latestEvent ? " / " + latestEvent.event_type + " " + latestEvent.date.value + " (" + latestEvent.date.precision + ")" : "")),
        element("td", null, assessment ? assessment.availability_status : text("unknown")),
        element("td", null, assessment?.evidence_checked_date || product.evidence_checked_date || text("unknown")),
        sourceReferences([...(product.source_ids || []), ...(assessment?.source_ids || [])])
      );
      body.append(row);
    });
    table.append(head, body); wrap.append(table); details.append(detailsSummary, wrap); evidenceRoot.append(details);
    const allGaps = new Map();
    result.vendor_candidates.forEach((candidate) => candidate.gaps.forEach((gap) => allGaps.set(gap.gap_id + "/" + gap.scope, gap)));
    const root = byId("gap-list"); root.replaceChildren();
    if (!allGaps.size) root.append(element("p", null, state.language === "ja" ? "必須入力のCoverage Gapはありません。" : "No required-input Coverage Gaps."));
    allGaps.forEach((gap) => {
      const item = element("article", "planner-gap");
      item.append(element("strong", null, gap.gap_id + " · " + gap.scope), element("p", null, state.language === "ja" ? gap.statement_ja : gap.statement_en), element("p", "mono-list", gap.missing_items.join(", ")));
      root.append(item);
    });
    byId("benchmark-list").textContent = result.benchmark_candidates.join(" · ");
  }

  function renderResult(result) {
    byId("result-notice").textContent = result.messages_ja && state.language === "ja" ? result.messages_ja.join(" ") : result.messages_en.join(" ");
    renderPareto(result);
    const summary = byId("result-summary"); summary.replaceChildren(...result.vendor_candidates.map(summaryCard));
    const comparison = byId("result-comparison"); comparison.replaceChildren(comparisonTable(result.vendor_candidates));
    const details = byId("result-details"); details.replaceChildren(...result.vendor_candidates.map(vendorDetails));
    renderEvidence(result);
  }

  function download(name, type, contents) {
    const url = URL.createObjectURL(new Blob([contents], {type}));
    const anchor = document.createElement("a"); anchor.href = url; anchor.download = name; anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 0);
  }

  function csvExport() {
    const rows = [["vendor", "price_case", "status", "product_id", "compute_units", "gpu_count", "rack_count", "it_power_kw", "configuration_cost_jpy", "contingency_jpy", "unused_budget_jpy", "tco_jpy", "gap_ids"]];
    state.latest.vendor_candidates.forEach((candidate) => candidate.cases.forEach((value) => rows.push([
      candidate.vendor, value.price_case, value.status, candidate.product_id || "",
      value.quantities?.compute_units ?? "", value.quantities?.gpu_count ?? "", value.quantities?.rack_count ?? "",
      value.power?.total_kw ?? "", value.costs.configuration_cost_jpy ?? "", value.costs.contingency_jpy ?? "",
      value.costs.unused_budget_jpy ?? "", value.tco.total_tco_jpy ?? "", value.gap_ids.join("|")
    ])));
    return rows.map((row) => row.map((value) => '"' + String(value).replaceAll('"', '""') + '"').join(",")).join("\n");
  }

  function fillPackage(vendor) {
    const key = vendor.toLowerCase();
    const values = {
      unit_type: "rack", gpus_per_unit: 72, host_cpus_per_unit: 36, units_per_rack: 1,
      nodes_per_unit: 18, trays_per_unit: 18, power_kw_per_unit: 400,
      hbm_gib_per_gpu: 288, host_memory_gib_per_unit: 18432, local_nvme_tb_per_unit: 144,
      rack_footprint_m2: 2, rack_weight_kg: 2000, spare_percent: 0, portability_risk_score: vendor === "NVIDIA" ? 0.7 : 0.5
    };
    Object.entries(values).forEach(([field, value]) => { byId(key + "-" + field).value = value; });
    byId(key + "-include-auxiliary-racks").value = "false";
    const network = {endpoint_ports_per_unit: 1, nics_per_unit: 1, switch_ports: 64, max_port_utilization: 1, redundant_switches: 0, max_switch_count: 100, optics_per_endpoint: 1, cables_per_endpoint: 1, blocking_ratio: 1};
    Object.entries(network).forEach(([field, value]) => { byId(key + "-network-" + field).value = value; });
    byId(key + "-network-topology").value = "synthetic nonblocking";
    const storage = {fast_capacity_pb_per_appliance: 10, fast_read_gb_s_per_appliance: 10000, fast_write_gb_s_per_appliance: 10000, metadata_million_inodes_per_appliance: 100, archive_capacity_pb_per_appliance: 100, minimum_controller_count: 2, max_fast_storage_appliances: 100, max_archive_storage_appliances: 100, controllers_per_appliance: 2, appliances_per_rack: 4};
    Object.entries(storage).forEach(([field, value]) => { byId(key + "-storage_capability-" + field).value = value; });
    const services = {login_min_nodes: 2, concurrent_users_per_login_node: 100, management_min_nodes: 3, compute_units_per_management_node: 1000, monitoring_min_nodes: 2, compute_units_per_monitoring_node: 1000, provisioning_min_nodes: 2, compute_units_per_provisioning_node: 1000, scheduler_min_nodes: 2, authentication_min_nodes: 2, nodes_per_rack: 40};
    Object.entries(services).forEach(([field, value]) => { byId(key + "-service_sizing-" + field).value = value; });
    powerFields.forEach(([field]) => { byId(key + "-power_profile-" + field).value = 0; });
    byId(key + "-eligible").value = "true";
    byId(key + "-delivery-date").value = "2027-09-30";
    byId(key + "-support-status").value = "synthetic-test-only";
    const templatePackage = state.source[4].packages.find((item) => item.vendor === vendor);
    templatePackage.cost_lines.forEach((line, index) => {
      const value = line.category === "compute" ? 10 : line.category === "integration" ? 15 : line.category === "maintenance" ? 0.01 : 0;
      PRICE_CASES.forEach((priceCase) => { byId(key + "-cost-" + index + "-" + priceCase).value = value; });
    });
  }

  function loadSyntheticExample() {
    const values = {
      capex: 100, "acceptance-date": "2027-12-31", "vendor-mode": "compare", deployment: "on-premises",
      "tco-years": 5, contingency: 10, "product-nvidia": "GPU-NVIDIA-VERA-RUBIN", "product-amd": "GPU-AMD-MI455X",
      "mix-training": 0, "mix-inference": 0, "mix-hpc": 100, "mix-data": 0,
      utilization: 80, headroom: 10, "annual-gpu-hours": 100000,
      "hpc-jobs": 1000, "hpc-gpus": 8, "hpc-runtime": 2, "concurrent-users": 100,
      "power-mw": 4, "cooling-mw": 4, "cooling-method": "direct-liquid",
      "rack-limit": 20, "floor-area": 1000, "floor-loading": 2500, "rack-density": 500,
      pue: 1.1, "power-redundancy": "N+1", "cooling-redundancy": "N+1",
      "fast-pb": 0, "archive-pb": 0, "read-gbs": 0, "write-gbs": 0,
      "metadata-m": 0, "backup-copies": 0, "retention-years": 1, "rto-hours": 24,
      "local-nvme-required": 0
    };
    Object.entries(values).forEach(([id, value]) => { byId(id).value = value; });
    fillPackage("NVIDIA"); fillPackage("AMD");
    byId("form-error").textContent = text("loadedTest");
    evaluate();
  }

  function importLocal(event) {
    const file = event.target.files[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = () => {
      try {
        const payload = JSON.parse(reader.result);
        if (payload.request) {
          const request = payload.request;
          byId("capex").value = request.budget.capex_ceiling_oku_jpy;
          byId("acceptance-date").value = request.schedule.required_acceptance_date;
          byId("vendor-mode").value = request.vendor_mode;
          byId("deployment").value = request.deployment_mode;
        }
        if (payload.cost_input && payload.cost_input.packages) {
          payload.cost_input.packages.forEach((pkg) => {
            const key = pkg.vendor.toLowerCase();
            byId("product-" + key).value = pkg.product_id;
            byId(key + "-unit_type").value = pkg.unit_type || "";
            byId(key + "-include-auxiliary-racks").value = pkg.include_auxiliary_racks === false ? "false" : "true";
            packageFields.forEach(([field]) => { byId(key + "-" + field).value = pkg[field] ?? ""; });
            networkFields.forEach(([field]) => { byId(key + "-network-" + field).value = pkg.network?.[field] ?? ""; });
            storageFields.forEach(([field]) => { byId(key + "-storage_capability-" + field).value = pkg.storage_capability?.[field] ?? ""; });
            serviceFields.forEach(([field]) => { byId(key + "-service_sizing-" + field).value = pkg.service_sizing?.[field] ?? ""; });
            powerFields.forEach(([field]) => { byId(key + "-power_profile-" + field).value = pkg.power_profile?.[field] ?? ""; });
            const templatePackage = state.source[4].packages.find((item) => item.vendor === pkg.vendor);
            templatePackage.cost_lines.forEach((line, index) => {
              const imported = pkg.cost_lines.find((candidate) => candidate.scope_id === line.scope_id) || pkg.cost_lines[index];
              PRICE_CASES.forEach((priceCase) => { byId(key + "-cost-" + index + "-" + priceCase).value = imported?.[priceCase + "_jpy"] == null ? "" : imported[priceCase + "_jpy"] / 100000000; });
            });
          });
        }
        byId("form-error").textContent = text("importDone");
      } catch (error) {
        byId("form-error").textContent = error.message;
      } finally {
        event.target.value = "";
      }
    };
    reader.readAsText(file);
  }

  function setMode(mode) {
    state.mode = mode;
    renderMode();
    if (mode === "public-evidence") populatePublicInputs();
    evaluate();
  }

  function bind() {
    document.querySelectorAll("[data-language]").forEach((button) => button.addEventListener("click", () => applyLanguage(button.dataset.language)));
    byId("mode-public").addEventListener("click", () => setMode("public-evidence"));
    byId("mode-whatif").addEventListener("click", () => setMode("what-if"));
    byId("planner-form").addEventListener("submit", (event) => { event.preventDefault(); evaluate(); });
    byId("reset-inputs").addEventListener("click", () => { populatePublicInputs(); setMode("public-evidence"); });
    byId("load-test-example").addEventListener("click", loadSyntheticExample);
    byId("import-json").addEventListener("change", importLocal);
    byId("download-json").addEventListener("click", () => {
      if (!state.latest) return;
      download("openfs-gpu-ai4s-candidate.json", "application/json", JSON.stringify({request: state.latestRequest, cost_input: state.latestCost, result: state.latest}, null, 2));
    });
    byId("download-csv").addEventListener("click", () => { if (state.latest) download("openfs-gpu-ai4s-candidate.csv", "text/csv;charset=utf-8", csvExport()); });
  }

  Promise.all(DATA_PATHS.map((path) => fetch("data/" + path).then((response) => {
    if (!response.ok) throw new Error(path + ": HTTP " + response.status);
    return response.json();
  }))).then((values) => {
    state.source = values;
    const requested = new URLSearchParams(location.search).get("lang");
    state.language = requested === "en" ? "en" : "ja";
    renderProductOptions();
    renderDynamicInputLabels();
    populatePublicInputs();
    bind();
    applyLanguage(state.language);
    renderMode();
    evaluate();
  }).catch((error) => {
    byId("result-notice").textContent = "Candidate data could not be loaded: " + error.message;
  });
})();
