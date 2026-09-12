(function () {
  "use strict";

  const scriptUrl = document.currentScript?.src || window.location.href;
  const siteRoot = new URL("./", scriptUrl);

  function language() {
    return new URLSearchParams(window.location.search).get("lang") === "en" ? "en" : "ja";
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
    if (event.target.closest?.("[data-language]")) window.setTimeout(linkHeader, 0);
  });
  const observer = new MutationObserver(linkHeader);
  const updated = document.getElementById("site-updated");
  if (updated) observer.observe(updated, {attributes: true, attributeFilter: ["href", "target", "rel"]});
  linkHeader();

  window.OpenFSPublication = {deploymentProvenance, linkHeader, provenanceUrl};
})();
