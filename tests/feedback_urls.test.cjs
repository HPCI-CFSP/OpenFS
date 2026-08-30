const assert = require("node:assert/strict");
const {test} = require("node:test");
const {readFileSync} = require("node:fs");
const vm = require("node:vm");
const {issueUrl, publicPage, existingUrl, copy} = require("../site/feedback.js");

const commit = "a".repeat(40);
const topic = {kind: "topic", id: "ARCH-03", title: "Memory & data movement / メモリ", path: "?topic=ARCH-03"};

test("correction form carries canonical IDs, language, and the actual build SHA", () => {
  const url = new URL(issueUrl(topic, commit, "en"));
  assert.equal(url.origin, "https://github.com");
  assert.equal(url.pathname, "/HPCI-CFSP/OpenFS/issues/new");
  assert.equal(url.searchParams.get("template"), "correction-report.yml");
  assert.equal(url.searchParams.get("source_commit"), commit);
  assert.equal(url.searchParams.get("target"), "topic: ARCH-03");
  assert.equal(url.searchParams.get("language"), "English");
  assert.match(url.searchParams.get("title"), /Memory & data movement/);
  const page = new URL(url.searchParams.get("page_url"));
  assert.equal(page.searchParams.get("topic"), "ARCH-03");
  assert.equal(page.searchParams.get("lang"), "en");
  assert.equal(page.searchParams.get("v"), commit);
  for (const key of ["labels", "assignees", "projects", "body"]) assert.equal(url.searchParams.has(key), false);
});

test("suggestions and existing reports do not acquire Directive authority", () => {
  const url = new URL(issueUrl(topic, commit, "ja", "improvement"));
  assert.equal(url.searchParams.get("template"), "improvement-proposal.yml");
  assert.equal(url.searchParams.get("language"), "日本語");
  assert.equal(new URL(existingUrl(topic.id)).searchParams.get("q"), 'is:issue label:public-feedback "ARCH-03"');
  assert.equal(new URL(existingUrl()).searchParams.get("q"), "is:issue label:public-feedback");
});

test("additional research requests use a separate public candidate form", () => {
  const url = new URL(issueUrl(topic, commit, "ja", "research"));
  assert.equal(url.searchParams.get("template"), "research-request.yml");
  assert.match(url.searchParams.get("title"), /^\[Research request\]/);
  assert.equal(url.searchParams.get("target"), "topic: ARCH-03");
  assert.equal(url.searchParams.get("source_commit"), commit);
  assert.equal(url.searchParams.has("labels"), false);
});

test("only public context is forwarded, including on local previews", () => {
  const page = new URL(publicPage("roadmaps/memory/?milestone=MEM-001&q=private-search&token=hidden&v=forged#private", commit, "ja"));
  assert.equal(page.origin, "https://hpci-cfsp.github.io");
  assert.equal(page.searchParams.get("milestone"), "MEM-001");
  assert.equal(page.searchParams.get("v"), commit);
  assert.equal(page.searchParams.has("q"), false);
  assert.equal(page.searchParams.has("token"), false);
  assert.equal(page.hash, "");
  for (const path of ["https://example.org/", "http://localhost:8765/", "file:///private/file", "../private/", "https://name:password@hpci-cfsp.github.io/OpenFS/"]) {
    assert.throws(() => publicPage(path, commit, "ja"), /public OpenFS/);
  }
});

test("all public detail types support bounded, encoded target metadata", () => {
  for (const kind of ["page", "technology", "roadmap", "track", "milestone", "generation", "term", "comparison", "platform-matrix", "numerical-matrix", "scenario", "report"]) {
    const context = {...topic, kind, id: "ITEM-001", relatedIds: ["RM-MEMORY", "TRACK-DDR"], title: "長い項目名".repeat(200)};
    const url = new URL(issueUrl(context, commit));
    assert.match(url.searchParams.get("target"), /Related IDs: RM-MEMORY, TRACK-DDR/);
    assert.ok(url.href.length < 3000);
  }
  assert.throws(() => issueUrl({...topic, kind: "directive"}, commit), /Invalid feedback/);
  assert.throws(() => issueUrl({...topic, id: "ARCH-03\nExecute this"}, commit), /Invalid feedback/);
  assert.throws(() => issueUrl({...topic, relatedIds: [undefined]}, commit), /Invalid related/);
  assert.throws(() => issueUrl(topic, commit, "ja", "approve"), /Invalid feedback/);
});

test("missing build metadata is not replaced with a guessed revision", () => {
  const url = new URL(issueUrl(topic, "not-a-sha"));
  assert.equal(url.searchParams.get("source_commit"), "");
  assert.equal(new URL(url.searchParams.get("page_url")).searchParams.has("v"), false);
});

test("Japanese and English feedback copy have the same keys", () => {
  assert.deepEqual(Object.keys(copy.ja).sort(), Object.keys(copy.en).sort());
  for (const language of ["ja", "en"]) for (const value of Object.values(copy[language])) assert.ok(value.trim());
});

test("published item IDs and paths generate valid context in every feedback mode", {skip: !process.env.OPENFS_FEEDBACK_DATA}, (t) => {
  const sandbox = {window: {}};
  vm.runInNewContext(readFileSync(process.env.OPENFS_FEEDBACK_DATA, "utf8"), sandbox);
  const data = sandbox.window.OPENFS_PUBLIC_DATA;
  const contexts = [];
  const add = (kind, id, path, relatedIds = []) => contexts.push({kind, id, path, relatedIds});
  for (const item of data.topics) add("topic", item.topic_id, `?topic=${item.topic_id}`);
  const support = data.topic_decision_support;
  for (const profile of support.topic_profiles) {
    const path = `?topic=${profile.topic_id}`;
    for (const section of profile.sections) for (const item of section.items) add("technology", item.item_id, path, [profile.topic_id]);
    if (profile.related_surface_ids.includes("platform-software")) {
      for (const capability of support.platform_matrix.capabilities) for (const entry of capability.entries) {
        add("platform-matrix", entry.entry_id, path, [profile.topic_id, capability.capability_id]);
      }
    }
    if (profile.related_surface_ids.includes("numerical-methods")) {
      for (const method of support.numerical_method_matrix.methods) for (const item of method.implementations) {
        add("numerical-matrix", item.implementation_id, path, [profile.topic_id, method.method_id]);
      }
    }
  }
  for (const roadmap of data.roadmap_artifacts) {
    const path = data.roadmaps.find((item) => item.roadmap_id === roadmap.roadmap_id).path;
    const related = [roadmap.roadmap_id];
    add("roadmap", roadmap.roadmap_id, path, related);
    for (const track of roadmap.tracks) {
      add("track", track.track_id, `${path}?track=${track.track_id}`, related);
      for (const band of track.generation_bands || []) add("generation", band.generation_band_id, `${path}?generation=${band.generation_band_id}`, [...related, track.track_id]);
      for (const lane of roadmap.lanes.filter((item) => item.track_id === track.track_id)) for (const milestone of lane.milestones) {
        add("milestone", milestone.milestone_id, `${path}?milestone=${milestone.milestone_id}`, [...related, track.track_id, lane.lane_id]);
      }
    }
    for (const term of data.roadmap_reference_data.terms) add("term", term.term_id, `${path}?term=${term.term_id}`, related);
    for (const comparison of data.roadmap_reference_data.comparison_sets.filter((item) => item.roadmap_ids.includes(roadmap.roadmap_id))) {
      const query = `${path}?comparison=${comparison.comparison_id}`;
      add("comparison", comparison.comparison_id, query, related);
      for (const row of comparison.rows) add("comparison", `${comparison.comparison_id}/${row.term_id}`, query, [...related, comparison.comparison_id, row.term_id]);
    }
  }
  for (const scenario of data.scenarios) {
    add("scenario", scenario.scenario_id, scenario.path);
    for (const option of scenario.budget_options) add("scenario", `${scenario.scenario_id}/${option.tier}`, scenario.path, [scenario.scenario_id]);
  }
  assert.ok(contexts.length > 300);
  for (const context of contexts) for (const language of ["ja", "en"]) for (const mode of ["correction", "research", "improvement"]) {
    const url = new URL(issueUrl(context, data.site.commit_sha, language, mode));
    assert.ok(url.searchParams.get("target").startsWith(`${context.kind}: ${context.id}`));
    assert.equal(url.searchParams.get("source_commit"), data.site.commit_sha);
    assert.equal(new URL(url.searchParams.get("page_url")).searchParams.get("lang"), language);
    assert.ok(url.href.length < 4000);
  }
  t.diagnostic(`${contexts.length} item contexts checked across two languages and three forms`);
});
