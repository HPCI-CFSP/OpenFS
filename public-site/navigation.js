(function () {
  "use strict";

  const nav = document.querySelector("nav.tabs");
  if (!nav || nav.querySelector(".nav-more")) return;

  const reportLinks = [...nav.querySelectorAll("a")].filter((link) =>
    link.dataset.i18n === "navReports" || /#reports(?:$|[?&])/.test(link.getAttribute("href") || "")
  );
  reportLinks.forEach((link) => link.remove());

  const secondaryLinks = [...nav.querySelectorAll("a")].filter((link) =>
    ["navGlossary", "navSearch"].includes(link.dataset.i18n) || link.hasAttribute("data-feedback-nav")
  );
  if (!secondaryLinks.length) return;

  const more = document.createElement("details");
  more.className = "nav-more";
  const summary = document.createElement("summary");
  summary.setAttribute("data-ja", "その他");
  summary.setAttribute("data-en", "More");
  summary.setAttribute("aria-haspopup", "menu");
  const menu = document.createElement("div");
  menu.className = "nav-more-menu";
  menu.setAttribute("role", "menu");
  secondaryLinks.forEach((link) => {
    link.setAttribute("role", "menuitem");
    menu.appendChild(link);
  });
  more.append(summary, menu);
  if (secondaryLinks.some((link) =>
    link.classList.contains("active") || link.getAttribute("aria-current") === "page"
  )) {
    more.classList.add("active");
  }
  nav.appendChild(more);

  function updateLanguage() {
    const language = document.body.dataset.language === "en" || document.documentElement.lang === "en" ? "en" : "ja";
    summary.textContent = language === "en" ? summary.dataset.en : summary.dataset.ja;
    summary.setAttribute("aria-label", language === "en" ? "More pages" : "その他のページ");
  }

  function positionMenu() {
    if (!more.open) return;
    const box = summary.getBoundingClientRect();
    const width = Math.min(220, window.innerWidth - 24);
    const left = Math.max(12, Math.min(box.right - width, window.innerWidth - width - 12));
    menu.style.setProperty("--nav-menu-left", `${left}px`);
    menu.style.setProperty("--nav-menu-top", `${box.bottom + 6}px`);
  }

  more.addEventListener("toggle", positionMenu);
  window.addEventListener("resize", positionMenu);
  window.addEventListener("scroll", positionMenu, {passive: true});
  document.addEventListener("click", (event) => {
    if (more.open && !more.contains(event.target)) more.open = false;
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && more.open) {
      more.open = false;
      summary.focus();
    }
  });
  document.querySelectorAll("[data-language]").forEach((button) => {
    button.addEventListener("click", () => setTimeout(updateLanguage, 0));
  });
  updateLanguage();
})();
