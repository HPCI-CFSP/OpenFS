(function () {
  "use strict";

  const data = window.OPENFS_PUBLIC_DATA;
  if (!data) { document.querySelector("main").textContent = "OpenFS public data is unavailable."; return; }
  const rootPrefix = document.body.dataset.rootPrefix || "../";
  const copy = {
    ja: {tagline: "公開調査カタログとシステム整備計画案", publicOnly: "公開情報のみ", languageControl: "表示言語", siteNavigation: "サイト内ナビゲーション", breadcrumbs: "パンくずリスト", navOverview: "概要", navCatalog: "調査カタログ", navSearch: "検索", navRoadmaps: "ロードマップ", navScenarios: "システム整備計画案", navReports: "報告書", searchKicker: "公開情報を探す", searchTitle: "横断検索", searchLead: "調査項目、ロードマップ、技術用語、アプリケーション、HPCIシステム、比較表、システム整備計画案、公開根拠を一度に検索します。", queryLabel: "検索語", queryPlaceholder: "例: HBM、Megatron、ストレージ", typeLabel: "種類", allTypes: "すべて", typeTopic: "調査項目", typeRoadmap: "ロードマップ", typeTrack: "技術・判断項目", typeApplication: "アプリケーション", typeSystem: "HPCIシステム", typeTerm: "用語", typeComparison: "比較表", typeScenario: "計画案", typeSource: "公開根拠", searchButton: "検索", emptySearch: "検索語を入力してください。", noResults: "一致する公開情報はありません。", resultCount: "件", openResult: "開く", provisional: "暫定", consensusIncomplete: "合意判定未完了", independentReviewPending: "独立レビュー待ち", sourceAcademic: "学術一次情報", sourceGovernment: "政府公式情報", sourceGovernance: "OpenFSガバナンス", sourceProject: "プロジェクト公式情報", sourceResearchOrganization: "研究機関公式情報", sourceStandards: "標準化団体", sourceVendor: "ベンダー公式情報", footerDescription: "HPCI-CFSP 公開調査ビュー"},
    en: {tagline: "Public research catalog and system planning options", publicOnly: "Public information only", languageControl: "Display language", siteNavigation: "Site navigation", breadcrumbs: "Breadcrumbs", navOverview: "Overview", navCatalog: "Research catalog", navSearch: "Search", navRoadmaps: "Roadmaps", navScenarios: "System planning options", navReports: "Reports", searchKicker: "FIND PUBLIC INFORMATION", searchTitle: "Site search", searchLead: "Search research topics, roadmaps, technical terms, applications, HPCI systems, comparisons, system planning options, and public sources together.", queryLabel: "Query", queryPlaceholder: "e.g. HBM, Megatron, storage", typeLabel: "Type", allTypes: "All", typeTopic: "Research topic", typeRoadmap: "Roadmap", typeTrack: "Technology / decision track", typeApplication: "Application", typeSystem: "HPCI system", typeTerm: "Term", typeComparison: "Comparison", typeScenario: "Planning option", typeSource: "Public source", searchButton: "Search", emptySearch: "Enter a search query.", noResults: "No public information matches the query.", resultCount: "results", resultCountOne: "result", openResult: "Open", provisional: "Provisional", consensusIncomplete: "Consensus incomplete", independentReviewPending: "Independent review pending", sourceAcademic: "Academic primary source", sourceGovernment: "Government official source", sourceGovernance: "OpenFS governance", sourceProject: "Project official source", sourceResearchOrganization: "Research-organization source", sourceStandards: "Standards body", sourceVendor: "Vendor official source", footerDescription: "HPCI-CFSP public research view"}
  };
  const typeKeys = {topic: "typeTopic", roadmap: "typeRoadmap", track: "typeTrack", application: "typeApplication", system: "typeSystem", term: "typeTerm", comparison: "typeComparison", scenario: "typeScenario", source: "typeSource"};
  let language = readLanguage();

  function readLanguage() {
    const requested = new URLSearchParams(window.location.search).get("lang");
    if (requested === "ja" || requested === "en") return requested;
    try { const value = localStorage.getItem("openfs-language"); if (value === "ja" || value === "en") return value; } catch (_error) {}
    return "ja";
  }
  function rememberLanguage() { try { localStorage.setItem("openfs-language", language); } catch (_error) {} }
  function tr(key) { return copy[language][key] || key; }
  function localized(item, field) { return item?.[`${field}_${language}`] || item?.[field] || ""; }
  function normalize(value) { return String(value || "").normalize("NFKC").toLocaleLowerCase(language).replace(/\s+/g, ""); }
  function flatten(value) { if (value === null || value === undefined) return ""; if (typeof value === "string" || typeof value === "number") return String(value); if (Array.isArray(value)) return value.map(flatten).join(" "); if (typeof value === "object") return Object.values(value).map(flatten).join(" "); return ""; }
  function roadmapPath(roadmapId) { return data.roadmaps.find((item) => item.roadmap_id === roadmapId)?.path || "roadmaps/"; }
  function statusLabel(status) {
    const keys = {incomplete: "consensusIncomplete", "independent-review-pending": "independentReviewPending", provisional: "provisional", "academic-primary": "sourceAcademic", "government-official": "sourceGovernment", "openfs-governance": "sourceGovernance", "project-official": "sourceProject", "research-organization": "sourceResearchOrganization", "standards-body": "sourceStandards", "vendor-official": "sourceVendor"};
    return keys[status] ? tr(keys[status]) : status || "";
  }

  function searchItems() {
    const items = [];
    const categories = new Map(data.catalog_taxonomy.categories.map((item) => [item.category_id, item]));
    const profileMap = new Map((data.topic_decision_support?.topic_profiles || []).map((item) => [item.topic_id, item]));
    data.topics.forEach((topic) => { const category = categories.get(topic.catalog_category_id); items.push({type: "topic", id: topic.catalog_code, title_ja: topic.title_ja, title_en: topic.title_en, body_ja: `正規Topic ID: ${topic.topic_id}。${profileMap.get(topic.topic_id)?.summary_ja || ""}`, body_en: `Canonical Topic ID: ${topic.topic_id}. ${profileMap.get(topic.topic_id)?.summary_en || ""}`, search: flatten([topic, category, profileMap.get(topic.topic_id)]), href: `${rootPrefix}?topic=${encodeURIComponent(topic.topic_id)}#catalog`, status: topic.verification_status}); });
    data.roadmap_artifacts.forEach((roadmap) => {
      const index = data.roadmaps.find((item) => item.roadmap_id === roadmap.roadmap_id); const category = categories.get(index?.catalog_category_id); items.push({type: "roadmap", id: roadmap.roadmap_id, title_ja: roadmap.title_ja, title_en: roadmap.title_en, body_ja: roadmap.summary_ja, body_en: roadmap.summary_en, search: flatten([roadmap, category]), href: `${rootPrefix}${roadmapPath(roadmap.roadmap_id)}`, status: roadmap.consensus_status});
      roadmap.tracks.forEach((track) => items.push({type: "track", id: track.track_id, title_ja: track.name_ja, title_en: track.name_en, body_ja: track.summary_ja, body_en: track.summary_en, search: flatten([track, roadmap.title_ja, roadmap.title_en]), href: `${rootPrefix}${roadmapPath(roadmap.roadmap_id)}?track=${encodeURIComponent(track.track_id)}#roadmap-track-details`, status: roadmap.consensus_status}));
      roadmap.sources.forEach((source) => items.push({type: "source", id: source.source_id, title_ja: source.title, title_en: source.title, body_ja: `${source.publisher} / ${roadmap.title_ja}`, body_en: `${source.publisher} / ${roadmap.title_en}`, search: flatten([source, roadmap.title_ja, roadmap.title_en]), href: source.url, external: true, status: source.source_class}));
    });
    data.roadmap_reference_data.terms.forEach((term) => items.push({type: "term", id: term.term_id, title_ja: term.label_ja, title_en: term.label_en, body_ja: term.short_definition_ja, body_en: term.short_definition_en, search: flatten(term), href: `${rootPrefix}${roadmapPath(term.roadmap_ids[0])}?term=${encodeURIComponent(term.term_id)}#roadmap-glossary`, status: data.roadmap_reference_data.consensus_status}));
    data.roadmap_reference_data.comparison_sets.forEach((comparison) => items.push({type: "comparison", id: comparison.comparison_id, title_ja: comparison.title_ja, title_en: comparison.title_en, body_ja: comparison.summary_ja, body_en: comparison.summary_en, search: flatten(comparison), href: `${rootPrefix}${roadmapPath(comparison.roadmap_ids[0])}#roadmap-comparisons`, status: data.roadmap_reference_data.consensus_status}));
    data.application_performance_forecasts.applications.forEach((application) => items.push({type: "application", id: application.application_id, title_ja: application.name, title_en: application.name, body_ja: `${application.domain_ja}。${application.code_availability.note_ja}`, body_en: `${application.domain_en}. ${application.code_availability.note_en}`, search: flatten(application), href: `${rootPrefix}${roadmapPath("RM-APP-WORKLOADS")}#application-performance-section`, status: data.application_performance_forecasts.consensus_status}));
    data.hpci_system_inventory.systems.forEach((system) => items.push({type: "system", id: system.system_id, title_ja: system.name_ja, title_en: system.name_en, body_ja: `${system.provider_ja}。${system.architecture_class}`, body_en: `${system.provider_en}. ${system.architecture_class}`, search: flatten(system), href: `${rootPrefix}${roadmapPath("RM-X-BLUEPRINT")}#hpci-system-inventory-section`, status: data.hpci_system_inventory.consensus_status}));
    data.scenarios.forEach((scenario) => items.push({type: "scenario", id: scenario.scenario_id, title_ja: scenario.title_ja, title_en: scenario.title_en, body_ja: scenario.objective, body_en: scenario.objective_en, search: flatten(scenario), href: `${rootPrefix}${scenario.path}`, status: scenario.consensus_status}));
    return items;
  }
  const items = searchItems();

  function applyCopy() {
    document.documentElement.lang = language;
    document.querySelectorAll("[data-i18n]").forEach((element) => { element.textContent = tr(element.dataset.i18n); });
    document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => { element.setAttribute("aria-label", tr(element.dataset.i18nAriaLabel)); });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => { element.placeholder = tr(element.dataset.i18nPlaceholder); });
    document.querySelectorAll("[data-language]").forEach((button) => { const active = button.dataset.language === language; button.classList.toggle("active", active); button.setAttribute("aria-pressed", String(active)); });
    document.title = `${tr("searchTitle")} | OpenFS`;
  }
  function resultScore(item, query) { const title = normalize(`${item.title_ja} ${item.title_en} ${item.id}`); if (title === query) return 0; if (title.startsWith(query)) return 1; if (title.includes(query)) return 2; return 3; }
  function render() {
    applyCopy();
    const input = document.getElementById("global-search-input");
    const query = normalize(input.value);
    const selectedType = document.getElementById("global-search-type").value;
    const root = document.getElementById("global-search-results"); root.replaceChildren();
    const empty = document.getElementById("global-search-empty"); const summary = document.getElementById("global-search-summary");
    if (!query) { empty.hidden = false; empty.textContent = tr("emptySearch"); summary.textContent = ""; return; }
    const matches = items.filter((item) => (selectedType === "all" || item.type === selectedType) && normalize(`${item.id} ${item.search}`).includes(query)).sort((a, b) => resultScore(a, query) - resultScore(b, query) || localized(a, "title").localeCompare(localized(b, "title"), language)).slice(0, 100);
    summary.textContent = `${matches.length} ${language === "en" && matches.length === 1 ? tr("resultCountOne") : tr("resultCount")}`;
    empty.hidden = matches.length !== 0; empty.textContent = tr("noResults");
    matches.forEach((result) => {
      const article = document.createElement("article"); article.className = "global-search-result";
      const meta = document.createElement("div"); meta.className = "global-search-result-meta"; const type = document.createElement("span"); type.textContent = tr(typeKeys[result.type]); const id = document.createElement("code"); id.textContent = result.id; meta.append(type, id);
      const title = document.createElement("h3"); const link = document.createElement("a"); link.href = result.href; if (result.external) { link.target = "_blank"; link.rel = "noopener noreferrer"; } link.textContent = localized(result, "title"); title.append(link);
      const body = document.createElement("p"); body.textContent = localized(result, "body");
      const status = document.createElement("small"); status.textContent = statusLabel(result.status);
      article.append(meta, title, body, status); root.append(article);
    });
  }
  function syncUrl() { const url = new URL(window.location.href); const value = document.getElementById("global-search-input").value.trim(); if (value) url.searchParams.set("q", value); else url.searchParams.delete("q"); history.replaceState(null, "", url); }
  const params = new URLSearchParams(window.location.search); document.getElementById("global-search-input").value = params.get("q") || "";
  document.getElementById("global-search-form").addEventListener("submit", (event) => { event.preventDefault(); syncUrl(); render(); });
  document.getElementById("global-search-input").addEventListener("input", () => { syncUrl(); render(); });
  document.getElementById("global-search-type").addEventListener("change", render);
  document.querySelectorAll("[data-language]").forEach((button) => button.addEventListener("click", () => { language = button.dataset.language; rememberLanguage(); render(); }));
  render();
})();
