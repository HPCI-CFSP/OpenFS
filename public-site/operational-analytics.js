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
      navOverview: "概要", navCatalog: "調査カタログ", navOperational: "実運用分析", navRoadmaps: "ロードマップ", navScenarios: "システム整備計画案", navReports: "報告書", navGlossary: "専門用語", navSearch: "検索",
      kicker: "開示制御済みの実運用分析", provisional: "暫定結果", consensus: "Consensus未完了", scope: "富岳の単一環境", footer: "HPCI-CFSP 公開調査ビュー",
      boundary: "公開値は最小セル10件、5単位丸めを適用しています。個人・課題・ジョブの識別子、自由記述、実行パス、行単位データは含みません。",
      methodologyKicker: "測定契約", methodologyTitle: "観測範囲と指標定義", channelTitle: "観測方式別の対象範囲", channelEvidenceTitle: "実行形式・依存情報の月次観測範囲", metricDefinitionTitle: "指標の定義", comparisonTitle: "基盤間比較の成立条件", channel: "観測方式", observedScope: "観測対象", detectionLimit: "この観測だけでは分からないこと", evidenceScope: "現在の根拠範囲", metricPopulation: "対象母集団", numerator: "分子", denominator: "分母", deduplication: "重複排除", timeBasis: "時間基準", exclusions: "除外規則", overlapRule: "重複の扱い", requiredDimensions: "比較時に一致させる項目", availableSystems: "現在の対象基盤", progress: "今回までの対応", status: "状態", dynamicLinkMetadata: "動的リンク情報あり", fileClassified: "実行形式分類あり", staticSignal: "静的実行形式信号", dynamicSignal: "動的実行形式信号", interpreterSignal: "インタープリタ／スクリプト信号", unclassifiedSignal: "実行形式未分類",
      gapKicker: "未確認事項", gapTitle: "未確認事項", details: "月次推移を表示", month: "月", jobs: "ジョブ数", totalJobs: "全ジョブ数", mappedJobs: "対応ジョブ数", mappingCoverage: "対応率", mappingCoverageHistory: "共有ライブラリ観測の月次対応率", windowJobs: "月別ユニークジョブ観測数の合計", share: "対応ジョブ比率", category: "分類", software: "ソフトウェア", trend: "傾向", prior: "直前期間", current: "直近期間", signal: "観測名", version: "版", confidence: "推定確度", nodeScale: "ノード規模", nodeSeconds: "割当ノード秒", counter: "カウンタ", coverage: "取得率", dataset: "集計領域", availableMonths: "利用可能な完全月", availablePeriod: "利用可能期間", valuesWithheld: "数値は定義確認中", requirement: "要件候補", basis: "観測根拠", planningAction: "計画上の扱い", validationCondition: "検証条件", priority: "優先度", procurementUse: "調達判断での利用", relatedGaps: "関連する未確認事項", gapClosure: "解消に必要な根拠", nextAction: "次の行動", noValue: "抑制／未確認", replacementTitle: "置換の可能性を示す信号", replacementNote: "同じ分類で減少傾向と増加傾向が同時に観測された組合せです。置換の因果関係を示すものではありません。", emergingApps: "増加・新規観測されたアプリケーション候補", decliningApps: "利用比率が低下したアプリケーション候補", appTrendNote: "観測メタデータの変化を示す信号であり、将来需要や他ソフトウェアへの置換を断定するものではありません。", aiNotObserved: "AI関連ソフトウェアは、この期間の動的リンク観測では確認できませんでした。未利用を意味するものではありません。",
      expanding: "増加", newlyObserved: "新規観測", stable: "横ばい", declining: "減少", insufficient: "証拠不足", low: "低", medium: "中", high: "高", coverageGap: "要追加確認", open: "未解消", partiallyAddressed: "一部対応", resolved: "解消", observedPartially: "一部観測", observed: "観測済み", notObserved: "未観測", defined: "定義済み", definitionReview: "定義確認中", singleSystemOnly: "単一基盤のみ", partial: "一部", complete: "完了", available: "観測あり", sourceDataUnavailable: "元データ未収録", candidateOnly: "要件候補としてのみ使用", notUntilValidated: "検証完了まで使用不可"
    },
    en: {
      publicOnly: "Public aggregates only", siteUpdated: "Updated", home: "OpenFS", breadcrumb: "Operational analysis",
      navOverview: "Overview", navCatalog: "Research catalog", navOperational: "Operational analysis", navRoadmaps: "Roadmaps", navScenarios: "System planning options", navReports: "Reports", navGlossary: "Glossary", navSearch: "Search",
      kicker: "PRIVACY-CONTROLLED OPERATIONAL ANALYSIS", provisional: "Provisional", consensus: "Consensus incomplete", scope: "One Fugaku environment", footer: "HPCI-CFSP public research view",
      boundary: "Published values apply a minimum cell size of 10 and rounding to 5. No person, project, or job identifiers, free text, execution paths, or row-level records are included.",
      methodologyKicker: "MEASUREMENT CONTRACT", methodologyTitle: "Observation coverage and metric definitions", channelTitle: "Coverage by observation channel", channelEvidenceTitle: "Monthly coverage of executable and dependency signals", metricDefinitionTitle: "Metric definitions", comparisonTitle: "Cross-system comparison requirements", channel: "Observation channel", observedScope: "What is observed", detectionLimit: "What this channel cannot establish", evidenceScope: "Current evidence scope", metricPopulation: "Population", numerator: "Numerator", denominator: "Denominator", deduplication: "Deduplication", timeBasis: "Time basis", exclusions: "Exclusions", overlapRule: "Overlap handling", requiredDimensions: "Dimensions that must agree", availableSystems: "Systems currently available", progress: "Progress to date", status: "Status", dynamicLinkMetadata: "Dynamic-link metadata", fileClassified: "File classification", staticSignal: "Static-executable signal", dynamicSignal: "Dynamic-executable signal", interpreterSignal: "Interpreter/script signal", unclassifiedSignal: "Unclassified executable",
      gapKicker: "LIMITATIONS", gapTitle: "Coverage Gaps", details: "Show monthly trend", month: "Month", jobs: "Jobs", totalJobs: "All jobs", mappedJobs: "Mapped jobs", mappingCoverage: "Coverage", mappingCoverageHistory: "Monthly shared-library observation coverage", windowJobs: "Sum of monthly unique-job observations", share: "Mapped-job share", category: "Category", software: "Software", trend: "Trend", prior: "Prior window", current: "Current window", signal: "Observed name", version: "Version", confidence: "Inference confidence", nodeScale: "Node scale", nodeSeconds: "Allocated node-seconds", counter: "Counter", coverage: "Coverage", dataset: "Aggregate area", availableMonths: "Complete months available", availablePeriod: "Available period", valuesWithheld: "Values withheld pending definition review", requirement: "Candidate requirement", basis: "Observed basis", planningAction: "Planning use", validationCondition: "Validation condition", priority: "Priority", procurementUse: "Procurement use", relatedGaps: "Related coverage gaps", gapClosure: "Evidence required for closure", nextAction: "Next action", noValue: "suppressed / unverified", replacementTitle: "Possible replacement signals", replacementNote: "Pairs combine a declining and an expanding family in the same category. They do not establish a causal replacement.",
      expanding: "expanding", newlyObserved: "newly observed", stable: "stable", declining: "declining", insufficient: "insufficient evidence", low: "low", medium: "medium", high: "high", coverageGap: "coverage gap", open: "open", partiallyAddressed: "partially addressed", resolved: "resolved", observedPartially: "partially observed", observed: "observed", notObserved: "not observed", defined: "defined", definitionReview: "definition under review", singleSystemOnly: "one system only", partial: "partial", complete: "complete", available: "observed", sourceDataUnavailable: "source data unavailable", candidateOnly: "candidate requirements only", notUntilValidated: "not usable until validated", emergingApps: "Expanding and newly observed application signals", decliningApps: "Application signals with declining use share", appTrendNote: "These are changes in observed metadata, not forecasts of future demand or proof of replacement by another package.", aiNotObserved: "No AI-related software was found in dynamic-link observations for this period. This does not establish non-use."
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
    headers.forEach((header) => {
      const cell = td(header, true);
      cell.scope = "col";
      headRow.append(cell);
    });
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

  function procurementUseLabel(name) {
    return text({"candidate-only": "candidateOnly", "not-until-validated": "notUntilValidated"}[name] || "noValue");
  }

  function statusLabel(name) {
    return text({
      "partially-addressed": "partiallyAddressed", resolved: "resolved", open: "open",
      "observed-partially": "observedPartially", observed: "observed", "not-observed": "notObserved",
      defined: "defined", "definition-review": "definitionReview", "single-system-only": "singleSystemOnly",
      partial: "partial", complete: "complete", available: "available",
      "source-data-unavailable": "sourceDataUnavailable"
    }[name] || "noValue");
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
    if (data.mapping_coverage_monthly?.length) {
      container.append(
        element("h4", "", text("mappingCoverageHistory")),
        table(
          [text("month"), text("totalJobs"), text("mappedJobs"), text("mappingCoverage")],
          data.mapping_coverage_monthly.map((row) => [
            row.month,
            value(row.total_jobs),
            value(row.mapped_jobs),
            row.coverage_pct === null ? text("sourceDataUnavailable") : `${row.coverage_pct}%`
          ])
        )
      );
    }
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
      const signalLabel = [signal.name, signal.version].filter(Boolean).join(" ");
      details.append(element("summary", "", `${signalLabel}: ${text("details")}`));
      details.append(table([text("month"), text("jobs"), text("share")], visible.map((row) => [row.month, value(row.unique_jobs), row.mapped_job_share_pct === null ? text("noValue") : `${row.mapped_job_share_pct}%`])));
      container.append(details);
    });
  }

  function renderPerformance(container, data) {
    const percentage = (number) => number == null ? text("noValue") : `${number}%`;
    const months = data.window_months;
    const period = months.length ? `${months[0].slice(0, 7)} - ${months[months.length - 1].slice(0, 7)} (${months.length}${language === "ja" ? "か月" : " months"})` : text("noValue");
    container.append(element("p", "operational-window", period));
    if (data.missing_months?.length) {
      container.append(element("p", "operational-note", `${language === "ja" ? "欠測月" : "Missing months"}: ${data.missing_months.join(", ")}`));
    }
    container.append(element("p", "operational-note", localized(data, "interpretation")));
    container.append(table(
      [text("nodeScale"), text("windowJobs"), language === "ja" ? "ステップ構成比" : "Step share", text("nodeSeconds"), language === "ja" ? "割当ノード時間構成比" : "Allocated node-time share"],
      data.node_scale_distribution.map((row) => [row.node_count_bin, value(row.monthly_bin_job_observations ?? row.unique_jobs), percentage(row.step_share_pct), value(row.allocated_node_seconds), percentage(row.node_time_share_pct)])
    ));
    if (data.queue_wait_monthly?.length) {
      container.append(element("h4", "", language === "ja" ? "ノード規模別の月次待ち時間" : "Monthly wait times by node scale"), element("p", "operational-note", localized(data, "queue_interpretation")));
      const details = document.createElement("details");
      details.append(element("summary", "", text("details")));
      details.append(table(
        [text("month"), text("nodeScale"), language === "ja" ? "有効標本数" : "Valid samples", "p50 (s)", "p95 (s)"],
        data.queue_wait_monthly.map((row) => [row.month, row.node_count_bin, value(row.valid_wait_samples), value(row.wait_p50_seconds), value(row.wait_p95_seconds)])
      ));
      container.append(details);
    }
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
      const metadata = element("p", "operational-note", `${text("priority")}: ${requirement.priority} | ${text("procurementUse")}: ${procurementUseLabel(requirement.procurement_use)}`);
      item.append(
        element("span", "eyebrow", requirement.requirement_id),
        element("h4", "", localized(requirement, "title")),
        metadata,
        element("strong", "", text("basis")),
        element("p", "", localized(requirement, "basis")),
        element("strong", "", text("planningAction")),
        element("p", "", localized(requirement, "planning_action")),
        element("strong", "", text("validationCondition")),
        element("p", "", localized(requirement, "validation_condition")),
        element("p", "operational-note", `${text("relatedGaps")}: ${(requirement.coverage_gap_refs || []).join(", ") || "-"}`),
        element("span", "tag", requirement.status === "coverage-gap" ? text("coverageGap") : text("provisional"))
      );
      list.append(item);
    });
    container.append(list);
  }

  function renderMethodology() {
    const methodology = artifact.methodology;
    document.getElementById("methodology-rule").textContent = localized(methodology, "interpretation_rule");
    const channels = document.getElementById("observation-channels");
    channels.replaceChildren(table(
      [text("channel"), text("status"), text("observedScope"), text("detectionLimit"), text("evidenceScope"), text("nextAction")],
      methodology.observation_channels.map((channel) => [
        localized(channel, "title"), statusLabel(channel.status), localized(channel, "observes"),
        localized(channel, "does_not_establish"), localized(channel, "evidence_scope"), localized(channel, "closure_action")
      ])
    ));

    const coverage = methodology.channel_coverage;
    channels.append(
      element("h4", "", text("channelEvidenceTitle")),
      element("p", "operational-note", localized(coverage, "interpretation")),
      table(
        [text("month"), text("status"), text("totalJobs"), text("mappedJobs"), text("mappingCoverage"), text("dynamicLinkMetadata"), text("fileClassified"), text("staticSignal"), text("dynamicSignal"), text("interpreterSignal"), text("unclassifiedSignal")],
        coverage.monthly.map((row) => [
          row.month, statusLabel(row.observation_status), value(row.total_jobs), value(row.executable_mapped_jobs),
          row.mapping_coverage_pct === null ? text("noValue") : `${row.mapping_coverage_pct}%`,
          value(row.jobs_with_dynamic_link_metadata), value(row.jobs_with_file_classification),
          value(row.jobs_with_static_executable_signal), value(row.jobs_with_dynamic_executable_signal),
          value(row.jobs_with_interpreter_or_script_signal), value(row.jobs_with_unclassified_executable)
        ])
      )
    );

    const definitions = document.getElementById("metric-definitions");
    definitions.replaceChildren();
    methodology.metric_definitions.forEach((metric) => {
      const details = document.createElement("details");
      details.className = "operational-definition";
      details.append(element("summary", "", `${localized(metric, "title")} · ${statusLabel(metric.status)}`));
      const fields = [
        ["metricPopulation", "population"], ["numerator", "numerator"], ["denominator", "denominator"],
        ["deduplication", "deduplication"], ["timeBasis", "time_basis"], ["exclusions", "exclusions"],
        ["overlapRule", "overlap_rule"]
      ];
      const list = element("dl", "operational-definition-fields");
      fields.forEach(([label, field]) => {
        const row = element("div", "");
        row.append(element("dt", "", text(label)), element("dd", "", localized(metric, field)));
        list.append(row);
      });
      details.append(list);
      definitions.append(details);
    });

    const comparison = methodology.system_comparison;
    const comparisonRoot = document.getElementById("system-comparison");
    comparisonRoot.replaceChildren();
    const summary = element("article", "operational-comparison-contract");
    summary.append(
      element("span", "tag", statusLabel(comparison.status)),
      element("p", "", localized(comparison, "comparison_rule")),
      element("p", "operational-note", localized(comparison, "adapter_requirement")),
      element("strong", "", text("availableSystems")),
      table(
        [language === "ja" ? "基盤" : "System", text("status"), language === "ja" ? "注記" : "Note"],
        comparison.available_systems.map((system) => [system.system_id, statusLabel(system.coverage_status), localized(system, "note")])
      ),
      element("strong", "", text("requiredDimensions")),
      element("p", "operational-note", comparison.required_dimensions.join(" · "))
    );
    comparisonRoot.append(summary);
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
    renderMethodology();
    const gaps = document.getElementById("coverage-gaps");
    gaps.replaceChildren();
    artifact.coverage_gaps.forEach((gap) => {
      const card = element("article", "operational-gap");
      card.append(
        element("span", "eyebrow", `${gap.gap_id} | ${statusLabel(gap.status)}`),
        element("h3", "", localized(gap, "title")),
        element("p", "", localized(gap, "effect")),
        element("strong", "", text("progress")),
        element("p", "", localized(gap, "progress")),
        element("strong", "", text("gapClosure")),
        element("p", "", localized(gap, "closure_evidence")),
        element("strong", "", text("nextAction")),
        element("p", "", localized(gap, "next_action"))
      );
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
