const assert = require("node:assert/strict");
const {readFileSync} = require("node:fs");
const {test} = require("node:test");
const vm = require("node:vm");
const path = require("node:path");
const root = path.join(__dirname, "..");
const source = readFileSync(path.join(root, "site/app.js"), "utf8");
const html = readFileSync(path.join(root, "site/index.html"), "utf8");
const publicScript = readFileSync(process.env.OPENFS_TEST_PUBLIC_DATA, "utf8");
const seed = {window: {}};
vm.runInNewContext(publicScript, seed);
const data = JSON.parse(JSON.stringify(seed.window.OPENFS_PUBLIC_DATA));

// Event/render tests without a browser, network, or a claim of CSS/layout coverage.
function fixture(query = "") {
  const walk = (node) => typeof node === "string" ? [] : [node, ...node.children.flatMap(walk)];
  class Element {
    constructor(tag) {
      this.tagName = tag; this.children = []; this.dataset = {}; this.attributes = {};
      this.events = {}; this.value = ""; this.open = false; this.text = "";
      this.classList = {toggle: () => {}};
    }
    set textContent(value) { this.text = String(value); this.children = []; }
    get textContent() { return this.text + this.children.map((c) => typeof c === "string" ? c : c.textContent).join(" "); }
    append(...nodes) { this.children.push(...nodes); }
    appendChild(node) { this.append(node); return node; }
    replaceChildren(...nodes) { this.text = ""; this.children = nodes; }
    setAttribute(k, v) { this.attributes[k] = String(v); }
    addEventListener(type, fn) { (this.events[type] ||= []).push(fn); }
    dispatch(type) { (this.events[type] || []).forEach((fn) => fn({target: this, currentTarget: this, preventDefault() {}})); }
    showModal() { this.open = true; }
    close() { this.open = false; this.dispatch("close"); }
    scrollIntoView() { this.scrolled = true; }
  }
  const ids = new Map([...html.matchAll(/id="([^"]+)"/g)].map((m) => {
    const element = new Element("div"); element.id = m[1]; return [m[1], element];
  }));
  const languageButtons = ["ja", "en"].map((language) => {
    const button = new Element("button"); button.dataset.language = language; return button;
  });
  const get = (id) => ids.get(id) || [...ids.values()].flatMap(walk).find((el) => el.id === id);
  const document = {documentElement: {}, body: new Element("body"),
    createElement: (tag) => new Element(tag), getElementById: get,
    querySelectorAll: (selector) => selector === "[data-language]" ? languageButtons : []};
  const location = new URL(`https://hpci-cfsp.github.io/OpenFS/${query}`);
  const window = {OPENFS_PUBLIC_DATA: structuredClone(data), location,
    localStorage: {getItem: () => null, setItem() {}},
    history: {replaceState(_a, _b, url) { location.href = String(url); }},
    OpenFSFeedback: {mount() {}, link: () => new Element("a")}};
  vm.runInNewContext(source, {window, document, URL, URLSearchParams, Intl});
  return {get, walk, location, languageButtons};
}

test("all 40 topics show the matching bilingual title, scope, units, and evidence links", () => {
  for (const topic of data.topics) for (const language of ["ja", "en"]) {
    const f = fixture(`?topic=${topic.topic_id}&lang=${language}`);
    assert.equal(f.get("topic-dialog").open, true);
    assert.equal(f.get("topic-dialog-title").textContent, topic[`title_${language}`]);
    const content = f.get("topic-dialog-content");
    for (const unit of topic.research_units) {
      assert.ok(content.textContent.includes(unit[`question_${language}`]), unit.unit_id);
      for (const id of unit.evidence_section_ids) assert.ok(f.get(id), `missing evidence target ${id}`);
    }
    assert.ok(!content.textContent.includes("undefined"));
    const ids = f.walk(content).map((el) => el.id).filter(Boolean);
    assert.equal(ids.length, new Set(ids).size);
  }
});

test("every old ID and public code gives explicit successors; split links do not guess", () => {
  for (const alias of data.catalog_aliases) for (const id of [alias.topic_id, alias.legacy_code].filter(Boolean)) {
    const f = fixture(`?topic=${id}`);
    assert.equal(f.get("topic-dialog").open, true, id);
    if (data.topics.some((t) => t.topic_id === id)) continue;
    const links = f.walk(f.get("topic-dialog-content")).filter((el) => el.tagName === "a");
    for (const tid of alias.target_topic_ids) assert.ok(links.some((link) => link.href.includes(`topic=${tid}`)), id);
    if (alias.target_topic_ids.length) {
      const tid = alias.target_topic_ids[0];
      links.find((link) => link.href.includes(`topic=${tid}`)).dispatch("click");
      assert.equal(f.location.searchParams.get("topic"), tid);
      assert.equal(f.get("topic-dialog-id").textContent, data.topics.find((t) => t.topic_id === tid).catalog_code);
    }
  }
  assert.equal(fixture("?topic=not-a-topic").get("topic-dialog").open, false);
});

test("language switching and related-topic navigation retain the current scope", () => {
  const f = fixture("?topic=SSW-05&lang=ja");
  f.languageButtons[1].dispatch("click");
  assert.equal(f.location.searchParams.get("lang"), "en");
  assert.equal(f.get("topic-dialog-title").textContent, "Storage systems and data management");
  const link = f.walk(f.get("topic-dialog-content")).find((el) => el.href?.includes("topic=CROSS-14"));
  link.dispatch("click");
  assert.equal(f.get("topic-dialog-title").textContent, data.topics.find((t) => t.topic_id === "CROSS-14").title_en);
  f.get("topic-dialog-close").dispatch("click");
  assert.equal(f.get("topic-dialog").open, false);
  assert.equal(f.location.searchParams.has("topic"), false);
});

test("category filters and research-unit keywords find the reorganized storage topic", () => {
  const f = fixture();
  assert.equal(f.get("topic-rows").children.length, 40);
  for (const category of data.catalog_taxonomy.categories) {
    f.get("topic-category-filter").children.find((b) => b.dataset.category === category.category_id).dispatch("click");
    assert.equal(f.get("topic-rows").children.length, category.topic_ids.length);
  }
  f.get("topic-category-filter").children.find((b) => b.dataset.category === "all").dispatch("click");
  const search = f.get("topic-search"); search.value = "SSD"; search.dispatch("input");
  assert.equal(f.get("topic-rows").children.length, 1);
  assert.ok(f.get("topic-rows").textContent.includes("ARCH-012"));
});
