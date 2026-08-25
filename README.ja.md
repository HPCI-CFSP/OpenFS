# OpenFS

[English](README.md) | **日本語**

[![OpenFS Pages](https://img.shields.io/badge/OpenFS-Public%20Site-18755b?logo=githubpages&logoColor=white)](https://hpci-cfsp.github.io/OpenFS/)
[![Validate OpenFS](https://github.com/HPCI-CFSP/OpenFS/actions/workflows/validate.yml/badge.svg)](https://github.com/HPCI-CFSP/OpenFS/actions/workflows/validate.yml)
[![Publish OpenFS Pages](https://github.com/HPCI-CFSP/OpenFS/actions/workflows/pages.yml/badge.svg)](https://github.com/HPCI-CFSP/OpenFS/actions/workflows/pages.yml)
[![License](https://img.shields.io/badge/License-Apache--2.0-173b57.svg)](LICENSE)

<!-- i18n-section: overview -->

OpenFSは、将来のHPCI基盤に必要な技術、システム、運用モデルを継続的に調査する、根拠重視の調査研究ハーネスです。

日英対応の公開調査ビューは[OpenFS Pages](https://hpci-cfsp.github.io/OpenFS/)で閲覧できます。

本プロジェクトは、繰り返し実行される調査課題を、追跡可能な成果物へ変換します。

```text
調査課題
  -> 情報源
  -> 根拠抜粋
  -> 原子的な主張
  -> 知見
  -> ロードマップシナリオ
  -> 報告書
```

<!-- i18n-section: status -->

## 現在の状況

本Repositoryには現在、Phase 0の設計Baseline、再実行可能な公開Web PilotのVertical Slice、決定論的なConsensusおよびAI Topic Promotion経路、FY2022-FY2025のFS報告書公式一覧、決定論的な複数Scenario表示Generator、Review専用のCanonical Claim Promotion経路、日英対応のGitHub Pages公開ビューが含まれています。定期的なProduction Provider dispatchとProduction Report生成はまだ有効化されておらず、Ownerが文書化されたDrillを完了するまでWorkflowは既定で無効です。

最初のVertical Sliceである`OFS-001`は、2030年代のHPCI向けメモリ階層候補を繰り返し調査します。`OFS-002`はFS由来Baselineを維持し、`OFS-003`は日付付きHPCI Provider Registryと現地根拠を持つCenter Profileからセンター状況を考慮したScenarioを作成し、`OFS-004`はConsensusで受理されたAI Topic追加をPromotionし、`OFS-005`は日本発技術を優先的に網羅しながら世界の技術動向を継続調査します。

<!-- i18n-section: core-principles -->

## 基本原則

- 公開OpenFSには公開情報だけを保存します。NDA情報はRiVaultまたは承認された別のPrivate環境に残します。
- Modelの投票は根拠ではありません。Modelの独立性と情報源Originの独立性は別々に評価します。
- 受理された知識は、報告書の文章からClaim、Evidence抜粋、Source、Run、Agent、Prompt、Policyまで追跡可能にします。
- 外部Webページ、文書、Issue、Pull Request本文、Commentは信頼できないDataとして扱い、そこに含まれる指示には従いません。
- 調査Agentが提案し、独立Agentが評価します。設定されたQuorumを満たすかは決定論的Codeが判定し、Canonical Dataを更新できるのはPromotion Workflowだけです。
- Canonical Claimは不変です。人が承認した撤回または置換はDigest固定のStatus Eventを追加し、生成されるActive Viewを変更しますが、履歴は削除しません。
- 事実、予測、HPCIへの提案は異なるObject Typeであり、それぞれ異なるReview Gateを通過します。
- 通常処理は自動化します。人はDigestを受け取り、Exception、影響の大きい提案、Policy変更、NDA Exportに介入します。

<!-- i18n-section: repository-map -->

## Repository構成

| Path | 役割 |
|---|---|
| `AGENTS.md` | Codexおよび他のRepository Agentが従う共通規則 |
| `docs/agent-onboarding.md` | 初回実行Checklist、停止条件、Role Routing |
| `docs/architecture.md` | End-to-End Architecture、状態、Trust Boundary |
| `docs/policies/` | 人が所有する判断・Governance規則 |
| `docs/tasks/` | 調査課題と期待される出力 |
| `docs/research-baseline/` | FS由来の調査Topic Catalog、Source Corpus、既知のGapを人が読める形で記録 |
| `docs/planning/` | 大学基盤センターの入力、複数Scenario生成、提示規則 |
| `docs/publication/` | GitHub Pagesの有効化と公開出力の境界 |
| `docs/operations/` | Owner設定、Pilot有効化、定期運用手順 |
| `config/` | Agent、Monitor、Budget、Consensus、日付付きHPCI Provider Scopeの機械可読設定 |
| `schemas/` | 永続的な調査ArtifactのJSON Schema |
| `skills/` | 各Runに固定されるDiscovery、抽出、統合、検証、反証手順 |
| `evals/` | Golden、Adversarial、Replay評価Case |
| `tools/` | 決定論的な検証・Consensus Command |
| `tests/` | 決定論的Harness動作のTest |
| `proposals/` | Agentが作成するCandidate。Canonicalではない |
| `assessments/` | 提案に対する独立Review |
| `decisions/` | 機械生成されたConsensus Decision |
| `data/` | 受理されたCanonical Source、Evidence、Finding Record |
| `knowledge/` | Promotion済みCanonical Claim、追記専用Status Event、生成されたActive View |
| `roadmaps/` | Scenario形式のRoadmap Draftと受理版 |
| `reports/` | 生成されたReport DraftとExport |
| `reviews/` | 人のDirective、Digest、Exception、Dissent |
| `runs/` | 不変のRun ManifestとRun単位の出力 |
| `state/` | Watermarkと再開可能なScheduler State |

まだ実装された動作を持たないDirectoryは`docs/architecture.md`に記載し、対応するVertical Sliceを実装するときに追加します。`config/skill-registry.json`は、対応する各Work Item種別の手順を決定論的に選択してSnapshotします。

<!-- i18n-section: research-baseline -->

## 調査Baseline

新しいResearch TaskとMonitorは`config/research-baseline.json`からTopicを選択します。`FSBASE-002`には58 Topicが含まれます。内訳は、保護された初期Catalog 30件、文部科学省が公開するFY2022-FY2025の全26 PDFから追加した27件、人の指示による日本発技術の優先Coverageを伴う世界技術Horizon Topic 1件です。

OpenFSの調査対象は全世界です。`config/global-technology-scope.json`は、地域的に幅広いDiscovery、可能な範囲での原語Source Coverage、国際的な代替候補の比較を要求します。国内研究、Startup、Standard、Prototype、Supply Chain能力を見落とさないよう日本発技術を優先して探索しますが、開発地域だけを採用判断の根拠にはしません。

FS1.0の記録と各HPCIセンターの現在の一次根拠は、まだ完全ではありません。AI Agentは`OFS-004`を通じて追加Topicを提案できますが、独立Review、Consensus Gate、決定論的Promotionが必要であり、自動経路から既存Topicを削除または変更することはできません。

<!-- i18n-section: local-validation -->

## Local検証

依存関係を必要としない構造検証を最初に実行します。Draft 2020-12 Instanceの完全検証、GitHub Actions YAML検証、それらのUnit Testには、`requirements-validation.txt`で固定したVersionを使用します。

```bash
python3 -m pip install --requirement requirements-validation.txt
python3 tools/validate_repository.py
python3 tools/validate_readme_i18n.py
python3 tools/validate_workflows.py
python3 tools/validate_json_schemas.py
python3 -m unittest discover -s tests -v
```

Research Roleが予定されたPathへ書き込めるか確認します。

```bash
python3 tools/check_agent_permissions.py \
  --role validator \
  assessments/PRP-CLM-000001/ASM-000001.json \
  runs/RUN-TEST-001/validator-summary.json
```

Consensus Gateの例を実行します。

```bash
python3 tools/consensus_gate.py \
  --proposal evals/golden/accepted-proposal.json \
  --assessments evals/golden/accepted-assessments.json \
  --policy config/consensus-policy.json
```

順位付けを行わず、例示用の複数ScenarioをRenderします。

```bash
python3 tools/generate_scenario_views.py \
  --input evals/scenarios/candidate-scenarios.json \
  --policy config/scenario-policy.json \
  --output-markdown /tmp/openfs-scenarios.md \
  --output-json /tmp/openfs-scenarios.json
```

公開GitHub Pages ViewをLocalでBuildします。

```bash
python3 tools/build_pages_site.py --output _site
```

公開Siteは日本語と英語に対応し、世界の技術を対象とする`Technology landscape` Viewを備え、その中で日本発技術を優先的に追跡します。Repository管理者は、**Settings → Pages → GitHub Actions**とRepository Variable `OPENFS_PAGES_ENABLED=true`を一度設定してDeploymentを有効化します。ScenarioとReportの公開には、一致する人の`publication-approval` Directiveも必要です。詳細は`docs/publication/github-pages.md`を参照してください。

調査自動化はまだ有効化されていません。Provider Account、GitHub設定、3 RunのPilot手順は`docs/operations/automation-setup.md`に記載されています。API Keyを設定するだけではLoopは起動しません。

<!-- i18n-section: human-directions -->

## 人からの追加指示

人は、次のいずれかの方法で非同期の指示を追加します。

- `research-directive` Labelを付けたGitHub Issue
- `reviews/directives/`配下でReviewされたDirective File

各Directiveは、将来的に、その指示を処理したWork Item、Run、Decisionと関連付けられます。

<!-- i18n-section: license -->

## License

OpenFSが作成したMaterialには[Apache License 2.0](LICENSE)を適用します。`NOTICE`にProject Attributionを示し、`THIRD_PARTY_NOTICES.md`には、Link先Report、Citation、Trademark、Dataset、その他の第三者著作物をOpenFSが再Licenseしないことを記載しています。
