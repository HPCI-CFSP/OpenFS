# OpenFS publication boundary

## Repository role

This repository is a public, static distribution of OpenFS research outputs.
It does not execute research agents or promote internal candidates. A reviewed
publication bundle is generated in the control environment and copied here.

The current tree may contain only:

- public structured data under `knowledge/public/`;
- accepted public scenario data under `roadmaps/scenarios/accepted/`;
- public report exports under `reports/exports/`;
- public brand assets under `assets/branding/`;
- the generated site under `public-site/`; and
- repository documentation, Feedback forms, and publication verification files.

Do not add secrets, personal data, NDA material, internal prompts, private run
logs, internal reviews, credentials, or links to post-separation private control
paths. Historical commits before repository separation remain public history and
may contain legacy workflow artifacts that were already public.

## Publication flow

1. Pin the public input commit and control commit.
2. Build and validate a candidate publication bundle in the control environment.
3. Review the bundle manifest, disclosure boundary, rendered Pages artifact, and
   unresolved Coverage Gaps.
4. Copy the bundle into a branch of this repository.
5. Run `.github/verify_publication.py` and review the Pages preview artifact.
6. Merge only with explicit maintainer approval. Production Pages are deployed
   only after the commit reaches `main` and the Pages workflow succeeds.

After bundle verification, the preview and production workflows copy the static
site to a disposable deployment directory and add the public repository commit
and Actions run to `data/openfs-deployment.json`. This deployment-time record is
not part of the signed bundle contents and cannot alter the source bundle. Pages
does not create a separate Git commit.

A successful build or preview does not mean that the research has passed
Consensus review, nor does it authorize publication.

## Local verification

```bash
python3 .github/verify_publication.py
python3 -m http.server 8000 --directory public-site
```

Then open `http://localhost:8000/`.

## Rollback

Revert the public pull request or publish a superseding reviewed bundle. Keep the
manifest with the corresponding site and data files so provenance remains
verifiable.

# OpenFSの公開範囲

## リポジトリの役割

このリポジトリは、OpenFSの調査成果を公開する静的な配布リポジトリです。
調査エージェントの実行や内部候補の承認は行いません。管理環境で生成・検証・
レビューした公開バンドルだけを取り込みます。

現在のツリーに収録できるのは、`knowledge/public/`の公開用構造化データ、
`roadmaps/scenarios/accepted/`の承認済み公開シナリオ、`reports/exports/`の公開用報告書、
`assets/branding/`のブランド素材、`public-site/`の生成済みサイト、および公開に必要な
文書、Feedbackフォーム、検証ファイルです。

秘密情報、個人情報、NDA情報、内部プロンプト、非公開の実行記録・レビュー、認証情報、
分離後の非公開管理パスへのリンクを追加してはいけません。分離前のGit履歴は引き続き
公開され、当時すでに公開されていた旧ワークフローの成果物を含む場合があります。

## 公開手順

1. 公開入力コミットと管理コミットを固定する。
2. 管理環境で公開候補バンドルを生成・検証する。
3. Manifest、情報境界、Pagesの表示、未解消のCoverage Gapをレビューする。
4. 公開リポジトリの作業ブランチへバンドルを取り込む。
5. `.github/verify_publication.py`とPagesプレビューartifactを確認する。
6. 保守担当者の明示的承認後にのみマージする。本番Pagesへの反映は、対象コミットが
   `main`へ入り、Pages Workflowが成功した後に成立する。

プレビューと本番のWorkflowは、バンドル検証後に静的サイトを一時的な配信用
ディレクトリへ複製し、公開リポジトリのコミットとActions実行を
`data/openfs-deployment.json`へ付加します。この実行時記録は署名対象のバンドル内容を
変更しません。GitHub Pagesが別のGitコミットを作成することもありません。

ビルドやプレビューの成功だけでは、Consensus通過や公開承認を意味しません。
