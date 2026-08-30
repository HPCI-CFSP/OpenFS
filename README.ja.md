# OpenFS

[English](README.md) | **日本語**

[![OpenFS Pages](https://img.shields.io/badge/OpenFS-Public%20Site-18755b?logo=githubpages&logoColor=white)](https://hpci-cfsp.github.io/OpenFS/)
[![Validate OpenFS](https://github.com/HPCI-CFSP/OpenFS/actions/workflows/validate.yml/badge.svg)](https://github.com/HPCI-CFSP/OpenFS/actions/workflows/validate.yml)
[![Publish OpenFS Pages](https://github.com/HPCI-CFSP/OpenFS/actions/workflows/pages.yml/badge.svg)](https://github.com/HPCI-CFSP/OpenFS/actions/workflows/pages.yml)
[![License](https://img.shields.io/badge/License-Apache--2.0-173b57.svg)](LICENSE)

<!-- i18n-section: overview -->

OpenFSは、将来のHPCI基盤に必要な技術、システム、運用モデルを継続的に調査する、根拠を重視した調査研究ハーネスです。

日英対応の公開調査ビューは[OpenFS Pages](https://hpci-cfsp.github.io/OpenFS/)で閲覧できます。

本プロジェクトは、繰り返し実行される調査課題を、追跡可能な成果物へ変換します。

```text
調査課題
  -> 情報源
  -> 根拠抜粋
  -> 単一の事実または論点に分解した主張
  -> 知見
  -> ロードマップとシステム整備計画案
  -> 報告書
```

<!-- i18n-section: status -->

## 現在の状況

本リポジトリには現在、フェーズ0の設計基準、公開ウェブ調査フローの再現可能な試験実装、決定論的な合意判定（Consensus Gate）、AIが新しい調査項目を提案する仕組み、2022～2025年度のFS報告書公式一覧、複数のシステム整備計画案を生成・表示する仕組み、レビューを経た主張を正式な主張（Canonical Claim）へ昇格させる経路、日本語・英語対応のGitHub Pages公開サイトが含まれています。

共通形式で作成した最初の暫定ロードマップ6本は、計算ノード、メモリ、インターコネクト、性能可搬性、科学ワークロード、HPCIの参照構成を対象としています。公開サイトでは、各ロードマップを四半期単位で表示し、ロードマップ間の比較も提供します。外部AIサービスを定期的に呼び出す本番調査と、本番用報告書の生成は、まだ有効化していません。リポジトリ管理者が文書化された試験手順を完了するまで、関連するGitHub Actionsワークフローは既定で無効です。

最初に実装した調査フローである`OFS-001`は、2030年代のHPCI向けメモリ階層候補を継続的に調査します。`OFS-002`はFS報告書から作成した調査基準を維持します。`OFS-003`は、基準日を記録したHPCI資源提供機関台帳と、項目ごとに公開根拠を示すセンタープロファイルを使い、各センターの状況を考慮した計画案を作成します。`OFS-004`は、合意判定（Consensus Gate）で受理されたAI提案の調査項目を調査カタログへ追加します。`OFS-005`は、日本発の技術を優先的に確認しつつ、世界の技術動向を継続調査します。

<!-- i18n-section: core-principles -->

## 基本原則

- 公開版のOpenFSには公開情報だけを保存します。NDA情報はRiVaultまたは承認された別の非公開環境に残します。
- AIモデルの投票結果そのものは根拠になりません。モデルの独立性と、情報源の発行主体の独立性を別々に評価します。
- 受理した知識は、報告書の文章から主張、根拠抜粋、情報源、調査実行、エージェント、プロンプト、適用方針まで追跡できるようにします。
- 外部ウェブページ、文書、GitHub Issue、プルリクエスト本文、コメントは、信頼できないデータとして扱います。そこに記載された指示を、OpenFSの実行指示として解釈しません。
- 調査エージェントが提案し、独立したエージェントが評価します。必要な定足数を満たすかは決定論的なプログラムが判定し、正式データを更新できるのは昇格ワークフローだけです。
- 正式データとして扱う主張（Canonical Claim）は書き換えません。人が撤回または置換を承認した場合は、ダイジェストで固定した状態変更記録を追記し、生成される現行ビューを更新します。過去の記録は削除しません。
- 事実、予測、HPCIへの提案を異なる種類の成果物として管理し、それぞれに適したレビューを行います。
- 定型処理は自動化します。人は定期要約を確認し、例外、影響の大きい提案、方針変更、NDA情報を承認済みの環境間で移す必要がある場合に介入します。
- 公開ウェブの検索、匿名かつ読み取り専用の取得、ローカルのシェル実行、依存パッケージの導入、GitHubへの反映を別々の権限として扱います。リポジトリ内の規則だけでは通信遮断を証明できません。検証済みの実行プロファイルで`python3 tools/check_research_web_security.py --require-production-profile`に合格するまで、無人の本番調査は有効化しません。

<!-- i18n-section: repository-map -->

## リポジトリ構成

| パス | 役割 |
|---|---|
| `AGENTS.md` | Codexおよび他のリポジトリエージェントが従う共通規則 |
| `docs/agent-onboarding.md` | 初回実行時のチェックリスト、停止条件、役割分担 |
| `docs/architecture.md` | 処理全体の構成、状態遷移、信頼境界 |
| `docs/policies/` | 人が管理する判断方針とガバナンス規則 |
| `docs/policies/language-and-terminology.md` | 公開文の日英表現、用語、一元管理に関する規則 |
| `docs/security/research-web-security-model.md` | ウェブ調査の権限境界、実行環境の制御、残存リスク |
| `docs/tasks/` | 調査課題と期待される出力 |
| `docs/research-baseline/` | FS報告書から作成した調査項目一覧、情報源集、既知の不足事項 |
| `docs/planning/` | 大学基盤センターの入力情報、複数計画案の生成方法、提示規則 |
| `docs/publication/` | GitHub Pagesの有効化と公開出力の境界 |
| `docs/operations/` | 管理者による設定、試験運用の有効化、定期運用の手順 |
| `config/` | エージェント、モニター、予算、合意判定、基準日付きのHPCI資源提供範囲に関する機械可読設定 |
| `config/execution-security-profiles.json` | 実行環境の制御と本番運用の適格性を示す検証根拠。現在、適格なプロファイルはありません |
| `schemas/` | 保存する調査成果物のJSONスキーマ |
| `skills/` | 各調査実行に固定する情報探索、抽出、統合、検証、反証の手順 |
| `evals/` | 正常系、攻撃的入力、再実行の評価事例 |
| `tools/` | 決定論的な検証コマンドと合意判定コマンド |
| `tests/` | ハーネスの決定論的な動作を確認するテスト |
| `proposals/` | エージェントが作成した候補。正式データではない |
| `assessments/` | 提案に対する独立レビュー |
| `decisions/` | 機械生成した合意判定結果 |
| `data/` | 受理した正式な情報源、根拠、知見の記録 |
| `knowledge/` | 正式データへ昇格した主張、追記専用の状態変更記録、生成した現行ビュー |
| `knowledge/public/roadmaps/` | 共通スキーマを使い、人による公開承認を受けた日英ロードマップ |
| `knowledge/public/roadmap-reference-data.json` | ロードマップの用語説明と意思決定向け比較表を一元管理する日英データ |
| `knowledge/public/hpci-system-inventory.json` | 年度別のHPCI公開資源と公称仕様。課題募集における提供期間とシステムの運用期間を区別する |
| `knowledge/public/application-performance-forecasts.json` | EEA1アプリケーションを複数の実行規模で予測するためのデータ仕様、準備状況表、検証済み数値予測の掲載先 |
| `knowledge/public/source-catalog-map.json` | 個別URLと正規Topic、ロードマップ、トラックの対応を生成した一覧 |
| `config/catalog-taxonomy.json` | 全ての有効な調査項目とロードマップを6つの公開分類へ割り当て、調査項目の表示コードを定める正本。Pagesの分類フィルタはこのファイルから生成する |
| `config/source-watch-registry.json` | 継続監視する公式ページと、影響を受けるTopic、ロードマップ、モニターの安定した対応表 |
| `roadmaps/` | システム整備計画案とロードマップの草稿・受理版 |
| `reports/` | 生成した報告書の草稿と公開用データ |
| `reviews/` | 人からの指示、定期要約、例外、異論、コミットで固定した合意判定用レビュー一式 |
| `runs/` | 書き換えない調査実行マニフェストと、実行単位の出力 |
| `state/` | 最終処理位置と、再開可能なスケジューラーの状態 |

まだ動作が実装されていないディレクトリは`docs/architecture.md`に記載し、対応する一連処理を実装するときに追加します。`config/skill-registry.json`は、各作業項目に適用する手順を決定論的に選び、その版をスナップショットとして保存します。

<!-- i18n-section: research-baseline -->

## 調査の基準

新しい調査課題とモニターは、`config/research-baseline.json`から調査項目を選択します。`FSBASE-002`は60件の正規Topic IDを保持しています。内訳は、自動処理では削除しない初期項目30件、文部科学省が公開する2022～2025年度の全26件のPDFから追加した27件、人からの指示に基づく3件（世界の技術動向、エージェント型ワークロード向けCPU・ノードアーキテクチャ、LLM推論サービング）です。このうち6件は、別Topicへの統合、Harnessへの移管、計画成果物への移管を後継情報として記録した上で退役し、Pagesには54件の有効な調査項目を表示します。`config/catalog-taxonomy.json`は正規IDを変更せず、全ての有効な調査項目とロードマップを6つの公開分類のいずれか1つへ割り当て、調査項目には分類別の表示コードを付与します。

手動で管理する監視先一覧は、繰り返し確認する公式の索引・ニュースページと、個々の主張を支える根拠資料を分離します。`tools/build_source_catalog_map.py`は、登録済みの公開根拠からURLとTopic、ロードマップ、トラックの対応表を生成します。監視ページの変更は兆候にすぎません。意味のある変更を個別の一次資料で確認し、該当する合意判定（Consensus Gate）を通過するまで公開内容を更新しません。`.github/workflows/emerging-topic-discovery.yml`は新規Topicの探索を毎日起動できますが、試行結果、セキュリティプロファイル、予算、合意判定能力の準備が完了するまではFail-closedで停止します。

OpenFSの調査対象は全世界です。`config/global-technology-scope.json`では、幅広い地域からの情報探索、可能な範囲で原語資料を確認すること、各国の代替候補を比較することを求めています。日本国内の研究、スタートアップ、標準化活動、試作品、サプライチェーンの能力を見落とさないよう、日本発の技術を優先的に探索します。ただし、開発地域だけを採用判断の根拠にはしません。

FS1.0の記録と、各HPCIセンターの現況を示す一次情報は、まだ完全ではありません。AIエージェントは`OFS-004`を通じて調査項目の追加を提案できますが、独立レビュー、合意判定（Consensus Gate）、決定論的な昇格処理が必要です。自動処理から既存の調査項目を削除または変更することはできません。

<!-- i18n-section: local-validation -->

## ローカルでの検証

最初に、追加の依存関係を必要としない構造検証を実行します。JSON Schema Draft 2020-12に準拠した完全なスキーマ検証、GitHub ActionsのYAML検証、それらの単体テストには、`requirements-validation.txt`で固定した版を使用します。

```bash
python3 -m pip install --requirement requirements-validation.txt
python3 tools/validate_repository.py
python3 tools/check_research_web_security.py
python3 tools/check_public_language.py
python3 tools/validate_readme_i18n.py
python3 tools/validate_workflows.py
python3 tools/validate_json_schemas.py
python3 -m unittest discover -s tests -v
```

調査エージェントの役割ごとに、予定したパスへの書き込みが許可されているか確認します。

```bash
python3 tools/check_agent_permissions.py \
  --role validator \
  assessments/PRP-CLM-000001/ASM-000001.json \
  runs/RUN-TEST-001/validator-summary.json
```

合意判定（Consensus Gate）の実行例です。

```bash
python3 tools/consensus_gate.py \
  --proposal evals/golden/accepted-proposal.json \
  --assessments evals/golden/accepted-assessments.json \
  --policy config/consensus-policy.json
```

成果物一式をコミットした後、優先度P0のロードマップに対する独立レビュー一式を作成して評価します。

```bash
python3 tools/build_consensus_review_package.py --base-commit <40-hex-artifact-commit>
python3 tools/evaluate_consensus_review_package.py \
  reviews/consensus-packages/CRP-P0-ROADMAPS-V02/manifest.json
```

評価プログラムが`ready-for-human-decision`を返しても、HPCIに大きな影響を与える採用判断には、
人がレビュー・承認した指示が必要です。各レビュアーはロードマップごとに、コミットで固定した
成果物を一次情報と照合し、明確な確認結果を記録します。詳細は
`docs/operations/independent-roadmap-review.md`を参照してください。

順位付けを行わず、例示用の複数計画案を生成します。

```bash
python3 tools/generate_scenario_views.py \
  --input evals/scenarios/candidate-scenarios.json \
  --policy config/scenario-policy.json \
  --output-markdown /tmp/openfs-scenarios.md \
  --output-json /tmp/openfs-scenarios.json
```

GitHub Pagesの公開サイトをローカルで生成します。

```bash
python3 tools/build_pages_site.py --output _site
```

公開サイトは日本語と英語に対応しています。ロードマップ一覧では、ハードウェア、システムソフトウェア、アプリケーション、分野横断の見通しを検索できます。各詳細ページでは、根拠が示す時期の精度を保った四半期表示を行います。6本のロードマップを比較するページでは、重要なマイルストーン、一次情報の確認状況、未確認事項、依存関係を横断的に表示します。年または半期までしか公表されていない時期は、特定の四半期や出来事の継続期間を推測せず、Q1-Q4または2四半期にまたがる不確実な期間として表示します。技術世代が判断に大きく影響する場合は、根拠に基づいてOpenFSが統合した見通しを、標準化団体やベンダーの行より上に表示します。複数世代が重なる可能性を認め、終了時期が未確認の帯から置換日を推定しません。初期表示は少なくとも2032年頃までとし、それより後の日付を持つ根拠が追加されると、詳細表示と横断比較の列を自動的に延長します。関連用語を選択すると、一元管理した説明と根拠資料を確認できます。また、メモリ、計算、実装、インターコネクト、移植性、評価手法に関する重要な選択肢を共通形式の比較表で確認できます。参照構成の詳細ページでは、2026年度のHPCI公開資源台帳と公称仕様を比較し、年度ごとの課題募集で利用できる期間と、システム自体の運用期間を区別します。ワークロードの詳細ページでは、EEA1の6アプリケーションを、富岳の1、4、32、128、1,024、約10,000ノードに相当する基準規模へ対応付け、公開情報から算出した確度の低い暫定数値予測を表示します。校正と独立検証が完了するまで、この予測は調達評価や性能保証には使用できません。リポジトリ管理者は、**Settings → Pages → GitHub Actions**を選び、リポジトリ変数`OPENFS_PAGES_ENABLED=true`を設定して、公開処理を有効化します。ロードマップ、共通参照データ、補足資料、システム整備計画案、報告書を公開するには、対象に対応する、人が承認した`publication-approval`指示が必要です。詳細は`docs/publication/github-pages.md`を参照してください。

調査の自動化はまだ有効化していません。AIサービスのアカウント、GitHubの設定、3回の試験実行手順は`docs/operations/automation-setup.md`に記載しています。APIキーを設定するだけでは、定期調査は始まりません。

本リポジトリには、取得方針をコードで強制する安全なウェブ取得仲介機能（Safe Web Fetch Broker）と、OpenAI APIおよびAnthropic APIを対象とするレビュー専用のAIサービス実行ワークフロー（Provider Worker）を実装しています。ただし、これらの機能が存在するだけでは、無人調査を本番運用できません。実行プロファイル、AIサービス側の費用上限、管理者による確認、有効な調査モニター、レビュー済みの試験実行が、総合的な運用準備状況の判定基準を満たす必要があります。

公開ウェブの無人調査を有効化する前に、実行環境の管理者は、管理されたウェブ検索、安全な匿名取得、DNSとリダイレクトに対するSSRF対策、シェルからのネットワーク接続の遮断、依存関係取得用通信の分離、GitHubへの公開権限の制限を検証する必要があります。現在登録されている実行プロファイルは、これらの制御を実際に強制している証拠が登録されるまで、本番適格性の判定を意図的に不合格とします。詳細は`docs/security/research-web-security-model.md`を参照してください。

<!-- i18n-section: human-directions -->

## 人からの追加指示

人は、次のいずれかの方法で非同期の指示を追加します。

- `research-directive`ラベルを付けたGitHubのIssue
- `reviews/directives/`配下にある、レビュー済みの人の指示（Directive）ファイル

各指示は、その指示を処理した作業項目、調査実行、判定結果と関連付けます。

閲覧者は、[Feedback](https://hpci-cfsp.github.io/OpenFS/feedback/)または公開調査項目の
Feedbackボタンから、誤りの報告、追加調査のリクエスト、改善提案を送れます。
項目から開いたフォームには、正規の項目ID、公開ページ、表示言語、表示時のビルドの
コミット情報が引き継がれます。投稿にはGitHubアカウントが必要ですが、Pagesに
アクセストークンを埋め込むことはありません。投稿は公開されるため、機密情報、
個人情報、脆弱性の詳細を含めないでください。第三者からのFeedbackは信頼できない
入力として扱い、承認済みのDirectiveやConsensusの票とは区別します。
検証から修正内容の公開までの流れは、[Feedbackの取扱方針](docs/operations/public-feedback.md)
を参照してください。この機能によって投稿の自動振り分けや調査の自動実行が有効に
なることはありません。

<!-- i18n-section: license -->

## ライセンス

OpenFSが作成した資料には[Apache License 2.0](LICENSE)を適用します。`NOTICE`にプロジェクトの帰属表示を示します。`THIRD_PARTY_NOTICES.md`には、リンク先の報告書、引用資料、商標、データセット、その他の第三者著作物にはOpenFSのライセンスを適用しないことを記載しています。
