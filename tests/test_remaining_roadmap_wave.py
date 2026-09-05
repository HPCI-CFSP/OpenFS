from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.build_remaining_roadmap_wave import DECISION_ID, DIRECTIVE_ID, specifications


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "RM-HW-SOVEREIGNTY",
    "RM-SSW-PERFORMANCE",
    "RM-APP-REALTIME",
    "RM-APP-ADOPTION",
}


class RemainingRoadmapWaveTests(unittest.TestCase):
    def setUp(self):
        self.specs = specifications()
        self.roadmaps = [
            json.loads(
                (ROOT / "knowledge/public/roadmaps" / item["filename"]).read_text(
                    encoding="utf-8"
                )
            )
            for item in self.specs
        ]

    def test_all_remaining_families_are_generated_once(self):
        self.assertEqual(EXPECTED, {item["roadmap_id"] for item in self.specs})
        self.assertEqual(len(EXPECTED), len({item["export_id"] for item in self.specs}))
        self.assertEqual(len(EXPECTED), len({item["filename"] for item in self.specs}))

    def test_outputs_remain_provisional_and_evidence_bounded(self):
        for roadmap in self.roadmaps:
            with self.subTest(roadmap_id=roadmap["roadmap_id"]):
                self.assertEqual("provisional", roadmap["research_status"])
                self.assertEqual("incomplete", roadmap["consensus_status"])
                self.assertEqual("official-source-scan-incomplete", roadmap["coverage_status"])
                self.assertEqual(DIRECTIVE_ID, roadmap["publication"]["human_approval_directive_id"])
                self.assertEqual(DECISION_ID, roadmap["publication"]["publication_decision_id"])
                self.assertTrue(roadmap["coverage_gaps"])
                self.assertTrue(all(item["status"] == "open" for item in roadmap["coverage_gaps"]))
        self.assertTrue(
            any(
                item["timing_precision"] == "undated"
                for roadmap in self.roadmaps
                for lane in roadmap["lanes"]
                for item in lane["milestones"]
            )
        )

    def test_each_family_has_a_blueprint_dependency(self):
        for roadmap in self.roadmaps:
            with self.subTest(roadmap_id=roadmap["roadmap_id"]):
                self.assertEqual(1, len(roadmap["dependencies"]))
                dependency = roadmap["dependencies"][0]
                self.assertEqual(roadmap["roadmap_id"], dependency["upstream_roadmap_id"])
                self.assertEqual("RM-X-BLUEPRINT", dependency["downstream_roadmap_id"])

    def test_publication_directive_covers_every_export(self):
        directive = json.loads(
            (ROOT / "reviews/directives" / f"{DIRECTIVE_ID}.json").read_text(
                encoding="utf-8"
            )
        )
        targets = set(directive["publication_targets"])
        self.assertTrue({item["export_id"] for item in self.specs}.issubset(targets))


if __name__ == "__main__":
    unittest.main()
