(function (root, factory) {
  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  else root.OpenFSOperationalModel = api;
})(typeof window !== "undefined" ? window : globalThis, function () {
  "use strict";
  const categories = {
    programming: ["プログラミング環境", "Programming environments"],
    numerical: ["数値計算ライブラリ", "Numerical libraries"],
    communication: ["通信ライブラリ", "Communication libraries"],
    ai: ["AI関連ソフトウェア", "AI software"],
    runtime: ["ランタイム・ツール", "Runtimes and tools"],
    molecular: ["分子動力学", "Molecular dynamics"],
    electronic: ["電子状態・量子化学", "Electronic structure and quantum chemistry"],
    chemistry: ["ケモインフォマティクス", "Cheminformatics"],
    support: ["基盤ソフトウェア・依存パッケージ", "Supporting software and dependencies"],
    unclassified: ["未分類", "Unclassified"]
  };
  // Exact identifiers, not guesses from arbitrary library substrings.
  const familyGroups = {MPI: "MPI", PMIX: "Process management", FFTW: "FFT", BLAS: "BLAS"};
  const familyCategories = {communication: "communication", "communication-runtime": "communication", numerical: "numerical", ai: "ai", programming: "programming", runtime: "runtime"};
  const appDomains = {gromacs: "molecular", gaussian: "electronic", abinitmp: "electronic", vasp6: "electronic", "quantum-espresso": "electronic", rdkit: "chemistry"};
  const supportPackages = new Set(["netcdf-fortran", "netcdf-c", "parallel-netcdf", "hdf5", "python", "py-scipy", "py-pandas", "py-python-dateutil", "py-cycler", "py-kiwisolver", "py-pillow", "py-pyparsing", "py-pytz", "py-matplotlib", "py-numpy", "py-psutil", "fftw", "flex", "libpng", "zlib", "jasper", "ncview", "nco"]);
  function classify(row, kind) {
    if (kind === "software") return {category: familyCategories[row.category] || "unclassified", group: familyGroups[row.family_id] || "unclassified"};
    return {category: appDomains[row.name] || (supportPackages.has(row.name) ? "support" : "unclassified"), group: row.name};
  }
  function label(row, kind) { return kind === "software" ? row.title : [row.name, row.version].filter(Boolean).join(" "); }
  function systems(data) {
    const artifacts = [data.operational_analytics, ...(data.additional_operational_analytics || [])].filter(Boolean);
    const items = artifacts.map((artifact) => ({
      id: artifact.system_id,
      names: artifact.system_id === "SYS-FUGAKU" ? ["富岳", "Fugaku"] : artifact.system_id === "SYS-RIKYU" ? ["理究", "Rikyu"] : [artifact.system_id, artifact.system_id],
      artifact
    }));
    if (!items.some((item) => item.id === "SYS-RIKYU")) items.push({id: "SYS-RIKYU", names: ["理究", "Rikyu"], artifact: null});
    return items;
  }
  function monthlySeries(rows, metric) {
    const observedMonths = rows.flatMap((row) => (row.monthly || []).map((point) => point.month)).sort();
    if (!observedMonths.length) return {months: [], series: []};
    const months = [];
    const date = new Date(observedMonths[0] + "T00:00:00Z");
    const last = observedMonths[observedMonths.length - 1];
    while (date.toISOString().slice(0, 10) <= last) {
      months.push(date.toISOString().slice(0, 10));
      date.setUTCMonth(date.getUTCMonth() + 1);
    }
    const key = metric === "share" ? "mapped_job_share_pct" : "unique_jobs";
    return {months, series: rows.map((row) => {
      const byMonth = new Map((row.monthly || []).map((point) => [point.month, point[key]]));
      return months.map((month) => Number.isFinite(byMonth.get(month)) ? byMonth.get(month) : null);
    })};
  }
  function segments(values) {
    const result = []; let current = [];
    values.forEach((value, index) => {
      if (value === null) { if (current.length) result.push(current); current = []; }
      else current.push([index, value]);
    });
    if (current.length) result.push(current);
    return result;
  }
  return {categories, classify, label, systems, monthlySeries, segments};
});
