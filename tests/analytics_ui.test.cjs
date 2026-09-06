const assert = require("node:assert/strict");
const {readFileSync} = require("node:fs");
const {test} = require("node:test");
const vm = require("node:vm");

const code = readFileSync(require.resolve("../site/analytics.js"), "utf8");

function fixture({url = "https://hpci-cfsp.github.io/OpenFS/roadmaps/hardware/memory-data-movement/?term=HBM#detail", consent = null} = {}) {
  class Element {
    constructor(tag) { this.tagName = tag; this.children = []; this.dataset = {}; this.events = {}; this.parent = null; this.className = ""; }
    set textContent(value) { this.text = String(value); this.children = []; }
    get textContent() { return (this.text || "") + this.children.map((item) => typeof item === "string" ? item : item.textContent).join(" "); }
    append(...nodes) { nodes.forEach((node) => { if (typeof node !== "string") node.parent = this; this.children.push(node); }); }
    replaceChildren(...nodes) { this.children = []; this.append(...nodes); }
    addEventListener(type, handler) { (this.events[type] ||= []).push(handler); }
    dispatch(type) { (this.events[type] || []).forEach((handler) => handler({target: this, currentTarget: this})); }
    setAttribute(key, value) { this[key] = String(value); }
    remove() { if (this.parent) this.parent.children = this.parent.children.filter((item) => item !== this); }
  }
  const location = new URL(url);
  location.assign = (value) => { location.href = String(value); };
  const body = new Element("body"); body.dataset.page = "roadmap-detail";
  const head = new Element("head");
  const currentScript = new Element("script");
  Object.assign(currentScript.dataset, {
    status: "enabled",
    measurementId: "G-7JB5N480MT",
    productionHostname: "hpci-cfsp.github.io",
    productionPathPrefix: "/OpenFS/",
    storageKey: "openfs-analytics-consent-v1",
    privacyPath: "../../privacy/",
    rootPrefix: "../../"
  });
  const walk = (element) => [element, ...element.children.filter((item) => typeof item !== "string").flatMap(walk)];
  const all = () => [...walk(head), ...walk(body)];
  const document = {
    body, head, currentScript, title: "Memory | OpenFS", referrer: "https://example.org/news?q=private#section", documentElement: {},
    createElement: (tag) => new Element(tag),
    getElementById: (id) => all().find((element) => element.id === id),
    querySelectorAll: (selector) => {
      if (selector === "[data-analytics-consent-status]") return all().filter((element) => Object.hasOwn(element.dataset, "analyticsConsentStatus"));
      if (selector === "[data-privacy-language]") return [];
      if (selector === "[data-language]") return [];
      return [];
    }
  };
  const storage = new Map(); if (consent) storage.set("openfs-analytics-consent-v1", consent);
  const window = {
    location,
    localStorage: {getItem: (key) => storage.get(key) || null, setItem: (key, value) => storage.set(key, value)}
  };
  vm.runInNewContext(code, {window, document, URL, URLSearchParams, Date, encodeURIComponent});
  return {window, document, storage, all, banner: () => document.getElementById("openfs-analytics-consent")};
}

test("GA4 is not loaded before consent and a bilingual-safe consent prompt is shown", () => {
  const f = fixture();
  assert.ok(f.banner());
  assert.equal(f.document.head.children.some((element) => element.dataset.openfsAnalytics === "ga4"), false);
  assert.equal(f.window.dataLayer, undefined);
  assert.match(f.banner().children[0].textContent, /検索語/);
});

test("consent loads only GA4 and sends a sanitized page view", () => {
  const f = fixture();
  f.banner().children[1].children[0].dispatch("click");
  assert.equal(f.storage.get("openfs-analytics-consent-v1"), "granted");
  const tag = f.document.head.children.find((element) => element.dataset.openfsAnalytics === "ga4");
  assert.ok(tag);
  assert.equal(tag.src, "https://www.googletagmanager.com/gtag/js?id=G-7JB5N480MT");
  const calls = f.window.dataLayer.map((entry) => Array.from(entry));
  const event = calls.find((entry) => entry[0] === "event" && entry[1] === "page_view");
  assert.ok(event);
  assert.equal(event[2].page_location, "https://hpci-cfsp.github.io/OpenFS/roadmaps/hardware/memory-data-movement/");
  assert.equal(event[2].page_path, "/OpenFS/roadmaps/hardware/memory-data-movement/");
  assert.equal(event[2].page_referrer, "https://example.org/news");
  assert.equal(JSON.stringify(event).includes("term=HBM"), false);
  assert.equal(JSON.stringify(event).includes("private"), false);
});

test("declining or using a preview host never loads the Google tag", () => {
  const declined = fixture({consent: "denied"});
  assert.equal(declined.banner(), undefined);
  assert.equal(declined.document.head.children.length, 0);
  const preview = fixture({url: "http://localhost:8000/OpenFS/?q=HBM", consent: "granted"});
  assert.equal(preview.banner(), undefined);
  assert.equal(preview.document.head.children.length, 0);
  assert.equal(preview.all().some((element) => element.className === "analytics-settings-link"), false);
});
