from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.check_public_language import validate


ROOT = Path(__file__).resolve().parents[1]


class PublicLanguageTests(unittest.TestCase):
    def test_repository_public_content_passes(self):
        self.assertEqual([], validate(ROOT))

    def test_missing_language_pair_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "knowledge/public/example.json"
            target.parent.mkdir(parents=True)
            target.write_text(
                json.dumps({"title_ja": "例"}, ensure_ascii=False), encoding="utf-8"
            )
            (root / "README.md").write_text("OpenFS\n", encoding="utf-8")
            (root / "README.ja.md").write_text("OpenFS\n", encoding="utf-8")
            self.assertTrue(any("has no title_en" in error for error in validate(root)))

    def test_known_awkward_japanese_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "knowledge/public/example.json"
            target.parent.mkdir(parents=True)
            target.write_text(
                json.dumps(
                    {
                        "summary_ja": "Coverage Gapとして残す。",
                        "summary_en": "Retain as an unresolved item.",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (root / "README.md").write_text("OpenFS\n", encoding="utf-8")
            (root / "README.ja.md").write_text("OpenFS\n", encoding="utf-8")
            self.assertTrue(
                any("未確認事項" in error for error in validate(root))
            )

    def test_archived_catalog_wording_is_preserved_but_current_wording_is_checked(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "knowledge/public/topic-decision-support.json"
            target.parent.mkdir(parents=True)
            (root / "README.md").write_text("OpenFS\n")
            (root / "README.ja.md").write_text("OpenFS\n")
            section = {"section_id": "TDS-OLD", "summary_ja": "Coverage Gapとして残す。",
                       "summary_en": "Retain as an unresolved item."}
            payload = {"topic_profiles": [{"sections": [section], "archived_section_ids": ["TDS-OLD"]}]}
            target.write_text(json.dumps(payload, ensure_ascii=False))
            before = target.read_bytes()
            self.assertEqual([], validate(root))
            self.assertEqual(before, target.read_bytes())
            payload["topic_profiles"][0]["archived_section_ids"] = []
            target.write_text(json.dumps(payload, ensure_ascii=False))
            self.assertTrue(any("未確認事項" in error for error in validate(root)))
            payload["topic_profiles"][0]["archived_section_ids"] = ["TDS-OLD"]
            del section["summary_en"]
            target.write_text(json.dumps(payload, ensure_ascii=False))
            self.assertTrue(any("has no summary_en" in error for error in validate(root)))

    def test_openfs_proposal_fragment_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "knowledge/public/example.json"
            target.parent.mkdir(parents=True)
            target.write_text(
                json.dumps(
                    {
                        "detail_ja": "共通基準を整備するOpenFSの提案。",
                        "detail_en": "OpenFS proposes a common baseline.",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (root / "README.md").write_text("OpenFS\n", encoding="utf-8")
            (root / "README.ja.md").write_text("OpenFS\n", encoding="utf-8")
            self.assertTrue(
                any("OpenFSは〜を提案する。" in error for error in validate(root))
            )

    def test_awkward_as_of_phrase_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "knowledge/public/example.json"
            target.parent.mkdir(parents=True)
            target.write_text(
                json.dumps(
                    {
                        "summary_ja": "調査基準日時点の状況を示す。",
                        "summary_en": "Shows status as of the research date.",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (root / "README.md").write_text("OpenFS\n", encoding="utf-8")
            (root / "README.ja.md").write_text("OpenFS\n", encoding="utf-8")
            self.assertTrue(
                any("調査基準日現在" in error for error in validate(root))
            )

    def test_language_pair_array_length_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "knowledge/public/example.json"
            target.parent.mkdir(parents=True)
            target.write_text(
                json.dumps(
                    {"items_ja": ["一", "二"], "items_en": ["one"]},
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (root / "README.md").write_text("OpenFS\n", encoding="utf-8")
            (root / "README.ja.md").write_text("OpenFS\n", encoding="utf-8")
            self.assertTrue(
                any("different item counts" in error for error in validate(root))
            )

    def test_reader_facing_explanation_requires_complete_sentences(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            target = root / "knowledge/public/example.json"
            target.parent.mkdir(parents=True)
            target.write_text(
                json.dumps(
                    {
                        "detail_ja": "文末が欠けている説明",
                        "detail_en": "An explanation without terminal punctuation",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            (root / "README.md").write_text("OpenFS\n", encoding="utf-8")
            (root / "README.ja.md").write_text("OpenFS\n", encoding="utf-8")

            errors = validate(root)

            self.assertTrue(any("complete Japanese sentence" in error for error in errors))
            self.assertTrue(any("complete English sentence" in error for error in errors))

    def test_awkward_japanese_in_site_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            public = root / "knowledge/public"
            public.mkdir(parents=True)
            (public / "example.json").write_text("{}\n", encoding="utf-8")
            (root / "README.md").write_text("OpenFS\n", encoding="utf-8")
            (root / "README.ja.md").write_text("OpenFS\n", encoding="utf-8")
            site = root / "site"
            site.mkdir()
            (site / "app.js").write_text(
                'const text = "中央管理された説明";\n', encoding="utf-8"
            )
            self.assertTrue(
                any("一元管理された" in error for error in validate(root))
            )

    def test_awkward_japanese_in_reader_facing_scenario_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            public = root / "knowledge/public"
            public.mkdir(parents=True)
            (public / "example.json").write_text("{}\n", encoding="utf-8")
            (root / "README.md").write_text("OpenFS\n", encoding="utf-8")
            (root / "README.ja.md").write_text("OpenFS\n", encoding="utf-8")
            scenario = root / "roadmaps/scenarios/accepted/example.json"
            scenario.parent.mkdir(parents=True)
            scenario.write_text(
                json.dumps({"condition": "package供給能力"}, ensure_ascii=False),
                encoding="utf-8",
            )
            self.assertTrue(
                any("パッケージ供給" in error for error in validate(root))
            )

    def test_legacy_japanese_scenario_field_is_accepted_as_pair(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            public = root / "knowledge/public"
            public.mkdir(parents=True)
            (public / "example.json").write_text("{}\n", encoding="utf-8")
            (root / "README.md").write_text("OpenFS\n", encoding="utf-8")
            (root / "README.ja.md").write_text("OpenFS\n", encoding="utf-8")
            scenario = root / "roadmaps/scenarios/accepted/example.json"
            scenario.parent.mkdir(parents=True)
            scenario.write_text(
                json.dumps(
                    {
                        "objective": "評価の目的を明確にする。",
                        "objective_en": "Clarify the purpose of the evaluation.",
                    },
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            self.assertEqual([], validate(root))

    def test_missing_legacy_japanese_scenario_field_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            public = root / "knowledge/public"
            public.mkdir(parents=True)
            (public / "example.json").write_text("{}\n", encoding="utf-8")
            (root / "README.md").write_text("OpenFS\n", encoding="utf-8")
            (root / "README.ja.md").write_text("OpenFS\n", encoding="utf-8")
            scenario = root / "roadmaps/scenarios/accepted/example.json"
            scenario.parent.mkdir(parents=True)
            scenario.write_text(
                json.dumps({"objective_en": "Objective"}), encoding="utf-8"
            )
            self.assertTrue(
                any("objective_ja or objective" in error for error in validate(root))
            )


if __name__ == "__main__":
    unittest.main()
