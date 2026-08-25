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
      navOverview: "概要", navCatalog: "調査カタログ", navRoadmaps: "ロードマップ", navScenarios: "整備シナリオ", navReports: "報告書",
      libraryKicker: "公開ロードマップ索引", libraryTitle: "ロードマップ一覧", libraryLead: "共通形式で作成したロードマップを分野別に確認し、6本比較で相互依存と判断時期を横断できます。",
      compareRoadmaps: "6本を比較", compareKicker: "P0初期公開波", compareTitle: "ロードマップ横断比較", compareLead: "重要マイルストーン、根拠カバレッジ、Coverage Gap、ロードマップ間依存を同じ尺度で比較します。",
      domainFilter: "分野フィルタ", all: "すべて", search: "検索", searchPlaceholder: "名称、分野", roadmapColumn: "ロードマップ", domainColumn: "分野", horizonColumn: "対象期間", researchAsOf: "調査基準日", researchStatus: "調査状態", coverageStatus: "調査範囲", consensusStatus: "Consensus", updatedColumn: "更新日時", noRoadmaps: "条件に一致するロードマップはありません。",
      roadmapKicker: "根拠付き暫定ロードマップ", roadmapFilter: "トラック群フィルタ", trackColumn: "技術・判断トラック", ownerColumn: "主体／対象", quarterUnknown: "Q未特定", undatedColumn: "時期未公表", roadmapTableNote: "項目を選択すると根拠と詳細を表示します。Q1-Q4は公開根拠がある場合のみ使用し、年次・半期情報はQ未特定に残しています。空欄は日程未確認を意味します。",
      trackNotesKicker: "トラック別ノート", trackNotesTitle: "現状とHPCI整備への示唆", currentState: "現在の状況", hpciImplications: "HPCI整備への示唆", roadmapCaveat: "公開時の注意事項", dependenciesKicker: "相互依存", dependenciesTitle: "他ロードマップとの依存関係", coverageGapsTitle: "Coverage Gap", gapImpact: "影響", gapNextAction: "次の確認",
      commercial: "製品・量産", sample: "サンプル", standard: "標準", target: "ベンダー目標", concept: "構想・研究", pilot: "実証", decisionGate: "判断ゲート", deployment: "導入", undated: "時期未公表",
      timingBasis: "時期の根拠", timingPrecision: "時期の精度", eventType: "イベント種別", quarterPrecision: "四半期", halfYearPrecision: "半期", yearPrecision: "年", undatedPrecision: "未公表", milestoneDetail: "マイルストーン詳細", publicSources: "公開根拠資料",
      observed: "確認済み", standardRelease: "標準公開", vendorTarget: "ベンダー目標", projectTarget: "プロジェクト目標", policyTarget: "政策目標", openfsPlan: "OpenFS暫定計画", noPublicDate: "公開時期なし",
      productEvent: "製品", standardEvent: "標準", researchEvent: "研究", policyEvent: "政策", evaluationEvent: "HPCI評価", adoptionEvent: "HPCI導入",
      provisional: "暫定", accepted: "受理済み", coverageMet: "宣言した範囲を充足", consensusIncomplete: "未完了", profileIncomplete: "一次情報の継続確認が必要",
      sourceCoverage: "一次情報", tracksUnit: "トラック", milestonesUnit: "項目", gapsUnit: "Gap", keyMilestones: "重要マイルストーン", selectedRoadmaps: "比較対象", dependencyMap: "依存関係一覧",
      evidenceBacked: "根拠に基づく", openfsAssessment: "OpenFS評価", requires: "必要とする", informs: "判断材料となる", constrains: "制約する", enables: "可能にする", coEvolves: "相互に発展",
      revisionKicker: "来歴", revisionTitle: "更新履歴と再現情報", artifactId: "Artifact ID", sourceCommit: "ソースコミット", closeDialog: "詳細を閉じる", footerDescription: "HPCI-CFSP 公開調査ビュー"
    },
    en: {
      languageControl: "Display language", tagline: "Public research catalog and planning outputs", publicOnly: "Public information only", siteUpdated: "Site updated",
      navOverview: "Overview", navCatalog: "Research catalog", navRoadmaps: "Roadmaps", navScenarios: "Roadmap scenarios", navReports: "Reports",
      libraryKicker: "PUBLISHED ROADMAP INDEX", libraryTitle: "Roadmap library", libraryLead: "Review common-format roadmaps by domain, then use the six-roadmap comparison to trace dependencies and decision timing.",
      compareRoadmaps: "Compare six", compareKicker: "P0 INITIAL PUBLICATION WAVE", compareTitle: "Cross-roadmap comparison", compareLead: "Compare key milestones, evidence coverage, Coverage Gaps, and cross-roadmap dependencies on common scales.",
      domainFilter: "Domain filter", all: "All", search: "Search", searchPlaceholder: "Title or domain", roadmapColumn: "Roadmap", domainColumn: "Domain", horizonColumn: "Horizon", researchAsOf: "Research as of", researchStatus: "Research status", coverageStatus: "Coverage", consensusStatus: "Consensus", updatedColumn: "Updated", noRoadmaps: "No roadmaps match the current filters.",
      roadmapKicker: "EVIDENCE-BASED PROVISIONAL ROADMAP", roadmapFilter: "Track group filter", trackColumn: "Technology / decision track", ownerColumn: "Owner / scope", quarterUnknown: "Q?", undatedColumn: "Timing not public", roadmapTableNote: "Select a milestone to inspect its evidence. Q1-Q4 are used only when supported by public evidence; year- or half-year-only dates remain under Q?. Blank cells mean no dated milestone was confirmed.",
      trackNotesKicker: "TRACK NOTES", trackNotesTitle: "Current state and implications for HPCI", currentState: "Current state", hpciImplications: "Implications for HPCI", roadmapCaveat: "Publication caveat", dependenciesKicker: "INTERDEPENDENCIES", dependenciesTitle: "Dependencies on other roadmaps", coverageGapsTitle: "Coverage Gaps", gapImpact: "Impact", gapNextAction: "Next check",
      commercial: "product / volume", sample: "sample", standard: "standard", target: "vendor target", concept: "concept / research", pilot: "pilot", decisionGate: "decision gate", deployment: "deployment", undated: "timing not public",
      timingBasis: "Timing basis", timingPrecision: "Timing precision", eventType: "Event type", quarterPrecision: "quarter", halfYearPrecision: "half-year", yearPrecision: "year", undatedPrecision: "not public", milestoneDetail: "Milestone detail", publicSources: "Public supporting sources",
      observed: "observed", standardRelease: "standard release", vendorTarget: "vendor target", projectTarget: "project target", policyTarget: "policy target", openfsPlan: "OpenFS provisional plan", noPublicDate: "no public date",
      productEvent: "product", standardEvent: "standard", researchEvent: "research", policyEvent: "policy", evaluationEvent: "HPCI evaluation", adoptionEvent: "HPCI adoption",
      provisional: "provisional", accepted: "accepted", coverageMet: "declared scope met", consensusIncomplete: "incomplete", profileIncomplete: "continued primary-source review required",
      sourceCoverage: "Primary sources", tracksUnit: "tracks", milestonesUnit: "milestones", gapsUnit: "gaps", keyMilestones: "Key milestones", selectedRoadmaps: "Roadmaps to compare", dependencyMap: "Dependency list",
      evidenceBacked: "evidence-backed", openfsAssessment: "OpenFS assessment", requires: "requires", informs: "informs", constrains: "constrains", enables: "enables", coEvolves: "co-evolves",
      revisionKicker: "PROVENANCE", revisionTitle: "Revision and reproducibility", artifactId: "Artifact ID", sourceCommit: "Source commit", closeDialog: "Close details", footerDescription: "HPCI-CFSP public research view"
    }
  };

  const domainLabels = {
    ja: {hardware: "ハードウェア", "system-software": "システムソフトウェア", applications: "アプリケーション", "cross-cutting": "分野横断"},
    en: {hardware: "Hardware", "system-software": "System software", applications: "Applications", "cross-cutting": "Cross-cutting"}
  };
  const maturityKeys = {commercial: "commercial", sample: "sample", standard: "standard", target: "target", concept: "concept", pilot: "pilot", "decision-gate": "decisionGate", deployment: "deployment", undated: "undated"};
  const timingBasisKeys = {observed: "observed", "standard-release": "standardRelease", "vendor-target": "vendorTarget", "project-target": "projectTarget", "policy-target": "policyTarget", "openfs-provisional-plan": "openfsPlan", "no-public-date": "noPublicDate"};
  const timingPrecisionKeys = {quarter: "quarterPrecision", "half-year": "halfYearPrecision", year: "yearPrecision", undated: "undatedPrecision"};
  const eventTypeKeys = {product: "productEvent", standard: "standardEvent", research: "researchEvent", policy: "policyEvent", "hpci-evaluation": "evaluationEvent", "hpci-adoption": "adoptionEvent"};
  const relationshipKeys = {requires: "requires", informs: "informs", constrains: "constrains", enables: "enables", "co-evolves": "coEvolves"};
  const page = document.body.dataset.page;
  let language = readLanguage();
  let activeDomain = "all";
  let activeRoadmapGroup = "all";
  let activeRoadmapMilestoneId = null;
  const selectedRoadmaps = new Set(data.roadmaps.map((item) => item.export_id));

  function readLanguage() {
    try { const value = window.localStorage.getItem("openfs-language"); if (value === "ja" || value === "en") return value; } catch (_error) {}
    return "ja";
  }
  function rememberLanguage(value) { try { window.localStorage.setItem("openfs-language", value); } catch (_error) {} }
  function tr(key) { return copy[language][key] || key; }
  function localized(item, field) { return item?.[`${field}_${language}`] || item?.[field] || ""; }
  function setText(id, value) { const element = document.getElementById(id); if (element) element.textContent = value; }
  function formatJst(value) { return new Intl.DateTimeFormat(language === "ja" ? "ja-JP" : "en-GB", {timeZone: "Asia/Tokyo", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false}).format(new Date(value)); }
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
    setText("license-status", `License: ${data.publication.license}`);
  }

  function renderRoadmapIndex() {
    const query = document.getElementById("roadmap-search").value.trim().toLocaleLowerCase(language);
    const root = document.getElementById("roadmap-rows"); root.replaceChildren();
    const filtered = data.roadmaps.filter((roadmap) => {
      const domainMatch = activeDomain === "all" || roadmap.domain === activeDomain;
      const searchText = [roadmap.title_ja, roadmap.title_en, roadmap.domain, roadmap.roadmap_id].join(" ").toLocaleLowerCase(language);
      return domainMatch && (!query || searchText.includes(query));
    });
    filtered.forEach((roadmap) => {
      const row = document.createElement("tr"); const title = document.createElement("td"); const link = document.createElement("a"); link.className = "roadmap-title-link"; link.href = `../${roadmap.path}?v=${encodeURIComponent(data.site.commit_sha)}`; link.textContent = language === "ja" ? roadmap.title_ja : roadmap.title_en;
      const note = document.createElement("span"); note.className = "roadmap-row-note"; note.textContent = `${roadmap.track_count} ${tr("tracksUnit")} / ${roadmap.milestone_count} ${tr("milestonesUnit")} / ${roadmap.coverage_gap_count} ${tr("gapsUnit")}`; title.append(link, note);
      const domain = document.createElement("td"); domain.textContent = domainLabels[language][roadmap.domain]; const horizon = document.createElement("td"); horizon.textContent = `${roadmap.horizon.start_year}-${roadmap.horizon.end_year}`; const asOf = document.createElement("td"); asOf.textContent = roadmap.as_of; const research = document.createElement("td"); research.textContent = statusLabel(roadmap.research_status); const consensus = document.createElement("td"); consensus.textContent = statusLabel(roadmap.consensus_status);
      const updated = document.createElement("td"); const commit = document.createElement("a"); commit.href = roadmap.source_commit_url; commit.target = "_blank"; commit.rel = "noopener noreferrer"; commit.textContent = formatJst(roadmap.updated_at); updated.append(commit); row.append(title, domain, horizon, asOf, research, consensus, updated); root.append(row);
    });
    document.getElementById("roadmap-empty").hidden = filtered.length !== 0;
  }

  function appendSourceList(root, roadmap, sourceIds) {
    const sources = sourceMap(roadmap); sourceIds.forEach((sourceId) => { const source = sources.get(sourceId); if (!source) return; const item = document.createElement("li"); const link = document.createElement("a"); link.href = source.url; link.target = "_blank"; link.rel = "noopener noreferrer"; link.textContent = source.title; const publisher = document.createElement("span"); publisher.textContent = `${source.publisher} · ${source.source_class}`; item.append(link, publisher); root.append(item); });
  }
  function renderRoadmapLegend() {
    const root = document.getElementById("roadmap-legend"); root.replaceChildren(); ["commercial", "sample", "standard", "target", "concept", "pilot", "decision-gate", "deployment", "undated"].forEach((maturity) => { const item = document.createElement("span"); item.className = `legend-item maturity-${maturity}`; item.textContent = tr(maturityKeys[maturity]); root.append(item); });
  }
  function renderGroupFilter(roadmap) {
    const root = document.getElementById("roadmap-group-filter"); root.replaceChildren();
    [{group_id: "all"}, ...roadmap.groups].forEach((group) => { const button = document.createElement("button"); button.type = "button"; button.dataset.roadmapGroup = group.group_id; button.classList.toggle("active", group.group_id === activeRoadmapGroup); button.textContent = group.group_id === "all" ? tr("all") : localized(group, "name"); button.addEventListener("click", () => { activeRoadmapGroup = group.group_id; renderRoadmapDetail(); }); root.append(button); });
  }
  function milestoneCellKey(milestone) { if (milestone.year === null) return "undated"; return `${milestone.year}-${milestone.quarter || "Q?"}`; }
  function renderRoadmapTimeline(roadmap) {
    const root = document.getElementById("roadmap-timeline"); root.replaceChildren(); const tracks = roadmap.tracks.filter((track) => activeRoadmapGroup === "all" || track.group === activeRoadmapGroup); const years = []; for (let year = roadmap.horizon.start_year; year <= roadmap.horizon.end_year; year += 1) years.push(year);
    const table = document.createElement("table"); table.className = "roadmap-table"; const colgroup = document.createElement("colgroup"); ["roadmap-tech-column", "roadmap-vendor-column", ...Array(years.length * 5).fill("roadmap-quarter-column"), "roadmap-undated-column"].forEach((className) => { const col = document.createElement("col"); col.className = className; colgroup.append(col); });
    const head = document.createElement("thead"); const yearRow = document.createElement("tr"); const trackHead = document.createElement("th"); trackHead.rowSpan = 2; trackHead.className = "roadmap-tech-column"; trackHead.textContent = tr("trackColumn"); const ownerHead = document.createElement("th"); ownerHead.rowSpan = 2; ownerHead.className = "roadmap-vendor-column"; ownerHead.textContent = tr("ownerColumn"); yearRow.append(trackHead, ownerHead); years.forEach((year) => { const cell = document.createElement("th"); cell.colSpan = 5; cell.className = "roadmap-year-heading"; cell.textContent = year; yearRow.append(cell); }); const undated = document.createElement("th"); undated.rowSpan = 2; undated.className = "roadmap-year-heading"; undated.textContent = tr("undatedColumn"); yearRow.append(undated);
    const quarterRow = document.createElement("tr"); years.forEach(() => ["Q1", "Q2", "Q3", "Q4", tr("quarterUnknown")].forEach((label) => { const cell = document.createElement("th"); cell.className = "roadmap-quarter-heading"; cell.textContent = label; quarterRow.append(cell); })); head.append(yearRow, quarterRow);
    const body = document.createElement("tbody"); tracks.forEach((track) => { const lanes = roadmap.lanes.filter((lane) => lane.track_id === track.track_id); lanes.forEach((lane, laneIndex) => { const row = document.createElement("tr"); if (laneIndex === 0) { const cell = document.createElement("th"); cell.scope = "rowgroup"; cell.rowSpan = lanes.length; cell.className = "roadmap-tech-column roadmap-technology-cell"; const name = document.createElement("strong"); name.textContent = localized(track, "name"); const group = document.createElement("span"); group.textContent = localized(roadmap.groups.find((item) => item.group_id === track.group), "name"); cell.append(name, group); row.append(cell); }
      const owner = document.createElement("th"); owner.scope = "row"; owner.className = "roadmap-vendor-column roadmap-vendor-cell"; const ownerName = document.createElement("strong"); ownerName.textContent = lane.owner; const scope = document.createElement("span"); scope.textContent = localized(lane, "scope"); owner.append(ownerName, scope); row.append(owner);
      const keys = years.flatMap((year) => ["Q1", "Q2", "Q3", "Q4", "Q?"].map((quarter) => `${year}-${quarter}`)); keys.push("undated"); keys.forEach((key) => { const cell = document.createElement("td"); lane.milestones.filter((milestone) => milestoneCellKey(milestone) === key).forEach((milestone) => { const button = document.createElement("button"); button.type = "button"; button.className = `roadmap-milestone maturity-${milestone.maturity} priority-${milestone.comparison_priority}`; button.textContent = localized(milestone, "label"); button.setAttribute("aria-haspopup", "dialog"); button.addEventListener("click", () => openRoadmapMilestone(milestone.milestone_id)); cell.append(button); }); row.append(cell); }); body.append(row); }); }); table.append(colgroup, head, body); root.append(table);
  }
  function renderTrackDetails(roadmap) {
    const root = document.getElementById("roadmap-track-details"); root.replaceChildren(); roadmap.tracks.filter((track) => activeRoadmapGroup === "all" || track.group === activeRoadmapGroup).forEach((track) => { const details = document.createElement("details"); details.className = "memory-technology-note"; const toggle = document.createElement("summary"); const name = document.createElement("strong"); name.textContent = localized(track, "name"); const summary = document.createElement("span"); summary.textContent = localized(track, "summary"); toggle.append(name, summary); const body = document.createElement("div"); body.className = "memory-technology-note-body"; const stateTitle = document.createElement("h4"); stateTitle.textContent = tr("currentState"); const state = document.createElement("p"); state.textContent = localized(track, "current_state"); const implicationTitle = document.createElement("h4"); implicationTitle.textContent = tr("hpciImplications"); const implication = document.createElement("p"); implication.textContent = localized(track, "hpci_implications"); const sourcesTitle = document.createElement("h4"); sourcesTitle.textContent = tr("publicSources"); const sources = document.createElement("ul"); sources.className = "source-list memory-source-list"; appendSourceList(sources, roadmap, track.source_ids); body.append(stateTitle, state, implicationTitle, implication, sourcesTitle, sources); details.append(toggle, body); root.append(details); });
  }
  function renderDependencies(roadmap) {
    const root = document.getElementById("roadmap-dependencies"); root.replaceChildren(); roadmap.dependencies.forEach((dependency) => { const item = document.createElement("article"); item.className = "roadmap-dependency-item"; const route = document.createElement("p"); route.className = "dependency-route"; route.textContent = `${roadmapName(dependency.upstream_roadmap_id)} → ${roadmapName(dependency.downstream_roadmap_id)}`; const relation = document.createElement("span"); relation.className = "summary-status"; relation.textContent = `${tr(relationshipKeys[dependency.relationship])} · ${dependency.basis === "evidence-backed" ? tr("evidenceBacked") : tr("openfsAssessment")}`; const statement = document.createElement("p"); statement.textContent = localized(dependency, "statement"); item.append(route, relation, statement); root.append(item); });
  }
  function renderCoverageGaps(roadmap) {
    const root = document.getElementById("roadmap-gaps"); root.replaceChildren(); roadmap.coverage_gaps.forEach((gap) => { const item = document.createElement("li"); const scope = document.createElement("strong"); scope.textContent = `${gap.gap_id} · ${localized(gap, "scope")}`; const impact = document.createElement("span"); impact.textContent = `${tr("gapImpact")}: ${localized(gap, "impact")}`; const action = document.createElement("span"); action.textContent = `${tr("gapNextAction")}: ${localized(gap, "next_action")}`; item.append(scope, impact, action); root.append(item); });
  }
  function renderRoadmapDetail() {
    const roadmap = currentRoadmap(); if (!roadmap) { document.querySelector("main").textContent = tr("noRoadmaps"); return; } document.title = `${localized(roadmap, "title")} | OpenFS`; setText("roadmap-breadcrumb-title", localized(roadmap, "title")); setText("roadmap-title", localized(roadmap, "title")); setText("roadmap-summary", localized(roadmap, "summary")); setText("roadmap-as-of", roadmap.as_of); setText("roadmap-horizon", `${roadmap.horizon.start_year}-${roadmap.horizon.end_year}`); setText("roadmap-research-status", statusLabel(roadmap.research_status)); setText("roadmap-coverage-status", statusLabel(roadmap.coverage_status)); setText("roadmap-consensus-status", statusLabel(roadmap.consensus_status)); setText("roadmap-caveat-text", localized(roadmap, "caveat")); setText("roadmap-artifact-id", roadmap.export_id); setText("roadmap-revision-updated", formatJst(roadmap.updated_at));
    const updated = document.getElementById("roadmap-updated"); updated.href = roadmap.source_commit_url; updated.textContent = formatJst(roadmap.updated_at); const commit = document.getElementById("roadmap-source-commit"); commit.href = roadmap.source_commit_url; commit.textContent = roadmap.source_commit; setText("roadmap-source-coverage", `${roadmap.source_coverage.primary_source_count}/${roadmap.source_coverage.source_count} (${Math.round(roadmap.source_coverage.primary_source_ratio * 100)}%)`); renderGroupFilter(roadmap); renderRoadmapLegend(); renderRoadmapTimeline(roadmap); renderTrackDetails(roadmap); renderDependencies(roadmap); renderCoverageGaps(roadmap);
  }
  function findRoadmapMilestone(milestoneId) { const roadmap = currentRoadmap(); for (const lane of roadmap.lanes) { const milestone = lane.milestones.find((item) => item.milestone_id === milestoneId); if (milestone) return {roadmap, track: roadmap.tracks.find((item) => item.track_id === lane.track_id), lane, milestone}; } return null; }
  function appendMetaItem(root, label, value) { const item = document.createElement("div"); const term = document.createElement("dt"); term.textContent = label; const description = document.createElement("dd"); description.textContent = value; item.append(term, description); root.append(item); }
  function renderRoadmapDialog() {
    if (!activeRoadmapMilestoneId) return; const match = findRoadmapMilestone(activeRoadmapMilestoneId); if (!match) return; const {roadmap, track, lane, milestone} = match; const period = milestone.year === null ? tr("undatedColumn") : `${milestone.year} ${milestone.quarter || tr("quarterUnknown")}`; setText("roadmap-dialog-id", milestone.milestone_id); setText("roadmap-dialog-title", localized(milestone, "label")); setText("roadmap-dialog-meta", `${localized(track, "name")} / ${lane.owner} / ${period}`);
    const root = document.getElementById("roadmap-dialog-content"); root.replaceChildren(); const section = document.createElement("section"); section.className = "roadmap-milestone-detail"; const status = document.createElement("span"); status.className = `summary-status maturity-${milestone.maturity}`; status.textContent = tr(maturityKeys[milestone.maturity]); const title = document.createElement("h3"); title.textContent = tr("milestoneDetail"); const detail = document.createElement("p"); detail.textContent = localized(milestone, "detail"); const meta = document.createElement("dl"); meta.className = "research-meta roadmap-dialog-meta-list"; appendMetaItem(meta, tr("trackColumn"), localized(track, "name")); appendMetaItem(meta, tr("ownerColumn"), `${lane.owner} / ${localized(lane, "scope")}`); appendMetaItem(meta, tr("eventType"), tr(eventTypeKeys[milestone.event_type])); appendMetaItem(meta, tr("timingBasis"), tr(timingBasisKeys[milestone.timing_basis])); appendMetaItem(meta, tr("timingPrecision"), tr(timingPrecisionKeys[milestone.timing_precision])); appendMetaItem(meta, tr("researchAsOf"), roadmap.as_of); const sourcesTitle = document.createElement("h4"); sourcesTitle.textContent = tr("publicSources"); const sources = document.createElement("ul"); sources.className = "source-list roadmap-dialog-source-list"; appendSourceList(sources, roadmap, milestone.source_ids); section.append(status, title, detail, meta, sourcesTitle, sources); root.append(section);
  }
  function openRoadmapMilestone(milestoneId) { activeRoadmapMilestoneId = milestoneId; renderRoadmapDialog(); const dialog = document.getElementById("roadmap-dialog"); if (!dialog.open) dialog.showModal(); }

  function renderCompareControls() {
    const root = document.getElementById("compare-controls"); root.replaceChildren(); data.roadmaps.forEach((roadmap) => { const label = document.createElement("label"); label.className = "compare-option"; const input = document.createElement("input"); input.type = "checkbox"; input.checked = selectedRoadmaps.has(roadmap.export_id); input.addEventListener("change", () => { input.checked ? selectedRoadmaps.add(roadmap.export_id) : selectedRoadmaps.delete(roadmap.export_id); renderComparison(); }); const text = document.createElement("span"); text.textContent = language === "ja" ? roadmap.title_ja : roadmap.title_en; label.append(input, text); root.append(label); });
  }
  function renderCompareMetrics(artifacts) {
    const root = document.getElementById("compare-metrics"); root.replaceChildren(); artifacts.forEach((roadmap) => { const card = document.createElement("article"); card.className = "compare-metric"; const title = document.createElement("h3"); const link = document.createElement("a"); link.href = `../${roadmap.slug}/`; link.textContent = localized(roadmap, "title"); title.append(link); const values = document.createElement("dl"); [[tr("sourceCoverage"), `${roadmap.source_coverage.primary_source_count}/${roadmap.source_coverage.source_count}`], [tr("keyMilestones"), roadmap.lanes.flatMap((lane) => lane.milestones).filter((item) => item.comparison_priority === "key").length], [tr("coverageGapsTitle"), roadmap.coverage_gaps.length], [tr("dependenciesTitle"), roadmap.dependencies.length]].forEach(([term, value]) => { const wrap = document.createElement("div"); const dt = document.createElement("dt"); dt.textContent = term; const dd = document.createElement("dd"); dd.textContent = value; wrap.append(dt, dd); values.append(wrap); }); card.append(title, values); root.append(card); });
  }
  function renderCompareTimeline(artifacts) {
    const root = document.getElementById("compare-timeline"); root.replaceChildren(); const years = [2026, 2027, 2028, 2029, 2030, 2031, 2032]; const table = document.createElement("table"); table.className = "comparison-table"; const head = document.createElement("thead"); const row = document.createElement("tr"); [tr("roadmapColumn"), ...years].forEach((label) => { const cell = document.createElement("th"); cell.textContent = label; row.append(cell); }); head.append(row); const body = document.createElement("tbody");
    artifacts.forEach((roadmap) => { const item = document.createElement("tr"); const title = document.createElement("th"); title.scope = "row"; const link = document.createElement("a"); link.href = `../${roadmap.slug}/`; link.textContent = localized(roadmap, "title"); title.append(link); item.append(title); years.forEach((year) => { const cell = document.createElement("td"); roadmap.lanes.flatMap((lane) => lane.milestones.map((milestone) => ({lane, milestone}))).filter(({milestone}) => milestone.year === year && milestone.comparison_priority === "key").forEach(({lane, milestone}) => { const entry = document.createElement("span"); entry.className = `comparison-milestone maturity-${milestone.maturity}`; entry.textContent = `${milestone.quarter || tr("quarterUnknown")} · ${localized(milestone, "label")} (${lane.owner})`; cell.append(entry); }); item.append(cell); }); body.append(item); }); table.append(head, body); root.append(table);
  }
  function renderCompareDependencies(artifacts) {
    const root = document.getElementById("compare-dependencies"); root.replaceChildren(); const allowed = new Set(artifacts.map((item) => item.roadmap_id)); const dependencies = artifacts.flatMap((roadmap) => roadmap.dependencies).filter((item) => allowed.has(item.upstream_roadmap_id) && allowed.has(item.downstream_roadmap_id)); dependencies.forEach((dependency) => { const item = document.createElement("li"); const route = document.createElement("strong"); route.textContent = `${roadmapName(dependency.upstream_roadmap_id)} → ${roadmapName(dependency.downstream_roadmap_id)}`; const text = document.createElement("span"); text.textContent = `${tr(relationshipKeys[dependency.relationship])}: ${localized(dependency, "statement")}`; item.append(route, text); root.append(item); });
  }
  function renderComparison() { const artifacts = data.roadmap_artifacts.filter((item) => selectedRoadmaps.has(item.export_id)); renderCompareControls(); renderCompareMetrics(artifacts); renderCompareTimeline(artifacts); renderCompareDependencies(artifacts); }

  function render() { applyStaticCopy(); if (page === "roadmap-index") renderRoadmapIndex(); if (page === "roadmap-detail") { renderRoadmapDetail(); renderRoadmapDialog(); } if (page === "roadmap-compare") renderComparison(); }
  document.querySelectorAll("[data-language]").forEach((button) => button.addEventListener("click", () => { language = button.dataset.language; rememberLanguage(language); render(); }));
  document.querySelectorAll("[data-roadmap-domain]").forEach((button) => button.addEventListener("click", () => { activeDomain = button.dataset.roadmapDomain; document.querySelectorAll("[data-roadmap-domain]").forEach((item) => item.classList.toggle("active", item === button)); renderRoadmapIndex(); }));
  document.getElementById("roadmap-search")?.addEventListener("input", renderRoadmapIndex);
  const dialog = document.getElementById("roadmap-dialog"); document.getElementById("roadmap-dialog-close")?.addEventListener("click", () => dialog.close()); dialog?.addEventListener("click", (event) => { if (event.target === event.currentTarget) event.currentTarget.close(); }); dialog?.addEventListener("close", () => { activeRoadmapMilestoneId = null; });
  render();
})();
