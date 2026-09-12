(function () {
  "use strict";

  const data = window.OPENFS_PUBLIC_DATA;
  const copy = {
    ja: {
      publicOnly: "公開情報のみ", breadcrumb: "公開来歴", kicker: "公開来歴", title: "公開来歴",
      lead: "調査入力からPages配信までの異なる版を区別して表示します。",
      pagesNote: "GitHub Pagesは独立したGitコミットを作成しません。配信元の公開コミットとActions実行を記録します。",
      consensusNote: "この来歴は再現性のための記録であり、独立したモデルによるConsensus完了を意味しません。",
      footer: "HPCI-CFSP 公開調査ビュー", navOverview: "概要", navCatalog: "調査カタログ", navOperational: "実運用分析", navRoadmaps: "ロードマップ", navScenarios: "システム整備計画案", navReports: "報告書", navGlossary: "専門用語", navSearch: "検索",
      inputTitle: "1. 公開調査入力", inputText: "Pages生成に使用した公開情報側の入力版です。",
      controlTitle: "2. Control生成", controlText: "検証とサイト生成を行った非公開Controlの版です。リポジトリURLは公開しません。",
      publicTitle: "3. 公開リポジトリ", publicText: "現在のPages成果物を格納し、デプロイを起動した公開コミットです。",
      deployTitle: "4. Pagesデプロイ", deployText: "公開コミットを配信したGitHub Actions実行です。ページが表示されている場合、この成果物の配信は完了しています。",
      commit: "コミット", workflow: "Actions実行", pending: "プレビューまたは未デプロイ", privateCommit: "非公開Controlのコミット（リンクなし）", bundleTitle: "公開バンドル", bundleId: "バンドルID", generatedAt: "生成日時", manifest: "公開マニフェスト", viewManifest: "マニフェストを表示", unavailable: "未記録"
    },
    en: {
      publicOnly: "Public information only", breadcrumb: "Publication provenance", kicker: "PUBLICATION PROVENANCE", title: "Publication provenance",
      lead: "Distinguishes the revisions involved from research input through Pages delivery.",
      pagesNote: "GitHub Pages does not create a separate Git commit. OpenFS records the public source commit and the Actions deployment run.",
      consensusNote: "This provenance supports reproducibility; it does not imply completion of Consensus review by independent models.",
      footer: "HPCI-CFSP public research view", navOverview: "Overview", navCatalog: "Research catalog", navOperational: "Operational analysis", navRoadmaps: "Roadmaps", navScenarios: "System planning options", navReports: "Reports", navGlossary: "Glossary", navSearch: "Search",
      inputTitle: "1. Public research input", inputText: "The public-information revision used as the input to Pages generation.",
      controlTitle: "2. Control generation", controlText: "The private Control revision that validated inputs and generated the site. Its repository URL is not disclosed.",
      publicTitle: "3. Public repository", publicText: "The public commit containing the Pages artifact and triggering deployment.",
      deployTitle: "4. Pages deployment", deployText: "The GitHub Actions run that delivered the public commit. If this page is being served, delivery of this artifact completed.",
      commit: "Commit", workflow: "Actions run", pending: "Preview or not yet deployed", privateCommit: "Private Control commit (no link)", bundleTitle: "Publication bundle", bundleId: "Bundle ID", generatedAt: "Generated", manifest: "Public manifest", viewManifest: "View manifest", unavailable: "Not recorded"
    }
  };

  let language = new URLSearchParams(window.location.search).get("lang") === "en" ? "en" : "ja";
  const text = (key) => copy[language][key] || key;
  const el = (tag, className, value) => { const node = document.createElement(tag); if (className) node.className = className; if (value !== undefined) node.textContent = value; return node; };

  function valueLink(label, value, href) {
    const row = el("p", "provenance-value");
    row.append(el("span", "", `${label}: `));
    if (value && href) {
      const link = el("a", "mono-list", value);
      link.href = href; link.target = "_blank"; link.rel = "noopener noreferrer";
      row.append(link);
    } else {
      row.append(el("strong", "mono-list", value || text("unavailable")));
    }
    return row;
  }

  function stage(title, description, value, href, label) {
    const card = el("article", "provenance-stage");
    card.append(el("h3", "", title), el("p", "", description), valueLink(label, value, href));
    return card;
  }

  function renderMetadata(payload) {
    document.documentElement.lang = language;
    document.querySelectorAll("[data-copy]").forEach((node) => { node.textContent = text(node.dataset.copy); });
    document.querySelectorAll("[data-language]").forEach((button) => {
      const active = button.dataset.language === language;
      button.classList.toggle("active", active);
      button.setAttribute("aria-pressed", String(active));
    });
    const input = payload?.public_input || {};
    const control = payload?.control_generation || {};
    const publicRepository = payload?.public_repository || {};
    const deployment = payload?.pages_deployment || {};
    const stages = document.getElementById("provenance-stages");
    stages.replaceChildren(
      stage(text("inputTitle"), text("inputText"), input.commit, input.commit_url, text("commit")),
      stage(text("controlTitle"), text("controlText"), control.commit ? `${control.commit} · ${text("privateCommit")}` : null, null, text("commit")),
      stage(text("publicTitle"), text("publicText"), publicRepository.commit || text("pending"), publicRepository.commit_url, text("commit")),
      stage(text("deployTitle"), text("deployText"), deployment.workflow_run_id ? `#${deployment.workflow_run_id}` : text("pending"), deployment.workflow_run_url, text("workflow"))
    );
    const metadata = document.getElementById("bundle-metadata");
    metadata.replaceChildren();
    [[text("bundleId"), payload?.bundle_id], [text("generatedAt"), payload?.generated_at]].forEach(([label, value]) => {
      const row = el("div", ""); row.append(el("dt", "", label), el("dd", "mono-list", value || text("unavailable"))); metadata.append(row);
    });
    if (payload?.manifest_url) {
      const row = el("div", ""); const link = el("a", "", text("viewManifest")); link.href = payload.manifest_url; link.target = "_blank"; link.rel = "noopener noreferrer";
      row.append(el("dt", "", text("manifest")), el("dd", "")); row.lastElementChild.append(link); metadata.append(row);
    }
    const updated = document.getElementById("site-updated");
    updated.textContent = payload?.public_repository?.commit ? `${text("commit")} ${payload.public_repository.commit.slice(0, 7)}` : text("pending");
    window.OpenFSPublication?.linkHeader();
  }

  async function render() {
    const payload = await window.OpenFSPublication.deploymentProvenance();
    renderMetadata(payload || data.publication_provenance);
  }

  document.querySelectorAll("[data-language]").forEach((button) => button.addEventListener("click", () => {
    language = button.dataset.language;
    const url = new URL(window.location.href); url.searchParams.set("lang", language); history.replaceState(null, "", url);
    render();
  }));
  render();
})();
