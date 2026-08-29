from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_source_catalog_map import build  # noqa: E402


class SourceCatalogMapTests(unittest.TestCase):
    def test_checked_in_map_is_deterministic(self):
        expected = json.loads(
            (ROOT / "knowledge/public/source-catalog-map.json").read_text(encoding="utf-8")
        )
        self.assertEqual(expected, build(ROOT))

    def test_every_mapping_reaches_a_catalog_topic_and_registered_evidence(self):
        result = build(ROOT)
        self.assertGreater(len(result["entries"]), 200)
        for entry in result["entries"]:
            with self.subTest(url=entry["canonical_url"]):
                self.assertTrue(entry["topic_links"])
                self.assertTrue(
                    entry["roadmap_source_refs"] or entry["catalog_source_refs"]
                )

    def test_every_topic_decision_source_is_mapped_as_direct_evidence(self):
        decision_support = json.loads(
            (ROOT / "knowledge/public/topic-decision-support.json").read_text(
                encoding="utf-8"
            )
        )
        entries_by_url = {
            entry["canonical_url"]: entry for entry in build(ROOT)["entries"]
        }
        result = build(ROOT)
        mapped_source_ids = {
            ref["source_id"]
            for entry in result["entries"]
            for ref in entry["catalog_source_refs"]
        }
        all_source_ids = {source["source_id"] for source in decision_support["sources"]}
        self.assertEqual(
            all_source_ids,
            mapped_source_ids | set(result["unmapped_catalog_source_ids"]),
        )
        self.assertFalse(
            mapped_source_ids & set(result["unmapped_catalog_source_ids"])
        )
        for entry in entries_by_url.values():
            direct_topics = {
                link["topic_id"]
                for link in entry["topic_links"]
                if link["mapping_basis"] == "direct-topic-evidence"
            }
            for catalog_ref in entry["catalog_source_refs"]:
                self.assertTrue(catalog_ref["topic_ids"])
                self.assertTrue(
                    set(catalog_ref["topic_ids"]).issubset(direct_topics)
                )

    def test_mext_committee_is_a_watch_target_not_inferred_evidence(self):
        registry = json.loads(
            (ROOT / "config/source-watch-registry.json").read_text(encoding="utf-8")
        )
        committee = next(
            item for item in registry["targets"]
            if item["watch_id"] == "WATCH-MEXT-HPCI-COMMITTEE"
        )
        self.assertIn("CROSS-10", committee["topic_ids"])
        self.assertTrue(committee["change_policy"]["consensus_required_for_catalog_update"])


if __name__ == "__main__":
    unittest.main()
