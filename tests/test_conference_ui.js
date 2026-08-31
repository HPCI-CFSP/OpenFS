const assert = require("node:assert/strict");
const {readFileSync} = require("node:fs");
const {test} = require("node:test");
const vm = require("node:vm");
const path = require("node:path");
const root = path.join(__dirname, "..");
const script = readFileSync(path.join(root, "site/conferences.js"), "utf8");
const html = readFileSync(path.join(root, "site/conference-detail.html"), "utf8");
const seed = {window: {}};
vm.runInNewContext(readFileSync(process.env.OPENFS_TEST_PUBLIC_DATA, "utf8"), seed);
const data = seed.window.OPENFS_PUBLIC_DATA;

// Offline event/render regression checks; not browser or CSS/layout verification.
function fixture(query = "") {
  const walk = (n) => typeof n === "string" ? [] : [n, ...n.children.flatMap(walk)];
  class Element {
    constructor(tag) { this.tagName = tag.toUpperCase(); this.children = []; this.events = {}; this.attributes = {}; this.dataset = {}; this.value = ""; this.text = ""; }
    set textContent(v) { this.text = String(v); this.children = []; }
    get textContent() { return this.text + this.children.map((n) => typeof n === "string" ? n : n.textContent).join(" "); }
    append(...nodes) { this.children.push(...nodes); }
    replaceChildren(...nodes) { this.text = ""; this.children = nodes; }
    setAttribute(k, v) { this.attributes[k] = v; }
    addEventListener(k, fn) { this.events[k] = fn; }
    dispatch(k) { this.events[k]?.(); }
  }
  const ids = new Map([...html.matchAll(/id="([^"]+)"/g)].map((m) => [m[1], new Element("div")]));
  const buttons = ["ja", "en"].map((language) => { const b = new Element("button"); b.dataset.language = language; return b; });
  const get = (id) => ids.get(id) || [...ids.values()].flatMap(walk).find((n) => n.id === id);
  const document = {documentElement: {}, body: {dataset: {rootPrefix: "../../"}}, getElementById: get,
    createElement: (tag) => new Element(tag), createTextNode: (text) => text,
    querySelectorAll: (selector) => selector === "[data-language]" ? buttons : []};
  const location = new URL(`https://hpci-cfsp.github.io/OpenFS/conferences/hot-chips-2026/${query}`);
  const events = {};
  const window = {OPENFS_PUBLIC_DATA: structuredClone(data), addEventListener: (key, fn) => { events[key] = fn; }};
  vm.runInNewContext(script, {window, document, location, URL, URLSearchParams,
    localStorage: {getItem: () => null, setItem() {}}, history: {replaceState(_a, _b, url) { location.href = url.href; }}});
  return {get, walk, buttons, location, events};
}

test("all 48 entries preserve canonical bilingual explanations and working catalog links", () => {
  for (const lang of ["ja", "en"]) {
    const f = fixture(`?lang=${lang}`);
    assert.equal(f.get("conference-entries").children.length, 48);
    for (const entry of data.conference_coverage.entries) {
      const detail = f.get(entry.entry_id);
      assert.ok(detail.textContent.includes(entry[`label_${lang}`]));
      assert.ok(detail.textContent.includes(entry[`gap_${lang}`]));
      assert.ok(!detail.textContent.includes("undefined"));
      for (const link of f.walk(detail).filter((n) => n.href?.startsWith("../../?topic="))) {
        const id = new URL(link.href, f.location).searchParams.get("topic");
        assert.ok(data.topics.some((t) => t.topic_id === id));
      }
      for (const id of entry.technical_item_ids) {
        const claim = data.topic_decision_support.topic_profiles.flatMap((p) => p.sections.flatMap((s) => s.items)).find((i) => i.item_id === id);
        assert.ok(detail.textContent.includes(claim[`statement_${lang}`]));
      }
    }
  }
});

test("organization and coverage filters intersect and language switching retains filters", () => {
  const f = fixture();
  f.get("conference-organization").value = "AMD"; f.get("conference-organization").dispatch("change");
  assert.equal(f.get("conference-entries").children.length, 4);
  f.get("conference-status").value = "program-only"; f.get("conference-status").dispatch("change");
  assert.equal(f.get("conference-entries").children.length, 1);
  f.buttons[1].dispatch("click");
  assert.equal(f.get("conference-entries").children.length, 1);
  assert.ok(f.get("conference-entries").textContent.includes("Versal RF"));
});

test("deep links open the target and clear conflicting filters", () => {
  const f = fixture("#HC26-C26");
  assert.equal(f.get("HC26-C26").open, true);
  f.get("conference-organization").value = "AMD"; f.get("conference-organization").dispatch("change");
  f.location.hash = "HC26-P06"; f.events.hashchange();
  assert.equal(f.get("HC26-P06").open, true);
  assert.equal(f.get("conference-entries").children.length, 48);
});
