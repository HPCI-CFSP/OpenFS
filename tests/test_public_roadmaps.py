from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_P0_WAVE = {
    "RM-HW-COMPUTE",
    "RM-HW-MEMORY",
    "RM-HW-INTERCONNECT",
    "RM-SSW-PORTABILITY",
    "RM-APP-WORKLOADS",
    "RM-X-BLUEPRINT",
}


class PublicRoadmapTests(unittest.TestCase):
    def setUp(self):
        self.roadmaps = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((ROOT / "knowledge" / "public" / "roadmaps").glob("*.json"))
        ]
        self.portfolio = json.loads(
            (ROOT / "config" / "roadmap-portfolio.json").read_text(encoding="utf-8")
        )

    def test_published_roadmaps_preserve_initial_wave_and_match_portfolio(self):
        actual = {item["roadmap_id"] for item in self.roadmaps}
        self.assertLessEqual(EXPECTED_P0_WAVE, actual)
        self.assertIn("RM-HW-STORAGE", actual)
        published = {
            item["roadmap_id"]
            for item in self.portfolio["roadmap_families"]
            if item["status"] == "published"
        }
        self.assertEqual(actual, published)

    def test_every_milestone_is_sourced_and_quarter_precision_is_explicit(self):
        for roadmap in self.roadmaps:
            source_ids = {item["source_id"] for item in roadmap["sources"]}
            for lane in roadmap["lanes"]:
                for milestone in lane["milestones"]:
                    self.assertTrue(milestone["source_ids"])
                    self.assertLessEqual(set(milestone["source_ids"]), source_ids)
                    if milestone["quarter"] is not None:
                        self.assertEqual("quarter", milestone["timing_precision"])
                    if milestone["year"] is None:
                        self.assertEqual("undated", milestone["timing_precision"])
                        self.assertEqual("no-public-date", milestone["timing_basis"])

    def test_openfs_plans_are_only_hpci_gates(self):
        gates = []
        for roadmap in self.roadmaps:
            for lane in roadmap["lanes"]:
                for milestone in lane["milestones"]:
                    if milestone["timing_basis"] == "openfs-provisional-plan":
                        gates.append(milestone)
                        self.assertIn(
                            milestone["event_type"], {"hpci-evaluation", "hpci-adoption"}
                        )
        self.assertTrue(gates)

    def test_coverage_gaps_are_actionable_and_dependency_graph_is_connected(self):
        graph = {roadmap["roadmap_id"]: set() for roadmap in self.roadmaps}
        for roadmap in self.roadmaps:
            self.assertTrue(roadmap["coverage_gaps"])
            for gap in roadmap["coverage_gaps"]:
                self.assertIn(gap["priority"], {"P0", "P1", "P2"})
                self.assertTrue(gap["impact_ja"] and gap["impact_en"])
                self.assertTrue(gap["next_action_ja"] and gap["next_action_en"])
            for dependency in roadmap["dependencies"]:
                upstream = dependency["upstream_roadmap_id"]
                downstream = dependency["downstream_roadmap_id"]
                if upstream in graph and downstream in graph:
                    graph[upstream].add(downstream)
                    graph[downstream].add(upstream)
        visited = set()
        pending = [next(iter(EXPECTED_P0_WAVE))]
        while pending:
            current = pending.pop()
            if current in visited:
                continue
            visited.add(current)
            pending.extend(graph[current] - visited)
        self.assertEqual(set(graph), visited)

    def test_consensus_is_not_overstated(self):
        for roadmap in self.roadmaps:
            self.assertEqual("provisional", roadmap["research_status"])
            self.assertEqual("incomplete", roadmap["consensus_status"])
            self.assertTrue(roadmap["caveat_ja"] and roadmap["caveat_en"])


if __name__ == "__main__":
    unittest.main()
