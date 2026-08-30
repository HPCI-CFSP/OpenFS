from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from build_catalog_reference import OUTPUT, render
from catalog_lineage import active_successors, catalog_aliases, current_finding_topics, validate_catalog_scope
from check_catalog_migration import audit


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class CatalogReorganizationTests(unittest.TestCase):
    def setUp(self):
        self.baseline = read("config/research-baseline.json")
        self.topics = {t["topic_id"]: t for t in self.baseline["topics"]}
        self.taxonomy = read("config/catalog-taxonomy.json")
        self.migration = read("config/catalog-migration.json")
        self.codes = {tid: code for c in self.taxonomy["categories"] for tid, code in c["topic_codes"].items()}

    def test_complete_migration_keeps_source_questions_and_codes_reserved(self):
        self.assertEqual(54, len(self.migration["entries"]))
        reserved = {code for c in self.taxonomy["categories"] for code in c["reserved_topic_codes"]}
        for entry in self.migration["entries"]:
            self.assertIn(entry["source_topic_id"], self.topics)
            self.assertTrue(entry["source_questions"])
            self.assertIn(entry["source_catalog_code"], reserved)
            self.assertTrue(set(entry["target_topic_ids"]) <= self.codes.keys())
        self.assertEqual([7, 8, 9, 11, 2, 3], [len(c["topic_ids"]) for c in self.taxonomy["categories"]])

    def test_storage_precision_and_programming_have_deliberate_owners(self):
        self.assertEqual("ARCH-012", self.codes["SSW-05"])
        self.assertEqual("APP-016", self.codes["ARCH-13"])
        self.assertEqual(["SSW-01"], active_successors("SSW-02", self.topics))
        self.assertIn("SSW-08", self.codes)
        self.assertIn("SSW-16", self.codes)
        storage = self.topics["SSW-05"]
        self.assertEqual(4, len(storage["research_units"]))
        self.assertTrue(any("SSD" in unit["question_ja"] for unit in storage["research_units"]))
        self.assertTrue(any("EXAScaler" in unit["question_en"] for unit in storage["research_units"]))

    def test_three_needs_and_evaluation_pairs_are_distinct(self):
        pairs = self.migration["workload_pairs"]
        self.assertEqual({"simulation", "ai", "experimental-realtime"}, {p["domain"] for p in pairs})
        ids = [p[key] for p in pairs for key in ("needs_topic_id", "evaluation_topic_id")]
        self.assertEqual(6, len(set(ids)))
        self.assertTrue(set(ids) <= self.codes.keys())
        self.assertEqual("not-started", self.topics["APP-15"]["status"])

    def test_legacy_links_expose_all_successors_and_moved_codes(self):
        aliases = catalog_aliases(ROOT, self.baseline, read("config/publication-i18n.json"), self.codes)
        by_id = {alias["topic_id"]: alias for alias in aliases}
        self.assertTrue(all(alias["target_topic_ids"] or alias["output_path"] for alias in aliases))
        self.assertEqual(["APP-02", "APP-13", "APP-15"], by_id["ARCH-08"]["target_topic_ids"])
        self.assertEqual("SSW-005", by_id["SSW-05"]["legacy_code"])
        self.assertEqual(["SSW-05"], by_id["SSW-05"]["target_topic_ids"])
        self.assertEqual("scenarios/", by_id["CROSS-13"]["output_path"])
        self.assertEqual([], by_id["CROSS-18"]["target_topic_ids"])

    def test_broad_history_is_not_assigned_to_all_successors(self):
        finding = {"topic_ids": ["ARCH-08", "ARCH-03"]}
        self.assertEqual(["ARCH-03"], current_finding_topics(finding, self.topics))
        self.assertEqual(["ARCH-08", "ARCH-03"], finding["topic_ids"])

    def test_retirement_cycles_are_rejected(self):
        self.topics["ARCH-08"]["retirement"]["successor_topic_ids"] = ["ARCH-09"]
        self.topics["ARCH-09"]["retirement"]["successor_topic_ids"] = ["ARCH-08"]
        with self.assertRaisesRegex(ValueError, "cycle"):
            active_successors("ARCH-08", self.topics)

    def test_scope_validation_passes_and_reference_is_current(self):
        self.assertEqual([], validate_catalog_scope(ROOT))
        self.assertEqual(render(ROOT), (ROOT / OUTPUT).read_text(encoding="utf-8"))

    def test_pinned_migration_preserves_all_original_claim_payloads_and_scope(self):
        report = audit(ROOT)
        self.assertEqual([], report["errors"])
        self.assertEqual(162, report["preserved_item_count"])
        self.assertEqual(60, report["preserved_topic_count"])

    def test_incomplete_units_cannot_claim_progress_or_review(self):
        modified = copy.deepcopy(self.baseline)
        topic = next(t for t in modified["topics"] if t["topic_id"] == "APP-15")
        topic["research_units"][0]["status"] = "reviewed"
        topic["status"] = "reviewed"
        with patch("catalog_lineage.load_catalog", return_value=modified):
            errors = validate_catalog_scope(ROOT)
        self.assertTrue(any("without evidence" in e for e in errors))
        self.assertTrue(any("Consensus receipt" in e for e in errors))
        self.assertTrue(any("incomplete research units" in e for e in errors))

    def test_cross_topic_evidence_and_retired_related_topics_are_rejected(self):
        modified = copy.deepcopy(self.baseline)
        topic = next(t for t in modified["topics"] if t["topic_id"] == "APP-15")
        topic["research_units"][0]["evidence_section_ids"] = ["TDS-ARCH03-MAIN"]
        topic["related_topic_ids"].append("SSW-02")
        with patch("catalog_lineage.load_catalog", return_value=modified):
            errors = validate_catalog_scope(ROOT)
        self.assertTrue(any("owned by another Topic" in e for e in errors))
        self.assertTrue(any("inactive related Topics" in e for e in errors))

    def test_science_and_framework_profiles_do_not_own_ai_benchmarks_or_policy(self):
        profiles = {p["topic_id"]: p for p in read("knowledge/public/topic-decision-support.json")["topic_profiles"]}
        for tid in ("APP-02", "SSW-09"):
            items = [i for s in profiles[tid]["sections"] for i in s["items"]]
            self.assertFalse(any("-WORKAI-" in i["item_id"] for i in items))
        self.assertFalse(any("-BLUEPOLICY-" in i["item_id"] for s in profiles["SSW-09"]["sections"] for i in s["items"]))
        self.assertTrue(any("-BLUEPOLICY-" in i["item_id"] for s in profiles["CROSS-10"]["sections"] for i in s["items"]))

    def test_catalog_ui_events_offline(self):
        node = os.environ.get("OPENFS_NODE") or shutil.which("node")
        if not node:
            self.skipTest("Node.js is unavailable")
        from build_pages_site import build
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            build(ROOT, output)
            env = dict(os.environ, OPENFS_TEST_PUBLIC_DATA=str(output / "data/openfs-public.js"))
            result = subprocess.run([node, "--test", "tests/test_catalog_ui.js"], cwd=ROOT,
                                    env=env, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
