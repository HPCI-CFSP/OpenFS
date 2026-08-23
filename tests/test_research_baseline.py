from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INITIAL_TOPIC_IDS = [
    "ARCH-01", "ARCH-02", "ARCH-03", "ARCH-04", "ARCH-05", "ARCH-06", "ARCH-07",
    "SSW-01", "SSW-02", "SSW-03", "SSW-04", "SSW-05", "SSW-06", "SSW-07", "SSW-08", "SSW-09",
    "APP-01", "APP-02", "APP-03", "APP-04", "APP-05", "APP-06", "APP-07",
    "CROSS-01", "CROSS-02", "CROSS-03", "CROSS-04", "CROSS-05", "CROSS-06", "CROSS-07",
]


class ResearchBaselineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = json.loads(
            (ROOT / "config" / "research-baseline.json").read_text(encoding="utf-8")
        )

    def test_topic_ids_are_unique_and_all_domains_are_covered(self):
        topics = self.baseline["topics"]
        topic_ids = [topic["topic_id"] for topic in topics]
        self.assertEqual(len(topic_ids), len(set(topic_ids)))
        self.assertEqual(
            {"architecture", "system-software", "applications", "cross-cutting"},
            {topic["domain"] for topic in topics},
        )

    def test_each_topic_is_actionable_and_traceable(self):
        source_ids = {source["source_id"] for source in self.baseline["source_corpus"]}
        for topic in self.baseline["topics"]:
            with self.subTest(topic_id=topic["topic_id"]):
                self.assertTrue(topic["research_questions"])
                self.assertTrue(topic["evidence_expected"])
                self.assertTrue(topic["outputs"])
                self.assertTrue(set(topic["source_refs"]).issubset(source_ids))

    def test_language_variants_share_one_origin_group(self):
        sources = {source["source_id"]: source for source in self.baseline["source_corpus"]}
        self.assertEqual(
            sources["FSBASE-SRC-001"]["origin_group_id"],
            sources["FSBASE-SRC-002"]["origin_group_id"],
        )

    def test_initial_catalog_is_protected_and_still_present(self):
        protected = self.baseline["initial_catalog"]
        self.assertEqual("FSBASE-001", protected["baseline_id"])
        self.assertEqual(30, protected["topic_count"])
        self.assertEqual(INITIAL_TOPIC_IDS, protected["topic_ids"])
        self.assertTrue(
            set(INITIAL_TOPIC_IDS).issubset(
                {topic["topic_id"] for topic in self.baseline["topics"]}
            )
        )

    def test_all_official_fs2_fs3_reports_are_registered(self):
        official = [
            source
            for source in self.baseline["source_corpus"]
            if source["source_id"] >= "FSBASE-SRC-006"
        ]
        self.assertEqual(26, len(official))
        self.assertEqual({2022, 2023, 2024, 2025}, {source["fiscal_year"] for source in official})
        for source in official:
            with self.subTest(source_id=source["source_id"]):
                self.assertTrue(source["public_url"].startswith("https://www.mext.go.jp/"))
                self.assertTrue(source["source_page_url"].startswith("https://www.mext.go.jp/"))
                self.assertGreater(source["page_count"], 0)

    def test_priority_japan_and_center_scenario_topics_are_explicit(self):
        topic_ids = {topic["topic_id"] for topic in self.baseline["topics"]}
        self.assertTrue(
            {"ARCH-11", "ARCH-12", "CROSS-08", "CROSS-11", "CROSS-12", "CROSS-13", "CROSS-17", "CROSS-18"}.issubset(topic_ids)
        )
        self.assertEqual(58, len(topic_ids))

    def test_missing_fs1_material_remains_explicit_but_fs2_gap_is_closed(self):
        self.assertFalse(self.baseline["complete"])
        self.assertIn("FSBASE-GAP-001", self.baseline["open_gap_ids"])
        self.assertNotIn("FSBASE-GAP-002", self.baseline["open_gap_ids"])
        self.assertNotIn("FSBASE-GAP-004", self.baseline["open_gap_ids"])


if __name__ == "__main__":
    unittest.main()
