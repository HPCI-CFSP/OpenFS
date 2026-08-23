from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


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

    def test_missing_fs1_and_fs2_material_remains_explicit(self):
        self.assertFalse(self.baseline["complete"])
        self.assertIn("FSBASE-GAP-001", self.baseline["open_gap_ids"])
        self.assertIn("FSBASE-GAP-002", self.baseline["open_gap_ids"])


if __name__ == "__main__":
    unittest.main()
