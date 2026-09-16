(function () {
  "use strict";
  const nav = document.querySelector("[data-shared-navigation]");
  if (!nav) return;
  const root = new URL("./", document.currentScript.src);
  const menus = [...nav.querySelectorAll("details")];
  function positionMenu(menu) {
    if (!menu.open) return;
    const box = menu.querySelector("summary").getBoundingClientRect();
    const panel = menu.querySelector(".nav-more-menu");
    const width = Math.min(220, window.innerWidth - 24);
    panel.style.setProperty("--nav-menu-left", `${Math.max(12, Math.min(box.right - width, window.innerWidth - width - 12))}px`);
    panel.style.setProperty("--nav-menu-top", `${box.bottom + 6}px`);
  }
  function update() {
    const lang = new URLSearchParams(location.search).get("lang") || document.documentElement.lang;
    const language = lang === "en" ? "en" : "ja";
    nav.setAttribute("aria-label", language === "ja" ? "サイト内ナビゲーション" : "Site navigation");
    nav.querySelectorAll("[data-ja]").forEach((node) => { node.textContent = node.dataset[language]; });
    const localPath = location.pathname.slice(root.pathname.length);
    nav.querySelectorAll("a").forEach((link) => {
      const url = new URL(link.href);
      url.searchParams.set("lang", language);
      link.href = url.href;
      const target = url.pathname.slice(root.pathname.length);
      const active = target ? localPath.startsWith(target) : (!localPath || localPath === "index.html") && (location.hash || "#overview") === url.hash;
      link.classList.toggle("active", active);
      if (active) link.setAttribute("aria-current", "page");
      else link.removeAttribute("aria-current");
    });
    menus.forEach((menu) => { menu.classList.toggle("active", Boolean(menu.querySelector("a.active"))); positionMenu(menu); });
  }
  menus.forEach((menu) => {
    menu.addEventListener("toggle", () => {
      if (menu.open) menus.filter((other) => other !== menu).forEach((other) => { other.open = false; });
      positionMenu(menu);
    });
    menu.querySelectorAll("a").forEach((link) => link.addEventListener("click", () => { menu.open = false; }));
  });
  document.addEventListener("click", (event) => {
    menus.forEach((menu) => { if (!menu.contains(event.target)) menu.open = false; });
    if (event.target.closest("button[data-language]")) setTimeout(update, 0);
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") menus.filter((menu) => menu.open).forEach((menu) => { menu.open = false; menu.querySelector("summary").focus(); });
  });
  ["resize", "scroll"].forEach((event) => window.addEventListener(event, () => menus.forEach(positionMenu), {passive: true}));
  ["hashchange", "popstate"].forEach((event) => window.addEventListener(event, update));
  new MutationObserver(update).observe(document.documentElement, {attributes: true, attributeFilter: ["lang"]});
  update();
})();
