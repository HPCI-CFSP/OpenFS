const assert = require("node:assert/strict");
const {readFileSync} = require("node:fs");
const {test} = require("node:test");
const vm = require("node:vm");
const path = require("node:path");
const root = path.join(__dirname, "..");
const source = readFileSync(path.join(root, "site/search.js"), "utf8");
const html = readFileSync(path.join(root, "site/search.html"), "utf8");
const seed = {window: {}};
vm.runInNewContext(readFileSync(process.env.OPENFS_TEST_PUBLIC_DATA, "utf8"), seed);
const data = JSON.parse(JSON.stringify(seed.window.OPENFS_PUBLIC_DATA));

// Offline event/render coverage; no network access or browser-layout claims.
function fixture(query, language = "ja", mutate = () => {}) {
  const walk = (node) => [node, ...node.children.flatMap(walk)];
  class Element {
    constructor(tag) {
      this.tagName = tag; this.children = []; this.dataset = {}; this.events = {};
      this.attributes = {}; this.text = ""; this.value = "";
      this.classList = {toggle() {}};
    }
    set textContent(value) { this.text = String(value); this.children = []; }
    get textContent() { return this.text + this.children.map((c) => c.textContent).join(" "); }
    append(...nodes) { this.children.push(...nodes); }
    replaceChildren(...nodes) { this.text = ""; this.children = nodes; }
    setAttribute(key, value) { this.attributes[key] = String(value); }
    addEventListener(type, fn) { (this.events[type] ||= []).push(fn); }
    dispatch(type) { (this.events[type] || []).forEach((fn) => fn({preventDefault() {}})); }
  }
  const ids = new Map([...html.matchAll(/id="([^"]+)"/g)].map((m) => [m[1], new Element("div")]));
  ids.get("global-search-type").value = "source";
  const buttons = ["ja", "en"].map((lang) => {
    const button = new Element("button"); button.dataset.language = lang; return button;
  });
  const document = {documentElement: {}, body: new Element("body"),
    createElement: (tag) => new Element(tag), getElementById: (id) => ids.get(id),
    querySelectorAll: (selector) => selector === "[data-language]" ? buttons : []};
  const location = new URL(`https://hpci-cfsp.github.io/OpenFS/search/?q=${encodeURIComponent(query)}&lang=${language}`);
  const payload = structuredClone(data); mutate(payload);
  const window = {OPENFS_PUBLIC_DATA: payload, location};
  vm.runInNewContext(source, {window, document, URL, URLSearchParams,
    localStorage: {getItem: () => null, setItem() {}},
    history: {replaceState(_a, _b, url) { location.href = String(url); }}});
  return {get: (id) => ids.get(id), walk, buttons, location,
    results: () => ids.get("global-search-results").children};
}

test("catalog-only evidence is searchable in Japanese and English", () => {
  for (const language of ["ja", "en"]) {
    for (const id of ["SRC-CDA113", "SRC-CDS114", "SRC-CDG025", "SRC-CDA116"]) {
      const evidence = data.topic_decision_support.sources.find((s) => s.source_id === id);
      assert.ok(evidence, id);
      const f = fixture(id, language);
      const links = f.results().flatMap(f.walk).filter((el) => el.tagName === "a");
      assert.ok(links.some((link) => link.href === evidence.url), id);
      assert.ok(f.get("global-search-results").textContent.includes(id));
      assert.ok(!f.get("global-search-results").textContent.includes("undefined"));
    }
  }
});

test("published reports are searchable and keep safe external links", () => {
  const report = data.reports.find((item) => item.report_id === "REPORT-FS3-DECISION-EVIDENCE-20260906");
  assert.ok(report);
  for (const language of ["ja", "en"]) {
    const f = fixture(report.report_id, language);
    f.get("global-search-type").value = "report";
    f.get("global-search-type").dispatch("change");
    assert.equal(f.results().length, 1);
    const link = f.walk(f.results()[0]).find((el) => el.tagName === "a");
    assert.equal(link.href, report.download_url);
    assert.equal(link.rel, "noopener noreferrer");
  }
});

function addSyntheticSources(payload) {
  const profile = payload.topic_decision_support.topic_profiles[0];
  const sources = payload.topic_decision_support.sources;
  for (const suffix of ["ACTIVE", "ARCHIVED", "ORPHAN", "RETIRED", "MATRIX", "OLD", "CORRECTED"]) {
    sources.push({source_id: `SRC-SEARCH-${suffix}`, title: `Search fixture ${suffix}`,
      publisher: "Search fixture publisher", url: `https://example.org/search-${suffix.toLowerCase()}`,
      source_class: "research-artifact"});
  }
  profile.sections.push({section_id: "SEARCH-ACTIVE", items: [{source_ids: ["SRC-SEARCH-ACTIVE", "SRC-SEARCH-CORRECTED"]}]});
  profile.sections.push({section_id: "SEARCH-ARCHIVED", items: [{source_ids: ["SRC-SEARCH-ARCHIVED", "SRC-SEARCH-OLD"]}]});
  profile.archived_section_ids = [...(profile.archived_section_ids || []), "SEARCH-ARCHIVED"];
  payload.topic_decision_support.topic_profiles.push({topic_id: "RETIRED-TEST", sections: [
    {section_id: "SEARCH-RETIRED", items: [{source_ids: ["SRC-SEARCH-RETIRED"]}]}]});
  payload.topic_decision_support.platform_matrix.capabilities.push({entries: [{source_ids: ["SRC-SEARCH-MATRIX"]}]});
  sources.find((s) => s.source_id === "SRC-SEARCH-CORRECTED").correction = {supersedes_source_id: "SRC-SEARCH-OLD"};
}

test("active claims and matrix evidence are indexed, not archived or unreferenced metadata", () => {
  for (const suffix of ["ACTIVE", "MATRIX", "CORRECTED"]) {
    assert.equal(fixture(`SRC-SEARCH-${suffix}`, "en", addSyntheticSources).results().length, 1, suffix);
  }
  for (const suffix of ["ARCHIVED", "ORPHAN", "RETIRED"]) {
    assert.equal(fixture(`SRC-SEARCH-${suffix}`, "en", addSyntheticSources).results().length, 0, suffix);
  }
  const corrected = fixture("SRC-SEARCH-OLD", "en", addSyntheticSources);
  assert.equal(corrected.results().length, 1);
  const link = corrected.walk(corrected.results()[0]).find((el) => el.tagName === "a");
  assert.equal(link.href, "https://example.org/search-corrected");
});

test("identical URLs retain all source IDs and classifications without duplicate results", () => {
  const mutate = (payload) => {
    addSyntheticSources(payload);
    const evidence = payload.topic_decision_support.sources.find((s) => s.source_id === "SRC-SEARCH-ACTIVE");
    payload.roadmap_artifacts[0].sources.push({...evidence, source_id: "SRC-SEARCH-ROADMAP", source_class: "academic-primary"});
  };
  for (const query of ["SRC-SEARCH-ACTIVE", "SRC-SEARCH-ROADMAP", "https://example.org/search-active"]) {
    const f = fixture(query, "en", mutate);
    assert.equal(f.results().length, 1);
    const text = f.results()[0].textContent;
    assert.ok(text.includes("SRC-SEARCH-ACTIVE"));
    assert.ok(text.includes("SRC-SEARCH-ROADMAP"));
    assert.ok(text.includes("Research artifact"));
    assert.ok(text.includes("Academic primary source"));
    assert.ok(!text.includes("Peer-reviewed"));
  }
});

test("source filters, input events and language switching preserve safe external links", () => {
  const f = fixture("SRC-SEARCH-ACTIVE", "ja", (payload) => {
    addSyntheticSources(payload);
    payload.topic_decision_support.sources.find((s) => s.source_id === "SRC-SEARCH-ACTIVE").title = "<script>example</script>";
  });
  assert.equal(f.results().length, 1);
  assert.ok(f.results()[0].textContent.includes("研究資料"));
  const link = f.walk(f.results()[0]).find((el) => el.tagName === "a");
  assert.equal(link.textContent, "<script>example</script>");
  assert.equal(link.children.length, 0);
  assert.equal(link.rel, "noopener noreferrer");
  f.buttons[1].dispatch("click");
  assert.ok(f.results()[0].textContent.includes("Research artifact"));
  assert.equal(f.location.searchParams.get("lang"), "en");
  f.get("global-search-type").value = "topic";
  f.get("global-search-type").dispatch("change");
  assert.ok(f.results().every((item) => !item.textContent.includes("Public source")));
  f.get("global-search-type").value = "source";
  f.get("global-search-input").value = "SRC-SEARCH-MATRIX";
  f.get("global-search-input").dispatch("input");
  assert.equal(f.results().length, 1);
  assert.equal(f.location.searchParams.get("q"), "SRC-SEARCH-MATRIX");
  f.get("global-search-input").value = "";
  f.get("global-search-form").dispatch("submit");
  assert.equal(f.results().length, 0);
  assert.equal(f.location.searchParams.has("q"), false);
});

test("a corrected catalog title takes precedence over legacy roadmap metadata for the same URL", () => {
  const f = fixture("SRC-SEARCH-CORRECTED", "en", (payload) => {
    addSyntheticSources(payload);
    const corrected = payload.topic_decision_support.sources.find((s) => s.source_id === "SRC-SEARCH-CORRECTED");
    corrected.title = "Corrected publication title";
    payload.roadmap_artifacts[0].sources.push({...corrected, source_id: "SRC-SEARCH-LEGACY-ROADMAP",
      title: "Legacy title", correction: undefined});
  });
  assert.equal(f.results().length, 1);
  const link = f.walk(f.results()[0]).find((el) => el.tagName === "a");
  assert.equal(link.textContent, "Corrected publication title");
  assert.ok(f.results()[0].textContent.includes("SRC-SEARCH-LEGACY-ROADMAP"));
});

test("topic search excludes archived claims while retaining current claims", () => {
  for (const language of ["ja", "en"]) {
    for (const [query, expected] of [["SRC-SEARCH-ARCHIVED", 0], ["SRC-SEARCH-ACTIVE", 1]]) {
      const f = fixture(query, language, addSyntheticSources);
      f.get("global-search-type").value = "topic";
      f.get("global-search-type").dispatch("change");
      assert.equal(f.results().length, expected, query);
    }
  }
});

test("category membership metadata does not match neighboring topics or roadmaps", () => {
  for (const language of ["ja", "en"]) {
    const f = fixture("CATEGORY-ONLY-PROBE", language, (payload) => {
      for (const category of payload.catalog_taxonomy.categories) {
        category.topic_codes["UNRELATED-TOPIC"] = "CATEGORY-ONLY-PROBE";
      }
    });
    for (const type of ["topic", "roadmap", "all"]) {
      f.get("global-search-type").value = type;
      f.get("global-search-type").dispatch("change");
      assert.equal(f.results().length, 0, type);
    }
  }
});
