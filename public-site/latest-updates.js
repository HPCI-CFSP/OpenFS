(() => {
  "use strict";
  const data = window.OPENFS_PUBLIC_DATA;
  const latest = data?.latest_updates;
  if (!latest) return;
  const archive = document.body.dataset.page === "latest-updates";
  const rootPrefix = document.body.dataset.rootPrefix || "";
  const copy = {
    ja: {
      publicOnly: "公開情報のみ", languageControl: "表示言語", siteNavigation: "サイト内ナビゲーション", breadcrumbs: "パンくずリスト",
      navOverview: "概要", navCatalog: "調査カタログ", navRoadmaps: "ロードマップ", navScenarios: "システム整備計画案", navReports: "報告書", navGlossary: "専門用語", navSearch: "検索",
      updatesKicker: "公開情報の更新", updatesTitle: "最新動向", updatesLead: "発信元が公表した日付を基準に、新しい公開情報と調査上の位置付けを示します。", updatesArchiveLead: "発信元が公表した日付を基準に、OpenFSが追跡する公開情報を新しい順に一覧表示します。", openAllUpdates: "最新動向をすべて見る",
      queryLabel: "最新動向を検索", queryPlaceholder: "例: HBM、ROCm、ベンチマーク", categoryLabel: "分類", allCategories: "すべて", publicationDate: "発信元の公表日", checkedDate: "OpenFS確認日", source: "公開根拠", relatedTopics: "関連する調査項目", relatedRoadmaps: "関連ロードマップ", provisional: "暫定", consensusIncomplete: "合意判定未完了", results: "件", noUpdates: "条件に一致する最新動向はありません。", footerDescription: "HPCI-CFSP 公開調査ビュー"
    },
    en: {
      publicOnly: "Public information only", languageControl: "Display language", siteNavigation: "Site navigation", breadcrumbs: "Breadcrumbs",
      navOverview: "Overview", navCatalog: "Research catalog", navRoadmaps: "Roadmaps", navScenarios: "System planning options", navReports: "Reports", navGlossary: "Glossary", navSearch: "Search",
      updatesKicker: "PUBLIC INFORMATION UPDATES", updatesTitle: "Latest Updates", updatesLead: "New public information and its research context, ordered by the date on which the source published it.", updatesArchiveLead: "Public information tracked by OpenFS, listed newest first by the source publication date.", openAllUpdates: "View all latest updates",
      queryLabel: "Search latest updates", queryPlaceholder: "e.g. HBM, ROCm, benchmark", categoryLabel: "Category", allCategories: "All", publicationDate: "Source publication date", checkedDate: "OpenFS checked", source: "Public source", relatedTopics: "Related research topics", relatedRoadmaps: "Related roadmaps", provisional: "Provisional", consensusIncomplete: "Consensus incomplete", results: "updates", noUpdates: "No latest updates match the filters.", footerDescription: "HPCI-CFSP public research view"
    }
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
  const localized = (value, field) => value?.[`${field}_${language}`] || value?.[`${field}_ja`] || "";
  const sourceMap = new Map(latest.sources.map((source) => [source.source_id, source]));
  const topicMap = new Map(data.topics.map((topic) => [topic.topic_id, topic]));
  const roadmapMap = new Map(data.roadmaps.map((roadmap) => [roadmap.roadmap_id, roadmap]));
  const categoryMap = new Map(data.catalog_taxonomy.categories.map((category) => [category.category_id, category]));

  function withLanguage(href) {
    const [path, fragment] = href.split("#", 2);
    const separator = path.includes("?") ? "&" : "?";
    return `${path}${separator}lang=${language}${fragment ? `#${fragment}` : ""}`;
  }
  function topicHref(topicId) {
    return withLanguage(`${rootPrefix}?topic=${encodeURIComponent(topicId)}#catalog`);
  }
  function roadmapHref(roadmap) {
    return withLanguage(`${rootPrefix}${roadmap.path}`);
  }
  function appendLinks(parent, labelText, values) {
    if (!values.length) return;
    const group = document.createElement("div"); group.className = "latest-update-links";
    const label = document.createElement("strong"); label.textContent = labelText; group.append(label);
    values.forEach(({href, text}) => {
      const link = document.createElement("a"); link.href = href; link.textContent = text; group.append(link);
    });
    parent.append(group);
  }
  function renderUpdate(update) {
    const article = document.createElement("article"); article.className = "latest-update-item"; article.id = update.update_id; article.tabIndex = -1;
    const date = document.createElement("time"); date.dateTime = update.published_at; date.className = "latest-update-date";
    const dateLabel = document.createElement("span"); dateLabel.textContent = tr("publicationDate");
    const dateValue = document.createElement("strong"); dateValue.textContent = update.published_at; date.append(dateLabel, dateValue);
    const content = document.createElement("div"); content.className = "latest-update-content";
    const meta = document.createElement("div"); meta.className = "latest-update-meta";
    const category = document.createElement("span"); category.className = "latest-update-category"; category.textContent = localized(categoryMap.get(update.category_id), "title");
    const provisional = document.createElement("span"); provisional.className = "latest-update-status"; provisional.textContent = tr("provisional");
    const consensus = document.createElement("span"); consensus.className = "latest-update-status"; consensus.textContent = tr("consensusIncomplete");
    meta.append(category, provisional, consensus);
    const title = document.createElement("h3");
    const self = document.createElement("a"); self.href = withLanguage(`${rootPrefix}updates/#${update.update_id}`); self.textContent = localized(update, "title"); title.append(self);
    const summary = document.createElement("p"); summary.textContent = localized(update, "summary");
    content.append(meta, title, summary);
    const source = sourceMap.get(update.primary_source_id);
    if (source) appendLinks(content, tr("source"), [{href: source.url, text: `${source.publisher}: ${source.title}`}]);
    appendLinks(content, tr("relatedTopics"), update.related_topic_ids.map((id) => {
      const topic = topicMap.get(id);
      return {href: topicHref(id), text: topic ? `${topic.catalog_code}: ${localized(topic, "title")}` : id};
    }));
    appendLinks(content, tr("relatedRoadmaps"), update.related_roadmap_ids.map((id) => {
      const roadmap = roadmapMap.get(id);
      return {href: roadmap ? roadmapHref(roadmap) : `${rootPrefix}roadmaps/`, text: roadmap ? localized(roadmap, "title") : id};
    }));
    const checked = document.createElement("small"); checked.className = "latest-update-checked"; checked.textContent = `${tr("checkedDate")}: ${update.checked_at}`; content.append(checked);
    if (window.OpenFSFeedback) content.append(window.OpenFSFeedback.link({kind: "latest-update", id: update.update_id, title: localized(update, "title"), path: `updates/?lang=${language}#${update.update_id}`}));
    article.append(date, content);
    return article;
  }
  function updateCategoryOptions() {
    if (!archive) return;
    const select = document.getElementById("latest-updates-category");
    [...select.options].forEach((option) => {
      option.textContent = option.value === "all" ? tr("allCategories") : localized(categoryMap.get(option.value), "title");
    });
  }
  function applyCopy() {
    document.documentElement.lang = language;
    const textSelector = archive ? "[data-latest-i18n], [data-i18n]" : "[data-latest-i18n]";
    const ariaSelector = archive ? "[data-latest-i18n-aria-label], [data-i18n-aria-label]" : "[data-latest-i18n-aria-label]";
    document.querySelectorAll(textSelector).forEach((element) => { element.textContent = tr(element.dataset.latestI18n || element.dataset.i18n); });
    document.querySelectorAll(ariaSelector).forEach((element) => { element.setAttribute("aria-label", tr(element.dataset.latestI18nAriaLabel || element.dataset.i18nAriaLabel)); });
    document.querySelectorAll("[data-latest-i18n-placeholder]").forEach((element) => { element.placeholder = tr(element.dataset.latestI18nPlaceholder); });
    document.querySelectorAll("[data-language]").forEach((button) => { button.setAttribute("aria-pressed", String(button.dataset.language === language)); });
    const caveat = document.getElementById("latest-updates-caveat"); if (caveat) caveat.textContent = localized(latest, "caveat");
    const all = document.getElementById("latest-updates-all"); if (all) all.href = withLanguage(all.getAttribute("href").split("&lang=")[0]);
    updateCategoryOptions();
    if (archive) document.title = `${tr("updatesTitle")} | OpenFS`;
  }
  function archiveFilters() {
    const query = document.getElementById("latest-updates-search")?.value.trim().toLocaleLowerCase() || "";
    const category = document.getElementById("latest-updates-category")?.value || "all";
    return latest.updates.filter((update) => (category === "all" || update.category_id === category) && (!query || JSON.stringify(update).toLocaleLowerCase().includes(query)));
  }
  function render() {
    applyCopy();
    const home = document.getElementById("latest-updates-home");
    if (home) home.replaceChildren(...latest.updates.slice(0, latest.featured_limit).map(renderUpdate));
    const list = document.getElementById("latest-updates-archive");
    if (list) {
      const visible = archiveFilters(); list.replaceChildren(...visible.map(renderUpdate));
      document.getElementById("latest-updates-count").textContent = `${visible.length} ${tr("results")}`;
      document.getElementById("latest-updates-empty").hidden = visible.length !== 0;
    }
  }
  if (archive) {
    const select = document.getElementById("latest-updates-category");
    const all = document.createElement("option"); all.value = "all"; select.append(all);
    [...new Set(latest.updates.map((update) => update.category_id))].forEach((id) => {
      const option = document.createElement("option"); option.value = id; select.append(option);
    });
    document.getElementById("latest-updates-search").addEventListener("input", render);
    select.addEventListener("change", render);
    const commit = document.getElementById("site-updated"); commit.href = latest.source_commit_url || data.site.commit_url; commit.textContent = latest.as_of;
  }
  document.querySelectorAll("[data-language]").forEach((button) => button.addEventListener("click", () => {
    language = button.dataset.language; rememberLanguage(language);
    if (archive) { const url = new URL(window.location.href); url.searchParams.set("lang", language); window.history.replaceState(null, "", url); }
    render();
  }));
  render();
  if (archive && window.location.hash) document.querySelector(window.location.hash)?.focus({preventScroll: true});
})();
