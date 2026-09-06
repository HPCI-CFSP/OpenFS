(() => {
  "use strict";

  const data = window.OPENFS_PUBLIC_DATA;
  const report = data.fs3_decision_evidence;
  const rootPrefix = document.body.dataset.rootPrefix || "";
  let language = new URLSearchParams(window.location.search).get("lang") === "en" ? "en" : "ja";

  const copy = {
    ja: {
      publicOnly: "公開情報のみ", navOverview: "概要", navCatalog: "調査カタログ", navRoadmaps: "ロードマップ", navScenarios: "システム整備計画案", navReports: "報告書", navSearch: "検索", kicker: "判断根拠パッケージ", asOf: "情報確認日", researchStatus: "調査状況", consensusStatus: "合意判定状況", provisional: "暫定結果", openNarrative: "報告書原稿を開く", openData: "機械可読データを開く", openConsensus: "Consensus履歴を開く", coverageTitle: "根拠の収集状況", coverageLead: "件数は調査範囲を示すものであり、整備案の点数や推奨順位を示すものではありません。", claimsTitle: "報告書に記載できる主張と残課題", claimsLead: "各章について、現時点で公表可能な範囲、不足する根拠、次の確認責任を分けて示します。", matrixTitle: "システム整備計画案ごとの根拠充足状況", matrixLead: "同じ根拠不足でも計画案への影響は異なります。確定を妨げる項目を明示しますが、採点、順位付け、推奨は行いません。", footerDescription: "HPCI-CFSP 公開調査ビュー", siteUpdated: "更新日時", systems: "HPCIシステム", procurements: "公開調達", applications: "EEA1アプリ", roadmaps: "ロードマップ", systemsUnit: "システム", casesUnit: "案件", appsUnit: "アプリ", roadmapsUnit: "件", operations: "公開運用情報", quantitativeOperations: "定量的な運用実績", facilityPower: "電力の数値根拠", contractAwards: "契約・落札総額", providerPayments: "提供者公表の支払額", specifications: "公開仕様書", completeTco: "完全な5年間TCO", pinnedCode: "コード版固定", pinnedInput: "入力版固定", proxyAssets: "公開Proxy資産", completeBaseline: "完全な基準測定パッケージ", approvedThresholds: "承認済み閾値", milestones: "マイルストーン", p0Gaps: "P0未確認事項", detail: "内訳", chapter: "章", currentClaim: "現時点で記載できる主張", state: "状態", evidence: "根拠", unresolved: "未解決事項", ownerAction: "次の確認", authority: "判断主体", evidenceDimension: "根拠項目", evidenceStatus: "根拠状況", gaps: "不足する根拠", publishableWithCaveat: "注記付きで記載可能", evidenceIncomplete: "根拠不足", partial: "一部確認", blocked: "不足", blocking: "確定を妨げる", availableWithCaveat: "注記付きで利用可能", provisionalStatus: "暫定", incomplete: "未完了", published: "公開", noValue: "なし"
    },
    en: {
      publicOnly: "Public information only", navOverview: "Overview", navCatalog: "Research catalog", navRoadmaps: "Roadmaps", navScenarios: "System planning options", navReports: "Reports", navSearch: "Search", kicker: "DECISION-EVIDENCE PACKAGE", asOf: "Information as of", researchStatus: "Research status", consensusStatus: "Consensus status", provisional: "Provisional result", openNarrative: "Open report manuscript", openData: "Open machine-readable data", openConsensus: "Open Consensus history", coverageTitle: "Evidence coverage", coverageLead: "Counts describe the research scope; they are not scores or rankings of planning options.", claimsTitle: "Reportable claims and remaining work", claimsLead: "For each chapter, this table separates what can currently be reported, missing evidence, the next action, and accountable authority.", matrixTitle: "Evidence sufficiency by system planning option", matrixLead: "The same evidence gap can affect planning options differently. Blocking gaps are shown without scoring, ranking, or recommending options.", footerDescription: "HPCI-CFSP public research view", siteUpdated: "Updated", systems: "HPCI systems", procurements: "Public procurements", applications: "EEA1 applications", roadmaps: "Roadmaps", systemsUnit: "systems", casesUnit: "cases", appsUnit: "applications", roadmapsUnit: "roadmaps", operations: "Public operational evidence", quantitativeOperations: "Quantitative operating records", facilityPower: "Numerical power evidence", contractAwards: "Contract or award totals", providerPayments: "Provider-reported payment", specifications: "Public specifications", completeTco: "Complete five-year TCO", pinnedCode: "Pinned code version", pinnedInput: "Pinned input version", proxyAssets: "Public proxy assets", completeBaseline: "Complete baseline package", approvedThresholds: "Approved thresholds", milestones: "Milestones", p0Gaps: "P0 Coverage Gaps", detail: "Breakdown", chapter: "Chapter", currentClaim: "Currently reportable claim", state: "State", evidence: "Evidence", unresolved: "Unresolved", ownerAction: "Next owner action", authority: "Decision authority", evidenceDimension: "Evidence dimension", evidenceStatus: "Evidence status", gaps: "Coverage Gaps", publishableWithCaveat: "Reportable with caveat", evidenceIncomplete: "Evidence incomplete", partial: "Partial", blocked: "Blocked", blocking: "Blocks commitment", availableWithCaveat: "Available with caveat", provisionalStatus: "Provisional", incomplete: "Incomplete", published: "Published", noValue: "None"
    }
  };

  function tr(key) { return copy[language][key] || key; }
  function local(item, stem) { return item[`${stem}_${language}`] ?? item[stem] ?? ""; }
  function element(tag, text, className) { const node = document.createElement(tag); if (text !== undefined) node.textContent = text; if (className) node.className = className; return node; }
  function appendList(cell, values, className = "report-ref-list") { const list = element("ul", undefined, className); (values || []).forEach((value) => list.append(element("li", value))); cell.append(list); }
  function status(value) {
    const explicit = {provisional: "provisionalStatus"};
    if (explicit[value]) return tr(explicit[value]);
    const key = value.replace(/-([a-z])/g, (_match, letter) => letter.toUpperCase());
    return tr(key) === key ? value : tr(key);
  }
  function statusBadge(value) { return element("span", status(value), `report-status report-status-${value}`); }
  function formatJst(value) { return new Intl.DateTimeFormat(language === "ja" ? "ja-JP" : "en-CA", {timeZone: "Asia/Tokyo", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false}).format(new Date(value)).replace(/\//g, "-"); }

  function applyCopy() {
    document.documentElement.lang = language;
    document.querySelectorAll("[data-copy]").forEach((node) => { node.textContent = tr(node.dataset.copy); });
    document.querySelectorAll("[data-language]").forEach((button) => { const active = button.dataset.language === language; button.classList.toggle("active", active); button.setAttribute("aria-pressed", String(active)); });
  }

  function metric(label, value, unit, note) {
    const item = element("article", undefined, "report-coverage-metric");
    item.append(element("span", label), element("strong", String(value)), element("small", `${unit} · ${note}`));
    return item;
  }

  function detailTable(title, rows) {
    const section = element("section", undefined, "report-coverage-group");
    section.append(element("h4", title));
    const dl = element("dl");
    rows.forEach(([label, value]) => { const row = element("div"); row.append(element("dt", label), element("dd", String(value))); dl.append(row); });
    section.append(dl);
    return section;
  }

  function renderCoverage() {
    const h = report.hpci_systems.summary;
    const p = report.procurements.summary;
    const e = report.eea1.summary;
    const r = report.roadmaps.summary;
    const metrics = document.getElementById("report-coverage-metrics");
    metrics.replaceChildren(
      metric(tr("systems"), h.system_count, tr("systemsUnit"), `${tr("operations")} ${h.operations_evidence_count}`),
      metric(tr("procurements"), p.case_count, tr("casesUnit"), `${tr("contractAwards")} ${p.public_contract_or_award_amount_count}`),
      metric(tr("applications"), e.application_count, tr("appsUnit"), `${tr("completeBaseline")} ${e.complete_baseline_package_count}`),
      metric(tr("roadmaps"), r.roadmap_count, tr("roadmapsUnit"), `${tr("p0Gaps")} ${r.p0_gap_count}`)
    );
    document.getElementById("report-coverage-details").replaceChildren(
      detailTable(tr("systems"), [[tr("operations"), `${h.operations_evidence_count}/${h.system_count}`], [tr("quantitativeOperations"), `${h.quantitative_operations_count}/${h.system_count}`], [tr("facilityPower"), `${h.facility_power_evidence_count}/${h.system_count}`]]),
      detailTable(tr("procurements"), [[tr("contractAwards"), `${p.public_contract_or_award_amount_count}/${p.case_count}`], [tr("providerPayments"), `${p.provider_reported_payment_count}/${p.case_count}`], [tr("specifications"), `${p.public_specification_count}/${p.case_count}`], [tr("completeTco"), `${p.complete_tco_count}/${p.case_count}`]]),
      detailTable(tr("applications"), [[tr("pinnedCode"), `${e.code_version_pinned_count}/${e.application_count}`], [tr("pinnedInput"), `${e.input_version_pinned_count}/${e.application_count}`], [tr("proxyAssets"), e.public_proxy_asset_count], [tr("completeBaseline"), `${e.complete_baseline_package_count}/${e.application_count}`], [tr("approvedThresholds"), `${e.approved_threshold_count}/${e.application_count}`]]),
      detailTable(tr("roadmaps"), [[tr("milestones"), r.milestone_count], [tr("p0Gaps"), r.p0_gap_count], ["P1", r.p1_gap_count], ["P2", r.p2_gap_count]])
    );
  }

  function renderClaims() {
    const wrap = document.getElementById("report-claim-readiness");
    const table = element("table", undefined, "report-claim-table");
    const head = element("thead"); const headRow = element("tr");
    [tr("chapter"), tr("state"), tr("currentClaim"), tr("evidence"), tr("unresolved"), tr("ownerAction"), tr("authority")].forEach((label) => headRow.append(element("th", label)));
    head.append(headRow); const body = element("tbody");
    const chapters = new Map(report.report_structure.map((item) => [item.chapter_id, item]));
    report.claim_readiness.forEach((item) => {
      const row = element("tr");
      const chapter = chapters.get(item.chapter_id); const chapterCell = element("th"); chapterCell.scope = "row"; chapterCell.append(element("strong", item.chapter_id), element("span", local(chapter, "title")));
      const stateCell = element("td"); stateCell.append(statusBadge(item.claim_state));
      const evidenceCell = element("td"); appendList(evidenceCell, item.evidence_refs);
      const unresolvedCell = element("td"); appendList(unresolvedCell, item.unresolved_refs);
      row.append(chapterCell, stateCell, element("td", local(item, "publishable_claim")), evidenceCell, unresolvedCell, element("td", local(item, "owner_action")), element("td", local(item, "decision_authority")));
      body.append(row);
    });
    table.append(head, body); wrap.replaceChildren(table);
  }

  function renderMatrix() {
    const matrix = report.planning_requirement_matrix;
    const wrap = document.getElementById("report-planning-matrix");
    const table = element("table", undefined, "report-planning-matrix");
    const head = element("thead"); const headRow = element("tr");
    headRow.append(element("th", tr("evidenceDimension")), element("th", tr("evidenceStatus")), element("th", tr("gaps")));
    matrix.rows[0].scenario_implications.forEach((item) => headRow.append(element("th", local(item, "scenario_title"))));
    head.append(headRow); const body = element("tbody");
    matrix.rows.forEach((item) => {
      const row = element("tr"); const label = element("th", local(item, "label")); label.scope = "row";
      const evidenceStatus = element("td"); evidenceStatus.append(statusBadge(item.evidence_status));
      const gaps = element("td"); appendList(gaps, item[`coverage_gaps_${language}`], "report-gap-list");
      row.append(label, evidenceStatus, gaps);
      item.scenario_implications.forEach((impact) => { const cell = element("td"); cell.append(statusBadge(impact.impact_status), element("p", local(impact, "interpretation"))); row.append(cell); });
      body.append(row);
    });
    table.append(head, body); wrap.replaceChildren(table);
    document.getElementById("report-matrix-caveat").textContent = local(matrix, "caveat");
  }

  function render() {
    applyCopy();
    document.getElementById("report-title").textContent = local(report, "title");
    document.getElementById("report-summary").textContent = local(report, "summary");
    document.getElementById("report-as-of").textContent = report.as_of;
    document.getElementById("report-research-status").textContent = status(report.research_status);
    document.getElementById("report-consensus-status").textContent = status(report.consensus_status);
    document.getElementById("report-caveat").textContent = local(report, "caveat");
    const updated = document.getElementById("site-updated"); updated.href = data.site.commit_url; updated.textContent = `${tr("siteUpdated")} ${formatJst(data.site.updated_at)} · ${data.site.commit_sha.slice(0, 7)}`;
    document.getElementById("license-status").textContent = `${data.publication.license} · ${tr("publicOnly")}`;
    renderCoverage(); renderClaims(); renderMatrix();
    const url = new URL(window.location.href); url.searchParams.set("lang", language); window.history.replaceState(null, "", url);
  }

  document.querySelectorAll("[data-language]").forEach((button) => button.addEventListener("click", () => { language = button.dataset.language; localStorage.setItem("openfs-language", language); render(); }));
  const stored = localStorage.getItem("openfs-language"); if (!new URLSearchParams(window.location.search).has("lang") && ["ja", "en"].includes(stored)) language = stored;
  render();
})();
