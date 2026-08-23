from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from consensus_gate import evaluate  # noqa: E402


def read_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class ConsensusGateTests(unittest.TestCase):
    def setUp(self):
        self.policy = read_json("config/consensus-policy.json")
        self.proposal = read_json("evals/golden/accepted-proposal.json")
        self.assessments = read_json("evals/golden/accepted-assessments.json")

    def test_accepts_when_agent_and_source_independence_pass(self):
        decision = evaluate(self.proposal, self.assessments, self.policy)
        self.assertEqual("accepted", decision["outcome"])

    def test_shared_origin_is_not_independent_corroboration(self):
        proposal = read_json("evals/adversarial/shared-origin-proposal.json")
        assessments = copy.deepcopy(self.assessments)
        for assessment in assessments:
            assessment["proposal_id"] = proposal["proposal_id"]
        decision = evaluate(proposal, assessments, self.policy)
        self.assertEqual("provisional", decision["outcome"])
        self.assertFalse(decision["policy_result"]["checks"]["minimum_origin_groups"])

    def test_critical_objection_blocks_acceptance(self):
        assessments = copy.deepcopy(self.assessments)
        assessments[2]["objections"] = [
            {"severity": "critical", "message": "The quotation contradicts the claim."}
        ]
        decision = evaluate(self.proposal, assessments, self.policy)
        self.assertEqual("contested", decision["outcome"])

    def test_duplicate_reviewer_is_counted_once(self):
        assessments = copy.deepcopy(self.assessments)
        assessments[1]["reviewer_agent_id"] = assessments[0]["reviewer_agent_id"]
        decision = evaluate(self.proposal, assessments, self.policy)
        self.assertEqual("provisional", decision["outcome"])
        self.assertEqual(2, decision["policy_result"]["counts"]["assessments"])


if __name__ == "__main__":
    unittest.main()
