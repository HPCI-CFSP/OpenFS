(function () {
  "use strict";

  const script = document.currentScript;
  if (!script) return;

  const config = {
    status: script.dataset.status,
    measurementId: script.dataset.measurementId,
    productionHostname: script.dataset.productionHostname,
    productionPathPrefix: script.dataset.productionPathPrefix,
    storageKey: script.dataset.storageKey,
    privacyPath: script.dataset.privacyPath,
    rootPrefix: script.dataset.rootPrefix || ""
  };
  const copy = {
    ja: {
      notice: "OpenFSは、閲覧状況の把握とサイト改善のため、同意いただいた場合に限りGoogle Analytics 4を使用します。検索語、Feedbackの入力内容、URLのクエリやページ内位置は送信しません。",
      accept: "同意する",
      decline: "同意しない",
      settings: "アクセス解析設定",
      privacy: "プライバシー",
      enabled: "アクセス解析は有効です。",
      disabled: "アクセス解析は無効です。",
      revoke: "同意を取り消す",
      allow: "アクセス解析に同意する"
    },
    en: {
      notice: "OpenFS uses Google Analytics 4 only after consent to understand site usage and improve the site. Search terms, Feedback text, URL queries, and page fragments are not sent.",
      accept: "Allow analytics",
      decline: "Decline",
      settings: "Analytics settings",
      privacy: "Privacy",
      enabled: "Analytics is enabled.",
      disabled: "Analytics is disabled.",
      revoke: "Withdraw consent",
      allow: "Allow analytics"
    }
  };

  function language() {
    const requested = new URLSearchParams(window.location.search).get("lang");
    if (requested === "ja" || requested === "en") return requested;
    try {
      const stored = window.localStorage.getItem("openfs-language");
      if (stored === "ja" || stored === "en") return stored;
    } catch (_error) {}
    return "ja";
  }
  function readConsent() {
    try { return window.localStorage.getItem(config.storageKey); } catch (_error) { return null; }
  }
  function writeConsent(value) {
    try { window.localStorage.setItem(config.storageKey, value); } catch (_error) {}
  }
  function isProduction() {
    return config.status === "enabled"
      && window.location.hostname === config.productionHostname
      && window.location.pathname.startsWith(config.productionPathPrefix);
  }
  function sanitizedLocation() {
    return `${window.location.origin}${window.location.pathname}`;
  }
  function sanitizedReferrer() {
    if (!document.referrer) return "";
    try { const referrer = new URL(document.referrer); return `${referrer.origin}${referrer.pathname}`; } catch (_error) { return ""; }
  }
  function loadGoogleAnalytics() {
    if (!isProduction() || readConsent() !== "granted" || window.__openfsGa4Loaded) return;
    window.__openfsGa4Loaded = true;
    window.dataLayer = window.dataLayer || [];
    window.gtag = function () { window.dataLayer.push(arguments); };
    window.gtag("consent", "default", {
      analytics_storage: "granted",
      ad_storage: "denied",
      ad_user_data: "denied",
      ad_personalization: "denied"
    });
    window.gtag("js", new Date());
    window.gtag("config", config.measurementId, {
      send_page_view: false,
      allow_google_signals: false,
      allow_ad_personalization_signals: false
    });
    window.gtag("event", "page_view", {
      page_location: sanitizedLocation(),
      page_path: window.location.pathname,
      page_title: document.title,
      page_referrer: sanitizedReferrer()
    });
    const tag = document.createElement("script");
    tag.async = true;
    tag.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(config.measurementId)}`;
    tag.dataset.openfsAnalytics = "ga4";
    document.head.append(tag);
  }
  function removeBanner() {
    document.getElementById("openfs-analytics-consent")?.remove();
  }
  function setConsent(value) {
    writeConsent(value);
    removeBanner();
    if (value === "granted") loadGoogleAnalytics();
    else if (window.gtag) window.gtag("consent", "update", {analytics_storage: "denied"});
    renderPrivacyStatus();
  }
  function showConsentBanner() {
    if (!isProduction() || readConsent()) return;
    const lang = language();
    const banner = document.createElement("aside");
    banner.id = "openfs-analytics-consent";
    banner.className = "analytics-consent";
    banner.setAttribute("aria-label", copy[lang].settings);
    const text = document.createElement("p");
    text.textContent = copy[lang].notice;
    const actions = document.createElement("div");
    const accept = document.createElement("button");
    accept.type = "button";
    accept.className = "button-primary";
    accept.textContent = copy[lang].accept;
    accept.addEventListener("click", () => setConsent("granted"));
    const decline = document.createElement("button");
    decline.type = "button";
    decline.textContent = copy[lang].decline;
    decline.addEventListener("click", () => setConsent("denied"));
    const privacy = document.createElement("a");
    privacy.href = `${config.privacyPath}?lang=${lang}`;
    privacy.textContent = copy[lang].privacy;
    actions.append(accept, decline, privacy);
    banner.append(text, actions);
    document.body.append(banner);
  }
  function addSettingsLink() {
    const lang = language();
    const container = document.createElement("div");
    container.className = "analytics-settings-link";
    const link = document.createElement("a");
    link.href = `${config.privacyPath}?lang=${lang}`;
    link.textContent = copy[lang].settings;
    container.append(link);
    document.body.append(container);
  }
  function renderPrivacyLanguage() {
    if (document.body.dataset.page !== "privacy") return;
    const lang = language();
    document.documentElement.lang = lang;
    document.querySelectorAll("[data-privacy-language]").forEach((element) => {
      element.hidden = element.dataset.privacyLanguage !== lang;
    });
    document.querySelectorAll("[data-language]").forEach((button) => {
      const selected = button.dataset.language === lang;
      button.setAttribute("aria-pressed", String(selected));
      button.classList.toggle("active", selected);
      button.addEventListener("click", () => {
        const url = new URL(window.location.href);
        url.searchParams.set("lang", button.dataset.language);
        try { window.localStorage.setItem("openfs-language", button.dataset.language); } catch (_error) {}
        window.location.assign(url);
      });
    });
  }
  function renderPrivacyStatus() {
    const lang = language();
    const consent = readConsent();
    document.querySelectorAll("[data-analytics-consent-status]").forEach((root) => {
      root.replaceChildren();
      const status = document.createElement("p");
      status.textContent = consent === "granted" ? copy[lang].enabled : copy[lang].disabled;
      const button = document.createElement("button");
      button.type = "button";
      button.textContent = consent === "granted" ? copy[lang].revoke : copy[lang].allow;
      button.addEventListener("click", () => setConsent(consent === "granted" ? "denied" : "granted"));
      root.append(status, button);
    });
  }

  renderPrivacyLanguage();
  renderPrivacyStatus();
  if (isProduction()) {
    addSettingsLink();
    if (readConsent() === "granted") loadGoogleAnalytics();
    else showConsentBanner();
  }
})();
