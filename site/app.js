(function () {
  "use strict";

  const data = window.OPENFS_PUBLIC_DATA;
  if (!data) {
    document.body.textContent = "OpenFS public data is unavailable.";
    return;
  }

  const copy = {
    ja: {
      languageControl: "表示言語", tagline: "公開調査カタログと整備計画成果", publicOnly: "公開情報のみ", asOf: "基準日",
      navOverview: "概要", navCatalog: "調査カタログ", navTechnology: "技術動向", navScenarios: "整備シナリオ", navReports: "報告書",
      overviewKicker: "現在の公開状況", overviewTitle: "継続調査の現在地",
      overviewLead: "公開情報から作成した調査サマリーは検証状況とともに表示し、整備シナリオと報告書は人の公開承認を通過した成果に限定します。",
      topicsMetric: "調査Topic", topicsMetricNote: "保護された初期項目を含む", scopeMetric: "調査更新",
      scopeMetricValue: "継続", scopeMetricNote: "新しい公開情報を反映", scenarioMetric: "公開シナリオ", scenarioMetricNote: "人の公開承認を通過した成果",
      reportMetric: "公開報告書", reportMetricNote: "来歴付きExport", revision: "改訂", officialSources: "登録済み公開資料",
      openGaps: "未解決Gap", none: "なし", catalogKicker: "調査項目一覧", catalogTitle: "調査カタログ",
      catalogLead: "各Topicには、公開情報から作成した調査サマリー、暫定知見、根拠資料を関連付けます。",
      domainFilter: "分野フィルタ", all: "すべて", search: "検索", searchPlaceholder: "Topic ID、名称",
      tableId: "ID", tableTopic: "調査項目", tableDomain: "分野", tableStatus: "状態", tableCadence: "更新", tableOrigin: "起点",
      noTopics: "条件に一致するTopicはありません。", technologyKicker: "継続調査対象", technologyTitle: "技術動向", technologyLead: "HPCI整備計画に関係する技術分野を継続的に調査します。", area: "領域",
      scenarioKicker: "ロードマップシナリオ", scenarioTitle: "HPCI整備シナリオ",
      scenarioLead: "Architecture、System Software、Applications、センター影響、技術動向、不確実性を一体で比較します。",
      noScenarioTitle: "公開済みシナリオはまだありません",
      noScenarioText: "現在の4案はGenerator検証用の例示です。根拠・評価・人の公開承認を通過した案だけを公開します。",
      reportKicker: "報告書", reportTitle: "報告書・Export", reportLead: "公開版には版、基準日、根拠への追跡、置換関係を付けます。",
      noReportTitle: "公開済み報告書はまだありません",
      noReportText: "Promotion workflowで受理され、人が公開を承認したExportが追加されると、ここへ自動表示されます。",
      footerDescription: "HPCI-CFSP 公開調査ビュー", originInitial: "保護された初期項目",
      originHuman: "人の指示", originAi: "AI Consensus", statusNotStarted: "未着手", statusPartial: "一部完了",
      statusReviewed: "確認済み", statusRetired: "廃止", cadenceWeekly: "週次", cadenceMonthly: "月次",
      cadenceQuarterly: "四半期", cadenceAnnual: "年次", cadenceEvent: "事象発生時",
      summaryAvailable: "公開サマリー", summaryPending: "公開サマリー未作成", closeDialog: "詳細を閉じる",
      topicDetailMeta: "Topic詳細", noSummaryTitle: "公開サマリーはまだありません",
      noSummaryText: "このTopicに紐づく調査結果はまだ公開されていません。今後の調査ループで更新されます。",
      researchOverview: "調査概要", findings: "調査で得られた知見", sources: "根拠資料", caveat: "検証状況に関する注意",
      sourceRun: "調査Run", generatedAt: "生成日時", researchStatus: "調査状態", coverageStatus: "調査範囲", consensusStatus: "Consensus",
      provisional: "暫定", accepted: "受理済み", coverageMet: "宣言した範囲を充足", profileIncomplete: "プロファイルに未確認項目あり", consensusIncomplete: "未完了"
    },
    en: {
      languageControl: "Display language", tagline: "Public research catalog and planning outputs", publicOnly: "Public information only", asOf: "As of",
      navOverview: "Overview", navCatalog: "Research catalog", navTechnology: "Technology landscape", navScenarios: "Roadmap scenarios", navReports: "Reports",
      overviewKicker: "CURRENT PUBLIC STATE", overviewTitle: "Continuous research status",
      overviewLead: "Research summaries derived from public information are shown with their validation status. Roadmap scenarios and reports are limited to explicitly human-approved outputs.",
      topicsMetric: "Research topics", topicsMetricNote: "Includes the protected initial catalog", scopeMetric: "Research updates",
      scopeMetricValue: "Continuous", scopeMetricNote: "Incorporates new public information", scenarioMetric: "Published scenarios", scenarioMetricNote: "Passed explicit human publication approval",
      reportMetric: "Published reports", reportMetricNote: "Traceable exports", revision: "revision", officialSources: "registered public sources",
      openGaps: "Open gaps", none: "none", catalogKicker: "RESEARCH INVENTORY", catalogTitle: "Research catalog",
      catalogLead: "Each Topic links to its public-source research summary, provisional findings, and supporting sources.",
      domainFilter: "Domain filter", all: "All", search: "Search", searchPlaceholder: "Topic ID or title",
      tableId: "ID", tableTopic: "Research topic", tableDomain: "Domain", tableStatus: "Status", tableCadence: "Review", tableOrigin: "Origin",
      noTopics: "No topics match the current filters.", technologyKicker: "CONTINUOUS RESEARCH SCOPE", technologyTitle: "Technology landscape", technologyLead: "Continuously surveys technology areas relevant to HPCI infrastructure planning.", area: "AREA", scenarioKicker: "ROADMAP SCENARIOS",
      scenarioTitle: "HPCI infrastructure scenarios",
      scenarioLead: "Compare architecture, system software, applications, center impacts, technology trends, and uncertainties as a coherent whole.",
      noScenarioTitle: "No scenarios have been published",
      noScenarioText: "The current four scenarios are generator examples. Only evidence-backed, evaluated, and human-approved scenarios are published.",
      reportKicker: "REPORTS", reportTitle: "Reports and exports",
      reportLead: "Published versions carry a version, as-of date, evidence traceability, and supersession links.",
      noReportTitle: "No reports have been published",
      noReportText: "Exports appear here after acceptance by the promotion workflow and explicit human publication approval.",
      footerDescription: "HPCI-CFSP public research view", originInitial: "protected initial",
      originHuman: "human directive", originAi: "AI consensus", statusNotStarted: "not started", statusPartial: "partial",
      statusReviewed: "reviewed", statusRetired: "retired", cadenceWeekly: "weekly", cadenceMonthly: "monthly",
      cadenceQuarterly: "quarterly", cadenceAnnual: "annual", cadenceEvent: "event-driven",
      summaryAvailable: "public summary", summaryPending: "public summary pending", closeDialog: "Close details",
      topicDetailMeta: "Topic details", noSummaryTitle: "No public summary yet",
      noSummaryText: "No research result linked to this Topic has been published yet. A future research cycle can update it.",
      researchOverview: "Research overview", findings: "Research findings", sources: "Supporting sources", caveat: "Validation caveat",
      sourceRun: "Research run", generatedAt: "Generated", researchStatus: "Research status", coverageStatus: "Coverage", consensusStatus: "Consensus",
      provisional: "provisional", accepted: "accepted", coverageMet: "declared scope met", profileIncomplete: "profile gaps remain", consensusIncomplete: "incomplete"
    }
  };

  const domainLabels = {
    ja: {architecture: "アーキテクチャ", "system-software": "システムソフトウェア", applications: "アプリケーション", "cross-cutting": "分野横断"},
    en: {architecture: "Architecture", "system-software": "System software", applications: "Applications", "cross-cutting": "Cross-cutting"}
  };
  const statusKeys = {"not-started": "statusNotStarted", partial: "statusPartial", reviewed: "statusReviewed", retired: "statusRetired"};
  const cadenceKeys = {weekly: "cadenceWeekly", monthly: "cadenceMonthly", quarterly: "cadenceQuarterly", annual: "cadenceAnnual", "event-driven": "cadenceEvent"};
  const originKeys = {"protected-initial": "originInitial", "human-directive": "originHuman", "ai-consensus": "originAi"};
  let activeDomain = "all";
  let language = readLanguage();
  let activeTopicId = null;

  function readLanguage() {
    try {
      const stored = window.localStorage.getItem("openfs-language");
      if (stored === "ja" || stored === "en") return stored;
    } catch (_error) {
      // Storage is optional.
    }
    return "ja";
  }

  function rememberLanguage(value) {
    try {
      window.localStorage.setItem("openfs-language", value);
    } catch (_error) {
      // Storage is optional.
    }
  }

  function tr(key) { return copy[language][key] || key; }
  function setText(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
  }

  function applyStaticCopy() {
    document.documentElement.lang = language;
    document.querySelectorAll("[data-i18n]").forEach((element) => { element.textContent = tr(element.dataset.i18n); });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => { element.placeholder = tr(element.dataset.i18nPlaceholder); });
    document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => { element.setAttribute("aria-label", tr(element.dataset.i18nAriaLabel)); });
    document.querySelectorAll("[data-language]").forEach((button) => {
      const selected = button.dataset.language === language;
      button.classList.toggle("active", selected);
      button.setAttribute("aria-pressed", String(selected));
    });
  }

  function renderSummary() {
    setText("as-of", `${tr("asOf")} ${data.as_of}`);
    setText("metric-topics", data.baseline.topic_count);
    setText("metric-scenarios", data.scenarios.length);
    setText("metric-reports", data.reports.length);
    setText("baseline-id", data.baseline.baseline_id);
    setText("baseline-detail", `${tr("revision")} ${data.baseline.catalog_revision} / ${tr("officialSources")} ${data.baseline.official_source_count}`);
    setText("gap-summary", `${tr("openGaps")}: ${data.baseline.open_gap_ids.join(", ") || tr("none")}`);
    setText("technology-rule", tr("technologyLead"));
    setText("license-status", `License: ${data.publication.license}`);
  }

  function renderTechnologyCategories() {
    const root = document.getElementById("technology-categories");
    root.replaceChildren();
    data.technology_landscape.categories.forEach((category, index) => {
      const item = document.createElement("article");
      item.className = "category-item";
      const number = document.createElement("span");
      number.textContent = `${tr("area")} ${String(index + 1).padStart(2, "0")}`;
      const label = document.createElement("p");
      label.textContent = category[language];
      item.append(number, label);
      root.appendChild(item);
    });
  }

  function renderTopics() {
    const query = document.getElementById("topic-search").value.trim().toLocaleLowerCase(language);
    const root = document.getElementById("topic-rows");
    root.replaceChildren();
    const filtered = data.topics.filter((topic) => {
      const domainMatch = activeDomain === "all" || topic.domain === activeDomain;
      const searchText = [topic.topic_id, topic.title_ja, topic.title_en].join(" ").toLocaleLowerCase(language);
      return domainMatch && (!query || searchText.includes(query));
    });

    filtered.forEach((topic) => {
      const row = document.createElement("tr");
      const idCell = document.createElement("td");
      idCell.className = "topic-id";
      idCell.textContent = topic.topic_id;
      const titleCell = document.createElement("td");
      const titleButton = document.createElement("button");
      titleButton.type = "button";
      titleButton.className = "topic-link";
      titleButton.setAttribute("aria-haspopup", "dialog");
      const titleText = document.createElement("span");
      titleText.className = "topic-link-title";
      titleText.textContent = language === "ja" ? topic.title_ja : topic.title_en;
      const resultState = document.createElement("span");
      resultState.className = `topic-result-state${topic.research_summary_count ? " available" : ""}`;
      resultState.textContent = topic.research_summary_count
        ? `${tr("summaryAvailable")} ${topic.research_summary_count}`
        : tr("summaryPending");
      titleButton.append(titleText, resultState);
      titleButton.addEventListener("click", () => openTopicDetail(topic.topic_id));
      titleCell.appendChild(titleButton);
      const domainCell = document.createElement("td");
      domainCell.textContent = domainLabels[language][topic.domain];
      const statusCell = document.createElement("td");
      statusCell.textContent = tr(statusKeys[topic.status] || topic.status);
      const cadenceCell = document.createElement("td");
      cadenceCell.textContent = tr(cadenceKeys[topic.review_cadence] || topic.review_cadence);
      const originCell = document.createElement("td");
      const origin = document.createElement("span");
      origin.className = `tag${topic.catalog_origin === "ai-consensus" ? " ai" : ""}`;
      origin.textContent = tr(originKeys[topic.catalog_origin] || topic.catalog_origin);
      originCell.appendChild(origin);
      row.append(idCell, titleCell, domainCell, statusCell, cadenceCell, originCell);
      root.appendChild(row);
    });
    document.getElementById("topic-empty").hidden = filtered.length !== 0;
  }

  function statusLabel(value) {
    const labels = {
      provisional: "provisional",
      accepted: "accepted",
      "met-declared-scope": "coverageMet",
      "profile-coverage-incomplete": "profileIncomplete",
      incomplete: "consensusIncomplete"
    };
    return tr(labels[value] || value);
  }

  function summariesForTopic(topicId) {
    return data.research_summaries
      .filter((summary) => summary.topic_ids.includes(topicId))
      .map((summary) => ({
        ...summary,
        findings: summary.findings.filter((finding) => finding.topic_ids.includes(topicId))
      }))
      .filter((summary) => summary.findings.length > 0);
  }

  function appendMetaItem(root, label, value) {
    const item = document.createElement("div");
    const term = document.createElement("dt");
    term.textContent = label;
    const description = document.createElement("dd");
    description.textContent = value;
    item.append(term, description);
    root.appendChild(item);
  }

  function renderTopicDetail() {
    if (!activeTopicId) return;
    const topic = data.topics.find((item) => item.topic_id === activeTopicId);
    if (!topic) return;
    setText("topic-dialog-id", topic.topic_id);
    setText("topic-dialog-title", language === "ja" ? topic.title_ja : topic.title_en);
    setText("topic-dialog-meta", `${tr("topicDetailMeta")} / ${domainLabels[language][topic.domain]}`);
    const root = document.getElementById("topic-dialog-content");
    root.replaceChildren();
    const summaries = summariesForTopic(topic.topic_id);
    if (!summaries.length) {
      const empty = document.createElement("div");
      empty.className = "dialog-empty";
      const title = document.createElement("strong");
      title.textContent = tr("noSummaryTitle");
      const body = document.createElement("p");
      body.textContent = tr("noSummaryText");
      empty.append(title, body);
      root.appendChild(empty);
      return;
    }

    summaries.forEach((summary) => {
      const section = document.createElement("section");
      section.className = "research-summary";
      const heading = document.createElement("div");
      heading.className = "research-summary-heading";
      const titleBlock = document.createElement("div");
      const kicker = document.createElement("span");
      kicker.className = "eyebrow";
      kicker.textContent = tr("researchOverview");
      const title = document.createElement("h3");
      title.textContent = language === "ja" ? summary.title_ja : summary.title_en;
      titleBlock.append(kicker, title);
      const status = document.createElement("span");
      status.className = "summary-status";
      status.textContent = statusLabel(summary.research_status);
      heading.append(titleBlock, status);
      const overview = document.createElement("p");
      overview.className = "research-overview";
      overview.textContent = language === "ja" ? summary.summary_ja : summary.summary_en;
      const meta = document.createElement("dl");
      meta.className = "research-meta";
      appendMetaItem(meta, tr("sourceRun"), summary.source_run_id);
      appendMetaItem(meta, tr("generatedAt"), summary.generated_at.slice(0, 10));
      appendMetaItem(meta, tr("coverageStatus"), statusLabel(summary.coverage_status));
      appendMetaItem(meta, tr("consensusStatus"), statusLabel(summary.consensus_status));

      const findingsTitle = document.createElement("h4");
      findingsTitle.textContent = tr("findings");
      const findings = document.createElement("ol");
      findings.className = "finding-list";
      summary.findings.forEach((finding) => {
        const item = document.createElement("li");
        const statement = document.createElement("p");
        statement.textContent = language === "ja" ? finding.statement_ja : finding.statement_en;
        const sourceLabel = document.createElement("span");
        sourceLabel.className = "source-label";
        sourceLabel.textContent = tr("sources");
        const sources = document.createElement("ul");
        sources.className = "source-list";
        finding.sources.forEach((source) => {
          const sourceItem = document.createElement("li");
          const link = document.createElement("a");
          link.href = source.url;
          link.target = "_blank";
          link.rel = "noopener noreferrer";
          link.textContent = source.title;
          const publisher = document.createElement("span");
          publisher.textContent = source.publisher;
          sourceItem.append(link, publisher);
          sources.appendChild(sourceItem);
        });
        item.append(statement, sourceLabel, sources);
        findings.appendChild(item);
      });
      const caveat = document.createElement("aside");
      caveat.className = "summary-caveat";
      const caveatTitle = document.createElement("strong");
      caveatTitle.textContent = tr("caveat");
      const caveatText = document.createElement("p");
      caveatText.textContent = language === "ja" ? summary.caveat_ja : summary.caveat_en;
      caveat.append(caveatTitle, caveatText);
      section.append(heading, overview, meta, findingsTitle, findings, caveat);
      root.appendChild(section);
    });
  }

  function openTopicDetail(topicId) {
    activeTopicId = topicId;
    renderTopicDetail();
    const dialog = document.getElementById("topic-dialog");
    if (!dialog.open) dialog.showModal();
  }

  function renderScenarios() {
    const root = document.getElementById("scenario-list");
    root.replaceChildren();
    data.scenarios.forEach((scenario) => {
      const item = document.createElement("article");
      item.className = "scenario-item";
      const title = document.createElement("h3");
      title.textContent = `${scenario.scenario_id} | ${language === "ja" ? scenario.title_ja : scenario.title_en}`;
      const objective = document.createElement("p");
      objective.textContent = language === "ja" ? scenario.objective : scenario.objective_en;
      item.append(title, objective);
      root.appendChild(item);
    });
    document.getElementById("scenario-empty").hidden = data.scenarios.length !== 0;
  }

  function renderReports() {
    const root = document.getElementById("report-list");
    root.replaceChildren();
    data.reports.forEach((report) => {
      const item = document.createElement("article");
      item.className = "report-item";
      const title = document.createElement("h3");
      title.textContent = language === "ja" ? report.title : report.title_en;
      const meta = document.createElement("p");
      meta.textContent = `${report.report_id} / ${report.as_of} / ${report.status}`;
      item.append(title, meta);
      root.appendChild(item);
    });
    document.getElementById("report-empty").hidden = data.reports.length !== 0;
  }

  function render() {
    applyStaticCopy();
    renderSummary();
    renderTopics();
    renderTechnologyCategories();
    renderScenarios();
    renderReports();
    renderTopicDetail();
  }

  document.querySelectorAll("[data-language]").forEach((button) => {
    button.addEventListener("click", () => {
      language = button.dataset.language;
      rememberLanguage(language);
      render();
    });
  });
  document.querySelectorAll("[data-domain]").forEach((button) => {
    button.addEventListener("click", () => {
      activeDomain = button.dataset.domain;
      document.querySelectorAll("[data-domain]").forEach((item) => item.classList.toggle("active", item === button));
      renderTopics();
    });
  });
  document.getElementById("topic-search").addEventListener("input", renderTopics);
  document.getElementById("topic-dialog-close").addEventListener("click", () => {
    document.getElementById("topic-dialog").close();
  });
  document.getElementById("topic-dialog").addEventListener("click", (event) => {
    if (event.target === event.currentTarget) event.currentTarget.close();
  });
  document.getElementById("topic-dialog").addEventListener("close", () => {
    activeTopicId = null;
  });
  render();
})();
