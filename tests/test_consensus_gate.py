from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))

from consensus_gate import evaluate, validate_assignment  # noqa: E402
from consensus_test_helpers import registry_bound_case  # noqa: E402


def read_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class ConsensusGateTests(unittest.TestCase):
    def setUp(self):
        self.policy = read_json("config/consensus-policy.json")
        self.proposal = read_json("evals/golden/accepted-proposal.json")
        self.assessments = read_json("evals/golden/accepted-assessments.json")
        self.registry, self.assessments = registry_bound_case(
            self.proposal, self.assessments
        )

    def test_accepts_when_agent_and_source_independence_pass(self):
        decision = evaluate(self.proposal, self.assessments, self.policy, self.registry)
        self.assertEqual("accepted", decision["outcome"])

    def test_shared_origin_is_not_independent_corroboration(self):
        proposal = read_json("evals/adversarial/shared-origin-proposal.json")
        assessments = copy.deepcopy(self.assessments)
        for assessment in assessments:
            assessment["proposal_id"] = proposal["proposal_id"]
        decision = evaluate(proposal, assessments, self.policy, self.registry)
        self.assertEqual("provisional", decision["outcome"])
        self.assertFalse(decision["policy_result"]["checks"]["minimum_origin_groups"])

    def test_critical_objection_blocks_acceptance(self):
        assessments = copy.deepcopy(self.assessments)
        assessments[2]["objections"] = [
            {"severity": "critical", "message": "The quotation contradicts the claim."}
        ]
        decision = evaluate(self.proposal, assessments, self.policy, self.registry)
        self.assertEqual("contested", decision["outcome"])

    def test_duplicate_reviewer_is_counted_once(self):
        assessments = copy.deepcopy(self.assessments)
        assessments[1]["reviewer_agent_id"] = assessments[0]["reviewer_agent_id"]
        decision = evaluate(self.proposal, assessments, self.policy, self.registry)
        self.assertEqual("provisional", decision["outcome"])
        self.assertEqual(2, decision["policy_result"]["counts"]["assessments"])

    def test_self_declared_independence_group_cannot_spoof_registry(self):
        assessments = copy.deepcopy(self.assessments)
        assessments[0]["agent_independence_group"] = "invented-independent-model"
        decision = evaluate(self.proposal, assessments, self.policy, self.registry)
        self.assertEqual("provisional", decision["outcome"])
        self.assertFalse(decision["policy_result"]["checks"]["valid_assessment_identities"])
        self.assertIn(
            "independence-group-mismatch",
            decision["policy_result"]["invalid_assessments"][0]["reason"],
        )

    def test_proposal_author_group_does_not_count_as_independent_support(self):
        assessments = copy.deepcopy(self.assessments)
        reviewer_id = assessments[0]["reviewer_agent_id"]
        for agent in self.registry["agents"]:
            if agent["agent_id"] == reviewer_id:
                agent["agent_independence_group"] = "test-author-group"
        digest = __import__("openfs_runtime").stable_digest(self.registry)
        for assessment in assessments:
            assessment["agent_registry_digest"] = digest
        assessments[0]["agent_independence_group"] = "test-author-group"
        decision = evaluate(self.proposal, assessments, self.policy, self.registry)
        self.assertNotIn(
            "test-author-group",
            decision["policy_result"]["support_independence_groups"],
        )

    def test_decision_time_can_be_pinned_to_the_work_item_lease(self):
        decision = evaluate(
            self.proposal,
            self.assessments,
            self.policy,
            self.registry,
            decided_at="2026-08-23T18:00:00Z",
        )
        self.assertEqual("2026-08-23T18:00:00Z", decision["decided_at"])

    def test_consensus_assignment_rejects_assessment_substitution(self):
        work_item = {
            "kind": "consensus",
            "status": "leased",
            "lease": {"agent_id": "consensus-agent"},
            "payload": {
                "proposal_assessment_pairs": [
                    {
                        "proposal_ref": "proposals/claims/RUN-1/WORK-000001.json",
                        "assessment_refs": [
                            "assessments/RUN-1/WORK-000002.json"
                        ],
                    }
                ]
            },
            "output_paths": ["decisions/RUN-1/CLM-1.json"],
        }
        with self.assertRaisesRegex(ValueError, "Assessment references differ"):
            validate_assignment(
                work_item,
                agent_id="consensus-agent",
                proposal_ref="proposals/claims/RUN-1/WORK-000001.json",
                assessment_refs=["assessments/RUN-1/WORK-999999.json"],
                output_ref="decisions/RUN-1/CLM-1.json",
            )

    def test_consensus_assignment_rejects_output_substitution(self):
        work_item = {
            "kind": "consensus",
            "status": "leased",
            "lease": {"agent_id": "consensus-agent"},
            "payload": {
                "proposal_assessment_pairs": [
                    {
                        "proposal_ref": "proposals/claims/RUN-1/WORK-000001.json",
                        "assessment_refs": [
                            "assessments/RUN-1/WORK-000002.json"
                        ],
                    }
                ]
            },
            "output_paths": ["decisions/RUN-1/CLM-1.json"],
        }
        with self.assertRaisesRegex(ValueError, "outside"):
            validate_assignment(
                work_item,
                agent_id="consensus-agent",
                proposal_ref="proposals/claims/RUN-1/WORK-000001.json",
                assessment_refs=["assessments/RUN-1/WORK-000002.json"],
                output_ref="decisions/RUN-1/CLM-OTHER.json",
            )


if __name__ == "__main__":
    unittest.main()
