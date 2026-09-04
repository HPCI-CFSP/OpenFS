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
    get textContent() { return this.text + this.children.map((c) => typeof c === "string" ? c : c.textContent).join(""); }
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
    createElement: (tag) => new Element(tag), createTextNode: (value) => String(value), getElementById: get,
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
    assert.ok(links.length > 0, `legacy entry lacks a destination: ${id}`);
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

test("catalog findings link centralized terms, comparisons, sources, and roadmaps", () => {
  const f = fixture("?topic=ARCH-03&lang=ja");
  const content = f.get("topic-dialog-content");
  const hbm = f.walk(content).find((el) => el.className === "glossary-term-link" && el.textContent === "HBM");
  assert.ok(hbm, "ARCH-03 should link HBM to the centralized glossary");
  hbm.dispatch("click");
  assert.equal(f.get("term-dialog").open, true);
  assert.equal(f.location.searchParams.get("term"), "TERM-HBM");
  assert.ok(f.get("term-dialog-content").textContent.includes(
    data.roadmap_reference_data.terms.find((term) => term.term_id === "TERM-HBM").definition_ja
  ));
  const termLinks = f.walk(f.get("term-dialog-content")).filter((el) => el.tagName === "a");
  assert.ok(termLinks.some((link) => link.href?.startsWith("http")), "term dialog should show primary sources");
  assert.ok(termLinks.some((link) => link.href?.includes("roadmaps/hardware/memory-data-movement/")), "term dialog should link its roadmap");
  assert.ok(f.walk(content).some((el) => el.className === "technology-comparison-table"), "topic should show a relevant comparison table");
  f.languageButtons.find((button) => button.dataset.language === "en").dispatch("click");
  assert.equal(f.get("term-dialog-title").textContent, "HBM");
  f.get("term-dialog-close").dispatch("click");
  assert.equal(f.location.searchParams.has("term"), false);
});

test("procurement findings expose the new comparison and catalog primary sources", () => {
  const f = fixture("?topic=CROSS-06&lang=ja");
  const content = f.get("topic-dialog-content");
  const comparison = f.get("catalog-comparison-CMP-NATIONAL-COMPUTE-PROCUREMENT-MODES");
  assert.ok(comparison, "CROSS-06 should show the national-compute procurement comparison");
  assert.ok(comparison.textContent.includes("官民共同投資"));
  const term = f.walk(content).find((el) =>
    el.className === "glossary-term-link" && el.textContent === "官民共同投資"
  );
  assert.ok(term, "CROSS-06 should link the co-investment term to the centralized glossary");
  term.dispatch("click");
  assert.equal(f.location.searchParams.get("term"), "TERM-PUBLIC-PRIVATE-COINVESTMENT");
  const sourceLinks = f.walk(f.get("term-dialog-content")).filter((el) => el.tagName === "a");
  assert.ok(
    sourceLinks.some((link) => link.href === data.topic_decision_support.sources.find(
      (source) => source.source_id === "SRC-CDS146"
    ).url),
    "catalog-backed glossary entries should expose their primary source"
  );
  assert.ok(
    sourceLinks.some((link) => link.href?.includes("roadmaps/cross-cutting/reference-blueprint-centers/")),
    "the glossary entry should link the reference-blueprint roadmap"
  );
});

test("hardware follow-ups show each current item in its own bilingual catalog", () => {
  let itemCount = 0;
  for (const profile of data.topic_decision_support.topic_profiles) {
    const sections = profile.sections.filter((s) => /^TDS-HW[123]-/.test(s.section_id));
    if (!sections.length) continue;
    itemCount += sections.reduce((count, section) => count + section.items.length, 0);
    for (const language of ["ja", "en"]) {
      const f = fixture(`?topic=${profile.topic_id}&lang=${language}`);
      for (const section of sections) {
        const visible = f.get(section.section_id);
        assert.ok(visible, section.section_id);
        for (const item of section.items) {
          assert.ok(visible.textContent.includes(item[`name_${language}`]), item.item_id);
          assert.ok(visible.textContent.includes(item[`statement_${language}`]), item.item_id);
          assert.equal(item.consensus_status, "incomplete");
        }
      }
      for (const archived of profile.archived_section_ids || []) assert.equal(f.get(archived), undefined);
    }
  }
  const canonical = JSON.parse(readFileSync(path.join(root, "knowledge/public/topic-decision-support.json"), "utf8"));
  const expectedCount = canonical.topic_profiles.reduce((total, profile) => {
    const archived = new Set(profile.archived_section_ids || []);
    return total + profile.sections
      .filter((section) => /^TDS-HW[123]-/.test(section.section_id) && !archived.has(section.section_id))
      .reduce((count, section) => count + section.items.length, 0);
  }, 0);
  assert.equal(itemCount, expectedCount);
});

test("cross-domain follow-ups render all current claims under their owning catalogs", () => {
  let topicCount = 0;
  const canonical = JSON.parse(readFileSync(path.join(root, "knowledge/public/topic-decision-support.json"), "utf8"));
  for (const profile of canonical.topic_profiles) {
    const archived = new Set(profile.archived_section_ids || []);
    const sections = profile.sections.filter((s) => /^TDS-CD\d+-/.test(s.section_id) && !archived.has(s.section_id));
    if (!sections.length) continue;
    topicCount++;
    const published = data.topic_decision_support.topic_profiles.find((p) => p.topic_id === profile.topic_id);
    assert.ok(published, profile.topic_id);
    assert.ok(published.sections.every((s) => !archived.has(s.section_id)));
    for (const language of ["ja", "en"]) {
      const f = fixture(`?topic=${profile.topic_id}&lang=${language}`);
      for (const section of sections) {
        const visible = f.get(section.section_id);
        assert.ok(visible, section.section_id);
        const links = f.walk(visible).filter((el) => el.tagName === "a").map((el) => el.href);
        for (const item of section.items) {
          assert.ok(visible.textContent.includes(item[`statement_${language}`]), item.item_id);
          assert.ok(visible.textContent.includes(item[`hpci_relevance_${language}`]), item.item_id);
          for (const condition of item[`adoption_conditions_${language}`]) assert.ok(visible.textContent.includes(condition), item.item_id);
          for (const id of item.source_ids) {
            const evidence = canonical.sources.find((s) => s.source_id === id);
            assert.ok(links.includes(evidence.url), `${item.item_id}: missing ${id}`);
          }
          assert.equal(item.consensus_status, "incomplete");
        }
      }
      for (const id of archived) assert.equal(f.get(id), undefined);
    }
  }
  assert.ok(topicCount >= 33, `expected at least 33 cross-domain topic profiles, found ${topicCount}`);
});
