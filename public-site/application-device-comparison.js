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
      value: "報告値", conditions: "実行条件・根拠", forecast: "予測先と予測元", unavailable: "算定不能",
      noData: "比較可能な1 CPU／1 GPUの実測値が未確認です。", noProfile: "予測に必要な入力・版・精度、カーネル別計測、ホスト処理・転送・同期・I/O、対象製品の仕様が不足しています。",
      from: "予測元", missing: "不足している情報", method: "予測方法と検証条件", provenance: "資料・確認日",
      published: "公開日", unknownDate: "公開日未確認", checked: "確認日", singleCPU: "1 CPU", singleGPU: "1 GPU ＋ ホストCPU",
      caveat: "暫定・独立検証未完了。調達評価には使用できません。予測の算定不能は性能ゼロではありません。",
      peers: "対象製品の世代だけでなく、入力・精度・コード・ホスト構成が異なる点にも注意が必要です。",
      range: "予測幅や誤差は未評価です。基準機を変えた予測のばらつきを「精度」とは表示しません。"
    },
    en: {
      app: "Application", workload: "Input / timing boundary", low: "Lower is faster", high: "Higher is faster",
      reference: "Reported measurements (equivalence to the EEA1 input unverified)", device: "CPU / GPU and environment",
      value: "Reported value", conditions: "Conditions and evidence", forecast: "Forecast target and baseline", unavailable: "Unavailable",
      noData: "No verified comparable single-CPU / single-GPU measurements.", noProfile: "Missing frozen input, version, precision, per-kernel profiles, host/transfer/sync/I/O timings and target product specifications.",
      from: "from", missing: "Missing evidence", method: "Prediction method and validation", provenance: "References and check dates",
      published: "Published", unknownDate: "Publication date unverified", checked: "Checked", singleCPU: "1 CPU", singleGPU: "1 GPU + host CPUs",
      caveat: "Provisional; independent verification incomplete. Not for procurement scoring. An unavailable estimate is not zero performance.",
      peers: "Input, precision, code and host configuration differences matter, not just the device generation.",
      range: "Forecast ranges and errors are not established. Spread across baselines is not reported as accuracy."
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
      const chart = el("div"); chart.className = "device-chart"; chart.setAttribute("role", "img");
      chart.setAttribute("aria-label", local(group, "title") + " / " + rows.map(m => m.device + ": " + m.value + " " + group.unit).join("; "));
      const maximum = Math.max(...rows.map(m => m.value)) * 1.1;
      const axis = el("div"); axis.className = "device-y-axis"; axis.setAttribute("aria-hidden", "true");
      [1, 0.5, 0].forEach(fraction => axis.append(el("span", (maximum * fraction).toLocaleString(lang, {maximumFractionDigits: 1}))));
      chart.append(axis);
      for (const measurement of rows) {
        const column = el("div"); column.className = "device-column";
        const plot = el("div"); plot.className = "device-plot";
        const bar = el("div"); bar.className = "device-bar " + measurement.kind;
        bar.style.height = (measurement.value / maximum * 100) + "%";
        bar.append(el("span", String(measurement.value))); plot.append(bar);
        const label = el("div", measurement.device); label.className = "device-label";
        column.append(plot, label, el("small", measurement.kind === "cpu" ? t.singleCPU : t.singleGPU)); chart.append(column);
      }
      const scroll = el("div"); scroll.className = "device-chart-scroll"; scroll.append(chart); root.append(scroll);
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
