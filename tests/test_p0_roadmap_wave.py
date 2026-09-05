from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.build_p0_dependency_wave import EDGES
from tools.build_p0_roadmap_wave import DECISION_ID, DIRECTIVE_ID, specifications


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SECOND_WAVE = {
    "RM-HW-FACILITY",
    "RM-SSW-RUNTIME",
    "RM-SSW-WORKFLOW",
    "RM-SSW-SECURITY",
    "RM-APP-AI",
    "RM-X-PROCUREMENT",
    "RM-X-OPERATIONS",
    "RM-X-HORIZON",
}


class P0RoadmapWaveTests(unittest.TestCase):
    def setUp(self):
        self.specs = specifications()
        self.roadmaps = []
        for spec in self.specs:
            path = ROOT / "knowledge/public/roadmaps" / spec["filename"]
            self.assertTrue(path.exists(), path)
            self.roadmaps.append(json.loads(path.read_text(encoding="utf-8")))

    def test_second_wave_is_complete_and_unique(self):
        self.assertEqual(EXPECTED_SECOND_WAVE, {item["roadmap_id"] for item in self.specs})
        self.assertEqual(len(self.specs), len({item["export_id"] for item in self.specs}))
        self.assertEqual(len(self.specs), len({item["filename"] for item in self.specs}))

    def test_generated_roadmaps_remain_provisional(self):
        for roadmap in self.roadmaps:
            with self.subTest(roadmap_id=roadmap["roadmap_id"]):
                self.assertEqual("provisional", roadmap["research_status"])
                self.assertEqual("incomplete", roadmap["consensus_status"])
                self.assertEqual(DIRECTIVE_ID, roadmap["publication"]["human_approval_directive_id"])
                self.assertEqual(DECISION_ID, roadmap["publication"]["publication_decision_id"])
                self.assertTrue(roadmap["coverage_gaps"])
                self.assertTrue(all(item["status"] == "open" for item in roadmap["coverage_gaps"]))

    def test_each_second_wave_roadmap_reaches_the_blueprint(self):
        self.assertEqual(EXPECTED_SECOND_WAVE, {item["upstream_roadmap_id"] for item in EDGES})
        self.assertTrue(all(item["downstream_roadmap_id"] == "RM-X-BLUEPRINT" for item in EDGES))

    def test_publication_directive_covers_roadmaps_and_readiness_surface(self):
        directive = json.loads(
            (ROOT / "reviews/directives" / f"{DIRECTIVE_ID}.json").read_text(
                encoding="utf-8"
            )
        )
        expected_targets = {item["export_id"] for item in self.specs}
        expected_targets.update(
            {
                "PLANNING-EVIDENCE-READINESS-001",
                "ROADMAP-DEPENDENCY-REGISTER-001",
            }
        )
        self.assertTrue(expected_targets.issubset(set(directive["publication_targets"])))


if __name__ == "__main__":
    unittest.main()
