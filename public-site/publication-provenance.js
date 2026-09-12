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
      publicTitle: "3. 公開リポジトリ", publicText: "この成果物のPages配信元として指定された公開コミットです。",
      deployTitle: "4. Pagesデプロイ", deployText: "この公開コミットのPages配信に対応するActions実行です。配信の成否はリンク先の実行結果で確認してください。",
      previewPublicText: "PRプレビューの生成元コミットです。mainへの取り込みや本番公開を示すものではありません。",
      previewTitle: "4. PRプレビュー", previewText: "レビュー用プレビュー成果物を生成したActions実行です。本番Pagesへのデプロイではありません。",
      pendingPublicText: "公開コミットと配信状態の対応をまだ確認できません。",
      pendingTitle: "4. 配信状態未確認", pendingText: "本番配信またはPRプレビューに対応する来歴が未確認です。ページが表示されることだけでは本番公開の根拠になりません。",
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
      publicTitle: "3. Public repository", publicText: "The public commit selected as the source of this Pages publication artifact.",
      deployTitle: "4. Pages deployment", deployText: "The Actions run associated with Pages publication of this source commit. Check the linked run for the deployment outcome.",
      previewPublicText: "The source commit for a PR preview. This does not establish a merge into main or production publication.",
      previewTitle: "4. PR preview", previewText: "The Actions run that generated a review preview artifact. This is not a production Pages deployment.",
      pendingPublicText: "The relationship between the public commit and publication state is not yet verified.",
      pendingTitle: "4. Publication state unverified", pendingText: "Provenance for production publication or a PR preview is unverified. Displaying this page alone does not establish production publication.",
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
    const preview = publicRepository.status === "preview-source" || deployment.status === "preview-artifact";
    const production = publicRepository.status === "published-source"
      && deployment.status === "serving-this-artifact" && publicRepository.commit
      && publicRepository.commit === deployment.source_commit && deployment.workflow_run_id;
    const publicText = preview ? "previewPublicText" : production ? "publicText" : "pendingPublicText";
    const deployTitle = preview ? "previewTitle" : production ? "deployTitle" : "pendingTitle";
    const deployText = preview ? "previewText" : production ? "deployText" : "pendingText";
    const stages = document.getElementById("provenance-stages");
    stages.replaceChildren(
      stage(text("inputTitle"), text("inputText"), input.commit, input.commit_url, text("commit")),
      stage(text("controlTitle"), text("controlText"), control.commit ? `${control.commit} · ${text("privateCommit")}` : null, null, text("commit")),
      stage(text("publicTitle"), text(publicText), publicRepository.commit || text("pending"), publicRepository.commit_url, text("commit")),
      stage(text(deployTitle), text(deployText), deployment.workflow_run_id ? `#${deployment.workflow_run_id}` : text("pending"), deployment.workflow_run_url, text("workflow"))
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
