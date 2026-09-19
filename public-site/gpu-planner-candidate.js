(() => {
  "use strict";

  const DATA_PATHS = ["request.json", "architecture.json", "product-catalog.json", "availability.json", "what-if-template.json", "planning-estimate.json"];
  const QUARTER_END = {"1": "03-31", "2": "06-30", "3": "09-30", "4": "12-31"};
  const PROCUREMENT_EVENTS = new Set(["procurement-observed", "operation-start"]);
  const FORWARD_EVENTS = new Set(["sampling", "volume-shipment", "sale-publication", "price-observation", "partner-availability", "support-start", "roadmap-target"]);
  const state = {language: "ja", source: null, latest: null, latestRequest: null};

  const copy = {
    analogy: {ja: "類推による計画概算（未検証）", en: "Analogy-based planning estimate (unvalidated)"},
    analogyNote: {ja: "メーカー公表のラック構成と、既存サーバー価格からの類推を組み合わせた感度分析です。Rubinの提示価格・確定見積ではなく、数量範囲も保証値ではありません。", en: "Sensitivity analysis combining manufacturer rack specifications with an analogy to existing server prices. Neither a Rubin asking price nor a firm quote; quantity ranges are not guarantees."},
    reference: {ja: "公開価格付きの参照構成", en: "Reference configuration with a public asking price"},
    referenceNote: {ja: "公開サーバー価格と明示した仮定による概算です。実際の学術向け見積、納期、施設適合を保証しません。", en: "Conceptual estimate using a published server price and explicit assumptions, not an academic quote, delivery guarantee or facility qualification."},
    auto: {ja: "AI提案", en: "AI proposal"},
    allVendors: {ja: "AI提案（公開カタログ全体）", en: "AI proposal (all catalog vendors)"},
    allProducts: {ja: "AI提案（受入時期から選択）", en: "AI proposal (select by acceptance date)"},
    evidenced: {ja: "調達実績を確認できる候補", en: "Procurement-evidenced candidate"},
    forward: {ja: "将来世代を含む先行候補", en: "Forward-looking candidate"},
    evidencedNote: {
      ja: "同系列製品の公開調達または運用実績を確認できます。ただし、入力した受入時期の価格、販売継続、保守、納期を保証するものではありません。",
      en: "Public procurement or operation of the product family has been observed. This does not guarantee price, continued sales, support, or delivery for the selected acceptance date."
    },
    forwardNote: {
      ja: "公式ロードマップまたは公表済み製品計画に基づく候補です。調達可能日、価格、最小構成、納期が未確認の場合は先行候補にとどめます。",
      en: "This candidate is based on an official roadmap or announced product plan. It remains forward-looking when procurement date, price, minimum configuration, or delivery lead time is unconfirmed."
    },
    unavailable: {ja: "算定不能", en: "Unavailable"},
    vendorQuote: {ja: "算定不能 / 要ベンダー見積", en: "Unavailable / vendor quote required"},
    product: {ja: "候補製品・世代", en: "Candidate product or generation"},
    availability: {ja: "調達可能性評価", en: "Procurement availability assessment"},
    timing: {ja: "時期の根拠", en: "Timing evidence"},
    computeUnits: {ja: "計算単位数", en: "Compute units"},
    gpuCount: {ja: "総GPU数", en: "Total GPUs"},
    rackCount: {ja: "ラック数（補助機器を含む）", en: "Rack count including auxiliary equipment"},
    power: {ja: "IT電力", en: "IT power"},
    configCost: {ja: "構成費用", en: "Configuration cost"},
    contingency: {ja: "予備費", en: "Contingency"},
    unused: {ja: "未使用予算", en: "Unused budget"},
    tco: {ja: "5年間TCO", en: "Five-year TCO"},
    optimistic: {ja: "楽観価格", en: "Optimistic price"},
    baseline: {ja: "基準価格", en: "Baseline price"},
    conservative: {ja: "保守価格", en: "Conservative price"},
    blocked: {ja: "算定不能", en: "Unavailable"},
    partial: {ja: "暫定算定", en: "Provisional calculation"},
    feasible: {ja: "制約適合（暫定）", en: "Constraint-feasible (provisional)"},
    unknown: {ja: "未確認", en: "Unknown"},
    conditional: {ja: "条件付き", en: "Conditional"},
    eligible: {ja: "調達可能性を確認", en: "Procurement eligibility observed"},
    ineligible: {ja: "対象外", en: "Ineligible"},
    "not-assessed": {ja: "未評価", en: "Not assessed"},
    "user-assumption": {ja: "利用者仮定", en: "User assumption"},
    noCandidate: {ja: "入力した条件に対応する公開候補はありません。", en: "No public candidate matches the selected conditions."},
    resultNotice: {
      ja: "候補は公開根拠の段階で分けています。調達実績があっても将来の納入を保証せず、ロードマップ上の候補を調達可能とは扱いません。",
      en: "Candidates are separated by evidence stage. Past procurement does not guarantee future delivery, and roadmap candidates are not treated as procurement-ready."
    },
    adjustedNotice: {
      ja: "手動調整を含むブラウザ内の概算です。公開提示価格と計画用仮定を区別し、Rubinの類推価格は未検証と明記します。価格モデルのない製品は算定しません。調達判断には使用できません。",
      en: "This browser-local estimate includes manual adjustments. Public asking prices and planning assumptions are distinguished; Rubin analogy prices are unvalidated. Products without a price model remain uncomputed. Not for procurement."
    },
    requiredEvidence: {ja: "不足している公開根拠", en: "Missing public evidence"},
    priceCases: {ja: "価格区間別の算定", en: "Calculations by price interval"},
    sources: {ja: "公開根拠", en: "Public sources"},
    checked: {ja: "根拠確認日", en: "Evidence checked"},
    lifecycle: {ja: "製品状況", en: "Lifecycle status"},
    procurementProhibited: {ja: "禁止", en: "Prohibited"},
    incomplete: {ja: "未完了", en: "Incomplete"}
  };

  const text = (key) => copy[key]?.[state.language] || key;
  const byId = (id) => document.getElementById(id);
  const clone = (value) => JSON.parse(JSON.stringify(value));
  const element = (name, className, value) => {
    const node = document.createElement(name);
    if (className) node.className = className;
    if (value != null) node.textContent = value;
    return node;
  };
  const inputNumber = (id) => {
    const node = byId(id);
    const value = node ? node.value.trim() : "";
    return value === "" || !Number.isFinite(Number(value)) ? null : Number(value);
  };
  const formatNumber = (value, digits = 0) => value == null
    ? text("unavailable")
    : new Intl.NumberFormat(state.language === "ja" ? "ja-JP" : "en-US", {maximumFractionDigits: digits}).format(value);
  const formatOku = (value) => value == null
    ? text("unavailable")
    : formatNumber(value / 100000000, 2) + (state.language === "ja" ? " 億円" : " x JPY 100m");
  const formatStatus = (value) => copy[value] ? text(value) : value || text("unknown");

  function definitionList(rows) {
    const list = element("dl", "planner-metrics");
    rows.forEach(([term, value]) => {
      const row = element("div");
      row.append(element("dt", null, term), element("dd", null, value));
      list.append(row);
    });
    return list;
  }

  function applyLanguage(language) {
    state.language = language;
    document.documentElement.lang = language;
    document.body.dataset.language = language;
    document.querySelectorAll("[data-ja][data-en]").forEach((node) => {
      node.textContent = node.dataset[language];
    });
    document.querySelectorAll("button[data-language]").forEach((button) => {
      button.setAttribute("aria-pressed", String(button.dataset.language === language));
    });
    document.title = (language === "ja"
      ? "CPU・GPU複合計算基盤 構成算定"
      : "CPU-GPU Accelerated Computing Infrastructure Planner") + " | OpenFS";
    const url = new URL(location.href);
    url.searchParams.set("lang", language);
    history.replaceState(null, "", url);
    renderVendorOptions(false);
    renderProductOptions(false);
    if (state.latest) renderResult(state.latest);
  }

  function acceptanceDate() {
    return byId("acceptance-year").value + "-" + QUARTER_END[byId("acceptance-quarter").value];
  }

  function relevantEvent(product, targetDate, types) {
    return (product.events || [])
      .filter((event) => OpenFSGpuEstimates.dateWindow(event.date).start <= targetDate && types.has(event.event_type))
      .sort((left, right) => right.date.value.localeCompare(left.date.value))[0] || null;
  }

  function observedProcurement(product, targetDate) {
    return (product.events || []).some((event) =>
      event.claim_status === "observed" &&
      PROCUREMENT_EVENTS.has(event.event_type) &&
      OpenFSGpuEstimates.dateWindow(event.date).end <= targetDate
    );
  }

  function forwardEvidence(product, targetDate) {
    return (product.events || []).some((event) =>
      FORWARD_EVENTS.has(event.event_type) &&
      OpenFSGpuEstimates.dateWindow(event.date).start <= targetDate &&
      (event.claim_status === "official-plan" || event.claim_status === "observed")
    );
  }

  function selectedVendors() {
    const selected = byId("accelerator-vendor").value;
    if (selected !== "auto") return [selected];
    return [...new Set(state.source[2].products.map((product) => product.vendor))].sort();
  }

  function selectedProducts() {
    const compatible = (product) => OpenFSGpuEstimates.compatible(product, {cpu_architecture: byId("cpu-mode").value}, state.source[5]);
    const reference = (product) => state.source[5].packages.some(p => p.product_id === product.product_id);
    const analogy = (product) => (state.source[5].rack_analogies || []).some(p => p.product_id === product.product_id);
    const exact = byId("accelerator-product").value;
    if (exact !== "auto") {
      return state.source[2].products.filter((product) => product.product_id === exact)
        .filter(compatible)
        .filter((product) => observedProcurement(product, acceptanceDate()) || forwardEvidence(product, acceptanceDate()))
        .map((product) => ({product, proposal_class: analogy(product) ? "analogy" : reference(product) ? "reference" : observedProcurement(product, acceptanceDate()) ? "evidenced" : "forward"}));
    }
    const target = acceptanceDate();
    const selected = [];
    selectedVendors().forEach((vendor) => {
      const products = state.source[2].products.filter((product) => product.vendor === vendor && compatible(product));
      const choose = (predicate) => products
        .filter((product) => predicate(product, target))
        .sort((left, right) => (right.generation_rank - left.generation_rank) ||
          ((right.events.at(-1)?.date.value || "").localeCompare(left.events.at(-1)?.date.value || "")))[0];
      const priced = choose((product, date) => reference(product) && forwardEvidence(product, date));
      const evidenced = priced ? null : choose(observedProcurement);
      const estimated = choose((product, date) => analogy(product) && forwardEvidence(product, date));
      const forward = choose((product, date) => !reference(product) && !analogy(product) && !observedProcurement(product, date) && forwardEvidence(product, date));
      if (estimated) selected.push({product: estimated, proposal_class: "analogy"});
      if (priced) selected.push({product: priced, proposal_class: "reference"});
      if (evidenced) selected.push({product: evidenced, proposal_class: "evidenced"});
      if (forward) selected.push({product: forward, proposal_class: "forward"});
    });
    return selected.sort((left, right) => {
      const classOrder = {analogy: 0, reference: 1, evidenced: 2, forward: 3};
      return classOrder[left.proposal_class] - classOrder[right.proposal_class] ||
        left.product.vendor.localeCompare(right.product.vendor);
    });
  }

  function renderYearOptions() {
    const select = byId("acceptance-year");
    for (let year = 2026; year <= 2032; year += 1) {
      const option = element("option", null, String(year));
      option.value = String(year);
      select.append(option);
    }
  }

  function renderVendorOptions(preserve = true) {
    if (!state.source) return;
    const select = byId("accelerator-vendor");
    const previous = preserve ? select.value : (select.value || "auto");
    const options = [{value: "auto", label: text("allVendors")}];
    [...new Set(state.source[2].products.map((product) => product.vendor))].sort()
      .forEach((vendor) => options.push({value: vendor, label: vendor}));
    select.replaceChildren(...options.map(({value, label}) => {
      const option = element("option", null, label);
      option.value = value;
      return option;
    }));
    select.value = options.some((item) => item.value === previous) ? previous : "auto";
  }

  function renderProductOptions(preserve = true) {
    if (!state.source) return;
    const select = byId("accelerator-product");
    const previous = preserve ? select.value : (select.value || "auto");
    const vendors = selectedVendors();
    const options = [{value: "auto", label: text("allProducts")}];
    state.source[2].products
      .filter((product) => vendors.includes(product.vendor))
      .sort((left, right) => left.vendor.localeCompare(right.vendor) || right.generation_rank - left.generation_rank)
      .forEach((product) => options.push({value: product.product_id, label: product.vendor + " " + product.model}));
    select.replaceChildren(...options.map(({value, label}) => {
      const option = element("option", null, label);
      option.value = value;
      return option;
    }));
    select.value = options.some((item) => item.value === previous) ? previous : "auto";
  }

  function buildRequest() {
    const request = clone(state.source[0]);
    const target = acceptanceDate();
    request.budget.capex_ceiling_oku_jpy = inputNumber("capex");
    request.schedule.acceptance_year = Number(byId("acceptance-year").value);
    request.schedule.required_acceptance_date = target;
    request.deployment_mode = byId("deployment").value;
    request.vendor_mode = "auto-pareto";
    request.product_selection = {nvidia: "auto", amd: "auto"};
    request.basic_preferences = {
      cpu_architecture: byId("cpu-mode").value,
      accelerator_vendor: byId("accelerator-vendor").value,
      accelerator_product: byId("accelerator-product").value,
      scale_out_fabric: byId("network-mode").value
    };
    request.estimate_assumptions = {
      fx_jpy_per_usd: inputNumber("estimate-fx"),
      baseline_annual_change: inputNumber("estimate-annual") / 100,
      storage_tb_per_node: inputNumber("estimate-storage-ratio"),
      storage_block_jpy: inputNumber("estimate-storage-cost") * 10000
    };
    const computeUnits = inputNumber("override-compute-units");
    const fastStorage = inputNumber("override-fast-pb");
    const localNvme = inputNumber("override-local-nvme");
    request.manual_overrides = {
      compute_units: computeUnits,
      shared_fast_capacity_pb: fastStorage,
      local_nvme_tb_per_compute_unit: localNvme
    };
    if (fastStorage != null) request.storage.shared_fast_capacity_pb = fastStorage;
    if (localNvme != null) request.storage.local_nvme_tb_per_compute_unit = localNvme;
    request.run_mode = [computeUnits, fastStorage, localNvme].some((value) => value != null)
      ? "what-if"
      : "public-evidence";
    return request;
  }

  function evaluateProduct(baseRequest, selection) {
    const request = clone(baseRequest);
    const product = selection.product;
    request.vendor_mode = product.vendor;
    request.product_selection[product.vendor.toLowerCase()] = product.product_id;
    const candidate = OpenFSGpuEstimates.evaluate(request, product, state.source[5], state.source[1]);
    candidate.availability_status = state.source[3].assessments.find(a => a.product_id === product.product_id)?.availability_status || "unknown";
    candidate.proposal_class = selection.proposal_class;
    candidate.track_note_ja = copy[selection.proposal_class + "Note"].ja;
    candidate.track_note_en = copy[selection.proposal_class + "Note"].en;
    return candidate;
  }

  function calculate() {
    try {
      byId("form-error").textContent = "";
      for (const id of ["estimate-fx", "estimate-annual", "estimate-storage-ratio", "estimate-storage-cost"]) {
        if (inputNumber(id) == null) throw new Error(state.language === "ja" ? "概算の仮定に数値を入力してください。" : "Enter numeric values for the estimate assumptions.");
      }
      const request = buildRequest();
      if (request.budget.capex_ceiling_oku_jpy == null || request.budget.capex_ceiling_oku_jpy <= 0) {
        throw new Error(state.language === "ja" ? "初期整備費上限を入力してください。" : "Enter a positive initial CAPEX ceiling.");
      }
      const selections = selectedProducts();
      const candidates = selections.map((selection) => evaluateProduct(request, selection));
      state.latestRequest = request;
      state.latest = {
        schema_version: "0.3.0",
        result_id: "CFGRESULT-CPU-GPU-ACCEL-BROWSER",
        status: candidates.length && candidates.some((candidate) => candidate.status !== "blocked") ? "partial" : "blocked",
        research_status: "provisional",
        consensus_status: "incomplete",
        procurement_use: "prohibited",
        calculation_mode: request.run_mode,
        request_id: request.request_id,
        architecture_id: request.architecture_id,
        product_catalog_id: state.source[2].catalog_id,
        availability_assessment_id: state.source[3].assessment_id,
        generated_at: new Date().toISOString(),
        engine_version: OpenFSGpuEstimates.ENGINE_VERSION,
        estimate_model_id: state.source[5].model_id,
        estimate_model_as_of: state.source[5].as_of,
        vendor_candidates: candidates,
        benchmark_candidates: OpenFSGpuPlanner.BENCHMARKS
      };
      renderResult(state.latest);
    } catch (error) {
      state.latest = null;
      state.latestRequest = null;
      ["result-summary", "result-comparison", "result-details", "evidence-status", "product-evidence", "gap-list", "benchmark-list", "result-notice", "result-fx"].forEach(id => byId(id)?.replaceChildren());
      byId("form-error").textContent = error.message;
    }
  }

  function baselineCase(candidate) {
    return candidate.cases.find((item) => item.price_case === "baseline") || candidate.cases[0];
  }

  function quantityRange(candidate, key) {
    const values = candidate.cases.map(c => c.quantities?.[key]).filter(Number.isFinite);
    if (!values.length) return text("unavailable");
    const min = Math.min(...values), max = Math.max(...values);
    const base = baselineCase(candidate).quantities?.[key];
    const range = min === max ? formatNumber(min) : formatNumber(min) + " ~ " + formatNumber(max);
    return range + (base == null ? "" : (state.language === "ja" ? "（基準 " : " (baseline ") + formatNumber(base) + (state.language === "ja" ? "）" : ")"));
  }

  function unitLabel(candidate) {
    return candidate.price_analogy
      ? (state.language === "ja" ? "計算トレイ数（4 GPU/トレイ）" : "Compute trays (4 GPUs/tray)")
      : (state.language === "ja" ? "計算ノード数" : "Compute nodes");
  }

  function failureLabel(reason) {
    const labels = {
      "assumed-lead-time-exceeds-acceptance": ["仮定した納期では受入四半期に間に合いません。", "Assumed lead time exceeds the acceptance quarter."],
      "whole-rack-purchase-required": ["18トレイ単位のラック構成を指定してください。", "Use complete racks in increments of 18 trays."],
      "absolute-demand-exceeds-budget-or-manual-lock": ["需要を満たす規模が予算または手動指定と両立しません。", "Demand is incompatible with the budget or manual locks."],
      "budget-facility-drive-bay-or-manual-lock-conflict": ["予算・設備・ドライブ数・手動指定のいずれかが制約を超えています。", "Budget, facility, drive bays or manual locks prevent this configuration."]
    };
    return labels[reason]?.[state.language === "ja" ? 0 : 1] || text("vendorQuote");
  }

  function eventLabel(product) {
    const target = acceptanceDate();
    const types = product && observedProcurement(product, target) ? PROCUREMENT_EVENTS : FORWARD_EVENTS;
    const event = product ? relevantEvent(product, target, types) : null;
    if (!event) return text("unknown");
    const labels = {
      announcement: ["発表", "Announcement"], sampling: ["サンプル出荷", "Sampling"],
      "volume-shipment": ["量産出荷", "Volume shipment"], "sale-publication": ["販売の公表", "Sale publication"],
      "price-observation": ["公開価格の確認", "Public price checked"],
      "partner-availability": ["パートナー経由の提供", "Partner availability"],
      "procurement-observed": ["調達実績", "Observed procurement"],
      "support-start": ["サポート開始", "Support start"], "operation-start": ["運用開始", "Operation start"],
      "roadmap-target": ["ロードマップ上の目標", "Roadmap target"], "end-of-support": ["サポート終了", "End of support"]
    };
    const statuses = {observed: ["公開情報で確認", "Publicly documented"],
      "official-plan": ["公表計画", "Announced plan"], "provisional-outlook": ["暫定見通し", "Provisional outlook"]};
    const {value, precision} = event.date, year = value.slice(0, 4), month = Number(value.slice(5, 7));
    const date = precision === "year" ? year : precision === "month" ? value.slice(0, 7)
      : precision === "quarter" ? year + " Q" + Math.ceil(month / 3)
      : precision === "half-year" ? year + " H" + Math.ceil(month / 6) : value;
    const language = state.language === "ja" ? 0 : 1;
    return (labels[event.event_type]?.[language] || event.event_type) + " / " + date
      + " (" + (statuses[event.claim_status]?.[language] || event.claim_status) + ")";
  }

  function summaryCard(candidate) {
    const value = baselineCase(candidate);
    const quantities = value?.quantities || {};
    const product = state.source[2].products.find((item) => item.product_id === candidate.product_id);
    const card = element("article", "planner-result planner-track-" + candidate.proposal_class);
    const track = element("span", "eyebrow", text(candidate.proposal_class));
    const head = element("div", "planner-result-head");
    head.append(element("h3", null, candidate.vendor + " " + (candidate.product_name || "")), element("span", "status-badge status-" + candidate.status, formatStatus(candidate.status)));
    card.append(track, head, element("p", "planner-track-note", state.language === "ja" ? candidate.track_note_ja : candidate.track_note_en));
    card.append(definitionList([
      [text("timing"), eventLabel(product)],
      [text("availability"), formatStatus(candidate.availability_status)],
      [unitLabel(candidate), quantityRange(candidate, "compute_units")],
      [text("gpuCount"), quantityRange(candidate, "gpu_count")],
      [state.language === "ja" ? "計算ラック数" : "Compute racks", candidate.cases.some(c => c.quantities) ? (() => {
        const values = candidate.cases.filter(c => c.quantities).map(c => c.quantities.physical_bom.compute_racks);
        return formatNumber(Math.min(...values)) + " ~ " + formatNumber(Math.max(...values));
      })() : text("unavailable")],
      [text("rackCount"), quantityRange(candidate, "rack_count")],
      [text("power"), value?.power ? formatNumber(value.power.total_kw, 1) + " kW" : text("unavailable")],
      [text("configCost"), formatOku(value?.costs.configuration_cost_jpy)],
      [text("tco"), formatOku(value?.tco.total_tco_jpy)]
    ]));
    if (!value || value.status === "blocked") card.append(element("p", "planner-blocking", failureLabel(value?.reason)));
    card.append(element("p", "planner-track-note", state.language === "ja"
      ? "範囲は算定できた価格ケースの最小〜最大です。下記に3ケースの内訳と成立しない条件を示します。"
      : "Ranges cover calculated price cases only. All three cases and any unmet conditions are shown below."));
    if (value?.tco.capex_plus_energy_jpy != null) card.append(element("p", null,
      (state.language === "ja" ? "部分集計：CAPEX＋5年間の電力量料金 " : "Partial subtotal: CAPEX + five-year energy charges ") + formatOku(value.tco.capex_plus_energy_jpy)));
    return card;
  }

  function comparisonTable(candidates) {
    if (!candidates.length) return element("p", "planner-blocking", text("noCandidate"));
    const table = element("table", "planner-comparison-table");
    const head = element("thead");
    const heading = element("tr");
    heading.append(element("th", null, state.language === "ja" ? "項目" : "Item"));
    candidates.forEach((candidate) => heading.append(element("th", null,
      text(candidate.proposal_class) + " / " + candidate.vendor)));
    head.append(heading);
    const rows = [
      [text("product"), (candidate) => candidate.product_name || text("unavailable")],
      [text("availability"), (candidate) => formatStatus(candidate.availability_status)],
      [text("computeUnits"), (candidate) => unitLabel(candidate) + ": " + quantityRange(candidate, "compute_units")],
      [text("gpuCount"), (candidate) => quantityRange(candidate, "gpu_count")],
      [text("rackCount"), (candidate) => quantityRange(candidate, "rack_count")],
      [text("configCost"), (candidate) => formatOku(baselineCase(candidate).costs.configuration_cost_jpy)],
      [text("contingency"), (candidate) => formatOku(baselineCase(candidate).costs.contingency_jpy)],
      [text("unused"), (candidate) => formatOku(baselineCase(candidate).costs.unused_budget_jpy)]
    ];
    const body = element("tbody");
    rows.forEach(([label, getter]) => {
      const row = element("tr");
      row.append(element("th", null, label));
      candidates.forEach((candidate) => row.append(element("td", null, getter(candidate))));
      body.append(row);
    });
    table.append(head, body);
    return table;
  }

  function candidateDetails(candidate) {
    const article = element("article", "planner-vendor-result");
    article.append(element("h3", null, text(candidate.proposal_class) + ": " + candidate.vendor + " " + (candidate.product_name || "")));
    const details = element("details");
    details.open = true;
    details.append(element("summary", null, text("priceCases")));
    const wrap = element("div", "table-wrap");
    const table = element("table", "planner-price-case-table");
    const head = element("thead");
    const hr = element("tr");
    [text("priceCases"), text("availability"), unitLabel(candidate), "GPU", text("rackCount"), text("configCost"), "TCO"].forEach((label) => hr.append(element("th", null, label)));
    head.append(hr);
    const body = element("tbody");
    candidate.cases.forEach((value) => {
      const row = element("tr");
      row.append(
        element("th", null, formatStatus(value.price_case)),
        element("td", null, formatStatus(value.status)),
        element("td", null, formatNumber(value.quantities?.compute_units)),
        element("td", null, formatNumber(value.quantities?.gpu_count)),
        element("td", null, formatNumber(value.quantities?.rack_count)),
        element("td", null, formatOku(value.costs.configuration_cost_jpy)),
        element("td", null, formatOku(value.tco.total_tco_jpy))
      );
      body.append(row);
      if (value.status === "blocked") {
        const reason = element("tr"), cell = element("td", "planner-blocking", failureLabel(value.reason));
        cell.colSpan = 7; reason.append(cell); body.append(reason);
      }
    });
    table.append(head, body);
    wrap.append(table);
    details.append(wrap);
    article.append(details);
    if (candidate.price_analogy) {
      const a = candidate.price_analogy;
      const basis = element("details");
      basis.append(element("summary", null, state.language === "ja" ? "Rubinの価格範囲・納期仮定の計算根拠" : "Rubin price-range and lead-time assumptions"));
      basis.append(element("p", null, a["explanation_" + state.language]));
      const anchor = state.source[5].packages.find(p => p.package_id === a.anchor_package_id);
      basis.append(element("p", null, state.language === "ja"
        ? "ラック価格の基準：USD " + formatNumber(anchor.price_usd, 2) + " × " + a.anchor_packages_per_rack + " × 倍率 " + Object.values(a.rack_price_multiplier).join(" / ") + "。年率・為替・税は別途適用。"
        : "Rack-price anchor: USD " + formatNumber(anchor.price_usd, 2) + " × " + a.anchor_packages_per_rack + " × multipliers " + Object.values(a.rack_price_multiplier).join(" / ") + ". Annual sensitivity, FX and tax are applied separately."));
      basis.append(element("p", null, (state.language === "ja" ? "納期は価格基準日から4/6/9か月と仮定。正式発注・施設準備・検収に要する期間は未確認です。価格・納期は要ベンダー見積。基準日：" : "Assume 4/6/9 months from the price-basis date. Formal ordering, facility preparation and acceptance duration are unconfirmed. Vendor price/delivery quotes required. Basis date: ") + a.price_basis_date));
      basis.append(sourceList(a.source_ids)); article.append(basis);
    }
    const base = baselineCase(candidate);
    if (base.quantities) {
      const q = base.quantities;
      article.append(definitionList([
        [state.language === "ja" ? "ホストCPU" : "Host CPUs", q.cpu_model + " × " + q.host_cpu_count],
        ["HBM (GB)", formatNumber(q.hbm_capacity_gb)],
        [state.language === "ja" ? "ホストメモリ (GB)" : "Host memory (GB)", formatNumber(q.host_memory_gb)],
        ["NVMe (TB)", formatNumber(q.local_nvme_tb, 2)],
        [state.language === "ja" ? "高速共有ストレージ (PB)" : "Fast shared storage (PB)", formatNumber(q.shared_fast_capacity_pb, 2)],
        [state.language === "ja" ? "スケールアウト接続" : "Scale-out fabric", q.fabric]
      ]));
      const bom = element("details");
      bom.append(element("summary", null, state.language === "ja" ? "費用内訳・算定根拠" : "Cost breakdown and calculation basis"));
      bom.append(element("p", null, candidate["package_scope_" + state.language]));
      const table = element("table");
      const heading = element("tr");
      (state.language === "ja" ? ["費用範囲", "数量", "単価（円）", "合計（円）", "根拠の区分"] : ["Cost scope", "Quantity", "Unit price (JPY)", "Total (JPY)", "Evidence class"])
        .forEach(v => heading.append(element("th", null, v)));
      table.append(heading);
      const labels = {
        "compute-package": ["計算パッケージ（ノード／トレイ）", "Compute package (node/tray)"],
        "local-nvme-additions": ["追加NVMe", "Additional NVMe"],
        "scale-out-fabric": ["NIC・スイッチ・配線", "NICs, switches and cabling"],
        "shared-storage-100TB": ["有効容量100 TB単位の共有ストレージ", "Shared storage per 100 TB usable"],
        "management-and-installation": ["管理基盤・導入", "Management and installation"],
        "racks-and-facility": ["ラック・施設", "Racks and facility"]
      };
      base.costs.line_items.forEach(line => {
        const row = element("tr");
        [labels[line.component_id][state.language === "ja" ? 0 : 1], line.quantity, formatNumber(line.unit_price_jpy), formatNumber(line.total_jpy),
          line.evidence_status === "planning-assumption" ? (state.language === "ja" ? "計画用仮定" : "Planning assumption") : (state.language === "ja" ? "公開提示価格を換算" : "Converted public asking price")]
          .forEach(v => row.append(element("td", null, v)));
        table.append(row);
      });
      const scroll = element("div", "table-wrap"); scroll.append(table); bom.append(scroll);
      bom.append(element("p", null, (state.language === "ja" ? "換算式：提示価格 × 為替 × 価格係数 × (1＋年率)^経過年数 × (1＋税率)。構成費用＋予備費＋未使用予算＝予算上限。基準日の価格を固定した基準ケースでは、年だけを変えてもGPU数が変わらない場合があります。" : "Conversion: asking price × FX × price factor × (1 + annual change)^elapsed years × (1 + tax rate). Configuration + contingency + unused budget = ceiling. GPU counts can stay unchanged across years in the constant-price baseline.")));
      bom.append(sourceList(candidate.source_ids)); article.append(bom);
      if (q.physical_bom) {
        const physical = element("details");
        physical.append(element("summary", null, state.language === "ja" ? "参照BOMの数量と制約" : "Reference BOM quantities and constraints"));
        physical.append(element("p", null, state.language === "ja"
          ? "数量は計画用仮定です。NIC・スイッチ・配線はネットワーク費、コントローラーはストレージ費、管理サーバーは管理基盤費に含め、再加算しません。接続部品・保守・障害時動作は未検証です。"
          : "Quantities are planning assumptions. Network devices are covered by the fabric allowance, controllers by storage, and service nodes by management; they are not added again. Components, support and failure behavior remain unqualified."));
        const labels = {
          compute_nic_ports: ["計算網NICポート", "Compute NIC ports"],
          compute_leaf_switches: ["計算網Leafスイッチ", "Compute leaf switches"],
          compute_spine_switches: ["計算網Spineスイッチ", "Compute spine switches"],
          compute_fabric_cables: ["計算網ケーブル", "Compute fabric cables"],
          compute_fabric_optics: ["計算網光モジュール（両端）", "Compute optics (both ends)"],
          converged_access_switches: ["収束網アクセススイッチ", "Converged access switches"],
          oob_access_switches: ["管理網アクセススイッチ", "OOB access switches"],
          login_nodes: ["ログインノード", "Login nodes"], management_nodes: ["管理・監視・プロビジョニング", "Management, monitoring and provisioning"],
          scheduler_nodes: ["スケジューラ", "Scheduler nodes"], authentication_nodes: ["認証", "Authentication nodes"],
          storage_controllers: ["内蔵ストレージコントローラー", "Bundled storage controllers"],
          compute_racks: ["計算ラック", "Compute racks"], storage_racks: ["ストレージラック", "Storage racks"],
          service_racks: ["サービスラック", "Service racks"], network_racks: ["ネットワークラック", "Network racks"],
          floor_area_m2: ["通路込み面積（m²・仮定）", "Area including aisles (m², assumed)"]
        };
        physical.append(definitionList(Object.entries(labels).map(([key, names]) =>
          [names[state.language === "ja" ? 0 : 1], formatNumber(q.physical_bom[key], 1)])));
        article.append(physical);
      }
      const tco = element("details");
      tco.append(element("summary", null, state.language === "ja" ? "電力・複数年費用の範囲" : "Power and multi-year cost scope"));
      tco.append(definitionList([
        [state.language === "ja" ? "計算機電力 (kW)" : "Compute power (kW)", formatNumber(base.power.compute_kw, 1)],
        [state.language === "ja" ? "補助機器電力 (kW・仮定)" : "Auxiliary power (kW, assumed)", formatNumber(base.power.auxiliary_kw, 1)],
        ["PUE", formatNumber(base.tco.pue, 2)],
        [state.language === "ja" ? "年間電力量料金（仮定）" : "Annual energy charges (assumed)", formatOku(base.tco.annual_energy_jpy)]
      ]));
      tco.append(element("p", null, state.language === "ja"
        ? "総IT電力には仮定の余裕率を加えます。電力量料金は一定負荷・一定単価の感度計算です。基本料金、人件費、保守、ホスティング、大規模施設改修、撤去費は未確認で、年間OPEXと完全TCOは算出しません。外部ホスティングの電力込み料金との二重加算も行いません。"
        : "Total IT power adds an assumed margin. Energy charges use constant-load/constant-price sensitivity assumptions. Demand charges, staffing, support, hosting, major facility works and decommissioning are unknown, so annual OPEX and full TCO remain uncomputed. An energy-inclusive hosting quote must not be added again."));
      article.append(tco);
    }
    const software = candidate.software_profile;
    if (candidate.demand_requirements) {
      const demand = candidate.demand_requirements;
      article.append(definitionList([
        [(state.language === "ja" ? "絶対需要による下限：" : "Absolute-demand minimum: ") + unitLabel(candidate), formatNumber(demand.minimum_compute_units)],
        [state.language === "ja" ? "チェックポイント帯域要件 (GB/s)" : "Required checkpoint bandwidth (GB/s)", formatNumber(demand.checkpoint_write_gb_s)],
        [state.language === "ja" ? "需要・性能適合" : "Demand/performance qualification", state.language === "ja" ? "帯域・推論SLO・アプリ性能は未検証" : "Bandwidth, inference SLOs and application performance unverified"]
      ]));
    }
    if (software) article.append(definitionList([
      [state.language === "ja" ? "計算スタック" : "Compute stack", software.compute_stack.join(", ")],
      [state.language === "ja" ? "通信スタック" : "Communication stack", software.communication_stack.join(", ")],
      [state.language === "ja" ? "ソフトウェア" : "Software", software.software_stack.join(", ")],
      [state.language === "ja" ? "構成別の対応版・移植工数・支援費" : "Configuration-specific versions, porting effort and support cost",
        state.language === "ja" ? "未検証・要見積（上記は参照スタック）" : "Unverified; quote required (reference stacks above)"]
    ]));
    return article;
  }

  function publicSourceIndex() {
    const index = new Map();
    const seen = new Set();
    const visit = (value) => {
      if (!value || typeof value !== "object" || seen.has(value)) return;
      seen.add(value);
      if (value.source_id && value.url) index.set(value.source_id, value);
      Object.values(value).forEach(visit);
    };
    visit(window.OPENFS_PUBLIC_DATA);
    visit(state.source[5]);
    return index;
  }

  function sourceList(sourceIds) {
    const list = element("ul", "source-list planner-source-list");
    const index = publicSourceIndex();
    [...new Set(sourceIds || [])].forEach((sourceId) => {
      const item = element("li");
      const source = index.get(sourceId);
      if (source && /^https:\/\//.test(source.url)) {
        const link = element("a", null, source.title || sourceId);
        link.href = source.url;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        item.append(link, element("span", "mono-list", sourceId));
      } else {
        item.append(element("span", "mono-list", sourceId));
      }
      list.append(item);
    });
    if (!list.childElementCount) list.append(element("li", null, text("unknown")));
    return list;
  }

  function renderEvidence(result) {
    const status = byId("evidence-status");
    status.replaceChildren(definitionList([
      [state.language === "ja" ? "製品カタログ基準日" : "Product catalog as of", state.source[2].as_of],
      [state.language === "ja" ? "調達評価基準日" : "Procurement assessment as of", state.source[3].as_of],
      [state.language === "ja" ? "調達利用" : "Procurement use", text("procurementProhibited")],
      ["Consensus Gate", text("incomplete")],
      [state.language === "ja" ? "独立した価格検証事例" : "Independent price-validation cases", formatNumber(state.source[5].validation.held_out_cases)],
      [state.language === "ja" ? "価格予測誤差 (%)" : "Price prediction error (%)", formatNumber(state.source[5].validation.error_percent)],
      [state.language === "ja" ? "処理場所" : "Processing location", state.language === "ja" ? "ブラウザ内のみ" : "Browser only"]
    ]));

    const assessments = new Map(state.source[3].assessments.map((item) => [item.product_id, item]));
    const details = element("details");
    details.append(element("summary", null, state.language === "ja" ? "製品カタログと調達可能性評価" : "Product catalog and procurement availability"));
    const wrap = element("div", "table-wrap");
    const table = element("table", "planner-evidence-table");
    const head = element("thead");
    const hr = element("tr");
    [text("product"), text("lifecycle"), text("availability"), text("checked"), text("sources")].forEach((label) => hr.append(element("th", null, label)));
    head.append(hr);
    const body = element("tbody");
    state.source[2].products.forEach((product) => {
      const assessment = assessments.get(product.product_id);
      const row = element("tr");
      const sources = element("td");
      sources.append(sourceList([...(product.source_ids || []), ...(assessment?.source_ids || [])]));
      row.append(
        element("th", null, product.vendor + " " + product.model),
        element("td", null, product.lifecycle_status),
        element("td", null, formatStatus(assessment?.availability_status)),
        element("td", null, assessment?.evidence_checked_date || product.evidence_checked_date || text("unknown")),
        sources
      );
      body.append(row);
    });
    table.append(head, body);
    wrap.append(table);
    details.append(wrap);
    byId("product-evidence").replaceChildren(details);
    const model = state.source[5];
    byId("product-evidence").append(element("p", null, model["method_" + state.language]), element("p", null,
      (state.language === "ja" ? "モデル初期値（現在の入力とは異なる場合があります）：" : "Model defaults (may differ from current inputs): ") + model["assumptions_" + state.language]));
    const exclusions = element("ul");
    model["excluded_costs_" + state.language].forEach(v => exclusions.append(element("li", null, v)));
    byId("product-evidence").append(exclusions);
    const references = element("details");
    references.append(element("summary", null, state.language === "ja" ? "構成比率の参照システム" : "Reference systems for component ratios"));
    model.reference_systems.forEach(r => {
      references.append(element("p", null, r.name + ": " + r.nodes + " nodes; " + r.cpus_per_node + " CPU / " + r.gpus_per_node + " GPU per node. " + r["use_" + state.language]), sourceList(r.source_ids));
    });
    byId("product-evidence").append(references);
    const assumptions = element("details");
    assumptions.append(element("summary", null, state.language === "ja" ? "全計算係数（計画用仮定）" : "All calculation coefficients (planning assumptions)"));
    assumptions.append(element("pre", "planner-coefficients", JSON.stringify(result.vendor_candidates.find(c => c.assumptions)?.assumptions || model.defaults, null, 2)));
    byId("product-evidence").append(assumptions);

    const gaps = new Map();
    result.vendor_candidates.forEach((candidate) => {
      candidate.gaps.forEach((gap) => gaps.set(gap.gap_id + "/" + gap.scope, gap));
    });
    const root = byId("gap-list");
    root.replaceChildren();
    if (!gaps.size) root.append(element("p", null, state.language === "ja" ? "表示対象のCoverage Gapはありません。" : "No Coverage Gaps are reported for the displayed candidates."));
    gaps.forEach((gap) => {
      const item = element("article", "planner-gap");
      item.append(
        element("strong", null, gap.gap_id + " / " + gap.scope),
        element("p", null, state.language === "ja" ? gap.statement_ja : gap.statement_en),
        element("p", "mono-list", (gap.missing_items || []).join(", "))
      );
      root.append(item);
    });
    byId("benchmark-list").textContent = result.benchmark_candidates.join(" · ");
  }

  function renderResult(result) {
    byId("result-notice").textContent = result.calculation_mode === "what-if"
      ? text("adjustedNotice")
      : text("resultNotice");
    const fx = state.latestRequest.estimate_assumptions.fx_jpy_per_usd;
    const changeFx = element("a", null, state.language === "ja" ? "為替を変更" : "Change FX assumption");
    changeFx.href = "#estimate-assumptions";
    changeFx.addEventListener("click", () => { byId("estimate-assumptions").open = true; });
    byId("result-fx").replaceChildren(element("strong", null,
      state.language === "ja" ? "円換算の仮定：1 USD = " + fx + " 円。" : "Assumed exchange rate: 1 USD = JPY " + fx + ". "),
      element("span", null, state.language === "ja"
        ? "全価格ケース共通。USD建て費目に適用し、円建て費目は再換算しません。市場レートの自動取得は行いません。 "
        : "Shared by all price cases. Applies to USD-denominated items; JPY items are not reconverted. No live market-rate feed. "), changeFx);
    const summary = byId("result-summary");
    summary.replaceChildren();
    if (!result.vendor_candidates.length) summary.append(element("p", "planner-blocking", text("noCandidate")));
    else result.vendor_candidates.forEach((candidate) => summary.append(summaryCard(candidate)));
    byId("result-comparison").replaceChildren(comparisonTable(result.vendor_candidates));
    byId("result-details").replaceChildren(...result.vendor_candidates.map(candidateDetails));
    renderEvidence(result);
  }

  function csvExport() {
    const rows = [["proposal_class", "vendor", "product_id", "price_case", "status", "compute_units", "gpu_count", "rack_count", "configuration_cost_jpy", "contingency_jpy", "unused_budget_jpy", "tco_jpy", "gap_ids", "compute_unit_type", "procurement_unit_type", "procurement_units", "reason", "fx_jpy_per_usd"]];
    state.latest.vendor_candidates.forEach((candidate) => candidate.cases.forEach((value) => rows.push([
      candidate.proposal_class,
      candidate.vendor,
      candidate.product_id || "",
      value.price_case,
      value.status,
      value.quantities?.compute_units ?? "",
      value.quantities?.gpu_count ?? "",
      value.quantities?.rack_count ?? "",
      value.costs.configuration_cost_jpy ?? "",
      value.costs.contingency_jpy ?? "",
      value.costs.unused_budget_jpy ?? "",
      value.tco.total_tco_jpy ?? "",
      value.gap_ids.join("|"),
      value.quantities?.compute_unit_type ?? "",
      value.quantities?.procurement_unit_type ?? "",
      value.quantities?.procurement_units ?? "",
      value.reason || "",
      state.latestRequest.estimate_assumptions.fx_jpy_per_usd
    ])));
    return rows.map((row) => row.map((value) => '"' + String(value).replaceAll('"', '""') + '"').join(",")).join("\n");
  }

  function download(name, type, contents) {
    const url = URL.createObjectURL(new Blob([contents], {type}));
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = name;
    anchor.click();
    setTimeout(() => URL.revokeObjectURL(url), 0);
  }

  function reset() {
    byId("capex").value = state.source[0].budget.capex_ceiling_oku_jpy;
    byId("acceptance-year").value = state.source[0].schedule.acceptance_year;
    byId("acceptance-quarter").value = String(Math.ceil(Number(state.source[0].schedule.required_acceptance_date.slice(5, 7)) / 3));
    byId("cpu-mode").value = "auto";
    byId("accelerator-vendor").value = "auto";
    renderProductOptions(false);
    byId("accelerator-product").value = "auto";
    byId("network-mode").value = "auto";
    byId("deployment").value = state.source[0].deployment_mode;
    byId("estimate-fx").value = state.source[5].defaults.fx_jpy_per_usd;
    byId("estimate-annual").value = state.source[5].defaults.annual_change.baseline * 100;
    byId("estimate-storage-ratio").value = state.source[5].defaults.storage_tb_per_node;
    byId("estimate-storage-cost").value = state.source[5].defaults.storage_block_jpy / 10000;
    ["override-compute-units", "override-fast-pb", "override-local-nvme"].forEach((id) => { byId(id).value = ""; });
    calculate();
  }

  function bind() {
    document.querySelectorAll("button[data-language]").forEach((button) => button.addEventListener("click", () => applyLanguage(button.dataset.language)));
    byId("accelerator-vendor").addEventListener("change", () => renderProductOptions(false));
    let timer;
    document.querySelectorAll("#planner-form input, #planner-form select, #manual-adjustments input, #estimate-assumptions input").forEach(input => {
      input.addEventListener("change", calculate);
      input.addEventListener("input", () => { clearTimeout(timer); timer = setTimeout(calculate, 250); });
    });
    byId("planner-form").addEventListener("submit", (event) => {
      event.preventDefault();
      calculate();
    });
    byId("reset-inputs").addEventListener("click", reset);
    byId("recalculate").addEventListener("click", calculate);
    byId("clear-overrides").addEventListener("click", () => {
      ["override-compute-units", "override-fast-pb", "override-local-nvme"].forEach((id) => { byId(id).value = ""; });
      calculate();
    });
    byId("download-json").addEventListener("click", () => {
      if (state.latest) download("openfs-cpu-gpu-planner-candidate.json", "application/json", JSON.stringify({request: state.latestRequest, result: state.latest}, null, 2));
    });
    byId("download-csv").addEventListener("click", () => {
      if (state.latest) download("openfs-cpu-gpu-planner-candidate.csv", "text/csv;charset=utf-8", csvExport());
    });
  }

  Promise.all(DATA_PATHS.map((path) => fetch("data/" + path).then((response) => {
    if (!response.ok) throw new Error(path + ": HTTP " + response.status);
    return response.json();
  }))).then((values) => {
    state.source = values;
    const requested = new URLSearchParams(location.search).get("lang");
    state.language = requested === "en" ? "en" : "ja";
    renderYearOptions();
    renderVendorOptions(false);
    renderProductOptions(false);
    bind();
    reset();
    applyLanguage(state.language);
  }).catch((error) => {
    byId("result-notice").textContent = "Candidate data could not be loaded: " + error.message;
  });
})();
