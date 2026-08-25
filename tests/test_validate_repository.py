from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from validate_repository import run, usage_summary_from_items  # noqa: E402


class RepositoryValidationTests(unittest.TestCase):
    def test_repository_structure_is_valid(self):
        self.assertEqual([], run(ROOT))

    def test_cost_summary_is_recomputed_from_completed_work_items(self):
        items = [
            {
                "status": "completed",
                "usage": {
                    "input_tokens": 10,
                    "output_tokens": 4,
                    "cost_usd": 0.25,
                },
            },
            {"status": "completed"},
            {"status": "queued", "usage": {"cost_usd": 99}},
        ]
        summary = usage_summary_from_items(items)
        self.assertEqual("partial", summary["measurement_status"])
        self.assertEqual(0.25, summary["reported_total_usd"])
        self.assertEqual(1, summary["reported_executions"])
        self.assertEqual(1, summary["unreported_executions"])
        self.assertEqual(10, summary["reported_input_tokens"])


if __name__ == "__main__":
    unittest.main()
