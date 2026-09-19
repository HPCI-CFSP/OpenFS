(() => {
  "use strict";
  const data = window.OPENFS_PUBLIC_DATA.application_device_comparison;
  const apps = window.OPENFS_PUBLIC_DATA.application_performance_overview.applications;
  const requested = new URLSearchParams(location.search).get("app") || location.hash.slice(1);
  let selectedApp = apps.some(a => a.application_id === requested) ? requested : apps[0].application_id;
  let selectedGroup = null;
  const el = (tag, text) => { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; return n; };
  const copy = {
    ja: {
      app: "アプリケーション", workload: "入力・計測区間", low: "小さいほど高速", high: "大きいほど高速",
      reference: "公開報告の実測値（EEA1指定入力との一致は未確認）", device: "CPU／GPU・測定環境",
      value: "報告値", conditions: "実行条件・根拠", forecast: "校正済み予測に不足する根拠", unavailable: "未成立",
      noData: "比較可能な1 CPU／1 GPUの実測値が未確認です。", noProfile: "予測に必要な入力・版・精度、カーネル別計測、ホスト処理・転送・同期・I/O、対象製品の仕様が不足しています。",
      from: "予測元", missing: "不足している情報", method: "予測方法と検証条件", provenance: "資料・確認日",
      published: "公開日", unknownDate: "公開日未確認", checked: "確認日", singleCPU: "1 CPU", singleGPU: "1 GPU ＋ ホストCPU",
      caveat: "暫定・独立検証未完了。調達評価には使用できません。予測の算定不能は性能ゼロではありません。",
      peers: "対象製品の世代だけでなく、入力・精度・コード・ホスト構成が異なる点にも注意が必要です。",
      range: "予測幅や誤差は未評価です。基準機を変えた予測のばらつきを「精度」とは表示しません。",
      conditional: "帯域比例の条件付き参考試算（未検証）", target: "試算対象GPU", assumptions: "成立に必要な仮定",
      preliminary: "暫定仕様", publishedSpec: "公表仕様", assumed: "基準機の型番は仮定", formula: "計算式・仕様の根拠",
      formulaText: "カーネル性能の参考値 = 基準機の報告値 × 対象機の仕様帯域 ÷ 基準機の仮定仕様帯域",
      diagnostic: "既存H100報告値との照合（精度検証ではありません）", difference: "報告値との差",
      diagnosticNote: "A100からH100を試算し、同じ格子サイズの報告値と照合しています。型番・精度・コード条件が未確定なので、差にはモデル誤差以外の要因も含まれます。対象値を使った係数調整はしていません。",
      conditionalValue: "条件付き試算値", pair: "試算先 ← 基準機", specification: "仮定型番・仕様帯域", noInterval: "信頼区間・検証済み誤差: 未確立。調達評価には利用不可。"
    },
    en: {
      app: "Application", workload: "Input / timing boundary", low: "Lower is faster", high: "Higher is faster",
      reference: "Reported measurements (equivalence to the EEA1 input unverified)", device: "CPU / GPU and environment",
      value: "Reported value", conditions: "Conditions and evidence", forecast: "Evidence still needed for calibrated forecasts", unavailable: "Not established",
      noData: "No verified comparable single-CPU / single-GPU measurements.", noProfile: "Missing frozen input, version, precision, per-kernel profiles, host/transfer/sync/I/O timings and target product specifications.",
      from: "from", missing: "Missing evidence", method: "Prediction method and validation", provenance: "References and check dates",
      published: "Published", unknownDate: "Publication date unverified", checked: "Checked", singleCPU: "1 CPU", singleGPU: "1 GPU + host CPUs",
      caveat: "Provisional; independent verification incomplete. Not for procurement scoring. An unavailable estimate is not zero performance.",
      peers: "Input, precision, code and host configuration differences matter, not just the device generation.",
      range: "Forecast ranges and errors are not established. Spread across baselines is not reported as accuracy.",
      conditional: "Bandwidth-proportional what-if (unvalidated)", target: "Target GPU", assumptions: "Required assumptions",
      preliminary: "Preliminary specification", publishedSpec: "Published specification", assumed: "Baseline variant assumed", formula: "Formula and specification evidence",
      formulaText: "Reference kernel throughput = reported baseline throughput × target specification bandwidth / assumed baseline specification bandwidth",
      diagnostic: "Check against existing H100 reports (not an accuracy validation)", difference: "Difference from report",
      diagnosticNote: "A100-based H100 calculations are compared with reports for the same lattice size. Unresolved variants, precision and code conditions confound the difference. No coefficient was fitted to the target values.",
      conditionalValue: "Conditional value", pair: "Target ← baseline", specification: "Assumed variant / specification bandwidth", noInterval: "Confidence interval and validated error: not established. Not for procurement scoring."
    }
  };
  function link(url, title) {
    const node = el("a", title);
    try {
      const parsed = new URL(url);
      if (parsed.protocol !== "https:") return el("span", title);
      node.href = parsed.href; node.target = "_blank"; node.rel = "noopener noreferrer";
    } catch (_) { return el("span", title); }
    return node;
  }
  function bars(rows, title, lang, t) {
    const chart = el("div"); chart.className = "device-chart"; chart.setAttribute("role", "img");
    chart.setAttribute("aria-label", title + " / " + rows.map(m => m.device + ": " + m.value).join("; "));
    const maximum = Math.max(...rows.map(m => m.value)) * 1.1;
    const axis = el("div"); axis.className = "device-y-axis"; axis.setAttribute("aria-hidden", "true");
    [1, 0.5, 0].forEach(f => axis.append(el("span", (maximum * f).toLocaleString(lang, {maximumFractionDigits: 1})))); chart.append(axis);
    for (const m of rows) {
      const column = el("div"); column.className = "device-column";
      const plot = el("div"); plot.className = "device-plot";
      const bar = el("div"); bar.className = "device-bar " + m.kind;
      bar.style.height = (m.value / maximum * 100) + "%";
      bar.append(el("span", m.kind === "conditional" ? m.value.toFixed(1) : String(m.value))); plot.append(bar);
      const label = el("div", m.device); label.className = "device-label";
      column.append(plot, label, el("small", m.kind === "conditional" ? t.conditionalValue : m.kind === "cpu" ? t.singleCPU : t.singleGPU)); chart.append(column);
    }
    const scroll = el("div"); scroll.className = "device-chart-scroll"; scroll.append(chart); return scroll;
  }
  function simpleTable(headers, rows) {
    const table = el("table"); table.className = "device-results-table";
    const head = el("thead"), hr = el("tr"), body = el("tbody");
    headers.forEach(h => { const th = el("th", h); th.scope = "col"; hr.append(th); }); head.append(hr);
    rows.forEach(row => { const tr = el("tr"); row.forEach((value, i) => { const td = el(i === 0 ? "th" : "td", value); if (!i) td.scope = "row"; tr.append(td); }); body.append(tr); });
    table.append(head, body); const wrap = el("div"); wrap.className = "table-wrap"; wrap.append(table); return wrap;
  }
  function bandwidthScenario(group, lang, t) {
    const s = data.bandwidth_scenario;
    if (!s?.results?.some(r => r.group_id === group.id)) return null;
    const section = el("details"); section.className = "device-bandwidth-case";
    section.append(el("summary", t.conditional), el("p", s["scope_" + lang]), el("h4", t.assumptions));
    const assumptions = el("ul"); s["assumptions_" + lang].forEach(a => assumptions.append(el("li", a))); section.append(assumptions);
    const specs = Object.fromEntries(s.hardware.map(h => [h.id, h]));
    const measurements = Object.fromEntries(group.measurements.map(m => [m.id, m]));
    const controls = el("div"); controls.className = "device-controls";
    const label = el("label", t.target), select = el("select"); select.setAttribute("aria-label", t.target);
    s.target_ids.forEach(id => { const opt = el("option", specs[id].name); opt.value = id; select.append(opt); });
    label.append(select); controls.append(label); section.append(controls);
    const output = el("div"); output.className = "device-bandwidth-output"; section.append(output);
    function update() {
      const target = specs[select.value];
      const rows = s.results.filter(r => r.group_id === group.id && r.target_id === target.id);
      const name = r => target.name + " ← " + measurements[r.baseline_measurement_id].device;
      output.replaceChildren(el("p", "GFLOP/s · " + t.high + " · " + (target.specification_status === "preliminary" ? t.preliminary : t.publishedSpec)));
      output.append(bars(rows.map(r => ({value: r.value, device: name(r), kind: "conditional"})), t.conditional, lang, t));
      output.append(el("p", t.noInterval), el("h4", t.formula), el("p", t.formulaText));
      output.append(simpleTable([t.pair, t.specification, t.conditionalValue + " (GFLOP/s)"], rows.map(r => {
        const base = specs[r.baseline_hardware_id], m = measurements[r.baseline_measurement_id];
        return [name(r), `${base.name}: ${base.bandwidth_gbs} GB/s → ${target.bandwidth_gbs} GB/s · ${t.assumed}`,
          `${m.value} × ${target.bandwidth_gbs} / ${base.bandwidth_gbs} = ${r.value.toFixed(1)} (${r.extrapolation_factor.toFixed(2)}×)`];
      })));
      [...new Set([target.id, ...rows.map(r => r.baseline_hardware_id)])].forEach(id => {
        const h = specs[id], source = data.sources.find(src => src.source_id === h.source_id);
        const p = el("p"); p.append(link(source.url, h.name + " · " + h.locator)); output.append(p);
      });
    }
    select.addEventListener("change", update); update();
    section.append(el("h4", t.diagnostic), el("p", t.diagnosticNote));
    section.append(simpleTable([t.pair, t.conditionalValue, t.value, t.difference], s.diagnostics.filter(d => d.group_id === group.id).map(d => [
      measurements[d.reference_measurement_id].device + " ← " + measurements[d.baseline_measurement_id].device,
      d.calculated_value.toFixed(1), String(d.reported_value), (d.signed_difference_percent >= 0 ? "+" : "") + d.signed_difference_percent.toFixed(1) + "%"
    ])));
    return section;
  }
  function render(lang) {
    if (!data) return;
    const t = copy[lang]; const local = (o, key) => o[key + "_" + lang];
    const root = document.getElementById("device-comparison");
    root.replaceChildren();
    root.append(el("h3", local(data, "title")), el("p", t.caveat));
    const controls = el("div"); controls.className = "device-controls";
    function selectControl(label, items, value, change) {
      const wrapper = el("label", label);
      const select = el("select"); select.setAttribute("aria-label", label);
      for (const [id, text] of items) { const option = el("option", text); option.value = id; select.append(option); }
      select.value = value; select.addEventListener("change", () => change(select.value));
      wrapper.append(select); controls.append(wrapper); return select;
    }
    selectControl(t.app, apps.map(a => [a.application_id, a.name]), selectedApp, value => { selectedApp = value; selectedGroup = null; render(lang); });
    const groups = data.groups.filter(g => g.application_id === selectedApp);
    if (!groups.some(g => g.id === selectedGroup)) selectedGroup = groups[0]?.id;
    if (groups.length) selectControl(t.workload, groups.map(g => [g.id, local(g, "title")]), selectedGroup, value => { selectedGroup = value; render(lang); });
    root.append(controls);
    const group = groups.find(g => g.id === selectedGroup);
    if (group) {
      const rows = group.measurements;
      root.append(el("h4", local(group, "title")), el("p", t.reference));
      const unit = el("p", group.unit + " · " + (group.direction === "lower" ? t.low : t.high)); unit.className = "device-axis-title";
      root.append(unit);
      root.append(bars(rows, local(group, "title") + " / " + group.unit, lang, t));
      root.append(el("p", local(group, "scope")), el("p", local(data, "caveat")));
      const details = el("details"); details.append(el("summary", t.conditions));
      const table = el("table"); table.className = "device-results-table";
      const head = el("thead"), hr = el("tr");
      [t.device, t.value + " (" + group.unit + ")", t.conditions].forEach(label => { const th = el("th", label); th.scope = "col"; hr.append(th); });
      head.append(hr); const body = el("tbody");
      rows.forEach(m => { const tr = el("tr"); const th = el("th", m.device); th.scope = "row"; tr.append(th, el("td", String(m.value)), el("td", m.environment)); body.append(tr); });
      table.append(head, body);
      const wrap = el("div"); wrap.className = "table-wrap"; wrap.append(table);
      details.append(wrap, link(group.source_url, group.locator)); root.append(details);
      const scenario = bandwidthScenario(group, lang, t); if (scenario) root.append(scenario);
    } else {
      root.append(el("p", t.noData));
      data.gaps.filter(g => g.application_id === selectedApp).forEach(g => root.append(el("p", local(g, "note"))));
    }
    root.append(el("h4", t.forecast), el("p", t.peers));
    const pairs = data.forecast_pairs.filter(p => p.application_id === selectedApp);
    if (!pairs.length) root.append(el("p", t.noProfile));
    for (const pair of pairs) {
      const detail = el("details"); detail.className = "device-forecast-gap";
      detail.append(el("summary", pair.target + " (" + t.from + ": " + pair.baseline + ") · " + t.unavailable));
      detail.append(el("p", t.missing));
      const list = el("ul"); local(pair, "missing").forEach(m => list.append(el("li", m)));
      detail.append(list, el("p", t.range)); root.append(detail);
    }
    const methods = el("details"); methods.append(el("summary", t.method));
    data.methods.forEach(m => methods.append(el("h4", m.name), el("p", local(m, "note"))));
    methods.append(el("h4", t.provenance));
    data.sources.forEach(s => {
      const p = el("p"); p.append(link(s.url, s.title), el("small", " · " + (s.published_at ? t.published + ": " + s.published_at : t.unknownDate) + " · " + t.checked + ": " + s.checked_at)); methods.append(p);
    });
    root.append(methods);
  }
  window.OpenFSDeviceComparison = {render};
})();
