from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class CatalogTaxonomyTests(unittest.TestCase):
    def setUp(self):
        self.taxonomy = read_json("config/catalog-taxonomy.json")
        self.baseline = read_json("config/research-baseline.json")
        self.portfolio = read_json("config/roadmap-portfolio.json")

    def test_six_categories_are_stable_and_ordered(self):
        self.assertEqual(
            [
                "architecture-hardware",
                "system-software-data-platform",
                "applications-workloads",
                "operations-facilities-security",
                "access-governance",
                "planning-evaluation-research",
            ],
            [category["category_id"] for category in self.taxonomy["categories"]],
        )
        self.assertEqual(list(range(1, 7)), [category["order"] for category in self.taxonomy["categories"]])

    def test_every_active_topic_is_assigned_exactly_once(self):
        active = {
            topic["topic_id"]
            for topic in self.baseline["topics"]
            if topic["status"] != "retired"
        }
        assigned = [
            topic_id
            for category in self.taxonomy["categories"]
            for topic_id in category["topic_ids"]
        ]
        self.assertEqual(len(assigned), len(set(assigned)))
        self.assertEqual(active, set(assigned))

    def test_every_roadmap_is_assigned_exactly_once(self):
        expected = {item["roadmap_id"] for item in self.portfolio["roadmap_families"]}
        assigned = [
            roadmap_id
            for category in self.taxonomy["categories"]
            for roadmap_id in category["roadmap_ids"]
        ]
        self.assertEqual(len(assigned), len(set(assigned)))
        self.assertEqual(expected, set(assigned))


if __name__ == "__main__":
    unittest.main()
