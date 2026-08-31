(function () {
  "use strict";
  const data = window.OPENFS_PUBLIC_DATA;
  const conference = data?.conference_coverage;
  if (!conference) return;
  const prefix = document.body.dataset.rootPrefix || "../../";
  const copy = {
    ja: {overview: "概要", catalog: "調査カタログ", roadmaps: "ロードマップ", plans: "システム整備計画案", reports: "報告書", search: "検索", organization: "発表・共著組織", coverage: "確認状況", all: "すべて", partners: "開発協力組織（発表者・スポンサーとは別）", related: "会議外の関連発表", sources: "確認した情報源と取得状況", technical: "技術講演", tutorial: "チュートリアル", keynote: "基調講演", poster: "ポスター", "program-only": "プログラムのみ確認", "abstract-only": "要旨のみ確認", "related-primary-checked": "関連一次情報を確認（講演全文は未確認）", coauthor: "共著組織", details: "関連する技術整理", next: "次の調査", read: "本文確認", "abstract-read": "要旨確認", blocked: "取得不可", empty: "本文取得不可", program: "公式プログラム等", discovery: "調査の手掛かり", primary: "一次情報", count: "表示件数", total: "登録件数", provisional: "暫定・Consensus未完了"},
    en: {overview: "Overview", catalog: "Research catalog", roadmaps: "Roadmaps", plans: "System planning options", reports: "Reports", search: "Search", organization: "Presenter / coauthor affiliation", coverage: "Verification status", all: "All", partners: "Development partners (not presenter or sponsor roles)", related: "Related announcements outside the program", sources: "Sources and retrieval status", technical: "Technical talk", tutorial: "Tutorial", keynote: "Keynote", poster: "Poster", "program-only": "Program only", "abstract-only": "Abstract only", "related-primary-checked": "Related primary evidence checked; full talk unverified", coauthor: "Coauthor affiliations", details: "Related technical assessment", next: "Next research", read: "Body read", "abstract-read": "Abstract read", blocked: "Access unavailable", empty: "No readable body", program: "Official program/context", discovery: "Discovery lead", primary: "Primary evidence", count: "Shown", total: "Registered", provisional: "Provisional; Consensus incomplete"}
  };
  let language = new URLSearchParams(location.search).get("lang");
  copy.ja.tagline = "公開調査カタログとシステム整備計画案";
  copy.en.tagline = "Public research catalog and system planning options";
  if (!["ja", "en"].includes(language)) {
    try { language = localStorage.getItem("openfs-language"); } catch (_error) {}
  }
  if (!["ja", "en"].includes(language)) language = "ja";
  const text = (object, key) => object[`${key}_${language}`] || "";
  const tr = (key) => copy[language][key] || key;
  const el = (tag, value) => { const node = document.createElement(tag); if (value) node.textContent = value; return node; };
  const sourceMap = new Map(conference.sources.map((s) => [s.source_id, s]));
  const topicMap = new Map(data.topics.map((t) => [t.topic_id, t]));
  const claimMap = new Map(data.topic_decision_support.topic_profiles.flatMap((p) => p.sections.filter((s) => !(p.archived_section_ids || []).includes(s.section_id)).flatMap((s) => s.items.map((i) => [i.item_id, i]))));
  function link(label, href) { const a = el("a", label); a.href = href; return a; }
  function topicLink(id) { const t = topicMap.get(id); return link(`${t.catalog_code}: ${text(t, "title")}`, `${prefix}?topic=${encodeURIComponent(id)}&lang=${language}#catalog`); }
  function sourceLinks(ids) {
    const p = el("p"); p.className = "conference-source-links";
    ids.forEach((id) => { const s = sourceMap.get(id); const a = link(s.title, s.url); a.target = "_blank"; a.rel = "noopener noreferrer"; p.append(a, document.createTextNode(" ")); });
    return p;
  }
  function options(id, values, label) {
    const select = document.getElementById(id); const previous = select.value;
    select.replaceChildren();
    ["", ...values].forEach((value) => { const option = el("option", value ? label(value) : tr("all")); option.value = value; select.append(option); });
    select.value = values.includes(previous) ? previous : "";
  }
  function render() {
    document.documentElement.lang = language;
    document.title = `${text(conference, "title")} | OpenFS`;
    document.querySelectorAll("[data-hc-copy]").forEach((n) => { n.textContent = tr(n.dataset.hcCopy); });
    document.querySelectorAll('[data-i18n="tagline"]').forEach((n) => { n.textContent = tr("tagline"); });
    document.querySelectorAll("[data-language]").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.language === language)));
    for (const field of ["title", "scope", "caveat"]) document.getElementById(`conference-${field}`).textContent = text(conference, field);
    const organizations = [...new Set(conference.entries.flatMap((e) => [...e.presenter_organizations, ...e.coauthor_organizations]))].sort();
    options("conference-organization", organizations, (s) => s);
    options("conference-status", ["program-only", "abstract-only", "related-primary-checked"], tr);
    const org = document.getElementById("conference-organization").value;
    const state = document.getElementById("conference-status").value;
    const shown = conference.entries.filter((e) => (!org || [...e.presenter_organizations, ...e.coauthor_organizations].includes(org)) && (!state || e.coverage_state === state));
    document.getElementById("conference-counts").textContent = `${tr("total")}: ${conference.entries.length} / ${tr("count")}: ${shown.length} / ${conference.as_of}`;
    const root = document.getElementById("conference-entries"); root.replaceChildren();
    shown.forEach((entry) => {
      const detail = el("details"); detail.id = entry.entry_id; detail.className = "conference-entry";
      const summary = el("summary"); summary.append(el("code", entry.entry_id), el("strong", text(entry, "label")), el("span", `${tr(entry.kind)} / ${entry.presenter_organizations.join(", ")}`), el("small", tr(entry.coverage_state)));
      detail.append(summary);
      if (entry.coauthor_organizations.length) detail.append(el("p", `${tr("coauthor")}: ${entry.coauthor_organizations.join(", ")}`));
      const topics = el("ul"); [entry.primary_topic_id, ...entry.related_topic_ids].forEach((id) => { const li = el("li"); li.append(topicLink(id)); topics.append(li); }); detail.append(topics);
      entry.technical_item_ids.forEach((id) => { const claim = claimMap.get(id); detail.append(el("h3", text(claim, "name")), el("p", text(claim, "statement"))); });
      detail.append(el("p", `${tr("provisional")}. ${text(entry, "gap")}`), el("p", `${tr("next")}: ${text(entry, "next_action")}`), sourceLinks(entry.source_ids));
      if (window.OpenFSFeedback) detail.append(window.OpenFSFeedback.link({kind: "page", id: entry.entry_id, title: text(entry, "label"), path: `conferences/hot-chips-2026/#${entry.entry_id}`}));
      root.append(detail);
    });
    const partners = document.getElementById("conference-partners"); partners.replaceChildren();
    conference.partnerships.forEach((p) => { const block = el("p", p.organizations.join(" / ")); p.entry_ids.forEach((id) => block.append(document.createTextNode(" "), link(id, `#${id}`))); partners.append(block, sourceLinks(p.source_ids)); });
    const related = document.getElementById("conference-related"); related.replaceChildren();
    conference.related_announcements.forEach((a) => { related.append(el("h3", text(a, "label")), el("p", text(claimMap.get(a.technical_item_id), "statement")), topicLink(a.topic_id), sourceLinks(a.source_ids)); });
    const gaps = document.getElementById("conference-gaps"); gaps.replaceChildren();
    conference.coverage_gaps.forEach((gap) => gaps.append(el("p", text(gap, "statement")), sourceLinks(gap.source_ids)));
    const sources = document.getElementById("conference-sources"); sources.replaceChildren();
    conference.sources.forEach((s) => { const p = el("p"); p.append(link(`${s.publisher}: ${s.title}`, s.url), document.createTextNode(` / ${tr(s.role)} / ${tr(s.retrieval_status)}`)); sources.append(p); });
    const anchor = document.getElementById(location.hash.slice(1)); if (anchor?.tagName === "DETAILS") anchor.open = true;
  }
  for (const id of ["conference-organization", "conference-status"]) document.getElementById(id).addEventListener("change", render);
  document.querySelectorAll("[data-language]").forEach((b) => b.addEventListener("click", () => { language = b.dataset.language; try { localStorage.setItem("openfs-language", language); } catch (_error) {} const url = new URL(location.href); url.searchParams.set("lang", language); history.replaceState(null, "", url); render(); }));
  window.addEventListener("hashchange", () => {
    document.getElementById("conference-organization").value = "";
    document.getElementById("conference-status").value = "";
    render();
  });
  render();
})();
