const assert = require("node:assert/strict");
const {readFileSync} = require("node:fs");
const {test} = require("node:test");
const vm = require("node:vm");

const code = readFileSync(require.resolve("../site/feedback.js"), "utf8");
const commit = "b".repeat(40);

// A small, offline DOM double tests widget events without loading a browser or resources.
function fixture({standalone = false, query = "", storageFails = false} = {}) {
  class Element {
    constructor(tag) {
      this.tagName = tag; this.children = []; this.dataset = {}; this.attributes = {}; this.events = {};
      this.classList = {toggle: (name, enabled) => {
        const names = new Set((this.className || "").split(" ").filter(Boolean));
        if (enabled) names.add(name); else names.delete(name);
        this.className = [...names].join(" ");
      }};
    }
    append(...nodes) { this.children.push(...nodes); }
    replaceChildren(...nodes) { this.children = nodes; }
    setAttribute(key, value) { this.attributes[key] = String(value); }
    addEventListener(type, handler) { (this.events[type] ||= []).push(handler); }
    dispatch(type, event = {target: this}) { for (const handler of this.events[type] || []) handler(event); }
    showModal() { assert.ok(!this.open); this.open = true; }
    close() { this.open = false; this.dispatch("close"); }
  }
  const document = {body: new Element("body"), documentElement: {lang: "ja"}, createElement: (tag) => new Element(tag)};
  const walk = (root) => [root, ...root.children.flatMap(walk)];
  const all = () => walk(document.body);
  const attributeKey = (selector) => selector.slice(6, -1).replace(/-([a-z])/g, (_, letter) => letter.toUpperCase());
  document.getElementById = (id) => all().find((element) => element.id === id);
  document.querySelectorAll = (selector) => all().filter((element) => selector.startsWith(".")
    ? (element.className || "").split(" ").includes(selector.slice(1))
    : Object.hasOwn(element.dataset, attributeKey(selector)));
  const add = (tag, id) => { const element = new Element(tag); element.id = id; document.body.append(element); return element; };
  const root = add("div", "context");
  const nav = add("a", "nav"); nav.dataset.feedbackNav = ""; nav.dataset.feedbackCopy = "navFeedback";
  nav.href = "https://hpci-cfsp.github.io/OpenFS/feedback/";
  if (standalone) {
    document.body.dataset.page = "feedback";
    for (const id of ["feedback-correction", "feedback-research", "feedback-suggestion", "feedback-existing"]) add("div", id);
    for (const language of ["ja", "en"]) add("button", language).dataset.language = language;
  }
  const window = {OPENFS_PUBLIC_DATA: {site: {commit_sha: commit}}, location: {search: query}, localStorage: {
    getItem() { if (storageFails) throw new Error("Disabled storage"); return "ja"; },
    setItem() { if (storageFails) throw new Error("Disabled storage"); },
  }};
  let refresh;
  class MutationObserver { constructor(callback) { refresh = callback; } observe() {} }
  vm.runInNewContext(code, {window, document, MutationObserver, URL, URLSearchParams});
  return {window, document, root, all, refresh: () => refresh(), dialog: document.getElementById("feedback-dialog")};
}

const topic = {kind: "topic", id: "ARCH-03", title: "Memory <HBM>", path: "?topic=ARCH-03"};

test("Feedback chooser preserves the original target for all three forms", () => {
  const f = fixture();
  f.window.OpenFSFeedback.mount("context", topic);
  const button = f.root.children[0];
  assert.equal(button.textContent, "Feedback");
  assert.equal(button.attributes["aria-haspopup"], "dialog");
  assert.equal(button.href, undefined);
  button.dispatch("click");
  assert.equal(f.dialog.open, true);
  const content = f.dialog.children[0];
  assert.equal(content.children[1].textContent, "ARCH-03 · Memory <HBM>");
  const links = content.children[2].children;
  assert.equal(links.length, 4);
  for (const [index, template] of ["correction-report.yml", "research-request.yml", "improvement-proposal.yml"].entries()) {
    const url = new URL(links[index].href);
    assert.equal(url.searchParams.get("template"), template);
    assert.equal(url.searchParams.get("target"), "topic: ARCH-03");
    assert.equal(url.searchParams.get("source_commit"), commit);
    assert.equal(links[index].rel, "noopener noreferrer");
  }
  assert.match(links[3].href, /public-feedback/);
  content.children[0].children[1].dispatch("click");
  assert.equal(f.dialog.open, false);
});

test("reopening for a different item updates context and display language", () => {
  const f = fixture();
  f.window.OpenFSFeedback.mount("context", topic);
  f.root.children[0].dispatch("click");
  f.dialog.dispatch("click");
  f.document.documentElement.lang = "en";
  f.refresh();
  f.window.OpenFSFeedback.mount("context", {...topic, id: "ARCH-04", title: "Interconnect", path: "?topic=ARCH-04"});
  f.root.children[0].dispatch("click");
  const links = f.dialog.children[0].children[2].children;
  assert.equal(links[1].textContent, "Request additional research");
  for (const link of links.slice(0, 3)) {
    const url = new URL(link.href);
    assert.equal(url.searchParams.get("target"), "topic: ARCH-04");
    assert.equal(url.searchParams.get("language"), "English");
  }
});

test("the Feedback page switches all form links and works without local storage", () => {
  const f = fixture({standalone: true, query: "?lang=en", storageFails: true});
  assert.equal(f.document.documentElement.lang, "en");
  assert.equal(f.document.getElementById("en").attributes["aria-pressed"], "true");
  assert.equal(f.document.getElementById("en").className, "active");
  for (const id of ["feedback-correction", "feedback-research", "feedback-suggestion"]) {
    assert.equal(new URL(f.document.getElementById(id).children[0].href).searchParams.get("language"), "English");
  }
  f.document.getElementById("ja").dispatch("click");
  assert.equal(f.document.documentElement.lang, "ja");
  assert.equal(f.document.getElementById("ja").attributes["aria-pressed"], "true");
  assert.equal(f.document.getElementById("ja").className, "active");
  assert.equal(f.document.getElementById("en").className, "");
  assert.equal(f.document.getElementById("feedback-research").children[0].textContent, "追加調査をリクエスト");
  assert.equal(new URL(f.document.getElementById("nav").href).searchParams.get("lang"), "ja");
});
