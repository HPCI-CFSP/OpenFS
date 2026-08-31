const assert = require("node:assert/strict");
const {readFileSync, existsSync} = require("node:fs");
const {test} = require("node:test");
const vm = require("node:vm");
const path = require("node:path");
const root = path.join(__dirname, "..");
const source = readFileSync(path.join(root, "site/roadmaps.js"), "utf8");
const html = readFileSync(path.join(root, "site/roadmap-detail.html"), "utf8");
const seed = {window: {}};
vm.runInNewContext(readFileSync(process.env.OPENFS_TEST_PUBLIC_DATA, "utf8"), seed);
const data = JSON.parse(JSON.stringify(seed.window.OPENFS_PUBLIC_DATA));
const site = path.dirname(path.dirname(process.env.OPENFS_TEST_PUBLIC_DATA));

// Offline rendering and event checks; not browser layout or pixel verification.
function fixture(slug = "reference-blueprint-centers", query = "") {
  const walk = (node) => typeof node === "string" ? [] : [node, ...node.children.flatMap(walk)];
  class Element {
    constructor(tag) {
      this.tagName = tag; this.children = []; this.dataset = {}; this.attributes = {};
      this.events = {}; this.value = ""; this.open = false; this.text = "";
      this.classList = {toggle: () => {}}; this.style = {setProperty() {}};
    }
    set textContent(value) { this.text = String(value); this.children = []; }
    get textContent() { return this.text + this.children.map((c) => typeof c === "string" ? c : c.textContent).join(" "); }
    append(...nodes) { this.children.push(...nodes); }
    prepend(...nodes) { this.children.unshift(...nodes); }
    appendChild(node) { this.append(node); return node; }
    replaceChildren(...nodes) { this.text = ""; this.children = nodes; }
    setAttribute(k, v) { this.attributes[k] = String(v); }
    addEventListener(type, fn) { (this.events[type] ||= []).push(fn); }
    dispatch(type) { (this.events[type] || []).forEach((fn) => fn({target: this, currentTarget: this, preventDefault() {}})); }
    showModal() { this.open = true; this.showCount = (this.showCount || 0) + 1; }
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
    createElement: (tag) => new Element(tag), createTextNode: (text) => text, getElementById: get,
    querySelectorAll: (selector) => selector === "[data-language]" ? languageButtons : [],
    querySelector: (selector) => {
      const [id, cls] = selector.split(" ");
      return walk(get(id.slice(1)) || new Element("div")).find((el) => el.className?.split(" ").includes(cls?.slice(1)));
    }};
  const artifact = data.roadmap_artifacts.find((r) => r.slug === slug);
  const builtPage = readFileSync(path.join(site, "roadmaps", slug, "index.html"), "utf8");
  document.body.dataset = {page: "roadmap-detail", rootPrefix: builtPage.match(/data-root-prefix="([^"]*)"/)[1], roadmapId: artifact.export_id};
  const location = new URL(`https://hpci-cfsp.github.io/OpenFS/roadmaps/${slug}/${query}`);
  const window = {OPENFS_PUBLIC_DATA: structuredClone(data), location,
    localStorage: {getItem: () => null, setItem() {}},
    history: {replaceState(_a, _b, url) { location.href = String(url); }},
    OpenFSFeedback: {mount() {}, link: () => new Element("a")}};
  vm.runInNewContext(source, {window, document, URL, URLSearchParams, Intl});
  return {get, walk, location, languageButtons, artifact};
}

test("inventory links resolve to the correct bilingual lifecycle dialog", () => {
  const blueprint = data.roadmap_artifacts.find((r) => r.roadmap_id === "RM-X-BLUEPRINT");
  for (const language of ["ja", "en"]) {
    const f = fixture(blueprint.slug, `?lang=${language}#HPCI-SYS-SIRIUS`);
    const row = f.get("HPCI-SYS-SIRIUS");
    assert.equal(row.scrolled, true);
    assert.ok(row.textContent.includes("512 GiB"));
    assert.ok(row.textContent.includes("2026 Q2"));
    const performance = f.get("HPCI-SYS-SIRIUS-performance");
    assert.equal(performance.children[0].colSpan, 8);
    assert.ok(performance.textContent.includes("496.08"));
    assert.ok(performance.textContent.includes(language === "ja" ? "性能値の定義" : "Peak-performance definitions"));
    const events = f.walk(row).filter((el) => el.href?.includes("milestone="));
    assert.equal(events.length, 3);
    assert.equal(f.walk(row).filter((el) => el.href?.includes("#procurement-")).length, 1);
    for (const event of events) {
      const url = new URL(event.href, f.location);
      assert.ok(existsSync(path.join(site, url.pathname.slice("/OpenFS/".length), "index.html")), url.href);
      const opened = fixture(blueprint.slug, url.search);
      const milestone = blueprint.lanes.flatMap((lane) => lane.milestones).find((m) => m.milestone_id === url.searchParams.get("milestone"));
      assert.equal(opened.get("roadmap-dialog").open, true);
      assert.equal(opened.get("roadmap-dialog").showCount, 1);
      assert.equal(opened.get("roadmap-dialog-title").textContent, milestone[`label_${language}`]);
      opened.get("roadmap-dialog-close").dispatch("click");
      assert.equal(opened.location.searchParams.has("milestone"), false);
    }
  }
});

test("every roadmap renders both languages without undefined titles or duplicate IDs", () => {
  for (const artifact of data.roadmap_artifacts) for (const language of ["ja", "en"]) {
    const f = fixture(artifact.slug, `?lang=${language}`);
    assert.equal(f.get("roadmap-title").textContent, artifact[`title_${language}`]);
    for (const id of ["roadmap-timeline", "roadmap-track-details", "roadmap-gaps"]) {
      const container = f.get(id);
      assert.ok(container, id);
      assert.ok(!f.walk(container).some((el) => el.text === "undefined" || el.text.startsWith("undefined:")), `${artifact.slug}: ${id}`);
      const ids = f.walk(container).map((el) => el.id).filter(Boolean);
      assert.equal(ids.length, new Set(ids).size);
    }
  }
});

test("generation URLs are updated, cleared on close, and cannot open two dialogs", () => {
  const artifact = data.roadmap_artifacts.find((r) => r.tracks.some((t) => t.generation_bands?.length));
  const band = artifact.tracks.flatMap((t) => t.generation_bands || [])[0];
  const f = fixture(artifact.slug, `?generation=${band.generation_band_id}`);
  assert.equal(f.get("roadmap-dialog").open, true);
  const milestoneButton = f.walk(f.get("roadmap-timeline")).find((el) => el.className?.startsWith("roadmap-milestone "));
  milestoneButton.dispatch("click");
  assert.equal(f.location.searchParams.has("generation"), false);
  assert.equal(f.location.searchParams.has("milestone"), true);
  const generationButton = f.walk(f.get("roadmap-timeline")).find((el) => el.className?.startsWith("roadmap-generation-band "));
  generationButton.dispatch("click");
  assert.equal(f.location.searchParams.has("milestone"), false);
  f.get("roadmap-dialog-close").dispatch("click");
  assert.equal(f.location.searchParams.has("generation"), false);
  const term = data.roadmap_reference_data.terms[0];
  const both = fixture(artifact.slug, `?term=${term.term_id}&generation=${band.generation_band_id}`);
  assert.equal(both.get("roadmap-term-dialog").open, true);
  assert.equal(both.get("roadmap-dialog").open, false);
});

test("language switches preserve the open event, anchor, and shareable URL", () => {
  const roadmap = data.roadmap_artifacts.find((r) => r.roadmap_id === "RM-X-BLUEPRINT");
  const milestone = roadmap.lanes.flatMap((lane) => lane.milestones)
    .find((m) => m.milestone_id === "MS-BLUE-TSUKUBA-SIRIUS-2026Q1");
  const f = fixture(roadmap.slug, `?lang=ja&milestone=${milestone.milestone_id}#HPCI-SYS-SIRIUS`);
  for (const language of ["en", "ja"]) {
    f.languageButtons.find((button) => button.dataset.language === language).dispatch("click");
    assert.equal(f.location.searchParams.get("lang"), language);
    assert.equal(f.location.searchParams.get("milestone"), milestone.milestone_id);
    assert.equal(f.location.hash, "#HPCI-SYS-SIRIUS");
    assert.equal(f.get("roadmap-dialog").showCount, 1);
    assert.equal(f.get("roadmap-dialog-title").textContent, milestone[`label_${language}`]);
    const reloaded = fixture(roadmap.slug, `${f.location.search}${f.location.hash}`);
    assert.equal(reloaded.get("roadmap-dialog-title").textContent, milestone[`label_${language}`]);
  }
});
