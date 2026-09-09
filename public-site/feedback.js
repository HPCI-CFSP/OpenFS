(function () {
  "use strict";

  const repository = "https://github.com/HPCI-CFSP/OpenFS";
  const publicRoot = "https://hpci-cfsp.github.io/OpenFS/";
  const copy = {
    ja: {
      navFeedback: "Feedback", report: "誤りを報告", request: "追加調査をリクエスト", suggest: "改善を提案", existing: "既存の報告・リクエスト",
      feedbackTitle: "Feedback", publicNotice: "投稿内容は公開されます。機密情報、個人情報、脆弱性の詳細は投稿しないでください。",
      researchTitle: "追加調査のリクエスト", close: "閉じる", choose: "報告・調査依頼・改善提案",
      signIn: "投稿にはGitHubへのログインが必要です。", correctionTitle: "内容の誤り・表示の不具合", suggestionTitle: "使いやすさ・機能の改善",
      reportsTitle: "報告と対応状況", tagline: "公開調査カタログとシステム整備計画案", publicOnly: "公開情報のみ",
      navOverview: "概要", navCatalog: "調査カタログ", navRoadmaps: "ロードマップ", navScenarios: "システム整備計画案", navReports: "報告書", navSearch: "検索",
      footerDescription: "HPCI-CFSP 公開調査ビュー", siteNavigation: "サイト内ナビゲーション", languageControl: "表示言語"
    },
    en: {
      navFeedback: "Feedback", report: "Report an error", suggest: "Suggest an improvement", existing: "Existing reports and requests",
      feedbackTitle: "Feedback", publicNotice: "Submissions are public. Do not include confidential information, personal data, or vulnerability details.",
      request: "Request additional research", researchTitle: "Additional research", close: "Close", choose: "Report, request research, or suggest an improvement",
      signIn: "A GitHub sign-in is required to submit feedback.", correctionTitle: "Content errors and display problems", suggestionTitle: "Usability and feature improvements",
      reportsTitle: "Reports and resolution status", tagline: "Public research catalog and system planning options", publicOnly: "Public information only",
      navOverview: "Overview", navCatalog: "Research catalog", navRoadmaps: "Roadmaps", navScenarios: "System planning options", navReports: "Reports", navSearch: "Search",
      footerDescription: "HPCI-CFSP public research view", siteNavigation: "Site navigation", languageControl: "Display language"
    }
  };
  const kinds = new Set(["page", "topic", "technology", "roadmap", "track", "milestone", "generation", "term", "comparison", "platform-matrix", "numerical-matrix", "scenario", "report"]);
  const safeId = (value) => typeof value === "string" && /^[A-Za-z0-9][A-Za-z0-9_.:/-]{0,159}$/.test(value);
  const validCommit = (value) => typeof value === "string" && /^[a-f0-9]{40}$/.test(value);

  function publicPage(path, commit, language) {
    const page = new URL(path || "", publicRoot);
    if (page.origin !== new URL(publicRoot).origin || !page.pathname.startsWith("/OpenFS/") || page.username || page.password) {
      throw new Error("Feedback must refer to a public OpenFS page");
    }
    // Do not forward search text, arbitrary query parameters, or local preview URLs.
    const allowed = new Set(["topic", "track", "term", "milestone", "generation", "comparison"]);
    for (const key of [...page.searchParams.keys()]) {
      if (!allowed.has(key) || !safeId(page.searchParams.get(key))) page.searchParams.delete(key);
    }
    page.hash = "";
    page.searchParams.set("lang", language === "en" ? "en" : "ja");
    if (validCommit(commit)) page.searchParams.set("v", commit);
    return page.href;
  }

  function issueUrl(context, commit, language = "ja", mode = "correction") {
    if (!kinds.has(context.kind) || !safeId(context.id)) throw new Error("Invalid feedback target");
    const templates = {correction: "correction-report.yml", research: "research-request.yml", improvement: "improvement-proposal.yml"};
    if (!Object.hasOwn(templates, mode)) throw new Error("Invalid feedback mode");
    const related = context.relatedIds || [];
    if (related.length > 8 || !related.every(safeId)) throw new Error("Invalid related IDs");
    const url = new URL(`${repository}/issues/new`);
    url.searchParams.set("template", templates[mode]);
    const title = String(context.title || context.id).replace(/[\r\n\t]/g, " ").slice(0, 100);
    const prefixes = {correction: "Correction", research: "Research request", improvement: "Suggestion"};
    url.searchParams.set("title", `[${prefixes[mode]}] ${context.id}: ${title}`);
    url.searchParams.set("target", `${context.kind}: ${context.id}${related.length ? `\nRelated IDs: ${related.join(", ")}` : ""}`);
    url.searchParams.set("page_url", publicPage(context.path, commit, language));
    url.searchParams.set("source_commit", validCommit(commit) ? commit : "");
    url.searchParams.set("language", language === "en" ? "English" : "日本語");
    return url.href;
  }

  function existingUrl(id) {
    const url = new URL(`${repository}/issues`);
    url.searchParams.set("q", `is:issue label:public-feedback${safeId(id) ? ` "${id}"` : ""}`);
    return url.href;
  }

  if (typeof module !== "undefined" && module.exports) module.exports = {issueUrl, publicPage, existingUrl, copy};
  if (typeof window === "undefined" || !window.OPENFS_PUBLIC_DATA) return;

  const data = window.OPENFS_PUBLIC_DATA;
  const targets = new WeakMap();
  const language = () => document.documentElement.lang === "en" ? "en" : "ja";

  function updateLink(anchor) {
    const {context, mode} = targets.get(anchor);
    const text = copy[language()];
    if (mode === "chooser") {
      anchor.textContent = "Feedback";
      anchor.title = `${text.choose}: ${context.title || context.id}`;
      anchor.setAttribute("aria-label", `Feedback: ${context.title || context.id}`);
      return;
    }
    anchor.href = mode === "existing" ? existingUrl(context.id) : issueUrl(context, data.site.commit_sha, language(), mode);
    const label = ({existing: text.existing, improvement: text.suggest, research: text.request, correction: text.report})[mode];
    anchor.textContent = label;
    anchor.title = `${label}: ${context.title || context.id}`;
    anchor.setAttribute("aria-label", anchor.title);
  }

  function issueLink(context, mode = "correction") {
    const anchor = document.createElement("a");
    anchor.className = "feedback-link";
    anchor.target = "_blank";
    anchor.rel = "noopener noreferrer";
    anchor.dataset.feedbackKind = context.kind;
    anchor.dataset.feedbackId = context.id;
    targets.set(anchor, {context, mode});
    updateLink(anchor);
    return anchor;
  }

  let activeContext = null;
  const dialog = document.createElement("dialog");
  dialog.id = "feedback-dialog";
  dialog.className = "feedback-dialog";
  dialog.setAttribute("aria-labelledby", "feedback-dialog-title");
  document.body.append(dialog);
  dialog.addEventListener("click", (event) => { if (event.target === dialog) dialog.close(); });
  dialog.addEventListener("close", () => { activeContext = null; });

  function renderDialog() {
    if (!activeContext) return;
    const text = copy[language()];
    const content = document.createElement("div");
    content.className = "feedback-dialog-content";
    const header = document.createElement("header");
    const heading = document.createElement("h2");
    heading.id = "feedback-dialog-title";
    heading.textContent = "Feedback";
    const close = document.createElement("button");
    close.type = "button";
    close.className = "dialog-close";
    close.textContent = "×";
    close.title = text.close;
    close.setAttribute("aria-label", text.close);
    close.addEventListener("click", () => dialog.close());
    header.append(heading, close);
    const target = document.createElement("p");
    target.className = "feedback-context";
    target.textContent = `${activeContext.id} · ${activeContext.title || activeContext.id}`;
    const choices = document.createElement("div");
    choices.className = "feedback-choices";
    for (const mode of ["correction", "research", "improvement", "existing"]) choices.append(issueLink(activeContext, mode));
    const warning = document.createElement("p");
    warning.className = "feedback-public-notice";
    warning.textContent = text.publicNotice;
    const login = document.createElement("p");
    login.textContent = text.signIn;
    content.append(header, target, choices, warning, login);
    dialog.replaceChildren(content);
  }

  function link(context) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "feedback-link feedback-trigger";
    button.dataset.feedbackKind = context.kind;
    button.dataset.feedbackId = context.id;
    button.setAttribute("aria-haspopup", "dialog");
    targets.set(button, {context, mode: "chooser"});
    updateLink(button);
    button.addEventListener("click", () => { activeContext = context; renderDialog(); dialog.showModal(); });
    return button;
  }

  function mount(id, context) {
    const root = document.getElementById(id);
    if (root) root.replaceChildren(link(context));
  }

  function refresh() {
    const text = copy[language()];
    document.querySelectorAll("[data-feedback-copy]").forEach((element) => { element.textContent = text[element.dataset.feedbackCopy]; });
    document.querySelectorAll("[data-feedback-aria]").forEach((element) => { element.setAttribute("aria-label", text[element.dataset.feedbackAria]); });
    document.querySelectorAll(".feedback-link").forEach((anchor) => { if (targets.has(anchor)) updateLink(anchor); });
    document.querySelectorAll("[data-feedback-nav]").forEach((anchor) => {
      const url = new URL(anchor.href);
      url.searchParams.set("lang", language());
      anchor.href = url.href;
    });
  }

  window.OpenFSFeedback = {link, mount};
  new MutationObserver(refresh).observe(document.documentElement, {attributes: true, attributeFilter: ["lang"]});

  if (document.body.dataset.page === "feedback") {
    let initial = new URLSearchParams(window.location.search).get("lang");
    if (!["ja", "en"].includes(initial)) {
      try { initial = window.localStorage.getItem("openfs-language"); } catch (_error) { initial = "ja"; }
    }
    document.documentElement.lang = initial === "en" ? "en" : "ja";
    const context = {kind: "page", id: "OpenFS", title: "OpenFS", path: "feedback/"};
    document.getElementById("feedback-correction").append(issueLink(context));
    document.getElementById("feedback-research").append(issueLink(context, "research"));
    document.getElementById("feedback-suggestion").append(issueLink(context, "improvement"));
    const reports = document.getElementById("feedback-existing");
    reports.href = existingUrl();
    const setLanguage = (value) => {
      document.documentElement.lang = value;
      document.title = `${copy[value].feedbackTitle} | OpenFS`;
      document.querySelectorAll("[data-language]").forEach((button) => {
        const selected = button.dataset.language === value;
        button.classList.toggle("active", selected);
        button.setAttribute("aria-pressed", String(selected));
      });
      try { window.localStorage.setItem("openfs-language", value); } catch (_error) { /* Optional preference only. */ }
      refresh();
    };
    document.querySelectorAll("[data-language]").forEach((button) => button.addEventListener("click", () => setLanguage(button.dataset.language)));
    setLanguage(language());
  }
  refresh();
})();
