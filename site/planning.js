(function () {
  "use strict";

  const data = window.OPENFS_PUBLIC_DATA;
  if (!data) {
    document.body.textContent = "OpenFS public data is unavailable.";
    return;
  }

  const copy = {
    ja: {
      languageControl: "表示言語", tagline: "公開調査カタログと整備計画成果", publicOnly: "公開情報のみ", siteUpdated: "サイト更新",
      navOverview: "概要", navCatalog: "調査カタログ", navRoadmaps: "ロードマップ", navScenarios: "整備シナリオ", navReports: "報告書", footerDescription: "HPCI-CFSP 公開調査ビュー",
      evidenceKicker: "EVIDENCE HARDENING", evidenceTitle: "根拠監査", evidenceLead: "URL到達性、マイルストーンの主張種別、時期精度、Coverage Gapを分けて表示します。",
      consensusCaveatTitle: "検証状態", evidenceCaveat: "全件の引用ID・主張種別・時期表現を構造検査し、主要な更新項目を単一モデルで一次情報と照合しました。全件の独立した意味検証ではなく、Consensus Gateは未完了です。到達性監査も主張の正しさを判定しません。",
      claimAuditTitle: "Claim-Evidence監査", sourceAuditTitle: "情報源到達性", sourceAuditNote: "到達性は主張の正しさを示しません。アクセス制限やtimeoutはブラウザで有効な資料でも発生します。",
      gapRegisterTitle: "優先度付きCoverage Gap", gapRegisterLead: "公開情報で確認できない条件を推測で補わず、判断への影響と次の調査行動を記録します。",
      normalizedDependenciesTitle: "正規化した相互依存", externalConstraintsTitle: "外部制約・Coverage Gap", sourceCount: "情報源", reachable: "到達", accessRestricted: "アクセス制限", timeoutError: "timeout / error", milestoneCount: "マイルストーン", primaryEvent: "出来事・標準", forwardTarget: "将来目標", baseline: "基準日時点", coverageGap: "時期未公表", provisionalGate: "OpenFS暫定ゲート",
      roadmap: "ロードマップ", total: "合計", status: "状態", source: "情報源", url: "公開URL", relationship: "関係", criticality: "重要度", decisionImpact: "判断への影響", delayRisk: "遅延リスク", gates: "判断ゲート", high: "高", medium: "中", low: "低", commit: "Commit", priority: "優先度", scope: "確認対象", impact: "判断への影響", nextAction: "次の調査行動", open: "未解決",
      scenarioKicker: "HPCI PLANNING OPTIONS", scenarioIndexTitle: "HPCI整備計画 3シナリオ", scenarioIndexLead: "同じ11評価軸と判断ゲートで比較し、未確認条件を推測で埋めずに残します。",
      notRanking: "推奨順位ではありません", scenarioNotice: "3案はいずれも単一モデルによる暫定案で、センターProfile、価格、供給、施設条件、Consensusが未完了です。",
      scenarioComparisonTitle: "共通形式で比較", commonDecisionGates: "共通判断ゲート", objective: "目的", architecture: "アーキテクチャ", systemSoftware: "システムソフトウェア", applications: "アプリケーション", unknownCount: "未確認条件", reversibility: "可逆性", openDetail: "詳細を見る",
      planningHorizon: "計画期間", researchStatus: "調査状態", consensusStatus: "Consensus", updatedColumn: "更新日時", provisional: "暫定", incomplete: "未完了",
      centerImpacts: "センターへの影響", technologyOptions: "技術候補とfallback", evaluationAxes: "11評価軸", unscoredNote: "人が重みを承認していないため総合点は付けません。", uncertainties: "未確認条件", decisionGates: "判断ゲート", provenance: "PROVENANCE", traceability: "来歴と参照ID", sourceCommit: "ソースコミット",
      fit: "適合性", migration: "移行", unverified: "未確認", candidate: "候補", role: "役割", maturityGate: "成熟度ゲート", fallback: "Fallback", criterion: "評価軸", assessment: "暫定評価", evidence: "参照ID", optionDomain: "分野", compute: "計算ノード", memory: "メモリ", interconnect: "インターコネクト", "system-software": "システムソフトウェア", applicationsDomain: "アプリケーション",
      "application-coverage": "アプリケーション・利用者適合性", "time-to-solution": "性能・応答・スループット", "power-facility-fit": "電力・冷却・建屋適合性", "lifecycle-cost": "ライフサイクル費用", "maturity-schedule": "技術成熟度・供給・導入時期", "software-migration": "ソフトウェア継続性・移行", "operations-security": "運用性・人材・セキュリティ", "hpci-interoperability": "HPCI相互運用性", "technology-origin-and-ecosystem": "技術・供給網・産業波及", "center-fit": "センター別適合", reversibilityCriterion: "可逆性・段階導入性"
    },
    en: {
      languageControl: "Display language", tagline: "Public research catalog and planning outputs", publicOnly: "Public information only", siteUpdated: "Site updated",
      navOverview: "Overview", navCatalog: "Research catalog", navRoadmaps: "Roadmaps", navScenarios: "Roadmap scenarios", navReports: "Reports", footerDescription: "HPCI-CFSP public research view",
      evidenceKicker: "EVIDENCE HARDENING", evidenceTitle: "Evidence assurance", evidenceLead: "Separates URL reachability, milestone claim type, timing precision, and Coverage Gaps.",
      consensusCaveatTitle: "Validation status", evidenceCaveat: "All items were structurally checked for source references, claim type, and timing semantics, and major updates were checked by one model against primary sources. This is not independent semantic verification of every item; Consensus is incomplete, and reachability does not establish correctness.",
      claimAuditTitle: "Claim-evidence audit", sourceAuditTitle: "Source reachability", sourceAuditNote: "Reachability does not validate claims. A browser-accessible source may still return an access restriction or timeout to the machine client.",
      gapRegisterTitle: "Prioritized Coverage Gaps", gapRegisterLead: "Unknown public conditions remain explicit rather than being filled by inference, with decision impact and the next research action recorded.",
      normalizedDependenciesTitle: "Normalized dependencies", externalConstraintsTitle: "External constraints and Coverage Gaps", sourceCount: "Sources", reachable: "Reachable", accessRestricted: "Access restricted", timeoutError: "Timeout / error", milestoneCount: "Milestones", primaryEvent: "Events / standards", forwardTarget: "Forward targets", baseline: "As-of baseline", coverageGap: "Undated", provisionalGate: "OpenFS provisional gates",
      roadmap: "Roadmap", total: "Total", status: "Status", source: "Source", url: "Public URL", relationship: "Relationship", criticality: "Criticality", decisionImpact: "Decision impact", delayRisk: "Delay risk", gates: "Decision gates", high: "high", medium: "medium", low: "low", commit: "Commit", priority: "Priority", scope: "Scope", impact: "Decision impact", nextAction: "Next research action", open: "open",
      scenarioKicker: "HPCI PLANNING OPTIONS", scenarioIndexTitle: "Three HPCI infrastructure scenarios", scenarioIndexLead: "Compare all three using the same 11 criteria and decision gates without filling unknowns by inference.",
      notRanking: "Not a recommendation ranking", scenarioNotice: "All three are single-model provisional options. Center profiles, price, supply, facility conditions, and Consensus remain incomplete.",
      scenarioComparisonTitle: "Common-format comparison", commonDecisionGates: "Common decision gates", objective: "Objective", architecture: "Architecture", systemSoftware: "System Software", applications: "Applications", unknownCount: "Unknown conditions", reversibility: "Reversibility", openDetail: "Open details",
      planningHorizon: "Planning horizon", researchStatus: "Research status", consensusStatus: "Consensus", updatedColumn: "Updated", provisional: "provisional", incomplete: "incomplete",
      centerImpacts: "Center impacts", technologyOptions: "Technology options and fallback", evaluationAxes: "Eleven evaluation criteria", unscoredNote: "No total score is calculated before human approval of weights.", uncertainties: "Uncertainties", decisionGates: "Decision gates", provenance: "PROVENANCE", traceability: "Traceability and references", sourceCommit: "Source commit",
      fit: "Fit", migration: "Migration", unverified: "Unverified", candidate: "Candidate", role: "Role", maturityGate: "Maturity gate", fallback: "Fallback", criterion: "Criterion", assessment: "Provisional assessment", evidence: "Evidence refs", optionDomain: "Domain", compute: "Compute", memory: "Memory", interconnect: "Interconnect", "system-software": "System Software", applicationsDomain: "Applications",
      "application-coverage": "Application and user fit", "time-to-solution": "Performance, response, and throughput", "power-facility-fit": "Power, cooling, and facility fit", "lifecycle-cost": "Lifecycle cost", "maturity-schedule": "Maturity, supply, and schedule", "software-migration": "Software continuity and migration", "operations-security": "Operations, staffing, and security", "hpci-interoperability": "HPCI interoperability", "technology-origin-and-ecosystem": "Technology, supply chain, and ecosystem", "center-fit": "Center-specific fit", reversibilityCriterion: "Reversibility and staged deployment"
    }
  };

  let language = readLanguage();
  const page = document.body.dataset.page;
  const rootPrefix = document.body.dataset.rootPrefix || "";

  function readLanguage() {
    try { const value = window.localStorage.getItem("openfs-language"); if (value === "ja" || value === "en") return value; } catch (_error) {}
    return "ja";
  }
  function rememberLanguage(value) { try { window.localStorage.setItem("openfs-language", value); } catch (_error) {} }
  function tr(key) { return copy[language][key] || key; }
  function localized(item, field) { return item?.[`${field}_${language}`] || item?.[field] || ""; }
  function localizedArray(item, field) { const value = item?.[`${field}_${language}`] || item?.[field] || []; return Array.isArray(value) ? value : []; }
  function setText(id, value) { const element = document.getElementById(id); if (element) element.textContent = value; }
  function formatJst(value) {
    const parts = Object.fromEntries(new Intl.DateTimeFormat("en-CA", {timeZone: "Asia/Tokyo", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false}).formatToParts(new Date(value)).filter((part) => part.type !== "literal").map((part) => [part.type, part.value]));
    return `${parts.year}-${parts.month}-${parts.day}-${parts.hour}:${parts.minute}:${parts.second} JST`;
  }
  function makeCell(tag, text) { const cell = document.createElement(tag); cell.textContent = text; return cell; }
  function scenarioLink(scenario) { return `${rootPrefix}${scenario.path}?v=${encodeURIComponent(data.site.commit_sha)}`; }
  function roadmapTitle(roadmapId) { const roadmap = data.roadmaps.find((item) => item.roadmap_id === roadmapId); return roadmap ? (language === "ja" ? roadmap.title_ja : roadmap.title_en) : roadmapId; }

  function applyStaticCopy() {
    document.documentElement.lang = language;
    document.querySelectorAll("[data-i18n]").forEach((element) => { element.textContent = tr(element.dataset.i18n); });
    document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => { element.setAttribute("aria-label", tr(element.dataset.i18nAriaLabel)); });
    document.querySelectorAll("[data-language]").forEach((button) => { const selected = button.dataset.language === language; button.classList.toggle("active", selected); button.setAttribute("aria-pressed", String(selected)); });
    const updated = document.getElementById("site-updated"); if (updated) { updated.href = data.site.commit_url; updated.textContent = `${tr("siteUpdated")} ${formatJst(data.site.updated_at)} · ${data.site.commit_sha.slice(0, 7)}`; }
    setText("license-status", `License: ${data.publication.license}`);
  }

  function renderMetric(root, label, value, note) {
    const item = document.createElement("div"); const term = document.createElement("span"); term.textContent = label; const count = document.createElement("strong"); count.textContent = value; item.append(term, count); if (note) { const small = document.createElement("small"); small.textContent = note; item.append(small); } root.append(item);
  }

  function renderEvidencePage() {
    const assurance = data.roadmap_assurance; const source = assurance.source_audit; const evidence = assurance.evidence_audit; const dependencies = assurance.dependency_register;
    const metrics = document.getElementById("assurance-metrics"); metrics.replaceChildren();
    renderMetric(metrics, tr("sourceCount"), source.summary.source_count, `${source.audit_id} · ${source.as_of}`);
    renderMetric(metrics, tr("reachable"), source.summary.reachable, `${Math.round(source.summary.reachable / source.summary.source_count * 100)}%`);
    renderMetric(metrics, tr("accessRestricted"), source.summary["access-restricted"], "HTTP 403 / 429");
    renderMetric(metrics, tr("timeoutError"), source.summary.timeout + source.summary.error, tr("sourceAuditNote"));
    renderMetric(metrics, tr("milestoneCount"), evidence.summary.milestone_count, evidence.as_of);
    renderMetric(metrics, tr("coverageGap"), evidence.summary.coverage_gap, `${evidence.summary.openfs_provisional} ${tr("provisionalGate")}`);
    setText("assurance-caveat-text", tr("evidenceCaveat"));
    [["evidence-audit-commit", evidence], ["source-audit-commit", source], ["dependency-register-commit", dependencies]].forEach(([id, artifact]) => { const link = document.getElementById(id); link.href = artifact.source_commit_url; link.textContent = `${tr("commit")} ${artifact.source_commit.slice(0, 7)}`; });

    const byRoadmap = new Map(data.roadmaps.map((item) => [item.roadmap_id, {total: 0, primary: 0, target: 0, baseline: 0, gap: 0, provisional: 0}]));
    evidence.entries.forEach((entry) => { const item = byRoadmap.get(entry.roadmap_id); item.total += 1; if (entry.review_status === "screened-primary") item.primary += 1; if (entry.review_status === "screened-forward-looking") item.target += 1; if (entry.review_status === "as-of-baseline") item.baseline += 1; if (entry.review_status === "coverage-gap") item.gap += 1; if (entry.review_status === "openfs-provisional") item.provisional += 1; });
    const claimTable = document.createElement("table"); claimTable.className = "assurance-table"; const claimHead = document.createElement("thead"); const claimHeadRow = document.createElement("tr"); [tr("roadmap"), tr("total"), tr("primaryEvent"), tr("forwardTarget"), tr("baseline"), tr("coverageGap"), tr("provisionalGate")].forEach((label) => claimHeadRow.append(makeCell("th", label))); claimHead.append(claimHeadRow); const claimBody = document.createElement("tbody"); byRoadmap.forEach((counts, roadmapId) => { const row = document.createElement("tr"); row.append(makeCell("th", roadmapTitle(roadmapId)), makeCell("td", counts.total), makeCell("td", counts.primary), makeCell("td", counts.target), makeCell("td", counts.baseline), makeCell("td", counts.gap), makeCell("td", counts.provisional)); claimBody.append(row); }); claimTable.append(claimHead, claimBody); const claimRoot = document.getElementById("claim-audit-by-roadmap"); claimRoot.replaceChildren(claimTable);

    const attention = source.results.filter((item) => item.status !== "reachable"); const sourceTable = document.createElement("table"); sourceTable.className = "assurance-table source-attention-table"; const sourceHead = document.createElement("thead"); const sourceHeadRow = document.createElement("tr"); [tr("roadmap"), tr("source"), tr("status"), tr("url")].forEach((label) => sourceHeadRow.append(makeCell("th", label))); sourceHead.append(sourceHeadRow); const sourceBody = document.createElement("tbody"); attention.forEach((item) => { const row = document.createElement("tr"); row.append(makeCell("th", roadmapTitle(item.roadmap_id)), makeCell("td", item.source_id), makeCell("td", item.status)); const url = document.createElement("td"); const link = document.createElement("a"); link.href = item.url; link.target = "_blank"; link.rel = "noopener noreferrer"; link.textContent = item.url; url.append(link); row.append(url); sourceBody.append(row); }); sourceTable.append(sourceHead, sourceBody); document.getElementById("source-audit-results").replaceChildren(sourceTable);

    const gaps = data.roadmap_artifacts.flatMap((roadmap) => roadmap.coverage_gaps.map((gap) => ({...gap, roadmap_id: roadmap.roadmap_id}))).sort((left, right) => left.priority.localeCompare(right.priority) || left.roadmap_id.localeCompare(right.roadmap_id) || left.gap_id.localeCompare(right.gap_id));
    const priorityRoot = document.getElementById("gap-priority-summary"); priorityRoot.replaceChildren(); ["P0", "P1", "P2"].forEach((priority) => { const item = document.createElement("div"); const label = document.createElement("span"); label.className = `gap-priority priority-${priority.toLowerCase()}`; label.textContent = priority; const count = document.createElement("strong"); count.textContent = String(gaps.filter((gap) => gap.priority === priority).length); item.append(label, count); priorityRoot.append(item); });
    const gapTable = document.createElement("table"); gapTable.className = "assurance-table coverage-gap-table"; const gapHead = document.createElement("thead"); const gapHeadRow = document.createElement("tr"); [tr("priority"), tr("roadmap"), tr("scope"), tr("impact"), tr("nextAction")].forEach((label) => gapHeadRow.append(makeCell("th", label))); gapHead.append(gapHeadRow); const gapBody = document.createElement("tbody"); gaps.forEach((gap) => { const row = document.createElement("tr"); const priorityCell = document.createElement("td"); const priority = document.createElement("span"); priority.className = `gap-priority priority-${gap.priority.toLowerCase()}`; priority.textContent = gap.priority; priorityCell.append(priority); row.append(priorityCell, makeCell("th", roadmapTitle(gap.roadmap_id)), makeCell("td", localized(gap, "scope")), makeCell("td", localized(gap, "impact")), makeCell("td", localized(gap, "next_action"))); gapBody.append(row); }); gapTable.append(gapHead, gapBody); document.getElementById("coverage-gap-register").replaceChildren(gapTable);

    const dependencyRoot = document.getElementById("dependency-register"); dependencyRoot.replaceChildren(); dependencies.dependencies.forEach((dependency) => { const item = document.createElement("article"); const route = document.createElement("h4"); route.textContent = `${roadmapTitle(dependency.upstream_roadmap_id)} → ${roadmapTitle(dependency.downstream_roadmap_id)}`; const meta = document.createElement("p"); meta.className = "dependency-meta"; meta.textContent = `${tr("relationship")}: ${dependency.relationship} · ${tr("criticality")}: ${tr(dependency.criticality)} · ${dependency.basis}`; const statement = document.createElement("p"); statement.textContent = localized(dependency, "statement"); const detail = document.createElement("dl"); [[tr("decisionImpact"), localized(dependency, "decision_impact")], [tr("delayRisk"), localized(dependency, "risk_if_late")], [tr("gates"), dependency.gate_refs.join(", ")]].forEach(([term, value]) => { const group = document.createElement("div"); group.append(makeCell("dt", term), makeCell("dd", value)); detail.append(group); }); item.append(route, meta, statement, detail); dependencyRoot.append(item); });
    const externalRoot = document.getElementById("external-constraints"); externalRoot.replaceChildren(); dependencies.external_constraints.forEach((constraint) => { const item = document.createElement("article"); const title = document.createElement("h4"); title.textContent = localized(constraint, "name"); const body = document.createElement("p"); body.textContent = localized(constraint, "impact"); item.append(title, body); externalRoot.append(item); });
  }

  function renderScenarioCards(root) {
    root.replaceChildren(); data.scenarios.forEach((scenario) => { const item = document.createElement("article"); const id = document.createElement("span"); id.className = "eyebrow"; id.textContent = scenario.scenario_id; const title = document.createElement("h3"); const link = document.createElement("a"); link.href = scenarioLink(scenario); link.textContent = localized(scenario, "title"); title.append(link); const objective = document.createElement("p"); objective.textContent = localized(scenario, "objective"); const meta = document.createElement("p"); meta.className = "scenario-card-meta"; meta.textContent = `${scenario.planning_horizon} · ${tr("provisional")} · Consensus ${tr("incomplete")}`; item.append(id, title, objective, meta); root.append(item); });
  }

  function comparisonValue(scenario, row) {
    if (row === "objective") return localized(scenario, "objective");
    if (row === "architecture") return localized(scenario.architecture, "summary");
    if (row === "systemSoftware") return localized(scenario.system_software, "summary");
    if (row === "applications") return localized(scenario.applications, "summary");
    if (row === "unknownCount") return String(localizedArray(scenario, "uncertainties").length);
    return localized(scenario.evaluation.reversibility, "rationale");
  }

  function renderScenarioIndex() {
    renderScenarioCards(document.getElementById("scenario-index-list"));
    const rows = ["objective", "architecture", "systemSoftware", "applications", "unknownCount", "reversibility"];
    const table = document.createElement("table"); table.className = "scenario-comparison-table"; const head = document.createElement("thead"); const headRow = document.createElement("tr"); headRow.append(makeCell("th", tr("criterion"))); data.scenarios.forEach((scenario) => { const cell = document.createElement("th"); const link = document.createElement("a"); link.href = scenarioLink(scenario); link.textContent = localized(scenario, "title"); cell.append(link); headRow.append(cell); }); head.append(headRow); const body = document.createElement("tbody"); rows.forEach((key) => { const row = document.createElement("tr"); row.append(makeCell("th", tr(key))); data.scenarios.forEach((scenario) => row.append(makeCell("td", comparisonValue(scenario, key)))); body.append(row); }); table.append(head, body); document.getElementById("scenario-comparison").replaceChildren(table);
    const gates = document.getElementById("scenario-gates"); gates.replaceChildren(); data.scenarios.forEach((scenario) => { const item = document.createElement("section"); const title = document.createElement("h4"); title.textContent = localized(scenario, "title"); const list = document.createElement("ol"); localizedArray(scenario, "decision_gates").forEach((gate) => list.append(makeCell("li", gate))); item.append(title, list); gates.append(item); });
  }

  function renderPlanSection(root, key, value) {
    const section = document.createElement("section"); section.className = "scenario-plan-section"; const title = document.createElement("h3"); title.textContent = tr(key); const summary = document.createElement("p"); summary.textContent = localized(value, "summary"); const list = document.createElement("ul"); localizedArray(value, "priorities").forEach((priority) => list.append(makeCell("li", priority))); const refs = document.createElement("p"); refs.className = "mono-list"; refs.textContent = (value.roadmap_refs || []).join(" · "); section.append(title, summary, list, refs); root.append(section);
  }

  function renderScenarioDetail() {
    const scenario = data.scenarios.find((item) => item.scenario_id === document.body.dataset.scenarioId); if (!scenario) { document.querySelector("main").textContent = "Scenario unavailable."; return; }
    document.title = `${localized(scenario, "title")} | OpenFS`; setText("scenario-breadcrumb-title", localized(scenario, "title")); setText("scenario-id", scenario.scenario_id); setText("scenario-title", localized(scenario, "title")); setText("scenario-objective", localized(scenario, "objective")); setText("scenario-horizon", scenario.planning_horizon); setText("scenario-research-status", tr(scenario.research_status)); setText("scenario-consensus-status", tr(scenario.consensus_status)); setText("scenario-caveat", localized(scenario, "caveat")); setText("scenario-artifact-id", scenario.scenario_id); setText("scenario-evidence-refs", scenario.evidence_refs.join(" · ")); setText("scenario-revision-updated", formatJst(scenario.updated_at)); const updated = document.getElementById("scenario-updated"); updated.href = scenario.source_commit_url; updated.textContent = formatJst(scenario.updated_at); const commit = document.getElementById("scenario-source-commit"); commit.href = scenario.source_commit_url; commit.textContent = scenario.source_commit;
    const sections = document.getElementById("scenario-plan-sections"); sections.replaceChildren(); renderPlanSection(sections, "architecture", scenario.architecture); renderPlanSection(sections, "systemSoftware", scenario.system_software); renderPlanSection(sections, "applications", scenario.applications);
    const centers = document.getElementById("scenario-center-impacts"); centers.replaceChildren(); scenario.center_impacts.forEach((impact) => { const item = document.createElement("article"); const title = document.createElement("h4"); title.textContent = localized(impact, "center_group"); const details = document.createElement("dl"); [[tr("fit"), localized(impact, "fit")], [tr("migration"), localized(impact, "migration")], [tr("unverified"), localizedArray(impact, "unverified_conditions").join("; ")]].forEach(([term, value]) => { const group = document.createElement("div"); group.append(makeCell("dt", term), makeCell("dd", value)); details.append(group); }); item.append(title, details); centers.append(item); });
    const options = document.getElementById("scenario-technology-options"); options.replaceChildren(); scenario.technology_options.forEach((option) => { const item = document.createElement("article"); const domain = document.createElement("span"); domain.className = "technology-option-domain"; domain.textContent = option.domain === "applications" ? tr("applicationsDomain") : tr(option.domain); const title = document.createElement("h4"); title.textContent = localized(option, "candidate"); const details = document.createElement("dl"); [[tr("role"), localized(option, "role")], [tr("maturityGate"), localized(option, "maturity_gate")], [tr("fallback"), localized(option, "fallback")], [tr("evidence"), option.evidence_refs.join(" · ")]].forEach(([term, value]) => { const group = document.createElement("div"); group.append(makeCell("dt", term), makeCell("dd", value)); details.append(group); }); item.append(domain, title, details); options.append(item); });
    const evalTable = document.createElement("table"); evalTable.className = "scenario-evaluation-table"; const head = document.createElement("thead"); const headRow = document.createElement("tr"); [tr("criterion"), tr("assessment"), tr("evidence")].forEach((label) => headRow.append(makeCell("th", label))); head.append(headRow); const body = document.createElement("tbody"); Object.entries(scenario.evaluation).forEach(([criterion, evaluation]) => { const row = document.createElement("tr"); const label = criterion === "reversibility" ? tr("reversibilityCriterion") : tr(criterion); row.append(makeCell("th", label), makeCell("td", localized(evaluation, "rationale")), makeCell("td", evaluation.evidence_refs.join(", "))); body.append(row); }); evalTable.append(head, body); document.getElementById("scenario-evaluation").replaceChildren(evalTable);
    const uncertaintyList = document.getElementById("scenario-uncertainties"); uncertaintyList.replaceChildren(); localizedArray(scenario, "uncertainties").forEach((item) => uncertaintyList.append(makeCell("li", item))); const gateList = document.getElementById("scenario-decision-gates"); gateList.replaceChildren(); localizedArray(scenario, "decision_gates").forEach((item) => gateList.append(makeCell("li", item)));
  }

  function render() { applyStaticCopy(); if (page === "roadmap-evidence") renderEvidencePage(); if (page === "scenario-index") renderScenarioIndex(); if (page === "scenario-detail") renderScenarioDetail(); }
  document.querySelectorAll("[data-language]").forEach((button) => button.addEventListener("click", () => { language = button.dataset.language; rememberLanguage(language); render(); }));
  render();
})();
