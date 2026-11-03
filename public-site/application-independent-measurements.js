(() => {
  "use strict";
  const make = (tag, text) => { const node = document.createElement(tag); if (text !== undefined) node.textContent = text; return node; };
  const columns = [
    {system: "R-CCS Cloud", device: "cpu", probe: "rccs-cpu"},
    {system: "R-CCS Cloud", device: "gpu", probe: "rccs"},
    {system: "RIKEN RIKYU", device: "cpu", probe: "rikyu"},
    {system: "RIKEN RIKYU", device: "gpu", probe: "rikyu"},
    {system: "R-CCS Cloud", device: "gpu", probe: "rccs-b300"}
  ];
  const fmt = value => new Intl.NumberFormat("en", {maximumFractionDigits: 6}).format(value);
  function render(language) {
    const root = document.getElementById("application-independent-measurements");
    const data = window.OPENFS_PUBLIC_DATA?.application_independent_measurements;
    if (!root || !data) return;
    const ja = language !== "en", t = (jp, en) => ja ? jp : en;
    root.replaceChildren();
    root.append(make("h3", t("派生入力・3サイズの通常実行", "Normal runs for three derived input sizes")));
    root.append(make("p", t(
      `${data.normal_cell_count}件の通常実行記録（基本${data.base_normal_cell_count}件・追加${data.additional_normal_cohort_count}件）。ウォームアップ1回を除く5反復の中央値（秒）です。基本72セルの台帳と正式EEA1入力との一致・厳密モデル精度は別に管理しています。`,
      `${data.normal_cell_count} normal-run records (${data.base_normal_cell_count} base records and ${data.additional_normal_cohort_count} additional cohort). Values are medians of five repetitions after one excluded warm-up, in seconds. The original72-cell ledger, formal EEA1 input match and strict model accuracy remain separate.`)));
    root.append(make("p", t(
      "基本31件の機器情報は別ジョブのプラットフォーム確認に基づきます。追加B300は同じ測定ジョブの全6回の原ログで機器を確認しました。CPU実行とGPU実行、入力・ソフトウェア・計測区間の違いを各詳細に保持しています。",
      "Device descriptions for the original31 records come from independent platform probes. The additional B300 device identity was checked against all six raw logs from its own normal job. CPU/GPU executions, inputs, software and timing boundaries remain distinct.")));
    root.append(make("p", t(
      "SCALE-LETKF、E-Wave、FrontFlow/blueの受理済み通常5反復はこの追加表にはありません。制御試験やプロファイルの時間は通常実行へ算入していません。",
      "This additional table contains no admitted five-run normal cohorts for SCALE-LETKF, E-Wave or FrontFlow/blue. Controls and profiled runs are not counted as normal measurements.")));
    const download = make("a", t("通常5反復の実測データ JSON", "Five-run measured data JSON"));
    download.href = `${document.body.dataset.rootPrefix}data/application-independent-measurements.json`;
    const downloadLine = make("p"); downloadLine.append(download); root.append(downloadLine);
    const probes = new Map(data.platform_metadata.map(p => [p.id, p]));
    const scroll = make("div"); scroll.className = "runtime-scroll"; scroll.tabIndex = 0;
    scroll.setAttribute("role", "region"); scroll.setAttribute("aria-label", t("派生入力のCPU・GPU通常実行", "CPU and GPU normal runs for derived inputs"));
    const table = make("table"); table.className = "runtime-grid independent-normal-grid";
    table.append(make("caption", t("入力ごとの通常実行中央値（秒）", "Normal-run median seconds by input")));
    const head = make("thead"), headings = make("tr");
    const first = make("th", t("入力・サイズ", "Input / size")); first.scope = "col"; headings.append(first);
    for (const column of columns) {
      const th = make("th"); th.scope = "col";
      th.append(make("strong", `${column.system} · ${column.device.toUpperCase()}`));
      const probe = probes.get(column.probe);
      const description = column.device === "cpu" ? probe.cpu_model_observed : probe.gpu_name_memory_driver_observed;
      th.append(make("p", description), make("small", probe.same_job_attestation ? t("同じ測定ジョブの機器を確認", "Same-job hardware checked") : t("別ジョブの機器確認", "Independent platform probe"))); headings.append(th);
    }
    head.append(headings); table.append(head);
    const body = make("tbody");
    for (const caseItem of data.cases) {
      const tr = make("tr"), title = make("th"); title.scope = "row";
      const size = ({small: t("小", "small"), medium: t("中", "medium"), large: t("大", "large")})[caseItem.size];
      title.append(make("strong", `${caseItem.application} · ${size}`));
      const condition = make("details"); condition.append(make("summary", t("固定入力・科学的限界", "Fixed input and scientific limits")));
      const input = make("dl");
      for (const [key, value] of Object.entries(caseItem.input_description)) {
        if (key === "source_urls") continue;
        input.append(make("dt", key), make("dd", typeof value === "object" ? JSON.stringify(value) : String(value)));
      }
      condition.append(input);
      for (const urlText of caseItem.input_description.source_urls || []) {
        let url; try { url = new URL(urlText); } catch (_error) { continue; }
        if (url.protocol !== "https:") continue;
        const a = make("a", url.hostname + url.pathname); a.href = url.href; a.target = "_blank"; a.rel = "noopener noreferrer";
        const paragraph = make("p"); paragraph.append(a); condition.append(paragraph);
      }
      title.append(condition); tr.append(title);
      for (const column of columns) {
        const td = make("td");
        const record = data.measurements.find(r => r.case_id === caseItem.id && r.system === column.system && r.execution_device === column.device && r.platform_probe_id === column.probe);
        if (!record) {
          td.append(make("strong", t("未測定", "Unmeasured")), make("p", t("受理済みの通常5反復がありません。", "No admitted five-run normal cohort.")));
          tr.append(td); continue;
        }
        td.append(make("strong", `${fmt(record.median_seconds)} s`));
        const details = make("details"); details.append(make("summary", t("5反復・条件・証拠", "Five runs, conditions and evidence")));
        const samples = make("ol");
        record.normal_runs.forEach(run => {
          const li = make("li", `${run.label}: ${fmt(run.seconds)} s`);
          if (run.GS_process_wall_seconds !== undefined && run.RT_process_wall_seconds !== undefined) {
            li.append(make("small", ` GS ${fmt(run.GS_process_wall_seconds)} + RT ${fmt(run.RT_process_wall_seconds)} s`));
          }
          samples.append(li);
        }); details.append(samples);
        const facts = [
          [t("計測区間", "Timing boundary"), record.native_timing_boundary],
          [t("データ区分", "Data class"), record.data_class],
          [t("科学的限界", "Scientific limits"), record.scientific_limits],
          ["OpenMP", record.OMP_threads_observed_in_retained_plan.join(", ") || t("未確認", "Unverified")],
          ["MPI", record.MPI_ranks_observed_in_retained_plan.join(", ") || t("未確認", "Unverified")],
          [t("通常実行ジョブ", "Normal jobs"), record.measurement_job_ids.join(", ")],
          [t("保存記録の時刻（UTC）", "Retained record timestamps (UTC)"), record.accepted_result_timestamps.join(", ") || t("未確認", "Unverified")],
          [t("入力SHA-256", "Input SHA-256"), record.fixed_input_sha256],
          [t("実行物SHA-256", "Executable SHA-256"), record.executable_sha256]
        ];
        if (record.shared_node_possible) facts.push([t("割当条件", "Allocation"), t("GPU1台・割当CPU16・OMP4。共有ノードの可能性あり。", "One application GPU,16 allocated CPUs,OMP4; a shared node is possible.")]);
        const dl = make("dl"); facts.forEach(([key, value]) => dl.append(make("dt", key), make("dd", value))); details.append(dl);
        const hashes = make("details"); hashes.append(make("summary", t("証拠ダイジェスト", "Evidence digests")));
        const list = make("ul"); record.evidence.forEach(e => list.append(make("li", `${e.id}: ${e.sha256}`))); hashes.append(list); details.append(hashes);
        td.append(details); tr.append(td);
      }
      body.append(tr);
    }
    table.append(body); scroll.append(table); root.append(scroll);
  }
  window.OpenFSIndependentMeasurements = {render};
})();
