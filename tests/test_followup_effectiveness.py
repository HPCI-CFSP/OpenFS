from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from evaluate_followup_effectiveness import evaluate, record  # noqa: E402


class FollowupEffectivenessTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.previous_run_id = "RUN-PREVIOUS"
        self.run_id = "RUN-CURRENT"
        plan_ref = f"runs/{self.run_id}/inputs/followups/plan.json"
        self.write_json(
            plan_ref,
            {
                "followup_plan_id": "CFP-TEST",
                "queries": [
                    {
                        "query_id": "CFQ-TEST",
                        "center_id": "CENTER-TEST",
                        "search_generation": 2,
                        "profile_fields": ["power", "facility"],
                    }
                ],
            },
        )
        self.write_json(
            f"runs/{self.run_id}/manifest.json",
            {
                "run_id": self.run_id,
                "followup_plan": {
                    "snapshot_ref": plan_ref,
                    "base_run_id": self.previous_run_id,
                },
                "metrics": {},
            },
        )
        self.write_profile(
            self.previous_run_id,
            {
                "power": {"status": "partial", "evidence_refs": ["EVD-OLD"]},
                "facility": {"status": "verified", "evidence_refs": ["EVD-OLD"]},
            },
        )

    def tearDown(self):
        self.temporary.cleanup()

    def write_json(self, relative: str, value: dict):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def write_profile(self, run_id: str, fields: dict):
        self.write_json(
            f"proposals/center-profiles/{run_id}/CENTER-TEST.json",
            {"center_id": "CENTER-TEST", **fields},
        )

    def test_reports_improved_and_refreshed_fields_as_effective(self):
        self.write_profile(
            self.run_id,
            {
                "power": {"status": "verified", "evidence_refs": ["EVD-NEW"]},
                "facility": {"status": "verified", "evidence_refs": ["EVD-NEW"]},
            },
        )

        report = evaluate(
            self.root,
            run_id=self.run_id,
            evaluated_at="2026-08-24T08:00:00Z",
        )

        self.assertEqual("effective", report["status"])
        self.assertEqual(1, report["effective_query_count"])
        self.assertEqual(1, report["field_outcomes"]["improved"])
        self.assertEqual(1, report["field_outcomes"]["refreshed"])
        manifest = record(self.root, report)
        self.assertEqual(
            "runs/RUN-CURRENT/followup-effectiveness.json",
            manifest["followup_effectiveness_ref"],
        )
        self.assertEqual(
            "effective",
            manifest["metrics"]["followup_effectiveness"]["status"],
        )

    def test_reports_unchanged_query_as_ineffective(self):
        self.write_profile(
            self.run_id,
            {
                "power": {"status": "partial", "evidence_refs": ["EVD-OLD"]},
                "facility": {"status": "verified", "evidence_refs": ["EVD-OLD"]},
            },
        )

        report = evaluate(self.root, run_id=self.run_id)

        self.assertEqual("ineffective", report["status"])
        self.assertEqual(0, report["effective_query_count"])
        self.assertEqual(2, report["field_outcomes"]["unchanged"])

    def test_missing_current_profile_is_a_regression(self):
        report = evaluate(self.root, run_id=self.run_id)

        self.assertEqual("ineffective", report["status"])
        self.assertEqual(2, report["field_outcomes"]["regressed"])
        self.assertEqual(
            "missing-profile",
            report["queries"][0]["field_results"][0]["current_status"],
        )


if __name__ == "__main__":
    unittest.main()
