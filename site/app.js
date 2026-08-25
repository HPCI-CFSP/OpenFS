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
      topicsMetric: "調査Topic", topicsMetricNote: "保護された初期項目を含む", scenarioMetric: "公開シナリオ", scenarioMetricNote: "人の公開承認を通過した成果",
      reportMetric: "公開報告書", reportMetricNote: "来歴付きExport", revision: "改訂", officialSources: "登録済み公開資料",
      openGaps: "未解決Gap", none: "なし", catalogKicker: "調査項目一覧", catalogTitle: "調査カタログ",
      catalogLead: "各Topicには、公開情報から得た知見と根拠資料を直接関連付け、調査元と検証状況を併記します。",
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
      findingAvailable: "公開知見", summaryPending: "公開知見未作成", closeDialog: "詳細を閉じる",
      topicDetailMeta: "Topic詳細", noSummaryTitle: "公開知見はまだありません",
      noSummaryText: "このTopicに紐づく調査結果はまだ公開されていません。今後の調査ループで更新されます。",
      topicResultsKicker: "Topic別の調査結果", topicResultsLead: "このTopicに直接関連付けられた公開知見を{runCount}件の調査Runから{findingCount}件表示しています。",
      sourceSurvey: "調査元", findings: "調査で得られた知見", sources: "根拠資料", sourceCaveat: "調査元の検証状況",
      sourceRun: "調査Run", generatedAt: "生成日時", researchStatus: "調査状態", coverageStatus: "調査範囲", consensusStatus: "Consensus",
      consensusProof: "この情報は{modelCount}個のAIモデル（{groupCount}つの独立AIグループ）と{harnessCount}件のAIハーネス構成によってConsensusを通過しています",
      consensusReceipt: "Consensus Receipt", decision: "Decision", decidedAt: "判定日時", policy: "Policy",
      participants: "参加モデル・エージェント", harnesses: "AIハーネス", agentRole: "役割", independenceGroup: "独立性グループ",
      promptProfile: "Prompt Profile", contribution: "検証上の担当", assessment: "Assessment", commit: "Commit", run: "Run",
      provisional: "暫定", accepted: "受理済み", coverageMet: "宣言した範囲を充足", profileIncomplete: "プロファイルに未確認項目あり", consensusIncomplete: "未完了",
      memoryRoadmapKicker: "メモリ技術調査", roadmapFilter: "技術群フィルタ", memoryProducts: "メモリ製品", integration3d: "3D実装", systemEnablers: "システム技術",
      technologyColumn: "技術", vendorColumn: "ベンダー／対象", undatedColumn: "時期未公表", roadmapTableNote: "項目を選択すると根拠と詳細を表示します。空欄は開発停止ではなく、確認できる公開日程がないことを示します。",
      technologyNotesKicker: "技術別ノート", technologyNotesTitle: "現状とHPCI整備への示唆", currentState: "現在の状況", hpciImplications: "HPCI整備への示唆", roadmapCaveat: "公開時の注意事項",
      commercial: "製品・量産", sample: "サンプル", standard: "標準", target: "ベンダー目標", concept: "構想・研究", undated: "時期未公表", timingBasis: "時期の根拠", milestoneDetail: "マイルストーン詳細", publicSources: "公開根拠資料",
      observed: "確認済み", standardRelease: "標準公開", vendorTarget: "ベンダー目標", noPublicDate: "公開時期なし", officialScanIncomplete: "一次情報の継続確認が必要"
    },
    en: {
      languageControl: "Display language", tagline: "Public research catalog and planning outputs", publicOnly: "Public information only", asOf: "As of",
      navOverview: "Overview", navCatalog: "Research catalog", navTechnology: "Technology landscape", navScenarios: "Roadmap scenarios", navReports: "Reports",
      overviewKicker: "CURRENT PUBLIC STATE", overviewTitle: "Continuous research status",
      overviewLead: "Research summaries derived from public information are shown with their validation status. Roadmap scenarios and reports are limited to explicitly human-approved outputs.",
      topicsMetric: "Research topics", topicsMetricNote: "Includes the protected initial catalog", scenarioMetric: "Published scenarios", scenarioMetricNote: "Passed explicit human publication approval",
      reportMetric: "Published reports", reportMetricNote: "Traceable exports", revision: "revision", officialSources: "registered public sources",
      openGaps: "Open gaps", none: "none", catalogKicker: "RESEARCH INVENTORY", catalogTitle: "Research catalog",
      catalogLead: "Each Topic directly links public-source findings and supporting sources while identifying the source survey and validation status.",
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
      findingAvailable: "public findings", summaryPending: "public findings pending", closeDialog: "Close details",
      topicDetailMeta: "Topic details", noSummaryTitle: "No public findings yet",
      noSummaryText: "No research result linked to this Topic has been published yet. A future research cycle can update it.",
      topicResultsKicker: "TOPIC-SPECIFIC RESULTS", topicResultsLead: "Showing {findingCount} public findings directly linked to this Topic from {runCount} research runs.",
      sourceSurvey: "SOURCE SURVEY", findings: "Research findings", sources: "Supporting sources", sourceCaveat: "Source survey validation status",
      sourceRun: "Research run", generatedAt: "Generated", researchStatus: "Research status", coverageStatus: "Coverage", consensusStatus: "Consensus",
      consensusProof: "This information passed Consensus with {modelCount} AI models in {groupCount} independent groups and {harnessCount} AI harness configurations",
      consensusReceipt: "Consensus Receipt", decision: "Decision", decidedAt: "Decided", policy: "Policy",
      participants: "Participating models and agents", harnesses: "AI harnesses", agentRole: "Role", independenceGroup: "Independence group",
      promptProfile: "Prompt profile", contribution: "Consensus contribution", assessment: "Assessment", commit: "Commit", run: "Run",
      provisional: "provisional", accepted: "accepted", coverageMet: "declared scope met", profileIncomplete: "profile gaps remain", consensusIncomplete: "incomplete",
      memoryRoadmapKicker: "MEMORY TECHNOLOGY RESEARCH", roadmapFilter: "Technology group filter", memoryProducts: "Memory products", integration3d: "3D integration", systemEnablers: "System enablers",
      technologyColumn: "Technology", vendorColumn: "Vendor / scope", undatedColumn: "Timing not public", roadmapTableNote: "Select a milestone to view its details and sources. Blank cells indicate that no dated public milestone was confirmed, not that development has stopped.",
      technologyNotesKicker: "TECHNOLOGY NOTES", technologyNotesTitle: "Current state and implications for HPCI", currentState: "Current state", hpciImplications: "Implications for HPCI", roadmapCaveat: "Publication caveat",
      commercial: "product / volume", sample: "sample", standard: "standard", target: "vendor target", concept: "concept / research", undated: "timing not public", timingBasis: "Timing basis", milestoneDetail: "Milestone detail", publicSources: "Public supporting sources",
      observed: "observed", standardRelease: "standard release", vendorTarget: "vendor target", noPublicDate: "no public date", officialScanIncomplete: "continued primary-source review required"
    }
  };

  const domainLabels = {
    ja: {architecture: "アーキテクチャ", "system-software": "システムソフトウェア", applications: "アプリケーション", "cross-cutting": "分野横断"},
    en: {architecture: "Architecture", "system-software": "System software", applications: "Applications", "cross-cutting": "Cross-cutting"}
  };
  const statusKeys = {"not-started": "statusNotStarted", partial: "statusPartial", reviewed: "statusReviewed", retired: "statusRetired"};
  const cadenceKeys = {weekly: "cadenceWeekly", monthly: "cadenceMonthly", quarterly: "cadenceQuarterly", annual: "cadenceAnnual", "event-driven": "cadenceEvent"};
  const originKeys = {"protected-initial": "originInitial", "human-directive": "originHuman", "ai-consensus": "originAi"};
  const roadmapGroupKeys = {"memory-products": "memoryProducts", "3d-integration": "integration3d", "system-enablers": "systemEnablers"};
  const maturityKeys = {commercial: "commercial", sample: "sample", standard: "standard", target: "target", concept: "concept", undated: "undated"};
  const timingBasisKeys = {observed: "observed", "standard-release": "standardRelease", "vendor-target": "vendorTarget", "no-public-date": "noPublicDate"};
  let activeDomain = "all";
  let language = readLanguage();
  let activeTopicId = null;
  let activeRoadmapGroup = "all";
  let activeRoadmapMilestoneId = null;

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

  function localized(item, field) {
    return item[`${field}_${language}`] || item[field] || "";
  }

  function roadmapSourceMap() {
    return new Map((data.memory_roadmap?.sources || []).map((source) => [source.source_id, source]));
  }

  function renderRoadmapLegend() {
    const root = document.getElementById("roadmap-legend");
    root.replaceChildren();
    ["commercial", "sample", "standard", "target", "concept", "undated"].forEach((maturity) => {
      const item = document.createElement("span");
      item.className = `legend-item maturity-${maturity}`;
      item.textContent = tr(maturityKeys[maturity]);
      root.appendChild(item);
    });
  }

  function renderRoadmapTimeline() {
    const roadmap = data.memory_roadmap;
    const root = document.getElementById("memory-roadmap-timeline");
    root.replaceChildren();
    if (!roadmap) return;

    const technologies = roadmap.technologies.filter(
      (technology) => activeRoadmapGroup === "all" || technology.group === activeRoadmapGroup
    );
    const years = [];
    for (let year = roadmap.horizon.start_year; year <= roadmap.horizon.end_year; year += 1) years.push(year);

    const table = document.createElement("table");
    table.className = "roadmap-table";
    const head = document.createElement("thead");
    const headRow = document.createElement("tr");
    [tr("technologyColumn"), tr("vendorColumn"), ...years, tr("undatedColumn")].forEach((label, index) => {
      const cell = document.createElement("th");
      cell.textContent = label;
      if (index === 0) cell.className = "roadmap-tech-column";
      if (index === 1) cell.className = "roadmap-vendor-column";
      headRow.appendChild(cell);
    });
    head.appendChild(headRow);

    const body = document.createElement("tbody");
    technologies.forEach((technology) => {
      const lanes = roadmap.lanes.filter((lane) => lane.technology_id === technology.technology_id);
      lanes.forEach((lane, laneIndex) => {
        const row = document.createElement("tr");
        if (laneIndex === 0) {
          const technologyCell = document.createElement("th");
          technologyCell.scope = "rowgroup";
          technologyCell.rowSpan = lanes.length;
          technologyCell.className = "roadmap-tech-column roadmap-technology-cell";
          const technologyName = document.createElement("strong");
          technologyName.textContent = localized(technology, "name");
          const technologyGroup = document.createElement("span");
          technologyGroup.textContent = tr(roadmapGroupKeys[technology.group]);
          technologyCell.append(technologyName, technologyGroup);
          row.appendChild(technologyCell);
        }

        const vendorCell = document.createElement("th");
        vendorCell.scope = "row";
        vendorCell.className = "roadmap-vendor-column roadmap-vendor-cell";
        const vendor = document.createElement("strong");
        vendor.textContent = lane.vendor;
        const scope = document.createElement("span");
        scope.textContent = localized(lane, "scope");
        vendorCell.append(vendor, scope);
        row.appendChild(vendorCell);

        [...years, null].forEach((year) => {
          const cell = document.createElement("td");
          const milestones = lane.milestones.filter((milestone) => milestone.year === year);
          milestones.forEach((milestone) => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = `roadmap-milestone maturity-${milestone.maturity}`;
            button.textContent = localized(milestone, "label");
            button.setAttribute("aria-haspopup", "dialog");
            button.addEventListener("click", () => openRoadmapMilestone(milestone.milestone_id));
            cell.appendChild(button);
          });
          row.appendChild(cell);
        });
        body.appendChild(row);
      });
    });
    table.append(head, body);
    root.appendChild(table);
  }

  function appendSourceList(root, sourceIds) {
    const sources = roadmapSourceMap();
    sourceIds.forEach((sourceId) => {
      const source = sources.get(sourceId);
      if (!source) return;
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = source.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = source.title;
      const publisher = document.createElement("span");
      publisher.textContent = source.publisher;
      item.append(link, publisher);
      root.appendChild(item);
    });
  }

  function renderMemoryTechnologyDetails() {
    const roadmap = data.memory_roadmap;
    const root = document.getElementById("memory-technology-details");
    root.replaceChildren();
    if (!roadmap) return;
    roadmap.technologies
      .filter((technology) => activeRoadmapGroup === "all" || technology.group === activeRoadmapGroup)
      .forEach((technology) => {
        const details = document.createElement("details");
        details.className = "memory-technology-note";
        const toggle = document.createElement("summary");
        const name = document.createElement("strong");
        name.textContent = localized(technology, "name");
        const summary = document.createElement("span");
        summary.textContent = localized(technology, "summary");
        toggle.append(name, summary);
        const body = document.createElement("div");
        body.className = "memory-technology-note-body";
        const stateTitle = document.createElement("h4");
        stateTitle.textContent = tr("currentState");
        const state = document.createElement("p");
        state.textContent = localized(technology, "current_state");
        const implicationsTitle = document.createElement("h4");
        implicationsTitle.textContent = tr("hpciImplications");
        const implications = document.createElement("p");
        implications.textContent = localized(technology, "hpci_implications");
        const sourcesTitle = document.createElement("h4");
        sourcesTitle.textContent = tr("publicSources");
        const sources = document.createElement("ul");
        sources.className = "source-list memory-source-list";
        appendSourceList(sources, technology.source_ids);
        body.append(stateTitle, state, implicationsTitle, implications, sourcesTitle, sources);
        details.append(toggle, body);
        root.appendChild(details);
      });
  }

  function renderMemoryRoadmap() {
    const roadmap = data.memory_roadmap;
    const section = document.getElementById("memory-roadmap");
    section.hidden = !roadmap;
    if (!roadmap) return;
    setText("memory-roadmap-title", localized(roadmap, "title"));
    setText("memory-roadmap-summary", localized(roadmap, "summary"));
    setText("memory-roadmap-as-of", roadmap.as_of);
    setText("memory-roadmap-research-status", statusLabel(roadmap.research_status));
    setText("memory-roadmap-coverage-status", statusLabel(roadmap.coverage_status));
    setText("memory-roadmap-consensus-status", statusLabel(roadmap.consensus_status));
    setText("memory-roadmap-caveat", localized(roadmap, "caveat"));
    const gaps = document.getElementById("memory-roadmap-gaps");
    gaps.replaceChildren();
    roadmap.coverage_gaps.forEach((gap) => {
      const item = document.createElement("li");
      item.textContent = localized(gap, "statement");
      gaps.appendChild(item);
    });
    document.querySelectorAll("[data-roadmap-group]").forEach((button) => {
      button.classList.toggle("active", button.dataset.roadmapGroup === activeRoadmapGroup);
    });
    renderRoadmapLegend();
    renderRoadmapTimeline();
    renderMemoryTechnologyDetails();
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
      resultState.className = `topic-result-state${topic.research_finding_count ? " available" : ""}`;
      resultState.textContent = topic.research_finding_count
        ? `${tr("findingAvailable")} ${topic.research_finding_count}`
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
      "official-source-scan-incomplete": "officialScanIncomplete",
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
      .filter((summary) => summary.findings.length > 0)
      .sort((left, right) => (
        right.findings.length - left.findings.length
        || right.generated_at.localeCompare(left.generated_at)
      ));
  }

  function consensusReceiptForFinding(finding) {
    if (!finding.consensus_receipt_id) return null;
    return data.consensus_receipts.find(
      (receipt) => receipt.receipt_id === finding.consensus_receipt_id
    ) || null;
  }

  function appendReceiptMeta(root, label, value) {
    const item = document.createElement("div");
    const term = document.createElement("dt");
    term.textContent = label;
    const description = document.createElement("dd");
    description.textContent = value;
    item.append(term, description);
    root.appendChild(item);
  }

  function renderConsensusReceipt(finding) {
    const receipt = consensusReceiptForFinding(finding);
    if (!receipt) return null;
    const details = document.createElement("details");
    details.className = "consensus-receipt";
    const toggle = document.createElement("summary");
    const modelCount = new Set(
      receipt.participants
        .filter((participant) => participant.contribution !== "consensus-controller")
        .map((participant) => `${participant.provider}\u0000${participant.model_family}`)
    ).size;
    toggle.textContent = tr("consensusProof")
      .replace("{modelCount}", String(modelCount))
      .replace("{groupCount}", String(receipt.independence_group_count))
      .replace("{harnessCount}", String(receipt.harnesses.length));
    const body = document.createElement("div");
    body.className = "consensus-receipt-body";
    const title = document.createElement("h5");
    title.textContent = `${tr("consensusReceipt")} ${receipt.receipt_id}`;
    const meta = document.createElement("dl");
    meta.className = "consensus-receipt-meta";
    appendReceiptMeta(meta, tr("decision"), receipt.decision_id);
    appendReceiptMeta(meta, tr("decidedAt"), receipt.decided_at.slice(0, 10));
    appendReceiptMeta(meta, tr("policy"), receipt.policy_id);
    appendReceiptMeta(
      meta,
      tr("independenceGroup"),
      receipt.policy_result.independence_groups.join(", ")
    );

    const participantsTitle = document.createElement("h6");
    participantsTitle.textContent = tr("participants");
    const participants = document.createElement("div");
    participants.className = "receipt-list";
    receipt.participants.forEach((participant) => {
      const item = document.createElement("div");
      item.className = "receipt-list-item";
      const model = document.createElement("strong");
      model.textContent = `${participant.provider} / ${participant.model_family}`;
      const identity = document.createElement("p");
      identity.textContent = participant.agent_id;
      const attributes = document.createElement("dl");
      appendReceiptMeta(attributes, tr("agentRole"), participant.role);
      appendReceiptMeta(attributes, tr("independenceGroup"), participant.independence_group);
      appendReceiptMeta(attributes, tr("promptProfile"), participant.prompt_profile);
      appendReceiptMeta(attributes, tr("contribution"), participant.contribution);
      if (participant.assessment_id) {
        appendReceiptMeta(attributes, tr("assessment"), participant.assessment_id);
      }
      item.append(model, identity, attributes);
      participants.appendChild(item);
    });

    const harnessesTitle = document.createElement("h6");
    harnessesTitle.textContent = tr("harnesses");
    const harnesses = document.createElement("div");
    harnesses.className = "receipt-list";
    receipt.harnesses.forEach((harness) => {
      const item = document.createElement("div");
      item.className = "receipt-list-item harness-item";
      const name = document.createElement("a");
      name.href = harness.repository_url;
      name.target = "_blank";
      name.rel = "noopener noreferrer";
      name.textContent = harness.name;
      const run = document.createElement("p");
      run.textContent = `${tr("run")}: ${harness.run_id}`;
      const commit = document.createElement("a");
      commit.href = `${harness.repository_url}/commit/${harness.commit_sha}`;
      commit.target = "_blank";
      commit.rel = "noopener noreferrer";
      commit.textContent = `${tr("commit")}: ${harness.commit_sha}`;
      item.append(name, run, commit);
      harnesses.appendChild(item);
    });
    body.append(title, meta, participantsTitle, participants, harnessesTitle, harnesses);
    details.append(toggle, body);
    return details;
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

    const findingCount = summaries.reduce(
      (count, summary) => count + summary.findings.length,
      0
    );
    const topicOverview = document.createElement("section");
    topicOverview.className = "topic-results-overview";
    const overviewKicker = document.createElement("span");
    overviewKicker.className = "eyebrow";
    overviewKicker.textContent = tr("topicResultsKicker");
    const overviewText = document.createElement("p");
    overviewText.textContent = tr("topicResultsLead")
      .replace("{runCount}", String(summaries.length))
      .replace("{findingCount}", String(findingCount));
    topicOverview.append(overviewKicker, overviewText);
    root.appendChild(topicOverview);

    summaries.forEach((summary) => {
      const section = document.createElement("section");
      section.className = "research-summary";
      const heading = document.createElement("div");
      heading.className = "research-summary-heading";
      const titleBlock = document.createElement("div");
      const kicker = document.createElement("span");
      kicker.className = "eyebrow";
      kicker.textContent = tr("findings");
      const title = document.createElement("h3");
      title.textContent = language === "ja" ? topic.title_ja : topic.title_en;
      const sourceSurvey = document.createElement("p");
      sourceSurvey.className = "research-source-title";
      sourceSurvey.textContent = `${tr("sourceSurvey")}: ${language === "ja" ? summary.title_ja : summary.title_en}`;
      titleBlock.append(kicker, title, sourceSurvey);
      const status = document.createElement("span");
      status.className = "summary-status";
      status.textContent = statusLabel(summary.research_status);
      heading.append(titleBlock, status);
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
        const consensusReceipt = renderConsensusReceipt(finding);
        if (consensusReceipt) item.appendChild(consensusReceipt);
        findings.appendChild(item);
      });
      const caveat = document.createElement("aside");
      caveat.className = "summary-caveat";
      const caveatTitle = document.createElement("strong");
      caveatTitle.textContent = tr("sourceCaveat");
      const caveatText = document.createElement("p");
      caveatText.textContent = language === "ja" ? summary.caveat_ja : summary.caveat_en;
      caveat.append(caveatTitle, caveatText);
      section.append(heading, meta, findingsTitle, findings, caveat);
      root.appendChild(section);
    });
  }

  function openTopicDetail(topicId) {
    activeTopicId = topicId;
    renderTopicDetail();
    const dialog = document.getElementById("topic-dialog");
    if (!dialog.open) dialog.showModal();
  }

  function findRoadmapMilestone(milestoneId) {
    const roadmap = data.memory_roadmap;
    if (!roadmap) return null;
    for (const lane of roadmap.lanes) {
      const milestone = lane.milestones.find((item) => item.milestone_id === milestoneId);
      if (milestone) {
        const technology = roadmap.technologies.find(
          (item) => item.technology_id === lane.technology_id
        );
        return {technology, lane, milestone};
      }
    }
    return null;
  }

  function renderRoadmapDialog() {
    if (!activeRoadmapMilestoneId) return;
    const match = findRoadmapMilestone(activeRoadmapMilestoneId);
    if (!match) return;
    const {technology, lane, milestone} = match;
    setText("roadmap-dialog-id", milestone.milestone_id);
    setText("roadmap-dialog-title", localized(milestone, "label"));
    setText(
      "roadmap-dialog-meta",
      `${localized(technology, "name")} / ${lane.vendor} / ${milestone.year || tr("undatedColumn")}`
    );
    const root = document.getElementById("roadmap-dialog-content");
    root.replaceChildren();
    const section = document.createElement("section");
    section.className = "roadmap-milestone-detail";
    const status = document.createElement("span");
    status.className = `summary-status maturity-${milestone.maturity}`;
    status.textContent = tr(maturityKeys[milestone.maturity]);
    const title = document.createElement("h3");
    title.textContent = tr("milestoneDetail");
    const detail = document.createElement("p");
    detail.textContent = localized(milestone, "detail");
    const meta = document.createElement("dl");
    meta.className = "research-meta roadmap-dialog-meta-list";
    appendMetaItem(meta, tr("technologyColumn"), localized(technology, "name"));
    appendMetaItem(meta, tr("vendorColumn"), `${lane.vendor} / ${localized(lane, "scope")}`);
    appendMetaItem(meta, tr("timingBasis"), tr(timingBasisKeys[milestone.timing_basis]));
    appendMetaItem(meta, tr("asOf"), data.memory_roadmap.as_of);
    const sourcesTitle = document.createElement("h4");
    sourcesTitle.textContent = tr("publicSources");
    const sources = document.createElement("ul");
    sources.className = "source-list roadmap-dialog-source-list";
    appendSourceList(sources, milestone.source_ids);
    section.append(status, title, detail, meta, sourcesTitle, sources);
    root.appendChild(section);
  }

  function openRoadmapMilestone(milestoneId) {
    activeRoadmapMilestoneId = milestoneId;
    renderRoadmapDialog();
    const dialog = document.getElementById("roadmap-dialog");
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
    renderMemoryRoadmap();
    renderScenarios();
    renderReports();
    renderTopicDetail();
    renderRoadmapDialog();
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
  document.querySelectorAll("[data-roadmap-group]").forEach((button) => {
    button.addEventListener("click", () => {
      activeRoadmapGroup = button.dataset.roadmapGroup;
      renderMemoryRoadmap();
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
  document.getElementById("roadmap-dialog-close").addEventListener("click", () => {
    document.getElementById("roadmap-dialog").close();
  });
  document.getElementById("roadmap-dialog").addEventListener("click", (event) => {
    if (event.target === event.currentTarget) event.currentTarget.close();
  });
  document.getElementById("roadmap-dialog").addEventListener("close", () => {
    activeRoadmapMilestoneId = null;
  });
  render();
})();
