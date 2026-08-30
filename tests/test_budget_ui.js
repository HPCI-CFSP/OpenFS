const assert = require("node:assert/strict");
const {readFileSync} = require("node:fs");
const {test} = require("node:test");
const vm = require("node:vm");
const path = require("node:path");
const rootPath = path.join(__dirname, "..");
const read = (file) => JSON.parse(readFileSync(path.join(rootPath, file), "utf8"));
const code = readFileSync(path.join(rootPath, "site/budget-planning.js"), "utf8");

// Offline event tests; these do not claim browser layout coverage.
function fixture(query = "") {
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
  const data = {budget_planning: read("config/budget-planning.json"), procurement_register: register};
  const window = {OPENFS_PUBLIC_DATA: data};
  const location = new URL(`https://hpci-cfsp.github.io/OpenFS/scenarios/${query}`);
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

test("public register displays four cases with access restrictions and no raw HTML", () => {
  const f = fixture(); f.data.procurement_register.cases[0].title_en = "<script>not markup</script>";
  f.api.renderRegister(f.root, "en");
  assert.equal(f.root.querySelectorAll("details").length, 4);
  assert.equal(f.root.querySelectorAll("summary")[0].textContent, "<script>not markup</script>");
  assert.ok(f.walk(f.root).some((e) => e.textContent?.includes("Confidentiality required; not obtained")));
  assert.ok(f.root.querySelectorAll("a").every((a) => a.href.startsWith("https://") && a.rel === "noopener noreferrer"));
});
