(() => {
  "use strict";

  const DATA_PATHS = ["request.json", "architecture.json", "product-catalog.json", "availability.json", "what-if-template.json"];
  const QUARTER_END = {"1": "03-31", "2": "06-30", "3": "09-30", "4": "12-31"};
  const PROCUREMENT_EVENTS = new Set(["procurement-observed", "operation-start"]);
  const FORWARD_EVENTS = new Set(["sampling", "volume-shipment", "sale-publication", "partner-availability", "support-start", "roadmap-target"]);
  const state = {language: "ja", source: null, latest: null, latestRequest: null};

  const copy = {
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
    rackCount: {ja: "ラック数", en: "Rack count"},
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
      ja: "手動調整を含むブラウザ内試算です。公開根拠が不足する数量は算定せず、調達判断には使用できません。",
      en: "This browser-local calculation includes manual adjustments. Quantities unsupported by public evidence remain unavailable and must not be used for procurement."
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
    document.querySelectorAll("[data-language]").forEach((button) => {
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
      .filter((event) => event.date.value <= targetDate && types.has(event.event_type))
      .sort((left, right) => right.date.value.localeCompare(left.date.value))[0] || null;
  }

  function observedProcurement(product, targetDate) {
    return (product.events || []).some((event) =>
      event.claim_status === "observed" &&
      PROCUREMENT_EVENTS.has(event.event_type) &&
      event.date.value <= targetDate
    );
  }

  function forwardEvidence(product, targetDate) {
    return (product.events || []).some((event) =>
      FORWARD_EVENTS.has(event.event_type) &&
      event.date.value <= targetDate &&
      (event.claim_status === "official-plan" || event.claim_status === "observed")
    );
  }

  function selectedVendors() {
    const selected = byId("accelerator-vendor").value;
    if (selected !== "auto") return [selected];
    return [...new Set(state.source[2].products.map((product) => product.vendor))].sort();
  }

  function selectedProducts() {
    const exact = byId("accelerator-product").value;
    if (exact !== "auto") {
      return state.source[2].products.filter((product) => product.product_id === exact)
        .filter((product) => observedProcurement(product, acceptanceDate()) || forwardEvidence(product, acceptanceDate()))
        .map((product) => ({product, proposal_class: observedProcurement(product, acceptanceDate()) ? "evidenced" : "forward"}));
    }
    const target = acceptanceDate();
    const selected = [];
    selectedVendors().forEach((vendor) => {
      const products = state.source[2].products.filter((product) => product.vendor === vendor);
      const choose = (predicate) => products
        .filter((product) => predicate(product, target))
        .sort((left, right) => (right.generation_rank - left.generation_rank) ||
          ((right.events.at(-1)?.date.value || "").localeCompare(left.events.at(-1)?.date.value || "")))[0];
      const evidenced = choose(observedProcurement);
      const forward = choose((product, date) => !observedProcurement(product, date) && forwardEvidence(product, date));
      if (evidenced) selected.push({product: evidenced, proposal_class: "evidenced"});
      if (forward) selected.push({product: forward, proposal_class: "forward"});
    });
    return selected.sort((left, right) => {
      const classOrder = {evidenced: 0, forward: 1};
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
    const result = OpenFSGpuPlanner.evaluate(
      request,
      state.source[1],
      state.source[2],
      state.source[3],
      null
    );
    const candidate = result.vendor_candidates[0];
    candidate.proposal_class = selection.proposal_class;
    candidate.track_note_ja = copy[selection.proposal_class + "Note"].ja;
    candidate.track_note_en = copy[selection.proposal_class + "Note"].en;
    return candidate;
  }

  function calculate() {
    try {
      byId("form-error").textContent = "";
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
        engine_version: OpenFSGpuPlanner.ENGINE_VERSION,
        vendor_candidates: candidates,
        benchmark_candidates: OpenFSGpuPlanner.BENCHMARKS
      };
      renderResult(state.latest);
    } catch (error) {
      byId("form-error").textContent = error.message;
    }
  }

  function baselineCase(candidate) {
    return candidate.cases.find((item) => item.price_case === "baseline") || candidate.cases[0];
  }

  function eventLabel(product) {
    const target = acceptanceDate();
    const types = product && observedProcurement(product, target) ? PROCUREMENT_EVENTS : FORWARD_EVENTS;
    const event = product ? relevantEvent(product, target, types) : null;
    if (!event) return text("unknown");
    return event.event_type + " / " + event.date.value + " (" + event.date.precision + ", " + event.claim_status + ")";
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
      [text("computeUnits"), formatNumber(quantities.compute_units)],
      [text("gpuCount"), formatNumber(quantities.gpu_count)],
      [text("rackCount"), formatNumber(quantities.rack_count)],
      [text("power"), value?.power ? formatNumber(value.power.total_kw, 1) + " kW" : text("unavailable")],
      [text("configCost"), formatOku(value?.costs.configuration_cost_jpy)],
      [text("tco"), formatOku(value?.tco.total_tco_jpy)]
    ]));
    if (!value || value.status === "blocked") card.append(element("p", "planner-blocking", text("vendorQuote")));
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
      [text("computeUnits"), (candidate) => formatNumber(baselineCase(candidate).quantities?.compute_units)],
      [text("gpuCount"), (candidate) => formatNumber(baselineCase(candidate).quantities?.gpu_count)],
      [text("rackCount"), (candidate) => formatNumber(baselineCase(candidate).quantities?.rack_count)],
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
    details.append(element("summary", null, text("priceCases")));
    const wrap = element("div", "table-wrap");
    const table = element("table", "planner-price-case-table");
    const head = element("thead");
    const hr = element("tr");
    ["price", "status", "compute", "GPU", "rack", "CAPEX", "TCO"].forEach((label) => hr.append(element("th", null, label)));
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
    });
    table.append(head, body);
    wrap.append(table);
    details.append(wrap);
    article.append(details);
    const software = candidate.software_profile;
    if (software) article.append(definitionList([
      [state.language === "ja" ? "計算スタック" : "Compute stack", software.compute_stack.join(", ")],
      [state.language === "ja" ? "通信スタック" : "Communication stack", software.communication_stack.join(", ")],
      [state.language === "ja" ? "ソフトウェア" : "Software", software.software_stack.join(", ")]
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
    const summary = byId("result-summary");
    summary.replaceChildren();
    if (!result.vendor_candidates.length) summary.append(element("p", "planner-blocking", text("noCandidate")));
    else result.vendor_candidates.forEach((candidate) => summary.append(summaryCard(candidate)));
    byId("result-comparison").replaceChildren(comparisonTable(result.vendor_candidates));
    byId("result-details").replaceChildren(...result.vendor_candidates.map(candidateDetails));
    renderEvidence(result);
  }

  function csvExport() {
    const rows = [["proposal_class", "vendor", "product_id", "price_case", "status", "compute_units", "gpu_count", "rack_count", "configuration_cost_jpy", "contingency_jpy", "unused_budget_jpy", "tco_jpy", "gap_ids"]];
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
      value.gap_ids.join("|")
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
    ["override-compute-units", "override-fast-pb", "override-local-nvme"].forEach((id) => { byId(id).value = ""; });
    calculate();
  }

  function bind() {
    document.querySelectorAll("[data-language]").forEach((button) => button.addEventListener("click", () => applyLanguage(button.dataset.language)));
    byId("accelerator-vendor").addEventListener("change", () => renderProductOptions(false));
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
