(() => {
  "use strict";
  const artifact = window.OPENFS_PUBLIC_DATA.application_device_comparison?.accelerator_targets;
  const selected = new Map();
  const node = (tag, text) => {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    return element;
  };
  const words = {
    ja: {device: "GPU（1基）", memory: "HBM4容量", bandwidth: "HBM帯域", unknown: "未公表・未確認", workload: "入力・計測区間",
      source: "基準実測", predicted: "条件付き推定", range: "仮定感度", coverage: "カウンタ標本のGPU時間カバー率", missing: "推定不可：FP32の仕事量が正で、理論FP32性能が未確認",
      assumptions: "適用条件・根拠", scenario: "MI430X 帯域の出典", status: "暫定・AMD実測なし・移植未検証", seconds: "秒", sources: "AMD一次資料", formula: "計算条件と入力SHA-256"},
    en: {device: "GPU (one device)", memory: "HBM4 capacity", bandwidth: "HBM bandwidth", unknown: "Unpublished / unverified", workload: "Input / timer scope",
      source: "Source measurement", predicted: "Conditional estimate", range: "Assumption sensitivity", coverage: "GPU-time coverage of counter samples", missing: "Unavailable: positive FP32 work with no verified FP32 peak",
      assumptions: "Applicability and evidence", scenario: "MI430X bandwidth source", status: "Provisional; no AMD measurements; port unvalidated", seconds: "s", sources: "AMD primary sources", formula: "Model contract and input SHA-256"}
  };
  function render(language) {
    const root = document.getElementById("accelerator-target-forecasts");
    if (!root || !artifact) return;
    const w = words[language];
    const field = (item, key) => item[`${key}_${language}`];
    const number = value => value.toLocaleString(language, {maximumFractionDigits: 3, minimumFractionDigits: 3});
    const frame = (table, label) => {
      const region = node("div"); region.className = "accelerator-scroll"; region.tabIndex = 0;
      region.setAttribute("role", "region"); region.setAttribute("aria-label", label); region.append(table); return region;
    };
    const table = headings => {
      const t = node("table"); t.className = "accelerator-table";
      const head = node("thead"); const row = node("tr");
      for (const heading of headings) {const th = node("th", heading); th.scope = "col"; row.append(th);}
      head.append(row); t.append(head, node("tbody")); return t;
    };
    const specs = table([w.device, "FP64 vector (TFLOP/s)", "FP32 vector (TFLOP/s)", w.memory, w.bandwidth]);
    for (const target of artifact.targets) {
      const scenario = target.bandwidth_scenarios.find(s => s.id === (selected.get(target.id) || target.default_scenario_id));
      const row = node("tr"); row.dataset.acceleratorId = target.id;
      const title = node("th", target.name); title.scope = "row";
      row.append(title, node("td", target.fp64_tflops ?? w.unknown), node("td", target.fp32_tflops ?? w.unknown),
        node("td", `${target.memory_gb} GB`), node("td", `${scenario.bandwidth_gbs / 1000} TB/s`));
      specs.tBodies[0].append(row);
    }
    const selector = node("select"); selector.id = "accelerator-bandwidth-scenario";
    const mi430 = artifact.targets.find(t => t.id === "mi430x");
    for (const scenario of mi430.bandwidth_scenarios) {
      const option = node("option", field(scenario, "label")); option.value = scenario.id;
      option.selected = scenario.id === (selected.get(mi430.id) || mi430.default_scenario_id); selector.append(option);
    }
    selector.addEventListener("change", () => {selected.set(mi430.id, selector.value); render(language);});
    const label = node("label", w.scenario); label.htmlFor = selector.id;
    const toolbar = node("div"); toolbar.className = "accelerator-toolbar"; toolbar.append(label, selector);
    const forecasts = table([w.workload, w.source, ...artifact.targets.map(t => `${t.name} · ${w.predicted}`)]);
    for (const request of artifact.requests) {
      const row = node("tr"); row.dataset.acceleratorCase = request.id;
      const title = node("th", field(request, "title")); title.scope = "row"; row.append(title);
      const sourceRow = artifact.results.find(r => r.case_id === request.id && r.baseline_seconds != null);
      const source = node("td", `${request.baseline_machine_id.toUpperCase()} · ${number(sourceRow.baseline_seconds)} ${w.seconds}`);
      row.append(source);
      for (const target of artifact.targets) {
        const result = artifact.results.find(r => r.case_id === request.id && r.target_id === target.id &&
          r.scenario_id === (selected.get(target.id) || target.default_scenario_id));
        const cell = node("td"); cell.dataset.acceleratorTarget = target.id;
        if (result.seconds == null) {
          cell.className = "measurement-unavailable"; cell.append(node("span", w.missing));
        } else {
          cell.append(node("strong", `${number(result.seconds)} ${w.seconds}`),
            node("small", `${w.range}: ${number(result.minimum)}–${number(result.maximum)} ${w.seconds}`),
            node("small", `${w.coverage}: ${(100 * result.coverage_fraction).toFixed(1)}%`));
        }
        cell.title = `SHA-256: ${result.forecast_inputs_sha256}`; row.append(cell);
      }
      forecasts.tBodies[0].append(row);
    }
    const evidence = node("details"); evidence.append(node("summary", w.assumptions), node("p", field(artifact, "caveat")));
    for (const target of artifact.targets) evidence.append(node("p", `${target.name}: ${field(target, "note")}`));
    evidence.append(node("h4", w.sources));
    const sources = node("ul");
    for (const source of artifact.sources) {
      const item = node("li"); const link = node("a", source.title);
      if (/^https:\/\/www\.amd\.com\//.test(source.url)) {link.href = source.url; link.rel = "noopener noreferrer";}
      item.append(link, node("small", `${source.published_at || source.checked_at} · ${source.locator}`)); sources.append(item);
    }
    const provenance = node("details"); provenance.append(node("summary", w.formula),
      node("pre", JSON.stringify({model_contract: artifact.model_contract, model_source_sha256: artifact.model_source_sha256,
        inputs: artifact.results.map(r => ({case_id:r.case_id, target_id:r.target_id, scenario_id:r.scenario_id, sha256:r.forecast_inputs_sha256}))}, null, 2)));
    evidence.append(sources, provenance);
    root.replaceChildren(node("h3", field(artifact, "title")), node("p", w.status), node("p", field(artifact, "summary")),
      toolbar, frame(specs, w.device), frame(forecasts, w.predicted), evidence);
  }
  window.OpenFSAcceleratorForecasts = {render};
})();
