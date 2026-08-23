(function () {
  "use strict";

  const data = window.OPENFS_PUBLIC_DATA;
  if (!data) {
    document.body.textContent = "OpenFS public data is unavailable.";
    return;
  }

  const domainLabels = {
    "architecture": "Architecture",
    "system-software": "System software",
    "applications": "Applications",
    "cross-cutting": "Cross-cutting"
  };
  let activeDomain = "all";

  function setText(id, value) {
    const element = document.getElementById(id);
    if (element) element.textContent = value;
  }

  setText("as-of", `As of ${data.as_of}`);
  setText("metric-topics", data.baseline.topic_count);
  setText("metric-domestic", data.domestic_technology.categories.length);
  setText("metric-scenarios", data.scenarios.length);
  setText("metric-reports", data.reports.length);
  setText("baseline-id", data.baseline.baseline_id);
  setText("baseline-detail", `revision ${data.baseline.catalog_revision} / official sources ${data.baseline.official_source_count}`);
  setText("gap-summary", `Open gaps: ${data.baseline.open_gap_ids.join(", ") || "none"}`);
  setText("domestic-rule", data.domestic_technology.scope_rule);
  setText("license-status", `License: ${data.publication.license_status} (${data.publication.recommended_license} recommended)`);

  const categoryRoot = document.getElementById("domestic-categories");
  data.domestic_technology.categories.forEach((category, index) => {
    const item = document.createElement("article");
    item.className = "category-item";
    const number = document.createElement("span");
    number.textContent = `AREA ${String(index + 1).padStart(2, "0")}`;
    const text = document.createElement("p");
    text.textContent = category;
    item.append(number, text);
    categoryRoot.appendChild(item);
  });

  function renderTopics() {
    const query = document.getElementById("topic-search").value.trim().toLocaleLowerCase("ja");
    const root = document.getElementById("topic-rows");
    root.replaceChildren();
    const filtered = data.topics.filter((topic) => {
      const domainMatch = activeDomain === "all" || topic.domain === activeDomain;
      const searchText = [topic.topic_id, topic.title_ja, ...topic.research_questions].join(" ").toLocaleLowerCase("ja");
      return domainMatch && (!query || searchText.includes(query));
    });

    filtered.forEach((topic) => {
      const row = document.createElement("tr");
      const idCell = document.createElement("td");
      idCell.className = "topic-id";
      idCell.textContent = topic.topic_id;
      const titleCell = document.createElement("td");
      titleCell.textContent = topic.title_ja;
      if (topic.domestic_scope) {
        const domestic = document.createElement("span");
        domestic.className = "tag domestic";
        domestic.textContent = "国内技術";
        titleCell.append(" ", domestic);
      }
      const domainCell = document.createElement("td");
      domainCell.textContent = domainLabels[topic.domain];
      const statusCell = document.createElement("td");
      statusCell.textContent = topic.status;
      const cadenceCell = document.createElement("td");
      cadenceCell.textContent = topic.review_cadence;
      const originCell = document.createElement("td");
      const origin = document.createElement("span");
      origin.className = `tag${topic.catalog_origin === "ai-consensus" ? " ai" : ""}`;
      origin.textContent = topic.catalog_origin;
      originCell.appendChild(origin);
      row.append(idCell, titleCell, domainCell, statusCell, cadenceCell, originCell);
      root.appendChild(row);
    });
    document.getElementById("topic-empty").hidden = filtered.length !== 0;
  }

  document.querySelectorAll("[data-domain]").forEach((button) => {
    button.addEventListener("click", () => {
      activeDomain = button.dataset.domain;
      document.querySelectorAll("[data-domain]").forEach((item) => item.classList.toggle("active", item === button));
      renderTopics();
    });
  });
  document.getElementById("topic-search").addEventListener("input", renderTopics);
  renderTopics();

  const scenarioRoot = document.getElementById("scenario-list");
  data.scenarios.forEach((scenario) => {
    const item = document.createElement("article");
    item.className = "scenario-item";
    const title = document.createElement("h3");
    title.textContent = `${scenario.scenario_id} | ${scenario.title_ja}`;
    const objective = document.createElement("p");
    objective.textContent = scenario.objective;
    item.append(title, objective);
    scenarioRoot.appendChild(item);
  });
  document.getElementById("scenario-empty").hidden = data.scenarios.length !== 0;

  const reportRoot = document.getElementById("report-list");
  data.reports.forEach((report) => {
    const item = document.createElement("article");
    item.className = "report-item";
    const title = document.createElement("h3");
    title.textContent = report.title;
    const meta = document.createElement("p");
    meta.textContent = `${report.report_id} / ${report.as_of} / ${report.status}`;
    item.append(title, meta);
    reportRoot.appendChild(item);
  });
  document.getElementById("report-empty").hidden = data.reports.length !== 0;
})();
