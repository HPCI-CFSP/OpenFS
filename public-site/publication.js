(function () {
  "use strict";

  const scriptUrl = document.currentScript?.src || window.location.href;
  const siteRoot = new URL("./", scriptUrl);

  function language() {
    const requested = new URLSearchParams(window.location.search).get("lang");
    if (requested === "ja" || requested === "en") return requested;
    return document.documentElement.lang === "en" ? "en" : "ja";
  }

  function provenanceUrl() {
    const url = new URL("provenance/", siteRoot);
    url.searchParams.set("lang", language());
    return url.href;
  }

  function linkHeader() {
    const link = document.getElementById("site-updated");
    if (!link) return;
    const target = provenanceUrl();
    if (link.href !== target) link.href = target;
    if (link.target !== "_self") link.target = "_self";
    if (link.hasAttribute("rel")) link.removeAttribute("rel");
    link.title = language() === "ja" ? "公開来歴を表示" : "View publication provenance";
  }

  function operationalNavigation() {
    const nav = document.querySelector("nav.tabs");
    if (!nav) return;
    const target = new URL("analytics/operational-workloads/", siteRoot);
    target.searchParams.set("lang", language());
    let link = [...nav.querySelectorAll("a")].find((item) => new URL(item.href).pathname === target.pathname);
    if (!link) {
      link = document.createElement("a");
      const catalog = [...nav.querySelectorAll("a")].find((item) => new URL(item.href).hash === "#catalog");
      if (catalog) catalog.after(link);
      else nav.prepend(link);
    }
    link.href = target.href;
    link.textContent = language() === "ja" ? "実運用分析" : "Operational analysis";
    if (window.location.pathname === target.pathname) {
      link.classList.add("active");
      link.setAttribute("aria-current", "page");
    }
  }

  function trackHeaderOffset() {
    const header = document.querySelector(".app-header");
    if (!header || typeof ResizeObserver === "undefined") return;
    const update = () => document.documentElement.style.setProperty(
      "--openfs-header-offset", `${Math.ceil(header.getBoundingClientRect().height) + 12}px`
    );
    update();
    new ResizeObserver(update).observe(header);
  }

  async function deploymentProvenance() {
    const fallback = window.OPENFS_PUBLIC_DATA?.publication_provenance || null;
    try {
      const url = new URL("data/openfs-deployment.json", siteRoot);
      url.searchParams.set("_", String(Date.now()));
      const response = await fetch(url, {cache: "no-store"});
      if (!response.ok) return fallback;
      const payload = await response.json();
      return payload?.schema_version === "0.1.0" ? payload : fallback;
    } catch (_error) {
      return fallback;
    }
  }

  document.addEventListener("click", (event) => {
    if (event.target.closest?.("[data-language]")) window.setTimeout(() => {
      linkHeader();
      operationalNavigation();
    }, 0);
  });
  const observer = new MutationObserver(linkHeader);
  const updated = document.getElementById("site-updated");
  if (updated) observer.observe(updated, {attributes: true, attributeFilter: ["href", "target", "rel"]});
  linkHeader();
  operationalNavigation();
  trackHeaderOffset();

  window.OpenFSPublication = {deploymentProvenance, linkHeader, provenanceUrl};
})();
