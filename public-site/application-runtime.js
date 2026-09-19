(() => {
  "use strict";
  const data = window.OPENFS_PUBLIC_DATA.application_device_comparison;
  const view = data.runtime_view;
  const apps = window.OPENFS_PUBLIC_DATA.application_performance_overview.applications;
  const root = document.getElementById("runtime-comparison");
  const params = () => new URLSearchParams(location.search);
  const el = (tag, text) => { const n = document.createElement(tag); if (text !== undefined) n.textContent = text; return n; };
  let language = "ja";
  const local = (item, key) => item[key + "_" + language];
  const t = (ja, en) => language === "ja" ? ja : en;
  const fmt = n => Number(n).toLocaleString(language, {maximumFractionDigits: 3});
  const machine = id => view.machines.find(m => m.id === id);
  const comparison = view.specification_comparison;
  const visibleMachines = new Set(view.machines.map(m => m.id));
  let selectedMachine = machine(params().get("machine"))?.id || null;
  let comparisonOpen = false;
  const specification = id => comparison.records.find(r => r.machine_id === id);
  const specStatus = status => ({
    published: t("公表仕様", "Published"), preliminary: t("暫定仕様", "Preliminary"),
    derived: t("換算値", "Derived")
  })[status];
  const specValue = (metric, value) => value ? fmt(value.value)+" "+(value.unit || metric.unit) : t("未確認", "Unverified");
  function href(c, anchor = "") {
    const url = new URL(location.href); url.search = "";
    url.searchParams.set("lang", language);
    if (c) { url.searchParams.set("app", c.application_id); url.searchParams.set("case", c.id); }
    url.hash = anchor; return url.href;
  }
  function link(text, url) {
    const a = el("a", text);
    try {
      const parsed = new URL(url, location.href);
      if (!["https:", "http:"].includes(parsed.protocol)) return el("span", text);
      a.href = parsed.href;
      a.addEventListener("click", () => document.getElementById("runtime-dialog")?.close());
      if (parsed.origin !== location.origin) { a.target = "_blank"; a.rel = "noopener noreferrer"; }
    } catch (_) { return el("span", text); }
    return a;
  }
  function button(text, action) { const b = el("button", text); b.type = "button"; b.addEventListener("click", action); return b; }
  function table(headers, rows) {
    const a = el("table"); const head = el("thead"), hr = el("tr");
    headers.forEach(s => { const th = el("th", s); th.scope = "col"; hr.append(th); }); head.append(hr);
    const body = el("tbody");
    rows.forEach(row => { const tr = el("tr"); row.forEach(s => tr.append(el("td", s))); body.append(tr); });
    a.append(head, body); const wrap = el("div"); wrap.className = "table-wrap"; wrap.append(a); return wrap;
  }
  function dialog(title, children, restoreFocus = null) {
    document.getElementById("runtime-dialog")?.remove();
    const d = el("dialog"); d.id = "runtime-dialog"; d.className = "operational-dialog device-dialog";
    const h = el("h2", title); h.id = "runtime-dialog-title"; d.setAttribute("aria-labelledby", h.id);
    d.append(h, button(t("閉じる", "Close"), () => d.close()), ...children);
    const opener = document.activeElement;
    d.addEventListener("close", () => { d.remove(); if (restoreFocus) restoreFocus(); else if (opener?.isConnected) opener.focus(); });
    document.body.append(d); d.showModal();
  }
  function source(id) {
    const s = data.sources.find(s => s.source_id === id);
    return s ? link(s.title, s.url) : el("span", t("出典未確認", "Source unavailable"));
  }
  function specs(m) {
    const opener=document.activeElement;
    selectedMachine = m.id;
    visibleMachines.add(m.id);
    refreshSpecifications();
    const p = data.device_profiles.find(p => p.id === m.profile_id);
    const parts = [];
    if (p) parts.push(table([t("項目", "Item"), t("内容", "Value")], [
      [t("ホストCPU", "Host CPU"), p.cpu_model], [t("搭載ソケット / コア", "Installed sockets / cores"), p.cpu_sockets+" / "+p.cpu_cores],
      [t("GPU", "GPU"), p.accelerator_variant || t("該当なし・未確認", "Not applicable / unverified")],
      [t("搭載GPU数", "Installed GPUs"), String(p.installed_accelerators)],
      [t("GPU当たりHBM容量", "HBM per GPU"), p.accelerator_memory_gb === null ? t("未確認", "Unverified") : p.accelerator_memory_gb+" GB"]
    ]), el("p", local(p,"note")), source(p.source_id));
    else parts.push(el("p", data.kernel_study?.runs.some(r=>r.machine_id===m.id) ?
      t("このGPUで独自測定を取得しています。ホストCPU・ノード構成の詳細は未登録です。以下の理論値はカタログ仕様です。","Own measurements are available for this GPU. Host CPU and node configuration details are not yet registered. The theoretical values below are catalog specifications.") :
      t("予測対象のカタログ仕様です。ホストCPU・実装・ソフトウェア互換性は同定していません。", "Catalog specification for prediction only. Host CPU, implementation and software compatibility are not identified.")));
    const record = specification(m.id);
    parts.push(el("p",local(record,"unit")),el("p",local(record,"note")));
    const specRows = comparison.metrics.map(metric => {
      const value = record.values[metric.id];
      return [local(metric,"name"),specValue(metric,value),value ? specStatus(value.status) : t("未確認","Unverified")];
    });
    parts.push(table([t("理論性能・仕様","Theoretical performance / specification"),t("値","Value"),t("根拠区分","Evidence status")],specRows));
    for (const id of new Set(Object.values(record.values).map(v=>v.source_id))) parts.push(source(id));
    const url = new URL(location.href);url.searchParams.set("machine",m.id);url.hash="runtime-specifications";
    const compare = link(t("CPU/GPU仕様比較表で見る","View in CPU/GPU specification comparison"),url.href);
    compare.addEventListener("click",event=>{
      event.preventDefault();document.getElementById("runtime-dialog")?.close();
      history.replaceState(null,"",url);comparisonOpen=true;
      document.getElementById("runtime-specifications").open=true;
      refreshSpecifications();focusAnchor();
      const target=document.querySelector('#runtime-specification-table th[data-machine-id="'+m.id+'"]');
      const scroll=document.querySelector(".runtime-specification-scroll");
      if(target&&scroll) {
        const frozen=document.querySelector("#runtime-specification-table th:first-child").getBoundingClientRect().width;
        scroll.scrollLeft+=target.getBoundingClientRect().left-scroll.getBoundingClientRect().left-frozen;
      }
    });
    parts.push(compare);
    dialog(m.name, parts,()=>{
      if(opener?.isConnected)opener.focus();
      else document.querySelector('#runtime-specification-table th[data-machine-id="'+m.id+'"] button')?.focus();
    });
  }
  function specificationEvidence(m, metric) {
    const record=specification(m.id),value=record.values[metric.id];
    const contents=[el("p",local(record,"unit")),el("p",local(record,"note")),el("p",specValue(metric,value))];
    if(value) {
      contents.push(el("p",specStatus(value.status)),el("p",value.locator));
      if(local(value,"note"))contents.push(el("p",local(value,"note")));
      const cited=data.sources.find(s=>s.source_id===value.source_id);
      contents.push(source(value.source_id),el("p",t("根拠確認日：","Source checked: ")+cited.checked_at));
    } else contents.push(el("p",t("この機器・演算方式で対応する公表値を確認できていません。ゼロや非対応を意味しません。","No matching published value has been verified for this device and arithmetic type. This does not mean zero or unsupported.")));
    dialog(m.name+" · "+local(metric,"name"),contents);
  }
  function refreshSpecifications() {
    const mount=document.getElementById("runtime-specification-content");if(!mount)return;
    mount.replaceChildren();
    const select=el("select");select.id="runtime-specification-select";
    const empty=el("option",t("機器を選択","Select a device"));empty.value="";select.append(empty);
    view.machines.forEach(m=>{const o=el("option",m.name);o.value=m.id;select.append(o);});
    select.value=selectedMachine || "";
    select.addEventListener("change",()=>{if(machine(select.value))specs(machine(select.value));});
    const label=el("label",t("機器の詳細","Device details"));label.append(select);label.className="runtime-case-control";mount.append(label);
    const filter=el("fieldset");filter.className="runtime-specification-filter";filter.append(el("legend",t("比較対象","Devices to compare")));
    view.machines.forEach(m=>{
      const label=el("label"),check=el("input");check.type="checkbox";check.value=m.id;check.checked=visibleMachines.has(m.id);
      check.addEventListener("change",()=>{if(check.checked)visibleMachines.add(m.id);else visibleMachines.delete(m.id);refreshSpecifications();
        document.querySelector('#runtime-specification-content input[value="'+m.id+'"]')?.focus();});
      label.append(check,document.createTextNode(m.name));filter.append(label);
    });mount.append(filter);
    const active=view.machines.filter(m=>visibleMachines.has(m.id));
    if(!active.length){mount.append(el("p",t("比較対象が選択されていません。","No comparison devices selected.")));return;}
    const scroll=el("div");scroll.className="runtime-specification-scroll";scroll.tabIndex=0;scroll.setAttribute("role","region");
    scroll.setAttribute("aria-label",t("CPU/GPU理論仕様比較","CPU/GPU theoretical specification comparison"));
    const tab=el("table");tab.id="runtime-specification-table";tab.style.minWidth=(220+active.length*180)+"px";
    const head=el("thead"),hr=el("tr"),first=el("th",t("性能項目","Performance metric"));first.scope="col";hr.append(first);
    for(const m of active) {
      const th=el("th");th.scope="col";th.dataset.machineId=m.id;
      if(m.id===selectedMachine){th.className="selected";th.setAttribute("aria-current","true");}
      th.append(button(m.name,()=>specs(m)),el("small",local(specification(m.id),"unit")));hr.append(th);
    }head.append(hr);
    const body=el("tbody");
    for(const metric of comparison.metrics) {
      const row=el("tr");row.dataset.metricId=metric.id;const title=el("th",local(metric,"name"));title.scope="row";row.append(title);
      for(const m of active) {
        const cell=el("td");cell.dataset.machineId=m.id;if(m.id===selectedMachine)cell.className="selected";
        const value=specification(m.id).values[metric.id];
        cell.append(button(specValue(metric,value),()=>specificationEvidence(m,metric)));
        if(value?.status!=="published"&&value)cell.append(el("small",specStatus(value.status)));
        row.append(cell);
      }body.append(row);
    }tab.append(head,body);scroll.append(tab);mount.append(scroll);
    if(selectedMachine&&visibleMachines.has(selectedMachine)) {
      const r=specification(selectedMachine),note=el("p",machine(selectedMachine).name+": "+local(r,"note"));
      note.className="runtime-specification-note";mount.append(note);
    }
  }
  function specificationPanel() {
    const panel=el("details");panel.id="runtime-specifications";panel.open=comparisonOpen;
    panel.addEventListener("toggle",()=>{comparisonOpen=panel.open;});
    panel.append(el("summary",t("CPU/GPU 理論性能・仕様比較","CPU/GPU theoretical performance and specifications")),
      el("p",t("公称ピーク値であり、アプリケーションの実測性能ではありません。CPUは1ソケット、GPUは1 GPUの値です。GH200のCPU性能・LPDDRはGPUの行へ加算しません。Dense、Sparsity、エミュレーション、メーカー併記値は別項目です。接続帯域は公称合計であり、片方向の実効帯域ではありません。","Catalog peaks, not measured application performance. CPU values are per socket and GPU values per GPU. GH200 CPU performance and LPDDR are not added to GPU rows. Dense, sparse, emulated and combined vendor labels remain distinct. Link bandwidth is the advertised aggregate, not one-way achieved bandwidth.")));
    const mount=el("div");mount.id="runtime-specification-content";panel.append(mount);root.append(panel);refreshSpecifications();
  }
  function methodLink(id, c) {
    const m = view.methods.find(m => m.id === id);
    return link(local(m, "name"), href(c, "method-"+id));
  }
  function evidence(r, c) {
    const contents = [el("p", local(c,"scope")),
      el("p", fmt(r.seconds)+" s · "+(r.scope === "main" ? t("main全体", "main runtime") : t("HMC更新区間のみ。総時間は未算定。", "HMC update only. Total runtime unavailable.")))];
    if (r.kind === "predicted") {
      const method = view.methods.find(m => m.id === r.method_id);
      contents.push(methodLink(r.method_id, c), el("p", method.formula),
        el("p", "T0="+fmt(r.baseline_seconds)+" s; B0="+r.baseline_bandwidth_gbs+" GB/s; B1="+r.target_bandwidth_gbs+" GB/s; f="+fmt(r.kernel_share)),
        el("p", t("予測元：", "Baseline: ")+machine(r.baseline_id).name),
        el("p", local(method,"note")));
      const observed = view.results.find(v => v.case_id === c.id && v.machine_id === r.machine_id && v.kind === "measured");
      if (observed) contents.push(el("p", t("同じ評価ケースの実測との差：", "Difference from the measured matching case: ")+((r.seconds/observed.seconds-1)*100).toFixed(1)+"%"));
      contents.push(el("p", t("対象実測値による係数調整なし。未校正・調達評価不可。", "No coefficient fitted to the target measurement. Uncalibrated; not for procurement.")));
      if(r.method_id==="kernel-roofline") {
        const frozen=data.kernel_study.frozen,base=frozen.baseline_spec,target=frozen.targets[r.machine_id];
        contents.push(table([t("モデル入力","Model input"),t("予測元","Baseline"),t("予測先","Target")],[
          ["FP64 TFLOP/s",fmt(base.fp64),fmt(target.fp64)],
          ["FP32 TFLOP/s",fmt(base.fp32),fmt(target.fp32)],
          ["HBM GB/s",fmt(base.bandwidth),fmt(target.bandwidth)]
        ]),el("p",t("B300のFP64はメーカー併記値から換算した条件付き上限です。通常FP64の実効値ではありません。","B300 FP64 is a conditional ceiling normalized from the combined vendor label, not an achieved native-FP64 rate.")));
        contents.push(el("p",t("仮定感度の範囲（信頼区間ではありません）：","Assumption sensitivity, not a confidence interval: ")+fmt(r.minimum)+"–"+fmt(r.maximum)+" s"),
          el("p",t("カウンタ対応率（基準機GPU時間）：","Counter coverage of baseline GPU time: ")+(100*r.coverage_fraction).toFixed(1)+"%"),
          el("p",t("予測固定日時：","Forecast frozen at: ")+r.frozen_at),
          el("p",r.prior_target_seen ? t("この対象の旧実測は開発時に既知です。盲検検証ではありません。","Earlier measurements of this target were known during development; not blind validation.") : t("この対象の実測結果を確認する前に予測を固定しました。","Forecast frozen before inspecting this target's measurements.")),
          link(t("カーネルカウンタ・時間区分・限界","Kernel counters, timeline and limitations"),href(c,"runtime-kernel-study")));
      }
    } else {
      contents.push(el("p", t("通常実行。プロファイラ無効。初回を除く3回の中央値。", "Normal execution with profiler disabled. Median of three retained repetitions after excluding the first process.")),
        el("p", t("観測範囲：", "Observed range: ")+fmt(r.minimum)+"–"+fmt(r.maximum)+" s"));
      if (r.phases) contents.push(table([t("区間", "Phase"), "s"], Object.entries(r.phases).map(([key,value])=>[phaseName(key),fmt(value)])));
      else contents.push(el("p", t("初期化・終了処理はこの計測区間に含まれません。", "Initialization and finalization are outside this timing boundary.")));
    }
    contents.push(link(t("評価条件・実行時間の内訳", "Conditions and runtime breakdown"),href(c,"runtime-detail")));
    dialog(machine(r.machine_id).name+" · "+(r.kind === "measured" ? t("実測値","Measured") : t("予測値","Predicted")),contents);
  }
  function phaseName(key) {
    return ({initialization:t("初期化","Initialization"),compute:t("主要計算","Computation"),finalization:t("終了処理","Finalization"),unclassified:t("未分類","Unclassified"),update:t("更新区間のみ","Update only")})[key];
  }
  function chart(cases, detail) {
    const scroll = el("div"); scroll.className = "runtime-scroll"; scroll.tabIndex = 0; scroll.setAttribute("role","region"); scroll.setAttribute("aria-label",t("評価ケース別の実行時間比較","Runtime comparison by evaluation case"));
    const tab = el("table"); tab.className = "runtime-grid"+(detail ? " runtime-detailed" : "");
    const head = el("thead"), hr = el("tr"), first = el("th",t("評価ケース / 秒・小さいほど高速","Evaluation case / seconds, lower is faster"));
    first.scope="col"; hr.append(first);
    view.machines.forEach(m => { const th=el("th"); th.scope="col"; th.dataset.machineId=m.id; th.append(button(m.name,()=>specs(m)));hr.append(th); });
    head.append(hr); const body=el("tbody");
    cases.forEach(c => {
      const row=el("tr"); row.dataset.caseId=c.id;
      const values=view.results.filter(r=>r.case_id===c.id);
      const max=values.length ? Math.max(...values.map(r=>r.seconds))*1.2 : 1;
      const th=el("th");th.scope="row";th.append(link(local(c,"title"),href(c)));
      const app=apps.find(a=>a.application_id===c.application_id);
      th.append(el("small",local(app,"domain")));
      th.append(el("small",values.length ? "0–"+fmt(max)+" s" : t("独自測定待ち","Awaiting own measurements")));
      row.append(th);
      view.machines.forEach(m=>{
        const cell=el("td");cell.dataset.machineId=m.id;
        const rs=values.filter(r=>r.machine_id===m.id);
        if (!rs.length) {
          const missing=button(t("未算定","Unavailable"),()=>dialog(local(c,"title")+" / "+m.name,[
            el("p",c.kind==="unmeasured" ? local(c,"scope") : t("この機器・評価条件に対応する通常実行の実測値、または区間別予測の根拠がありません。ゼロ秒ではありません。","No matching normal-run measurement or evidenced phase prediction for this machine and case. This is not zero seconds.")),
            link(t("詳細","Details"),href(c))]));
          missing.className="runtime-missing";cell.append(missing);
        } else {
          const group=el("div");group.className="runtime-bars";
          rs.forEach(r=>{
            const column=el("div");column.className="runtime-column";
            const plot=el("div");plot.className="runtime-plot";
            const bar=button("",()=>evidence(r,c));bar.className="runtime-bar "+r.kind;bar.dataset.resultId=r.id;
            bar.style.height=(r.seconds/max*100)+"%";
            bar.setAttribute("aria-label",m.name+" · "+(r.kind==="measured" ? t("実測値","Measured") : local(view.methods.find(v=>v.id===r.method_id),"name"))+" · "+fmt(r.seconds)+" s");
            bar.title=bar.getAttribute("aria-label");
            const value=el("span",fmt(r.seconds));value.className="runtime-value";bar.append(value);
            const segments=r.phases || {update:r.seconds};
            for(const [key,sec] of Object.entries(segments)) {const s=el("span");s.className="runtime-segment phase-"+key;s.style.height=(sec/r.seconds*100)+"%";s.title=phaseName(key)+": "+fmt(sec)+" s";bar.append(s);}
            plot.append(bar);column.append(plot);
            if(r.kind==="measured") column.append(el("small",t("実測","Measured")));
            else {
              const a=methodLink(r.method_id,c);a.className="runtime-method-label";a.title=a.textContent;
              a.textContent=({"bandwidth-proportional":t("帯域比例","Bandwidth"),"profile-assisted":t("時間比併用","Time-share"),"kernel-roofline":t("カーネル別","Per-kernel")})[r.method_id];
              column.append(a,el("small","← "+machine(r.baseline_id).name.split("-")[0]));
            }
            group.append(column);
          });cell.append(group);
        }
        row.append(cell);
      });body.append(row);
    });
    tab.append(head,body);scroll.append(tab);return scroll;
  }
  function profileDetails(study) {
    const outer=el("details");outer.id="runtime-profile";outer.append(el("summary",t("プロファイル実行：GPU内訳（通常実行とは別）","Profiled execution: GPU breakdown (separate from normal runtime)")));
      outer.append(el("p",t("以下は別実行のHMC更新区間だけのトレースです。main全体の内訳ではなく、通常実行の棒にも転用しません。GPUが稼働していない時間の原因は未分類です。","These separate-run traces cover only the HMC update, not the entire main function. They are not decompositions of the normal-run bars. Causes of non-GPU-active time remain unclassified.")));
    for(const run of [study.baseline,study.target]) {
      const m=view.machines.find(m=>m.profile_id===run.device_profile_id);
      const detail=el("details");detail.append(el("summary",m.name));
      const normal=[...run.repeat_seconds].sort((a,b)=>a-b)[1];
      detail.append(table([t("指標","Metric"),"s"],[
        [t("通常実行：更新区間の中央値","Normal run: median update"),fmt(normal)],
        [t("プロファイル実行：更新区間","Profiled run: update window"),fmt(run.window_seconds)],
        [t("GPU稼働時間（区間の和集合）","GPU-active interval union"),fmt(run.kernel_union_seconds)],
        [t("GPU非稼働時間（未分類）","Non-GPU-active time (unclassified)"),fmt(run.window_seconds-run.kernel_union_seconds)]
      ]),el("p",t("トレース中の時間増加：","Traced runtime increase: ")+((run.window_seconds/normal-1)*100).toFixed(1)+"%"));
      const stack=el("div");stack.className="runtime-profile-stack";stack.setAttribute("role","img");
      stack.setAttribute("aria-label",t("GPU稼働 / 未分類","GPU active / unclassified")+": "+fmt(run.kernel_union_seconds)+" / "+fmt(run.window_seconds-run.kernel_union_seconds)+" s");
      for(const [key,value] of [["compute",run.kernel_union_seconds],["unclassified",run.window_seconds-run.kernel_union_seconds]]) {const segment=el("span",key==="compute" ? "GPU" : t("未分類","Unclassified"));segment.className="phase-"+key;segment.style.width=(value/run.window_seconds*100)+"%";stack.append(segment);}
      detail.append(stack);
      const kernel=el("details");kernel.append(el("summary",t("カーネル別累積時間","Cumulative time by kernel")));
      const largest=Math.max(...run.kernels.map(k=>k.seconds));
      const graph=el("div");graph.className="runtime-kernels";
      for(const k of run.kernels) {const line=el("div"),name=el("span",k.name),bar=el("span",fmt(k.seconds)+" s");bar.className="runtime-kernel-bar";bar.style.width=(k.seconds/largest*100)+"%";line.append(name,bar);graph.append(line);}
      kernel.append(el("p",t("累積カーネル時間です。重なりがある場合は壁時計時間と一致しません。","Cumulative kernel times; overlapping intervals must not be added as wall-clock time.")),graph,
        table([t("カーネル","Kernel"),"s",t("呼出回数","Calls")],run.kernels.map(k=>[k.name,fmt(k.seconds),String(k.count)])));
      detail.append(kernel);outer.append(detail);
    }
    return outer;
  }
  function kernelDetails(study) {
    const outer=el("details");outer.id="runtime-kernel-study";outer.open=true;
    outer.append(el("summary",t("カーネル別モデル：計測根拠と検証","Per-kernel model: measurements and validation")),el("p",local(study,"note")),el("p",study.compiler),
      link(study.source_commit,"https://github.com/i-kanamori/LQCD-DWF-HMC/tree/"+study.source_commit));
    const names={gpu:t("GPUカーネル","GPU kernels"),copy:t("GPU転送","GPU copies"),sync_api:t("同期API（GPU等との重複除外）","Sync APIs, excluding higher-priority overlap"),launch_api:t("起動API（重複除外）","Launch APIs, excluding overlap"),unclassified:t("未分類：CPU処理・I/O等","Unclassified: CPU work, I/O, etc.")};
    for(const run of study.runs) {
      const detail=el("details"),r=run.data;detail.append(el("summary",machine(run.machine_id).name));
      detail.append(el("p",run.receipt.measurement_started_at+" → "+run.receipt.completed_at),
        el("p","Nsight Systems "+run.receipt.nsys_version+" / Nsight Compute "+run.receipt.ncu_version),
        el("p","Binary SHA-256: "+run.receipt.binary_sha256));
      detail.append(table([t("通常実行","Normal run"),t("更新区間（秒）","Update (seconds)"),"H(diff)"],r.runs.map((v,i)=>[String(i)+(v.warmup?t("（除外）"," (excluded)"):""),fmt(v.seconds),String(v.h_diff)])),
        el("h4",t("別実行のトレース内訳","Separate-run trace partition")),
        el("p",t("以下はプロファイル実行の時間です。通常実行の実測内訳ではありません。","These are profiled-run times, not measured decompositions of normal execution.")),
        table([t("重複を除いた時間区分","Disjoint time partition"),"s"],Object.entries(r.timeline).map(([k,v])=>[names[k],fmt(v)])));
      const graph=el("div");graph.className="runtime-kernels";
      const max=Math.max(...Object.values(r.timeline));
      for(const [key,seconds] of Object.entries(r.timeline)) {
        const row=el("div"),bar=el("span",fmt(seconds)+" s");bar.className="runtime-kernel-bar";bar.style.width=(seconds/max*100)+"%";
        row.append(el("span",names[key]),bar);graph.append(row);
      }detail.append(graph);
      const counter=el("details");counter.append(el("summary",t("起動形状別カウンタ（1呼出し当たり）","Counters by launch shape, per invocation")));
      const median=(samples,key)=>{const values=samples.map(v=>v[key]).filter(v=>v!==null).sort((a,b)=>a-b);return values.length?fmt((values[Math.floor((values.length-1)/2)]+values[Math.floor(values.length/2)])/2):t("未取得","Not captured");};
      counter.append(table([t("カーネル・起動形状","Kernel / grid / block"),t("累積秒 / 回数","Cumulative seconds / calls"),t("サンプル数","Samples"),"FP64 FLOPs","FP32 FLOPs","HBM bytes","L2 bytes"],r.kernels.map(k=>[
        k.name+" / "+k.grid.join("×")+" / "+k.block.join("×"),fmt(k.seconds)+" / "+k.count,String(k.samples.length),
        ...["fp64_ops","fp32_ops","hbm_bytes","l2_bytes"].map(key=>median(k.samples,key))])));
      detail.append(counter);outer.append(detail);
    }
    const ul=el("ul");study["limitations_"+language].forEach(note=>ul.append(el("li",note)));outer.append(ul);
    return outer;
  }
  function detail(c) {
    root.append(link(t("← すべての評価ケース","← All evaluation cases"),href(null)));
    const label=el("label",t("評価ケース","Evaluation case")),select=el("select");select.id="runtime-case-select";
    view.cases.forEach(item=>{const o=el("option",local(item,"title"));o.value=item.id;o.selected=item.id===c.id;select.append(o);});
    select.addEventListener("change",()=>{location.href=href(view.cases.find(v=>v.id===select.value));});label.append(select);label.className="runtime-case-control";root.append(label);
    const h=el("h3",local(c,"title"));h.id="runtime-detail";root.append(h,el("p",local(c,"scope")),chart([c],true));
    const study=data.profile_studies.find(s=>s.id===c.study_id);
    if(study) {
      const d=el("details");d.id="runtime-repro";d.append(el("summary",t("評価条件・再現情報","Conditions and reproducibility")),el("p",local(study,"precision")),el("p",study.compiler),link(study.source_commit,study.code_url),
        table([t("入力ファイル","Input file"),"SHA-256"],study.input_files.map(f=>[f.name,f.sha256])));
      d.append(el("p",t("1 MPIランク・1 OpenMPスレッド・1 GPU。EEA1指定入力との一致は未確認。","One MPI rank, one OpenMP thread, one GPU. Equivalence to the prescribed EEA1 input is unverified.")));
      root.append(d);
      const records=view.phase_runs.filter(r=>r.case_id===c.id);
      if(records.length) {
        const normal=el("details");normal.id="runtime-normal";normal.open=true;normal.append(el("summary",t("通常実行：初期化・主要計算・終了処理","Normal run: initialization, computation and finalization")));
        normal.append(el("p",t("総時間の中央値に当たる1回の実行を積み上げ表示します。区間ごとの中央値を足し合わせてはいません。初回プロセスは除外しますが、各実行の初期化は除外しません。","The stacked bar uses the complete median-total run, not a sum of independently selected phase medians. The first process is excluded; initialization in each retained run is not excluded.")));
        for(const r of records) {
          normal.append(el("h4",machine(r.machine_id).name),
            table([t("反復","Repeat"),t("初期化","Initialization"),t("主要計算","Computation"),t("終了処理","Finalization"),t("main合計","main total"),t("外側の経過時間","Outer elapsed time")],
              r.rows.map((v,i)=>[String(i)+(v.warmup ? t("（除外）"," (excluded)") : ""),fmt(v.initialization),fmt(v.compute),fmt(v.finalization),fmt(v.total),fmt(v.normal_wall_seconds)])));
          const result=view.results.find(x=>x.case_id===c.id&&x.machine_id===r.machine_id);
          normal.append(el("p",t("元の実行との経過時間中央値の差：","Median outer-time difference from the original executable: ")+result.instrumentation_wall_difference_percent.toFixed(1)+"%"));
        }
        root.append(normal);
      }
      root.append(profileDetails(study));
      const limits=el("details");limits.append(el("summary",t("予測の限界・未確認事項","Prediction limitations and gaps")));
      const ul=el("ul");study["caveats_"+language].forEach(v=>ul.append(el("li",v)));limits.append(ul);root.append(limits);
    }
    if(c.kind==="kernel-study")root.append(kernelDetails(data.kernel_study));
    for(const method of view.methods) {
      const section=el("details");section.id="method-"+method.id;section.className="runtime-method";
      section.append(el("summary",local(method,"name")),el("p",method.formula),el("p",local(method,"note")));
      method.source_ids.forEach(id=>section.append(source(id)));
      root.append(section);
    }
  }
  function focusAnchor() {
    let id;try{id=decodeURIComponent(location.hash.slice(1));}catch(_){return;}
    if(!id.startsWith("method-")&&!id.startsWith("runtime-"))return;
    const node=document.getElementById(id);
    if(node){if(node.tagName==="DETAILS")node.open=true;node.tabIndex=-1;node.scrollIntoView({block:"start"});node.focus({preventScroll:true});}
  }
  function render(lang) {
    language=lang;root.replaceChildren();
    const p=params(),requested=view.cases.find(c=>c.id===p.get("case"));
    const app=apps.find(a=>a.application_id===p.get("app"));
    const c=requested || (app ? view.cases.find(c=>c.application_id===app.application_id) : null);
    document.getElementById("legacy-device-reference").hidden=!c;
    root.append(el("p",t("通常実行の秒数。塗りつぶし＝実測、点線枠＝予測。色＝初期化・主要計算・終了処理。未算定はゼロではありません。","Normal-run seconds. Solid bars: measured; dashed outlines: predicted. Colors: initialization, computation, finalization. Unavailable does not mean zero.")));
    const legend=el("div");legend.className="runtime-legend";
    ["initialization","compute","finalization","update"].forEach(key=>{const item=el("span",phaseName(key));item.className="legend-"+key;legend.append(item);});root.append(legend);
    if(c) detail(c);
    else {
      root.append(el("p",t("機器列は世代順で共通です。同世代内の列順は性能順位ではありません。各行は同一条件・同一計測区間で比較し、行間で尺度は異なります。","Shared machine columns follow generation order, not performance rank within a generation. Comparisons use matching conditions and timing boundaries within each row; scales differ across rows.")));
      const available=new Set(view.results.map(r=>r.case_id));
      const ordered=[...view.cases].sort((a,b)=>Number(available.has(b.id))-Number(available.has(a.id)));
      root.append(chart(ordered,false));
    }
    specificationPanel();
    focusAnchor();
  }
  window.addEventListener("hashchange",focusAnchor);
  window.OpenFSRuntime={render,focusAnchor};
})();
