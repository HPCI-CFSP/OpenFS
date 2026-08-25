from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class RoadmapPortfolioTests(unittest.TestCase):
    def setUp(self):
        self.baseline = json.loads(
            (ROOT / "config" / "research-baseline.json").read_text(encoding="utf-8")
        )
        self.portfolio = json.loads(
            (ROOT / "config" / "roadmap-portfolio.json").read_text(encoding="utf-8")
        )

    def test_portfolio_matches_baseline_and_covers_every_topic(self):
        self.assertEqual(self.baseline["baseline_id"], self.portfolio["baseline_id"])
        baseline_ids = {topic["topic_id"] for topic in self.baseline["topics"]}
        mapped_ids = {
            topic_id
            for roadmap in self.portfolio["roadmap_families"]
            for topic_id in roadmap["source_topic_ids"]
        }
        self.assertEqual(baseline_ids, mapped_ids)

    def test_portfolio_has_unique_ids_slugs_and_all_decision_domains(self):
        roadmaps = self.portfolio["roadmap_families"]
        self.assertEqual(
            len(roadmaps), len({roadmap["roadmap_id"] for roadmap in roadmaps})
        )
        self.assertEqual(len(roadmaps), len({roadmap["slug"] for roadmap in roadmaps}))
        self.assertEqual(
            {"hardware", "system-software", "applications", "cross-cutting"},
            {roadmap["domain"] for roadmap in roadmaps},
        )

    def test_published_portfolio_entries_name_their_public_artifacts(self):
        status_counts = Counter(
            roadmap["status"] for roadmap in self.portfolio["roadmap_families"]
        )
        self.assertEqual(1, status_counts["published"])
        for roadmap in self.portfolio["roadmap_families"]:
            if roadmap["status"] == "published":
                self.assertTrue(roadmap["published_artifact_ids"])
            else:
                self.assertEqual([], roadmap["published_artifact_ids"])

    def test_quarter_is_the_default_timeline_granularity(self):
        self.assertEqual(
            "quarter", self.portfolio["planning_horizon"]["default_granularity"]
        )


if __name__ == "__main__":
    unittest.main()
