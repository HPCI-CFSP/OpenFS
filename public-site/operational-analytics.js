(function () {
  "use strict";

  const rootData = window.OPENFS_PUBLIC_DATA;
  const artifact = rootData?.operational_analytics;
  if (!artifact) {
    document.body.textContent = "OpenFS operational analytics are unavailable.";
    return;
  }

  const copy = {
    ja: {
      publicOnly: "公開用集計のみ", siteUpdated: "更新", home: "OpenFS", breadcrumb: "実運用分析",
      navOverview: "概要", navCatalog: "調査カタログ", navOperational: "実運用分析", navRoadmaps: "ロードマップ", navScenarios: "システム整備計画案", navReports: "報告書", navSearch: "検索",
      kicker: "開示制御済みの実運用分析", provisional: "暫定結果", consensus: "Consensus未完了", scope: "富岳の単一環境", footer: "HPCI-CFSP 公開調査ビュー",
      boundary: "公開値は最小セル10件、5単位丸めを適用しています。個人・課題・ジョブの識別子、自由記述、実行パス、行単位データは含みません。",
      gapKicker: "未確認事項", gapTitle: "未確認事項", details: "月次推移を表示", month: "月", jobs: "ジョブ数", windowJobs: "月別ユニークジョブ観測数の合計", share: "対応ジョブ比率", category: "分類", software: "ソフトウェア", trend: "傾向", prior: "直前期間", current: "直近期間", signal: "観測名", version: "版", confidence: "推定確度", nodeScale: "ノード規模", nodeSeconds: "割当ノード秒", counter: "カウンタ", coverage: "取得率", dataset: "集計領域", availableMonths: "利用可能な完全月", availablePeriod: "利用可能期間", valuesWithheld: "数値は定義確認中", requirement: "要件候補", basis: "根拠", noValue: "抑制／未確認", replacementTitle: "置換の可能性を示す信号", replacementNote: "同じ分類で減少傾向と増加傾向が同時に観測された組合せです。置換の因果関係を示すものではありません。", emergingApps: "増加・新規観測されたアプリケーション候補", decliningApps: "利用比率が低下したアプリケーション候補", appTrendNote: "観測メタデータの変化を示す信号であり、将来需要や他ソフトウェアへの置換を断定するものではありません。", aiNotObserved: "AI関連ソフトウェアは、この期間の動的リンク観測では確認できませんでした。未利用を意味するものではありません。",
      expanding: "増加", newlyObserved: "新規観測", stable: "横ばい", declining: "減少", insufficient: "証拠不足", low: "低", medium: "中", high: "高", coverageGap: "要追加確認"
    },
    en: {
      publicOnly: "Public aggregates only", siteUpdated: "Updated", home: "OpenFS", breadcrumb: "Operational analysis",
      navOverview: "Overview", navCatalog: "Research catalog", navOperational: "Operational analysis", navRoadmaps: "Roadmaps", navScenarios: "System planning options", navReports: "Reports", navSearch: "Search",
      kicker: "PRIVACY-CONTROLLED OPERATIONAL ANALYSIS", provisional: "Provisional", consensus: "Consensus incomplete", scope: "One Fugaku environment", footer: "HPCI-CFSP public research view",
      boundary: "Published values apply a minimum cell size of 10 and rounding to 5. No person, project, or job identifiers, free text, execution paths, or row-level records are included.",
      gapKicker: "LIMITATIONS", gapTitle: "Coverage Gaps", details: "Show monthly trend", month: "Month", jobs: "Jobs", windowJobs: "Sum of monthly unique-job observations", share: "Mapped-job share", category: "Category", software: "Software", trend: "Trend", prior: "Prior window", current: "Current window", signal: "Observed name", version: "Version", confidence: "Inference confidence", nodeScale: "Node scale", nodeSeconds: "Allocated node-seconds", counter: "Counter", coverage: "Coverage", dataset: "Aggregate area", availableMonths: "Complete months available", availablePeriod: "Available period", valuesWithheld: "Values withheld pending definition review", requirement: "Candidate requirement", basis: "Basis", noValue: "suppressed / unverified", replacementTitle: "Possible replacement signals", replacementNote: "Pairs combine a declining and an expanding family in the same category. They do not establish a causal replacement.",
      expanding: "expanding", newlyObserved: "newly observed", stable: "stable", declining: "declining", insufficient: "insufficient evidence", low: "low", medium: "medium", high: "high", coverageGap: "coverage gap", emergingApps: "Expanding and newly observed application signals", decliningApps: "Application signals with declining use share", appTrendNote: "These are changes in observed metadata, not forecasts of future demand or proof of replacement by another package.", aiNotObserved: "No AI-related software was found in dynamic-link observations for this period. This does not establish non-use."
    }
  };
  let language = new URLSearchParams(window.location.search).get("lang") === "en" ? "en" : "ja";
  const text = (key) => copy[language][key] || key;
  const localized = (item, field) => item[`${field}_${language}`] || item[`${field}_ja`] || "";
  const value = (input) => input === null || input === undefined ? text("noValue") : Number(input).toLocaleString(language === "ja" ? "ja-JP" : "en-US");
  const element = (tag, className, content) => {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (content !== undefined) node.textContent = content;
    return node;
  };
  const td = (content, heading) => {
    const node = element(heading ? "th" : "td", "", content);
    if (heading) node.scope = "row";
    return node;
  };

  function table(headers, rows) {
    const wrap = element("div", "table-wrap operational-table-wrap");
    const node = document.createElement("table");
    const head = document.createElement("thead");
    const headRow = document.createElement("tr");
    headers.forEach((header) => headRow.append(td(header, false)));
    head.append(headRow);
    const body = document.createElement("tbody");
    rows.forEach((cells) => {
      const row = document.createElement("tr");
      cells.forEach((cell, index) => row.append(td(cell, index === 0)));
      body.append(row);
    });
    node.append(head, body);
    wrap.append(node);
    return wrap;
  }

  function trendLabel(name) {
    return text({expanding: "expanding", "newly-observed": "newlyObserved", stable: "stable", declining: "declining", "insufficient-evidence": "insufficient"}[name] || "insufficient");
  }

  function renderDataScope(container, data) {
    const grid = element("div", "operational-metric-grid");
    const metrics = [
      [language === "ja" ? "最新の完全月" : "Latest complete month", data.latest_complete_month],
      [language === "ja" ? "最新完全月のジョブ数" : "Jobs in latest complete month", value(data.latest_complete_month_total_jobs)],
      [language === "ja" ? "ライブラリ観測基準月" : "Library observation month", data.mapping_reference_month || text("noValue")],
      [language === "ja" ? "基準月の全ジョブ数" : "All jobs in reference month", value(data.mapping_reference_total_jobs)],
      [language === "ja" ? "基準月の対応ジョブ数" : "Mapped jobs in reference month", value(data.mapping_reference_mapped_jobs)],
      [language === "ja" ? "基準月の対応率" : "Mapping coverage in reference month", data.mapping_reference_coverage_pct === null ? text("noValue") : `${data.mapping_reference_coverage_pct}%`],
      [language === "ja" ? "ソフトウェア観測最終月" : "Software observation end", data.software_observation_end || text("noValue")]
    ];
    metrics.forEach(([label, metric]) => {
      const card = element("article", "operational-metric");
      card.append(element("span", "", label), element("strong", "", metric || text("noValue")));
      grid.append(card);
    });
    container.append(grid);
  }

  function renderSoftware(container, data) {
    const windows = element("p", "operational-window", `${text("current")}: ${data.window.current_months.join(" / ") || text("noValue")} | ${text("prior")}: ${data.window.prior_months.join(" / ") || text("noValue")}`);
    container.append(windows);
    const rows = data.families.map((family) => [
      family.title,
      family.category,
      value(family.current_monthly_unique_job_observations),
      `${family.current_mapped_job_share_pct}%`,
      trendLabel(family.trend)
    ]);
    container.append(table([text("software"), text("category"), text("windowJobs"), text("share"), text("trend")], rows));
    if (data.ai_observation_status === "not-observed-within-coverage") {
      container.append(element("p", "operational-note", text("aiNotObserved")));
    }
    data.families.forEach((family) => {
      const visible = family.monthly.filter((row) => row.unique_jobs !== null);
      if (!visible.length) return;
      const details = document.createElement("details");
      details.className = "operational-trend-detail";
      details.append(element("summary", "", `${family.title}: ${text("details")}`));
      details.append(table([text("month"), text("jobs"), text("share")], visible.map((row) => [row.month, value(row.unique_jobs), row.mapped_job_share_pct === null ? text("noValue") : `${row.mapped_job_share_pct}%`])));
      container.append(details);
    });
    if (data.replacement_signals.length) {
      container.append(element("h4", "", text("replacementTitle")), element("p", "operational-note", text("replacementNote")));
      container.append(table([text("category"), language === "ja" ? "減少側" : "Declining", language === "ja" ? "増加側" : "Expanding"], data.replacement_signals.map((row) => [row.category, row.declining_family_id, row.rising_family_id])));
    }
  }

  function renderApplications(container, data) {
    container.append(element("p", "operational-window", `${text("current")}: ${data.window.current_months.join(" / ") || text("noValue")} | ${text("prior")}: ${data.window.prior_months.join(" / ") || text("noValue")}`));
    container.append(table(
      [text("signal"), text("version"), text("windowJobs"), text("share"), text("trend"), text("confidence")],
      data.signals.map((row) => [row.name, row.version || "-", value(row.current_monthly_unique_job_observations), `${row.current_mapped_job_share_pct}%`, trendLabel(row.trend), text(row.inference_confidence)])
    ));
    const trendSummary = (titleKey, rows) => {
      if (!rows.length) return;
      container.append(element("h4", "", text(titleKey)), element("p", "operational-note", text("appTrendNote")));
      container.append(table(
        [text("signal"), text("version"), text("windowJobs"), text("share"), text("trend")],
        rows.map((row) => [row.name, row.version || "-", value(row.current_monthly_unique_job_observations), `${row.current_mapped_job_share_pct}%`, trendLabel(row.trend)])
      ));
    };
    trendSummary("emergingApps", data.emerging_signals);
    trendSummary("decliningApps", data.declining_signals);
    data.signals.forEach((signal) => {
      const visible = signal.monthly.filter((row) => row.unique_jobs !== null);
      if (!visible.length) return;
      const details = document.createElement("details");
      details.className = "operational-trend-detail";
      details.append(element("summary", "", `${signal.name}: ${text("details")}`));
      details.append(table([text("month"), text("jobs"), text("share")], visible.map((row) => [row.month, value(row.unique_jobs), row.mapped_job_share_pct === null ? text("noValue") : `${row.mapped_job_share_pct}%`])));
      container.append(details);
    });
  }

  function renderPerformance(container, data) {
    container.append(table([text("nodeScale"), text("jobs"), text("nodeSeconds")], data.node_scale_distribution.map((row) => [row.node_count_bin, value(row.unique_jobs), value(row.allocated_node_seconds)])));
    const coverageRows = Object.entries(data.counter_coverage_pct).map(([name, coverage]) => [name, coverage === null ? text("noValue") : `${coverage}%`]);
    container.append(element("h4", "", language === "ja" ? "性能カウンタ取得率" : "Performance-counter coverage"), table([text("counter"), text("coverage")], coverageRows));
  }

  function renderInfrastructure(container, data) {
    const grid = element("div", "operational-availability-grid");
    data.datasets.forEach((dataset) => {
      const card = element("article", "operational-availability");
      card.append(element("h4", "", localized(dataset, "dataset")));
      card.append(element("p", "", `${text("availableMonths")}: ${dataset.available_month_count}`));
      card.append(element("p", "", `${text("availablePeriod")}: ${dataset.period_start || "-"} - ${dataset.period_end || "-"}`));
      card.append(element("span", "tag", text("valuesWithheld")));
      grid.append(card);
    });
    container.append(grid);
  }

  function renderRequirements(container, data) {
    const list = element("div", "operational-requirement-list");
    data.requirements.forEach((requirement) => {
      const item = element("article", "operational-requirement");
      item.append(element("span", "eyebrow", requirement.requirement_id), element("h4", "", localized(requirement, "title")), element("p", "", localized(requirement, "basis")), element("span", "tag", requirement.status === "coverage-gap" ? text("coverageGap") : text("provisional")));
      list.append(item);
    });
    container.append(list);
  }

  function renderSection(section) {
    const node = element("section", "operational-section");
    node.id = section.section_id;
    const header = element("header", "operational-section-header");
    header.append(element("h2", "", localized(section, "title")), element("span", "tag", section.status === "coverage-gap" ? text("coverageGap") : text("provisional")));
    node.append(header, element("p", "operational-section-summary", localized(section, "summary")));
    const renderers = {"data-scope": renderDataScope, "system-software": renderSoftware, applications: renderApplications, performance: renderPerformance, infrastructure: renderInfrastructure, "system-requirements": renderRequirements};
    renderers[section.section_id](node, section.data);
    return node;
  }

  function render() {
    document.documentElement.lang = language;
    document.querySelectorAll("[data-copy]").forEach((node) => { node.textContent = text(node.dataset.copy); });
    document.querySelectorAll("[data-language]").forEach((button) => {
      const active = button.dataset.language === language;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    document.getElementById("public-status").textContent = text("publicOnly");
    const updated = document.getElementById("site-updated");
    updated.textContent = `${text("siteUpdated")} ${rootData.site.updated_at.replace("T", " ").slice(0, 19)}`;
    updated.href = rootData.site.commit_url;
    document.getElementById("page-title").textContent = localized(artifact, "title");
    document.getElementById("page-summary").textContent = localized(artifact, "summary");
    document.getElementById("research-status").textContent = text("provisional");
    document.getElementById("consensus-status").textContent = text("consensus");
    document.getElementById("scope-status").textContent = text("scope");
    document.getElementById("boundary-note").textContent = text("boundary");
    document.getElementById("page-caveat").textContent = localized(artifact, "caveat");
    const index = document.getElementById("section-index");
    const sections = document.getElementById("operational-sections");
    index.replaceChildren(); sections.replaceChildren();
    artifact.sections.forEach((section) => {
      const link = document.createElement("a");
      link.href = `#${section.section_id}`;
      link.textContent = localized(section, "title").replace(/^\d+[.]\s*/, "");
      index.append(link);
      sections.append(renderSection(section));
    });
    const gaps = document.getElementById("coverage-gaps");
    gaps.replaceChildren();
    artifact.coverage_gaps.forEach((gap) => {
      const card = element("article", "operational-gap");
      card.append(element("span", "eyebrow", gap.gap_id), element("h3", "", localized(gap, "title")), element("p", "", localized(gap, "effect")));
      gaps.append(card);
    });
    window.OpenFSFeedback?.mount("page-feedback", {kind: "operational-analytics", id: artifact.artifact_id, title: localized(artifact, "title"), path: "analytics/operational-workloads/"});
  }

  document.querySelectorAll("[data-language]").forEach((button) => button.addEventListener("click", () => {
    language = button.dataset.language;
    const url = new URL(window.location.href);
    url.searchParams.set("lang", language);
    history.replaceState(null, "", url);
    render();
  }));
  render();
})();
