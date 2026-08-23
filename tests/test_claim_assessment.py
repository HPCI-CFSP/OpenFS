from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from create_assessment import create  # noqa: E402
from propose_claim import propose  # noqa: E402


def read_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class ClaimAssessmentTests(unittest.TestCase):
    def setUp(self):
        self.registry = read_json("config/agent-registry.json")
        self.bundle_ref = "proposals/evidence/RUN-OFS001-PILOT-001/WORK-000005.json"
        self.bundle = read_json(self.bundle_ref)

    def test_claim_preserves_evidence_and_source_lineage(self):
        proposal = propose(
            [self.bundle],
            bundle_refs=[self.bundle_ref],
            run_id="RUN-OFS001-PILOT-001",
            agent_id="synthesis-public-01",
            statement="CXL Consortium reported that CXL 4.0 supports 128 GT/s.",
            claim_kind="reported_claim",
            temporal_scope="as reported on 2025-11-18",
            registry=self.registry,
            created_at="2026-08-24T00:00:00Z",
        )
        self.assertEqual("claim", proposal["object_type"])
        self.assertEqual(
            self.bundle["evidence_candidates"][0]["evidence_id"],
            proposal["claim_candidate"]["evidence_ids"][0],
        )
        self.assertEqual(self.bundle["origin_group_ids"], proposal["origin_group_ids"])

    def test_assessment_identity_is_copied_from_registry(self):
        proposal = {
            "proposal_id": "PRP-CLM-000099",
            "object_type": "claim",
            "run_id": "RUN-OFS001-PILOT-001",
            "created_by_agent_id": "synthesis-public-01",
        }
        assessment = create(
            proposal,
            reviewer_agent_id="validator-public-01",
            verdict="uncertain",
            confidence=0.5,
            checks={"citation_entailment": "pass", "falsification_review": False},
            objections=[],
            registry=self.registry,
            base_commit="abc123",
            allow_disabled_pilot_agent=True,
            reviewed_at="2026-08-24T00:00:00Z",
        )
        self.assertEqual("OpenAI", assessment["reviewer_identity"]["provider"])
        self.assertEqual(
            "openai-gpt5-codex-interactive",
            assessment["agent_independence_group"],
        )

    def test_unconfigured_critic_cannot_create_assessment(self):
        proposal = {
            "proposal_id": "PRP-CLM-000099",
            "object_type": "claim",
            "run_id": "RUN-OFS001-PILOT-001",
            "created_by_agent_id": "synthesis-public-01",
        }
        with self.assertRaisesRegex(ValueError, "unconfigured provider"):
            create(
                proposal,
                reviewer_agent_id="critic-public-01",
                verdict="support",
                confidence=0.5,
                checks={},
                objections=[],
                registry=self.registry,
                base_commit="abc123",
                allow_disabled_pilot_agent=True,
            )


if __name__ == "__main__":
    unittest.main()
