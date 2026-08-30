(() => {
  "use strict";
  const data = window.OPENFS_PUBLIC_DATA;
  const copy = {
    ja: {budget: "予算上限", custom: "任意の予算（億円）", year: "導入年", allocation: "仮配分", estimate: "推定費用", unknown: "未算出", quantity: "数量・容量", component: "構成要素", tco: "5年間TCO", provisional: "仮配分案・実現可能性は未確認", contract: "契約額", award: "落札額", "program-budget": "事業予算", "planned-price": "予定価格", date: "契約日", unallocated: "内訳未配賦", sources: "公開資料・仕様書の取得状況", gaps: "未確認事項", next: "次の調査", "public-read": "公開資料を確認", "not-obtained": "未取得", expired: "交付期限終了", "registration-required": "登録が必要", "confidentiality-required": "秘密保持条件あり・未取得", tender: "入札公告", "final-specification": "最終仕様書", "draft-specification": "仕様書案", correction: "訂正資料", "contract-result": "契約結果", "deployed-configuration": "公開構成", "including-tax": "税込", "excluding-tax": "税抜", notKnown: "未確認", monthly: "月額", total: "総額", initial: "初期整備予算", shares: "配分率", notice: "配分額は見積価格ではありません。機器単価・施設条件・運用費の検証が済むまで、数量とTCOを確定しません。", publication: "根拠と交付条件", checkDate: "資料確認日", independence: "暫定・独立したAIモデルによる合意判定は未完了", topology: "構成図へ"},
    en: {budget: "Budget ceiling", custom: "Custom budget (JPY 100M)", year: "Deployment year", allocation: "Allocation assumption", estimate: "Estimated cost", unknown: "Not calculated", quantity: "Quantity / capacity", component: "Component", tco: "Five-year TCO", provisional: "Allocation proposal; feasibility unverified", contract: "Contract value", award: "Award value", "program-budget": "Program budget", "planned-price": "Planned price", date: "Contract date", unallocated: "Unallocated breakdown", sources: "Public documents and specification access", gaps: "Coverage Gaps", next: "Next research action", "public-read": "Public document checked", "not-obtained": "Not obtained", expired: "Distribution ended", "registration-required": "Registration required", "confidentiality-required": "Confidentiality required; not obtained", tender: "Tender notice", "final-specification": "Final specification", "draft-specification": "Draft specification", correction: "Correction", "contract-result": "Contract result", "deployed-configuration": "Public configuration", "including-tax": "Tax included", "excluding-tax": "Tax excluded", notKnown: "Unknown", monthly: "Monthly", total: "Total", initial: "Initial funding", shares: "Share", notice: "Allocations are not price estimates. Quantities and TCO stay uncomputed until component pricing, facility constraints, and recurring costs are validated.", publication: "Evidence and access conditions", checkDate: "Source checked", independence: "Provisional; Consensus review by independent models incomplete", topology: "Open topology"}
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
  function renderRegister(root, language) {
    const register = context().procurement_register; const t = copy[language]; root.replaceChildren();
    const sources = new Map(register.sources.map((s) => [s.source_id, s]));
    root.append(el("p", register[`caveat_${language}`]), el("p", `${t.independence} · ${register.as_of}`, "budget-status"));
    register.cases.forEach((item) => {
      const section = el("details", undefined, "procurement-case"); section.id = `procurement-${item.case_id}`;
      const heading = el("summary", item[`title_${language}`]); section.append(heading);
      const amount = item.amount; const values = el("dl", undefined, "procurement-facts");
      [[amount ? t[amount.kind] : t.contract, amount ? `${money(amount.value_jpy / 1e8, language)} · ${t[amount.tax_basis] || t.notKnown} · ${t[amount.payment_basis] || t.notKnown}` : t.notKnown],
       [t.date, item.contract_date || t.notKnown], [t.unallocated, money(item.breakdown.unallocated_jpy === null ? null : item.breakdown.unallocated_jpy / 1e8, language)]]
        .forEach(([label, value]) => { const group = el("div"); group.append(el("dt", label), el("dd", value)); values.append(group); });
      section.append(values, el("p", item[`scope_${language}`]), el("h4", t.sources)); const documents = el("ul");
      item.documents.forEach((doc) => { const source = sources.get(doc.source_id); const line = el("li"); const link = el("a", source.title); link.href = source.url; link.target = "_blank"; link.rel = "noopener noreferrer";
        line.append(el("strong", `${t[doc.kind]}: ${t[doc.access_status]}`), el("br"), link, el("small", `${t.checkDate}: ${source.checked_on} · ${source.locator}`)); documents.append(line); });
      section.append(documents, el("p", `${t.gaps}: ${item.gap_ids.join(" · ")}`, "mono-list")); root.append(section);
    });
    root.append(el("h4", t.gaps)); register.coverage_gaps.forEach((gap) => { const item = el("p"); item.append(el("strong", `${gap.gap_id} (${gap.priority}) `), gap[`description_${language}`], el("br"), `${t.next}: ${gap[`next_action_${language}`]}`); root.append(item); });
  }
  window.OpenFSBudget = {controls, renderAllocations, renderRegister, allocation, money};
})();
