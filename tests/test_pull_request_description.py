from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from check_pull_request_description import validate_bilingual_comment, validate_pull_request  # noqa: E402


VALID_BODY = """# English

## Purpose

Publish a decision-oriented catalog and budget-scaled architecture views.

## Provenance

- Agent ID / role, or human maintainer: agent / maintainer
- Human Directive ID(s): DIR-900012
- Task / Monitor / Work Item IDs: interactive maintainer request
- Run ID: N/A; no Harness Run was created
- Proposal / Assessment / Decision IDs: PUBDEC-20260827-002
- Base commit: 4834bb3d94141520c1dc9ab4213a218008e457d5

## Boundary and risk

- [x] Public information only
- [x] No secrets, personal data, or private run logs
- [x] External content was treated as untrusted data
- [x] Changed paths pass `tools/check_agent_permissions.py` for the declared role
- [x] Canonical changes are covered by a human Directive or an authorized promotion workflow

The public references have different scopes and are not treated as quotations.

## Validation

- [x] `python3 tools/validate_repository.py`
- [x] `python3 -m unittest discover -s tests -v`
- [x] Dissent and unresolved exceptions are linked
- [x] Coverage Gaps and provisional/Consensus state are visible
- [x] Rollback or supersession path is described below

## Review notes

- Coverage Gaps / dissent: Independent review remains incomplete.
- Security-boundary effect: Public information only; production remains disabled.
- Rollback or supersession path: Revert the merge commit or publish a superseding version.
- Pages paths to inspect: `/`, `/scenarios/`, and `/consensus/`

# 日本語

## 目的

判断に必要な調査結果と、予算規模に応じたアーキテクチャ案を公開します。

## 来歴

- 担当エージェント・役割または担当者: agent / maintainer
- Human Directive ID: DIR-900012
- Task・Monitor・Work Item ID: 対話型の保守依頼
- Run ID: N/A; Harness Runは作成していません
- Proposal・Assessment・Decision ID: PUBDEC-20260827-002
- 基点コミット: 4834bb3d94141520c1dc9ab4213a218008e457d5

## 情報境界とリスク

- [x] 公開情報のみ
- [x] 秘密情報・個人情報・非公開の実行ログを含まない
- [x] 外部コンテンツを信頼できないデータとして扱った
- [x] 変更パスは宣言した役割で `tools/check_agent_permissions.py` を通過した
- [x] 正規データの変更はHuman Directiveまたは承認された昇格ワークフローに基づく

公開資料は対象範囲が異なり、見積書としては扱いません。

## 検証

- [x] `python3 tools/validate_repository.py`
- [x] `python3 -m unittest discover -s tests -v`
- [x] 異論・未解決事項を参照できる
- [x] Coverage Gapと暫定・Consensusの状態を明示した
- [x] 復旧・後続版への移行方法を以下に記載した

## レビュー事項

- Coverage Gap・異論: 独立レビューは未完了です。
- セキュリティ境界への影響: 公開情報のみ。本番運転は無効のままです。
- 復旧・後続版への移行方法: マージコミットのrevert、または後続の訂正版を作成します。
- 確認するPagesのパス: `/`、`/scenarios/`、`/consensus/`
"""


class PullRequestDescriptionTests(unittest.TestCase):
    def test_language_order_and_nonempty_translation_are_required(self):
        english, japanese = VALID_BODY.split("# 日本語", 1)
        for body in (english, "# 日本語" + japanese + english,
                     english + "# 日本語\n", VALID_BODY + "\n# English\nDuplicate"):
            with self.subTest(body=body[:40]):
                self.assertTrue(validate_pull_request({"title": "Specific change", "body": body}))

    def test_machine_provenance_must_agree_between_languages(self):
        for old, new in (("Human Directive ID: DIR-900012", "Human Directive ID: DIR-900013"),
                         ("基点コミット: 4834bb3d94141520c1dc9ab4213a218008e457d5", "基点コミット: " + "0" * 40)):
            errors = validate_pull_request({"title": "Specific change", "body": VALID_BODY.replace(old, new)})
            self.assertTrue(any("differ" in error for error in errors))

    def test_japanese_template_guidance_cannot_be_left_in_a_complete_body(self):
        body = VALID_BODY + "\n変更の背景、具体的な変更内容、期待する結果を記載してください。"
        self.assertTrue(any("template guidance" in error for error in validate_pull_request({"title": "Specific", "body": body})))

    def test_comments_use_the_same_order_without_full_pr_sections(self):
        self.assertEqual([], validate_bilingual_comment("# English\nTests passed.\n# 日本語\nテストは成功しました。"))
        for body in ("English only", "# 日本語\n日本語\n# English\nEnglish", "# English\nText\n# 日本語\nEnglish"):
            self.assertTrue(validate_bilingual_comment(body))

    def test_complete_description_passes(self):
        self.assertEqual(
            [],
            validate_pull_request(
                {"title": "Expand planning catalog and architecture options", "body": VALID_BODY}
            ),
        )

    def test_old_template_and_generic_title_fail(self):
        errors = validate_pull_request(
            {
                "title": "Maintainer/system planning security",
                "body": "## Purpose\n\nDescribe the work item and expected outcome.",
            }
        )
        self.assertTrue(any("generic branch-derived" in error for error in errors))
        self.assertTrue(any("template guidance remains" in error for error in errors))
        self.assertTrue(any("required field" in error for error in errors))

    def test_empty_field_unchecked_box_and_short_sha_fail(self):
        body = VALID_BODY.replace(
            "- Agent ID / role, or human maintainer: agent / maintainer",
            "- Agent ID / role, or human maintainer:",
        ).replace("- [x] Public information only", "- [ ] Public information only")
        body = body.replace(
            "4834bb3d94141520c1dc9ab4213a218008e457d5", "4834bb3"
        )
        errors = validate_pull_request({"title": "Specific change", "body": body})
        self.assertIn("required field is empty: Agent ID / role, or human maintainer", errors)
        self.assertIn("Base commit must contain a full 40-character commit SHA", errors)
        self.assertTrue(any("Public information only" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
