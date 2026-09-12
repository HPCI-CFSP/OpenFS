(() => {
  "use strict";
  const data = window.OPENFS_PUBLIC_DATA;
  const rootPrefix = document.body.dataset.rootPrefix || "../";
  const copy = {
    ja: {
      publicOnly: "公開情報のみ", languageControl: "表示言語", siteNavigation: "サイト内ナビゲーション", breadcrumbs: "パンくずリスト",
      navOverview: "概要", navCatalog: "調査カタログ", navRoadmaps: "ロードマップ", navScenarios: "システム整備計画案", navReports: "報告書", navGlossary: "専門用語", navSearch: "検索",
      glossaryKicker: "一元管理された定義", glossaryTitle: "専門用語", glossaryLead: "調査カタログとロードマップで使用する用語を、共通の定義と根拠に結び付けます。",
      provisionalTitle: "暫定的な用語整理", queryLabel: "用語を検索", queryPlaceholder: "例: HBM、MPI、Graph500", categoryLabel: "分類", allCategories: "すべて", aliases: "別名", relatedTerms: "関連用語", relatedRoadmaps: "関連ロードマップ", sources: "公開根拠", results: "件", noResults: "一致する用語はありません。", footerDescription: "HPCI-CFSP 公開調査ビュー",
      published: "公開日", updated: "更新日", sourceDate: "発信日（公開・更新の区別未確認）", eventDate: "内容上の事象日", verified: "OpenFS確認日", dateUnknown: "発信日（未確認）", dateNotStated: "発信日（資料に記載なし）"
    },
    en: {
      publicOnly: "Public information only", languageControl: "Display language", siteNavigation: "Site navigation", breadcrumbs: "Breadcrumbs",
      navOverview: "Overview", navCatalog: "Research catalog", navRoadmaps: "Roadmaps", navScenarios: "System planning options", navReports: "Reports", navGlossary: "Glossary", navSearch: "Search",
      glossaryKicker: "CENTRALIZED DEFINITIONS", glossaryTitle: "Glossary", glossaryLead: "Connect terms used in the research catalog and roadmaps to shared definitions and evidence.",
      provisionalTitle: "Provisional terminology", queryLabel: "Search terms", queryPlaceholder: "e.g. HBM, MPI, Graph500", categoryLabel: "Category", allCategories: "All", aliases: "Aliases", relatedTerms: "Related terms", relatedRoadmaps: "Related roadmaps", sources: "Public sources", results: "terms", noResults: "No terms match the filters.", footerDescription: "HPCI-CFSP public research view",
      published: "Published", updated: "Updated", sourceDate: "Source date (publication/update not distinguished)", eventDate: "Event described", verified: "OpenFS verified", dateUnknown: "Source date: not verified", dateNotStated: "Source date: not stated"
    }
  };
  const categoryCopy = {
    ja: {benchmark: "ベンチマーク", compute: "計算技術", interconnect: "接続技術", memory: "メモリ", packaging: "実装技術", planning: "計画・調達", software: "ソフトウェア", storage: "ストレージ"},
    en: {benchmark: "Benchmark", compute: "Compute", interconnect: "Interconnect", memory: "Memory", packaging: "Packaging", planning: "Planning and procurement", software: "Software", storage: "Storage"}
  };
  function storedLanguage() {
    try { return window.localStorage.getItem("openfs-language"); } catch (_error) { return null; }
  }
  function rememberLanguage(value) {
    try { window.localStorage.setItem("openfs-language", value); } catch (_error) { /* Optional preference only. */ }
  }
  const requestedLanguage = new URLSearchParams(window.location.search).get("lang");
  let language = ["ja", "en"].includes(requestedLanguage) ? requestedLanguage : storedLanguage();
  if (!copy[language]) language = "ja";
  const tr = (key) => copy[language][key] || key;
  const localized = (value, field) => value[`${field}_${language}`] || value[`${field}_ja`] || "";
  const terms = data.roadmap_reference_data.terms;
  const termMap = new Map(terms.map((term) => [term.term_id, term]));
  const dateMap = new Map((data.source_date_index?.records || []).map((record) => [record.source_id, record]));
  const roadmapMap = new Map(data.roadmap_artifacts.map((roadmap) => [roadmap.roadmap_id, roadmap]));
  const catalogSourceMap = new Map(data.topic_decision_support.sources.map((source) => [source.source_id, source]));

  function sourceFor(reference) {
    if (reference.catalog_source_id) return catalogSourceMap.get(reference.catalog_source_id);
    return roadmapMap.get(reference.roadmap_id)?.sources.find((source) => source.source_id === reference.source_id);
  }
  function sourceDates(sourceId) {
    const record = dateMap.get(sourceId);
    if (!record) return [tr("dateUnknown")];
    const labels = {publication: "published", update: "updated", "publication-or-update": "sourceDate"};
    const values = record.source_dates.map((entry) => `${tr(labels[entry.kind])}: ${entry.value}`);
    if (!values.length) values.push(tr(record.source_date_status === "not-stated" ? "dateNotStated" : "dateUnknown"));
    record.event_dates.forEach((entry) => values.push(`${tr("eventDate")}: ${entry.value}`));
    if (record.openfs_verified_on) values.push(`${tr("verified")}: ${record.openfs_verified_on}`);
    return values;
  }
  function glossaryHref(termId) { return `?term=${encodeURIComponent(termId)}&lang=${language}#${encodeURIComponent(termId)}`; }
  function roadmapHref(roadmap) { return `${rootPrefix}roadmaps/${roadmap.slug}/?lang=${language}`; }

  function renderTerm(term) {
    const article = document.createElement("article");
    article.id = term.term_id;
    article.className = "glossary-catalog-item";
    article.tabIndex = -1;
    const header = document.createElement("header");
    const title = document.createElement("h3");
    const self = document.createElement("a");
    self.href = glossaryHref(term.term_id);
    self.textContent = localized(term, "label");
    title.append(self);
    const meta = document.createElement("span");
    meta.textContent = `${term.term_id} · ${categoryCopy[language][term.category] || term.category}`;
    header.append(title, meta);
    const short = document.createElement("p"); short.className = "glossary-short-definition"; short.textContent = localized(term, "short_definition");
    const definition = document.createElement("p"); definition.textContent = localized(term, "definition");
    article.append(header, short, definition);
    const aliases = term.aliases.filter((alias) => alias !== localized(term, "label"));
    if (aliases.length) {
      const p = document.createElement("p"); p.className = "glossary-meta-line";
      const label = document.createElement("strong"); label.textContent = `${tr("aliases")}:`;
      p.append(label, document.createTextNode(` ${aliases.join(", ")}`)); article.append(p);
    }
    if (term.related_term_ids.length) {
      const block = document.createElement("div"); block.className = "glossary-link-group"; const label = document.createElement("strong"); label.textContent = tr("relatedTerms"); block.append(label);
      term.related_term_ids.forEach((id) => { const related = termMap.get(id); if (!related) return; const link = document.createElement("a"); link.href = glossaryHref(id); link.textContent = localized(related, "label"); block.append(link); }); article.append(block);
    }
    if (term.roadmap_ids.length) {
      const block = document.createElement("div"); block.className = "glossary-link-group"; const label = document.createElement("strong"); label.textContent = tr("relatedRoadmaps"); block.append(label);
      term.roadmap_ids.forEach((id) => { const roadmap = roadmapMap.get(id); if (!roadmap) return; const link = document.createElement("a"); link.href = roadmapHref(roadmap); link.textContent = localized(roadmap, "title"); block.append(link); }); article.append(block);
    }
    if (term.source_refs.length) {
      const heading = document.createElement("strong"); heading.className = "glossary-source-heading"; heading.textContent = tr("sources"); const list = document.createElement("ul"); list.className = "source-list";
      term.source_refs.forEach((reference) => { const source = sourceFor(reference); if (!source) return; const id = reference.catalog_source_id || reference.source_id; const item = document.createElement("li"); const link = document.createElement("a"); link.href = source.url; link.target = "_blank"; link.rel = "noopener noreferrer"; link.textContent = source.title; const meta = document.createElement("span"); meta.textContent = [source.publisher, id, ...sourceDates(id)].filter(Boolean).join(" · "); item.append(link, meta); list.append(item); }); article.append(heading, list);
    }
    if (window.OpenFSFeedback) article.append(window.OpenFSFeedback.link({kind: "term", id: term.term_id, title: localized(term, "label"), path: `glossary/?term=${encodeURIComponent(term.term_id)}&lang=${language}#${term.term_id}`}));
    return article;
  }

  function render() {
    document.documentElement.lang = language;
    document.title = `${tr("glossaryTitle")} | OpenFS`;
    document.querySelectorAll("[data-i18n]").forEach((element) => { element.textContent = tr(element.dataset.i18n); });
    document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => { element.setAttribute("aria-label", tr(element.dataset.i18nAriaLabel)); });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => { element.placeholder = tr(element.dataset.i18nPlaceholder); });
    document.querySelectorAll("[data-language]").forEach((button) => { button.setAttribute("aria-pressed", String(button.dataset.language === language)); });
    document.getElementById("glossary-caveat").textContent = localized(data.roadmap_reference_data, "caveat");
    const commit = document.getElementById("site-updated"); commit.href = data.roadmap_reference_data.source_commit_url || data.site.commit_url; commit.textContent = data.roadmap_reference_data.as_of;
    const category = document.getElementById("glossary-category"); const selected = category.value;
    const all = document.createElement("option"); all.value = "all"; all.textContent = tr("allCategories"); category.replaceChildren(all);
    [...new Set(terms.map((term) => term.category))].sort().forEach((value) => {
      const option = document.createElement("option"); option.value = value; option.textContent = categoryCopy[language][value] || value; category.append(option);
    });
    category.value = selected || "all";
    applyFilters();
  }
  function applyFilters() {
    const query = document.getElementById("glossary-search").value.trim().toLocaleLowerCase();
    const category = document.getElementById("glossary-category").value;
    const visible = terms.filter((term) => (category === "all" || term.category === category) && (!query || JSON.stringify(term).toLocaleLowerCase().includes(query)));
    const list = document.getElementById("glossary-list"); list.replaceChildren(...visible.map(renderTerm));
    document.getElementById("glossary-count").textContent = visible.length ? `${visible.length} ${tr("results")}` : tr("noResults");
  }
  document.getElementById("glossary-search").addEventListener("input", applyFilters);
  document.getElementById("glossary-category").addEventListener("change", applyFilters);
  document.querySelectorAll("[data-language]").forEach((button) => button.addEventListener("click", () => { language = button.dataset.language; rememberLanguage(language); const url = new URL(window.location.href); url.searchParams.set("lang", language); window.history.replaceState(null, "", url); render(); }));
  const initialTerm = new URLSearchParams(window.location.search).get("term");
  render();
  if (initialTerm && termMap.has(initialTerm)) {
    const target = document.getElementById(initialTerm);
    target?.scrollIntoView({block: "start"});
    target?.focus({preventScroll: true});
  }
})();
