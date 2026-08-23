from __future__ import annotations

import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from promote_claim import prepare_canonical_claim, promote  # noqa: E402
from prepare_claim_promotions import prepare as prepare_promotions  # noqa: E402
from validate_repository import validate_canonical_claims  # noqa: E402


class ClaimPromotionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.run_id = "RUN-PILOT-TEST"
        self.proposal_ref = f"proposals/claims/{self.run_id}/WORK-000003.json"
        self.decision_ref = f"decisions/{self.run_id}/PRP-CLM-000001.json"
        self.bundle_ref = f"proposals/evidence/{self.run_id}/WORK-000002.json"
        self.bundle = {
            "run_id": self.run_id,
            "evidence_candidates": [
                {
                    "evidence_id": "EVD-000001",
                    "source_lineage_id": "LIN-000001",
                }
            ],
        }
        self.proposal = {
            "proposal_id": "PRP-CLM-000001",
            "object_type": "claim",
            "run_id": self.run_id,
            "artifact_id": "CLM-000001",
            "evidence_bundle_refs": [self.bundle_ref],
            "claim_candidate": {
                "schema_version": "0.1.0",
                "claim_id": "CLM-000001",
                "statement": "A tested public fact.",
                "claim_kind": "observed_fact",
                "temporal_scope": "2026-08-24",
                "conditions": [],
                "evidence_ids": ["EVD-000001"],
                "source_lineage_ids": ["LIN-000001"],
                "status": "candidate",
            },
        }
        self.decision = {
            "proposal_id": "PRP-CLM-000001",
            "object_type": "claim",
            "outcome": "accepted",
            "policy_id": "POLICY-TEST",
            "policy_result": {"checks": {"all_requirements": True}},
        }
        self.policy = {
            "policy_id": "POLICY-TEST",
            "calibration_status": "calibrated",
        }
        self.write(self.proposal_ref, self.proposal)
        self.write(self.decision_ref, self.decision)
        self.write(self.bundle_ref, self.bundle)
        self.write(
            f"runs/{self.run_id}/inputs/config/consensus-policy.json",
            self.policy,
        )

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, ref, value):
        path = self.root / ref
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_accepted_claim_promotes_idempotently_with_provenance(self):
        output, canonical = promote(
            self.root,
            proposal_ref=self.proposal_ref,
            decision_ref=self.decision_ref,
            promoted_at="2026-08-24T00:00:00Z",
        )
        self.assertEqual(
            self.root / "knowledge" / "claims" / "CLM-000001.json", output
        )
        self.assertEqual("accepted", canonical["claim"]["status"])
        self.assertEqual(self.proposal_ref, canonical["provenance"]["proposal_ref"])
        self.assertEqual(64, len(canonical["promotion_digest"]))
        index = json.loads(
            (self.root / "knowledge" / "claims" / "index.json").read_text()
        )
        self.assertEqual(1, index["claim_count"])
        self.assertIn(
            "A tested public fact.", (self.root / "TBD.md").read_text()
        )

        second_output, second = promote(
            self.root,
            proposal_ref=self.proposal_ref,
            decision_ref=self.decision_ref,
            promoted_at="2026-08-25T00:00:00Z",
        )
        self.assertEqual(output, second_output)
        self.assertEqual(canonical, second)

    def test_provisional_or_uncalibrated_result_cannot_promote(self):
        decision = deepcopy(self.decision)
        decision["outcome"] = "provisional"
        with self.assertRaisesRegex(ValueError, "accepted Decision"):
            prepare_canonical_claim(
                self.proposal,
                decision,
                self.policy,
                [self.bundle],
                proposal_ref=self.proposal_ref,
                decision_ref=self.decision_ref,
                dependency_impact_refs_checked=[],
                promoted_at="2026-08-24T00:00:00Z",
            )

        policy = deepcopy(self.policy)
        policy["calibration_status"] = "uncalibrated"
        with self.assertRaisesRegex(ValueError, "uncalibrated"):
            prepare_canonical_claim(
                self.proposal,
                self.decision,
                policy,
                [self.bundle],
                proposal_ref=self.proposal_ref,
                decision_ref=self.decision_ref,
                dependency_impact_refs_checked=[],
                promoted_at="2026-08-24T00:00:00Z",
            )

    def test_recommendation_requires_separate_human_gate(self):
        proposal = deepcopy(self.proposal)
        proposal["claim_candidate"]["claim_kind"] = "recommendation"
        with self.assertRaisesRegex(ValueError, "Recommendation Gate"):
            prepare_canonical_claim(
                proposal,
                self.decision,
                self.policy,
                [self.bundle],
                proposal_ref=self.proposal_ref,
                decision_ref=self.decision_ref,
                dependency_impact_refs_checked=[],
                promoted_at="2026-08-24T00:00:00Z",
            )

    def test_unresolved_dependency_impact_blocks_promotion(self):
        self.write(
            "runs/RUN-LATER/dependency-impact.json",
            {
                "impacts": [
                    {
                        "canonical_url": "https://example.org/changed",
                        "classification": "changed",
                        "promotion_blocked": True,
                        "claim_proposal_refs": [self.proposal_ref],
                    }
                ]
            },
        )
        with self.assertRaisesRegex(RuntimeError, "dependency impact"):
            promote(
                self.root,
                proposal_ref=self.proposal_ref,
                decision_ref=self.decision_ref,
            )

    def test_repository_validator_detects_post_promotion_tampering(self):
        promote(
            self.root,
            proposal_ref=self.proposal_ref,
            decision_ref=self.decision_ref,
            promoted_at="2026-08-24T00:00:00Z",
        )
        self.assertEqual([], validate_canonical_claims(self.root))

        changed = deepcopy(self.decision)
        changed["outcome"] = "provisional"
        self.write(self.decision_ref, changed)
        errors = validate_canonical_claims(self.root)
        self.assertTrue(any("Decision digest differs" in error for error in errors))
        self.assertTrue(any("Decision is not accepted" in error for error in errors))

    def test_batch_preparation_promotes_only_readiness_eligible_claims(self):
        self.write(
            f"runs/{self.run_id}/promotion-readiness.json",
            {
                "run_id": self.run_id,
                "claims": [
                    {
                        "status": "eligible",
                        "proposal_ref": self.proposal_ref,
                        "decision_ref": self.decision_ref,
                    }
                ],
            },
        )
        summary = prepare_promotions(
            self.root, promoted_at="2026-08-24T02:00:00Z"
        )
        self.assertEqual(1, summary["prepared_count"])
        self.assertEqual(["RUN-PILOT-TEST"], summary["affected_run_ids"])
        self.assertIn("knowledge/claims/CLM-000001.json", summary["outputs"])
        self.assertIn("TBD.md", summary["outputs"])

    def test_batch_preparation_is_noop_without_eligible_claims(self):
        summary = prepare_promotions(self.root, promoted_at="2026-08-24T02:00:00Z")
        self.assertEqual(0, summary["prepared_count"])
        self.assertEqual([], summary["outputs"])


if __name__ == "__main__":
    unittest.main()
