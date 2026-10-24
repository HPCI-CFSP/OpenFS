(() => {
  "use strict";
  const artifact = window.OPENFS_PUBLIC_DATA.application_gpu_measurements;
  let mode = "long";
  const node = (tag, text) => {
    const element = document.createElement(tag);
    if (text !== undefined) element.textContent = text;
    return element;
  };
  const text = {
    ja: {long: "長時間5ケース", historical: "過去の短時間ケース", workload: "アプリケーション・入力", scope: "計測区間",
      missing: "未掲載", samples: "反復値", aggregate: "旧保存集計・反復内訳未掲載", count: "掲載済みの条件別実測", download: "実測データ JSON",
      "native-compute": "主要計算区間", "native-solver": "solver / timed section", main: "main全体"},
    en: {long: "Five long-run cases", historical: "Historical short cases", workload: "Application / workload", scope: "Timer scope",
      missing: "Not available", samples: "Retained samples", aggregate: "Legacy aggregate; per-run samples not included", count: "Published case/device measurements", download: "Measured data JSON",
      "native-compute": "Native compute", "native-solver": "Solver / timed section", main: "Full main"}
  };
  function render(language) {
    const root = document.getElementById("gpu-measured-runtimes");
    if (!root || !artifact) return;
    const tr = text[language];
    const field = (name) => artifact[`${name}_${language}`];
    const cases = artifact.cases.filter((row) => row.long_run === (mode === "long"));
    const known = new Map(artifact.measurements.map((row) => [`${row.case_id}:${row.device_id}`, row]));
    const heading = node("h3", field("title"));
    const filter = node("select");
    filter.setAttribute("aria-label", language === "ja" ? "測定ケース" : "Measurement cases");
    for (const key of ["long", "historical"]) {
      const option = node("option", tr[key]); option.value = key; option.selected = mode === key; filter.append(option);
    }
    filter.addEventListener("change", () => { mode = filter.value; render(language); });
    const toolbar = node("div"); toolbar.className = "gpu-measured-toolbar";
    const link = node("a", tr.download);
    link.href = `${document.body.dataset.rootPrefix}data/application-gpu-measurements.json`;
    toolbar.append(filter, link);
    const count = cases.reduce((sum, row) => sum + artifact.devices.filter((device) => known.has(`${row.id}:${device.id}`)).length, 0);
    const coverage = node("p", `${tr.count}: ${count} / ${cases.length * artifact.devices.length} · ${artifact.as_of} · s`);
    const table = node("table"); table.className = "gpu-measurements-table";
    const caption = node("caption", tr[mode]); caption.className = "sr-only"; table.append(caption);
    const thead = node("thead"); const headers = node("tr");
    for (const name of [tr.workload, tr.scope, ...artifact.devices.map((device) => `${device.site}: ${device.name}`)]) {
      const cell = node("th", name); cell.scope = "col"; headers.append(cell);
    }
    thead.append(headers); table.append(thead);
    const tbody = node("tbody");
    for (const row of cases) {
      const line = node("tr"); line.dataset.measurementCase = row.id;
      const label = node("th"); label.scope = "row";
      label.append(node("strong", row.application), node("small", row.workload));
      line.append(label, node("td", tr[row.scope]));
      for (const device of artifact.devices) {
        const cell = node("td"); cell.dataset.measurementDevice = device.id;
        const measurement = known.get(`${row.id}:${device.id}`);
        if (!measurement) {
          cell.append(node("span", tr.missing)); cell.className = "measurement-unavailable";
        } else {
          cell.append(node("strong", measurement.seconds.toLocaleString(language, {maximumFractionDigits: 6})));
          if (measurement.samples_seconds) {
            const detail = node("details");
            detail.append(node("summary", `${tr.samples}: n=${measurement.samples_seconds.length}`),
              node("small", measurement.samples_seconds.map((value) => value.toFixed(9)).join(", ") + " s"));
            cell.append(detail);
          } else {
            cell.append(node("small", tr.aggregate));
          }
          cell.title = `Evidence SHA-256: ${measurement.evidence_sha256}`;
        }
        line.append(cell);
      }
      tbody.append(line);
    }
    table.append(tbody);
    const frame = node("div"); frame.className = "gpu-measured-scroll"; frame.tabIndex = 0;
    frame.setAttribute("role", "region"); frame.setAttribute("aria-label", field("title")); frame.append(table);
    root.replaceChildren(heading, node("p", field("summary")), toolbar, coverage, frame, node("p", field("caveat")));
  }
  window.OpenFSGpuMeasurements = {render};
})();
