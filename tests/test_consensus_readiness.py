from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from check_consensus_readiness import evaluate_readiness  # noqa: E402


class ConsensusReadinessTests(unittest.TestCase):
    def setUp(self):
        self.policy = json.loads(
            (ROOT / "config" / "consensus-policy.json").read_text(encoding="utf-8")
        )

    @staticmethod
    def agent(agent_id, role, group, provider="provider", model="model"):
        return {
            "agent_id": agent_id,
            "enabled": True,
            "role": role,
            "provider": provider,
            "model_family": model,
            "agent_independence_group": group,
        }

    def test_same_group_as_author_does_not_supply_independent_capacity(self):
        registry = {
            "agents": [
                self.agent("author", "synthesis", "group-a"),
                self.agent("reviewer", "validator", "group-a"),
                self.agent(
                    "placeholder",
                    "critic",
                    "group-b",
                    provider="unconfigured",
                    model="unconfigured",
                ),
            ]
        }
        report = evaluate_readiness(
            run_id="RUN-TEST",
            registry=registry,
            policy=self.policy,
            object_types=["claim"],
            pilot=False,
            evaluated_at="2026-08-24T00:00:00Z",
        )
        self.assertEqual("incomplete", report["status"])
        available = report["object_type_results"][0]["available"]
        self.assertEqual([], available["independent_reviewer_groups"])

    def test_distinct_configured_groups_can_make_claim_capacity_ready(self):
        registry = {
            "agents": [
                self.agent("author", "synthesis", "group-a"),
                self.agent("reviewer-a", "validator", "group-a"),
                self.agent("reviewer-b", "validator", "group-b"),
                self.agent("critic-c", "critic", "group-c"),
            ]
        }
        report = evaluate_readiness(
            run_id="RUN-TEST",
            registry=registry,
            policy=self.policy,
            object_types=["claim"],
            pilot=False,
            evaluated_at="2026-08-24T00:00:00Z",
        )
        self.assertEqual("ready", report["status"])
        self.assertEqual([], report["unmet_requirements"])


if __name__ == "__main__":
    unittest.main()
