(() => {
  "use strict";
  const data = window.OPENFS_PUBLIC_DATA;
  const overview = data.application_performance_overview;
  const rootPrefix = document.body.dataset.rootPrefix;
  const copy = {
    ja: {
      publicOnly: "公開情報のみ", languageControl: "表示言語", breadcrumbs: "パンくずリスト",
      tagline: "公開調査カタログとシステム整備計画案", analysis: "分析",
      pageTitle: "アプリケーション性能予測", lead: "EEA1対象アプリの公開実測値と、基準機別の条件付き参考試算をまとめています。検証済みの数値予測は未掲載です。",
      tableTitle: "EEA1評価対象アプリケーション", name: "アプリケーション", domain: "分野・計算内容",
      code: "公開コード・公式情報", conditions: "評価条件", sources: "根拠",
      publicCode: "公開コードあり", unreleased: "EEA1参照資料では非公開", unknown: "未確認",
      conditionNote: "EEA1の入力・版・実行条件の組合せは未確認です。",
      trace: "ノードの通信トレース", details: "確認状況", moreSources: "その他の確認先",
      published: "公開日", dateUnknown: "公開日未確認", asOf: "調査情報の基準日",
      provisional: "暫定整理・独立検証未完了", roadmapLink: "科学ワークロード・ベンチマーク・性能モデルのロードマップ",
      footerDescription: "HPCI-CFSP 公開調査ビュー"
    },
    en: {
      publicOnly: "Public information only", languageControl: "Display language", breadcrumbs: "Breadcrumbs",
      tagline: "Public research catalog and system planning options", analysis: "Analysis",
      pageTitle: "Application performance forecasting", lead: "Public measurements of EEA1 applications and conditional reference calculations by baseline. Validated numerical forecasts are not yet available.",
      tableTitle: "EEA1 evaluation applications", name: "Application", domain: "Domain / computation",
      code: "Public code / official information", conditions: "Evaluation conditions", sources: "Evidence",
      publicCode: "Public source available", unreleased: "Unreleased in the EEA1 reference", unknown: "Not verified",
      conditionNote: "The combination of EEA1 input, version and execution conditions is unverified.",
      trace: "-node communication trace", details: "Verification notes", moreSources: "Other references",
      published: "Published", dateUnknown: "Publication date unverified", asOf: "Research as of",
      provisional: "Provisional; independent verification incomplete", roadmapLink: "Scientific workloads, benchmarks and performance models roadmap",
      footerDescription: "HPCI-CFSP public research view"
    }
  };
  let stored = null;
  try { stored = window.localStorage.getItem("openfs-language"); } catch (_error) { /* Optional preference. */ }
  const requested = new URLSearchParams(window.location.search).get("lang");
  let language = ["ja", "en"].includes(requested) ? requested : stored === "en" ? "en" : "ja";
  const tr = (key) => copy[language][key] || key;
  const local = (item, field) => item[`${field}_${language}`] || item[`${field}_ja`] || "";
  const sources = new Map(overview.sources.map((source) => [source.source_id, source]));
  const make = (tag, text) => { const node = document.createElement(tag); if (text !== undefined) node.textContent = text; return node; };

  function sourceLink(id) {
    const source = sources.get(id);
    if (!source) return make("span", tr("unknown"));
    const item = make("li");
    let url;
    try { url = new URL(source.url); } catch (_error) { return make("li", tr("unknown")); }
    if (!["https:", "http:"].includes(url.protocol)) return make("li", tr("unknown"));
    const link = make("a", source.title);
    link.href = url.href; link.target = "_blank"; link.rel = "noopener noreferrer";
    item.append(link, make("small", source.published_at ? `${tr("published")}: ${source.published_at}` : tr("dateUnknown")));
    return item;
  }

  function render() {
    document.documentElement.lang = language;
    document.title = `${tr("pageTitle")} | OpenFS`;
    document.querySelectorAll("[data-i18n]").forEach((node) => { node.textContent = tr(node.dataset.i18n); });
    document.querySelectorAll("[data-i18n-aria-label]").forEach((node) => node.setAttribute("aria-label", tr(node.dataset.i18nAriaLabel)));
    document.querySelectorAll("[data-language]").forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.language === language)));
    const comparisonDate = data.application_device_comparison?.as_of || overview.as_of;
    document.getElementById("application-overview-status").textContent = `${tr("provisional")} · ${tr("asOf")}: ${comparisonDate}`;
    const updated = document.getElementById("site-updated");
    updated.href = data.site.commit_url; updated.textContent = overview.as_of;
    const roadmap = data.roadmaps.find((item) => item.roadmap_id === "RM-APP-WORKLOADS");
    document.getElementById("application-roadmap-link").href = `${rootPrefix}roadmaps/${roadmap.slug}/?lang=${language}`;
    const table = make("table"); table.className = "application-basics-table";
    const caption = make("caption", tr("tableTitle")); caption.className = "sr-only";
    const head = make("thead"); const headings = make("tr");
    const columns = ["name", "domain", "code", "conditions", "sources"];
    columns.forEach((key) => { const cell = make("th", tr(key)); cell.scope = "col"; headings.append(cell); });
    head.append(headings); const body = make("tbody");
    overview.applications.forEach((app) => {
      const row = make("tr"); row.id = app.application_id; row.tabIndex = -1;
      const cells = columns.map((key, i) => { const cell = make(i === 0 ? "th" : "td"); cell.dataset.label = tr(key); if (i === 0) cell.scope = "row"; return cell; });
      cells[0].append(make("strong", app.name));
      cells[1].append(make("span", local(app, "domain")));
      const availability = app.code_availability;
      cells[2].append(make("p", tr(availability.status === "public-source-confirmed" ? "publicCode" : availability.status === "unreleased-in-eea1-reference" ? "unreleased" : "unknown")));
      const codeList = make("ul"); codeList.className = "application-basic-sources";
      availability.source_ids.slice(0, 2).forEach((id) => codeList.append(sourceLink(id)));
      cells[2].append(codeList);
      if (availability.source_ids.length > 2) {
        const details = make("details"); details.append(make("summary", tr("moreSources")));
        const list = make("ul"); list.className = "application-basic-sources";
        availability.source_ids.slice(2).forEach((id) => list.append(sourceLink(id)));
        details.append(list); cells[2].append(details);
      }
      cells[3].append(make("p", tr("conditionNote")));
      app.trace_observations.forEach((trace) => {
        const description = make("p", `${trace.nodes}${tr("trace")}`);
        description.title = local(trace, "note"); cells[3].append(description);
      });
      const notes = make("details"); notes.append(make("summary", tr("details")), make("p", local(availability, "note")));
      cells[3].append(notes);
      const evidence = make("ul"); evidence.className = "application-basic-sources";
      app.source_ids.filter((id) => !availability.source_ids.includes(id)).forEach((id) => evidence.append(sourceLink(id)));
      cells[4].append(evidence); row.append(...cells); body.append(row);
    });
    table.append(caption, head, body);
    document.getElementById("application-overview-table").replaceChildren(table);
    window.OpenFSDeviceComparison.render(language);
  }
  function focusApplication() {
    const id = new URLSearchParams(window.location.search).get("app") || window.location.hash.slice(1);
    if (!overview.applications.some((app) => app.application_id === id)) return;
    const row = document.getElementById(id); row?.scrollIntoView({block: "center"}); row?.focus({preventScroll: true});
  }
  document.querySelectorAll("[data-language]").forEach((button) => button.addEventListener("click", () => {
    language = button.dataset.language;
    try { window.localStorage.setItem("openfs-language", language); } catch (_error) { /* Optional preference. */ }
    const url = new URL(window.location.href); url.searchParams.set("lang", language);
    window.history.replaceState(null, "", url); render(); focusApplication();
  }));
  render(); focusApplication();
})();
