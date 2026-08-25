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
      libraryKicker: "公開ロードマップ索引", libraryTitle: "ロードマップ一覧", libraryLead: "ハードウェア、システムソフトウェア、アプリケーション、分野横断の見通しを検索し、専用ページで詳細を確認できます。",
      domainFilter: "分野フィルタ", all: "すべて", search: "検索", searchPlaceholder: "名称、分野", roadmapColumn: "ロードマップ", domainColumn: "分野", horizonColumn: "対象期間", researchAsOf: "調査基準日", researchStatus: "調査状態", coverageStatus: "調査範囲", consensusStatus: "Consensus", updatedColumn: "更新日時", noRoadmaps: "条件に一致するロードマップはありません。",
      memoryRoadmapKicker: "メモリ技術調査", roadmapFilter: "技術群フィルタ", memoryProducts: "メモリ製品", integration3d: "3D実装", systemEnablers: "システム技術",
      technologyColumn: "技術", vendorColumn: "ベンダー／対象", quarterUnknown: "Q未特定", undatedColumn: "時期未公表", roadmapTableNote: "項目を選択すると根拠と詳細を表示します。四半期を確認できない年次・半期情報は各年の「Q未特定」に置き、空欄は確認できる公開日程がないことを示します。",
      technologyNotesKicker: "技術別ノート", technologyNotesTitle: "現状とHPCI整備への示唆", currentState: "現在の状況", hpciImplications: "HPCI整備への示唆", roadmapCaveat: "公開時の注意事項",
      commercial: "製品・量産", sample: "サンプル", standard: "標準", target: "ベンダー目標", concept: "構想・研究", undated: "時期未公表", timingBasis: "時期の根拠", timingPrecision: "時期の精度", quarterPrecision: "四半期", halfYearPrecision: "半期", yearPrecision: "年", undatedPrecision: "未公表", milestoneDetail: "マイルストーン詳細", publicSources: "公開根拠資料",
      observed: "確認済み", standardRelease: "標準公開", vendorTarget: "ベンダー目標", noPublicDate: "公開時期なし", officialScanIncomplete: "一次情報の継続確認が必要",
      provisional: "暫定", accepted: "受理済み", coverageMet: "宣言した範囲を充足", consensusIncomplete: "未完了", profileIncomplete: "未確認項目あり",
      revisionKicker: "来歴", revisionTitle: "更新履歴と再現情報", artifactId: "Artifact ID", sourceCommit: "ソースコミット", closeDialog: "詳細を閉じる", footerDescription: "HPCI-CFSP 公開調査ビュー"
    },
    en: {
      languageControl: "Display language", tagline: "Public research catalog and planning outputs", publicOnly: "Public information only", siteUpdated: "Site updated",
      navOverview: "Overview", navCatalog: "Research catalog", navRoadmaps: "Roadmaps", navScenarios: "Roadmap scenarios", navReports: "Reports",
      libraryKicker: "PUBLISHED ROADMAP INDEX", libraryTitle: "Roadmap library", libraryLead: "Search hardware, system software, application, and cross-cutting outlooks, then open a dedicated page for details.",
      domainFilter: "Domain filter", all: "All", search: "Search", searchPlaceholder: "Title or domain", roadmapColumn: "Roadmap", domainColumn: "Domain", horizonColumn: "Horizon", researchAsOf: "Research as of", researchStatus: "Research status", coverageStatus: "Coverage", consensusStatus: "Consensus", updatedColumn: "Updated", noRoadmaps: "No roadmaps match the current filters.",
      memoryRoadmapKicker: "MEMORY TECHNOLOGY RESEARCH", roadmapFilter: "Technology group filter", memoryProducts: "Memory products", integration3d: "3D integration", systemEnablers: "System enablers",
      technologyColumn: "Technology", vendorColumn: "Vendor / scope", quarterUnknown: "Q?", undatedColumn: "Timing not public", roadmapTableNote: "Select a milestone to view its details and sources. Year- or half-year-only information remains under Q? for that year; blank cells mean no dated public milestone was confirmed.",
      technologyNotesKicker: "TECHNOLOGY NOTES", technologyNotesTitle: "Current state and implications for HPCI", currentState: "Current state", hpciImplications: "Implications for HPCI", roadmapCaveat: "Publication caveat",
      commercial: "product / volume", sample: "sample", standard: "standard", target: "vendor target", concept: "concept / research", undated: "timing not public", timingBasis: "Timing basis", timingPrecision: "Timing precision", quarterPrecision: "quarter", halfYearPrecision: "half-year", yearPrecision: "year", undatedPrecision: "not public", milestoneDetail: "Milestone detail", publicSources: "Public supporting sources",
      observed: "observed", standardRelease: "standard release", vendorTarget: "vendor target", noPublicDate: "no public date", officialScanIncomplete: "continued primary-source review required",
      provisional: "provisional", accepted: "accepted", coverageMet: "declared scope met", consensusIncomplete: "incomplete", profileIncomplete: "gaps remain",
      revisionKicker: "PROVENANCE", revisionTitle: "Revision and reproducibility", artifactId: "Artifact ID", sourceCommit: "Source commit", closeDialog: "Close details", footerDescription: "HPCI-CFSP public research view"
    }
  };

  const domainLabels = {
    ja: {hardware: "ハードウェア", "system-software": "システムソフトウェア", applications: "アプリケーション", "cross-cutting": "分野横断"},
    en: {hardware: "Hardware", "system-software": "System software", applications: "Applications", "cross-cutting": "Cross-cutting"}
  };
  const roadmapGroupKeys = {"memory-products": "memoryProducts", "3d-integration": "integration3d", "system-enablers": "systemEnablers"};
  const maturityKeys = {commercial: "commercial", sample: "sample", standard: "standard", target: "target", concept: "concept", undated: "undated"};
  const timingBasisKeys = {observed: "observed", "standard-release": "standardRelease", "vendor-target": "vendorTarget", "no-public-date": "noPublicDate"};
  const timingPrecisionKeys = {quarter: "quarterPrecision", "half-year": "halfYearPrecision", year: "yearPrecision", undated: "undatedPrecision"};
  const page = document.body.dataset.page;
  const rootPrefix = document.body.dataset.rootPrefix || "";
  let language = readLanguage();
  let activeDomain = "all";
  let activeRoadmapGroup = "all";
  let activeRoadmapMilestoneId = null;

  function readLanguage() {
    try {
      const stored = window.localStorage.getItem("openfs-language");
      if (stored === "ja" || stored === "en") return stored;
    } catch (_error) {
      // Storage is optional.
    }
    return "ja";
  }

  function rememberLanguage(value) {
    try {
      window.localStorage.setItem("openfs-language", value);
    } catch (_error) {
      // Storage is optional.
    }
  }

  function tr(key) { return copy[language][key] || key; }
  function localized(item, field) { return item[`${field}_${language}`] || item[field] || ""; }
  function setText(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
  }

  function formatJst(value) {
    const parts = new Intl.DateTimeFormat("en-CA", {
      timeZone: "Asia/Tokyo", year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23"
    }).formatToParts(new Date(value));
    const item = Object.fromEntries(parts.map((part) => [part.type, part.value]));
    return `${item.year}-${item.month}-${item.day} ${item.hour}:${item.minute}:${item.second} JST`;
  }

  function statusLabel(value) {
    const labels = {
      provisional: "provisional", accepted: "accepted", incomplete: "consensusIncomplete",
      "met-declared-scope": "coverageMet", "profile-coverage-incomplete": "profileIncomplete",
      "official-source-scan-incomplete": "officialScanIncomplete"
    };
    return tr(labels[value] || value);
  }

  function applyStaticCopy() {
    document.documentElement.lang = language;
    document.querySelectorAll("[data-i18n]").forEach((element) => { element.textContent = tr(element.dataset.i18n); });
    document.querySelectorAll("[data-i18n-placeholder]").forEach((element) => { element.placeholder = tr(element.dataset.i18nPlaceholder); });
    document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => { element.setAttribute("aria-label", tr(element.dataset.i18nAriaLabel)); });
    document.querySelectorAll("[data-language]").forEach((button) => {
      const selected = button.dataset.language === language;
      button.classList.toggle("active", selected);
      button.setAttribute("aria-pressed", String(selected));
    });
    const siteUpdated = document.getElementById("site-updated");
    siteUpdated.href = data.site.commit_url;
    siteUpdated.textContent = `${tr("siteUpdated")} ${formatJst(data.site.updated_at)} · ${data.site.commit_sha.slice(0, 7)}`;
    setText("license-status", `License: ${data.publication.license}`);
  }

  function renderRoadmapIndex() {
    const search = document.getElementById("roadmap-search");
    const query = search.value.trim().toLocaleLowerCase(language);
    const root = document.getElementById("roadmap-rows");
    root.replaceChildren();
    const filtered = data.roadmaps.filter((roadmap) => {
      const domainMatch = activeDomain === "all" || roadmap.domain === activeDomain;
      const text = [roadmap.title_ja, roadmap.title_en, roadmap.domain, domainLabels.ja[roadmap.domain], domainLabels.en[roadmap.domain]].join(" ").toLocaleLowerCase(language);
      return domainMatch && (!query || text.includes(query));
    });
    filtered.forEach((roadmap) => {
      const row = document.createElement("tr");
      const titleCell = document.createElement("td");
      const link = document.createElement("a");
      link.className = "roadmap-title-link";
      link.href = `${rootPrefix}${roadmap.path}?v=${encodeURIComponent(data.site.commit_sha)}`;
      link.textContent = localized(roadmap, "title");
      const summary = document.createElement("span");
      summary.className = "roadmap-row-note";
      summary.textContent = localized(roadmap, "summary");
      titleCell.append(link, summary);
      const domain = document.createElement("td");
      domain.textContent = domainLabels[language][roadmap.domain] || roadmap.domain;
      const horizon = document.createElement("td");
      horizon.textContent = `${roadmap.horizon.start_year}-${roadmap.horizon.end_year}`;
      const asOf = document.createElement("td");
      asOf.textContent = roadmap.as_of;
      const research = document.createElement("td");
      research.textContent = statusLabel(roadmap.research_status);
      const consensus = document.createElement("td");
      consensus.textContent = statusLabel(roadmap.consensus_status);
      const updated = document.createElement("td");
      const commit = document.createElement("a");
      commit.href = roadmap.source_commit_url;
      commit.target = "_blank";
      commit.rel = "noopener noreferrer";
      commit.textContent = formatJst(roadmap.updated_at);
      updated.appendChild(commit);
      row.append(titleCell, domain, horizon, asOf, research, consensus, updated);
      root.appendChild(row);
    });
    document.getElementById("roadmap-empty").hidden = filtered.length !== 0;
  }

  function currentRoadmap() {
    const roadmapId = document.body.dataset.roadmapId;
    const entry = data.roadmaps.find((item) => item.roadmap_id === roadmapId);
    if (!entry || entry.renderer !== "memory-technology") return null;
    if (data.memory_roadmap?.export_id !== roadmapId) return null;
    return data.memory_roadmap;
  }

  function roadmapSourceMap() {
    return new Map((currentRoadmap()?.sources || []).map((source) => [source.source_id, source]));
  }

  function renderRoadmapLegend() {
    const root = document.getElementById("roadmap-legend");
    root.replaceChildren();
    ["commercial", "sample", "standard", "target", "concept", "undated"].forEach((maturity) => {
      const item = document.createElement("span");
      item.className = `legend-item maturity-${maturity}`;
      item.textContent = tr(maturityKeys[maturity]);
      root.appendChild(item);
    });
  }

  function renderRoadmapTimeline() {
    const roadmap = currentRoadmap();
    const root = document.getElementById("memory-roadmap-timeline");
    root.replaceChildren();
    if (!roadmap) return;
    const technologies = roadmap.technologies.filter(
      (technology) => activeRoadmapGroup === "all" || technology.group === activeRoadmapGroup
    );
    const years = [];
    for (let year = roadmap.horizon.start_year; year <= roadmap.horizon.end_year; year += 1) years.push(year);
    const table = document.createElement("table");
    table.className = "roadmap-table";
    const colgroup = document.createElement("colgroup");
    ["roadmap-tech-column", "roadmap-vendor-column"].forEach((className) => {
      const column = document.createElement("col");
      column.className = className;
      colgroup.appendChild(column);
    });
    years.forEach(() => {
      ["Q1", "Q2", "Q3", "Q4", null].forEach(() => {
        const column = document.createElement("col");
        column.className = "roadmap-quarter-column";
        colgroup.appendChild(column);
      });
    });
    const undatedColumn = document.createElement("col");
    undatedColumn.className = "roadmap-undated-column";
    colgroup.appendChild(undatedColumn);
    const head = document.createElement("thead");
    const yearRow = document.createElement("tr");
    [tr("technologyColumn"), tr("vendorColumn")].forEach((label, index) => {
      const cell = document.createElement("th");
      cell.textContent = label;
      cell.rowSpan = 2;
      if (index === 0) cell.className = "roadmap-tech-column";
      if (index === 1) cell.className = "roadmap-vendor-column";
      yearRow.appendChild(cell);
    });
    years.forEach((year) => {
      const cell = document.createElement("th");
      cell.colSpan = 5;
      cell.className = "roadmap-year-heading";
      cell.textContent = year;
      yearRow.appendChild(cell);
    });
    const undatedHeading = document.createElement("th");
    undatedHeading.rowSpan = 2;
    undatedHeading.className = "roadmap-undated-heading";
    undatedHeading.textContent = tr("undatedColumn");
    yearRow.appendChild(undatedHeading);
    const quarterRow = document.createElement("tr");
    years.forEach(() => {
      ["Q1", "Q2", "Q3", "Q4", tr("quarterUnknown")].forEach((label) => {
        const cell = document.createElement("th");
        cell.className = "roadmap-quarter-heading";
        cell.textContent = label;
        quarterRow.appendChild(cell);
      });
    });
    head.append(yearRow, quarterRow);
    const body = document.createElement("tbody");
    technologies.forEach((technology) => {
      const lanes = roadmap.lanes.filter((lane) => lane.technology_id === technology.technology_id);
      lanes.forEach((lane, laneIndex) => {
        const row = document.createElement("tr");
        if (laneIndex === 0) {
          const technologyCell = document.createElement("th");
          technologyCell.scope = "rowgroup";
          technologyCell.rowSpan = lanes.length;
          technologyCell.className = "roadmap-tech-column roadmap-technology-cell";
          const technologyName = document.createElement("strong");
          technologyName.textContent = localized(technology, "name");
          const technologyGroup = document.createElement("span");
          technologyGroup.textContent = tr(roadmapGroupKeys[technology.group]);
          technologyCell.append(technologyName, technologyGroup);
          row.appendChild(technologyCell);
        }
        const vendorCell = document.createElement("th");
        vendorCell.scope = "row";
        vendorCell.className = "roadmap-vendor-column roadmap-vendor-cell";
        const vendor = document.createElement("strong");
        vendor.textContent = lane.vendor;
        const scope = document.createElement("span");
        scope.textContent = localized(lane, "scope");
        vendorCell.append(vendor, scope);
        row.appendChild(vendorCell);
        const timelineSlots = years.flatMap((year) => ["Q1", "Q2", "Q3", "Q4", null].map((quarter) => ({year, quarter})));
        timelineSlots.push({year: null, quarter: null});
        timelineSlots.forEach((slot) => {
          const cell = document.createElement("td");
          lane.milestones.filter((milestone) => milestone.year === slot.year && milestone.quarter === slot.quarter).forEach((milestone) => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = `roadmap-milestone maturity-${milestone.maturity}`;
            button.textContent = localized(milestone, "label");
            button.setAttribute("aria-haspopup", "dialog");
            button.addEventListener("click", () => openRoadmapMilestone(milestone.milestone_id));
            cell.appendChild(button);
          });
          row.appendChild(cell);
        });
        body.appendChild(row);
      });
    });
    table.append(colgroup, head, body);
    root.appendChild(table);
  }

  function appendSourceList(root, sourceIds) {
    const sources = roadmapSourceMap();
    sourceIds.forEach((sourceId) => {
      const source = sources.get(sourceId);
      if (!source) return;
      const item = document.createElement("li");
      const link = document.createElement("a");
      link.href = source.url;
      link.target = "_blank";
      link.rel = "noopener noreferrer";
      link.textContent = source.title;
      const publisher = document.createElement("span");
      publisher.textContent = source.publisher;
      item.append(link, publisher);
      root.appendChild(item);
    });
  }

  function renderMemoryTechnologyDetails() {
    const roadmap = currentRoadmap();
    const root = document.getElementById("memory-technology-details");
    root.replaceChildren();
    roadmap.technologies
      .filter((technology) => activeRoadmapGroup === "all" || technology.group === activeRoadmapGroup)
      .forEach((technology) => {
        const details = document.createElement("details");
        details.className = "memory-technology-note";
        const toggle = document.createElement("summary");
        const name = document.createElement("strong");
        name.textContent = localized(technology, "name");
        const summary = document.createElement("span");
        summary.textContent = localized(technology, "summary");
        toggle.append(name, summary);
        const body = document.createElement("div");
        body.className = "memory-technology-note-body";
        const stateTitle = document.createElement("h4");
        stateTitle.textContent = tr("currentState");
        const state = document.createElement("p");
        state.textContent = localized(technology, "current_state");
        const implicationsTitle = document.createElement("h4");
        implicationsTitle.textContent = tr("hpciImplications");
        const implications = document.createElement("p");
        implications.textContent = localized(technology, "hpci_implications");
        const sourcesTitle = document.createElement("h4");
        sourcesTitle.textContent = tr("publicSources");
        const sources = document.createElement("ul");
        sources.className = "source-list memory-source-list";
        appendSourceList(sources, technology.source_ids);
        body.append(stateTitle, state, implicationsTitle, implications, sourcesTitle, sources);
        details.append(toggle, body);
        root.appendChild(details);
      });
  }

  function renderRoadmapDetail() {
    const roadmap = currentRoadmap();
    if (!roadmap) {
      document.querySelector("main").textContent = tr("noRoadmaps");
      return;
    }
    document.title = `${localized(roadmap, "title")} | OpenFS`;
    setText("roadmap-breadcrumb-title", localized(roadmap, "title"));
    setText("memory-roadmap-title", localized(roadmap, "title"));
    setText("memory-roadmap-summary", localized(roadmap, "summary"));
    setText("memory-roadmap-as-of", roadmap.as_of);
    setText("memory-roadmap-horizon", `${roadmap.horizon.start_year}-${roadmap.horizon.end_year}`);
    setText("memory-roadmap-research-status", statusLabel(roadmap.research_status));
    setText("memory-roadmap-coverage-status", statusLabel(roadmap.coverage_status));
    setText("memory-roadmap-consensus-status", statusLabel(roadmap.consensus_status));
    setText("memory-roadmap-caveat", localized(roadmap, "caveat"));
    const updated = document.getElementById("memory-roadmap-updated");
    updated.href = roadmap.source_commit_url;
    updated.textContent = formatJst(roadmap.updated_at);
    setText("roadmap-artifact-id", roadmap.export_id);
    const sourceCommit = document.getElementById("roadmap-source-commit");
    sourceCommit.href = roadmap.source_commit_url;
    sourceCommit.textContent = roadmap.source_commit;
    setText("roadmap-revision-updated", formatJst(roadmap.updated_at));
    const gaps = document.getElementById("memory-roadmap-gaps");
    gaps.replaceChildren();
    roadmap.coverage_gaps.forEach((gap) => {
      const item = document.createElement("li");
      item.textContent = localized(gap, "statement");
      gaps.appendChild(item);
    });
    document.querySelectorAll("[data-roadmap-group]").forEach((button) => {
      button.classList.toggle("active", button.dataset.roadmapGroup === activeRoadmapGroup);
    });
    renderRoadmapLegend();
    renderRoadmapTimeline();
    renderMemoryTechnologyDetails();
  }

  function findRoadmapMilestone(milestoneId) {
    const roadmap = currentRoadmap();
    for (const lane of roadmap.lanes) {
      const milestone = lane.milestones.find((item) => item.milestone_id === milestoneId);
      if (milestone) {
        const technology = roadmap.technologies.find((item) => item.technology_id === lane.technology_id);
        return {technology, lane, milestone};
      }
    }
    return null;
  }

  function appendMetaItem(root, label, value) {
    const item = document.createElement("div");
    const term = document.createElement("dt");
    term.textContent = label;
    const description = document.createElement("dd");
    description.textContent = value;
    item.append(term, description);
    root.appendChild(item);
  }

  function renderRoadmapDialog() {
    if (!activeRoadmapMilestoneId) return;
    const match = findRoadmapMilestone(activeRoadmapMilestoneId);
    if (!match) return;
    const {technology, lane, milestone} = match;
    setText("roadmap-dialog-id", milestone.milestone_id);
    setText("roadmap-dialog-title", localized(milestone, "label"));
    const milestonePeriod = milestone.year === null
      ? tr("undatedColumn")
      : milestone.quarter
        ? `${milestone.year} ${milestone.quarter}`
        : `${milestone.year} (${tr("quarterUnknown")})`;
    setText("roadmap-dialog-meta", `${localized(technology, "name")} / ${lane.vendor} / ${milestonePeriod}`);
    const root = document.getElementById("roadmap-dialog-content");
    root.replaceChildren();
    const section = document.createElement("section");
    section.className = "roadmap-milestone-detail";
    const status = document.createElement("span");
    status.className = `summary-status maturity-${milestone.maturity}`;
    status.textContent = tr(maturityKeys[milestone.maturity]);
    const title = document.createElement("h3");
    title.textContent = tr("milestoneDetail");
    const detail = document.createElement("p");
    detail.textContent = localized(milestone, "detail");
    const meta = document.createElement("dl");
    meta.className = "research-meta roadmap-dialog-meta-list";
    appendMetaItem(meta, tr("technologyColumn"), localized(technology, "name"));
    appendMetaItem(meta, tr("vendorColumn"), `${lane.vendor} / ${localized(lane, "scope")}`);
    appendMetaItem(meta, tr("timingBasis"), tr(timingBasisKeys[milestone.timing_basis]));
    appendMetaItem(meta, tr("timingPrecision"), tr(timingPrecisionKeys[milestone.timing_precision]));
    appendMetaItem(meta, tr("researchAsOf"), currentRoadmap().as_of);
    const sourcesTitle = document.createElement("h4");
    sourcesTitle.textContent = tr("publicSources");
    const sources = document.createElement("ul");
    sources.className = "source-list roadmap-dialog-source-list";
    appendSourceList(sources, milestone.source_ids);
    section.append(status, title, detail, meta, sourcesTitle, sources);
    root.appendChild(section);
  }

  function openRoadmapMilestone(milestoneId) {
    activeRoadmapMilestoneId = milestoneId;
    renderRoadmapDialog();
    const dialog = document.getElementById("roadmap-dialog");
    if (!dialog.open) dialog.showModal();
  }

  function render() {
    applyStaticCopy();
    if (page === "roadmap-index") renderRoadmapIndex();
    if (page === "roadmap-detail") {
      renderRoadmapDetail();
      renderRoadmapDialog();
    }
  }

  document.querySelectorAll("[data-language]").forEach((button) => {
    button.addEventListener("click", () => {
      language = button.dataset.language;
      rememberLanguage(language);
      render();
    });
  });
  document.querySelectorAll("[data-roadmap-domain]").forEach((button) => {
    button.addEventListener("click", () => {
      activeDomain = button.dataset.roadmapDomain;
      document.querySelectorAll("[data-roadmap-domain]").forEach((item) => item.classList.toggle("active", item === button));
      renderRoadmapIndex();
    });
  });
  document.querySelectorAll("[data-roadmap-group]").forEach((button) => {
    button.addEventListener("click", () => {
      activeRoadmapGroup = button.dataset.roadmapGroup;
      renderRoadmapDetail();
    });
  });
  document.getElementById("roadmap-search")?.addEventListener("input", renderRoadmapIndex);
  const dialog = document.getElementById("roadmap-dialog");
  document.getElementById("roadmap-dialog-close")?.addEventListener("click", () => dialog.close());
  dialog?.addEventListener("click", (event) => {
    if (event.target === event.currentTarget) event.currentTarget.close();
  });
  dialog?.addEventListener("close", () => { activeRoadmapMilestoneId = null; });
  render();
})();
