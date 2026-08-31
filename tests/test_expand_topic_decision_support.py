from __future__ import annotations

import unittest
from datetime import date

from tools.expand_topic_decision_support import import_source, latest_research_date, next_milestone, timing_text


class TopicDecisionSupportGenerationTests(unittest.TestCase):
    def test_first_party_research_does_not_imply_peer_review(self):
        source = {"source_id": "SRC-TEST", "title": "Author research artifact",
                  "publisher": "Research authors", "url": "https://example.org/research",
                  "source_class": "academic-primary", "published_at": "2026-05-27"}
        imported = import_source(source)
        self.assertEqual("research-artifact", imported["source_class"])
        self.assertEqual("2026-05-27", imported["published_or_updated"])
        self.assertEqual("academic-primary", source["source_class"])

    def test_source_import_does_not_invent_a_retrieval_date(self):
        source = {"source_id": "SRC-TEST", "title": "Undated project page",
                  "publisher": "Project", "url": "https://example.org/project",
                  "source_class": "project-official"}
        imported = import_source(source)
        self.assertEqual("Publication/update date not provided", imported["published_or_updated"])
        self.assertEqual("official-project", imported["source_class"])
        source["updated_at"] = "2026-08-31"
        self.assertEqual("2026-08-31", import_source(source)["published_or_updated"])

    def test_latest_roadmap_date_advances_the_generated_catalog(self):
        selected = latest_research_date(
            {"as_of": "2026-08-27"},
            [{"as_of": "2026-08-28"}, {"as_of": "2026-08-28"}],
        )
        self.assertEqual(date(2026, 8, 28), selected)

    def test_next_milestone_excludes_completed_quarters(self):
        lanes = [
            {
                "track_id": "TRACK-1",
                "milestones": [
                    {
                        "milestone_id": "PAST",
                        "year": 2026,
                        "quarter": "Q1",
                        "timing_basis": "standard-release",
                    },
                    {
                        "milestone_id": "FUTURE",
                        "year": 2026,
                        "quarter": "Q4",
                        "timing_basis": "vendor-target",
                    },
                ],
            }
        ]

        selected = next_milestone("TRACK-1", lanes, date(2026, 8, 27))

        self.assertIsNotNone(selected)
        self.assertEqual("FUTURE", selected["milestone_id"])

    def test_second_half_window_remains_future_in_third_quarter(self):
        lanes = [
            {
                "track_id": "TRACK-1",
                "milestones": [
                    {
                        "milestone_id": "H2",
                        "year": 2026,
                        "quarter": None,
                        "half": "H2",
                        "timing_basis": "vendor-target",
                    }
                ],
            }
        ]

        selected = next_milestone("TRACK-1", lanes, date(2026, 8, 27))

        self.assertIsNotNone(selected)
        self.assertEqual("H2", selected["milestone_id"])

    def test_timing_text_preserves_available_precision(self):
        self.assertEqual(
            "2026年後半（H2）",
            timing_text({"year": 2026, "quarter": None, "half": "H2"}, "ja"),
        )
        self.assertEqual(
            "H2 2026",
            timing_text({"year": 2026, "quarter": None, "half": "H2"}, "en"),
        )
        self.assertEqual(
            "2027年（四半期未公表）",
            timing_text({"year": 2027, "quarter": None}, "ja"),
        )

    def test_cross_year_window_is_not_reduced_to_its_start_quarter(self):
        item = {"milestone_id": "FY2026", "year": 2026, "quarter": "Q2",
                "end_year": 2027, "end_quarter": "Q1", "timing_precision": "quarter-range",
                "timing_basis": "vendor-target"}
        lanes = [{"track_id": "TRACK-1", "milestones": [item]}]
        self.assertEqual(item, next_milestone("TRACK-1", lanes, date(2026, 12, 31)))
        self.assertIsNone(next_milestone("TRACK-1", lanes, date(2027, 4, 1)))
        self.assertEqual("2026年Q2〜2027年Q1", timing_text(item, "ja"))
        self.assertEqual("2026 Q2 - 2027 Q1", timing_text(item, "en"))


if __name__ == "__main__":
    unittest.main()
