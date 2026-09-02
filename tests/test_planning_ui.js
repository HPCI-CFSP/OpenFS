const assert = require("node:assert/strict");
const {readFileSync, existsSync} = require("node:fs");
const {test} = require("node:test");
const path = require("node:path");
const vm = require("node:vm");
const site = path.dirname(path.dirname(process.env.OPENFS_TEST_PUBLIC_DATA));
const seed = {window: {}};
vm.runInNewContext(readFileSync(process.env.OPENFS_TEST_PUBLIC_DATA, "utf8"), seed);
const data = JSON.parse(JSON.stringify(seed.window.OPENFS_PUBLIC_DATA));

// Run both production scripts together against IDs and route data from built pages.
// This checks DOM output and navigation, not browser layout or rendered pixels.
function fixture(route, language) {
  const html = readFileSync(path.join(site, route, "index.html"), "utf8");
  const walk = (node) => typeof node === "string" ? [] : [node, ...node.children.flatMap(walk)];
  class Element {
    constructor(tag) {
      this.tagName = tag; this.children = []; this.dataset = {}; this.attributes = {};
      this.events = {}; this.text = ""; this.style = {setProperty() {}};
      this.classList = {toggle() {}};
    }
    set textContent(value) { this.text = String(value); this.children = []; }
    get textContent() { return this.text + this.children.map((c) => typeof c === "string" ? c : c.textContent).join(" "); }
    get childElementCount() { return this.children.filter((c) => typeof c !== "string").length; }
    append(...nodes) { this.children.push(...nodes); }
    replaceChildren(...nodes) { this.text = ""; this.children = nodes; }
    setAttribute(key, value) { this.attributes[key] = String(value); }
    addEventListener(type, callback) { (this.events[type] ||= []).push(callback); }
    dispatch(type) { (this.events[type] || []).forEach((fn) => fn({target: this})); }
    checkValidity() { return true; }
    querySelectorAll(tag) { return walk(this).filter((node) => node !== this && node.tagName === tag); }
  }
  const ids = new Map([...html.matchAll(/id="([^"]+)"/g)].map((match) => {
    const node = new Element("div"); node.id = match[1]; return [node.id, node];
  }));
  const buttons = ["ja", "en"].map((lang) => { const node = new Element("button"); node.dataset.language = lang; return node; });
  const elements = () => [...ids.values()].flatMap(walk);
  const body = new Element("body");
  body.dataset = Object.fromEntries([...html.match(/<body[^>]+>/)[0].matchAll(/data-([a-z-]+)="([^"]*)"/g)]
    .map((match) => [match[1].replace(/-([a-z])/g, (_, c) => c.toUpperCase()), match[2]]));
  const document = {body, documentElement: {}, getElementById: (id) => ids.get(id) || elements().find((node) => node.id === id),
    createElement: (tag) => new Element(tag),
    querySelectorAll: (selector) => selector === "[data-language]" ? buttons : selector === "a[href]" ? elements().filter((node) => node.tagName === "a" && node.href) : []};
  const location = new URL(`https://hpci-cfsp.github.io/OpenFS/${route}?lang=${language}&budget=30&year=2031`);
  const history = {replaceState(_a, _b, url) { location.href = String(url); }};
  const window = {OPENFS_PUBLIC_DATA: structuredClone(data), location, history,
    localStorage: {getItem: () => null, setItem() {}}, OpenFSFeedback: {mount() {}}};
  const context = vm.createContext({window, document, location, history, URL, URLSearchParams, Intl});
  for (const script of ["budget-planning.js", "planning.js"]) vm.runInContext(readFileSync(path.join(site, script), "utf8"), context);
  return {elements, location, buttons, document};
}

test("portfolio and all plan pages pass their actual root prefix to the budget register", () => {
  for (const route of ["scenarios/", ...data.scenarios.map((s) => s.path)]) {
    const f = fixture(route, "ja");
    for (const language of ["ja", "en", "ja"]) {
      f.buttons.find((b) => b.dataset.language === language).dispatch("click");
      assert.equal(f.location.searchParams.get("lang"), language);
      const links = f.elements().filter((node) => node.href?.includes("#HPCI-SYS-"));
      assert.equal(links.length, 3, route);
      for (const link of links) {
        const url = new URL(link.href, f.location);
        assert.equal(url.searchParams.get("lang"), language);
        assert.ok(url.pathname.startsWith("/OpenFS/roadmaps/"), url.href);
        assert.ok(existsSync(path.join(site, url.pathname.slice("/OpenFS/".length), "index.html")), url.href);
      }
      const text = f.elements().map((node) => node.textContent).join(" ");
      assert.ok(text.includes(language === "ja" ? "契約資料に記載された予定総額" : "Planned total reported in the contract disclosure"));
      assert.ok(text.includes(language === "ja" ? "購入価格・TCOではありません" : "Not purchase price or TCO"));
      if (route === "scenarios/") {
        assert.ok(text.includes(language === "ja" ? "計画判断に必要な根拠の充足状況" : "Evidence readiness for planning decisions"));
      } else {
        assert.ok(text.includes(language === "ja" ? "公開根拠から見たこの案の位置付け" : "Position of this option against public evidence"));
        assert.ok(text.includes(language === "ja" ? "確定しない範囲" : "Commitment boundary"));
      }
    }
  }
});
