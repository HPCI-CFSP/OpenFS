from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from evaluate_promotion_readiness import evaluate, record  # noqa: E402


class PromotionReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.run_id = "RUN-TEST"
        self.write(
            f"runs/{self.run_id}/manifest.json",
            {"run_id": self.run_id, "metrics": {}},
        )
        self.write(
            f"runs/{self.run_id}/inputs/config/consensus-policy.json",
            {"policy_id": "POLICY-TEST", "calibration_status": "calibrated"},
        )

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, ref, value):
        path = self.root / ref
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def add_claim(self, number, kind="observed_fact", outcome="accepted"):
        proposal_id = f"PRP-CLM-{number:06d}"
        proposal_ref = f"proposals/claims/{self.run_id}/WORK-{number:06d}.json"
        self.write(
            proposal_ref,
            {
                "proposal_id": proposal_id,
                "run_id": self.run_id,
                "claim_candidate": {
                    "claim_id": f"CLM-{number:06d}",
                    "claim_kind": kind,
                },
            },
        )
        self.write(
            f"decisions/{self.run_id}/{proposal_id}.json",
            {
                "proposal_id": proposal_id,
                "outcome": outcome,
                "policy_id": "POLICY-TEST",
                "policy_result": {"checks": {"all_requirements": outcome == "accepted"}},
            },
        )
        return proposal_ref

    def test_classifies_eligible_provisional_and_recommendation_claims(self):
        self.add_claim(1)
        self.add_claim(2, outcome="provisional")
        self.add_claim(3, kind="recommendation")

        report = evaluate(
            self.root,
            run_id=self.run_id,
            evaluated_at="2026-08-24T00:00:00Z",
        )
        statuses = {item["claim_id"]: item["status"] for item in report["claims"]}
        self.assertEqual("eligible", statuses["CLM-000001"])
        self.assertEqual("decision-not-accepted", statuses["CLM-000002"])
        self.assertEqual("recommendation-gate-required", statuses["CLM-000003"])
        self.assertEqual(1, report["summary"]["eligible_count"])
        self.assertEqual(2, report["summary"]["blocked_count"])

        output = record(self.root, report)
        self.assertTrue(output.is_file())
        manifest = json.loads(
            (self.root / "runs" / self.run_id / "manifest.json").read_text()
        )
        self.assertEqual(
            f"runs/{self.run_id}/promotion-readiness.json",
            manifest["promotion_readiness_ref"],
        )

    def test_dependency_impact_blocks_otherwise_eligible_claim(self):
        proposal_ref = self.add_claim(1)
        self.write(
            "runs/RUN-LATER/dependency-impact.json",
            {
                "impacts": [
                    {
                        "canonical_url": "https://example.org/changed",
                        "classification": "changed",
                        "promotion_blocked": True,
                        "claim_proposal_refs": [proposal_ref],
                    }
                ]
            },
        )

        report = evaluate(self.root, run_id=self.run_id)
        self.assertEqual("dependency-impact-blocked", report["claims"][0]["status"])
        self.assertEqual(0, report["summary"]["eligible_count"])


if __name__ == "__main__":
    unittest.main()
