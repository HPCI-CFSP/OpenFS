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
      compareRoadmaps: "6本を比較", openEvidence: "根拠監査を開く", compareKicker: "P0初期公開波", compareTitle: "ロードマップ横断比較", compareLead: "重要マイルストーン、根拠カバレッジ、Coverage Gap、ロードマップ間依存を同じ尺度で比較します。",
      domainFilter: "分野フィルタ", all: "すべて", search: "検索", searchPlaceholder: "名称、分野", roadmapColumn: "ロードマップ", domainColumn: "分野", horizonColumn: "対象期間", researchAsOf: "調査基準日", researchStatus: "調査状態", coverageStatus: "調査範囲", consensusStatus: "Consensus", updatedColumn: "更新日時", noRoadmaps: "条件に一致するロードマップはありません。",
      roadmapKicker: "根拠付き暫定ロードマップ", roadmapFilter: "トラック群フィルタ", trackColumn: "技術・判断トラック", ownerColumn: "主体／対象", quarterUnknown: "四半期未公表", undatedColumn: "時期未公表", roadmapTableNote: "矩形は公開情報が許す時期の範囲を示します。年のみ公表された項目はQ1-Q4、半期は該当する2四半期にまたがり、継続期間を意味しません。空欄は日程未確認です。",
      trackNotesKicker: "トラック別ノート", trackNotesTitle: "現状とHPCI整備への示唆", currentState: "現在の状況", hpciImplications: "HPCI整備への示唆", roadmapCaveat: "公開時の注意事項", dependenciesKicker: "相互依存", dependenciesTitle: "他ロードマップとの依存関係", coverageGapsTitle: "Coverage Gap", gapImpact: "影響", gapNextAction: "次の確認",
      comparisonsKicker: "技術選択の比較", comparisonsTitle: "関連技術の比較表", comparisonsLead: "役割、利点、制約、適用先を共通の軸で比較します。", decisionUse: "判断への使い方", comparisonCaveat: "比較上の注意", glossaryKicker: "共通用語集", glossaryTitle: "このロードマップの用語", glossaryLead: "用語を選択すると、中央管理された説明と根拠資料を表示します。", termDefinition: "用語の説明", relatedTerms: "関連用語", referenceSources: "用語・比較の根拠", referenceRevision: "共通データ更新", timingWindow: "表示範囲", timingWindowNote: "表示範囲は公開情報の時期精度を表し、事象の継続期間ではありません。", quarterNotPublished: "Q未公表",
      commercial: "製品・量産", sample: "サンプル", standard: "標準", published: "公開済み", target: "公表目標", concept: "構想・研究", pilot: "実証", decisionGate: "判断ゲート", deployment: "導入", undated: "時期未公表",
      timingBasis: "時期の根拠", timingPrecision: "時期の精度", eventType: "イベント種別", quarterPrecision: "四半期", halfYearPrecision: "半期", yearPrecision: "年", undatedPrecision: "未公表", milestoneDetail: "マイルストーン詳細", publicSources: "公開根拠資料",
      observed: "確認済み", asOfBaseline: "基準日時点の提供状況", standardRelease: "標準公開", vendorTarget: "ベンダー目標", projectTarget: "プロジェクト目標", policyTarget: "政策目標", openfsPlan: "OpenFS暫定計画", noPublicDate: "公開時期なし",
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
      compareRoadmaps: "Compare six", openEvidence: "Open evidence assurance", compareKicker: "P0 INITIAL PUBLICATION WAVE", compareTitle: "Cross-roadmap comparison", compareLead: "Compare key milestones, evidence coverage, Coverage Gaps, and cross-roadmap dependencies on common scales.",
      domainFilter: "Domain filter", all: "All", search: "Search", searchPlaceholder: "Title or domain", roadmapColumn: "Roadmap", domainColumn: "Domain", horizonColumn: "Horizon", researchAsOf: "Research as of", researchStatus: "Research status", coverageStatus: "Coverage", consensusStatus: "Consensus", updatedColumn: "Updated", noRoadmaps: "No roadmaps match the current filters.",
      roadmapKicker: "EVIDENCE-BASED PROVISIONAL ROADMAP", roadmapFilter: "Track group filter", trackColumn: "Technology / decision track", ownerColumn: "Owner / scope", quarterUnknown: "quarter not published", undatedColumn: "Timing not public", roadmapTableNote: "Each rectangle shows the timing window supported by public information. A year-only item spans Q1-Q4 and a half-year item spans two quarters; neither represents event duration. Blank cells mean no dated milestone was confirmed.",
      trackNotesKicker: "TRACK NOTES", trackNotesTitle: "Current state and implications for HPCI", currentState: "Current state", hpciImplications: "Implications for HPCI", roadmapCaveat: "Publication caveat", dependenciesKicker: "INTERDEPENDENCIES", dependenciesTitle: "Dependencies on other roadmaps", coverageGapsTitle: "Coverage Gaps", gapImpact: "Impact", gapNextAction: "Next check",
      comparisonsKicker: "TECHNOLOGY CHOICES", comparisonsTitle: "Related technology comparisons", comparisonsLead: "Compare roles, strengths, constraints, and suitable uses on common dimensions.", decisionUse: "How to use this comparison", comparisonCaveat: "Comparison caveat", glossaryKicker: "SHARED GLOSSARY", glossaryTitle: "Terms in this roadmap", glossaryLead: "Select a term to open its centrally maintained explanation and supporting sources.", termDefinition: "Term definition", relatedTerms: "Related terms", referenceSources: "Glossary and comparison sources", referenceRevision: "Shared data updated", timingWindow: "Displayed window", timingWindowNote: "The displayed window expresses public timing precision, not the duration of the event.", quarterNotPublished: "quarter not published",
      commercial: "product / volume", sample: "sample", standard: "standard", published: "published", target: "published target", concept: "concept / research", pilot: "pilot", decisionGate: "decision gate", deployment: "deployment", undated: "timing not public",
      timingBasis: "Timing basis", timingPrecision: "Timing precision", eventType: "Event type", quarterPrecision: "quarter", halfYearPrecision: "half-year", yearPrecision: "year", undatedPrecision: "not public", milestoneDetail: "Milestone detail", publicSources: "Public supporting sources",
      observed: "observed", asOfBaseline: "availability as of baseline", standardRelease: "standard release", vendorTarget: "vendor target", projectTarget: "project target", policyTarget: "policy target", openfsPlan: "OpenFS provisional plan", noPublicDate: "no public date",
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
  const maturityKeys = {commercial: "commercial", sample: "sample", standard: "standard", published: "published", target: "target", concept: "concept", pilot: "pilot", "decision-gate": "decisionGate", deployment: "deployment", undated: "undated"};
  const timingBasisKeys = {observed: "observed", "as-of-baseline": "asOfBaseline", "standard-release": "standardRelease", "vendor-target": "vendorTarget", "project-target": "projectTarget", "policy-target": "policyTarget", "openfs-provisional-plan": "openfsPlan", "no-public-date": "noPublicDate"};
  const timingPrecisionKeys = {quarter: "quarterPrecision", "half-year": "halfYearPrecision", year: "yearPrecision", undated: "undatedPrecision"};
  const eventTypeKeys = {product: "productEvent", standard: "standardEvent", research: "researchEvent", policy: "policyEvent", "hpci-evaluation": "evaluationEvent", "hpci-adoption": "adoptionEvent"};
  const relationshipKeys = {requires: "requires", informs: "informs", constrains: "constrains", enables: "enables", "co-evolves": "coEvolves"};
  const page = document.body.dataset.page;
  let language = readLanguage();
  let activeDomain = "all";
  let activeRoadmapGroup = "all";
  let activeRoadmapMilestoneId = null;
  let activeTermId = null;
  const selectedRoadmaps = new Set(data.roadmaps.map((item) => item.export_id));

  function readLanguage() {
    try { const value = window.localStorage.getItem("openfs-language"); if (value === "ja" || value === "en") return value; } catch (_error) {}
    return "ja";
  }
  function rememberLanguage(value) { try { window.localStorage.setItem("openfs-language", value); } catch (_error) {} }
  function tr(key) { return copy[language][key] || key; }
  function localized(item, field) { return item?.[`${field}_${language}`] || item?.[field] || ""; }
  function setText(id, value) { const element = document.getElementById(id); if (element) element.textContent = value; }
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
  function renderRoadmapTimeline(roadmap) {
    const root = document.getElementById("roadmap-timeline"); root.replaceChildren(); const tracks = roadmap.tracks.filter((track) => activeRoadmapGroup === "all" || track.group === activeRoadmapGroup); const years = []; for (let year = roadmap.horizon.start_year; year <= roadmap.horizon.end_year; year += 1) years.push(year);
    const table = document.createElement("table"); table.className = "roadmap-table"; table.style.width = `${512 + years.length * 448}px`; table.style.minWidth = table.style.width; const colgroup = document.createElement("colgroup"); ["roadmap-tech-column", "roadmap-vendor-column", ...Array(years.length).fill("roadmap-year-column"), "roadmap-undated-column"].forEach((className) => { const col = document.createElement("col"); col.className = className; colgroup.append(col); });
    const head = document.createElement("thead"); const yearRow = document.createElement("tr"); const trackHead = document.createElement("th"); trackHead.className = "roadmap-tech-column"; trackHead.textContent = tr("trackColumn"); const ownerHead = document.createElement("th"); ownerHead.className = "roadmap-vendor-column"; ownerHead.textContent = tr("ownerColumn"); yearRow.append(trackHead, ownerHead); years.forEach((year) => { const cell = document.createElement("th"); cell.className = "roadmap-year-heading"; const label = document.createElement("strong"); label.textContent = year; const quarters = document.createElement("span"); quarters.className = "roadmap-quarter-scale"; ["Q1", "Q2", "Q3", "Q4"].forEach((quarter) => { const item = document.createElement("span"); item.textContent = quarter; quarters.append(item); }); cell.append(label, quarters); yearRow.append(cell); }); const undated = document.createElement("th"); undated.className = "roadmap-year-heading roadmap-undated-heading"; undated.textContent = tr("undatedColumn"); yearRow.append(undated); head.append(yearRow);
    const body = document.createElement("tbody"); tracks.forEach((track) => { const lanes = roadmap.lanes.filter((lane) => lane.track_id === track.track_id); lanes.forEach((lane, laneIndex) => { const row = document.createElement("tr"); if (laneIndex === 0) { const cell = document.createElement("th"); cell.scope = "rowgroup"; cell.rowSpan = lanes.length; cell.className = "roadmap-tech-column roadmap-technology-cell"; const name = document.createElement("strong"); appendGlossaryText(name, localized(track, "name"), roadmap); const group = document.createElement("span"); group.textContent = localized(roadmap.groups.find((item) => item.group_id === track.group), "name"); cell.append(name, group); row.append(cell); }
      const owner = document.createElement("th"); owner.scope = "row"; owner.className = "roadmap-vendor-column roadmap-vendor-cell"; const ownerName = document.createElement("strong"); ownerName.textContent = lane.owner; const scope = document.createElement("span"); scope.textContent = localized(lane, "scope"); owner.append(ownerName, scope); row.append(owner);
      years.forEach((year) => { const cell = document.createElement("td"); cell.className = "roadmap-year-cell"; const laneGrid = document.createElement("div"); laneGrid.className = "roadmap-year-lane"; placeMilestones(lane.milestones.filter((milestone) => milestone.year === year)).forEach(({milestone, start, end, row: gridRow}) => { const button = milestoneButton(milestone); button.style.gridColumn = `${start} / ${end}`; button.style.gridRow = String(gridRow); laneGrid.append(button); }); cell.append(laneGrid); row.append(cell); }); const undatedCell = document.createElement("td"); undatedCell.className = "roadmap-undated-cell"; lane.milestones.filter((milestone) => milestone.year === null).forEach((milestone) => undatedCell.append(milestoneButton(milestone))); row.append(undatedCell); body.append(row); }); }); table.append(colgroup, head, body); root.append(table);
  }
  function renderTrackDetails(roadmap) {
    const root = document.getElementById("roadmap-track-details"); root.replaceChildren(); roadmap.tracks.filter((track) => activeRoadmapGroup === "all" || track.group === activeRoadmapGroup).forEach((track) => { const details = document.createElement("details"); details.className = "memory-technology-note"; const toggle = document.createElement("summary"); const name = document.createElement("strong"); appendGlossaryText(name, localized(track, "name"), roadmap); const summary = document.createElement("span"); appendGlossaryText(summary, localized(track, "summary"), roadmap); toggle.append(name, summary); const body = document.createElement("div"); body.className = "memory-technology-note-body"; const stateTitle = document.createElement("h4"); stateTitle.textContent = tr("currentState"); const state = document.createElement("p"); appendGlossaryText(state, localized(track, "current_state"), roadmap); const implicationTitle = document.createElement("h4"); implicationTitle.textContent = tr("hpciImplications"); const implication = document.createElement("p"); appendGlossaryText(implication, localized(track, "hpci_implications"), roadmap); const sourcesTitle = document.createElement("h4"); sourcesTitle.textContent = tr("publicSources"); const sources = document.createElement("ul"); sources.className = "source-list memory-source-list"; appendSourceList(sources, roadmap, track.source_ids); body.append(stateTitle, state, implicationTitle, implication, sourcesTitle, sources); details.append(toggle, body); root.append(details); });
  }
  function renderTechnologyComparisons(roadmap) {
    const root = document.getElementById("roadmap-comparisons"); root.replaceChildren(); const terms = termMap(); referenceData().comparison_sets.filter((comparison) => comparison.roadmap_ids.includes(roadmap.roadmap_id)).forEach((comparison) => { const section = document.createElement("section"); section.className = "technology-comparison"; const title = document.createElement("h4"); title.textContent = localized(comparison, "title"); const summary = document.createElement("p"); summary.className = "technology-comparison-summary"; summary.textContent = localized(comparison, "summary"); const use = document.createElement("p"); use.className = "technology-comparison-use"; const useLabel = document.createElement("strong"); useLabel.textContent = `${tr("decisionUse")}: `; use.append(useLabel, document.createTextNode(localized(comparison, "decision_use"))); const wrap = document.createElement("div"); wrap.className = "technology-comparison-wrap"; const table = document.createElement("table"); table.className = "technology-comparison-table"; const head = document.createElement("thead"); const headRow = document.createElement("tr"); const termHead = document.createElement("th"); termHead.textContent = tr("trackColumn"); headRow.append(termHead); comparison.columns.forEach((column) => { const cell = document.createElement("th"); cell.textContent = localized(column, "label"); headRow.append(cell); }); head.append(headRow); const body = document.createElement("tbody"); comparison.rows.forEach((row) => { const item = document.createElement("tr"); const termCell = document.createElement("th"); termCell.scope = "row"; const term = terms.get(row.term_id); const button = document.createElement("button"); button.type = "button"; button.className = "comparison-term-link"; button.textContent = localized(term, "label"); button.setAttribute("aria-haspopup", "dialog"); button.addEventListener("click", () => openRoadmapTerm(row.term_id)); termCell.append(button); item.append(termCell); comparison.columns.forEach((column) => { const cell = document.createElement("td"); const value = row.cells.find((entry) => entry.column_id === column.column_id); cell.textContent = localized(value, "text"); item.append(cell); }); body.append(item); }); table.append(head, body); wrap.append(table); const caveat = document.createElement("p"); caveat.className = "technology-comparison-caveat"; const caveatLabel = document.createElement("strong"); caveatLabel.textContent = `${tr("comparisonCaveat")}: `; caveat.append(caveatLabel, document.createTextNode(localized(comparison, "caveat"))); section.append(title, summary, use, wrap, caveat); root.append(section); });
  }
  function renderGlossary(roadmap) {
    const root = document.getElementById("roadmap-glossary"); root.replaceChildren(); relevantTerms(roadmap).forEach((term) => { const item = document.createElement("article"); item.className = "roadmap-glossary-item"; const heading = document.createElement("div"); const button = document.createElement("button"); button.type = "button"; button.className = "glossary-entry-link"; button.textContent = localized(term, "label"); button.setAttribute("aria-haspopup", "dialog"); button.addEventListener("click", () => openRoadmapTerm(term.term_id)); const category = document.createElement("span"); category.textContent = term.category; heading.append(button, category); const definition = document.createElement("p"); definition.textContent = localized(term, "short_definition"); item.append(heading, definition); root.append(item); }); const revision = document.getElementById("roadmap-reference-updated"); revision.href = referenceData().source_commit_url; revision.textContent = `${formatJst(referenceData().updated_at)} · ${referenceData().source_commit.slice(0, 7)}`;
  }
  function renderDependencies(roadmap) {
    const root = document.getElementById("roadmap-dependencies"); root.replaceChildren(); roadmap.dependencies.forEach((dependency) => { const item = document.createElement("article"); item.className = "roadmap-dependency-item"; const route = document.createElement("p"); route.className = "dependency-route"; route.textContent = `${roadmapName(dependency.upstream_roadmap_id)} → ${roadmapName(dependency.downstream_roadmap_id)}`; const relation = document.createElement("span"); relation.className = "summary-status"; relation.textContent = `${tr(relationshipKeys[dependency.relationship])} · ${dependency.basis === "evidence-backed" ? tr("evidenceBacked") : tr("openfsAssessment")}`; const statement = document.createElement("p"); appendGlossaryText(statement, localized(dependency, "statement"), roadmap); item.append(route, relation, statement); root.append(item); });
  }
  function renderCoverageGaps(roadmap) {
    const root = document.getElementById("roadmap-gaps"); root.replaceChildren(); roadmap.coverage_gaps.forEach((gap) => { const item = document.createElement("li"); const scope = document.createElement("strong"); scope.textContent = `${gap.priority} · ${gap.gap_id} · ${localized(gap, "scope")}`; const impact = document.createElement("span"); impact.textContent = `${tr("gapImpact")}: ${localized(gap, "impact")}`; const action = document.createElement("span"); action.textContent = `${tr("gapNextAction")}: ${localized(gap, "next_action")}`; item.append(scope, impact, action); root.append(item); });
  }
  function renderRoadmapDetail() {
    const roadmap = currentRoadmap(); if (!roadmap) { document.querySelector("main").textContent = tr("noRoadmaps"); return; } document.title = `${localized(roadmap, "title")} | OpenFS`; setText("roadmap-breadcrumb-title", localized(roadmap, "title")); setText("roadmap-title", localized(roadmap, "title")); setText("roadmap-summary", localized(roadmap, "summary")); setText("roadmap-as-of", roadmap.as_of); setText("roadmap-horizon", `${roadmap.horizon.start_year}-${roadmap.horizon.end_year}`); setText("roadmap-research-status", statusLabel(roadmap.research_status)); setText("roadmap-coverage-status", statusLabel(roadmap.coverage_status)); setText("roadmap-consensus-status", statusLabel(roadmap.consensus_status)); setText("roadmap-caveat-text", localized(roadmap, "caveat")); setText("roadmap-artifact-id", roadmap.export_id); setText("roadmap-revision-updated", formatJst(roadmap.updated_at));
    const updated = document.getElementById("roadmap-updated"); updated.href = roadmap.source_commit_url; updated.textContent = formatJst(roadmap.updated_at); const commit = document.getElementById("roadmap-source-commit"); commit.href = roadmap.source_commit_url; commit.textContent = roadmap.source_commit; setText("roadmap-source-coverage", `${roadmap.source_coverage.primary_source_count}/${roadmap.source_coverage.source_count} (${Math.round(roadmap.source_coverage.primary_source_ratio * 100)}%)`); renderGroupFilter(roadmap); renderRoadmapLegend(); renderRoadmapTimeline(roadmap); renderTechnologyComparisons(roadmap); renderTrackDetails(roadmap); renderGlossary(roadmap); renderDependencies(roadmap); renderCoverageGaps(roadmap);
  }
  function findRoadmapMilestone(milestoneId) { const roadmap = currentRoadmap(); for (const lane of roadmap.lanes) { const milestone = lane.milestones.find((item) => item.milestone_id === milestoneId); if (milestone) return {roadmap, track: roadmap.tracks.find((item) => item.track_id === lane.track_id), lane, milestone}; } return null; }
  function appendMetaItem(root, label, value) { const item = document.createElement("div"); const term = document.createElement("dt"); term.textContent = label; const description = document.createElement("dd"); description.textContent = value; item.append(term, description); root.append(item); }
  function renderRoadmapDialog() {
    if (!activeRoadmapMilestoneId) return; const match = findRoadmapMilestone(activeRoadmapMilestoneId); if (!match) return; const {roadmap, track, lane, milestone} = match; const period = milestone.year === null ? tr("undatedColumn") : `${milestone.year} ${milestonePeriodLabel(milestone)}`; setText("roadmap-dialog-id", milestone.milestone_id); setText("roadmap-dialog-title", localized(milestone, "label")); setText("roadmap-dialog-meta", `${localized(track, "name")} / ${lane.owner} / ${period}`);
    const root = document.getElementById("roadmap-dialog-content"); root.replaceChildren(); const section = document.createElement("section"); section.className = "roadmap-milestone-detail"; const status = document.createElement("span"); status.className = `summary-status maturity-${milestone.maturity}`; status.textContent = tr(maturityKeys[milestone.maturity]); const title = document.createElement("h3"); title.textContent = tr("milestoneDetail"); const detail = document.createElement("p"); appendGlossaryText(detail, localized(milestone, "detail"), roadmap); const meta = document.createElement("dl"); meta.className = "research-meta roadmap-dialog-meta-list"; appendMetaItem(meta, tr("trackColumn"), localized(track, "name")); appendMetaItem(meta, tr("ownerColumn"), `${lane.owner} / ${localized(lane, "scope")}`); appendMetaItem(meta, tr("eventType"), tr(eventTypeKeys[milestone.event_type])); appendMetaItem(meta, tr("timingBasis"), tr(timingBasisKeys[milestone.timing_basis])); appendMetaItem(meta, tr("timingPrecision"), tr(timingPrecisionKeys[milestone.timing_precision])); appendMetaItem(meta, tr("timingWindow"), period); appendMetaItem(meta, tr("researchAsOf"), roadmap.as_of); const timingNote = document.createElement("p"); timingNote.className = "roadmap-timing-note"; timingNote.textContent = tr("timingWindowNote"); const sourcesTitle = document.createElement("h4"); sourcesTitle.textContent = tr("publicSources"); const sources = document.createElement("ul"); sources.className = "source-list roadmap-dialog-source-list"; appendSourceList(sources, roadmap, milestone.source_ids); section.append(status, title, detail, meta, timingNote, sourcesTitle, sources); root.append(section);
  }
  function openRoadmapMilestone(milestoneId) { activeRoadmapMilestoneId = milestoneId; renderRoadmapDialog(); const dialog = document.getElementById("roadmap-dialog"); if (!dialog.open) dialog.showModal(); }
  function appendReferenceSourceList(root, sourceRefs) {
    sourceRefs.forEach((sourceRef) => { const roadmap = data.roadmap_artifacts.find((item) => item.roadmap_id === sourceRef.roadmap_id); const source = roadmap?.sources.find((item) => item.source_id === sourceRef.source_id); if (!source) return; const item = document.createElement("li"); const link = document.createElement("a"); link.href = source.url; link.target = "_blank"; link.rel = "noopener noreferrer"; link.textContent = source.title; const publisher = document.createElement("span"); publisher.textContent = `${roadmapName(sourceRef.roadmap_id)} · ${source.publisher} · ${sourceRef.source_id}`; item.append(link, publisher); root.append(item); });
  }
  function renderRoadmapTermDialog() {
    if (!activeTermId) return; const term = termMap().get(activeTermId); if (!term) return; setText("roadmap-term-dialog-id", term.term_id); setText("roadmap-term-dialog-title", localized(term, "label")); setText("roadmap-term-dialog-meta", `${term.category} · ${referenceData().as_of}`); const root = document.getElementById("roadmap-term-dialog-content"); root.replaceChildren(); const section = document.createElement("section"); section.className = "roadmap-term-detail"; const title = document.createElement("h3"); title.textContent = tr("termDefinition"); const definition = document.createElement("p"); definition.textContent = localized(term, "definition"); const relatedTitle = document.createElement("h4"); relatedTitle.textContent = tr("relatedTerms"); const related = document.createElement("div"); related.className = "roadmap-related-terms"; term.related_term_ids.forEach((termId) => { const relatedTerm = termMap().get(termId); if (!relatedTerm) return; const button = document.createElement("button"); button.type = "button"; button.className = "related-term-link"; button.textContent = localized(relatedTerm, "label"); button.addEventListener("click", () => { activeTermId = termId; renderRoadmapTermDialog(); }); related.append(button); }); const sourcesTitle = document.createElement("h4"); sourcesTitle.textContent = tr("referenceSources"); const sources = document.createElement("ul"); sources.className = "source-list roadmap-dialog-source-list"; appendReferenceSourceList(sources, term.source_refs); section.append(title, definition, relatedTitle, related, sourcesTitle, sources); root.append(section);
  }
  function openRoadmapTerm(termId) { activeTermId = termId; renderRoadmapTermDialog(); const dialog = document.getElementById("roadmap-term-dialog"); if (!dialog.open) dialog.showModal(); }

  function renderCompareControls() {
    const root = document.getElementById("compare-controls"); root.replaceChildren(); data.roadmaps.forEach((roadmap) => { const label = document.createElement("label"); label.className = "compare-option"; const input = document.createElement("input"); input.type = "checkbox"; input.checked = selectedRoadmaps.has(roadmap.export_id); input.addEventListener("change", () => { input.checked ? selectedRoadmaps.add(roadmap.export_id) : selectedRoadmaps.delete(roadmap.export_id); renderComparison(); }); const text = document.createElement("span"); text.textContent = language === "ja" ? roadmap.title_ja : roadmap.title_en; label.append(input, text); root.append(label); });
  }
  function renderCompareMetrics(artifacts) {
    const root = document.getElementById("compare-metrics"); root.replaceChildren(); artifacts.forEach((roadmap) => { const card = document.createElement("article"); card.className = "compare-metric"; const title = document.createElement("h3"); const link = document.createElement("a"); link.href = `../${roadmap.slug}/`; link.textContent = localized(roadmap, "title"); title.append(link); const values = document.createElement("dl"); [[tr("sourceCoverage"), `${roadmap.source_coverage.primary_source_count}/${roadmap.source_coverage.source_count}`], [tr("keyMilestones"), roadmap.lanes.flatMap((lane) => lane.milestones).filter((item) => item.comparison_priority === "key").length], [tr("coverageGapsTitle"), roadmap.coverage_gaps.length], [tr("dependenciesTitle"), roadmap.dependencies.length]].forEach(([term, value]) => { const wrap = document.createElement("div"); const dt = document.createElement("dt"); dt.textContent = term; const dd = document.createElement("dd"); dd.textContent = value; wrap.append(dt, dd); values.append(wrap); }); card.append(title, values); root.append(card); });
  }
  function renderCompareTimeline(artifacts) {
    const root = document.getElementById("compare-timeline"); root.replaceChildren(); const years = [2026, 2027, 2028, 2029, 2030, 2031, 2032]; const table = document.createElement("table"); table.className = "comparison-table"; const head = document.createElement("thead"); const row = document.createElement("tr"); [tr("roadmapColumn"), ...years].forEach((label) => { const cell = document.createElement("th"); cell.textContent = label; row.append(cell); }); head.append(row); const body = document.createElement("tbody");
    artifacts.forEach((roadmap) => { const item = document.createElement("tr"); const title = document.createElement("th"); title.scope = "row"; const link = document.createElement("a"); link.href = `../${roadmap.slug}/`; link.textContent = localized(roadmap, "title"); title.append(link); item.append(title); years.forEach((year) => { const cell = document.createElement("td"); roadmap.lanes.flatMap((lane) => lane.milestones.map((milestone) => ({lane, milestone}))).filter(({milestone}) => milestone.year === year && milestone.comparison_priority === "key").forEach(({lane, milestone}) => { const entry = document.createElement("span"); entry.className = `comparison-milestone maturity-${milestone.maturity}`; entry.textContent = `${milestonePeriodLabel(milestone)} · ${localized(milestone, "label")} (${lane.owner})`; cell.append(entry); }); item.append(cell); }); body.append(item); }); table.append(head, body); root.append(table);
  }
  function renderCompareDependencies(artifacts) {
    const root = document.getElementById("compare-dependencies"); root.replaceChildren(); const allowed = new Set(artifacts.map((item) => item.roadmap_id)); const dependencies = artifacts.flatMap((roadmap) => roadmap.dependencies).filter((item) => allowed.has(item.upstream_roadmap_id) && allowed.has(item.downstream_roadmap_id)); dependencies.forEach((dependency) => { const item = document.createElement("li"); const route = document.createElement("strong"); route.textContent = `${roadmapName(dependency.upstream_roadmap_id)} → ${roadmapName(dependency.downstream_roadmap_id)}`; const text = document.createElement("span"); text.textContent = `${tr(relationshipKeys[dependency.relationship])}: ${localized(dependency, "statement")}`; item.append(route, text); root.append(item); });
  }
  function renderComparison() { const artifacts = data.roadmap_artifacts.filter((item) => selectedRoadmaps.has(item.export_id)); renderCompareControls(); renderCompareMetrics(artifacts); renderCompareTimeline(artifacts); renderCompareDependencies(artifacts); }

  function render() { applyStaticCopy(); if (page === "roadmap-index") renderRoadmapIndex(); if (page === "roadmap-detail") { renderRoadmapDetail(); renderRoadmapDialog(); renderRoadmapTermDialog(); } if (page === "roadmap-compare") renderComparison(); }
  document.querySelectorAll("[data-language]").forEach((button) => button.addEventListener("click", () => { language = button.dataset.language; rememberLanguage(language); render(); }));
  document.querySelectorAll("[data-roadmap-domain]").forEach((button) => button.addEventListener("click", () => { activeDomain = button.dataset.roadmapDomain; document.querySelectorAll("[data-roadmap-domain]").forEach((item) => item.classList.toggle("active", item === button)); renderRoadmapIndex(); }));
  document.getElementById("roadmap-search")?.addEventListener("input", renderRoadmapIndex);
  const dialog = document.getElementById("roadmap-dialog"); document.getElementById("roadmap-dialog-close")?.addEventListener("click", () => dialog.close()); dialog?.addEventListener("click", (event) => { if (event.target === event.currentTarget) event.currentTarget.close(); }); dialog?.addEventListener("close", () => { activeRoadmapMilestoneId = null; });
  const termDialog = document.getElementById("roadmap-term-dialog"); document.getElementById("roadmap-term-dialog-close")?.addEventListener("click", () => termDialog.close()); termDialog?.addEventListener("click", (event) => { if (event.target === event.currentTarget) event.currentTarget.close(); }); termDialog?.addEventListener("close", () => { activeTermId = null; });
  render();
})();
