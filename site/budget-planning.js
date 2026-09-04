(() => {
  "use strict";
  const data = window.OPENFS_PUBLIC_DATA;
  const copy = {
    ja: {budget: "予算上限", custom: "任意の予算（億円）", year: "導入年", allocation: "仮配分", estimate: "推定費用", unknown: "未算出", quantity: "数量・容量", component: "構成要素", tco: "5年間TCO", provisional: "仮配分案・実現可能性は未確認", contract: "契約額", award: "落札額", "program-budget": "事業予算", "planned-price": "予定価格", date: "契約日", unallocated: "内訳未配賦", sources: "公開資料・仕様書の取得状況", gaps: "未確認事項", next: "次の調査", "public-read": "公開資料を確認", "not-obtained": "未取得", expired: "交付期限終了", "registration-required": "登録が必要", "confidentiality-required": "秘密保持条件あり・未取得", tender: "入札公告", "final-specification": "最終仕様書", "draft-specification": "仕様書案", correction: "訂正資料", "contract-result": "契約結果", "deployed-configuration": "公開構成", "including-tax": "税込", "excluding-tax": "税抜", notKnown: "未確認", monthly: "月額", total: "総額", initial: "初期整備予算", shares: "配分率", notice: "配分額は見積価格ではありません。機器単価・施設条件・運用費の検証が済むまで、数量とTCOを確定しません。", publication: "根拠と交付条件", checkDate: "資料確認日", independence: "暫定・独立したAIモデルによる合意判定は未完了", topology: "構成図へ", tcoEvidence: "5年間TCOの証拠範囲", procurementCase: "調達事例", "observed-contract-scope": "契約範囲", "reported-unitemized": "内訳未分解", tcoUnknown: "未確認", tcoBasis: "5年間費用の判定"},
    en: {budget: "Budget ceiling", custom: "Custom budget (JPY 100M)", year: "Deployment year", allocation: "Allocation assumption", estimate: "Estimated cost", unknown: "Not calculated", quantity: "Quantity / capacity", component: "Component", tco: "Five-year TCO", provisional: "Allocation proposal; feasibility unverified", contract: "Contract value", award: "Award value", "program-budget": "Program budget", "planned-price": "Planned price", date: "Contract date", unallocated: "Unallocated breakdown", sources: "Public documents and specification access", gaps: "Coverage Gaps", next: "Next research action", "public-read": "Public document checked", "not-obtained": "Not obtained", expired: "Distribution ended", "registration-required": "Registration required", "confidentiality-required": "Confidentiality required; not obtained", tender: "Tender notice", "final-specification": "Final specification", "draft-specification": "Draft specification", correction: "Correction", "contract-result": "Contract result", "deployed-configuration": "Public configuration", "including-tax": "Tax included", "excluding-tax": "Tax excluded", notKnown: "Unknown", monthly: "Monthly", total: "Total", initial: "Initial funding", shares: "Share", notice: "Allocations are not price estimates. Quantities and TCO stay uncomputed until component pricing, facility constraints, and recurring costs are validated.", publication: "Evidence and access conditions", checkDate: "Source checked", independence: "Provisional; Consensus review by independent models incomplete", topology: "Open topology", tcoEvidence: "Five-year TCO evidence scope", procurementCase: "Procurement case", "observed-contract-scope": "Scoped contract", "reported-unitemized": "Unitemized", tcoUnknown: "Unknown", tcoBasis: "Five-year cost assessment"}
  };
  function context() { return data; }
  function el(tag, text, className) { const node = document.createElement(tag); if (text !== undefined) node.textContent = text; if (className) node.className = className; return node; }
  function money(value, language) {
    if (value == null) return copy[language].unknown;
    return language === "ja" ? `${value.toLocaleString("ja-JP", {maximumFractionDigits: 4})}億円` : `JPY ${(value / 10).toLocaleString("en-US", {maximumFractionDigits: 5})}B`;
  }
  function allocation(config, scenarioId, budget) {
    if (!Number.isFinite(budget) || budget <= 0 || budget > 100000) throw new Error("Invalid budget");
    const profile = config.profiles.find((p) => p.scenario_id === scenarioId);
    if (!profile) throw new Error("Unknown planning profile");
    return config.components.map((item) => ({...item, share: profile.shares_percent[item.id], amount: budget * profile.shares_percent[item.id] / 100}));
  }
  function controls(root, language, onChange) {
    const config = context().budget_planning; const t = copy[language];
    const params = new URLSearchParams(location.search);
    let budget = Number(params.get("budget")) || config.default_budget_oku_jpy;
    let year = Number(params.get("year")) || config.default_deployment_year;
    if (!Number.isFinite(budget) || budget <= 0 || budget > 100000) budget = config.default_budget_oku_jpy;
    if (!config.deployment_years.includes(year)) year = config.default_deployment_year;
    root.replaceChildren(); root.className = "budget-controls";
    const levels = el("div", undefined, "segmented budget-levels"); levels.setAttribute("role", "group"); levels.setAttribute("aria-label", t.budget);
    const customLabel = el("label", t.custom); const input = el("input"); input.type = "number"; input.min = "0.01"; input.max = "100000"; input.step = "any"; input.value = budget; customLabel.append(input);
    const yearLabel = el("label", t.year); const select = el("select");
    config.deployment_years.forEach((value) => { const option = el("option", String(value)); option.value = value; select.append(option); }); select.value = year; yearLabel.append(select);
    function update() {
      input.value = budget;
      levels.querySelectorAll("button").forEach((button) => { const selected = Number(button.dataset.budget) === budget; button.classList.toggle("active", selected); button.setAttribute("aria-pressed", String(selected)); });
      const url = new URL(location.href); url.searchParams.set("budget", budget); url.searchParams.set("year", year); url.searchParams.set("lang", language); history.replaceState(null, "", url);
      onChange({budget, year});
    }
    config.budget_ceilings_oku_jpy.forEach((value) => { const button = el("button", money(value, language)); button.type = "button"; button.dataset.budget = value; button.addEventListener("click", () => { budget = value; update(); }); levels.append(button); });
    input.addEventListener("change", () => { const value = Number(input.value); if (!input.checkValidity() || !Number.isFinite(value) || value <= 0) { input.reportValidity(); input.value = budget; return; } budget = value; update(); });
    select.addEventListener("change", () => { year = Number(select.value); update(); });
    root.append(levels, customLabel, yearLabel); update();
  }
  function renderAllocations(root, scenarios, state, language, rootPrefix) {
    const config = context().budget_planning; const t = copy[language]; root.replaceChildren();
    const heading = el("p", `${state.year} · ${t.initial}: ${money(state.budget, language)} · ${t.provisional}`, "budget-status");
    const scope = el("p", config[`scope_${language}`]);
    const tableWrap = el("div", undefined, "table-wrap"); const table = el("table", undefined, "budget-comparison-table");
    const head = el("thead"); const row = el("tr"); row.append(el("th", t.component));
    scenarios.forEach((scenario) => { const cell = el("th"); const link = el("a", scenario[`title_${language}`]); link.href = `${rootPrefix}${scenario.path}?budget=${state.budget}&year=${state.year}&lang=${language}`; cell.append(link); row.append(cell); }); head.append(row);
    const body = el("tbody"); const plans = scenarios.map((s) => allocation(config, s.scenario_id, state.budget));
    config.components.forEach((component, index) => { const line = el("tr"); line.append(el("th", component[`label_${language}`])); plans.forEach((plan) => line.append(el("td", `${money(plan[index].amount, language)} (${plan[index].share}%)`))); body.append(line); });
    for (const title of [t.estimate, t.quantity, t.tco]) { const line = el("tr"); line.append(el("th", title)); scenarios.forEach(() => line.append(el("td", t.unknown))); body.append(line); }
    const caption = el("caption", t.allocation); table.append(caption, head, body); tableWrap.append(table);
    root.append(heading, scope, tableWrap, el("p", t.notice, "budget-caveat"), el("p", config[`caveat_${language}`], "budget-caveat"));
  }
  function sourceLink(source) {
    const link = el("a", source.title); link.href = source.url; link.target = "_blank"; link.rel = "noopener noreferrer";
    return link;
  }
  function renderCapacities(section, observations, sources, language) {
    if (!observations?.length) return;
    const labels = language === "ja"
      ? {title: "ストレージ容量の定義と対象範囲", scope: "対象", value: "公表値", basis: "容量の定義", note: "解釈上の注意", source: "出典", physical: "物理容量", effective: "実効容量", allocation: "提供枠", unspecified: "定義未記載", planned: "計画構成", operating: "稼働構成"}
      : {title: "Storage capacity: definitions and scope", scope: "Scope", value: "Published value", basis: "Capacity basis", note: "Interpretation", source: "Source", physical: "Physical", effective: "Effective", allocation: "Allocation", unspecified: "Not specified", planned: "Planned configuration", operating: "Operating configuration"};
    const wrap = el("div", undefined, "table-wrap"); const table = el("table", undefined, "procurement-capacity-table");
    const head = el("thead"); const row = el("tr");
    [labels.scope, labels.value, labels.basis, labels.note, labels.source].forEach((label) => row.append(el("th", label)));
    head.append(row); const body = el("tbody");
    observations.forEach((observation) => {
      const line = el("tr"); line.id = observation.observation_id;
      const scope = el("th", observation[`scope_${language}`]); scope.scope = "row";
      const value = el("td", `${observation.value} ${observation.unit}`);
      value.append(el("small", labels[observation.configuration_status]));
      const refs = el("td"); observation.source_refs.forEach((ref) => refs.append(sourceLink(sources.get(ref))));
      line.append(scope, value, el("td", labels[observation.capacity_basis]), el("td", observation[`caveat_${language}`]), refs); body.append(line);
    });
    table.append(el("caption", labels.title), head, body); wrap.append(table); section.append(wrap);
  }
  function renderRegister(root, language, rootPrefix = "../") {
    const register = context().procurement_register; const t = copy[language]; root.replaceChildren();
    const sources = new Map(register.sources.map((s) => [s.source_id, s]));
    root.append(el("p", register[`caveat_${language}`]), el("p", `${t.independence} · ${register.as_of}`, "budget-status"));
    root.append(el("h4", t.tcoEvidence), el("p", register[`five_year_tco_method_${language}`]));
    const tcoWrap = el("div", undefined, "table-wrap"); const tcoTable = el("table", undefined, "tco-evidence-matrix");
    const tcoHead = el("thead"); const tcoHeadRow = el("tr"); tcoHeadRow.append(el("th", t.procurementCase));
    register.tco_scope_catalog.forEach((scope) => { const cell = el("th", scope[`label_${language}`]); cell.title = scope[`definition_${language}`]; tcoHeadRow.append(cell); });
    tcoHead.append(tcoHeadRow); const tcoBody = el("tbody");
    register.cases.forEach((item) => { const row = el("tr"); const name = el("th", item[`title_${language}`]); name.scope = "row"; row.append(name); item.five_year_cost_assessment.scope_coverage.forEach((entry) => { const status = entry.evidence_status === "unknown" ? t.tcoUnknown : t[entry.evidence_status]; const cell = el("td", status); cell.className = `tco-scope-${entry.evidence_status}`; row.append(cell); }); tcoBody.append(row); });
    tcoTable.append(tcoHead, tcoBody); tcoWrap.append(tcoTable); root.append(tcoWrap);
    register.cases.forEach((item) => {
      const section = el("details", undefined, "procurement-case"); section.id = `procurement-${item.case_id}`;
      const heading = el("summary", item[`title_${language}`]); section.append(heading);
      const amount = item.amount; const values = el("dl", undefined, "procurement-facts");
      [[amount ? t[amount.kind] : t.contract, amount ? `${money(amount.value_jpy / 1e8, language)} · ${t[amount.tax_basis] || t.notKnown} · ${t[amount.payment_basis] || t.notKnown}` : t.notKnown],
       [item.contract_date ? t.date : (language === "ja" ? "落札日" : "Award date"), item.contract_date || item.award_date || t.notKnown], [t.unallocated, money(item.breakdown.unallocated_jpy === null ? null : item.breakdown.unallocated_jpy / 1e8, language)]]
        .forEach(([label, value]) => { const group = el("div"); group.append(el("dt", label), el("dd", value)); values.append(group); });
      section.append(values, el("p", item[`scope_${language}`])); const documents = el("ul");
      section.append(el("h4", t.tcoBasis), el("p", item.five_year_cost_assessment[`basis_${language}`]));
      if (item.contract_window) {
        const period = item.contract_window;
        const label = language === "ja" ? "公告・契約に記載された期間" : "Period specified in the tender / contract";
        section.append(el("p", `${label}: ${period.start} – ${period.end}`));
      }
      if (item.reported_period_total) {
        const total = item.reported_period_total;
        const paragraph = el("p", language === "ja"
          ? `契約資料に記載された予定総額（${total.period_months}か月）: ${money(total.value_jpy / 1e8, language)}（${t[total.tax_basis] || t.notKnown}）。購入価格・TCOではありません。`
          : `Planned total reported in the contract disclosure (${total.period_months} months): ${money(total.value_jpy / 1e8, language)} (${t[total.tax_basis] || t.notKnown}). Not purchase price or TCO.`);
        total.source_refs.forEach((ref) => paragraph.append(" ", sourceLink(sources.get(ref)))); section.append(paragraph);
      } else if (item.lease_period_total) {
        const total = item.lease_period_total;
        section.append(el("p", language === "ja"
          ? `月額一定と仮定した${total.months}か月分の単純合計: ${money(total.value_jpy / 1e8, language)}（${t[total.tax_basis] || t.notKnown}）。購入価格・TCOではありません。`
          : `Arithmetic total for ${total.months} months at an unchanged monthly rate: ${money(total.value_jpy / 1e8, language)} (${t[total.tax_basis] || t.notKnown}). Not purchase price or TCO.`));
      }
      if (item.five_year_known_cost_floor) {
        const floor = item.five_year_known_cost_floor;
        section.append(el("p", language === "ja"
          ? `最初の60か月の契約上の既知費用下限: ${money(floor.value_jpy / 1e8, language)}（${t[floor.tax_basis] || t.notKnown}）。電力、施設共用費、人件費、契約変更、増設を含む5年間TCOではありません。`
          : `Contractual known-cost floor for the first 60 months: ${money(floor.value_jpy / 1e8, language)} (${t[floor.tax_basis] || t.notKnown}). This is not five-year TCO including electricity, shared facilities, staffing, amendments or expansion.`, "known-cost-floor"));
      }
      if (item.configuration_observation) {
        const observation = item.configuration_observation;
        const label = language === "ja" ? "公開構成との対応確認" : "Public configuration matching";
        section.append(el("h4", label), el("p", observation[`summary_${language}`]), el("p", observation[`match_caveat_${language}`]));
      }
      renderCapacities(section, item.storage_capacity_observations, sources, language);
      if (item.linked_systems?.length) {
        const links = el("p", language === "ja" ? "対応候補の仕様・運用日程: " : "Candidate system specifications and operational dates: ");
        item.linked_systems.forEach((system) => {
          const link = el("a", system[`name_${language}`]);
          link.href = `${rootPrefix}${system.inventory_path}?lang=${language}#${system.system_id}`;
          links.append(link, " ");
        });
        section.append(links);
      }
      section.append(el("h4", t.sources));
      item.documents.forEach((doc) => { const source = sources.get(doc.source_id); const line = el("li"); const link = sourceLink(source);
        line.append(el("strong", `${t[doc.kind]}: ${t[doc.access_status]}`), el("br"), link, el("small", `${t.checkDate}: ${source.checked_on} · ${source.locator}`)); documents.append(line); });
      section.append(documents, el("p", `${t.gaps}: ${item.gap_ids.join(" · ")}`, "mono-list")); root.append(section);
      if (location.hash.slice(1) === section.id) section.open = true;
    });
    root.append(el("h4", t.gaps)); register.coverage_gaps.forEach((gap) => { const item = el("p"); item.append(el("strong", `${gap.gap_id} (${gap.priority}) `), gap[`description_${language}`], el("br"), `${t.next}: ${gap[`next_action_${language}`]}`); root.append(item); });
  }
  window.OpenFSBudget = {controls, renderAllocations, renderRegister, allocation, money};
})();
