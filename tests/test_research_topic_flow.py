from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tests"))

from consensus_gate import evaluate  # noqa: E402
from expand_topic_monitor import expand  # noqa: E402
from promote_research_topic import validate_and_promote  # noqa: E402
from consensus_test_helpers import registry_bound_case  # noqa: E402


def read_json(path: str):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class ResearchTopicFlowTests(unittest.TestCase):
    def setUp(self):
        self.policy = read_json("config/consensus-policy.json")
        self.proposal = read_json("evals/research-topics/accepted-proposal.json")
        self.assessments = read_json("evals/research-topics/accepted-assessments.json")
        self.registry, self.assessments = registry_bound_case(
            self.proposal, self.assessments
        )
        self.baseline = read_json("config/research-baseline.json")
        self.monitor = read_json("config/monitors/MON-AUTO-TOPICS-001.json")
        self.i18n = read_json("config/publication-i18n.json")

    def test_consensus_accepts_and_other_agents_receive_work_item(self):
        decision = evaluate(self.proposal, self.assessments, self.policy, self.registry)
        self.assertEqual("accepted", decision["outcome"])
        promoted_baseline, promoted_monitor, promoted_i18n = validate_and_promote(
            self.proposal, decision, self.baseline, self.monitor, self.i18n
        )
        topic = promoted_baseline["topics"][-1]
        self.assertEqual("CROSS-99", topic["topic_id"])
        self.assertEqual("ai-consensus", topic["catalog_origin"])
        self.assertEqual(decision["decision_id"], topic["added_by_decision_id"])
        self.assertEqual(
            self.baseline["initial_catalog"], promoted_baseline["initial_catalog"]
        )
        self.assertEqual(
            self.proposal["candidate_topic"]["title_en"],
            promoted_i18n["topic_titles_en"]["CROSS-99"],
        )
        work = expand(
            promoted_monitor,
            promoted_baseline,
            "RUN-TOPIC-NEXT-001",
            include_disabled=True,
        )
        self.assertEqual(1, len(work["work_items"]))
        self.assertEqual("discovery", work["work_items"][0]["assigned_role"])
        self.assertEqual("CROSS-99", work["work_items"][0]["topic_id"])

    def test_provisional_decision_cannot_promote(self):
        assessments = copy.deepcopy(self.assessments[:1])
        decision = evaluate(self.proposal, assessments, self.policy, self.registry)
        self.assertEqual("provisional", decision["outcome"])
        with self.assertRaisesRegex(ValueError, "accepted decision"):
            validate_and_promote(self.proposal, decision, self.baseline, self.monitor, self.i18n)

    def test_topic_with_one_actual_origin_cannot_promote(self):
        proposal = copy.deepcopy(self.proposal)
        proposal["candidate_topic"]["source_refs"] = ["FSBASE-SRC-029", "FSBASE-SRC-030"]
        proposal["origin_group_ids"] = ["FSBASE-ORG-021"]
        decision = evaluate(proposal, self.assessments, self.policy, self.registry)
        decision["outcome"] = "accepted"
        decision["policy_result"]["checks"] = {"test": True}
        with self.assertRaisesRegex(ValueError, "at least two source origin groups"):
            validate_and_promote(proposal, decision, self.baseline, self.monitor, self.i18n)


if __name__ == "__main__":
    unittest.main()
