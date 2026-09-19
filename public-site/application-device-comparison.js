(() => {
  "use strict";
  const data = window.OPENFS_PUBLIC_DATA.application_device_comparison;
  const apps = window.OPENFS_PUBLIC_DATA.application_performance_overview.applications;
  const requested = new URLSearchParams(location.search).get("app") || location.hash.slice(1);
  let selectedApp = apps.some(a => a.application_id === requested) ? requested : apps[0].application_id;
  let selectedGroup = new URLSearchParams(location.search).get("study");
  let selectedTarget = data?.bandwidth_scenario?.target_ids[0];
  const el = (tag, text) => { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; return n; };
  const copy = {
    ja: {
      app: "アプリケーション", workload: "入力・計測区間", low: "小さいほど高速", high: "大きいほど高速",
      reference: "公開報告の実測値（EEA1指定入力との一致は未確認）", device: "CPU／GPU・測定環境",
      measuredCPU: "実測値 · 1 CPU", measuredGPU: "実測値 · 1 GPU ＋ ホストCPU", estimated: "条件付き予測値（参考試算）",
      legend: "実測値・予測値の区別", forecastScope: "点線枠は帯域比例による未検証のカーネル性能予測です。アプリケーション全体の性能や予測精度を保証するものではありません。",
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
      conditionalValue: "条件付き試算値", pair: "試算先 ← 基準機", specification: "仮定型番・仕様帯域", noInterval: "信頼区間・検証済み誤差: 未確立。調達評価には利用不可。",
      specs: "機器仕様", evidence: "性能値の根拠", close: "閉じる", unknown: "未確認", item: "項目", detail: "内容",
      host: "ホストCPU", sockets: "搭載CPUソケット数", cores: "搭載CPUコア数", gpu: "GPU", installed: "搭載GPU数",
      variant: "GPUの製品版・形態", hbm: "GPU当たりHBM容量 (GB)", used: "測定に使用したデバイス数",
      publicMethod: "公開情報ベース予測", source: "根拠資料", noKernel: "この公開報告に対応するカーネル別時間の内訳は未確認です。",
      identityNote: "予測先の仕様と、報告書の測定機器が一致するとは確認できていません。基準機のGPU版・帯域は仮定です。"
    },
    en: {
      app: "Application", workload: "Input / timing boundary", low: "Lower is faster", high: "Higher is faster",
      reference: "Reported measurements (equivalence to the EEA1 input unverified)", device: "CPU / GPU and environment",
      measuredCPU: "Measured · 1 CPU", measuredGPU: "Measured · 1 GPU + host CPUs", estimated: "Conditional forecast (what-if)",
      legend: "Measured and forecast values", forecastScope: "Dashed outlines indicate unvalidated, bandwidth-proportional kernel forecasts, not whole-application performance or validated prediction accuracy.",
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
      conditionalValue: "Conditional value", pair: "Target ← baseline", specification: "Assumed variant / specification bandwidth", noInterval: "Confidence interval and validated error: not established. Not for procurement scoring.",
      specs: "Device specifications", evidence: "Performance evidence", close: "Close", unknown: "Unverified", item: "Item", detail: "Detail",
      host: "Host CPU", sockets: "Installed CPU sockets", cores: "Installed CPU cores", gpu: "GPU", installed: "Installed GPUs",
      variant: "GPU variant / form factor", hbm: "HBM per GPU (GB)", used: "Devices used in this measurement",
      publicMethod: "Public-information forecast", source: "Source", noKernel: "Per-kernel time breakdown for this reported measurement is unavailable.",
      identityNote: "The forecast specification is not a verified identification of the reported target machine. Baseline GPU variant and bandwidth remain assumptions."
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
  function dialog(title, nodes, t) {
    document.getElementById("device-evidence-dialog")?.remove();
    const modal = el("dialog"); modal.id = "device-evidence-dialog"; modal.className = "operational-dialog device-dialog";
    const heading = el("div"); heading.className = "operational-dialog-heading";
    const h = el("h2", title); h.id = "device-dialog-title"; modal.setAttribute("aria-labelledby", h.id);
    const close = el("button", t.close); close.type = "button"; close.addEventListener("click", () => modal.close());
    heading.append(h, close); modal.append(heading, ...nodes);
    modal.addEventListener("close", () => modal.remove());
    document.body.append(modal); modal.showModal();
  }
  function sourceNode(id, locator, t) {
    const source = data.sources.find(s => s.source_id === id);
    if (!source) return el("p", t.unknown);
    const p = el("p");
    p.append(link(source.url, source.title + (locator ? " · " + locator : "")),
      el("small", " · " + (source.published_at ? t.published + ": " + source.published_at : t.unknownDate) + " · " + t.checked + ": " + source.checked_at));
    return p;
  }
  function deviceNodes(m, lang, t) {
    const p = data.device_profiles.find(p => p.id === m.device_profile_id);
    if (!p) return [el("p", t.unknown)];
    return [simpleTable([t.item, t.detail], [
      [t.host, p.cpu_model], [t.sockets, String(p.cpu_sockets)], [t.cores, String(p.cpu_cores)],
      [t.gpu, p.accelerator_model || "—"], [t.installed, String(p.installed_accelerators)],
      [t.variant, p.accelerator_variant || t.unknown], [t.hbm, p.accelerator_memory_gb === null ? t.unknown : String(p.accelerator_memory_gb)],
      [t.used, String(m.device_count)], [t.conditions, m.environment]
    ]), el("p", p["note_" + lang]), sourceNode(p.source_id, p.locator, t)];
  }
  function measuredDetails(m, group, lang, t) {
    dialog(m.device + " · " + t.evidence, [
      el("p", m.value + " " + group.unit), el("p", group["scope_" + lang]),
      ...deviceNodes(m, lang, t), el("p", t.noKernel), link(group.source_url, group.locator), el("p", t.caveat)
    ], t);
  }
  function forecastDetails(r, group, target, lang, t) {
    const s = data.bandwidth_scenario, base = s.hardware.find(h => h.id === r.baseline_hardware_id);
    const m = group.measurements.find(m => m.id === r.baseline_measurement_id);
    const list = el("ul"); s["assumptions_" + lang].forEach(a => list.append(el("li", a)));
    dialog(target.name + " ← " + m.device, [
      el("p", t.publicMethod + " · " + r.value.toFixed(1) + " " + group.unit), el("p", t.formulaText),
      el("p", m.value + " × " + target.bandwidth_gbs + " / " + base.bandwidth_gbs + " = " + r.value.toFixed(1)),
      el("p", t.identityNote), el("h3", t.assumptions), list,
      el("h3", t.specification), el("p", base.name + ": " + base.bandwidth_gbs + " GB/s → " + target.name + ": " + target.bandwidth_gbs + " GB/s"),
      sourceNode(base.source_id, base.locator, t), sourceNode(target.source_id, target.locator, t),
      link(group.source_url, group.locator), el("p", t.noInterval), el("p", t.caveat)
    ], t);
  }
  function bars(rows, title, lang, t) {
    const status = m => m.kind === "conditional" ? t.estimated : m.kind === "cpu" ? t.measuredCPU : t.measuredGPU;
    const chart = el("div"); chart.className = "device-chart"; chart.setAttribute("role", "group");
    chart.setAttribute("aria-label", title + " / " + rows.map(m => m.device + ": " + m.value + " (" + status(m) + ")").join("; "));
    const maximum = Math.max(...rows.map(m => m.value)) * 1.1;
    const axis = el("div"); axis.className = "device-y-axis"; axis.setAttribute("aria-hidden", "true");
    [1, 0.5, 0].forEach(f => axis.append(el("span", (maximum * f).toLocaleString(lang, {maximumFractionDigits: 1})))); chart.append(axis);
    for (const m of rows) {
      const column = el("div"); column.className = "device-column";
      const plot = el("div"); plot.className = "device-plot";
      const bar = el("button"); bar.type = "button"; bar.className = "device-bar " + m.kind;
      bar.setAttribute("aria-label", m.device + ": " + m.value + " · " + status(m) + " · " + t.evidence);
      bar.title = t.evidence; bar.addEventListener("click", m.onEvidence);
      bar.style.height = (m.value / maximum * 100) + "%";
      bar.append(el("span", m.displayValue || (m.kind === "conditional" ? m.value.toFixed(1) : String(m.value)))); plot.append(bar);
      const label = el("button", m.device); label.type = "button"; label.className = "device-label device-spec-link";
      label.title = t.specs; label.addEventListener("click", m.onSpecs);
      column.append(plot, label, el("small", status(m))); chart.append(column);
    }
    const legend = el("ul"); legend.className = "device-chart-legend"; legend.setAttribute("aria-label", t.legend);
    for (const kind of new Set(rows.map(m => m.kind))) {
      const item = el("li"), swatch = el("span"); swatch.className = "device-legend-swatch " + kind; swatch.setAttribute("aria-hidden", "true");
      item.append(swatch, el("span", status({kind}))); legend.append(item);
    }
    const scroll = el("div"); scroll.className = "device-chart-scroll"; scroll.tabIndex = 0;
    scroll.setAttribute("role", "region"); scroll.setAttribute("aria-label", title); scroll.append(chart);
    const figure = el("figure"); figure.className = "device-comparison-chart"; figure.append(legend, scroll); return figure;
  }
  function simpleTable(headers, rows) {
    const table = el("table"); table.className = "device-results-table";
    const head = el("thead"), hr = el("tr"), body = el("tbody");
    headers.forEach(h => { const th = el("th", h); th.scope = "col"; hr.append(th); }); head.append(hr);
    rows.forEach(row => { const tr = el("tr"); row.forEach((value, i) => { const td = el(i === 0 ? "th" : "td", value); if (!i) td.scope = "row"; tr.append(td); }); body.append(tr); });
    table.append(head, body); const wrap = el("div"); wrap.className = "table-wrap"; wrap.append(table); return wrap;
  }
  function profileStudy(study, lang, t) {
    const ja = lang === "ja", r = study.results;
    const name = run => data.device_profiles.find(p => p.id === run.device_profile_id).name;
    const methods = [ja ? "帯域比のみ" : "Bandwidth ratio only", ja ? "実測プロファイル併用" : "Measured-profile assisted"];
    const section = el("section"); section.className = "device-profile-study";
    const local = key => study[key + "_" + lang];
    const notes = el("ul"); local("caveats").forEach(note => notes.append(el("li", note)));
    const fakeMeasurement = run => ({device_profile_id: run.device_profile_id, device_count: 1, environment: study.compiler});
    const fmt = n => n.toFixed(3);
    function measured(run, seconds) {
      const show = () => dialog(name(run) + " · " + t.evidence, [
        el("p", local("scope")), el("p", study.timing_boundary), el("p", study.compiler), el("p", local("precision")),
        ...deviceNodes(fakeMeasurement(run), lang, t),
        simpleTable([ja ? "反復" : "Repeat", "s"], run.repeat_seconds.map((n,i) => [String(i+1),fmt(n)])),
        el("p", ja ? "ウォームアップ1回を除く3回の中央値。標本が少なく、一般的な性能や信頼区間を保証しません。" : "Median of three repetitions after excluding one warm-up. Too few observations to establish general performance or confidence intervals."),
        link(study.code_url, study.source_commit), el("p", t.caveat)
      ], t);
      return {device: name(run), kind: "gpu", value: seconds, displayValue: fmt(seconds), onEvidence: show,
        onSpecs: () => dialog(name(run) + " · " + t.specs, deviceNodes(fakeMeasurement(run), lang, t), t)};
    }
    function forecast(index) {
      const value = index ? r.profile.seconds : r.bandwidth_seconds;
      const label = name(study.target) + " ← " + name(study.baseline) + " · " + methods[index];
      const error = index ? r.profile_error : r.bandwidth_error;
      const show = () => dialog(label, [
        el("p", fmt(value) + " s"), el("p", index ? "T = T₀ × (1 − f + f × B₀ / B₁)" : "T = T₀ × B₀ / B₁"),
        el("p", `T₀=${fmt(r.baseline_seconds)} s; B₀=${study.baseline_bandwidth_gbs} GB/s; B₁=${study.target_bandwidth_gbs} GB/s; f=${r.profile.kernel_share.toFixed(6)}`),
        el("p", ja ? "fはトレース内のGPUカーネル区間の和集合／計測窓。GPU活性時間がメモリ律速であるという仮定は未検証です。残りの時間は固定し、CPU処理だけとはみなしません。" : "f is the clipped union of GPU-kernel intervals divided by the trace window. Uniform bandwidth scaling of kernel time is unverified; remaining time is held fixed and is not identified as pure CPU work."),
        el("p", index ? (ja ? "仮定を変えた範囲（信頼区間ではない）: " : "Assumption range (not a confidence interval): ") + fmt(r.profile.scenario_low_seconds) + "–" + fmt(r.profile.scenario_high_seconds) + " s" : t.noInterval),
        el("p", (ja ? "対象の実測値との差: " : "Difference from held-out target: ") + error.signed_percentage_error.toFixed(1) + "%"),
        el("p", (ja ? "予測固定: " : "Forecast frozen: ") + study.frozen_at),
        el("p", "SHA256: " + study.forecast_freeze_sha256),
        ...study.source_ids.map(id => sourceNode(id, "", t)), el("p", t.caveat)
      ], t);
      return {device: label, kind: "conditional", value, displayValue: fmt(value), onEvidence: show, onSpecs: show};
    }
    section.append(el("h4", local("title")), el("p", local("scope")), el("p", "s · " + t.low),
      bars([measured(study.baseline, r.baseline_seconds), measured(study.target, r.target_seconds), forecast(0), forecast(1)], local("title") + " / s", lang, t));
    section.append(simpleTable([ja ? "予測方法" : "Prediction method", "s", ja ? "実測との差" : "Difference from measured"], [
      [methods[0], fmt(r.bandwidth_seconds), r.bandwidth_error.signed_percentage_error.toFixed(1) + "%"],
      [methods[1], fmt(r.profile.seconds), r.profile_error.signed_percentage_error.toFixed(1) + "%"]
    ]), notes);
    for (const run of [study.baseline, study.target]) {
      const details = el("details"); details.className = "device-kernel-details";
      details.append(el("summary", name(run) + " · " + (ja ? "GPUカーネル内訳・計測品質" : "GPU-kernel breakdown and measurement quality")));
      const median = values => [...values].sort((a,b) => a-b)[1];
      details.append(simpleTable([t.item, t.detail], [
        [ja ? "通常実行の中央値" : "Normal-run median", fmt(median(run.repeat_seconds)) + " s"],
        [ja ? "トレース中の計測窓" : "Traced timing window", fmt(run.window_seconds) + " s"],
        [ja ? "GPUカーネル区間の和集合" : "GPU-kernel interval union", fmt(run.kernel_union_seconds) + " s"],
        [ja ? "トレースによる時間比" : "Trace / normal time ratio", (run.window_seconds / median(run.repeat_seconds)).toFixed(3)],
        [ja ? "フック挿入前後のMainタイマー差" : "Main-timer change with instrumentation", ((median(run.instrumented_main_seconds)/median(run.original_main_seconds)-1)*100).toFixed(1) + "%"],
        ["H(diff)", run.h_diff.map(String).join(", ")]
      ]));
      details.append(el("p", ja ? "下図はトレース中のGPUカーネル累積時間の内訳です。通常実行の総時間の内訳ではありません。重なりは別途検査しています。最初の3つの初期化カーネルのみで取得したDRAMカウンタは、本計算の律速判定には使っていません。" : "The breakdown is cumulative GPU-kernel time during tracing, not normal-run total time. Overlap is checked separately. DRAM counters collected for only the first three initialization kernels are not used to infer bottlenecks in the update."));
      const sum = run.kernels.reduce((n,k) => n + k.seconds, 0);
      const graph = el("div"); graph.className = "device-kernel-graph";
      const top = run.kernels.slice(0, 6);
      if (run.kernels.length > 6) top.push({name: ja ? "その他のカーネル" : "Other kernels", seconds: sum - top.reduce((n,k) => n+k.seconds, 0)});
      for (const kernel of top) {
        const row = el("div"), label = el("span", kernel.name), track = el("div"), bar = el("span");
        track.className = "device-kernel-track"; bar.style.width = (kernel.seconds / sum * 100) + "%"; track.append(bar);
        row.append(label, track, el("span", fmt(kernel.seconds) + " s · " + (kernel.seconds / sum * 100).toFixed(1) + "%")); graph.append(row);
      }
      details.append(graph, simpleTable([ja ? "カーネル" : "Kernel", "s", ja ? "呼出回数" : "Invocations"], run.kernels.map(k => [k.name, fmt(k.seconds), String(k.count)])));
      section.append(details);
    }
    const repro = el("details"); repro.append(el("summary", ja ? "再現条件・公開根拠" : "Reproducibility and public evidence"), link(study.code_url, study.source_commit),
      el("p", study.compiler), el("p", local("precision")), el("p", study.timing_boundary),
      simpleTable([ja ? "入力" : "Input", "SHA256"], study.input_files.map(f => [f.name, f.sha256])),
      el("p", "Protocol SHA256: " + study.protocol_sha256),
      el("p", "Forecast SHA256: " + study.forecast_freeze_sha256),
      el("p", (ja ? "対象結果の初回確認: " : "Target results first read: ") + study.target_read_at),
      ...study.source_ids.map(id => sourceNode(id, "", t)));
    section.append(repro); return section;
  }
  function bandwidthScenario(group, target, rows, lang, t) {
    const s = data.bandwidth_scenario;
    const section = el("details"); section.className = "device-bandwidth-case";
    section.append(el("summary", t.conditional), el("p", s["scope_" + lang]), el("h4", t.assumptions));
    const assumptions = el("ul"); s["assumptions_" + lang].forEach(a => assumptions.append(el("li", a))); section.append(assumptions);
    const specs = Object.fromEntries(s.hardware.map(h => [h.id, h]));
    const measurements = Object.fromEntries(group.measurements.map(m => [m.id, m]));
    const output = el("div"); output.className = "device-bandwidth-output"; section.append(output);
    const name = r => target.name + " ← " + measurements[r.baseline_measurement_id].device;
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
    const studies = (data.profile_studies || []).filter(s => s.application_id === selectedApp);
    const choices = [...groups, ...studies];
    if (!choices.some(g => g.id === selectedGroup)) selectedGroup = choices[0]?.id;
    if (choices.length) selectControl(t.workload, choices.map(g => [g.id, local(g, "title")]), selectedGroup, value => { selectedGroup = value; render(lang); });
    root.append(controls);
    const study = studies.find(s => s.id === selectedGroup);
    if (study) { root.append(profileStudy(study, lang, t)); return; }
    if (studies.length) {
      const openStudy = el("button", lang === "ja" ? "実測・プロファイルによる予測と照合を見る" : "View measured-profile predictions and held-out checks");
      openStudy.type = "button"; openStudy.addEventListener("click", () => { selectedGroup = studies[0].id; render(lang); });
      root.append(openStudy);
    }
    const group = groups.find(g => g.id === selectedGroup);
    if (group) {
      const rows = group.measurements;
      const scenario = data.bandwidth_scenario;
      const targets = scenario?.target_ids.filter(id => scenario.results.some(r => r.group_id === group.id && r.target_id === id)) || [];
      if (targets.length && !targets.includes(selectedTarget)) selectedTarget = targets[0];
      const specs = Object.fromEntries((scenario?.hardware || []).map(h => [h.id, h]));
      if (targets.length) selectControl(t.target, targets.map(id => [id, specs[id].name]), selectedTarget, value => { selectedTarget = value; render(lang); });
      const forecasts = targets.length ? scenario.results.filter(r => r.group_id === group.id && r.target_id === selectedTarget) : [];
      const target = specs[selectedTarget];
      root.append(el("h4", local(group, "title")), el("p", t.reference));
      if (forecasts.length) {
        const note = el("p", t.forecastScope + " " + target.name + ": " + (target.specification_status === "preliminary" ? t.preliminary : t.publishedSpec));
        note.className = "device-forecast-note"; root.append(note);
      }
      const unit = el("p", group.unit + " · " + (group.direction === "lower" ? t.low : t.high)); unit.className = "device-axis-title";
      root.append(unit);
      root.append(bars([
        ...rows.map(m => ({...m, onEvidence: () => measuredDetails(m, group, lang, t),
          onSpecs: () => dialog(m.device + " · " + t.specs, deviceNodes(m, lang, t), t)})),
        ...forecasts.map(r => ({value: r.value, device: target.name + " ← " + rows.find(m => m.id === r.baseline_measurement_id).device, kind: "conditional",
          onEvidence: () => forecastDetails(r, group, target, lang, t), onSpecs: () => forecastDetails(r, group, target, lang, t)}))
      ], local(group, "title") + " / " + group.unit, lang, t));
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
      if (forecasts.length) root.append(bandwidthScenario(group, target, forecasts, lang, t));
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
