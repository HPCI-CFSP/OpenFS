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
    "data-io": ["データI/O", "Data I/O"],
    "application-library": ["アプリケーションのライブラリ", "Application libraries"],
    molecular: ["分子動力学", "Molecular dynamics"],
    electronic: ["電子状態・量子化学", "Electronic structure and quantum chemistry"],
    chemistry: ["ケモインフォマティクス", "Cheminformatics"],
    fluid: ["流体・連続体解析", "Fluid and continuum simulation"],
    support: ["基盤ソフトウェア・依存パッケージ", "Supporting software and dependencies"],
    unclassified: ["未分類", "Unclassified"]
  };
  // Exact identifiers, not guesses from arbitrary library substrings.
  const familyGroups = {MPI: "MPI", PMIX: "Process management", FFTW: "FFT", BLAS: "BLAS"};
  const familyCategories = {communication: "communication", "communication-runtime": "communication", numerical: "numerical", ai: "ai", programming: "programming", runtime: "runtime"};
  const appDomains = {gromacs: "molecular", lammps: "molecular", genesis: "molecular", gaussian: "electronic", abinitmp: "electronic", vasp6: "electronic", cp2k: "electronic", abinit: "electronic", "quantum-espresso": "electronic", rdkit: "chemistry", openfoam: "fluid", "openfoam-org": "fluid", fds: "fluid", "py-torch": "ai", "py-tensorflow": "ai", "py-scikit-learn": "ai"};
  const supportPackages = new Set(["netcdf-fortran", "netcdf-c", "parallel-netcdf", "hdf5", "python", "py-scipy", "py-pandas", "py-python-dateutil", "py-cycler", "py-kiwisolver", "py-pillow", "py-pyparsing", "py-pytz", "py-matplotlib", "py-numpy", "py-psutil", "fftw", "flex", "libpng", "zlib", "jasper", "ncview", "nco"]);
  function classify(row, kind) {
    if (kind === "software") return {
      category: row.category?.startsWith("ai-") ? "ai" : familyCategories[row.category] || (categories[row.category] ? row.category : "unclassified"),
      group: row.comparison_group || familyGroups[row.family_id] || row.family_id || "unclassified"
    };
    return {category: appDomains[row.name] || (supportPackages.has(row.name) ? "support" : "unclassified"), group: row.name};
  }
  function label(row, kind) { return kind === "software" ? row.title : [row.name, row.version].filter(Boolean).join(" "); }
  function atMonth(row, month) {
    if (month === "current") return row;
    const point = (row.monthly || []).find((item) => item.month === month);
    return {...row,
      current_monthly_unique_job_observations: point?.unique_jobs ?? null,
      current_mapped_job_share_pct: point?.mapped_job_share_pct ?? null,
      trend: "insufficient-evidence"
    };
  }
  function periodSelection(data, mode = "all", start = "", end = "") {
    const observed = [...new Set(data.observed_months || [])].sort();
    if (mode === "all") [start, end] = [observed[0]?.slice(0, 7), observed.at(-1)?.slice(0, 7)];
    if (mode === "current") [start, end] = [data.window?.current_months?.[0]?.slice(0, 7), data.window?.current_months?.at(-1)?.slice(0, 7)];
    const valid = (value) => typeof value === "string" && /^[1-9][0-9]{3}-(0[1-9]|1[0-2])$/.test(value);
    if (!valid(start) || !valid(end) || start > end) return {months: [], error: "invalid-period"};
    const ordinal = (value) => Number(value.slice(0, 4)) * 12 + Number(value.slice(5)) - 1;
    if (ordinal(end) - ordinal(start) > 1200) return {months: [], error: "invalid-period"};
    const months = [];
    for (let i = ordinal(start); i <= ordinal(end); i++) months.push(`${Math.floor(i / 12)}-${String(i % 12 + 1).padStart(2, "0")}-01`);
    return {months, error: null};
  }
  function atPeriod(row, data, months, mode = "all") {
    const byMonth = new Map((row.monthly || []).map((point) => [point.month, point]));
    const population = new Map((data.population_monthly || []).map((point) => [point.month, point.unique_jobs]));
    const observed = new Set(data.observed_months || []);
    const states = months.map((month) => {
      if (!observed.has(month)) return "no-coverage";
      const point = byMonth.get(month);
      return Number.isFinite(point?.unique_jobs) ? "disclosed" : point?.value_status || "unavailable";
    });
    const values = months.filter((month) => observed.has(month)).map((month) => byMonth.get(month)?.unique_jobs).filter(Number.isFinite);
    const count = values.length ? values.reduce((sum, value) => sum + value, 0) : null;
    const covered = months.filter((month) => observed.has(month));
    const denominators = covered.map((month) => population.get(month));
    const denominator = denominators.length && denominators.every(Number.isFinite) ? denominators.reduce((sum, n) => sum + n, 0) : null;
    const released = (row.monthly || []).filter((point) => Number.isFinite(point.unique_jobs)).map((point) => point.month).sort();
    let status = "unavailable";
    if (values.length) status = values.length === months.length ? "disclosed" : "partial";
    else if (states.length && states.every((state) => state === "no-coverage")) status = "no-coverage";
    else if (states.includes("below-threshold")) status = "below-threshold";
    else if (states.includes("not-observed") && !states.includes("unavailable")) status = "not-observed";
    return {...row,
      current_monthly_unique_job_observations: count,
      current_mapped_job_share_pct: count !== null && denominator > 0 ? Math.round(count / denominator * 1000) / 10 : null,
      trend: mode === "current" ? row.trend : "not-comparable",
      period_status: status,
      period_month_count: months.length,
      disclosed_month_count: values.length,
      covered_month_count: covered.length,
      suppressed_month_count: states.filter((state) => state === "below-threshold").length,
      unobserved_month_count: states.filter((state) => state === "not-observed").length,
      historical_first_month: released[0] || null,
      historical_last_month: released.at(-1) || null
    };
  }
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
  return {categories, classify, label, atMonth, periodSelection, atPeriod, systems, monthlySeries, segments};
});
