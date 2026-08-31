# Pull-request descriptions and comments

Every new description and comment uses `# English` followed by `# 日本語`.
Both versions must communicate the same change, evidence, limitations, review
status and validation outcome. Keep machine IDs, URLs and commit SHAs identical.
The Japanese block is not a shorter summary that omits qualifications.

Replace the template guidance with a concrete purpose. Complete the provenance
and review fields, and mark a check complete only after performing it. Tests do
not establish independent Consensus, institutional approval or scientific truth.
Do not overwrite an existing PR body with the repository template during a push.
If changing the body, preserve still-relevant review context and describe what
was corrected. Existing published comments are historical records, not files to
rewrite silently.

Before posting:

```sh
python3 tools/check_pull_request_description.py --body /path/to/body.md --title "Specific change"
python3 tools/check_pull_request_description.py --comment /path/to/comment.md
```

The checker enforces block order, nonempty required sections, checkboxes, base
SHA agreement and common provenance ID agreement. It cannot prove that prose is
accurately translated or that an asserted test was run. Read both versions and
retain the actual validation results. The trusted-base GitHub workflow checks PR
descriptions after posting; new checker rules take effect after their merge.

The deterministic Handoff and Claim PR publishers use the same bilingual format.
They re-run repository validation, the full unittest suite and role/path checks
on the committed output branch before creating a completed description. The
base SHA is the workflow checkout SHA, not a guessed branch name. Dirty branches,
disallowed paths, failed checks or a changed HEAD stop publication. No production
workflow is enabled by this change. Existing Consensus decisions are referenced,
not recreated or upgraded by the PR description generator. The requested local
head branch must match the checked commit before and after validation. Push
steps remove the credential-bearing origin URL on exit, and validation children
receive an allowlisted environment without the API token. These safeguards are
not a sandbox against arbitrary code already trusted on the default branch.

Short comments need only the two language blocks, not all PR sections. For example:

```markdown
# English
The capacity figure now distinguishes physical capacity from the user allocation.
The final procurement specification remains unverified.

# 日本語
容量の値について、物理容量と利用者への提供枠を区別しました。
最終調達仕様書との照合は未完了です。
```

## 日本語

新しいPR本文とコメントは、必ず英語を先、日本語を後に記載します。変更内容、
根拠、制約、レビュー状況、検証結果は両言語で同じ内容にし、ID・URL・コミット
ハッシュも一致させます。日本語版で注意事項を省略してはいけません。

雛形の案内文は具体的な説明に置き換え、実施していない検証にチェックを入れないで
ください。自動検査は書式と一部のIDの一致を確認しますが、翻訳の意味や実施記録の
正しさを保証しません。両言語を読み合わせ、実際の検証結果を保持します。pushの際に
既存のPR本文を雛形で上書きしないでください。過去のコメントも無断で書き換えません。
GitHub側は信頼された基点の検査を使用するため、今回の規則はマージ後に有効になります。
Handoff・Claimの決定的なPR作成処理も同じ形式を使い、変更後のコミットに対して
リポジトリ検証・全unittest・役割別パス検査を再実行してから本文を作成します。
未コミットの変更、権限外のパス、検証失敗、検証中のHEAD変更があれば作成を止めます。
今回の変更で本番ワークフローを有効にしたり、Consensusの状態を昇格したりはしません。
指定されたローカルのPRブランチと検証対象コミットの一致を、検証の前後に確認します。
push処理終了時にorigin URLから認証情報を除去し、検証用の子プロセスにはAPIトークンを
含まない許可済み環境変数だけを渡します。ただし、これは既にデフォルトブランチで
信頼されている任意のコードに対するサンドボックスではありません。
