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
  const kernelStudy = c => c.kind === "application-study" ? data.application_studies.find(s => s.id === c.study_id) : data.kernel_study;
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
    rows.forEach(row => { const tr = el("tr"); row.forEach(s => {
      const cell=el("td");if(s instanceof Node)cell.append(s);else cell.textContent=s;tr.append(cell);
    }); body.append(tr); });
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
      else contents.push(el("p",t("予測対象の同条件の独自実測は未取得です。精度検証は未完了です。","No matching own measurement of the target is available. Prediction accuracy is not validated.")));
      if(observed&&r.minimum!==null&&r.maximum!==null&&(observed.seconds<r.minimum||observed.seconds>r.maximum)) contents.push(el("p",t("注意：実測値は仮定感度の範囲外です。このケースではモデルの説明力が不足しています。","Warning: the measurement lies outside the assumption-sensitivity range. This model does not adequately explain this case.")));
      contents.push(el("p", t("対象実測値による係数調整なし。未校正・調達評価不可。", "No coefficient fitted to the target measurement. Uncalibrated; not for procurement.")));
      if(r.method_id==="kernel-roofline") {
        const study=kernelStudy(c);
        const forecasts=study.forecasts || [{baseline_machine_id:study.baseline_machine_id,frozen:study.frozen},...(study.additional_forecasts||[])];
        const forecast=forecasts.find(f=>f.baseline_machine_id===r.baseline_id&&f.frozen.targets[r.machine_id]);
        const frozen=forecast.frozen;
        const base=frozen.baseline_spec,target=frozen.targets[r.machine_id];
        contents.push(table([t("モデル入力","Model input"),t("予測元","Baseline"),t("予測先","Target")],[
          ["FP64 TFLOP/s",fmt(base.fp64),fmt(target.fp64)],
          ["FP32 TFLOP/s",fmt(base.fp32),fmt(target.fp32)],
          ["HBM GB/s",fmt(base.bandwidth),fmt(target.bandwidth)]
        ]),el("p",t("B200/B300のFP64入力はメーカー併記値を使った条件付き上限、Rubinは公表暫定仕様です。通常FP64の実効性能を保証する値ではありません。","B200/B300 FP64 inputs are conditional ceilings from combined vendor labels; Rubin uses announced preliminary specifications. These do not guarantee achieved native-FP64 performance.")));
        contents.push(el("p",t("仮定感度の範囲（信頼区間ではありません）：","Assumption sensitivity, not a confidence interval: ")+fmt(r.minimum)+"–"+fmt(r.maximum)+" s"),
          el("p",t("カウンタ対応率（基準機GPU時間）：","Counter coverage of baseline GPU time: ")+(100*r.coverage_fraction).toFixed(1)+"%"),
          el("p",t("予測固定日時：","Forecast frozen at: ")+r.frozen_at),
          el("p",r.prior_target_seen ? t("この対象の旧実測は開発時に既知です。盲検検証ではありません。","Earlier measurements of this target were known during development; not blind validation.") : t("この対象の実測結果を確認する前に予測を固定しました。","Forecast frozen before inspecting this target's measurements.")),
          link(t("カーネルカウンタ・時間区分・限界","Kernel counters, timeline and limitations"),href(c,"runtime-kernel-study")));
        if(c.kind==="application-study") contents.push(el("p",t("主要計算区間にカーネル別モデルを適用します。初期化・終了処理の中心値は予測元の通常実行から据え置き、0.5〜2倍を感度範囲に含めます。ホストCPU・I/Oの性能予測ではありません。","The kernel model scales computation only. Initialization and finalization retain baseline normal-run values, with 0.5–2× sensitivity. Host CPU and I/O performance are not independently predicted.")));
      }
    } else {
      contents.push(el("p", t("通常実行。プロファイラ無効。初回を除く3回の中央値。", "Normal execution with profiler disabled. Median of three retained repetitions after excluding the first process.")),
        el("p", t("観測範囲：", "Observed range: ")+fmt(r.minimum)+"–"+fmt(r.maximum)+" s"));
      if (r.phases) contents.push(table([t("区間", "Phase"), "s"], Object.entries(r.phases).map(([key,value])=>[phaseName(key),fmt(value)])));
      else contents.push(el("p", t("初期化・終了処理はこの計測区間に含まれません。", "Initialization and finalization are outside this timing boundary.")));
    }
    contents.push(link(t("評価条件・実行時間の内訳", "Conditions and runtime breakdown"),href(c,"runtime-detail")));
    contents.push(link(t("再現情報・ジョブスクリプト", "Reproduction records and job scripts"),href(c,"runtime-repro-records")));
    if(r.kind === "predicted") contents.push(link(t("予測元の通常実行・プロファイル", "Baseline normal runs and profiles"),href(c,["kernel-study","application-study"].includes(c.kind)?"runtime-kernel-study":"runtime-profile")));
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
      const groups=view.generation_comparison.groups.filter(g=>g.case_id===c.id);
      const selected=new Set(groups.flatMap(g=>g.slots.map(s=>s.result_id).filter(Boolean)));
      const values=view.results.filter(r=>selected.has(r.id));
      const max=values.length ? Math.max(...values.map(r=>r.seconds))*1.2 : 1;
      const th=el("th");th.scope="row";th.append(link(local(c,"title"),href(c)));
      const app=apps.find(a=>a.application_id===c.application_id);
      th.append(el("small",local(app,"domain")));
      th.append(el("small",values.length ? "0–"+fmt(max)+" s" : t("独自測定待ち","Awaiting own measurements")));
      row.append(th);
      view.machines.forEach(m=>{
        const cell=el("td");cell.dataset.machineId=m.id;
        const slots=groups.find(g=>g.machine_id===m.id).slots;
        const rs=slots.map(s=>({...s,...values.find(r=>r.id===s.result_id)}));
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
            const slotLabel=r.offset===0 ? t("実測","Measured") : t(r.offset+"世代前",r.offset+" gen earlier");
            if(!r.result_id) {
              const missing=button(t("未算定","Unavailable"),()=>dialog(m.name+" · "+slotLabel,[
                el("p",r.offset===0 ? t("同じ入力・計測区間の独自実測は未取得です。","No own measurement with matching input and timing boundary.") :
                  t((r.source_generation || "対象世代")+"の同条件での通常実測・プロファイルに基づく予測が未取得です。他世代の数値で代用しません。","A forecast using matching normal runs and profiles from "+(r.source_generation || "the required generation")+" is unavailable. No substitute from another generation.")),
                link(t("再現情報・不足項目","Reproduction records and gaps"),href(c,"runtime-repro-records"))]));
              missing.className="runtime-missing";plot.append(missing);column.append(plot,el("small",slotLabel));
              if(r.source_generation)column.append(el("small",r.source_generation));
              group.append(column);return;
            }
            const bar=button("",()=>evidence(r,c));bar.className="runtime-bar "+r.kind;bar.dataset.resultId=r.id;
            bar.style.height=(r.seconds/max*100)+"%";
            bar.setAttribute("aria-label",m.name+" · "+slotLabel+" · "+(r.kind==="measured" ? t("実測値","Measured") : local(view.methods.find(v=>v.id===r.method_id),"name"))+" · "+fmt(r.seconds)+" s");
            bar.title=bar.getAttribute("aria-label");
            const value=el("span",fmt(r.seconds));value.className="runtime-value";bar.append(value);
            const segments=r.phases || {update:r.seconds};
            for(const [key,sec] of Object.entries(segments)) {const s=el("span");s.className="runtime-segment phase-"+key;s.style.height=(sec/r.seconds*100)+"%";s.title=phaseName(key)+": "+fmt(sec)+" s";bar.append(s);}
            plot.append(bar);column.append(plot);
            if(r.kind==="measured") column.append(el("small",t("実測","Measured")));
            else {
              const a=methodLink(r.method_id,c);a.className="runtime-method-label";a.title=a.textContent;
              a.textContent=({"bandwidth-proportional":t("帯域比例","Bandwidth"),"profile-assisted":t("時間比併用","Time-share"),"kernel-roofline":t("カーネル別","Per-kernel")})[r.method_id];
              const baseLabel=el("small",machine(r.baseline_id).name.split(/[ -]/)[0]);baseLabel.title=machine(r.baseline_id).name;
              column.append(el("small",slotLabel),a,baseLabel);
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
      link(study.source_commit,study.source_url || "https://github.com/i-kanamori/LQCD-DWF-HMC/tree/"+study.source_commit));
    const names={gpu:t("GPUカーネル","GPU kernels"),copy:t("GPU転送","GPU copies"),sync_api:t("同期API（GPU等との重複除外）","Sync APIs, excluding higher-priority overlap"),launch_api:t("起動API（重複除外）","Launch APIs, excluding overlap"),unclassified:t("未分類：CPU処理・I/O等","Unclassified: CPU work, I/O, etc.")};
    for(const run of study.runs) {
      const detail=el("details"),r=run.data;detail.append(el("summary",machine(run.machine_id).name));
      detail.append(el("p",run.receipt.measurement_started_at+" → "+run.receipt.completed_at),
        el("p","Nsight Systems "+run.receipt.nsys_version+" / Nsight Compute "+run.receipt.ncu_version),
        el("p","Binary SHA-256: "+run.receipt.binary_sha256));
      if(run.receipt.completion_basis)detail.append(el("p",t("終了日時は別プロファイル取得を含むジョブ完了時刻です。","Completion is the scheduler job end, including separate profiling.")));
      detail.append(table([t("入力ファイル","Input file"),"SHA-256"],Object.entries(r.input_sha256)));
      if(run.phase_rows) detail.append(table([t("通常実行","Normal run"),t("初期化","Initialization"),t("主要計算","Computation"),t("終了処理","Finalization"),t("合計（秒）","Total (seconds)")],run.phase_rows.map((v,i)=>[String(i)+(v.warmup?t("（除外）"," (excluded)"):""),...['initialization','compute','finalization','total'].map(k=>fmt(v[k]))])),el("p",local(run.verification,"method")));
      else detail.append(table([t("通常実行","Normal run"),t("更新区間（秒）","Update (seconds)"),"H(diff)"],r.runs.map((v,i)=>[String(i)+(v.warmup?t("（除外）"," (excluded)"):""),fmt(v.seconds),String(v.h_diff)])));
      detail.append(
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
    const history=view.phase_runs.filter(r=>r.historical_study_id&&study.id==="PHASE-"+r.case_id.toUpperCase());
    if(history.length) {
      const previous=el("details");previous.append(el("summary",t("過去の通常実行記録（現在の棒グラフとは別）","Historical normal runs (separate from current bars)")));
      for(const r of history)previous.append(el("h4",machine(r.machine_id).name),
        el("p","Header SHA-256: "+r.header_sha256),
        table([t("反復","Repeat"),t("初期化","Initialization"),t("主要計算","Computation"),t("終了","Finalization"),t("合計秒","Total seconds")],
          r.rows.map((v,i)=>[String(i)+(v.warmup?t("（除外）"," (excluded)"):""),...["initialization","compute","finalization","total"].map(k=>fmt(v[k]))])));
      outer.append(previous);
    }
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
    if(["kernel-study","application-study"].includes(c.kind))root.append(kernelDetails(kernelStudy(c)));
    root.append(reproductionDetails(c),diagnosticDetails(c));
    for(const method of view.methods) {
      const section=el("details");section.id="method-"+method.id;section.className="runtime-method";
      section.append(el("summary",local(method,"name")),el("p",method.formula),el("p",local(method,"note")));
      method.source_ids.forEach(id=>section.append(source(id)));
      root.append(section);
    }
  }
  function reproductionDetails(c) {
    const panel=el("details");panel.id="runtime-repro-records";
    panel.append(el("summary",t("再現情報・ジョブスクリプト","Reproduction records and job scripts")));
    const records=view.reproducibility.filter(r=>r.case_ids.includes(c.id));
    if(!records.length)panel.append(el("p",t("この評価ケースの再現情報は未登録です。","No reproducibility record for this evaluation case yet.")));
    for(const record of records) {
      panel.append(el("p",record.status==="partial" ? t("一部未記録：完全に同じ実行環境での再現は未確認です。","Partially recorded: reproduction of the complete execution environment is not established.") : t("記録済み。再実行時は入力と環境の一致を確認してください。","Recorded. Verify matching inputs and environment when rerunning.")),
        link("Source commit: "+record.source_commit,record.source_url),
        table([t("項目","Item"),t("設定・観測","Configuration / observation"),t("状態","Status")],record.settings.map(s=>[
          local(s,"name"),local(s,"value"),({recorded:t("記録済み","Recorded"),requested:t("指定値","Requested"),"not-recorded":t("未記録","Not recorded")})[s.status]])));
      for(const artifact of record.artifacts) {
        const d=el("details");d.append(el("summary",artifact.name),el("p",local(artifact,"note")),el("p","SHA-256: "+artifact.sha256));
        if(artifact.content!==null) {
          const pre=el("pre");pre.append(el("code",artifact.content));d.append(pre);
          d.append(button(t("ファイルをダウンロード","Download file"),()=>{
            const url=URL.createObjectURL(new Blob([artifact.content],{type:"text/plain;charset=utf-8"}));
            const a=document.createElement("a");a.href=url;a.download=artifact.name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
          }));
        }panel.append(d);
      }
      const gaps=el("ul");record["gaps_"+language].forEach(g=>gaps.append(el("li",g)));panel.append(gaps);
    }return panel;
  }
  function diagnosticDetails(c) {
    const d=el("details");d.id="runtime-diagnostics";
    d.append(el("summary",t("旧モデル・同世代／逆方向の参考試算","Historical methods and same-/reverse-generation diagnostics")),
      el("p",t("主グラフには実測と1・2世代前からのプロファイル併用予測を表示します。以下は旧来の比較手法や同世代・逆方向の試算であり、将来世代の予測とは区別します。数値と固定履歴は保持しています。","The main chart shows measurements and profile-assisted forecasts from one and two previous generations. These historical methods and same-/reverse-generation estimates are separate diagnostics; their frozen values are retained.")));
    const ids=new Set(view.generation_comparison.diagnostic_result_ids);
    const rows=view.results.filter(r=>r.case_id===c.id&&ids.has(r.id));
    for(const r of rows) {
      const b=button(machine(r.machine_id).name+" / "+machine(r.baseline_id).name+" / "+local(view.methods.find(m=>m.id===r.method_id),"name")+": "+fmt(r.seconds)+" s",()=>evidence(r,c));
      b.dataset.resultId=r.id;d.append(b);
    }
    if(!rows.length)d.append(el("p",t("該当する参考試算はありません。","No historical diagnostics for this case.")));
    return d;
  }
  function focusAnchor() {
    let id;try{id=decodeURIComponent(location.hash.slice(1));}catch(_){return;}
    if(!id.startsWith("method-")&&!id.startsWith("runtime-"))return;
    const node=document.getElementById(id);
    if(node){if(node.tagName==="DETAILS")node.open=true;node.tabIndex=-1;node.scrollIntoView({block:"start"});node.focus({preventScroll:true});}
  }
  function analyticalPanel(c) {
    const study=data.analytical_model_study;if(!study)return null;
    const rows=study.results.filter(r=>!c||r.case_id===c.id);if(!rows.length)return null;
    const panel=el("section");panel.id="runtime-analytical-models";
    panel.append(el("h3",t("定式化モデルの比較検証","Analytical model comparison")),
      el("p",t("3アプリに同じ式を適用した暫定比較。対象機の結果は既知であり、盲検検証ではありません。初期化から終了までの秒数です。",
                 "Provisional comparison using the same formulas for three applications. Target results were already known: this is not blind validation. Seconds cover initialization through finalization.")));
    panel.append(el("p",t("各行は同一入力・同一計測区間の比較です。行間で縦軸の尺度は異なります。",
                         "Each row compares matching inputs and timing boundaries. Vertical scales differ across rows.")));
    const explain=(row,value)=>{
      const method=study.methods.find(m=>m.id===value.model);
      const content=[el("p",local(method,"note")),el("p",method.formula),
        el("p",machine(row.baseline).name+" → "+machine(row.target).name),
        table([t("量","Quantity"),t("値","Value")],[
          [t("実測 / 予測（秒）","Observed / predicted seconds"),fmt(row.observed_seconds)+" / "+fmt(value.seconds)],
          [t("相対誤差","Relative error"),value.error_percent.toFixed(1)+"%"],
          [t("GPU計算 / 据え置き部分（秒）","GPU / fixed part (seconds)"),fmt(value.gpu_seconds)+" / "+fmt(value.fixed_seconds)],
          [t("カウンタ取得済み時間率","Counter-covered time share"),(100*value.coverage_fraction).toFixed(1)+"%"],
          [t("トレース区間 / 通常実行区間","Trace / normal computation"),fmt(value.trace_to_normal_ratio)+"×"]
        ]),el("p",t("誤差は評価結果であり、モデル入力には使っていません。未分類時間等の据え置きは仮定で、正確さの保証ではありません。",
          "Error is an evaluation output, never a predictor input. Holding unknown components fixed is an assumption, not an accuracy guarantee."))];
      const kernels=el("details");kernels.append(el("summary",t("カーネル別の予測内訳","Per-kernel prediction")),
        table([t("カーネル / 形状","Kernel / shape"),t("予測元の秒数","Baseline seconds"),t("予測秒数","Predicted seconds")],
          value.kernels.map(k=>[k.name+" / "+k.grid.join("×")+" / "+k.block.join("×"),fmt(k.baseline_seconds),fmt(k.seconds)])));
      content.push(kernels,link(t("予測元の通常実行・カウンタ・再現情報","Source normal runs, counters and reproducibility"),href(view.cases.find(v=>v.id===row.case_id),"runtime-kernel-study")));
      content.push(table([t("モデル入力","Model input"),t("予測元","Source"),t("対象機","Target")],
        Object.keys(value.source_spec).map(key=>[key,String(value.source_spec[key]),String(value.target_spec[key])])),
        button(t("計算入力をJSONで取得","Download model inputs as JSON"),()=>{
          const sourceStudy=data.application_studies.find(s=>s.id===row.study_id);
          const inputs={model:value.model,model_sha256:study.model_sha256,
            run:sourceStudy.runs.find(r=>r.machine_id===row.baseline),source_spec:value.source_spec,target_spec:value.target_spec,
            expected_seconds:value.seconds,target_application_timings_used:false};
          const url=URL.createObjectURL(new Blob([JSON.stringify(inputs,null,2)],{type:"application/json"}));
          const a=el("a");a.href=url;a.download=row.case_id+"-"+value.model+".json";a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
        }));
      dialog(local(row,"name")+" · "+local(method,"name"),content);
    };
    const tableNode=el("table");tableNode.className="analytical-results";
    const head=el("thead"),hr=el("tr");
    [t("評価ケース","Case"),t("実測と予測（秒）","Measured and predicted seconds"),t("値 / 相対誤差","Values / relative error")].forEach(v=>{const h=el("th",v);h.scope="col";hr.append(h);});head.append(hr);
    const body=el("tbody");
    for(const row of rows) {
      const tr=el("tr");tr.dataset.caseId=row.case_id;
      const title=el("th");title.scope="row";title.append(link(local(row,"name"),href(view.cases.find(v=>v.id===row.case_id))),
        el("small",machine(row.baseline).name+" → "+machine(row.target).name));
      const plotCell=el("td"),plot=el("div");plot.className="analytical-bars";
      const max=Math.max(row.observed_seconds,...row.predictions.map(p=>p.seconds))*1.1;
      const observed=button(t("実測","Measured")+": "+fmt(row.observed_seconds)+" s",()=>{
        const r=view.results.find(r=>r.case_id===row.case_id&&r.machine_id===row.target&&r.kind==="measured");
        if(r)evidence(r,view.cases.find(c=>c.id===row.case_id));
      });observed.className="analytical-bar observed";observed.style.height=(row.observed_seconds/max*100)+"%";
      observed.title=observed.textContent;observed.setAttribute("aria-label",observed.textContent);
      observed.replaceChildren(el("span",t("実測","Measured")));plot.append(observed);
      const values=el("td");values.append(el("div",t("実測：","Measured: ")+fmt(row.observed_seconds)+" s"));
      row.predictions.forEach((value,index)=>{
        const method=study.methods.find(m=>m.id===value.model);
        const label=local(method,"name")+": "+fmt(value.seconds)+" s ("+value.error_percent.toFixed(1)+"%)";
        const bar=button(label,()=>explain(row,value));bar.className="analytical-bar predicted model-"+index;
        bar.style.height=(value.seconds/max*100)+"%";bar.title=label;bar.setAttribute("aria-label",label);
        bar.replaceChildren(el("span",[t("従来","Control"),t("資源比","Ratio"),t("階層","Hierarchy"),t("残余保持","Residual")][index]));
        plot.append(bar);const line=el("div");line.append(button(label,()=>explain(row,value)));values.append(line);
      });
      plotCell.append(plot);tr.append(title,plotCell,values);body.append(tr);
    }
    tableNode.append(head,body);const wrap=el("div");wrap.className="table-wrap";wrap.append(tableNode);panel.append(wrap);
    const methods=el("details");methods.append(el("summary",t("定式化・技術的根拠・限界","Formulas, technical basis and limitations")));
    for(const m of study.methods)methods.append(el("h4",local(m,"name")),el("p",m.formula),el("p",local(m,"note")));
    const limits=el("ul");study["limitations_"+language].forEach(l=>limits.append(el("li",l)));methods.append(limits);
    study.source_urls.forEach(url=>methods.append(el("p"),link(new URL(url).hostname+new URL(url).pathname,url)));
    panel.append(methods);
    const calibration=el("details");calibration.append(el("summary",t("独立ハードウェア測定・再現レシピ","Independent hardware probes and recipes")),
      el("p",t("L2とHBMの値は、通常実行の転送速度に、別のカウンタ実行で得た実転送量／論理転送量を掛けた値です。アプリごとに合わせた係数ではありません。",
                 "L2/HBM rates combine ordinary-run throughput with actual/logical traffic measured in a separate counter run. This is measured traffic accounting, not application-specific fitting.")),
      table([t("機器","Device"),"FP64 TFLOP/s","FP32 TFLOP/s","HBM GB/s","L2 GB/s",t("確認日","Captured")],
        Object.entries(study.calibrations).map(([mid,v])=>[machine(mid).name,...["fp64","fp32","bandwidth","cache_bandwidth"].map(k=>fmt(v.rates[k])),v.captured_at])));
    for(const recipe of study.recipes) {
      const entry=el("details"),pre=el("pre");pre.append(el("code",recipe.content));
      entry.append(el("summary",recipe.name),el("p","SHA-256: "+recipe.sha256),pre);calibration.append(entry);
    }panel.append(calibration);
    const transfer=transferPanel(c,explain);if(transfer)panel.append(transfer);
    const future=el("details");future.append(el("summary",t("1・2世代前からの予測：公表仕様によるリソース比","One-/two-prior-generation predictions: catalog resource ratio")),
      el("p",t("下表は階層実測校正ではなく、公表仕様のみを使う式です。対象機の実効値を測れない場合にも算定できますが、CPU・キャッシュ等の不確実性は残ります。",
                 "These use catalog specifications, not target-hardware calibration. They can be evaluated without target probes but leave CPU/cache and other uncertainty unresolved.")),
      table([t("ケース","Case"),t("対象機","Target"),t("予測元","Source"),t("予測秒数","Predicted seconds")],
        study.forecasts.filter(r=>rows.some(x=>x.case_id===r.case_id)).map(r=>[
          local(rows.find(x=>x.case_id===r.case_id),"name"),machine(r.target).name,
          String(r.generation_offset)+t("世代前："," generation(s) prior: ")+(r.baseline?machine(r.baseline).name:t("データ待ち","Awaiting data")),
          r.seconds===null?t("未算定","Unavailable"):fmt(r.seconds)
    ])));panel.append(future);return panel;
  }
  function transferPanel(c,explain) {
    const study=data.transfer_study;if(!study)return null;
    const rows=study.results.filter(r=>!c||r.case_id===c.id);
    const panel=el("section");panel.id="runtime-transfer-validation";
    panel.append(el("h4",t("CPU・接続条件を考慮した予測元の比較","Source comparison accounting for CPU and host-link conditions")),
      el("p",t("全ケースで同じ階層リソース比・通常時間基準の残余保持式を比較。CPU命令体系とCPU–GPU接続方式が一致する予測元を明示し、異なる構成からの予測も残します。誤差を使って式や予測元を選びません。",
        "Every case compares the same hierarchical ratio and normal-time residual formulas. Sources matching CPU ISA and host-to-GPU link class are identified; other configurations remain visible. Target error does not select formulas or sources.")));
    const results=table([t("ケース・予測元","Case / source"),t("実測と予測（秒）","Measured / predicted seconds"),t("結果・構成条件","Result / configuration")],rows.flatMap(row=>{
      if(!row.candidates.length)return [[local(row,"name")+" / "+row.generation_offset+t("世代前"," generations prior"),t("未算定","Unavailable"),t("対応する実測・プロファイル待ち","Awaiting matched measurements and profiles")]];
      const max=Math.max(row.observed_seconds,...row.candidates.flatMap(v=>[v.seconds,v.residual_prediction.seconds]))*1.1;
      return row.candidates.map(v=>{
        const title=el("div");title.append(link(local(row,"name"),href(view.cases.find(x=>x.id===row.case_id))),
          el("small",machine(v.baseline).name+" → "+machine(row.target).name));
        const plot=el("div");plot.className="analytical-bars";
        const observed=button(t("実測","Measured")+": "+fmt(row.observed_seconds)+" s",()=>{
          const r=view.results.find(x=>x.case_id===row.case_id&&x.machine_id===row.target&&x.kind==="measured");
          if(r)evidence(r,view.cases.find(x=>x.id===row.case_id));
        });observed.className="analytical-bar transfer-measured";observed.style.height=(row.observed_seconds/max*100)+"%";
        observed.title=observed.textContent;observed.setAttribute("aria-label",observed.textContent);observed.replaceChildren(el("span",t("実測","Measured")));plot.append(observed);
        const value={...v,model:"hierarchical-resource-ratio"};
        const open=()=>explain({...row,baseline:v.baseline},value);
        const predicted=button(t("予測","Predicted")+": "+fmt(v.seconds)+" s",open);
        predicted.className="analytical-bar transfer-predicted";predicted.style.height=(v.seconds/max*100)+"%";
        predicted.title=predicted.textContent;predicted.setAttribute("aria-label",predicted.textContent);predicted.replaceChildren(el("span",t("階層比","Ratio")));plot.append(predicted);
        const residual={...v.residual_prediction,model:"normal-residual-hierarchy",source_spec:v.source_spec,target_spec:v.target_spec};
        const openResidual=()=>explain({...row,baseline:v.baseline},residual);
        const rb=button(t("残余保持","Residual")+": "+fmt(residual.seconds)+" s",openResidual);
        rb.className="analytical-bar transfer-predicted model-3";rb.style.height=(residual.seconds/max*100)+"%";
        rb.title=rb.textContent;rb.setAttribute("aria-label",rb.textContent);rb.replaceChildren(el("span",t("残余保持","Residual")));plot.append(rb);
        const details=el("div");details.append(button(t("階層比：","Ratio: ")+fmt(v.seconds)+" s / "+v.error_percent.toFixed(1)+"%",open),
          button(t("残余保持：","Residual: ")+fmt(residual.seconds)+" s / "+residual.error_percent.toFixed(1)+"%",openResidual),
          el("small",v.configuration_match?t("CPU命令体系・接続方式が一致","CPU ISA / host-link match"):t("CPU命令体系・接続方式が異なる","CPU ISA / host-link mismatch")),
          el("small",t("据え置き時間率：","Fixed-time share: ")+(100*v.fixed_fraction).toFixed(1)+"%"));
        return [title,plot,details];
      });
    }));results.classList.add("transfer-results");panel.append(results);
    const diagnostic=el("details");diagnostic.append(el("summary",t("メモリ移動の診断と通常実行の内訳","Memory-movement diagnostics and native normal-run timers")),
      el("p",t("診断の件数・転送量は別のプロファイル実行のcompute区間です。CPUイベント数とGPUフォールト数は異なる指標で、通常実行時間への加算はできません。欠測は0として扱いません。",
        "Counts and bytes cover the compute range in separate diagnostic processes. CPU events and GPU fault counts are different metrics, not additive normal-runtime components. Missing observations are not zero.")));
    const selected=study.diagnostics.filter(d=>!c||d.case_id===c.id);
    diagnostic.append(table([t("ケース / 機器","Case / device"),t("通常の主要計算（秒）","Normal compute (s)"),t("診断 / 通常時間比","Diagnostic / normal"),t("CPU faultイベント","CPU fault events"),t("GPU faults","GPU faults"),t("移動量（MB）","Migration (MB)")],selected.map(d=>[
      local(view.cases.find(x=>x.id===d.case_id),"title")+" / "+machine(d.machine_id).name,fmt(d.normal_compute_seconds),fmt(d.window_seconds/d.normal_compute_seconds)+"×",
      d.cpu_fault_events===null?t("未取得","Missing"):String(d.cpu_fault_events),d.gpu_faults===null?t("未取得","Missing"):String(d.gpu_faults),fmt(d.migration_bytes/1e6)
    ])));
    diagnostic.append(el("p",t("内蔵タイマーは通常実行の値です。入れ子を含むため合計せず、原因を調べる手掛かりとして使います。",
      "Native timers below come from normal execution. They can be nested: do not sum them; use them as diagnostic evidence.")),
      table([t("機器","Device"),t("最小化（秒）","Minimization (s)"),t("直交化（秒）","Gram-Schmidt (s)"),t("部分空間対角化（秒）","Subspace diagonalization (s)")],selected.filter(d=>Object.keys(d.native_timers).length).map(d=>[
        machine(d.machine_id).name,...["Minimization","Gram Schmidt","subspace-diag."].map(k=>d.native_timers[k]===undefined?t("未取得","Missing"):fmt(d.native_timers[k]))
      ])));
    panel.append(diagnostic);
    const limitations=el("details");limitations.append(el("summary",t("構成条件・限界・診断レシピ","Configuration, limitations and diagnostic recipes")),
      table([t("機器","Device"),"CPU","ISA",t("CPU–GPU接続","Host-to-GPU link")],Object.entries(study.hosts).map(([mid,h])=>[machine(mid).name,h.cpu_model,h.cpu_isa,h.host_gpu_link])));
    const list=el("ul");study["limitations_"+language].forEach(l=>list.append(el("li",l)));limitations.append(list);
    study.source_urls.forEach(url=>limitations.append(el("p"),link(new URL(url).hostname+new URL(url).pathname,url)));
    for(const r of study.recipes){const entry=el("details"),pre=el("pre");pre.append(el("code",r.content));entry.append(el("summary",r.name),el("p","SHA-256: "+r.sha256),pre);limitations.append(entry);}
    panel.append(limitations);return panel;
  }
  function render(lang) {
    language=lang;root.replaceChildren();
    const p=params(),requested=view.cases.find(c=>c.id===p.get("case"));
    const app=apps.find(a=>a.application_id===p.get("app"));
    const measuredCases=new Set(view.results.filter(r=>r.kind==="measured").map(r=>r.case_id));
    const c=requested || (app ? (view.cases.find(c=>c.application_id===app.application_id&&measuredCases.has(c.id)) || view.cases.find(c=>c.application_id===app.application_id)) : null);
    document.getElementById("legacy-device-reference").hidden=!c;
    root.append(el("p",t("通常実行の秒数。塗りつぶし＝実測、点線枠＝予測。色＝初期化・主要計算・終了処理。未算定はゼロではありません。","Normal-run seconds. Solid bars: measured; dashed outlines: predicted. Colors: initialization, computation, finalization. Unavailable does not mean zero.")));
    root.append(el("p",local(view.generation_policy,"note")));
    const analysis=analyticalPanel(c);
    if(analysis)root.append(link(t("定式化モデルの比較検証へ","Analytical model comparison"),href(c,"runtime-analytical-models")));
    const legend=el("div");legend.className="runtime-legend";
    ["initialization","compute","finalization","update"].forEach(key=>{const item=el("span",phaseName(key));item.className="legend-"+key;legend.append(item);});root.append(legend);
    if(c) detail(c);
    else {
      root.append(el("p",t("機器列は世代順で共通です。同世代内の列順は性能順位ではありません。各行は同一条件・同一計測区間で比較し、行間で尺度は異なります。","Shared machine columns follow generation order, not performance rank within a generation. Comparisons use matching conditions and timing boundaries within each row; scales differ across rows.")));
      const available=new Set(view.results.map(r=>r.case_id));
      const ordered=[...view.cases].sort((a,b)=>Number(available.has(b.id))-Number(available.has(a.id)));
      root.append(chart(ordered,false));
    }
    if(analysis)root.append(analysis);
    specificationPanel();
    focusAnchor();
  }
  window.addEventListener("hashchange",focusAnchor);
  window.OpenFSRuntime={render,focusAnchor};
})();
