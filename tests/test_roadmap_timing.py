import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from roadmap_timing import milestone_quarter_window, quarter_ordinal


def event(**changes):
    return {
        "milestone_id": "MS-TIMING-TEST", "year": 2026, "quarter": "Q2",
        "half": None, "timing_precision": "quarter", "maturity": "target",
        "event_type": "product", "timing_basis": "vendor-target",
        "comparison_priority": "key", "source_ids": ["SRC-TEST"],
        "dependency_refs": [], "label_ja": "試験", "label_en": "Test",
        "detail_ja": "試験用", "detail_en": "Test fixture", **changes,
    }


class MilestoneTimingTests(unittest.TestCase):
    def setUp(self):
        schema = json.loads((ROOT / "schemas/public-roadmap.schema.json").read_text())
        self.schema = Draft202012Validator({"$defs": schema["$defs"], **schema["$defs"]["milestone"]})

    def test_supported_windows(self):
        cases = [
            (event(), (2026 * 4 + 1, 2026 * 4 + 1)),
            (event(quarter=None, timing_precision="half-year", half="H1"), (8104, 8105)),
            (event(quarter=None, timing_precision="half-year", half="H2"), (8106, 8107)),
            (event(quarter=None, timing_precision="year"), (8104, 8107)),
            (event(timing_precision="quarter-range", end_year=2027, end_quarter="Q1"), (8105, 8108)),
            (event(timing_precision="quarter-range", end_year=2026, end_quarter="Q2"), (8105, 8105)),
            (event(year=None, quarter=None, timing_precision="undated", timing_basis="no-public-date"), None),
        ]
        for milestone, expected in cases:
            with self.subTest(milestone=milestone):
                self.schema.validate(milestone)
                self.assertEqual(expected, milestone_quarter_window(milestone))

    def test_schema_and_runtime_reject_inconsistent_fields(self):
        for milestone in [
            event(timing_precision="quarter-range"),
            event(timing_precision="quarter-range", end_year=2027, end_quarter=None),
            event(timing_precision="quarter-range", end_year=True, end_quarter="Q1"),
            event(timing_precision="quarter-range", end_year=2027, end_quarter="Q5"),
            event(end_year=2027, end_quarter="Q1"),
            event(quarter=None),
            event(year=None),
            event(timing_precision="year"),
            event(quarter=None, timing_precision="half-year"),
            event(half="H1"),
            event(timing_precision="undated"),
        ]:
            with self.subTest(milestone=milestone):
                self.assertTrue(list(self.schema.iter_errors(milestone)))
                with self.assertRaises(ValueError):
                    milestone_quarter_window(milestone)

    def test_reversed_range_rejected_semantically(self):
        for end_year, end_quarter in [(2025, "Q4"), (2026, "Q1")]:
            with self.assertRaisesRegex(ValueError, "reversed"):
                milestone_quarter_window(event(timing_precision="quarter-range", end_year=end_year, end_quarter=end_quarter))

    def test_quarter_ordinal_validates_input(self):
        for year, quarter in [(True, "Q1"), (2026, "Q0"), (None, "Q1"), (2019, "Q4"), (2026, [])]:
            with self.assertRaises(ValueError):
                quarter_ordinal(year, quarter)


if __name__ == "__main__":
    unittest.main()
