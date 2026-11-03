(() => {
  "use strict";
  const artifact = window.OPENFS_PUBLIC_DATA.application_device_comparison?.accelerator_targets;
  const selected = new Map();
  const virtual = {fp64: "288", fp32: "315", bandwidth: "23300"};
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
      const title = node("th", field(request, "title")); title.scope = "row";
      const provenance = request.calculation_inputs?.provenance;
      if (provenance) {
        const code = node("a", provenance.source_commit || (language === "ja" ? "commit不明" : "Unknown commit"));
        if (/^https:\/\/github\.com\//.test(provenance.source_url || "")) {code.href=provenance.source_url;code.rel="noopener noreferrer";}
        title.append(node("small", language === "ja" ? "使用コード / commit" : "Application code / commit"), code);
      }
      row.append(title);
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
        const model = node("a", artifact.model_version || artifact.model_contract.method_id);
        model.href=`models/sampled-roofline-typed-v1/?lang=${language}`; model.className="accelerator-model-version";
        cell.append(node("small")); cell.lastChild.append(model);
        if (request.calculation_inputs) {
          const calculation = node("details"); calculation.className="accelerator-calculation";
          const calculationSummary=node("summary", language === "ja" ? " — パラメータと算術" : " — parameters and arithmetic");
          const valueElement=cell.querySelector("strong");if(valueElement) calculationSummary.prepend(valueElement);
          calculation.append(calculationSummary);
          const spec={fp64:target.fp64_tflops,fp32:target.fp32_tflops,bandwidth:target.bandwidth_scenarios.find(s=>s.id===result.scenario_id).bandwidth_gbs};
          let calculated;
          try {calculated=window.OpenFSVirtualGPU.predict(request.calculation_inputs,spec);}
          catch(error) {calculated={unavailable:error.message};}
          calculation.append(node("pre", JSON.stringify({model_version:artifact.model_version,model_source_sha256:artifact.model_source_sha256,
            units:{fp64:"TFLOP/s",fp32:"TFLOP/s",bandwidth:"GB/s",fp64_ops:"FLOP",fp32_ops:"FLOP",hbm_bytes:"byte",profiled_nanoseconds:"ns",time:"s"},
            baseline_spec:request.calculation_inputs.baseline_spec,target_spec:spec,input_sha256:request.input_sha256,forecast_inputs_sha256:result.forecast_inputs_sha256,
            phases:request.calculation_inputs.phases,provenance:request.calculation_inputs.provenance,calculation:calculated},null,2)));
          cell.append(calculation);
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
      toolbar, frame(specs, w.device), frame(forecasts, w.predicted), virtualPanel(language, artifact, frame, table), evidence);
  }
  function virtualPanel(language, artifact, frame, table) {
    const ja=language==="ja", root=node("section");root.id="virtual-gpu-model";
    root.append(node("h4",ja?"仮想GPU：同じモデルで再計算":"Virtual GPU: recompute with the same model"),
      node("p",ja?"入力は1 GPUの理論vector性能とHBM帯域です。空の精度別ピークは不明。単位は十進。メモリ容量・L2帯域・通信はこの式の入力ではなく、適合や実装を保証しません。推定できるのは根拠のある4短時間ケースのみです。":"Enter theoretical vector peaks and HBM bandwidth for one GPU. Blank precision peaks mean unknown. Units are decimal. Memory capacity, L2 bandwidth and communication are not inputs to this equation; fit and implementation are not guaranteed. Only four evidenced short cases can be estimated."));
    const form=node("form");form.className="accelerator-toolbar";
    const fields={};
    for (const [key,title] of [["fp64","FP64 vector (TFLOP/s)"],["fp32","FP32 vector (TFLOP/s)"],["bandwidth","HBM bandwidth (GB/s)"]]) {
      const label=node("label",title),input=node("input");input.type="number";input.step="any";input.min="0";input.value=virtual[key];input.id="virtual-gpu-"+key;input.setAttribute("aria-label",title);input.style.maxWidth="12rem";label.htmlFor=input.id;label.append(input);form.append(label);fields[key]=input;
    }
    const submit=node("button",ja?"再計算":"Recalculate");submit.type="submit";form.append(submit);
    const output=node("div");output.setAttribute("aria-live","polite");
    const update=()=>{
      output.replaceChildren();const spec={};
      try {
        for (const key of Object.keys(fields)) {virtual[key]=fields[key].value;spec[key]=fields[key].value.trim()===""?null:Number(fields[key].value);}
        window.OpenFSVirtualGPU.validateSpec(spec);
        const resultTable=table([ja?"入力":"Input",ja?"条件付き推定 / 仮定感度 (s)":"Conditional estimate / assumption sensitivity (s)"]);
        for (const request of artifact.requests) {
          const row=node("tr"),title=node("th",request["title_"+language]);title.scope="row";const cell=node("td");
          try {
            if (!request.calculation_inputs) throw Error(ja?"モデル入力不足":"Model inputs unavailable");
            const value=window.OpenFSVirtualGPU.predict(request.calculation_inputs,spec);
            cell.append(node("strong",value.seconds.toFixed(6)+" s"),node("small",value.minimum.toFixed(6)+"–"+value.maximum.toFixed(6)+" s"));
            const detail=node("details");detail.append(node("summary",ja?"実パラメータ・算術":"Actual parameters and arithmetic"),node("pre",JSON.stringify({model_version:artifact.model_version,target_spec:spec,baseline_spec:request.calculation_inputs.baseline_spec,input_sha256:request.input_sha256,phases:request.calculation_inputs.phases,...value},null,2)));cell.append(detail);
          } catch(error) {cell.append(node("span",(ja?"推定不可: ":"Unavailable: ")+error.message));}
          row.append(title,cell);resultTable.tBodies[0].append(row);
        }
        for(const app of ["SCALE-LETKF","E-Wave","FrontFlow/blue","HPL","HPCG"]) {
          const row=node("tr"),title=node("th",app);title.scope="row";
          row.append(title,node("td",ja?"推定不可：この式へ結び付いたsourceカウンタ・排他的トレース・通常phase入力が未提供。別モデルの数値は流用しません。":"Unavailable: no source counter, exclusive trace and normal-phase input bound to this formula. Values from another model are not reused."));
          resultTable.tBodies[0].append(row);
        }
        output.append(frame(resultTable,ja?"仮想GPU予測":"Virtual GPU forecasts"));
      } catch(error) {output.append(node("p",(ja?"入力エラー: ":"Invalid input: ")+error.message));}
    };
    form.addEventListener("submit",event=>{event.preventDefault();update();});
    for(const input of Object.values(fields)) input.addEventListener("input",update);
    root.append(form,output,node("p",artifact["caveat_"+language]));update();return root;
  }
  window.OpenFSAcceleratorForecasts = {render};
})();
