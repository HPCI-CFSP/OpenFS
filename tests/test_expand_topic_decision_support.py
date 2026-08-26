from __future__ import annotations

import unittest
from datetime import date

from tools.expand_topic_decision_support import next_milestone, timing_text


class TopicDecisionSupportGenerationTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
