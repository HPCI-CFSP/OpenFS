import json
import unittest
from pathlib import Path

from tools.build_topic_page_layouts import (
    active_topics,
    build_default_layout,
    load_json,
    missing_layout_ids,
    populate_layouts,
    roadmap_index,
    stale_generated_layout_ids,
)


ROOT = Path(__file__).resolve().parents[1]


class TopicPageLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline = load_json(ROOT / "config/research-baseline.json")
        cls.portfolio = load_json(ROOT / "config/roadmap-portfolio.json")
        cls.support = load_json(ROOT / "knowledge/public/topic-decision-support.json")

    def test_every_active_topic_has_a_layout(self):
        self.assertEqual(missing_layout_ids(self.baseline, self.support), [])

    def test_population_is_idempotent(self):
        updated, changed = populate_layouts(
            self.baseline, self.portfolio, self.support
        )
        self.assertEqual(changed, [])
        self.assertEqual(updated, self.support)

    def test_generated_layouts_are_current(self):
        self.assertEqual(
            stale_generated_layout_ids(self.baseline, self.portfolio, self.support), []
        )

    def test_default_layout_assigns_each_active_section_once(self):
        topic = next(item for item in self.baseline["topics"] if item["topic_id"] == "ARCH-02")
        profile = next(
            item for item in self.support["topic_profiles"] if item["topic_id"] == "ARCH-02"
        )
        layout = build_default_layout(
            topic, profile, roadmap_index(self.portfolio)["ARCH-02"]
        )
        section_ids = [
            section_id
            for component in layout["components"]
            if component["type"] == "research-unit"
            for section_id in component["section_ids"]
        ]
        active_section_ids = [
            section["section_id"]
            for section in profile["sections"]
            if section["section_id"] not in set(profile.get("archived_section_ids", []))
        ]
        self.assertCountEqual(section_ids, active_section_ids)
        self.assertEqual(len(section_ids), len(set(section_ids)))
        self.assertEqual(layout["layout_mode"], "generated")
        self.assertEqual(layout["components"][2]["type"], "topic-comparisons")

    def test_active_topic_count_is_the_public_catalog_count(self):
        self.assertEqual(len(active_topics(self.baseline)), 40)


if __name__ == "__main__":
    unittest.main()
