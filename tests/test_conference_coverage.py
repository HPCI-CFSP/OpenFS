import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from check_conference_coverage import load_and_validate, validate_coverage
from build_pages_site import build, collect_conference_coverage
from build_source_catalog_map import build as build_source_map
from build_roadmap_evidence_audit import timing_label


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class ConferenceCoverageTests(unittest.TestCase):
    def setUp(self):
        self.payload = read("knowledge/public/conferences/HC2026.json")
        self.baseline = read("config/research-baseline.json")
        self.surface = read("knowledge/public/topic-decision-support.json")

    def check(self):
        validate_coverage(self.payload, self.baseline, self.surface)

    def test_complete_program_does_not_claim_complete_research(self):
        load_and_validate(ROOT)
        self.assertEqual(48, len(self.payload["entries"]))
        self.assertEqual(18, sum(e["coverage_state"] == "program-only" for e in self.payload["entries"]))
        self.assertEqual(30, sum(e["coverage_state"] == "related-primary-checked" for e in self.payload["entries"]))
        for entry in self.payload["entries"]:
            self.assertNotEqual("conference-materials-checked", entry["coverage_state"])
        self.assertEqual("incomplete", self.payload["consensus_status"])

    def test_followup_preserves_conference_and_related_announcement_boundaries(self):
        by_id = {entry["entry_id"]: entry for entry in self.payload["entries"]}
        for entry_id in ["HC26-T06", "HC26-C16", "HC26-C17", "HC26-P01", "HC26-P06"]:
            self.assertEqual("related-primary-checked", by_id[entry_id]["coverage_state"])
        announcements = self.payload["related_announcements"]
        self.assertEqual(2, len(announcements))
        self.assertEqual({"TDI-HW1-NVHBM-READINESS", "TDI-HW1-ZHBM-CONCEPT"},
                         {item["technical_item_id"] for item in announcements})

    def test_dropped_entry_and_rewritten_denominator_fail(self):
        self.payload["entries"].pop()
        self.payload["expected_counts"]["poster"] -= 1
        with self.assertRaises(ValueError): self.check()

    def test_duplicate_and_retired_ids_fail(self):
        self.payload["entries"][1]["entry_id"] = self.payload["entries"][0]["entry_id"]
        with self.assertRaises(ValueError): self.check()
        self.setUp()
        self.payload["entries"][0]["primary_topic_id"] = "ARCH-08"
        with self.assertRaises(ValueError): self.check()

    def test_program_only_cannot_claim_technical_review(self):
        self.payload["entries"][0]["coverage_state"] = "related-primary-checked"
        with self.assertRaises(ValueError): self.check()

    def test_failed_or_secondary_or_abstract_source_cannot_support_claim(self):
        for field, value in [("retrieval_status", "blocked"), ("retrieval_status", "abstract-read"), ("role", "discovery")]:
            self.setUp()
            source = next(s for s in self.payload["sources"] if s["source_id"] == "SRC-HC26-INTEL")
            source[field] = value
            with self.assertRaises(ValueError): self.check()

    def test_wrong_catalog_reference_fails(self):
        entry = next(e for e in self.payload["entries"] if e["entry_id"] == "HC26-T08")
        entry["primary_topic_id"] = "ARCH-03"
        with self.assertRaises(ValueError): self.check()

    def test_related_announcement_cites_the_whole_shared_claim(self):
        self.payload["related_announcements"][0]["source_ids"] = ["SRC-HC26-NVHBM"]
        with self.assertRaises(ValueError): self.check()

    def test_publication_authorization_is_required(self):
        policy = read("config/publication-policy.json")
        result = collect_conference_coverage(ROOT, policy)
        self.assertNotIn("publication", result)
        self.assertNotIn("base_commit", result)
        unauthorized = copy.deepcopy(self.payload)
        unauthorized["publication"]["human_approval_directive_id"] = "DIR-000000"
        with patch("check_conference_coverage.load_and_validate", return_value=unauthorized):
            with self.assertRaises(ValueError): collect_conference_coverage(ROOT, policy)

    def test_source_map_keeps_program_context_distinct_from_evidence(self):
        entries = build_source_map(ROOT)["entries"]
        program = next(e for e in entries if e["canonical_url"] == "https://hc2026.hotchips.org/")
        self.assertEqual(48, len(program["conference_entry_refs"]))
        self.assertTrue(all(t["mapping_basis"] == "conference-program-context" for t in program["topic_links"]))

    def test_roadmap_timing_does_not_invent_quarters(self):
        roadmap = read("knowledge/public/roadmaps/compute-nodes-accelerators.json")
        milestones = {m["milestone_id"]: m for l in roadmap["lanes"] for m in l["milestones"]}
        for key in ["MTIA450", "MTIA500", "MOP-SAMPLE", "JALAPENO-INTERNAL"]:
            self.assertEqual("year", milestones[f"MS-HC26-{key}"]["timing_precision"])
            self.assertIsNone(milestones[f"MS-HC26-{key}"]["quarter"])
        self.assertEqual("2027 H2", timing_label(milestones["MS-HC26-MOP-PRODUCTION"], "en"))

    def test_bilingual_page_and_offline_dom_events(self):
        node = os.environ.get("OPENFS_NODE") or shutil.which("node")
        if not node: self.skipTest("Node.js is required for offline DOM checks")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            build(ROOT, output)
            page = (output / "conferences/hot-chips-2026/index.html").read_text()
            self.assertIn("../../assets/branding/openfs-logo-compact.svg", page)
            self.assertNotIn("{{", page)
            env = dict(os.environ, OPENFS_TEST_PUBLIC_DATA=str(output / "data/openfs-public.js"))
            result = subprocess.run([node, "--test", "tests/test_conference_ui.js"], cwd=ROOT,
                                    env=env, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
