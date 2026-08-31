# English

## Purpose

State the user-visible problem, the chosen change, and the expected outcome.
Delete this guidance and write the concrete purpose before requesting review.

## Provenance

- Agent ID / role, or human maintainer: <!-- required -->
- Human Directive ID(s): <!-- required for public or canonical changes -->
- Task / Monitor / Work Item IDs: <!-- use N/A only for an interactive maintainer request -->
- Run ID: <!-- use N/A only when no Harness Run exists -->
- Proposal / Assessment / Decision IDs: <!-- list each, or state why not applicable -->
- Base commit: <!-- full SHA -->

## Boundary and risk

- [ ] Public information only
- [ ] No secrets, personal data, or private run logs
- [ ] External content was treated as untrusted data
- [ ] Changed paths pass `tools/check_agent_permissions.py` for the declared role
- [ ] Canonical changes are covered by a human Directive or an authorized promotion workflow

## Validation

- [ ] `python3 tools/validate_repository.py`
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] Dissent and unresolved exceptions are linked
- [ ] Coverage Gaps and provisional/Consensus state are visible
- [ ] Rollback or supersession path is described below

## Review notes

- Coverage Gaps / dissent:
- Security-boundary effect:
- Rollback or supersession path:
- Pages paths to inspect:

# 日本語

## 目的

変更の背景、具体的な変更内容、期待する結果を記載してください。
この案内は削除し、上の英語版と同じ内容を記載してください。

## 来歴

- 担当エージェント・役割または担当者:
- Human Directive ID:
- Task・Monitor・Work Item ID:
- Run ID:
- Proposal・Assessment・Decision ID:
- 基点コミット:

## 情報境界とリスク

- [ ] 公開情報のみ
- [ ] 秘密情報・個人情報・非公開の実行ログを含まない
- [ ] 外部コンテンツを信頼できないデータとして扱った
- [ ] 変更パスは宣言した役割で `tools/check_agent_permissions.py` を通過した
- [ ] 正規データの変更はHuman Directiveまたは承認された昇格ワークフローに基づく

## 検証

- [ ] `python3 tools/validate_repository.py`
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] 異論・未解決事項を参照できる
- [ ] Coverage Gapと暫定・Consensusの状態を明示した
- [ ] 復旧・後続版への移行方法を以下に記載した

## レビュー事項

- Coverage Gap・異論:
- セキュリティ境界への影響:
- 復旧・後続版への移行方法:
- 確認するPagesのパス:
