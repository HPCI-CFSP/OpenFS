from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.build_center_profile_assurance import build


ROOT = Path(__file__).resolve().parents[1]


class CenterProfileAssuranceTests(unittest.TestCase):
    def test_committed_projection_is_deterministic_and_keeps_contract_gaps_open(self):
        expected = json.loads(
            (ROOT / "knowledge/public/audits/center-profile-assurance.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(expected, build(ROOT, run_id=expected["source_run_id"]))
        self.assertEqual(15, expected["summary"]["center_count"])
        self.assertEqual(0, expected["summary"]["accepted_current_count"])
        self.assertEqual(30, expected["summary"]["not_collected"])
        self.assertEqual(
            {"budget", "procurement"},
            {
                item["field"]
                for item in expected["field_summary"]
                if item["not_collected"] == 15
            },
        )
        self.assertTrue(all(item["status"] == "open" for item in expected["gap_status"]))


if __name__ == "__main__":
    unittest.main()
