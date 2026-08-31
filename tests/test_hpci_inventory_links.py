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

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_pages_site import build, link_inventory_evidence
from check_public_planning_surfaces import validate_inventory_links


def read(relative):
    return json.loads((ROOT / relative).read_text())


class InventoryEvidenceLinkTests(unittest.TestCase):
    def test_roadmap_ui_deep_links_offline(self):
        node = os.environ.get("OPENFS_NODE") or shutil.which("node")
        if not node:
            self.skipTest("Node.js is required for UI event tests")
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            public = build(ROOT, output)
            projected = {p["topic_id"]: p for p in public["topic_decision_support"]["topic_profiles"]}
            original = read("knowledge/public/topic-decision-support.json")
            for profile in original["topic_profiles"]:
                if profile["topic_id"] not in projected:
                    continue
                archived = set(profile.get("archived_section_ids", []))
                visible = {s["section_id"] for s in projected[profile["topic_id"]]["sections"]}
                self.assertFalse(archived & visible)
                self.assertEqual({s["section_id"] for s in profile["sections"]} - archived, visible)
            current = projected["CROSS-08"]
            self.assertIn("TDS-CBL-CHANGES-V2", [s["section_id"] for s in current["sections"]])
            self.assertEqual("incomplete", current["research_updates"][-1]["consensus_status"])
            env = dict(os.environ, OPENFS_TEST_PUBLIC_DATA=str(output / "data/openfs-public.js"))
            result = subprocess.run([node, "--test", "tests/test_roadmap_ui.js", "tests/test_budget_ui.js", "tests/test_planning_ui.js"], cwd=ROOT,
                                    env=env, capture_output=True, text=True)
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def setUp(self):
        self.inventory = read("knowledge/public/hpci-system-inventory.json")
        self.register = read("knowledge/public/procurement-cost-register.json")
        self.roadmaps = [json.loads(path.read_text()) for path in (ROOT / "knowledge/public/roadmaps").glob("*.json")]

    def test_bidirectional_links_are_derived_and_idempotent(self):
        self.assertEqual([], validate_inventory_links(self.inventory, self.register, self.roadmaps))
        link_inventory_evidence(self.inventory, self.register, self.roadmaps)
        systems = {item["system_id"]: item for item in self.inventory["systems"]}
        for case in self.register["cases"]:
            self.assertEqual(case.get("linked_system_ids", []), [s["system_id"] for s in case["linked_systems"]])
            for system_id in case.get("linked_system_ids", []):
                self.assertIn(case["case_id"], [p["case_id"] for p in systems[system_id]["procurement_links"]])
            for linked in case["linked_systems"]:
                self.assertEqual("roadmaps/cross-cutting/reference-blueprint-centers/", linked["inventory_path"])
        before = copy.deepcopy((self.inventory, self.register))
        link_inventory_evidence(self.inventory, self.register, self.roadmaps)
        self.assertEqual(before, (self.inventory, self.register))

    def test_unknown_system_and_lifecycle_references_fail_closed(self):
        self.register["cases"][0]["linked_system_ids"] = ["HPCI-SYS-UNKNOWN"]
        self.assertTrue(validate_inventory_links(self.inventory, self.register, self.roadmaps))
        with self.assertRaises(ValueError):
            link_inventory_evidence(self.inventory, self.register, self.roadmaps)
        self.register["cases"][0]["linked_system_ids"] = []
        self.inventory["systems"][0]["lifecycle_milestone_refs"] = [
            {"roadmap_id": "RM-X-BLUEPRINT", "milestone_id": "MS-UNKNOWN"}]
        self.assertTrue(validate_inventory_links(self.inventory, self.register, self.roadmaps))

    def test_lifecycle_dates_are_not_copied_into_the_inventory_source(self):
        source_system = next(s for s in self.inventory["systems"] if s["system_id"] == "HPCI-SYS-SIRIUS")
        self.assertNotIn("lifecycle_events", source_system)
        milestone = next(m for r in self.roadmaps for lane in r["lanes"] for m in lane["milestones"]
                         if m["milestone_id"] == "MS-BLUE-TSUKUBA-SIRIUS-EXPANSION-UNDATED")
        self.assertIsNone(milestone["year"])
        self.assertEqual("no-public-date", milestone["timing_basis"])
        link_inventory_evidence(self.inventory, self.register, self.roadmaps)
        self.assertIsNone(source_system["lifecycle_events"][-1]["year"])
        self.assertEqual(24, source_system["specifications"]["node_count"])
        self.assertEqual("512 GiB (4 x 128 GiB unified memory)", source_system["specifications"]["node_memory"])
        self.assertEqual({"year": 2026, "quarter": "Q2"}, source_system["availability_windows"][0]["start"])
        self.assertEqual("incomplete", self.inventory["consensus_status"])

    def test_peak_scope_notes_need_bilingual_prose_and_registered_sources(self):
        system = next(s for s in self.inventory["systems"] if s["system_id"] == "HPCI-SYS-SIRIUS")
        self.assertEqual(490.4, system["specifications"]["node_peak_tf"])
        self.assertIn("496.08", system["performance_note"]["note_ja"])
        self.assertIn("OpenFS arithmetic", system["performance_note"]["note_en"])
        system["performance_note"]["source_ids"] = ["MISSING"]
        system["performance_note"]["note_en"] = ""
        errors = validate_inventory_links(self.inventory, self.register, self.roadmaps)
        self.assertEqual(2, len(errors))


if __name__ == "__main__":
    unittest.main()
