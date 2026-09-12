(function () {
  "use strict";

  const scriptUrl = document.currentScript?.src || window.location.href;
  const siteRoot = new URL("./", scriptUrl);
  let provenance = window.OPENFS_PUBLIC_DATA?.publication_provenance || null;

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
    const generated = new Date(provenance?.generated_at || "");
    const ja = language() === "ja";
    const date = Number.isNaN(generated.getTime()) ? (ja ? "未記録" : "Not recorded") : new Intl.DateTimeFormat("sv-SE", {
      timeZone: "Asia/Tokyo", year: "numeric", month: "2-digit", day: "2-digit",
      hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23"
    }).format(generated).replace(" ", "-") + " JST";
    const repository = provenance?.public_repository || {};
    const deployment = provenance?.pages_deployment || {};
    const matching = /^[0-9a-f]{40}$/.test(repository.commit || "")
      && repository.commit === deployment.source_commit && deployment.workflow_run_id;
    const production = matching && repository.status === "published-source" && deployment.status === "serving-this-artifact";
    const preview = matching && repository.status === "preview-source" && deployment.status === "preview-artifact";
    const revision = production ? `${ja ? "公開版" : "Public revision"} ${repository.commit.slice(0, 7)}`
      : preview ? `PR ${ja ? "プレビュー" : "preview"} ${repository.commit.slice(0, 7)}`
      : (ja ? "本番反映未確認" : "Production status unverified");
    const label = `${ja ? "サイト生成日時" : "Site generated"} ${date} · ${revision}`;
    if (link.textContent !== label) link.textContent = label;
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
      const matchingBundle = !fallback?.bundle_id || payload?.bundle_id === fallback.bundle_id;
      return payload?.schema_version === "0.1.0" && matchingBundle ? payload : fallback;
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
  if (updated) observer.observe(updated, {attributes: true, attributeFilter: ["href", "target", "rel"], childList: true, subtree: true});
  linkHeader();
  operationalNavigation();
  trackHeaderOffset();
  deploymentProvenance().then((payload) => { provenance = payload; linkHeader(); });

  window.OpenFSPublication = {deploymentProvenance, linkHeader, provenanceUrl};
})();
