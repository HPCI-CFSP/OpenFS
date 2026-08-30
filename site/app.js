(function () {
  "use strict";

  const data = window.OPENFS_PUBLIC_DATA;
  if (!data) {
    document.body.textContent = "OpenFS public data is unavailable.";
    return;
  }

  const copy = {
    ja: {
      scopeTitle: "調査範囲と進捗", relatedTopics: "関連する調査項目", movedTopic: "再編前の調査項目", movedTopicNote: "この項目は統合・移管されました。現在の調査範囲は以下の項目・成果物から確認できます。", relatedOutput: "関連する公開ページ", evidenceSections: "収集済みの関連情報", sharedEvidence: "同一の記述・根拠を参照",
      languageControl: "表示言語", publicStatus: "公開状態", inPageNavigation: "ページ内ナビゲーション", openfsSummary: "OpenFSの集計", tagline: "公開調査カタログとシステム整備計画案", publicOnly: "公開情報のみ", siteUpdated: "サイト更新日時", catalogAsOf: "カタログ基準日", researchAsOf: "調査基準日", asOf: "情報確認日", licenseLabel: "ライセンス",
      navOverview: "概要", navCatalog: "調査カタログ", navSearch: "検索", navRoadmaps: "ロードマップ", navScenarios: "システム整備計画案", navReports: "報告書",
      aboutKicker: "OpenFSについて",
      aboutLead: "OpenFSは、将来の計算・データ基盤の整備計画を検討するため、計算機アーキテクチャ、メモリ、ネットワーク、システムソフトウェア、アプリケーションなどの公開情報を継続的に調査・比較する基盤です。根拠をたどれる技術動向、ロードマップ、システム整備計画案を公開し、未確認事項、各情報の更新日と確認状況、合意判定の状況も明示します。",
      overviewKicker: "現在の公開状況", overviewTitle: "継続調査の進捗状況",
      overviewLead: "公開情報から作成した調査サマリーは検証状況とともに表示します。システム整備計画案と報告書は、人による公開承認を受けた成果だけを掲載します。",
      topicsMetric: "調査項目", topicsMetricNote: "調査カタログに登録済み", roadmapMetric: "公開ロードマップ", roadmapMetricNote: "専用ページで公開中", scenarioMetric: "公開計画案", scenarioMetricNote: "人による公開承認済み",
      reportMetric: "公開報告書", reportMetricNote: "来歴を確認できる出力", revision: "改訂", officialSources: "登録済みの公開資料",
      openGaps: "未確認事項", none: "なし", catalogKicker: "調査項目一覧", catalogTitle: "調査カタログ",
      catalogLead: "各調査項目では、調査基準日現在の最新状況、近い将来の方向性、中長期の研究開発候補、見解が分かれている論点を区別して示します。システム整備との関係、公開根拠、未確認事項、調査履歴、関連ロードマップも確認できます。",
      domainFilter: "分類で絞り込む", all: "すべて", domainArchitecture: "アーキテクチャ", domainSystemSoftware: "システムソフトウェア", domainApplications: "アプリケーション", domainCrossCutting: "分野横断", search: "検索", searchPlaceholder: "表示コード、正規ID、名称または分類",
      tableId: "ID", tableTopic: "調査項目", tableDomain: "分類", tableStatus: "調査状況", tableVerification: "検証状況", tableUpdated: "最終更新日時", tableGaps: "未確認事項",
      noTopics: "条件に一致する調査項目はありません。", technologyKicker: "継続調査対象", technologyTitle: "技術動向", technologyLead: "HPCI整備計画に関係する技術分野を継続的に調査します。", area: "領域",
      roadmapKicker: "技術・ソフトウェア・応用の見通し", roadmapTitle: "ロードマップ", roadmapLead: "分類別のロードマップを一覧から選び、年表、根拠、HPCIシステム整備への示唆を専用ページで確認できます。", roadmapColumn: "ロードマップ", domainColumn: "分類", horizonColumn: "対象期間", updatedColumn: "更新日時", noRoadmaps: "公開中のロードマップはまだありません。", openRoadmapLibrary: "ロードマップ一覧を開く",
      scenarioKicker: "計画の選択肢", scenarioTitle: "システム整備計画案",
      scenarioLead: "アーキテクチャ、システムソフトウェア、アプリケーション、運用主体への影響、技術動向、不確実性を一体として比較します。HPCI固有の条件は各計画案で注記します。",
      noScenarioTitle: "公開済みの計画案はまだありません",
      noScenarioText: "根拠と評価を確認し、人による公開承認を受けた計画案をここに表示します。",
      openScenarioComparison: "3つの計画案を比較する",
      reportKicker: "報告書", reportTitle: "報告書・公開データ", reportLead: "公開版にはバージョン、情報確認日、根拠への参照、旧版との関係を記録します。",
      noReportTitle: "公開済み報告書はまだありません",
      noReportText: "昇格ワークフローで受理され、人による公開承認を受けた報告書やデータをここに自動表示します。",
      footerDescription: "HPCI-CFSP 公開調査ビュー", statusNotStarted: "未着手", statusPartial: "一部完了",
      statusReviewed: "レビュー済み", statusRetired: "廃止", verificationPending: "独立検証待ち", verificationAccepted: "合意判定で受理済み", evidenceCollected: "根拠あり・検証待ち", notYetReviewed: "未検証", noPublicUpdate: "公開結果なし",
      findingAvailable: "公開知見", decisionAvailable: "技術整理", summaryPending: "公開知見を準備中", closeDialog: "詳細を閉じる",
      topicDetailMeta: "調査項目の詳細", canonicalTopicId: "正規Topic ID", relatedRoadmaps: "関連ロードマップ", roadmapPlanned: "（作成予定）", noSummaryTitle: "公開知見はまだありません",
      noSummaryText: "この調査項目に対応する調査結果は、まだ公開されていません。今後の調査で公開可能な結果が得られた時点で更新します。",
      topicResultsKicker: "調査項目別の結果", topicResultsLead: "この調査項目に直接対応する公開知見を、{runCount}回の調査実行から{findingCount}件表示しています。",
      sourceSurvey: "情報源の調査記録", findings: "調査で得られた知見", sources: "根拠資料", sourceCaveat: "この調査実行の検証状況",
      sourceRun: "調査実行ID", generatedAt: "生成日時", researchStatus: "調査状況", coverageStatus: "調査範囲", consensusStatus: "合意判定状況",
      consensusProof: "この情報は、{modelCount}種類のAIモデル、{groupCount}つの独立グループ、{harnessCount}種類のAIハーネス構成による合意判定を通過しています。",
      consensusReceipt: "合意判定の記録", decision: "判定ID", decidedAt: "判定日時", policy: "適用方針",
      participants: "参加したモデルとエージェント", harnesses: "AIハーネス", agentRole: "役割", independenceGroup: "独立性グループ",
      promptProfile: "プロンプト設定", contribution: "検証上の担当", assessment: "評価ID", commit: "コミット", run: "実行ID",
      provisional: "暫定", accepted: "受理済み", coverageMet: "設定した調査範囲を確認済み", profileIncomplete: "一次情報の継続確認が必要", consensusIncomplete: "合意判定未完了",
      memoryRoadmapKicker: "メモリ技術調査", roadmapFilter: "技術群フィルタ", memoryProducts: "メモリ製品", integration3d: "3D実装", systemEnablers: "システム技術",
      technologyColumn: "技術", vendorColumn: "ベンダー／対象", undatedColumn: "時期未公表", roadmapTableNote: "項目を選択すると根拠と詳細を表示します。空欄は開発停止ではなく、確認できる公開日程がないことを示します。",
      technologyNotesKicker: "技術別ノート", technologyNotesTitle: "最新状況とHPCIシステム整備への示唆", currentState: "最新状況（調査基準日現在）", hpciImplications: "HPCIシステム整備への示唆", roadmapCaveat: "公開時の注意事項",
      commercial: "製品・量産", sample: "サンプル", standard: "標準", target: "公表目標", concept: "構想・研究", undated: "時期未公表", timingBasis: "時期の根拠", milestoneDetail: "マイルストーン詳細", publicSources: "公開根拠資料",
      observed: "確認済み", standardRelease: "標準公開", vendorTarget: "ベンダー目標", noPublicDate: "時期未公表", officialScanIncomplete: "一次情報の継続確認が必要",
      decisionSummary: "整備判断に向けた技術整理", provisionalNotice: "公開情報に基づく暫定整理です。独立したAIモデルによる合意判定（Consensus Gate）は完了していません。", regionFilter: "地域・主体で絞り込む", allRegions: "すべて", currentStage: "最新状況（調査基準日現在）", nearTermStage: "近い将来の方向性", researchStage: "中長期の研究開発候補", contestedStage: "見解が分かれている論点・未確定事項", maturity: "成熟度", timing: "時期", confidence: "確度", hpciRelevance: "HPCIシステム整備との関係", adoptionConditions: "採用判断で確認する条件", actorsLabel: "関係主体", actorRoles: "役割", regionBasis: "地域分類の根拠", sourceEvidence: "公開根拠", decisionDimensions: "整備判断の評価軸", relatedTables: "関連する比較表", platformMatrix: "主要CPU・GPUのソフトウェア対応表", numericalMatrix: "数値計算アルゴリズム・精度対応表", capabilitySoftware: "機能／ソフトウェア", supportLevel: "対応状況", optimizationLevel: "最適化状況", versionLicense: "版・ライセンス", methodSoftware: "アルゴリズム／ソフトウェア", targetPlatforms: "対象プラットフォーム", inputPrecision: "入力精度", computePrecision: "演算精度", accumulationPrecision: "累積精度", outputPrecision: "出力精度", mixedPrecision: "混合精度", precisionEmulation: "精度エミュレーション", distributedSupport: "分散実行", coverageGaps: "未確認事項", nextAction: "次の調査", researchHistory: "調査履歴・個別知見", researchHistoryLead: "調査実行ごとの来歴と抽出知見を確認できます。", noRegionalItems: "この地域条件に該当する項目はありません。", high: "高", medium: "中", low: "低", deployed: "運用中", standardized: "標準化済み", sampling: "サンプル提供中", announced: "発表済み", prototype: "試作", research: "研究", uncertain: "不確定", production: "製品対応", partial: "部分対応", experimental: "実験的", community: "コミュニティ対応", notVerified: "未確認", vendorTuned: "ベンダー最適化", architectureTuned: "アーキテクチャ最適化", portable: "移植可能", generic: "汎用", researchArtifact: "研究成果", native: "ネイティブ対応", libraryDependent: "ライブラリ依存", singleNode: "単一ノード"
    },
    en: {
      scopeTitle: "Research scope and progress", relatedTopics: "Related research topics", movedTopic: "Previous catalog entry", movedTopicNote: "This entry has been merged or transferred. Its current scope is available through the following topics or outputs.", relatedOutput: "Related public page", evidenceSections: "Related evidence collected", sharedEvidence: "Refer to the same statement and evidence",
      languageControl: "Display language", publicStatus: "Publication status", inPageNavigation: "Page navigation", openfsSummary: "OpenFS summary", tagline: "Public research catalog and system planning options", publicOnly: "Public information only", siteUpdated: "Site updated", catalogAsOf: "Catalog as of", researchAsOf: "Research as of", asOf: "As of", licenseLabel: "License",
      navOverview: "Overview", navCatalog: "Research catalog", navSearch: "Search", navRoadmaps: "Roadmaps", navScenarios: "System planning options", navReports: "Reports",
      aboutKicker: "ABOUT OPENFS",
      aboutLead: "OpenFS is a public research platform for planning future computing and data infrastructure. It continuously surveys public evidence on computer architecture, memory, networks, system software, and applications. It publishes traceable technology assessments, roadmaps, and system planning options while clearly identifying unresolved questions, the date and verification status of each item, and its Consensus status.",
      overviewKicker: "CURRENT PUBLIC STATE", overviewTitle: "Continuous research status",
      overviewLead: "Research summaries derived from public information are shown with their validation status. System planning options and reports are limited to explicitly human-approved outputs.",
      topicsMetric: "Research topics", topicsMetricNote: "Registered in the research catalog", roadmapMetric: "Published roadmaps", roadmapMetricNote: "Available on dedicated pages", scenarioMetric: "Published planning options", scenarioMetricNote: "Human-approved for publication",
      reportMetric: "Published reports", reportMetricNote: "Traceable exports", revision: "revision", officialSources: "registered public sources",
      openGaps: "Open gaps", none: "none", catalogKicker: "RESEARCH INVENTORY", catalogTitle: "Research catalog",
      catalogLead: "Each research topic distinguishes the latest status confirmed as of the research date, near-term direction, mid- to long-term R&D candidates, and unresolved questions. It also presents relevance to system planning, public evidence, coverage gaps, research history, and related roadmaps.",
      domainFilter: "Category filter", all: "All", domainArchitecture: "Architecture", domainSystemSoftware: "System software", domainApplications: "Applications", domainCrossCutting: "Cross-cutting", search: "Search", searchPlaceholder: "Display code, canonical ID, title, or category",
      tableId: "ID", tableTopic: "Research topic", tableDomain: "Category", tableStatus: "Research status", tableVerification: "Verification", tableUpdated: "Last updated", tableGaps: "Gaps",
      noTopics: "No topics match the current filters.", technologyKicker: "CONTINUOUS RESEARCH SCOPE", technologyTitle: "Technology landscape", technologyLead: "OpenFS continuously surveys technology areas relevant to HPCI infrastructure planning.", area: "AREA",
      roadmapKicker: "HARDWARE, SOFTWARE, AND APPLICATION OUTLOOKS", roadmapTitle: "Roadmaps", roadmapLead: "Choose a roadmap by category and open its dedicated timeline, supporting evidence, and implications for HPCI planning.", roadmapColumn: "Roadmap", domainColumn: "Category", horizonColumn: "Horizon", updatedColumn: "Updated", noRoadmaps: "No roadmaps have been published.", openRoadmapLibrary: "Open the roadmap library", scenarioKicker: "PLANNING OPTIONS",
      scenarioTitle: "System planning options",
      scenarioLead: "Compare architecture, system software, applications, operator impacts, technology trends, and uncertainties as a coherent whole. HPCI-specific constraints are noted within each option.",
      noScenarioTitle: "No planning options have been published",
      noScenarioText: "Evidence-backed, evaluated, and human-approved planning options will appear here.",
      openScenarioComparison: "Compare the three planning options",
      reportKicker: "REPORTS", reportTitle: "Reports and exports",
      reportLead: "Each published report records its version, as-of date, evidence provenance, and relationship to earlier versions.",
      noReportTitle: "No reports have been published",
      noReportText: "Exports appear here after acceptance by the promotion workflow and explicit human publication approval.",
      footerDescription: "HPCI-CFSP public research view", statusNotStarted: "not started", statusPartial: "partial",
      statusReviewed: "reviewed", statusRetired: "retired", verificationPending: "independent review pending", verificationAccepted: "accepted through the Consensus Gate", evidenceCollected: "evidence available; review pending", notYetReviewed: "not reviewed", noPublicUpdate: "no public result",
      findingAvailable: "public findings", decisionAvailable: "technology synthesis", summaryPending: "public findings in preparation", closeDialog: "Close details",
      topicDetailMeta: "Topic details", canonicalTopicId: "Canonical Topic ID", relatedRoadmaps: "Related roadmaps", roadmapPlanned: "(planned)", noSummaryTitle: "No public findings yet",
      noSummaryText: "No research result linked to this topic has been published yet. This page will be updated when a later research cycle produces a publishable result.",
      topicResultsKicker: "TOPIC-SPECIFIC RESULTS", topicResultsLead: "Showing {findingCount} public findings directly linked to this research topic from {runCount} research runs.",
      sourceSurvey: "SOURCE REVIEW", findings: "Research findings", sources: "Supporting sources", sourceCaveat: "Validation status for this research run",
      sourceRun: "Research run", generatedAt: "Generated", researchStatus: "Research status", coverageStatus: "Coverage", consensusStatus: "Consensus",
      consensusProof: "This information passed the Consensus Gate based on reviews from {modelCount} AI models in {groupCount} independent groups and {harnessCount} AI harness configurations.",
      consensusReceipt: "Consensus record", decision: "Decision", decidedAt: "Decided", policy: "Policy",
      participants: "Participating models and agents", harnesses: "AI harnesses", agentRole: "Role", independenceGroup: "Independence group",
      promptProfile: "Prompt profile", contribution: "Consensus contribution", assessment: "Assessment", commit: "Commit", run: "Run",
      provisional: "provisional", accepted: "accepted", coverageMet: "declared research scope covered", profileIncomplete: "primary-source review incomplete", consensusIncomplete: "Consensus review incomplete",
      memoryRoadmapKicker: "MEMORY TECHNOLOGY RESEARCH", roadmapFilter: "Technology group filter", memoryProducts: "Memory products", integration3d: "3D integration", systemEnablers: "System enablers",
      technologyColumn: "Technology", vendorColumn: "Vendor / scope", undatedColumn: "Timing not public", roadmapTableNote: "Select a milestone to view its details and sources. Blank cells indicate that no dated public milestone was confirmed, not that development has stopped.",
      technologyNotesKicker: "TECHNOLOGY NOTES", technologyNotesTitle: "Status as of the research date and implications for HPCI", currentState: "Status as of the research date", hpciImplications: "Implications for HPCI", roadmapCaveat: "Publication caveat",
      commercial: "product / volume", sample: "sample", standard: "standard", target: "published target", concept: "concept / research", undated: "timing not public", timingBasis: "Timing basis", milestoneDetail: "Milestone detail", publicSources: "Public supporting sources",
      observed: "observed", standardRelease: "standard release", vendorTarget: "vendor target", noPublicDate: "no public date", officialScanIncomplete: "continued primary-source review required",
      decisionSummary: "Technology synthesis for planning decisions", provisionalNotice: "This is a provisional synthesis of public information. Consensus review by independent models is incomplete.", regionFilter: "Filter by region and actor", allRegions: "All", currentStage: "Latest status confirmed as of the research date", nearTermStage: "Near-term direction", researchStage: "Mid- to long-term R&D candidates", contestedStage: "Competing or unresolved paths", maturity: "Maturity", timing: "Timing", confidence: "Confidence", hpciRelevance: "Relevance to HPCI planning", adoptionConditions: "Conditions to verify before adoption", actorsLabel: "Actors", actorRoles: "Roles", regionBasis: "Basis for region classification", sourceEvidence: "Public evidence", decisionDimensions: "Planning evaluation dimensions", relatedTables: "Related comparison tables", platformMatrix: "Software support across major CPUs and GPUs", numericalMatrix: "Numerical algorithms and precision support", capabilitySoftware: "Capability / software", supportLevel: "Support", optimizationLevel: "Optimization", versionLicense: "Version and license", methodSoftware: "Algorithm / software", targetPlatforms: "Target platforms", inputPrecision: "Input precision", computePrecision: "Compute precision", accumulationPrecision: "Accumulation precision", outputPrecision: "Output precision", mixedPrecision: "Mixed precision", precisionEmulation: "Precision emulation", distributedSupport: "Distributed execution", coverageGaps: "Coverage gaps", nextAction: "Next research action", researchHistory: "Research history and individual findings", researchHistoryLead: "Inspect provenance and extracted findings for each research run.", noRegionalItems: "No item matches this region filter.", high: "high", medium: "medium", low: "low", deployed: "deployed", standardized: "standardized", sampling: "sampling", announced: "announced", prototype: "prototype", research: "research", uncertain: "uncertain", production: "production", partial: "partial", experimental: "experimental", community: "community", notVerified: "not verified", vendorTuned: "vendor tuned", architectureTuned: "architecture tuned", portable: "portable", generic: "generic", researchArtifact: "research artifact", native: "native", libraryDependent: "library dependent", singleNode: "single node"
    }
  };

  const domainLabels = {
    ja: {architecture: "アーキテクチャ", "system-software": "システムソフトウェア", applications: "アプリケーション", "cross-cutting": "分野横断"},
    en: {architecture: "Architecture", "system-software": "System software", applications: "Applications", "cross-cutting": "Cross-cutting"}
  };
  const roadmapDomainLabels = {
    ja: {hardware: "ハードウェア", "system-software": "システムソフトウェア", applications: "アプリケーション", "cross-cutting": "分野横断"},
    en: {hardware: "Hardware", "system-software": "System software", applications: "Applications", "cross-cutting": "Cross-cutting"}
  };
  const statusKeys = {"not-started": "statusNotStarted", partial: "statusPartial", reviewed: "statusReviewed", retired: "statusRetired"};
  const verificationKeys = {"independent-review-pending": "verificationPending", "consensus-verified": "verificationAccepted", "evidence-collected": "evidenceCollected", "not-yet-reviewed": "notYetReviewed"};
  const roadmapGroupKeys = {"memory-products": "memoryProducts", "3d-integration": "integration3d", "system-enablers": "systemEnablers"};
  const maturityKeys = {commercial: "commercial", sample: "sample", standard: "standard", target: "target", concept: "concept", undated: "undated"};
  const timingBasisKeys = {observed: "observed", "standard-release": "standardRelease", "vendor-target": "vendorTarget", "no-public-date": "noPublicDate"};
  let activeCategory = "all";
  let language = readLanguage();
  let activeTopicId = null;
  let activeTopicRegion = "all";
  let activeRoadmapMilestoneId = null;

  function readLanguage() {
    const requested = new URLSearchParams(window.location.search).get("lang");
    if (requested === "ja" || requested === "en") return requested;
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
  function categoryLabel(categoryId) {
    const category = data.catalog_taxonomy.categories.find((item) => item.category_id === categoryId);
    return category ? category[`title_${language}`] : categoryId;
  }
  function formatJst(value) {
    const parts = new Intl.DateTimeFormat("en-CA", {
      timeZone: "Asia/Tokyo",
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
      hourCycle: "h23"
    }).formatToParts(new Date(value));
    const item = Object.fromEntries(parts.map((part) => [part.type, part.value]));
    return `${item.year}-${item.month}-${item.day}-${item.hour}:${item.minute}:${item.second} JST`;
  }
  function setText(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
  }
  function setRoadmapLinkTitle(element, value) {
    const breakAt = value.indexOf("（");
    if (breakAt <= 0) {
      element.textContent = value;
      return;
    }
    element.append(value.slice(0, breakAt), document.createElement("wbr"), value.slice(breakAt));
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
    const siteUpdated = document.getElementById("site-updated");
    siteUpdated.href = data.site.commit_url;
    siteUpdated.textContent = `${tr("siteUpdated")} ${formatJst(data.site.updated_at)} · ${data.site.commit_sha.slice(0, 7)}`;
    setText("metric-topics", data.baseline.topic_count);
    setText("metric-roadmaps", data.roadmaps.length);
    setText("metric-scenarios", data.scenarios.length);
    setText("metric-reports", data.reports.length);
    setText("catalog-as-of", data.catalog_as_of);
    setText("baseline-id", data.baseline.baseline_id);
    setText("baseline-detail", `${tr("revision")} ${data.baseline.catalog_revision} / ${tr("officialSources")} ${data.baseline.official_source_count}`);
    setText("gap-summary", `${tr("openGaps")}: ${data.baseline.open_gap_ids.join(", ") || tr("none")}`);
    setText("license-status", `${tr("licenseLabel")}: ${data.publication.license}`);
  }

  function renderRoadmapHome() {
    const root = document.getElementById("roadmap-home-rows");
    if (!root) return;
    root.replaceChildren();
    data.roadmaps.slice(0, 5).forEach((roadmap) => {
      const row = document.createElement("tr");
      const titleCell = document.createElement("td");
      const link = document.createElement("a");
      link.className = "roadmap-title-link";
      link.href = `${roadmap.path}?v=${encodeURIComponent(data.site.commit_sha)}`;
      setRoadmapLinkTitle(link, language === "ja" ? roadmap.title_ja : roadmap.title_en);
      const count = document.createElement("span");
      count.className = "roadmap-row-note";
      count.textContent = `${roadmap.track_count} ${language === "ja" ? "トラック" : "tracks"} / ${roadmap.milestone_count} ${language === "ja" ? "項目" : "milestones"}`;
      titleCell.append(link, count);
      const domain = document.createElement("td");
      domain.textContent = categoryLabel(roadmap.catalog_category_id);
      const horizon = document.createElement("td");
      horizon.textContent = `${roadmap.horizon.start_year}-${roadmap.horizon.end_year}`;
      const asOf = document.createElement("td");
      asOf.textContent = roadmap.as_of;
      const consensus = document.createElement("td");
      consensus.textContent = statusLabel(roadmap.consensus_status);
      const updated = document.createElement("td");
      const commit = document.createElement("a");
      commit.href = roadmap.source_commit_url;
      commit.target = "_blank";
      commit.rel = "noopener noreferrer";
      commit.textContent = formatJst(roadmap.updated_at);
      updated.appendChild(commit);
      row.append(titleCell, domain, horizon, asOf, consensus, updated);
      root.appendChild(row);
    });
    document.getElementById("roadmap-home-empty").hidden = data.roadmaps.length !== 0;
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
      item.textContent = `${gap.priority} · ${localized(gap, "statement")}`;
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
      const categoryMatch = activeCategory === "all" || topic.catalog_category_id === activeCategory;
      const searchText = [topic.catalog_code, topic.topic_id, topic.title_ja, topic.title_en, topic.summary_ja, topic.summary_en, ...(topic.research_units || []).flatMap((unit) => [unit.title_ja, unit.title_en, unit.question_ja, unit.question_en]), categoryLabel(topic.catalog_category_id)].join(" ").toLocaleLowerCase(language);
      return categoryMatch && (!query || searchText.includes(query));
    });

    filtered.forEach((topic) => {
      const row = document.createElement("tr");
      const idCell = document.createElement("td");
      idCell.className = "topic-id";
      idCell.textContent = topic.catalog_code;
      const titleCell = document.createElement("td");
      const titleButton = document.createElement("button");
      titleButton.type = "button";
      titleButton.className = "topic-link";
      titleButton.setAttribute("aria-haspopup", "dialog");
      const titleText = document.createElement("span");
      titleText.className = "topic-link-title";
      titleText.textContent = language === "ja" ? topic.title_ja : topic.title_en;
      const resultState = document.createElement("span");
      const resultCount = topic.decision_item_count || topic.research_finding_count;
      resultState.className = `topic-result-state${resultCount ? " available" : ""}`;
      resultState.textContent = topic.decision_item_count
        ? `${tr("decisionAvailable")} ${topic.decision_item_count}`
        : topic.research_finding_count
          ? `${tr("findingAvailable")} ${topic.research_finding_count}`
          : tr("summaryPending");
      titleButton.append(titleText, resultState);
      titleButton.addEventListener("click", () => openTopicDetail(topic.topic_id));
      titleCell.appendChild(titleButton);
      const domainCell = document.createElement("td");
      domainCell.textContent = categoryLabel(topic.catalog_category_id);
      const statusCell = document.createElement("td");
      statusCell.textContent = tr(statusKeys[topic.status] || topic.status);
      const verificationCell = document.createElement("td");
      const verification = document.createElement("span");
      verification.className = `tag verification-${topic.verification_status}`;
      verification.textContent = tr(verificationKeys[topic.verification_status] || topic.verification_status);
      verificationCell.appendChild(verification);
      const updatedCell = document.createElement("td");
      if (topic.last_updated_at && topic.last_updated_commit_url) {
        const updatedLink = document.createElement("a");
        updatedLink.href = topic.last_updated_commit_url;
        updatedLink.target = "_blank";
        updatedLink.rel = "noopener noreferrer";
        updatedLink.textContent = formatJst(topic.last_updated_at);
        updatedCell.appendChild(updatedLink);
      } else {
        updatedCell.textContent = tr("noPublicUpdate");
      }
      const gapCell = document.createElement("td");
      gapCell.className = "topic-gap-count";
      gapCell.textContent = String(topic.coverage_gap_count);
      row.append(idCell, titleCell, domainCell, statusCell, verificationCell, updatedCell, gapCell);
      root.appendChild(row);
    });
    document.getElementById("topic-empty").hidden = filtered.length !== 0;
  }

  function renderTopicCategoryFilter() {
    const root = document.getElementById("topic-category-filter");
    if (!root) return;
    root.replaceChildren();
    [{category_id: "all", title_ja: tr("all"), title_en: tr("all")}, ...data.catalog_taxonomy.categories]
      .forEach((category) => {
        const button = document.createElement("button");
        button.type = "button";
        button.dataset.category = category.category_id;
        button.textContent = category.category_id === "all" ? tr("all") : (category[`short_title_${language}`] || category[`title_${language}`]);
        button.title = category.category_id === "all" ? tr("all") : category[`title_${language}`];
        button.setAttribute("aria-label", button.title);
        button.setAttribute("aria-pressed", String(activeCategory === category.category_id));
        button.classList.toggle("active", activeCategory === category.category_id);
        button.addEventListener("click", () => {
          activeCategory = category.category_id;
          renderTopicCategoryFilter();
          renderTopics();
        });
        root.append(button);
      });
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
      .filter((summary) => (summary.catalog_topic_ids || summary.topic_ids).includes(topicId))
      .map((summary) => ({
        ...summary,
        findings: summary.findings.filter((finding) => (finding.catalog_topic_ids || finding.topic_ids).includes(topicId))
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

  function decisionProfileForTopic(topicId) {
    return data.topic_decision_support?.topic_profiles.find(
      (profile) => profile.topic_id === topicId
    ) || null;
  }

  function decisionSourceMap() {
    return new Map(
      (data.topic_decision_support?.sources || []).map((source) => [source.source_id, source])
    );
  }

  function decisionActorMap() {
    return new Map(
      (data.topic_decision_support?.actors || []).map((actor) => [actor.actor_id, actor])
    );
  }

  function decisionRegionMap() {
    return new Map(
      (data.topic_decision_support?.regions || []).map((region) => [region.region_id, region])
    );
  }

  function enumLabel(value) {
    const keys = {
      "not-verified": "notVerified",
      "vendor-tuned": "vendorTuned",
      "architecture-tuned": "architectureTuned",
      "research-artifact": "researchArtifact",
      "library-dependent": "libraryDependent",
      "single-node": "singleNode"
    };
    return tr(keys[value] || value);
  }

  function renderDecisionSources(sourceIds) {
    const sourceMap = decisionSourceMap();
    const list = document.createElement("ul");
    list.className = "source-list decision-source-list";
    sourceIds.forEach((sourceId) => {
      const source = sourceMap.get(sourceId);
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
      list.appendChild(item);
    });
    return list;
  }

  function itemMatchesRegion(item, actorMap) {
    if (activeTopicRegion === "all") return true;
    return item.actor_ids.some((actorId) => (
      actorMap.get(actorId)?.region_ids.includes(activeTopicRegion)
    ));
  }

  function profileRegionIds(profile, actorMap) {
    const values = new Set();
    profile.sections.forEach((section) => section.items.forEach((item) => {
      item.actor_ids.forEach((actorId) => {
        actorMap.get(actorId)?.region_ids.forEach((regionId) => values.add(regionId));
      });
    }));
    return values;
  }

  function renderRegionFilter(root, profile, actorMap) {
    const regionMap = decisionRegionMap();
    const available = profileRegionIds(profile, actorMap);
    if (activeTopicRegion !== "all" && !available.has(activeTopicRegion)) {
      activeTopicRegion = "all";
    }
    const toolbar = document.createElement("div");
    toolbar.className = "decision-region-toolbar";
    const label = document.createElement("strong");
    label.textContent = tr("regionFilter");
    const controls = document.createElement("div");
    controls.className = "segmented decision-region-filter";
    controls.setAttribute("role", "group");
    controls.setAttribute("aria-label", tr("regionFilter"));
    const options = [
      {region_id: "all", name_ja: tr("allRegions"), name_en: tr("allRegions")},
      ...Array.from(available).map((regionId) => regionMap.get(regionId)).filter(Boolean)
    ];
    options.forEach((region) => {
      const button = document.createElement("button");
      button.type = "button";
      button.classList.toggle("active", region.region_id === activeTopicRegion);
      button.setAttribute("aria-pressed", String(region.region_id === activeTopicRegion));
      button.textContent = localized(region, "name");
      button.addEventListener("click", () => {
        activeTopicRegion = region.region_id;
        renderTopicDetail();
      });
      controls.appendChild(button);
    });
    toolbar.append(label, controls);
    root.appendChild(toolbar);
  }

  function renderDecisionDimensions(root, profile) {
    const section = document.createElement("section");
    section.className = "decision-dimensions";
    const title = document.createElement("h3");
    title.textContent = tr("decisionDimensions");
    const list = document.createElement("div");
    list.className = "decision-dimension-list";
    profile.hpci_decision_dimensions.forEach((dimension) => {
      const item = document.createElement("article");
      const heading = document.createElement("strong");
      heading.textContent = localized(dimension, "label");
      const question = document.createElement("p");
      question.textContent = localized(dimension, "question");
      item.append(heading, question);
      list.appendChild(item);
    });
    section.append(title, list);
    root.appendChild(section);
  }

  function renderActorDetails(actorIds, actorMap) {
    const container = document.createElement("div");
    container.className = "decision-actors";
    actorIds.forEach((actorId) => {
      const actor = actorMap.get(actorId);
      if (!actor) return;
      const details = document.createElement("details");
      const summary = document.createElement("summary");
      summary.textContent = actor.name;
      const basis = document.createElement("p");
      basis.textContent = `${tr("regionBasis")}: ${localized(actor, "region_basis")}`;
      const roles = document.createElement("p");
      roles.textContent = `${tr("actorRoles")}: ${localized(actor, "roles").join(" / ")}`;
      details.append(summary, basis, roles);
      container.appendChild(details);
    });
    return container;
  }

  function renderTechnologyItem(item, actorMap) {
    const article = document.createElement("article");
    article.className = `decision-item decision-stage-${item.stage}`;
    article.id = item.item_id;
    const header = document.createElement("div");
    header.className = "decision-item-header";
    const title = document.createElement("h5");
    title.textContent = localized(item, "name");
    const badges = document.createElement("div");
    badges.className = "decision-badges";
    [enumLabel(item.maturity), `${tr("confidence")}: ${tr(item.confidence)}`].forEach((value) => {
      const badge = document.createElement("span");
      badge.textContent = value;
      badges.appendChild(badge);
    });
    header.append(title, badges);
    const timing = document.createElement("p");
    timing.className = "decision-timing";
    timing.textContent = `${tr("timing")}: ${localized(item, "timing")}`;
    const statement = document.createElement("p");
    statement.className = "decision-statement";
    statement.textContent = localized(item, "statement");
    const relevanceTitle = document.createElement("strong");
    relevanceTitle.className = "decision-subtitle";
    relevanceTitle.textContent = tr("hpciRelevance");
    const relevance = document.createElement("p");
    relevance.textContent = localized(item, "hpci_relevance");
    const conditionsTitle = document.createElement("strong");
    conditionsTitle.className = "decision-subtitle";
    conditionsTitle.textContent = tr("adoptionConditions");
    const conditions = document.createElement("ul");
    localized(item, "adoption_conditions").forEach((condition) => {
      const entry = document.createElement("li");
      entry.textContent = condition;
      conditions.appendChild(entry);
    });
    const actorsTitle = document.createElement("strong");
    actorsTitle.className = "decision-subtitle";
    actorsTitle.textContent = tr("actorsLabel");
    const sourcesTitle = document.createElement("strong");
    sourcesTitle.className = "decision-subtitle";
    sourcesTitle.textContent = tr("sourceEvidence");
    article.append(
      header, timing, statement, relevanceTitle, relevance,
      conditionsTitle, conditions, actorsTitle, renderActorDetails(item.actor_ids, actorMap),
      sourcesTitle, renderDecisionSources(item.source_ids)
    );
    article.append(topicFeedbackLink("technology", item.item_id, localized(item, "name")));
    return article;
  }

  function renderDecisionSections(root, profile, actorMap) {
    const renderedItems = new Map();
    const stageOrder = ["current", "near-term", "research", "contested"];
    const stageLabels = {
      current: "currentStage", "near-term": "nearTermStage",
      research: "researchStage", contested: "contestedStage"
    };
    let displayed = 0;
    profile.sections.forEach((profileSection) => {
      const filtered = profileSection.items.filter((item) => itemMatchesRegion(item, actorMap));
      if (!filtered.length) return;
      displayed += filtered.length;
      const section = document.createElement("section");
      section.className = "decision-technology-section";
      section.id = profileSection.section_id;
      const title = document.createElement("h3");
      title.textContent = localized(profileSection, "title");
      const summary = document.createElement("p");
      summary.className = "decision-section-summary";
      summary.textContent = localized(profileSection, "summary");
      section.append(title, summary);
      stageOrder.forEach((stage) => {
        const items = filtered.filter((item) => item.stage === stage);
        if (!items.length) return;
        const heading = document.createElement("h4");
        heading.className = `decision-stage-heading decision-stage-heading-${stage}`;
        heading.textContent = tr(stageLabels[stage]);
        const list = document.createElement("div");
        list.className = "decision-item-list";
        items.forEach((item) => {
          const key = JSON.stringify(Object.fromEntries(Object.keys(item).filter((key) => key !== "item_id").sort().map((key) => [key, item[key]])));
          const previous = renderedItems.get(key);
          if (!previous) {
            renderedItems.set(key, item.item_id);
            list.appendChild(renderTechnologyItem(item, actorMap));
            return;
          }
          const reference = document.createElement("p");
          reference.id = item.item_id;
          const link = document.createElement("a");
          link.href = `#${previous}`;
          link.textContent = `${localized(item, "name")}: ${tr("sharedEvidence")}`;
          link.addEventListener("click", (event) => { event.preventDefault(); document.getElementById(previous)?.scrollIntoView({block: "start"}); });
          reference.appendChild(link);
          list.appendChild(reference);
        });
        section.append(heading, list);
      });
      root.appendChild(section);
    });
    if (!displayed) {
      const empty = document.createElement("p");
      empty.className = "dialog-empty";
      empty.textContent = tr("noRegionalItems");
      root.appendChild(empty);
    }
  }

  function renderPlatformMatrix(root) {
    const matrix = data.topic_decision_support.platform_matrix;
    const details = document.createElement("details");
    details.className = "decision-matrix";
    details.open = true;
    const toggle = document.createElement("summary");
    toggle.textContent = localized(matrix, "title");
    const description = document.createElement("p");
    description.textContent = localized(matrix, "summary");
    const wrap = document.createElement("div");
    wrap.className = "table-wrap decision-table-wrap";
    const table = document.createElement("table");
    table.className = "decision-matrix-table software-matrix";
    const head = document.createElement("thead");
    const headRow = document.createElement("tr");
    [tr("capabilitySoftware"), ...matrix.platforms.map((platform) => platform.name)].forEach((label) => {
      const cell = document.createElement("th");
      cell.textContent = label;
      headRow.appendChild(cell);
    });
    head.appendChild(headRow);
    const body = document.createElement("tbody");
    matrix.capabilities.forEach((capability) => {
      const groupRow = document.createElement("tr");
      groupRow.className = "matrix-group-row";
      const groupCell = document.createElement("th");
      groupCell.colSpan = matrix.platforms.length + 1;
      groupCell.textContent = localized(capability, "label");
      groupRow.appendChild(groupCell);
      body.appendChild(groupRow);
      capability.entries.forEach((entry) => {
        const row = document.createElement("tr");
        const software = document.createElement("th");
        const name = document.createElement("strong");
        name.textContent = entry.software_name;
        const meta = document.createElement("small");
        meta.textContent = `${entry.version_note} / ${entry.license_class}`;
        software.append(name, meta, topicFeedbackLink("platform-matrix", entry.entry_id, entry.software_name, [capability.capability_id]));
        row.appendChild(software);
        matrix.platforms.forEach((platform) => {
          const cell = document.createElement("td");
          if (entry.platform_ids.includes(platform.platform_id)) {
            const state = document.createElement("strong");
            state.textContent = `${enumLabel(entry.support_level)} / ${enumLabel(entry.optimization_level)}`;
            const note = document.createElement("span");
            note.textContent = localized(entry, "summary");
            cell.append(state, note);
          } else {
            cell.className = "matrix-empty-cell";
            cell.textContent = "-";
          }
          row.appendChild(cell);
        });
        body.appendChild(row);
      });
    });
    table.append(head, body);
    wrap.appendChild(table);
    details.append(toggle, description, wrap);
    root.appendChild(details);
  }

  function renderNumericalMatrix(root) {
    const matrix = data.topic_decision_support.numerical_method_matrix;
    const details = document.createElement("details");
    details.className = "decision-matrix numerical-decision-matrix";
    details.open = true;
    const toggle = document.createElement("summary");
    toggle.textContent = localized(matrix, "title");
    const description = document.createElement("p");
    description.textContent = localized(matrix, "summary");
    const platformMap = new Map(
      data.topic_decision_support.platform_matrix.platforms.map((platform) => [platform.platform_id, platform])
    );
    const wrap = document.createElement("div");
    wrap.className = "table-wrap decision-table-wrap";
    const table = document.createElement("table");
    table.className = "decision-matrix-table numerical-matrix";
    const head = document.createElement("thead");
    const headRow = document.createElement("tr");
    [
      tr("methodSoftware"), tr("targetPlatforms"), tr("inputPrecision"),
      tr("computePrecision"), tr("accumulationPrecision"), tr("outputPrecision"),
      tr("mixedPrecision"), tr("precisionEmulation"), tr("distributedSupport")
    ].forEach((label) => {
      const cell = document.createElement("th");
      cell.textContent = label;
      headRow.appendChild(cell);
    });
    head.appendChild(headRow);
    const body = document.createElement("tbody");
    matrix.methods.forEach((method) => {
      const groupRow = document.createElement("tr");
      groupRow.className = "matrix-group-row";
      const groupCell = document.createElement("th");
      groupCell.colSpan = 9;
      groupCell.textContent = `${localized(method, "name")} / ${localized(method, "purpose")}`;
      groupRow.appendChild(groupCell);
      body.appendChild(groupRow);
      method.implementations.forEach((implementation) => {
        const row = document.createElement("tr");
        const software = document.createElement("th");
        const name = document.createElement("strong");
        name.textContent = implementation.software_name;
        const meta = document.createElement("small");
        meta.textContent = `${enumLabel(implementation.support_level)} / ${implementation.license_class}`;
        software.append(name, meta, topicFeedbackLink("numerical-matrix", implementation.implementation_id, implementation.software_name, [method.method_id]));
        const values = [
          implementation.platform_ids.map((platformId) => platformMap.get(platformId)?.name || platformId).join(" / "),
          implementation.precision.input,
          implementation.precision.compute,
          implementation.precision.accumulation,
          implementation.precision.output,
          implementation.precision.mixed_precision,
          implementation.precision.emulation,
          enumLabel(implementation.distributed_support)
        ];
        row.appendChild(software);
        values.forEach((value) => {
          const cell = document.createElement("td");
          cell.textContent = value;
          row.appendChild(cell);
        });
        body.appendChild(row);
      });
    });
    table.append(head, body);
    wrap.appendChild(table);
    details.append(toggle, description, wrap);
    root.appendChild(details);
  }

  function renderCoverageGaps(root, profile) {
    const gapMap = new Map(
      data.topic_decision_support.coverage_gaps.map((gap) => [gap.gap_id, gap])
    );
    const gaps = profile.coverage_gap_ids.map((gapId) => gapMap.get(gapId)).filter(Boolean);
    if (!gaps.length) return;
    const details = document.createElement("details");
    details.className = "decision-gaps";
    const toggle = document.createElement("summary");
    toggle.textContent = `${tr("coverageGaps")} (${gaps.length})`;
    const list = document.createElement("div");
    list.className = "decision-gap-list";
    gaps.forEach((gap) => {
      const item = document.createElement("article");
      const title = document.createElement("strong");
      title.textContent = `${gap.gap_id} / ${gap.priority}`;
      const question = document.createElement("p");
      question.textContent = localized(gap, "question");
      const next = document.createElement("p");
      next.textContent = `${tr("nextAction")}: ${localized(gap, "next_action")}`;
      item.append(title, question, next);
      list.appendChild(item);
    });
    details.append(toggle, list);
    root.appendChild(details);
  }

  function renderResearchHistory(root, summaries, openByDefault = false) {
    if (!summaries.length) return;
    const history = document.createElement("details");
    history.className = "research-history";
    history.open = openByDefault;
    const toggle = document.createElement("summary");
    toggle.textContent = `${tr("researchHistory")} (${summaries.length})`;
    const lead = document.createElement("p");
    lead.className = "research-history-lead";
    lead.textContent = tr("researchHistoryLead");
    history.append(toggle, lead);
    summaries.forEach((summary) => {
      const section = document.createElement("section");
      section.className = "research-summary";
      const heading = document.createElement("div");
      heading.className = "research-summary-heading";
      const title = document.createElement("h3");
      title.textContent = localized(summary, "title");
      const status = document.createElement("span");
      status.className = "summary-status";
      status.textContent = statusLabel(summary.research_status);
      heading.append(title, status);
      const summaryText = document.createElement("p");
      summaryText.className = "research-summary-text";
      summaryText.textContent = localized(summary, "summary");
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
        statement.textContent = localized(finding, "statement");
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
        const receipt = renderConsensusReceipt(finding);
        if (receipt) item.appendChild(receipt);
        findings.appendChild(item);
      });
      const caveat = document.createElement("aside");
      caveat.className = "summary-caveat";
      const caveatTitle = document.createElement("strong");
      caveatTitle.textContent = tr("sourceCaveat");
      const caveatText = document.createElement("p");
      caveatText.textContent = localized(summary, "caveat");
      caveat.append(caveatTitle, caveatText);
      section.append(heading, summaryText, meta, findingsTitle, findings, caveat);
      history.appendChild(section);
    });
    root.appendChild(history);
  }

  function topicFeedbackLink(kind, id, title, relatedIds = []) {
    return window.OpenFSFeedback.link({kind, id, title, relatedIds: [activeTopicId, ...relatedIds], path: `?topic=${encodeURIComponent(activeTopicId)}`});
  }

  function renderTopicDetail() {
    if (!activeTopicId) return;
    const topic = data.topics.find((item) => item.topic_id === activeTopicId);
    if (!topic) {
      renderTopicAlias();
      return;
    }
    setText("topic-dialog-id", topic.catalog_code);
    setText("topic-dialog-title", language === "ja" ? topic.title_ja : topic.title_en);
    setText("topic-dialog-meta", `${tr("topicDetailMeta")} / ${categoryLabel(topic.catalog_category_id)} / ${tr("canonicalTopicId")}: ${topic.topic_id}`);
    window.OpenFSFeedback.mount("topic-feedback", {kind: "topic", id: topic.topic_id, title: localized(topic, "title"), path: `?topic=${encodeURIComponent(topic.topic_id)}`});
    const root = document.getElementById("topic-dialog-content");
    root.replaceChildren();
    renderTopicScope(root, topic);
    const summaries = summariesForTopic(topic.topic_id);
    const profile = decisionProfileForTopic(topic.topic_id);
    if (!summaries.length && !profile) {
      const empty = document.createElement("div");
      empty.className = "dialog-empty";
      const title = document.createElement("strong");
      title.textContent = tr("noSummaryTitle");
      const body = document.createElement("p");
      body.textContent = tr("noSummaryText");
      empty.append(title, body);
      root.appendChild(empty);
    }
    if (profile) {
      const overview = document.createElement("section");
      overview.className = "topic-results-overview decision-overview";
      const kicker = document.createElement("span");
      kicker.className = "eyebrow";
      kicker.textContent = tr("decisionSummary");
      const text = document.createElement("p");
      text.textContent = localized(profile, "summary");
      const notice = document.createElement("p");
      notice.className = "decision-provisional-notice";
      notice.textContent = tr("provisionalNotice");
      overview.append(kicker, text, notice);
      root.appendChild(overview);
      const actorMap = decisionActorMap();
      renderRegionFilter(root, profile, actorMap);
      renderDecisionDimensions(root, profile);
      renderDecisionSections(root, profile, actorMap);
      if (profile.related_surface_ids.length) {
        const heading = document.createElement("h3");
        heading.className = "related-tables-heading";
        heading.textContent = tr("relatedTables");
        root.appendChild(heading);
      }
      if (profile.related_surface_ids.includes("platform-software")) renderPlatformMatrix(root);
      if (profile.related_surface_ids.includes("numerical-methods")) renderNumericalMatrix(root);
      renderCoverageGaps(root, profile);
    }
    if (topic.related_roadmaps.length) {
      const section = document.createElement("section");
      section.className = "topic-related-roadmaps";
      const heading = document.createElement("h3");
      heading.textContent = tr("relatedRoadmaps");
      const list = document.createElement("ul");
      list.className = "related-roadmap-list";
      topic.related_roadmaps.forEach((roadmap) => {
        const item = document.createElement("li");
        const title = language === "ja" ? roadmap.title_ja : roadmap.title_en;
        if (roadmap.path) {
          const link = document.createElement("a");
          link.href = `${roadmap.path}?v=${encodeURIComponent(data.site.commit_sha)}`;
          link.textContent = title;
          item.appendChild(link);
        } else {
          const label = document.createElement("span");
          label.textContent = title;
          const status = document.createElement("small");
          status.className = "roadmap-planned-label";
          status.textContent = tr("roadmapPlanned");
          item.append(label, status);
        }
        list.appendChild(item);
      });
      section.append(heading, list);
      root.appendChild(section);
    }
    renderResearchHistory(root, summaries, !profile);
  }

  function openTopicDetail(topicId) {
    const current = data.topics.find((topic) => topic.topic_id === topicId || topic.catalog_code === topicId);
    const alias = (data.catalog_aliases || []).find((item) => item.topic_id === topicId || item.legacy_code === topicId);
    if (!current && !alias) return;
    topicId = current ? current.topic_id : topicId;
    if (activeTopicId !== topicId) activeTopicRegion = "all";
    activeTopicId = topicId;
    const url = new URL(window.location.href);
    url.searchParams.set("topic", topicId);
    window.history.replaceState(null, "", url);
    renderTopicDetail();
    const dialog = document.getElementById("topic-dialog");
    if (!dialog.open) dialog.showModal();
  }

  function topicLinks(ids) {
    const list = document.createElement("ul");
    list.className = "related-roadmap-list";
    ids.forEach((id) => {
      const topic = data.topics.find((item) => item.topic_id === id);
      if (!topic) return;
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = `?topic=${encodeURIComponent(id)}&lang=${language}#catalog`;
      link.textContent = `${topic.catalog_code}: ${localized(topic, "title")}`;
      link.addEventListener("click", (event) => { event.preventDefault(); openTopicDetail(id); });
      item.appendChild(link);
      list.appendChild(item);
    });
    return list;
  }

  function renderTopicAlias() {
    const alias = (data.catalog_aliases || []).find((item) => item.topic_id === activeTopicId || item.legacy_code === activeTopicId);
    if (!alias) return;
    setText("topic-dialog-id", alias.legacy_code || alias.topic_id);
    setText("topic-dialog-title", localized(alias, "title"));
    setText("topic-dialog-meta", tr("movedTopic"));
    document.getElementById("topic-feedback").replaceChildren();
    const root = document.getElementById("topic-dialog-content");
    root.replaceChildren();
    const note = document.createElement("p");
    note.textContent = tr("movedTopicNote");
    root.append(note, topicLinks(alias.target_topic_ids));
    if (alias.output_path) {
      const link = document.createElement("a");
      link.href = alias.output_path;
      link.textContent = tr("relatedOutput");
      if (alias.output_path.startsWith("#")) link.addEventListener("click", () => document.getElementById("topic-dialog").close());
      root.appendChild(link);
    }
  }

  function renderTopicScope(root, topic) {
    if (!topic.summary_ja && !topic.research_units?.length) return;
    const section = document.createElement("section");
    section.className = "topic-scope";
    const heading = document.createElement("h3");
    heading.textContent = tr("scopeTitle");
    const summary = document.createElement("p");
    summary.textContent = localized(topic, "summary");
    const list = document.createElement("ul");
    list.className = "research-unit-list";
    (topic.research_units || []).forEach((unit) => {
      const item = document.createElement("li");
      const title = document.createElement("strong");
      title.textContent = localized(unit, "title");
      const status = document.createElement("span");
      status.className = "research-unit-status";
      status.textContent = tr(statusKeys[unit.status]);
      const question = document.createElement("p");
      question.textContent = localized(unit, "question");
      item.append(title, status, question);
      unit.evidence_section_ids.forEach((id, index) => {
        const link = document.createElement("a");
        link.href = `#${id}`;
        link.textContent = `${tr("evidenceSections")} ${index + 1}`;
        link.addEventListener("click", (event) => {
          event.preventDefault();
          if (activeTopicRegion !== "all") { activeTopicRegion = "all"; renderTopicDetail(); }
          document.getElementById(id)?.scrollIntoView({block: "start"});
        });
        item.appendChild(link);
      });
      list.appendChild(item);
    });
    section.append(heading, summary, list);
    if (topic.related_topic_ids?.length) {
      const related = document.createElement("h4");
      related.textContent = tr("relatedTopics");
      section.append(related, topicLinks(topic.related_topic_ids));
    }
    root.appendChild(section);
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
      const link = document.createElement("a");
      link.href = `${scenario.path}?v=${encodeURIComponent(data.site.commit_sha)}`;
      link.textContent = `${scenario.scenario_id} | ${language === "ja" ? scenario.title_ja : scenario.title_en}`;
      title.appendChild(link);
      const objective = document.createElement("p");
      objective.textContent = language === "ja" ? scenario.objective : scenario.objective_en;
      const meta = document.createElement("p");
      meta.className = "scenario-card-meta";
      meta.textContent = `${scenario.planning_horizon} · ${statusLabel(scenario.research_status)} · ${tr("consensusStatus")}: ${statusLabel(scenario.consensus_status)}`;
      item.append(title, objective, meta);
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
    renderTopicCategoryFilter();
    renderTopics();
    renderRoadmapHome();
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
  document.getElementById("topic-search").addEventListener("input", renderTopics);
  document.getElementById("topic-dialog-close").addEventListener("click", () => {
    document.getElementById("topic-dialog").close();
  });
  document.getElementById("topic-dialog").addEventListener("click", (event) => {
    if (event.target === event.currentTarget) event.currentTarget.close();
  });
  document.getElementById("topic-dialog").addEventListener("close", () => {
    activeTopicId = null;
    const url = new URL(window.location.href);
    url.searchParams.delete("topic");
    window.history.replaceState(null, "", url);
  });
  render();
  const initialTopicId = new URLSearchParams(window.location.search).get("topic");
  if (initialTopicId) openTopicDetail(initialTopicId);
})();
