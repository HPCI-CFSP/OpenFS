(function () {
  "use strict";

  const data = window.OPENFS_PUBLIC_DATA;
  const rootPrefix = document.body.dataset.rootPrefix || "../../";
  if (!data) {
    document.body.textContent = "OpenFS public data is unavailable.";
    return;
  }

  const copy = {
    ja: {
      languageControl: "表示言語", publicStatus: "公開状態", siteNavigation: "サイト内ナビゲーション", breadcrumbs: "パンくずリスト", roadmapValidation: "ロードマップの検証状況", maturityLegend: "成熟度の凡例", tagline: "公開調査カタログとシステム整備計画案", publicOnly: "公開情報のみ", siteUpdated: "サイト更新日時", licenseLabel: "ライセンス",
      navOverview: "概要", navCatalog: "調査カタログ", navSearch: "検索", navRoadmaps: "ロードマップ", navScenarios: "システム整備計画案", navReports: "報告書",
      libraryKicker: "公開ロードマップ索引", libraryTitle: "ロードマップ一覧", libraryLead: "技術、ソフトウェア、アプリケーション、運用・制度、計画評価のロードマップを共通形式で確認できます。横断比較では、相互依存関係と判断時期を同じ時間軸で確認できます。",
      compareRoadmaps: "6本を比較", openEvidence: "根拠情報の監査を開く", compareKicker: "優先度P0のロードマップ", compareTitle: "ロードマップ横断比較", compareLead: "重要なマイルストーン、一次情報の確認状況、未確認事項、ロードマップ間の依存関係を同じ尺度で比較します。",
      domainFilter: "分類で絞り込む", all: "すべて", domainHardware: "ハードウェア", domainSystemSoftware: "システムソフトウェア", domainApplications: "アプリケーション", domainCrossCutting: "分野横断", search: "検索", searchPlaceholder: "名称または分類", roadmapColumn: "ロードマップ", domainColumn: "分類", horizonColumn: "対象期間", researchAsOf: "調査基準日", researchStatus: "調査状況", coverageStatus: "調査範囲", consensusStatus: "合意判定状況", updatedColumn: "更新日時", noRoadmaps: "条件に一致するロードマップはありません。",
      roadmapKicker: "根拠付き暫定ロードマップ", roadmapFilter: "項目群で絞り込む", trackColumn: "技術・判断項目", ownerColumn: "主体／対象", quarterUnknown: "四半期未公表", undatedColumn: "時期未公表", roadmapTableNote: "世代見通しは、標準化と製品に関する複数の公開情報を統合した暫定的な期間です。世代間の重複を許容します。各矩形は公開情報から確認できる時期の範囲を示します。年だけが公表された項目はQ1-Q4、半期だけが公表された項目は該当する2四半期にまたがって表示しますが、事象がその全期間に継続することを意味しません。空欄は、日程を確認できる公開情報がないことを示します。",
      trackNotesKicker: "項目別の注記", trackNotesTitle: "最新状況とHPCIシステム整備への示唆", currentState: "最新状況（調査基準日現在）", hpciImplications: "HPCIシステム整備への示唆", roadmapCaveat: "公開時の注意事項", dependenciesKicker: "相互依存", dependenciesTitle: "他ロードマップとの依存関係", coverageGapsTitle: "未確認事項", gapImpact: "影響", gapNextAction: "次の確認",
      comparisonsKicker: "技術選択の比較", comparisonsTitle: "関連技術の比較表", comparisonsLead: "役割、利点、制約、適用先を共通の軸で比較します。", decisionUse: "判断への使い方", comparisonCaveat: "比較上の注意", glossaryKicker: "共通用語集", glossaryTitle: "このロードマップの用語", glossaryLead: "用語を選択すると、一元管理された説明と根拠資料を表示します。", termDefinition: "用語の説明", relatedTerms: "関連用語", referenceSources: "用語・比較の根拠", referenceRevision: "共通データ更新", timingWindow: "表示範囲", timingWindowNote: "表示範囲は公開情報の時期精度を表し、事象の継続期間ではありません。", quarterNotPublished: "四半期未公表",
      commercial: "製品・量産", sample: "サンプル", standard: "標準", published: "公開済み", target: "公表目標", concept: "構想・研究", pilot: "実証", decisionGate: "判断ゲート", deployment: "導入", undated: "時期未公表",
      timingBasis: "時期の根拠", timingPrecision: "時期の精度", eventType: "事象の種別", quarterPrecision: "四半期", halfYearPrecision: "半期", yearPrecision: "年", undatedPrecision: "未公表", milestoneDetail: "マイルストーン詳細", generationBandDetail: "世代見通し詳細", publicSources: "公開根拠資料", directSources: "直接参照",
      observed: "確認済み", asOfBaseline: "調査基準日現在の提供状況", standardRelease: "標準公開", vendorTarget: "ベンダー目標", projectTarget: "プロジェクト目標", policyTarget: "政策目標", openfsPlan: "OpenFS暫定計画", openfsSynthesis: "OpenFSによる統合整理", noPublicDate: "時期未公表",
      generationOutlook: "世代見通し（暫定）", generationPhase: "世代フェーズ", confidence: "確度", highConfidence: "高", mediumConfidence: "中", lowConfidence: "低", openEnded: "終了時期未確認", standardizationPhase: "標準化", introductionPhase: "導入", mainstreamPhase: "主流", transitionPhase: "移行", continuingPhase: "継続", generationWindowNote: "世代帯は、複数の公開情報を統合した時期の範囲です。世代間の重複を許容し、終了時期が未確認の矢印は、表示期間後も続く可能性を示します。",
      productEvent: "製品", standardEvent: "標準", researchEvent: "研究", policyEvent: "政策", evaluationEvent: "HPCI評価", adoptionEvent: "HPCI導入",
      provisional: "暫定", accepted: "受理済み", coverageMet: "設定した調査範囲を確認済み", consensusIncomplete: "合意判定未完了", profileIncomplete: "一次情報の継続確認が必要",
      sourceCoverage: "一次情報の登録比率", tracksUnit: "項目", milestonesUnit: "マイルストーン", gapsUnit: "未確認事項", keyMilestones: "重要なマイルストーン", selectedRoadmaps: "比較対象", dependencyMap: "依存関係一覧",
      evidenceBacked: "根拠に基づく", openfsAssessment: "OpenFS評価", requires: "必要とする", informs: "判断材料となる", constrains: "制約する", enables: "可能にする", coEvolves: "相互に発展",
      hpciInventoryKicker: "HPCI公開資源台帳", hpciInventoryTitle: "HPCIシステム構成と令和8年度提供期間", systemsCount: "掲載システム", applicationsCount: "対象アプリケーション", forecastsCount: "公開中の暫定予測", baselineDate: "基準日", systemName: "システム", provider: "提供機関", architectureClass: "構成区分", nodeCount: "ノード数", processorConfig: "プロセッサ／アクセラレータ", nodeMemory: "ノードメモリ", interconnect: "インターコネクト", nominalPeak: "公称ピーク", callAvailability: "課題募集上の期間", entriesUnit: "件", notPublished: "未公表",
      performanceForecastKicker: "EEA1アプリケーションの暫定性能予測", modelContractTitle: "分析モデル", forecastMethodTitle: "予測方法と候補構成", codeAvailabilityTitle: "公開コードと再現条件", codeAvailabilityLead: "公開コードの有無と、EEA1評価を再現するために残る確認事項を区別して示します。", codeStatusColumn: "コード公開状況", reproducibilityAssessment: "EEA1再現条件の確認状況", supportingLinks: "確認先", publicSourceConfirmed: "開発元の公開コードを確認", unreleasedInEea1Reference: "EEA1参照資料では非公開", baselineObservationsTitle: "公開された富岳実測値", applicationDomainMetric: "アプリケーション／分野指標", scalingModes: "評価方法", comparisonBases: "比較基準", uncertaintyPolicy: "不確かさの扱い", lowerBaseUpper: "下限・基準値・上限", calibrationValidation: "校正と独立検証", separated: "別々に実施", procurementUse: "調達判断への利用", prohibitedUntilValidated: "検証完了まで使用不可", numericalForecastsPending: "数値予測は未公開", analyticalForecast: "確度の低い予測", forecastRange: "暫定範囲", relativeToFugaku: "富岳と同一ノード数での相対性能", baselineSystem: "実測基準システム", designProxy: "設計仮定に基づく参考構成", candidateSystem: "比較対象", systemRole: "位置付け", modelAssumption: "アプリケーション別の仮定", acceleratorFraction: "アクセラレータへ移行できる処理の割合", scaleRetention: "1ノードから約10,000ノードまでの並列効率保持率", assumptionBasis: "仮定の根拠", nodeFp64Peak: "1ノード当たりのFP64理論ピーク性能", nodeMemoryBandwidth: "1ノード当たりのメモリ帯域", applicationColumn: "アプリケーション", workloadColumn: "入力データ／ワークロード", observedNodes: "富岳のノード数", observedValue: "実測値", observationStatus: "状況", measured: "実測済み", unavailable: "未取得", fugakuNodes: "富岳のノード数", calibrationRequired: "校正データが必要", measurementAvailable: "補助的な観測データあり", forecastAvailable: "予測値あり", notApplicable: "対象外", strongScaling: "強スケーリング", weakScaling: "弱スケーリング", throughputEnsemble: "スループット／アンサンブル", sameNodeCount: "同じノード数", sameAcceleratorCount: "同じCPU／アクセラレータ数", sameMemoryCapacity: "同じメモリ容量", samePower: "同じ消費電力", sameProcurementCost: "同じ調達費用",
      relatedCatalogTopics: "関連する調査カタログ項目",
      revisionKicker: "来歴", revisionTitle: "更新履歴と再現情報", artifactId: "成果物ID", sourceCommit: "生成元コミット", closeDialog: "詳細を閉じる", footerDescription: "HPCI-CFSP 公開調査ビュー"
    },
    en: {
      languageControl: "Display language", publicStatus: "Publication status", siteNavigation: "Site navigation", breadcrumbs: "Breadcrumbs", roadmapValidation: "Roadmap validation status", maturityLegend: "Maturity legend", tagline: "Public research catalog and system planning options", publicOnly: "Public information only", siteUpdated: "Site updated", licenseLabel: "License",
      navOverview: "Overview", navCatalog: "Research catalog", navSearch: "Search", navRoadmaps: "Roadmaps", navScenarios: "System planning options", navReports: "Reports",
      libraryKicker: "PUBLISHED ROADMAP INDEX", libraryTitle: "Roadmap library", libraryLead: "Review common-format roadmaps across technology, software, applications, operations, governance, and planning, then trace dependencies and decision timing.",
      compareRoadmaps: "Compare all six roadmaps", openEvidence: "Review evidence assurance", compareKicker: "P0 PRIORITY ROADMAPS", compareTitle: "Cross-roadmap comparison", compareLead: "Compare key milestones, primary-source coverage, coverage gaps, and dependencies across roadmaps on a common scale.",
      domainFilter: "Category filter", all: "All", domainHardware: "Hardware", domainSystemSoftware: "System software", domainApplications: "Applications", domainCrossCutting: "Cross-cutting", search: "Search", searchPlaceholder: "Title or category", roadmapColumn: "Roadmap", domainColumn: "Category", horizonColumn: "Horizon", researchAsOf: "Research as of", researchStatus: "Research status", coverageStatus: "Coverage", consensusStatus: "Consensus", updatedColumn: "Updated", noRoadmaps: "No roadmaps match the current filters.",
      roadmapKicker: "EVIDENCE-BASED PROVISIONAL ROADMAP", roadmapFilter: "Filter by track group", trackColumn: "Technology / decision track", ownerColumn: "Owner / scope", quarterUnknown: "quarter not published", undatedColumn: "Timing not public", roadmapTableNote: "Generation outlooks are provisional bands synthesized from standards and product evidence, and generations may overlap. Each ordinary rectangle shows the timing window supported by public information. A year-only item spans Q1-Q4 and a half-year item spans two quarters; neither represents event duration. Blank cells mean no dated milestone was confirmed.",
      trackNotesKicker: "TRACK NOTES", trackNotesTitle: "Status as of the research date and implications for HPCI", currentState: "Status as of the research date", hpciImplications: "Implications for HPCI", roadmapCaveat: "Publication caveat", dependenciesKicker: "INTERDEPENDENCIES", dependenciesTitle: "Dependencies on other roadmaps", coverageGapsTitle: "Coverage gaps", gapImpact: "Impact", gapNextAction: "Next check",
      comparisonsKicker: "TECHNOLOGY CHOICES", comparisonsTitle: "Related technology comparisons", comparisonsLead: "Compare roles, strengths, constraints, and suitable uses on common dimensions.", decisionUse: "How to use this comparison", comparisonCaveat: "Comparison caveat", glossaryKicker: "SHARED GLOSSARY", glossaryTitle: "Terms in this roadmap", glossaryLead: "Select a term to open its centrally maintained explanation and supporting sources.", termDefinition: "Term definition", relatedTerms: "Related terms", referenceSources: "Glossary and comparison sources", referenceRevision: "Shared data updated", timingWindow: "Displayed window", timingWindowNote: "The displayed window expresses public timing precision, not the duration of the event.", quarterNotPublished: "quarter not published",
      commercial: "product / volume", sample: "sample", standard: "standard", published: "published", target: "published target", concept: "concept / research", pilot: "pilot", decisionGate: "decision gate", deployment: "deployment", undated: "timing not public",
      timingBasis: "Timing basis", timingPrecision: "Timing precision", eventType: "Event type", quarterPrecision: "quarter", halfYearPrecision: "half-year", yearPrecision: "year", undatedPrecision: "not public", milestoneDetail: "Milestone detail", generationBandDetail: "Generation outlook detail", publicSources: "Public supporting sources", directSources: "Direct sources",
      observed: "observed", asOfBaseline: "availability as of baseline", standardRelease: "standard release", vendorTarget: "vendor target", projectTarget: "project target", policyTarget: "policy target", openfsPlan: "OpenFS provisional plan", openfsSynthesis: "OpenFS synthesis", noPublicDate: "no public date",
      generationOutlook: "Generation outlook (provisional)", generationPhase: "Generation phase", confidence: "Confidence", highConfidence: "high", mediumConfidence: "medium", lowConfidence: "low", openEnded: "end date not confirmed", standardizationPhase: "standardization", introductionPhase: "introduction", mainstreamPhase: "mainstream", transitionPhase: "transition", continuingPhase: "continuing", generationWindowNote: "A generation band synthesizes multiple public sources into a timing window. Generations may overlap, and an open-ended arrow means the generation may continue beyond the displayed horizon.",
      productEvent: "product", standardEvent: "standard", researchEvent: "research", policyEvent: "policy", evaluationEvent: "HPCI evaluation", adoptionEvent: "HPCI adoption",
      provisional: "provisional", accepted: "accepted", coverageMet: "declared scope met", consensusIncomplete: "incomplete", profileIncomplete: "continued primary-source review required",
      sourceCoverage: "Primary-source registration ratio", tracksUnit: "tracks", milestonesUnit: "milestones", gapsUnit: "gaps", keyMilestones: "Key milestones", selectedRoadmaps: "Roadmaps to compare", dependencyMap: "Dependency list",
      evidenceBacked: "evidence-backed", openfsAssessment: "OpenFS assessment", requires: "requires", informs: "informs", constrains: "constrains", enables: "enables", coEvolves: "co-evolves",
      hpciInventoryKicker: "PUBLIC HPCI RESOURCE INVENTORY", hpciInventoryTitle: "HPCI system configurations and FY2026 call availability", systemsCount: "Systems", applicationsCount: "Applications", forecastsCount: "Published provisional forecasts", baselineDate: "Baseline", systemName: "System", provider: "Provider", architectureClass: "Architecture", nodeCount: "Nodes", processorConfig: "Processor / accelerator", nodeMemory: "Node memory", interconnect: "Interconnect", nominalPeak: "Nominal peak", callAvailability: "Call availability", entriesUnit: "entries", notPublished: "not published",
      performanceForecastKicker: "EEA1 PROVISIONAL APPLICATION PERFORMANCE FORECASTS", modelContractTitle: "Analytical model", forecastMethodTitle: "Method and candidate configurations", codeAvailabilityTitle: "Public code and reproduction conditions", codeAvailabilityLead: "Code availability is shown separately from the remaining conditions required to reproduce the EEA1 evaluation.", codeStatusColumn: "Code availability", reproducibilityAssessment: "EEA1 reproduction assessment", supportingLinks: "Verified sources", publicSourceConfirmed: "Developer public code confirmed", unreleasedInEea1Reference: "Unreleased in the EEA1 reference", baselineObservationsTitle: "Published Fugaku measurements", applicationDomainMetric: "Application / domain metric", scalingModes: "Evaluation modes", comparisonBases: "Comparison bases", uncertaintyPolicy: "Treatment of uncertainty", lowerBaseUpper: "lower, central, and upper estimates", calibrationValidation: "Calibration and independent validation", separated: "must be performed separately", procurementUse: "Use in procurement decisions", prohibitedUntilValidated: "not permitted until validation", numericalForecastsPending: "No numerical forecasts are published", analyticalForecast: "low-confidence analytical forecast", forecastRange: "provisional range", relativeToFugaku: "relative performance at the same Fugaku node count", baselineSystem: "measured baseline system", designProxy: "design-assumption proxy", candidateSystem: "Candidate system", systemRole: "Role", modelAssumption: "Application-specific assumptions", acceleratorFraction: "Accelerator-eligible fraction", scaleRetention: "Scaling retention from 1 to about 10,000 nodes", assumptionBasis: "Basis for assumption", nodeFp64Peak: "FP64 theoretical peak per node", nodeMemoryBandwidth: "Memory bandwidth per node", applicationColumn: "Application", workloadColumn: "Input / workload", observedNodes: "Fugaku node count", observedValue: "Measured value", observationStatus: "Status", measured: "measured", unavailable: "unavailable", fugakuNodes: "Fugaku node count", calibrationRequired: "calibration required", measurementAvailable: "supporting measurement available", forecastAvailable: "forecast available", notApplicable: "not applicable", strongScaling: "strong scaling", weakScaling: "weak scaling", throughputEnsemble: "throughput / ensemble", sameNodeCount: "same node count", sameAcceleratorCount: "same CPU / accelerator count", sameMemoryCapacity: "same memory capacity", samePower: "same power", sameProcurementCost: "same procurement cost",
      relatedCatalogTopics: "Related research catalog topics",
      revisionKicker: "PROVENANCE", revisionTitle: "Revision and reproducibility", artifactId: "Artifact ID", sourceCommit: "Source commit", closeDialog: "Close details", footerDescription: "HPCI-CFSP public research view"
    }
  };

  const domainLabels = {
    ja: {hardware: "ハードウェア", "system-software": "システムソフトウェア", applications: "アプリケーション", "cross-cutting": "分野横断"},
    en: {hardware: "Hardware", "system-software": "System software", applications: "Applications", "cross-cutting": "Cross-cutting"}
  };
  const categoryLabels = {
    ja: {benchmark: "ベンチマーク", compute: "計算", interconnect: "インターコネクト", memory: "メモリ", packaging: "実装技術", software: "ソフトウェア"},
    en: {benchmark: "Benchmark", compute: "Compute", interconnect: "Interconnect", memory: "Memory", packaging: "Packaging", software: "Software"}
  };
  const sourceClassLabels = {
    ja: {"academic-primary": "学術一次資料", "government-official": "政府・公的機関", "project-official": "プロジェクト公式", "research-organization": "研究機関公開資料"},
    en: {"academic-primary": "academic primary source", "government-official": "government official", "project-official": "project official", "research-organization": "research organization"}
  };
  const maturityKeys = {commercial: "commercial", sample: "sample", standard: "standard", published: "published", target: "target", concept: "concept", pilot: "pilot", "decision-gate": "decisionGate", deployment: "deployment", undated: "undated"};
  const timingBasisKeys = {observed: "observed", "as-of-baseline": "asOfBaseline", "standard-release": "standardRelease", "vendor-target": "vendorTarget", "project-target": "projectTarget", "policy-target": "policyTarget", "openfs-provisional-plan": "openfsPlan", "openfs-synthesis": "openfsSynthesis", "no-public-date": "noPublicDate"};
  const timingPrecisionKeys = {quarter: "quarterPrecision", "half-year": "halfYearPrecision", year: "yearPrecision", undated: "undatedPrecision"};
  const generationPhaseKeys = {standardization: "standardizationPhase", introduction: "introductionPhase", mainstream: "mainstreamPhase", transition: "transitionPhase", continuing: "continuingPhase"};
  const confidenceKeys = {high: "highConfidence", medium: "mediumConfidence", low: "lowConfidence"};
  const eventTypeKeys = {product: "productEvent", standard: "standardEvent", research: "researchEvent", policy: "policyEvent", "hpci-evaluation": "evaluationEvent", "hpci-adoption": "adoptionEvent"};
  const relationshipKeys = {requires: "requires", informs: "informs", constrains: "constrains", enables: "enables", "co-evolves": "coEvolves"};
  const readinessKeys = {"calibration-required": "calibrationRequired", "measurement-available": "measurementAvailable", "forecast-available": "forecastAvailable", "not-applicable": "notApplicable"};
  const scalingModeKeys = {"strong-scaling": "strongScaling", "weak-scaling": "weakScaling", "throughput-ensemble": "throughputEnsemble"};
  const comparisonBasisKeys = {"same-node-count": "sameNodeCount", "same-cpu-or-accelerator-count": "sameAcceleratorCount", "same-memory-capacity": "sameMemoryCapacity", "same-power": "samePower", "same-procurement-cost": "sameProcurementCost"};
  const systemMetricKeys = {"node-fp64-peak": "nodeFp64Peak", "node-memory-bandwidth": "nodeMemoryBandwidth"};
  const page = document.body.dataset.page;
  let language = readLanguage();
  let activeCategory = "all";
  let activeRoadmapGroup = "all";
  let activeRoadmapMilestoneId = null;
  let activeRoadmapGenerationBandId = null;
  let activeTermId = null;
  const selectedRoadmaps = new Set(data.roadmaps.map((item) => item.export_id));

  function readLanguage() {
    try { const value = window.localStorage.getItem("openfs-language"); if (value === "ja" || value === "en") return value; } catch (_error) {}
    return "ja";
  }
  function rememberLanguage(value) { try { window.localStorage.setItem("openfs-language", value); } catch (_error) {} }
  function tr(key) { return copy[language][key] || key; }
  function localized(item, field) { return item?.[`${field}_${language}`] || item?.[field] || ""; }
  function categoryLabel(categoryId) { const category = data.catalog_taxonomy.categories.find((item) => item.category_id === categoryId); return category ? category[`title_${language}`] : categoryId; }
  function setText(id, value) { const element = document.getElementById(id); if (element) element.textContent = value; }
  function setRoadmapLinkTitle(element, value) {
    const breakAt = value.indexOf("（");
    if (breakAt <= 0) { element.textContent = value; return; }
    element.append(value.slice(0, breakAt), document.createElement("wbr"), value.slice(breakAt));
  }
  function formatJst(value) {
    const parts = Object.fromEntries(new Intl.DateTimeFormat("en-CA", {timeZone: "Asia/Tokyo", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false}).formatToParts(new Date(value)).filter((part) => part.type !== "literal").map((part) => [part.type, part.value]));
    return `${parts.year}-${parts.month}-${parts.day}-${parts.hour}:${parts.minute}:${parts.second} JST`;
  }
  function statusLabel(status) { return ({provisional: tr("provisional"), accepted: tr("accepted"), "official-source-scan-incomplete": tr("profileIncomplete"), "met-declared-scope": tr("coverageMet"), incomplete: tr("consensusIncomplete")})[status] || status; }
  function currentRoadmap() { return data.roadmap_artifacts.find((item) => item.export_id === document.body.dataset.roadmapId); }
  function sourceMap(roadmap) { return new Map(roadmap.sources.map((source) => [source.source_id, source])); }
  function roadmapName(roadmapId) { const item = data.roadmaps.find((roadmap) => roadmap.roadmap_id === roadmapId); return item ? (language === "ja" ? item.title_ja : item.title_en) : roadmapId; }
  function applyStaticCopy() {
    document.documentElement.lang = language;
    document.querySelectorAll("[data-i18n]").forEach((element) => { element.textContent = tr(element.dataset.i18n); });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => { element.placeholder = tr(element.dataset.i18nPlaceholder); });
    document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => { element.setAttribute("aria-label", tr(element.dataset.i18nAriaLabel)); });
    document.querySelectorAll("[data-language]").forEach((button) => { const selected = button.dataset.language === language; button.classList.toggle("active", selected); button.setAttribute("aria-pressed", String(selected)); });
    const updated = document.getElementById("site-updated"); if (updated) { updated.href = data.site.commit_url; updated.textContent = `${tr("siteUpdated")} ${formatJst(data.site.updated_at)} · ${data.site.commit_sha.slice(0, 7)}`; }
    setText("license-status", `${tr("licenseLabel")}: ${data.publication.license}`);
    const pageTitleKey = {"roadmap-index": "libraryTitle", "roadmap-compare": "compareTitle"}[page];
    if (pageTitleKey) document.title = `${tr(pageTitleKey)} | OpenFS`;
  }

  function renderRoadmapIndex() {
    const query = document.getElementById("roadmap-search").value.trim().toLocaleLowerCase(language);
    const root = document.getElementById("roadmap-rows"); root.replaceChildren();
    const filtered = data.roadmaps.filter((roadmap) => {
      const categoryMatch = activeCategory === "all" || roadmap.catalog_category_id === activeCategory;
      const searchText = [roadmap.title_ja, roadmap.title_en, categoryLabel(roadmap.catalog_category_id), roadmap.roadmap_id].join(" ").toLocaleLowerCase(language);
      return categoryMatch && (!query || searchText.includes(query));
    });
    filtered.forEach((roadmap) => {
      const row = document.createElement("tr"); const title = document.createElement("td"); const link = document.createElement("a"); link.className = "roadmap-title-link"; link.href = `../${roadmap.path}?v=${encodeURIComponent(data.site.commit_sha)}`; setRoadmapLinkTitle(link, language === "ja" ? roadmap.title_ja : roadmap.title_en);
      const note = document.createElement("span"); note.className = "roadmap-row-note"; note.textContent = `${roadmap.track_count} ${tr("tracksUnit")} / ${roadmap.milestone_count} ${tr("milestonesUnit")} / ${roadmap.coverage_gap_count} ${tr("gapsUnit")}`; title.append(link, note);
      const domain = document.createElement("td"); domain.textContent = categoryLabel(roadmap.catalog_category_id); const horizon = document.createElement("td"); horizon.textContent = `${roadmap.horizon.start_year}-${roadmap.horizon.end_year}`; const asOf = document.createElement("td"); asOf.textContent = roadmap.as_of; const research = document.createElement("td"); research.textContent = statusLabel(roadmap.research_status); const consensus = document.createElement("td"); consensus.textContent = statusLabel(roadmap.consensus_status);
      const updated = document.createElement("td"); const commit = document.createElement("a"); commit.href = roadmap.source_commit_url; commit.target = "_blank"; commit.rel = "noopener noreferrer"; commit.textContent = formatJst(roadmap.updated_at); updated.append(commit); row.append(title, domain, horizon, asOf, research, consensus, updated); root.append(row);
    });
    document.getElementById("roadmap-empty").hidden = filtered.length !== 0;
  }

  function renderRoadmapCategoryFilter() {
    const root = document.getElementById("roadmap-category-filter");
    if (!root) return;
    root.replaceChildren();
    [{category_id: "all"}, ...data.catalog_taxonomy.categories].forEach((category) => {
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.roadmapCategory = category.category_id;
      button.textContent = category.category_id === "all" ? tr("all") : category[`title_${language}`];
      button.classList.toggle("active", activeCategory === category.category_id);
      button.addEventListener("click", () => { activeCategory = category.category_id; renderRoadmapCategoryFilter(); renderRoadmapIndex(); });
      root.append(button);
    });
  }

  function appendSourceList(root, roadmap, sourceIds) {
    const sources = sourceMap(roadmap); sourceIds.forEach((sourceId) => { const source = sources.get(sourceId); if (!source) return; const item = document.createElement("li"); const link = document.createElement("a"); link.href = source.url; link.target = "_blank"; link.rel = "noopener noreferrer"; link.textContent = source.title; const publisher = document.createElement("span"); publisher.textContent = `${source.publisher} · ${sourceClassLabels[language][source.source_class] || source.source_class}`; item.append(link, publisher); root.append(item); });
  }
  function referenceData() { return data.roadmap_reference_data || {terms: [], comparison_sets: []}; }
  function termMap() { return new Map(referenceData().terms.map((term) => [term.term_id, term])); }
  function relevantTerms(roadmap) { return referenceData().terms.filter((term) => term.roadmap_ids.includes(roadmap.roadmap_id)); }
  function appendGlossaryText(root, value, roadmap) {
    const entries = relevantTerms(roadmap).flatMap((term) => term.aliases.map((alias) => ({alias, term}))).sort((left, right) => right.alias.length - left.alias.length);
    if (!value || entries.length === 0) { root.append(document.createTextNode(value || "")); return; }
    const byAlias = new Map(entries.map((entry) => [entry.alias.toLocaleLowerCase(), entry.term]));
    const escaped = entries.map((entry) => entry.alias.replace(/[.*+?^${}()|[\]\\]/g, "\\$&"));
    const matcher = new RegExp(escaped.join("|"), "giu");
    let cursor = 0; let match;
    while ((match = matcher.exec(value)) !== null) {
      const alias = match[0]; const start = match.index; const end = start + alias.length;
      const asciiStart = /^[A-Za-z0-9_]/.test(alias); const asciiEnd = /[A-Za-z0-9_]$/.test(alias);
      if ((asciiStart && /[A-Za-z0-9_]/.test(value[start - 1] || "")) || (asciiEnd && /[A-Za-z0-9_]/.test(value[end] || ""))) continue;
      root.append(document.createTextNode(value.slice(cursor, start)));
      const button = document.createElement("button"); button.type = "button"; button.className = "glossary-term-link"; button.textContent = alias; button.setAttribute("aria-haspopup", "dialog"); button.addEventListener("click", () => openRoadmapTerm(byAlias.get(alias.toLocaleLowerCase()).term_id)); root.append(button); cursor = end;
    }
    root.append(document.createTextNode(value.slice(cursor)));
  }
  function milestoneGridRange(milestone) {
    if (milestone.timing_precision === "quarter") { const start = Number(milestone.quarter.slice(1)); return [start, start + 1]; }
    if (milestone.timing_precision === "half-year") return milestone.half === "H1" ? [1, 3] : [3, 5];
    return [1, 5];
  }
  function milestonePeriodLabel(milestone) {
    if (milestone.year === null) return tr("undatedColumn");
    if (milestone.timing_precision === "quarter") return milestone.quarter;
    if (milestone.timing_precision === "half-year") return milestone.half === "H1" ? "Q1-Q2" : "Q3-Q4";
    return `Q1-Q4 · ${tr("quarterNotPublished")}`;
  }
  function placeMilestones(milestones) {
    const occupiedUntil = [];
    return [...milestones].sort((left, right) => milestoneGridRange(left)[0] - milestoneGridRange(right)[0]).map((milestone) => {
      const [start, end] = milestoneGridRange(milestone); let row = occupiedUntil.findIndex((value) => value <= start);
      if (row === -1) { row = occupiedUntil.length; occupiedUntil.push(end); } else occupiedUntil[row] = end;
      return {milestone, start, end, row: row + 1};
    });
  }
  function milestoneButton(milestone) {
    const button = document.createElement("button"); button.type = "button"; button.className = `roadmap-milestone maturity-${milestone.maturity} priority-${milestone.comparison_priority} precision-${milestone.timing_precision}`; button.setAttribute("aria-haspopup", "dialog"); button.setAttribute("aria-label", `${milestonePeriodLabel(milestone)}: ${localized(milestone, "label")}`); const period = document.createElement("span"); period.className = "roadmap-milestone-period"; period.textContent = milestonePeriodLabel(milestone); const label = document.createElement("span"); label.className = "roadmap-milestone-label"; label.textContent = localized(milestone, "label"); button.append(period, label); button.addEventListener("click", () => openRoadmapMilestone(milestone.milestone_id)); return button;
  }
  function renderRoadmapLegend() {
    const root = document.getElementById("roadmap-legend"); root.replaceChildren(); ["commercial", "sample", "standard", "published", "target", "concept", "pilot", "decision-gate", "deployment", "undated"].forEach((maturity) => { const item = document.createElement("span"); item.className = `legend-item maturity-${maturity}`; item.textContent = tr(maturityKeys[maturity]); root.append(item); });
  }
  function renderGroupFilter(roadmap) {
    const root = document.getElementById("roadmap-group-filter"); root.replaceChildren();
    [{group_id: "all"}, ...roadmap.groups].forEach((group) => { const button = document.createElement("button"); button.type = "button"; button.dataset.roadmapGroup = group.group_id; button.classList.toggle("active", group.group_id === activeRoadmapGroup); button.textContent = group.group_id === "all" ? tr("all") : localized(group, "name"); button.addEventListener("click", () => { activeRoadmapGroup = group.group_id; renderRoadmapDetail(); }); root.append(button); });
  }
  function timingBoundaryQuarter(boundary, edge) {
    if (boundary.precision === "quarter") return Number(boundary.quarter.slice(1));
    if (boundary.precision === "half-year") {
      if (boundary.half === "H1") return edge === "start" ? 1 : 2;
      return edge === "start" ? 3 : 4;
    }
    return edge === "start" ? 1 : 4;
  }
  function timingBoundaryLabel(boundary) {
    if (boundary.precision === "quarter") return `${boundary.year} ${boundary.quarter}`;
    if (boundary.precision === "half-year") return `${boundary.year} ${boundary.half === "H1" ? "Q1-Q2" : "Q3-Q4"}`;
    return `${boundary.year} Q1-Q4`;
  }
  function generationBandGridRange(band, roadmap) {
    const start = (band.start.year - roadmap.horizon.start_year) * 4 + timingBoundaryQuarter(band.start, "start");
    const end = band.end === null ? (roadmap.horizon.end_year - roadmap.horizon.start_year + 1) * 4 + 1 : (band.end.year - roadmap.horizon.start_year) * 4 + timingBoundaryQuarter(band.end, "end") + 1;
    const maximum = (roadmap.horizon.end_year - roadmap.horizon.start_year + 1) * 4 + 1;
    return [Math.max(1, start), Math.min(maximum, end)];
  }
  function generationBandPeriodLabel(band) {
    const start = timingBoundaryLabel(band.start);
    return band.end === null ? `${start} → ${tr("openEnded")}` : `${start} → ${timingBoundaryLabel(band.end)}`;
  }
  function placeGenerationBands(bands, roadmap) {
    const occupiedUntil = [];
    return [...bands].sort((left, right) => generationBandGridRange(left, roadmap)[0] - generationBandGridRange(right, roadmap)[0]).map((band) => {
      const [start, end] = generationBandGridRange(band, roadmap); let row = occupiedUntil.findIndex((value) => value <= start);
      if (row === -1) { row = occupiedUntil.length; occupiedUntil.push(end); } else occupiedUntil[row] = end;
      return {band, start, end, row: row + 1};
    });
  }
  function generationBandButton(band) {
    const button = document.createElement("button"); button.type = "button"; button.className = `roadmap-generation-band phase-${band.phase} confidence-${band.confidence}`; button.setAttribute("aria-haspopup", "dialog"); button.setAttribute("aria-label", `${generationBandPeriodLabel(band)}: ${localized(band, "label")}`); const period = document.createElement("span"); period.className = "roadmap-generation-period"; period.textContent = generationBandPeriodLabel(band); const label = document.createElement("span"); label.className = "roadmap-generation-label"; label.textContent = localized(band, "label"); button.append(period, label); button.addEventListener("click", () => openRoadmapGenerationBand(band.generation_band_id)); return button;
  }
  function roadmapTechnologyCell(roadmap, track, rowSpan) {
    const cell = document.createElement("th"); cell.scope = "rowgroup"; cell.rowSpan = rowSpan; cell.className = "roadmap-tech-column roadmap-technology-cell"; const name = document.createElement("strong"); appendGlossaryText(name, localized(track, "name"), roadmap); const group = document.createElement("span"); group.textContent = localized(roadmap.groups.find((item) => item.group_id === track.group), "name"); cell.append(name, group); return cell;
  }
  function renderRoadmapTimeline(roadmap) {
    const root = document.getElementById("roadmap-timeline"); root.replaceChildren(); const tracks = roadmap.tracks.filter((track) => activeRoadmapGroup === "all" || track.group === activeRoadmapGroup); const years = []; for (let year = roadmap.horizon.start_year; year <= roadmap.horizon.end_year; year += 1) years.push(year);
    const table = document.createElement("table"); table.className = "roadmap-table"; table.style.width = `${512 + years.length * 448}px`; table.style.minWidth = table.style.width; const colgroup = document.createElement("colgroup"); ["roadmap-tech-column", "roadmap-vendor-column", ...Array(years.length).fill("roadmap-year-column"), "roadmap-undated-column"].forEach((className) => { const col = document.createElement("col"); col.className = className; colgroup.append(col); });
    const head = document.createElement("thead"); const yearRow = document.createElement("tr"); const trackHead = document.createElement("th"); trackHead.className = "roadmap-tech-column"; trackHead.textContent = tr("trackColumn"); const ownerHead = document.createElement("th"); ownerHead.className = "roadmap-vendor-column"; ownerHead.textContent = tr("ownerColumn"); yearRow.append(trackHead, ownerHead); years.forEach((year) => { const cell = document.createElement("th"); cell.className = "roadmap-year-heading"; const label = document.createElement("strong"); label.textContent = year; const quarters = document.createElement("span"); quarters.className = "roadmap-quarter-scale"; ["Q1", "Q2", "Q3", "Q4"].forEach((quarter) => { const item = document.createElement("span"); item.textContent = quarter; quarters.append(item); }); cell.append(label, quarters); yearRow.append(cell); }); const undated = document.createElement("th"); undated.className = "roadmap-year-heading roadmap-undated-heading"; undated.textContent = tr("undatedColumn"); yearRow.append(undated); head.append(yearRow);
    const body = document.createElement("tbody"); tracks.forEach((track) => { const lanes = roadmap.lanes.filter((lane) => lane.track_id === track.track_id); const bands = track.generation_bands || []; if (bands.length > 0) { const row = document.createElement("tr"); row.className = "roadmap-generation-row"; row.append(roadmapTechnologyCell(roadmap, track, lanes.length + 1)); const owner = document.createElement("th"); owner.scope = "row"; owner.className = "roadmap-vendor-column roadmap-vendor-cell roadmap-generation-owner"; const ownerName = document.createElement("strong"); ownerName.textContent = "OpenFS"; const scope = document.createElement("span"); scope.textContent = tr("generationOutlook"); owner.append(ownerName, scope); row.append(owner); const cell = document.createElement("td"); cell.colSpan = years.length; cell.className = "roadmap-generation-cell"; const grid = document.createElement("div"); grid.className = "roadmap-generation-grid"; grid.style.gridTemplateColumns = `repeat(${years.length * 4}, minmax(0, 1fr))`; grid.style.setProperty("--quarter-width", `${100 / (years.length * 4)}%`); grid.style.setProperty("--year-width", `${100 / years.length}%`); placeGenerationBands(bands, roadmap).forEach(({band, start, end, row: gridRow}) => { const button = generationBandButton(band); button.style.gridColumn = `${start} / ${end}`; button.style.gridRow = String(gridRow); grid.append(button); }); cell.append(grid); row.append(cell); const undatedCell = document.createElement("td"); undatedCell.className = "roadmap-undated-cell roadmap-generation-undated"; row.append(undatedCell); body.append(row); } lanes.forEach((lane, laneIndex) => { const row = document.createElement("tr"); if (laneIndex === 0 && bands.length === 0) row.append(roadmapTechnologyCell(roadmap, track, lanes.length));
      const owner = document.createElement("th"); owner.scope = "row"; owner.className = "roadmap-vendor-column roadmap-vendor-cell"; const ownerName = document.createElement("strong"); ownerName.textContent = localized(lane, "owner"); const scope = document.createElement("span"); scope.textContent = localized(lane, "scope"); owner.append(ownerName, scope); row.append(owner);
      years.forEach((year) => { const cell = document.createElement("td"); cell.className = "roadmap-year-cell"; const laneGrid = document.createElement("div"); laneGrid.className = "roadmap-year-lane"; placeMilestones(lane.milestones.filter((milestone) => milestone.year === year)).forEach(({milestone, start, end, row: gridRow}) => { const button = milestoneButton(milestone); button.style.gridColumn = `${start} / ${end}`; button.style.gridRow = String(gridRow); laneGrid.append(button); }); cell.append(laneGrid); row.append(cell); }); const undatedCell = document.createElement("td"); undatedCell.className = "roadmap-undated-cell"; lane.milestones.filter((milestone) => milestone.year === null).forEach((milestone) => undatedCell.append(milestoneButton(milestone))); row.append(undatedCell); body.append(row); }); }); table.append(colgroup, head, body); root.append(table);
  }
  function renderTrackDetails(roadmap) {
    const root = document.getElementById("roadmap-track-details"); root.replaceChildren(); roadmap.tracks.filter((track) => activeRoadmapGroup === "all" || track.group === activeRoadmapGroup).forEach((track) => { const details = document.createElement("details"); details.className = "memory-technology-note"; details.id = `track-${track.track_id}`; const toggle = document.createElement("summary"); const name = document.createElement("strong"); appendGlossaryText(name, localized(track, "name"), roadmap); const summary = document.createElement("span"); appendGlossaryText(summary, localized(track, "summary"), roadmap); toggle.append(name, summary); const body = document.createElement("div"); body.className = "memory-technology-note-body"; const stateTitle = document.createElement("h4"); stateTitle.textContent = tr("currentState"); const state = document.createElement("p"); appendGlossaryText(state, localized(track, "current_state"), roadmap); const implicationTitle = document.createElement("h4"); implicationTitle.textContent = tr("hpciImplications"); const implication = document.createElement("p"); appendGlossaryText(implication, localized(track, "hpci_implications"), roadmap); const sourcesTitle = document.createElement("h4"); sourcesTitle.textContent = tr("publicSources"); const sources = document.createElement("ul"); sources.className = "source-list memory-source-list"; appendSourceList(sources, roadmap, track.source_ids); body.append(stateTitle, state, implicationTitle, implication, sourcesTitle, sources); details.append(toggle, body); root.append(details); });
  }
  function renderTechnologyComparisons(roadmap) {
    const root = document.getElementById("roadmap-comparisons");
    root.replaceChildren();
    const terms = termMap();
    const artifacts = new Map(data.roadmap_artifacts.map((item) => [item.roadmap_id, item]));
    referenceData().comparison_sets
      .filter((comparison) => comparison.roadmap_ids.includes(roadmap.roadmap_id))
      .forEach((comparison) => {
        const section = document.createElement("section");
        section.className = "technology-comparison";
        const title = document.createElement("h4");
        title.textContent = localized(comparison, "title");
        const summary = document.createElement("p");
        summary.className = "technology-comparison-summary";
        summary.textContent = localized(comparison, "summary");
        const use = document.createElement("p");
        use.className = "technology-comparison-use";
        const useLabel = document.createElement("strong");
        useLabel.textContent = `${tr("decisionUse")}: `;
        use.append(useLabel, document.createTextNode(localized(comparison, "decision_use")));
        const wrap = document.createElement("div");
        wrap.className = "technology-comparison-wrap";
        const table = document.createElement("table");
        table.className = "technology-comparison-table";
        const head = document.createElement("thead");
        const headRow = document.createElement("tr");
        const termHead = document.createElement("th");
        termHead.textContent = tr("trackColumn");
        headRow.append(termHead);
        comparison.columns.forEach((column) => {
          const cell = document.createElement("th");
          cell.textContent = localized(column, "label");
          headRow.append(cell);
        });
        head.append(headRow);
        const body = document.createElement("tbody");
        comparison.rows.forEach((row) => {
          const item = document.createElement("tr");
          const termCell = document.createElement("th");
          termCell.scope = "row";
          const term = terms.get(row.term_id);
          const button = document.createElement("button");
          button.type = "button";
          button.className = "comparison-term-link";
          button.textContent = localized(term, "label");
          button.setAttribute("aria-haspopup", "dialog");
          button.addEventListener("click", () => openRoadmapTerm(row.term_id));
          termCell.append(button);
          const sourceLinks = document.createElement("div");
          sourceLinks.className = "comparison-row-sources";
          sourceLinks.setAttribute("aria-label", tr("directSources"));
          row.source_refs.forEach((reference) => {
            const source = artifacts
              .get(reference.roadmap_id)
              ?.sources.find((entry) => entry.source_id === reference.source_id);
            if (!source) return;
            const link = document.createElement("a");
            link.href = source.url;
            link.target = "_blank";
            link.rel = "noopener noreferrer";
            link.textContent = source.title;
            sourceLinks.append(link);
          });
          termCell.append(sourceLinks);
          item.append(termCell);
          comparison.columns.forEach((column) => {
            const cell = document.createElement("td");
            const value = row.cells.find((entry) => entry.column_id === column.column_id);
            cell.textContent = localized(value, "text");
            item.append(cell);
          });
          body.append(item);
        });
        table.append(head, body);
        wrap.append(table);
        const caveat = document.createElement("p");
        caveat.className = "technology-comparison-caveat";
        const caveatLabel = document.createElement("strong");
        caveatLabel.textContent = `${tr("comparisonCaveat")}: `;
        caveat.append(caveatLabel, document.createTextNode(localized(comparison, "caveat")));
        section.append(title, summary, use, wrap, caveat);
        root.append(section);
      });
  }
  function renderGlossary(roadmap) {
    const root = document.getElementById("roadmap-glossary"); root.replaceChildren(); relevantTerms(roadmap).forEach((term) => { const item = document.createElement("article"); item.className = "roadmap-glossary-item"; const heading = document.createElement("div"); const button = document.createElement("button"); button.type = "button"; button.className = "glossary-entry-link"; button.textContent = localized(term, "label"); button.setAttribute("aria-haspopup", "dialog"); button.addEventListener("click", () => openRoadmapTerm(term.term_id)); const category = document.createElement("span"); category.textContent = categoryLabels[language][term.category] || term.category; heading.append(button, category); const definition = document.createElement("p"); definition.textContent = localized(term, "short_definition"); item.append(heading, definition); root.append(item); }); const revision = document.getElementById("roadmap-reference-updated"); revision.href = referenceData().source_commit_url; revision.textContent = `${formatJst(referenceData().updated_at)} · ${referenceData().source_commit.slice(0, 7)}`;
  }
  function renderDependencies(roadmap) {
    const root = document.getElementById("roadmap-dependencies"); root.replaceChildren(); roadmap.dependencies.forEach((dependency) => { const item = document.createElement("article"); item.className = "roadmap-dependency-item"; const route = document.createElement("p"); route.className = "dependency-route"; route.textContent = `${roadmapName(dependency.upstream_roadmap_id)} → ${roadmapName(dependency.downstream_roadmap_id)}`; const relation = document.createElement("span"); relation.className = "summary-status"; relation.textContent = `${tr(relationshipKeys[dependency.relationship])} · ${dependency.basis === "evidence-backed" ? tr("evidenceBacked") : tr("openfsAssessment")}`; const statement = document.createElement("p"); appendGlossaryText(statement, localized(dependency, "statement"), roadmap); item.append(route, relation, statement); root.append(item); });
  }
  function renderCoverageGaps(roadmap) {
    const root = document.getElementById("roadmap-gaps"); root.replaceChildren(); roadmap.coverage_gaps.forEach((gap) => { const item = document.createElement("li"); const scope = document.createElement("strong"); scope.textContent = `${gap.priority} · ${gap.gap_id} · ${localized(gap, "scope")}`; const impact = document.createElement("span"); impact.textContent = `${tr("gapImpact")}: ${localized(gap, "impact")}`; const action = document.createElement("span"); action.textContent = `${tr("gapNextAction")}: ${localized(gap, "next_action")}`; item.append(scope, impact, action); root.append(item); });
  }
  function appendSupplementMeta(root, label, value, href) {
    const item = document.createElement("div"); const term = document.createElement("dt"); term.textContent = label; const description = document.createElement("dd");
    if (href) { const link = document.createElement("a"); link.href = href; link.target = "_blank"; link.rel = "noopener noreferrer"; link.textContent = value; description.append(link); } else { description.textContent = value; }
    item.append(term, description); root.append(item);
  }
  function appendSupplementSources(root, supplement) {
    root.replaceChildren(); supplement.sources.forEach((source) => { const item = document.createElement("li"); const link = document.createElement("a"); link.href = source.url; link.target = "_blank"; link.rel = "noopener noreferrer"; link.textContent = source.title; const meta = document.createElement("span"); meta.textContent = `${source.publisher} · ${sourceClassLabels[language][source.source_class] || source.source_class}`; item.append(link, meta); root.append(item); });
  }
  function appendSupplementGaps(root, supplement) {
    root.replaceChildren(); supplement.coverage_gaps.forEach((gap) => { const item = document.createElement("li"); const scope = document.createElement("strong"); scope.textContent = `${gap.priority} · ${gap.gap_id} · ${localized(gap, "scope")}`; const impact = document.createElement("span"); impact.textContent = `${tr("gapImpact")}: ${localized(gap, "impact")}`; const action = document.createElement("span"); action.textContent = `${tr("gapNextAction")}: ${localized(gap, "next_action")}`; item.append(scope, impact, action); root.append(item); });
  }
  function formatPublicNumber(value) {
    if (value === null || value === undefined) return tr("notPublished");
    return new Intl.NumberFormat(language === "ja" ? "ja-JP" : "en-US", {maximumFractionDigits: 4}).format(value);
  }
  function availabilityLabel(windows) {
    return windows.map((window) => `${window.start.year} ${window.start.quarter}–${window.end.year} ${window.end.quarter}`).join(" / ");
  }
  function renderHPCIInventory(roadmap) {
    const section = document.getElementById("hpci-system-inventory-section"); const inventory = data.hpci_system_inventory; const visible = roadmap.roadmap_id === "RM-X-BLUEPRINT" && inventory;
    section.hidden = !visible; if (!visible) return;
    setText("hpci-inventory-scope", localized(inventory, "scope")); setText("hpci-inventory-semantics", localized(inventory, "availability_semantics")); setText("hpci-inventory-caveat", localized(inventory, "caveat"));
    const meta = document.getElementById("hpci-inventory-meta"); meta.replaceChildren(); appendSupplementMeta(meta, tr("baselineDate"), inventory.as_of); appendSupplementMeta(meta, tr("systemsCount"), `${inventory.systems.length} ${tr("entriesUnit")}`); appendSupplementMeta(meta, tr("consensusStatus"), statusLabel(inventory.consensus_status)); appendSupplementMeta(meta, tr("sourceCommit"), `${formatJst(inventory.updated_at)} · ${inventory.source_commit.slice(0, 7)}`, inventory.source_commit_url);
    const table = document.createElement("table"); table.className = "supplement-table hpci-inventory-table"; const head = document.createElement("thead"); const headRow = document.createElement("tr"); [tr("systemName"), tr("architectureClass"), tr("nodeCount"), tr("processorConfig"), tr("nodeMemory"), tr("interconnect"), tr("nominalPeak"), tr("callAvailability")].forEach((label) => { const cell = document.createElement("th"); cell.textContent = label; headRow.append(cell); }); head.append(headRow); const body = document.createElement("tbody");
    inventory.systems.forEach((system) => { const row = document.createElement("tr"); const systemCell = document.createElement("th"); systemCell.scope = "row"; const name = document.createElement("strong"); name.textContent = localized(system, "name"); const provider = document.createElement("span"); provider.textContent = localized(system, "provider"); systemCell.append(name, provider); const architecture = document.createElement("td"); architecture.textContent = system.architecture_class; const nodes = document.createElement("td"); nodes.textContent = formatPublicNumber(system.specifications.node_count); const configuration = document.createElement("td"); configuration.textContent = [system.specifications.processor, system.specifications.accelerator].filter(Boolean).join(" / ") || tr("notPublished"); const memory = document.createElement("td"); memory.textContent = system.specifications.node_memory || tr("notPublished"); const interconnect = document.createElement("td"); interconnect.textContent = system.specifications.interconnect || tr("notPublished"); const peak = document.createElement("td"); peak.textContent = system.specifications.system_peak_pf === null ? tr("notPublished") : `${formatPublicNumber(system.specifications.system_peak_pf)} PF`; const availability = document.createElement("td"); const window = document.createElement("span"); window.className = `availability-window evidence-${system.evidence_status}`; window.textContent = availabilityLabel(system.availability_windows); availability.append(window); row.append(systemCell, architecture, nodes, configuration, memory, interconnect, peak, availability); body.append(row); });
    table.append(head, body); const root = document.getElementById("hpci-inventory-table"); root.replaceChildren(table); appendSupplementSources(document.getElementById("hpci-inventory-sources"), inventory); appendSupplementGaps(document.getElementById("hpci-inventory-gaps"), inventory);
  }
  function renderApplicationPerformance(roadmap) {
    const section = document.getElementById("application-performance-section"); const performance = data.application_performance_forecasts; const visible = roadmap.roadmap_id === "RM-APP-WORKLOADS" && performance;
    section.hidden = !visible; if (!visible) return;
    setText("application-performance-title", localized(performance, "title")); setText("application-performance-summary", localized(performance, "summary")); setText("application-performance-equation", localized(performance.model_contract, "equation")); setText("application-performance-flops", localized(performance.metric_policy, "flops_policy")); setText("application-performance-caveat", localized(performance, "caveat"));
    const meta = document.getElementById("application-performance-meta"); meta.replaceChildren(); appendSupplementMeta(meta, tr("baselineDate"), performance.as_of); appendSupplementMeta(meta, tr("applicationsCount"), `${performance.applications.length} ${tr("entriesUnit")}`); appendSupplementMeta(meta, tr("forecastsCount"), performance.forecasts.length === 0 ? tr("numericalForecastsPending") : `${performance.forecasts.length} ${tr("entriesUnit")}`); appendSupplementMeta(meta, tr("consensusStatus"), statusLabel(performance.consensus_status)); appendSupplementMeta(meta, tr("sourceCommit"), `${formatJst(performance.updated_at)} · ${performance.source_commit.slice(0, 7)}`, performance.source_commit_url);
    const policies = document.getElementById("application-performance-policies"); policies.replaceChildren(); const uncertainty = performance.model_contract.required_uncertainty === "lower-base-upper" ? tr("lowerBaseUpper") : performance.model_contract.required_uncertainty; const policyGroups = [[tr("scalingModes"), performance.scaling_modes.map((item) => tr(scalingModeKeys[item])).join(" / ")], [tr("comparisonBases"), performance.comparison_bases.map((item) => tr(comparisonBasisKeys[item])).join(" / ")], [tr("uncertaintyPolicy"), uncertainty], [tr("calibrationValidation"), tr("separated")], [tr("procurementUse"), tr("prohibitedUntilValidated")]]; policyGroups.forEach(([label, value]) => { const item = document.createElement("span"); const strong = document.createElement("strong"); strong.textContent = `${label}: `; item.append(strong, document.createTextNode(value)); policies.append(item); });

    const methodRoot = document.getElementById("application-performance-method"); methodRoot.replaceChildren();
    const systems = document.createElement("div"); systems.className = "forecast-system-list";
    performance.candidate_systems.forEach((system) => {
      const article = document.createElement("article"); const title = document.createElement("h5"); title.textContent = localized(system, "name"); const role = document.createElement("span"); role.className = "forecast-system-role"; role.textContent = tr(system.role === "baseline" ? "baselineSystem" : "designProxy"); const description = document.createElement("p"); description.textContent = localized(system, "description"); const metrics = document.createElement("dl"); system.metrics.forEach((metric) => { const item = document.createElement("div"); const term = document.createElement("dt"); term.textContent = tr(systemMetricKeys[metric.metric_id] || metric.metric_id); const value = document.createElement("dd"); value.textContent = `${formatPublicNumber(metric.value)} ${metric.unit}`; item.append(term, value); metrics.append(item); }); article.append(role, title, description, metrics); systems.append(article);
    });
    const methodNotes = document.createElement("div"); methodNotes.className = "forecast-method-notes"; [localized(performance.model_contract, "scale_equation"), localized(performance.model_contract, "interval_method"), localized(performance.model_contract, "limitations")].forEach((value) => { const paragraph = document.createElement("p"); paragraph.textContent = value; methodNotes.append(paragraph); });
    const assumptions = document.createElement("table"); assumptions.className = "supplement-table forecast-assumption-table"; const assumptionHead = document.createElement("thead"); const assumptionHeadRow = document.createElement("tr"); [tr("modelAssumption"), tr("acceleratorFraction"), tr("scaleRetention"), tr("assumptionBasis")].forEach((label) => { const cell = document.createElement("th"); cell.textContent = label; assumptionHeadRow.append(cell); }); assumptionHead.append(assumptionHeadRow); const assumptionBody = document.createElement("tbody"); performance.assumptions.forEach((assumption) => { const row = document.createElement("tr"); const app = performance.applications.find((item) => item.application_id === assumption.application_id); const name = document.createElement("th"); name.scope = "row"; name.textContent = app?.name || assumption.application_id; const fraction = document.createElement("td"); fraction.textContent = `${Math.round(assumption.accelerator_eligible_fraction * 100)}%`; const retention = document.createElement("td"); retention.textContent = assumption.scale_retention.map((item) => `${formatPublicNumber(item.fugaku_nodes)}:${formatPublicNumber(item.factor)}`).join(" / "); const basis = document.createElement("td"); basis.textContent = localized(assumption, "basis"); row.append(name, fraction, retention, basis); assumptionBody.append(row); }); assumptions.append(assumptionHead, assumptionBody); const assumptionWrap = document.createElement("div"); assumptionWrap.className = "supplement-table-wrap"; assumptionWrap.append(assumptions); methodRoot.append(systems, methodNotes, assumptionWrap);

    const codeSources = new Map(performance.sources.map((source) => [source.source_id, source]));
    const codeTable = document.createElement("table"); codeTable.className = "supplement-table forecast-code-table";
    const codeHead = document.createElement("thead"); const codeHeadRow = document.createElement("tr");
    [tr("applicationColumn"), tr("codeStatusColumn"), tr("reproducibilityAssessment"), tr("supportingLinks")].forEach((label) => { const cell = document.createElement("th"); cell.textContent = label; codeHeadRow.append(cell); });
    codeHead.append(codeHeadRow); const codeBody = document.createElement("tbody");
    performance.applications.forEach((application) => {
      const row = document.createElement("tr"); const name = document.createElement("th"); name.scope = "row"; name.textContent = application.name;
      const status = document.createElement("td"); const badge = document.createElement("span"); badge.className = `code-availability-badge code-${application.code_availability.status}`; badge.textContent = tr(application.code_availability.status === "public-source-confirmed" ? "publicSourceConfirmed" : "unreleasedInEea1Reference"); status.append(badge);
      const note = document.createElement("td"); note.textContent = localized(application.code_availability, "note");
      const links = document.createElement("td"); const list = document.createElement("ul"); list.className = "forecast-code-links";
      application.code_availability.source_ids.forEach((sourceId) => { const source = codeSources.get(sourceId); if (!source) return; const item = document.createElement("li"); const link = document.createElement("a"); link.href = source.url; link.target = "_blank"; link.rel = "noopener noreferrer"; link.textContent = source.title; item.append(link); list.append(item); });
      links.append(list); row.append(name, status, note, links); codeBody.append(row);
    });
    codeTable.append(codeHead, codeBody); document.getElementById("application-code-availability").replaceChildren(codeTable);

    const baselineTable = document.createElement("table"); baselineTable.className = "supplement-table forecast-baseline-table"; const baselineHead = document.createElement("thead"); const baselineHeadRow = document.createElement("tr"); [tr("applicationColumn"), tr("workloadColumn"), tr("observedNodes"), tr("observedValue"), tr("observationStatus")].forEach((label) => { const cell = document.createElement("th"); cell.textContent = label; baselineHeadRow.append(cell); }); baselineHead.append(baselineHeadRow); const baselineBody = document.createElement("tbody"); performance.baseline_observations.forEach((observation) => { const row = document.createElement("tr"); const app = performance.applications.find((item) => item.application_id === observation.application_id); const appCell = document.createElement("th"); appCell.scope = "row"; appCell.textContent = app?.name || observation.application_id; const workload = document.createElement("td"); workload.textContent = observation.workload; const nodes = document.createElement("td"); nodes.textContent = formatPublicNumber(observation.fugaku_nodes); const value = document.createElement("td"); value.textContent = observation.value === null ? "N/A" : `${formatPublicNumber(observation.value)} ${observation.unit}`; const status = document.createElement("td"); status.textContent = tr(observation.status === "measured" ? "measured" : "unavailable"); row.title = localized(observation, "note"); row.append(appCell, workload, nodes, value, status); baselineBody.append(row); }); baselineTable.append(baselineHead, baselineBody); document.getElementById("application-performance-baselines").replaceChildren(baselineTable);

    const table = document.createElement("table"); table.className = "supplement-table performance-matrix"; const head = document.createElement("thead"); const headRow = document.createElement("tr"); const appHead = document.createElement("th"); appHead.textContent = tr("applicationDomainMetric"); headRow.append(appHead); performance.standard_fugaku_node_scales.forEach((scale) => { const cell = document.createElement("th"); cell.textContent = `${formatPublicNumber(scale)} ${tr("fugakuNodes")}`; headRow.append(cell); }); head.append(headRow); const body = document.createElement("tbody");
    performance.applications.forEach((application) => { const row = document.createElement("tr"); const app = document.createElement("th"); app.scope = "row"; const name = document.createElement("strong"); name.textContent = application.name; const domain = document.createElement("span"); domain.textContent = localized(application, "domain"); const metric = document.createElement("small"); metric.textContent = `${localized(application, "primary_metric")} / ${localized(application, "domain_metric")}`; app.append(name, domain, metric); row.append(app); performance.standard_fugaku_node_scales.forEach((scale) => { const readiness = application.scale_readiness.find((item) => item.fugaku_nodes === scale); const forecast = performance.forecasts.find((item) => item.application_id === application.application_id && item.fugaku_nodes === scale); const cell = document.createElement("td"); if (forecast) { cell.className = "readiness-cell readiness-forecast-available forecast-value-cell"; const badge = document.createElement("span"); badge.className = "readiness-badge"; badge.textContent = tr("analyticalForecast"); const value = document.createElement("strong"); value.className = "forecast-base"; value.textContent = `${formatPublicNumber(forecast.estimate.base)}×`; const range = document.createElement("small"); range.className = "forecast-range"; range.textContent = `${tr("forecastRange")} ${formatPublicNumber(forecast.estimate.lower)}–${formatPublicNumber(forecast.estimate.upper)}×`; const basis = document.createElement("small"); basis.className = "forecast-basis"; basis.textContent = tr("relativeToFugaku"); cell.title = localized(readiness, "reason"); cell.append(badge, value, range, basis); } else { cell.className = `readiness-cell readiness-${readiness.status}`; const badge = document.createElement("span"); badge.className = "readiness-badge"; badge.textContent = tr(readinessKeys[readiness.status]); const reason = document.createElement("small"); reason.textContent = localized(readiness, "reason"); cell.append(badge, reason); } row.append(cell); }); body.append(row); });
    table.append(head, body); const root = document.getElementById("application-performance-table"); root.replaceChildren(table); appendSupplementSources(document.getElementById("application-performance-sources"), performance); appendSupplementGaps(document.getElementById("application-performance-gaps"), performance);
  }
  function renderRoadmapDetail() {
    const roadmap = currentRoadmap(); if (!roadmap) { document.querySelector("main").textContent = tr("noRoadmaps"); return; } document.title = `${localized(roadmap, "title")} | OpenFS`; setText("roadmap-breadcrumb-title", localized(roadmap, "title")); setText("roadmap-title", localized(roadmap, "title")); setText("roadmap-summary", localized(roadmap, "summary")); setText("roadmap-as-of", roadmap.as_of); setText("roadmap-horizon", `${roadmap.horizon.start_year}-${roadmap.horizon.end_year}`); setText("roadmap-research-status", statusLabel(roadmap.research_status)); setText("roadmap-coverage-status", statusLabel(roadmap.coverage_status)); setText("roadmap-consensus-status", statusLabel(roadmap.consensus_status)); setText("roadmap-caveat-text", localized(roadmap, "caveat")); setText("roadmap-artifact-id", roadmap.export_id); setText("roadmap-revision-updated", formatJst(roadmap.updated_at));
    const updated = document.getElementById("roadmap-updated"); updated.href = roadmap.source_commit_url; updated.textContent = formatJst(roadmap.updated_at); const commit = document.getElementById("roadmap-source-commit"); commit.href = roadmap.source_commit_url; commit.textContent = roadmap.source_commit; setText("roadmap-source-coverage", `${roadmap.source_coverage.primary_source_count}/${roadmap.source_coverage.source_count} (${Math.round(roadmap.source_coverage.primary_source_ratio * 100)}%)`); renderRelatedTopics(roadmap); renderGroupFilter(roadmap); renderRoadmapLegend(); renderRoadmapTimeline(roadmap); renderHPCIInventory(roadmap); renderApplicationPerformance(roadmap); renderTechnologyComparisons(roadmap); renderTrackDetails(roadmap); renderGlossary(roadmap); renderDependencies(roadmap); renderCoverageGaps(roadmap);
  }
  function renderRelatedTopics(roadmap) {
    const root = document.getElementById("roadmap-related-topics");
    root.replaceChildren();
    roadmap.related_topics.forEach((topic) => {
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = `${rootPrefix}?topic=${encodeURIComponent(topic.topic_id)}&v=${encodeURIComponent(data.site.commit_sha)}`;
      link.textContent = `${topic.catalog_code} · ${localized(topic, "title")}`;
      item.appendChild(link);
      root.appendChild(item);
    });
  }
  function findRoadmapMilestone(milestoneId) { const roadmap = currentRoadmap(); for (const lane of roadmap.lanes) { const milestone = lane.milestones.find((item) => item.milestone_id === milestoneId); if (milestone) return {roadmap, track: roadmap.tracks.find((item) => item.track_id === lane.track_id), lane, milestone}; } return null; }
  function findRoadmapGenerationBand(generationBandId) { const roadmap = currentRoadmap(); for (const track of roadmap.tracks) { const band = (track.generation_bands || []).find((item) => item.generation_band_id === generationBandId); if (band) return {roadmap, track, band}; } return null; }
  function appendMetaItem(root, label, value) { const item = document.createElement("div"); const term = document.createElement("dt"); term.textContent = label; const description = document.createElement("dd"); description.textContent = value; item.append(term, description); root.append(item); }
  function renderRoadmapDialog() {
    if (activeRoadmapGenerationBandId) { renderRoadmapGenerationBandDialog(); return; }
    if (!activeRoadmapMilestoneId) return; const match = findRoadmapMilestone(activeRoadmapMilestoneId); if (!match) return; const {roadmap, track, lane, milestone} = match; const period = milestone.year === null ? tr("undatedColumn") : `${milestone.year} ${milestonePeriodLabel(milestone)}`; setText("roadmap-dialog-id", milestone.milestone_id); setText("roadmap-dialog-title", localized(milestone, "label")); setText("roadmap-dialog-meta", `${localized(track, "name")} / ${localized(lane, "owner")} / ${period}`);
    const root = document.getElementById("roadmap-dialog-content"); root.replaceChildren(); const section = document.createElement("section"); section.className = "roadmap-milestone-detail"; const status = document.createElement("span"); status.className = `summary-status maturity-${milestone.maturity}`; status.textContent = tr(maturityKeys[milestone.maturity]); const title = document.createElement("h3"); title.textContent = tr("milestoneDetail"); const detail = document.createElement("p"); appendGlossaryText(detail, localized(milestone, "detail"), roadmap); const meta = document.createElement("dl"); meta.className = "research-meta roadmap-dialog-meta-list"; appendMetaItem(meta, tr("trackColumn"), localized(track, "name")); appendMetaItem(meta, tr("ownerColumn"), `${localized(lane, "owner")} / ${localized(lane, "scope")}`); appendMetaItem(meta, tr("eventType"), tr(eventTypeKeys[milestone.event_type])); appendMetaItem(meta, tr("timingBasis"), tr(timingBasisKeys[milestone.timing_basis])); appendMetaItem(meta, tr("timingPrecision"), tr(timingPrecisionKeys[milestone.timing_precision])); appendMetaItem(meta, tr("timingWindow"), period); appendMetaItem(meta, tr("researchAsOf"), roadmap.as_of); const timingNote = document.createElement("p"); timingNote.className = "roadmap-timing-note"; timingNote.textContent = tr("timingWindowNote"); const sourcesTitle = document.createElement("h4"); sourcesTitle.textContent = tr("publicSources"); const sources = document.createElement("ul"); sources.className = "source-list roadmap-dialog-source-list"; appendSourceList(sources, roadmap, milestone.source_ids); section.append(status, title, detail, meta, timingNote, sourcesTitle, sources); root.append(section);
  }
  function renderRoadmapGenerationBandDialog() {
    const match = findRoadmapGenerationBand(activeRoadmapGenerationBandId); if (!match) return; const {roadmap, track, band} = match; const period = generationBandPeriodLabel(band); setText("roadmap-dialog-id", band.generation_band_id); setText("roadmap-dialog-title", localized(band, "label")); setText("roadmap-dialog-meta", `${localized(track, "name")} / ${tr("generationOutlook")} / ${period}`); const root = document.getElementById("roadmap-dialog-content"); root.replaceChildren(); const section = document.createElement("section"); section.className = "roadmap-milestone-detail roadmap-generation-detail"; const status = document.createElement("span"); status.className = "summary-status"; status.textContent = statusLabel(band.consensus_status); const title = document.createElement("h3"); title.textContent = tr("generationBandDetail"); const detail = document.createElement("p"); appendGlossaryText(detail, localized(band, "detail"), roadmap); const meta = document.createElement("dl"); meta.className = "research-meta roadmap-dialog-meta-list"; appendMetaItem(meta, tr("trackColumn"), localized(track, "name")); appendMetaItem(meta, tr("generationPhase"), tr(generationPhaseKeys[band.phase])); appendMetaItem(meta, tr("timingBasis"), tr(timingBasisKeys[band.timing_basis])); appendMetaItem(meta, tr("confidence"), tr(confidenceKeys[band.confidence])); appendMetaItem(meta, tr("timingWindow"), period); appendMetaItem(meta, tr("consensusStatus"), statusLabel(band.consensus_status)); appendMetaItem(meta, tr("researchAsOf"), roadmap.as_of); const timingNote = document.createElement("p"); timingNote.className = "roadmap-timing-note"; timingNote.textContent = tr("generationWindowNote"); const sourcesTitle = document.createElement("h4"); sourcesTitle.textContent = tr("publicSources"); const sources = document.createElement("ul"); sources.className = "source-list roadmap-dialog-source-list"; appendSourceList(sources, roadmap, band.source_ids); section.append(status, title, detail, meta, timingNote, sourcesTitle, sources); root.append(section);
  }
  function openRoadmapMilestone(milestoneId) { activeRoadmapGenerationBandId = null; activeRoadmapMilestoneId = milestoneId; renderRoadmapDialog(); const dialog = document.getElementById("roadmap-dialog"); if (!dialog.open) dialog.showModal(); }
  function openRoadmapGenerationBand(generationBandId) { activeRoadmapMilestoneId = null; activeRoadmapGenerationBandId = generationBandId; renderRoadmapDialog(); const dialog = document.getElementById("roadmap-dialog"); if (!dialog.open) dialog.showModal(); }
  function appendReferenceSourceList(root, sourceRefs) {
    sourceRefs.forEach((sourceRef) => { const roadmap = data.roadmap_artifacts.find((item) => item.roadmap_id === sourceRef.roadmap_id); const source = roadmap?.sources.find((item) => item.source_id === sourceRef.source_id); if (!source) return; const item = document.createElement("li"); const link = document.createElement("a"); link.href = source.url; link.target = "_blank"; link.rel = "noopener noreferrer"; link.textContent = source.title; const publisher = document.createElement("span"); publisher.textContent = `${roadmapName(sourceRef.roadmap_id)} · ${source.publisher} · ${sourceRef.source_id}`; item.append(link, publisher); root.append(item); });
  }
  function renderRoadmapTermDialog() {
    if (!activeTermId) return; const term = termMap().get(activeTermId); if (!term) return; setText("roadmap-term-dialog-id", term.term_id); setText("roadmap-term-dialog-title", localized(term, "label")); setText("roadmap-term-dialog-meta", `${categoryLabels[language][term.category] || term.category} · ${referenceData().as_of}`); const root = document.getElementById("roadmap-term-dialog-content"); root.replaceChildren(); const section = document.createElement("section"); section.className = "roadmap-term-detail"; const title = document.createElement("h3"); title.textContent = tr("termDefinition"); const definition = document.createElement("p"); definition.textContent = localized(term, "definition"); const relatedTitle = document.createElement("h4"); relatedTitle.textContent = tr("relatedTerms"); const related = document.createElement("div"); related.className = "roadmap-related-terms"; term.related_term_ids.forEach((termId) => { const relatedTerm = termMap().get(termId); if (!relatedTerm) return; const button = document.createElement("button"); button.type = "button"; button.className = "related-term-link"; button.textContent = localized(relatedTerm, "label"); button.addEventListener("click", () => { activeTermId = termId; renderRoadmapTermDialog(); }); related.append(button); }); const sourcesTitle = document.createElement("h4"); sourcesTitle.textContent = tr("referenceSources"); const sources = document.createElement("ul"); sources.className = "source-list roadmap-dialog-source-list"; appendReferenceSourceList(sources, term.source_refs); section.append(title, definition, relatedTitle, related, sourcesTitle, sources); root.append(section);
  }
  function openRoadmapTerm(termId) { activeTermId = termId; const url = new URL(window.location.href); url.searchParams.set("term", termId); window.history.replaceState(null, "", url); renderRoadmapTermDialog(); const dialog = document.getElementById("roadmap-term-dialog"); if (!dialog.open) dialog.showModal(); }

  function renderCompareControls() {
    const root = document.getElementById("compare-controls"); root.replaceChildren(); data.roadmaps.forEach((roadmap) => { const label = document.createElement("label"); label.className = "compare-option"; const input = document.createElement("input"); input.type = "checkbox"; input.checked = selectedRoadmaps.has(roadmap.export_id); input.addEventListener("change", () => { input.checked ? selectedRoadmaps.add(roadmap.export_id) : selectedRoadmaps.delete(roadmap.export_id); renderComparison(); }); const text = document.createElement("span"); text.textContent = language === "ja" ? roadmap.title_ja : roadmap.title_en; label.append(input, text); root.append(label); });
  }
  function renderCompareMetrics(artifacts) {
    const root = document.getElementById("compare-metrics"); root.replaceChildren(); artifacts.forEach((roadmap) => { const card = document.createElement("article"); card.className = "compare-metric"; const title = document.createElement("h3"); const link = document.createElement("a"); link.href = `../${roadmap.slug}/`; link.textContent = localized(roadmap, "title"); title.append(link); const values = document.createElement("dl"); [[tr("sourceCoverage"), `${roadmap.source_coverage.primary_source_count}/${roadmap.source_coverage.source_count}`], [tr("keyMilestones"), roadmap.lanes.flatMap((lane) => lane.milestones).filter((item) => item.comparison_priority === "key").length], [tr("coverageGapsTitle"), roadmap.coverage_gaps.length], [tr("dependenciesTitle"), roadmap.dependencies.length]].forEach(([term, value]) => { const wrap = document.createElement("div"); const dt = document.createElement("dt"); dt.textContent = term; const dd = document.createElement("dd"); dd.textContent = value; wrap.append(dt, dd); values.append(wrap); }); card.append(title, values); root.append(card); });
  }
  function renderCompareTimeline(artifacts) {
    const root = document.getElementById("compare-timeline"); root.replaceChildren(); if (artifacts.length === 0) return; const startYear = Math.min(...artifacts.map((roadmap) => roadmap.horizon.start_year)); const endYear = Math.max(...artifacts.map((roadmap) => roadmap.horizon.end_year)); const years = []; for (let year = startYear; year <= endYear; year += 1) years.push(year); const table = document.createElement("table"); table.className = "comparison-table"; const head = document.createElement("thead"); const row = document.createElement("tr"); [tr("roadmapColumn"), ...years].forEach((label) => { const cell = document.createElement("th"); cell.textContent = label; row.append(cell); }); head.append(row); const body = document.createElement("tbody");
    artifacts.forEach((roadmap) => { const item = document.createElement("tr"); const title = document.createElement("th"); title.scope = "row"; const link = document.createElement("a"); link.href = `../${roadmap.slug}/`; link.textContent = localized(roadmap, "title"); title.append(link); item.append(title); years.forEach((year) => { const cell = document.createElement("td"); roadmap.lanes.flatMap((lane) => lane.milestones.map((milestone) => ({lane, milestone}))).filter(({milestone}) => milestone.year === year && milestone.comparison_priority === "key").forEach(({lane, milestone}) => { const entry = document.createElement("span"); entry.className = `comparison-milestone maturity-${milestone.maturity}`; entry.textContent = `${milestonePeriodLabel(milestone)} · ${localized(milestone, "label")} (${localized(lane, "owner")})`; cell.append(entry); }); item.append(cell); }); body.append(item); }); table.append(head, body); root.append(table);
  }
  function renderCompareDependencies(artifacts) {
    const root = document.getElementById("compare-dependencies"); root.replaceChildren(); const allowed = new Set(artifacts.map((item) => item.roadmap_id)); const dependencies = artifacts.flatMap((roadmap) => roadmap.dependencies).filter((item) => allowed.has(item.upstream_roadmap_id) && allowed.has(item.downstream_roadmap_id)); dependencies.forEach((dependency) => { const item = document.createElement("li"); const route = document.createElement("strong"); route.textContent = `${roadmapName(dependency.upstream_roadmap_id)} → ${roadmapName(dependency.downstream_roadmap_id)}`; const text = document.createElement("span"); text.textContent = `${tr(relationshipKeys[dependency.relationship])}: ${localized(dependency, "statement")}`; item.append(route, text); root.append(item); });
  }
  function renderComparison() { const artifacts = data.roadmap_artifacts.filter((item) => selectedRoadmaps.has(item.export_id)); renderCompareControls(); renderCompareMetrics(artifacts); renderCompareTimeline(artifacts); renderCompareDependencies(artifacts); }

  function render() { applyStaticCopy(); if (page === "roadmap-index") { renderRoadmapCategoryFilter(); renderRoadmapIndex(); } if (page === "roadmap-detail") { renderRoadmapDetail(); renderRoadmapDialog(); renderRoadmapTermDialog(); } if (page === "roadmap-compare") renderComparison(); }
  document.querySelectorAll("[data-language]").forEach((button) => button.addEventListener("click", () => { language = button.dataset.language; rememberLanguage(language); render(); }));
  document.getElementById("roadmap-search")?.addEventListener("input", renderRoadmapIndex);
  const dialog = document.getElementById("roadmap-dialog"); document.getElementById("roadmap-dialog-close")?.addEventListener("click", () => dialog.close()); dialog?.addEventListener("click", (event) => { if (event.target === event.currentTarget) event.currentTarget.close(); }); dialog?.addEventListener("close", () => { activeRoadmapMilestoneId = null; activeRoadmapGenerationBandId = null; });
  const termDialog = document.getElementById("roadmap-term-dialog"); document.getElementById("roadmap-term-dialog-close")?.addEventListener("click", () => termDialog.close()); termDialog?.addEventListener("click", (event) => { if (event.target === event.currentTarget) event.currentTarget.close(); }); termDialog?.addEventListener("close", () => { activeTermId = null; const url = new URL(window.location.href); url.searchParams.delete("term"); window.history.replaceState(null, "", url); });
  render();
  if (page === "roadmap-detail") {
    const params = new URLSearchParams(window.location.search);
    const termId = params.get("term");
    if (termId && termMap().has(termId)) openRoadmapTerm(termId);
    const trackId = params.get("track");
    const track = trackId ? document.getElementById(`track-${trackId}`) : null;
    if (track) { track.open = true; track.scrollIntoView({block: "start"}); }
  }
})();
