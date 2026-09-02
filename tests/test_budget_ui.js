const assert = require("node:assert/strict");
const {readFileSync, existsSync} = require("node:fs");
const {test} = require("node:test");
const vm = require("node:vm");
const path = require("node:path");
const rootPath = path.join(__dirname, "..");
const read = (file) => JSON.parse(readFileSync(path.join(rootPath, file), "utf8"));
const code = readFileSync(path.join(rootPath, "site/budget-planning.js"), "utf8");
const publicSeed = {window: {}};
if (process.env.OPENFS_TEST_PUBLIC_DATA) vm.runInNewContext(readFileSync(process.env.OPENFS_TEST_PUBLIC_DATA, "utf8"), publicSeed);

// Offline event tests; these do not claim browser layout coverage.
function fixture(query = "", route = "scenarios/") {
  const walk = (element) => typeof element === "string" ? [] : [element, ...element.children.flatMap(walk)];
  class Element {
    constructor(tag) {
      this.tagName = tag; this.children = []; this.dataset = {}; this.attributes = {}; this.events = {};
      this.classList = {toggle: (name, active) => {
        const classes = new Set((this.className || "").split(" ").filter(Boolean));
        if (active) classes.add(name); else classes.delete(name);
        this.className = [...classes].join(" ");
      }};
    }
    append(...items) { this.children.push(...items); }
    replaceChildren(...items) { this.children = items; }
    setAttribute(key, value) { this.attributes[key] = String(value); }
    addEventListener(type, handler) { this.events[type] = handler; }
    dispatch(type) { this.events[type]({target: this}); }
    querySelectorAll(tag) { return walk(this).filter((e) => e.tagName === tag); }
    checkValidity() { const n = Number(this.value); return Number.isFinite(n) && n >= Number(this.min) && n <= Number(this.max); }
    reportValidity() { this.invalidReported = true; }
  }
  const register = read("knowledge/public/procurement-cost-register.json");
  for (const item of register.cases) item.breakdown = {unallocated_jpy: item.amount ? item.amount.value_jpy : null};
  const systems = read("knowledge/public/hpci-system-inventory.json").systems;
  const blueprint = read("knowledge/public/roadmaps/reference-blueprint-centers.json");
  for (const item of register.cases) item.linked_systems = (item.linked_system_ids || []).map((id) => ({...systems.find((s) => s.system_id === id), inventory_path: `roadmaps/${blueprint.slug}/`}));
  const data = publicSeed.window.OPENFS_PUBLIC_DATA ? structuredClone(publicSeed.window.OPENFS_PUBLIC_DATA) : {budget_planning: read("config/budget-planning.json"), procurement_register: register};
  const window = {OPENFS_PUBLIC_DATA: data};
  const location = new URL(`https://hpci-cfsp.github.io/OpenFS/${route}${query}`);
  const history = {replaceState(_state, _title, url) { location.href = String(url); }};
  vm.runInNewContext(code, {window, location, history, URL, URLSearchParams,
    document: {createElement: (tag) => new Element(tag)}});
  return {api: window.OpenFSBudget, data, location, root: new Element("div"), walk};
}

test("five budget buttons, custom amount, year, and language preserve state", () => {
  const f = fixture("?budget=27.5&year=2031"); let state;
  f.api.controls(f.root, "ja", (s) => { state = s; });
  assert.equal(state.budget, 27.5); assert.equal(state.year, 2031);
  let buttons = f.root.querySelectorAll("button");
  assert.equal(buttons.length, 5); buttons[1].dispatch("click");
  assert.equal(state.budget, 30); assert.equal(buttons[1].attributes["aria-pressed"], "true");
  const input = f.root.querySelectorAll("input")[0]; input.value = "46.25"; input.dispatch("change");
  assert.equal(state.budget, 46.25);
  input.value = "-2"; input.dispatch("change");
  assert.equal(state.budget, 46.25); assert.equal(input.invalidReported, true);
  const year = f.root.querySelectorAll("select")[0]; year.value = "2032"; year.dispatch("change");
  assert.equal(state.year, 2032);
  f.api.controls(f.root, "en", (s) => { state = s; });
  assert.equal(state.budget, 46.25); assert.equal(state.year, 2032);
  assert.equal(f.root.querySelectorAll("button").length, 5);
  assert.equal(f.location.searchParams.get("budget"), "46.25");
  assert.equal(f.location.searchParams.get("lang"), "en");
});

test("malformed URL parameters cannot generate negative or nonfinite allocations", () => {
  for (const query of ["?budget=NaN&year=unknown", "?budget=-10&year=2100", "?budget=Infinity&year=2000"]) {
    const f = fixture(query); let state;
    f.api.controls(f.root, "en", (s) => { state = s; });
    assert.equal(state.budget, f.data.budget_planning.default_budget_oku_jpy);
    assert.equal(state.year, f.data.budget_planning.default_deployment_year);
  }
});

test("all profiles and budget levels sum to the ceiling and preserve currency units", () => {
  const f = fixture(); const config = f.data.budget_planning;
  for (const profile of config.profiles) for (const ceiling of [...config.budget_ceilings_oku_jpy, 27.5]) {
    const rows = f.api.allocation(config, profile.scenario_id, ceiling);
    assert.ok(Math.abs(rows.reduce((sum, r) => sum + r.amount, 0) - ceiling) < 1e-8);
  }
  assert.equal(f.api.money(10, "ja"), "10億円");
  assert.equal(f.api.money(10, "en"), "JPY 1B");
  assert.throws(() => f.api.allocation(config, config.profiles[0].scenario_id, NaN));
});

test("comparison links retain budget/year and distinguish allocations from estimates", () => {
  const f = fixture(); const scenarios = read("roadmaps/scenarios/accepted/hpci-p0-scenarios.json").scenarios;
  scenarios.forEach((s) => { s.path = `scenarios/${s.scenario_id}/`; });
  for (const language of ["ja", "en"]) {
    f.api.renderAllocations(f.root, scenarios, {budget: 30, year: 2031}, language, "../");
    const nodes = f.walk(f.root);
    const links = nodes.filter((e) => e.tagName === "a");
    assert.equal(links.length, 3);
    assert.ok(links.every((e) => e.href.endsWith(`?budget=30&year=2031&lang=${language}`)));
    const unknown = language === "ja" ? "未算出" : "Not calculated";
    assert.equal(nodes.filter((e) => e.textContent === unknown).length, 9);
    assert.equal(f.root.querySelectorAll("tbody")[0].children.length, 12);
  }
});

test("public register displays all cases with access restrictions and no raw HTML", () => {
  const f = fixture(); f.data.procurement_register.cases[0].title_en = "<script>not markup</script>";
  f.api.renderRegister(f.root, "en");
  assert.equal(f.root.querySelectorAll("details").length, f.data.procurement_register.cases.length);
  assert.equal(f.root.querySelectorAll("summary")[0].textContent, "<script>not markup</script>");
  assert.ok(f.walk(f.root).some((e) => e.textContent?.includes("Confidentiality required; not obtained")));
  assert.ok(f.root.querySelectorAll("a").filter((a) => a.href.startsWith("https://")).every((a) => a.rel === "noopener noreferrer"));
  assert.equal(f.root.querySelectorAll("a").filter((a) => a.href.startsWith("../roadmaps/")).length, 3);
});

test("reported total, differently defined capacities, and system links remain distinguishable", () => {
  for (const language of ["ja", "en"]) {
    const f = fixture(`#procurement-PROC-TSUKUBA-UNIFIED-MEMORY-2025`);
    f.api.renderRegister(f.root, language);
    const details = f.root.querySelectorAll("details");
    assert.equal(details.filter((d) => d.open).length, 1);
    assert.equal(details.find((d) => d.open).id, "procurement-PROC-TSUKUBA-UNIFIED-MEMORY-2025");
    const tables = f.root.querySelectorAll("table");
    assert.equal(tables.length, 4);
    assert.ok(f.walk(f.root).some((e) => e.textContent === (language === "ja" ? "実効容量" : "Effective")));
    assert.ok(f.walk(f.root).some((e) => e.textContent?.includes(language === "ja" ? "契約資料に記載された予定総額" : "Planned total reported in the contract disclosure")));
    const systemLinks = f.root.querySelectorAll("a").filter((a) => a.href.includes("#HPCI-SYS-"));
    assert.equal(systemLinks.length, 3);
    assert.ok(systemLinks.every((a) => a.href.includes(`?lang=${language}#HPCI-SYS-`)));
  }
});

test("lease period and award date remain distinct from commissioning and purchase cost", () => {
  const f = fixture();
  const caseData = f.data.procurement_register.cases.find((item) => item.case_id === "PROC-TSUKUBA-UNIFIED-MEMORY-2025");
  caseData.lease_period_total = {months: 72, value_jpy: 855360000, tax_basis: "including-tax"};
  for (const language of ["ja", "en"]) {
    f.api.renderRegister(f.root, language);
    const section = f.root.querySelectorAll("details").find((e) => e.id === `procurement-${caseData.case_id}`);
    const text = f.walk(section).map((e) => e.textContent || "").join(" ");
    assert.ok(text.includes("2026-03-01"));
    assert.ok(text.includes("2032-02-29"));
    assert.ok(text.includes(caseData.award_date));
    assert.ok(text.includes(language === "ja" ? "購入価格・TCOではありません" : "Not purchase price or TCO"));
    assert.ok(text.includes(language === "ja" ? "月額" : "Monthly"));
  }
});

test("five-year contractual floor remains distinct from complete TCO", {skip: !process.env.OPENFS_TEST_PUBLIC_DATA}, () => {
  for (const language of ["ja", "en"]) {
    const f = fixture("?lang=" + language);
    f.api.renderRegister(f.root, language);
    const text = f.walk(f.root).map((e) => e.textContent || "").join(" ");
    assert.ok(text.includes(language === "ja" ? "最初の60か月の契約上の既知費用下限" : "Contractual known-cost floor for the first 60 months"));
    assert.ok(text.includes(language === "ja" ? "5年間TCOではありません" : "This is not five-year TCO"));
    assert.ok(text.includes(language === "ja" ? "5年間TCOの証拠範囲" : "Five-year TCO evidence scope"));
    assert.ok(text.includes(language === "ja" ? "内訳未分解" : "Unitemized"));
  }
});

test("inventory links resolve to built pages from portfolio and every nested plan", {skip: !process.env.OPENFS_TEST_PUBLIC_DATA}, () => {
  const site = path.dirname(path.dirname(process.env.OPENFS_TEST_PUBLIC_DATA));
  const routes = ["scenarios/", ...publicSeed.window.OPENFS_PUBLIC_DATA.scenarios.map((s) => s.path)];
  for (const route of routes) for (const language of ["ja", "en"]) {
    const page = readFileSync(path.join(site, route, "index.html"), "utf8");
    const prefix = page.match(/data-root-prefix="([^"]*)"/)[1];
    const f = fixture(`?lang=${language}`, route);
    f.api.renderRegister(f.root, language, prefix);
    for (const link of f.root.querySelectorAll("a").filter((a) => a.href.includes("#HPCI-SYS-"))) {
      const url = new URL(link.href, f.location);
      assert.equal(url.searchParams.get("lang"), language);
      assert.ok(url.pathname.startsWith("/OpenFS/roadmaps/"));
      assert.ok(existsSync(path.join(site, url.pathname.slice("/OpenFS/".length), "index.html")), url.href);
      assert.ok(f.data.hpci_system_inventory.systems.some((s) => `#${s.system_id}` === url.hash));
    }
  }
});
