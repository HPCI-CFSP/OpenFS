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
      overviewLead: "受理済みの公開情報だけを表示します。内部情報、候補段階の提案、例示シナリオは公開対象に含めません。",
      topicsMetric: "調査Topic", topicsMetricNote: "保護された初期項目を含む", scopeMetric: "調査対象地域",
      scopeMetricValue: "全世界", scopeMetricNote: "日本発技術を優先追跡", scenarioMetric: "公開シナリオ", scenarioMetricNote: "人の公開承認を通過した成果",
      reportMetric: "公開報告書", reportMetricNote: "来歴付きExport", revision: "改訂", officialSources: "登録済み公開資料",
      openGaps: "未解決Gap", none: "なし", catalogKicker: "調査項目一覧", catalogTitle: "調査カタログ",
      catalogLead: "AIが追加提案したTopicも、独立レビューとConsensus Gateを通過したものだけがここへ加わります。",
      domainFilter: "分野フィルタ", all: "すべて", search: "検索", searchPlaceholder: "Topic ID、名称",
      tableId: "ID", tableTopic: "調査項目", tableDomain: "分野", tableStatus: "状態", tableCadence: "更新", tableOrigin: "起点",
      noTopics: "条件に一致するTopicはありません。", technologyKicker: "継続調査対象", technologyTitle: "技術動向", area: "領域",
      scenarioKicker: "ロードマップシナリオ", scenarioTitle: "HPCI整備シナリオ",
      scenarioLead: "Architecture、System Software、Applications、センター影響、世界技術動向、日本発技術、不確実性を一体で比較します。",
      noScenarioTitle: "公開済みシナリオはまだありません",
      noScenarioText: "現在の4案はGenerator検証用の例示です。根拠・評価・人の公開承認を通過した案だけを公開します。",
      reportKicker: "報告書", reportTitle: "報告書・Export", reportLead: "公開版には版、基準日、根拠への追跡、置換関係を付けます。",
      noReportTitle: "公開済み報告書はまだありません",
      noReportText: "Promotion workflowで受理され、人が公開を承認したExportが追加されると、ここへ自動表示されます。",
      footerDescription: "HPCI-CFSP 公開調査ビュー", originInitial: "保護された初期項目",
      originHuman: "人の指示", originAi: "AI Consensus", statusNotStarted: "未着手", statusPartial: "一部完了",
      statusReviewed: "確認済み", statusRetired: "廃止", cadenceWeekly: "週次", cadenceMonthly: "月次",
      cadenceQuarterly: "四半期", cadenceAnnual: "年次", cadenceEvent: "事象発生時"
    },
    en: {
      languageControl: "Display language", tagline: "Public research catalog and planning outputs", publicOnly: "Public information only", asOf: "As of",
      navOverview: "Overview", navCatalog: "Research catalog", navTechnology: "Technology landscape", navScenarios: "Roadmap scenarios", navReports: "Reports",
      overviewKicker: "CURRENT PUBLIC STATE", overviewTitle: "Continuous research status",
      overviewLead: "Only accepted public information is shown. Internal information, candidate proposals, and illustrative scenarios are excluded from publication.",
      topicsMetric: "Research topics", topicsMetricNote: "Includes the protected initial catalog", scopeMetric: "Geographic scope",
      scopeMetricValue: "Worldwide", scopeMetricNote: "Priority coverage for Japan-origin technologies", scenarioMetric: "Published scenarios", scenarioMetricNote: "Passed explicit human publication approval",
      reportMetric: "Published reports", reportMetricNote: "Traceable exports", revision: "revision", officialSources: "registered public sources",
      openGaps: "Open gaps", none: "none", catalogKicker: "RESEARCH INVENTORY", catalogTitle: "Research catalog",
      catalogLead: "AI-proposed topics enter this catalog only after independent review and the Consensus Gate.",
      domainFilter: "Domain filter", all: "All", search: "Search", searchPlaceholder: "Topic ID or title",
      tableId: "ID", tableTopic: "Research topic", tableDomain: "Domain", tableStatus: "Status", tableCadence: "Review", tableOrigin: "Origin",
      noTopics: "No topics match the current filters.", technologyKicker: "CONTINUOUS RESEARCH SCOPE", technologyTitle: "Technology landscape", area: "AREA", scenarioKicker: "ROADMAP SCENARIOS",
      scenarioTitle: "HPCI infrastructure scenarios",
      scenarioLead: "Compare architecture, system software, applications, center impacts, worldwide trends, Japan-origin technologies, and uncertainties as a coherent whole.",
      noScenarioTitle: "No scenarios have been published",
      noScenarioText: "The current four scenarios are generator examples. Only evidence-backed, evaluated, and human-approved scenarios are published.",
      reportKicker: "REPORTS", reportTitle: "Reports and exports",
      reportLead: "Published versions carry a version, as-of date, evidence traceability, and supersession links.",
      noReportTitle: "No reports have been published",
      noReportText: "Exports appear here after acceptance by the promotion workflow and explicit human publication approval.",
      footerDescription: "HPCI-CFSP public research view", originInitial: "protected initial",
      originHuman: "human directive", originAi: "AI consensus", statusNotStarted: "not started", statusPartial: "partial",
      statusReviewed: "reviewed", statusRetired: "retired", cadenceWeekly: "weekly", cadenceMonthly: "monthly",
      cadenceQuarterly: "quarterly", cadenceAnnual: "annual", cadenceEvent: "event-driven"
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
    setText("technology-rule", `${data.technology_landscape.scope_rule[language]} ${data.technology_landscape.priority_rule[language]}`);
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
      titleCell.textContent = language === "ja" ? topic.title_ja : topic.title_en;
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
  render();
})();
