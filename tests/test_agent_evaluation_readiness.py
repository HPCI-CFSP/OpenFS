from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from evaluate_agent_evaluation_readiness import _pinned_payload, evaluate  # noqa: E402
from openfs_runtime import stable_digest  # noqa: E402


class AgentEvaluationReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.policy = {
            "policy_id": "AEVALPOL-TEST-001",
            "status": "enforced",
            "development_suite_ref": "evals/agent-harness/public-pilot-suite.json",
            "applicable_roles": ["discovery", "extraction", "validator", "critic", "synthesis"],
            "required_bundle_status": "accepted",
            "required_consensus_status": "accepted",
            "maximum_bundle_age_days": 30,
            "minimum_repetitions": 3,
            "formal_holdout": {
                "status": "unavailable",
                "custodian_id": "unconfigured",
                "task_set_digest": None,
                "answer_set_digest": None,
                "attestation_ref": None,
            },
            "effect": "Default deny.",
        }
        self.agent = {
            "agent_id": "discovery-a",
            "enabled": False,
            "role": "discovery",
            "provider": "Provider A",
            "model_id": "unconfigured",
            "agent_independence_group": "ORG-SYSTEM-A",
            "harness_id": "unconfigured",
            "harness_repository_url": "unconfigured",
            "harness_commit": "unconfigured",
            "prompt_profile": "discovery-v1",
        }
        self.write("config/agent-evaluation-policy.json", self.policy)
        self.write("config/agent-registry.json", {"agents": [self.agent]})
        self.write("evals/agent-harness/public-pilot-suite.json", {"suite_id": "AESUITE-TEST"})

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, relative: str, value: dict) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    @patch("evaluate_agent_evaluation_readiness.evaluate_suite")
    def test_aggregate_without_enabled_provider_agents_is_explicitly_blocked(self, suite):
        suite.return_value = {"ready_for_public_development_runs": True}
        report = evaluate(self.root, evaluated_at="2026-08-28T00:00:00Z")

        self.assertEqual("blocked", report["status"])
        self.assertFalse(report["checks"]["requested_agents_present"])
        self.assertFalse(report["checks"]["formal_holdout_available"])
        self.assertEqual([], report["agents"])

    @patch("evaluate_agent_evaluation_readiness.evaluate_suite")
    def test_explicit_unconfigured_agent_fails_closed(self, suite):
        suite.return_value = {"ready_for_public_development_runs": True}
        report = evaluate(
            self.root,
            agent_ids=["discovery-a"],
            evaluated_at="2026-08-28T00:00:00Z",
        )

        blockers = report["agents"][0]["blockers"]
        self.assertIn("agent-not-enabled", blockers)
        self.assertIn("model-id-unconfigured", blockers)
        self.assertIn("formal-holdout-unavailable", blockers)

    @patch("evaluate_agent_evaluation_readiness.evaluate_bundle")
    @patch("evaluate_agent_evaluation_readiness.evaluate_suite")
    def test_exact_current_bundle_and_external_holdout_can_pass(self, suite, bundle):
        suite.return_value = {"ready_for_public_development_runs": True}
        bundle.return_value = {"candidate_ready_for_consensus": True}
        self.agent.update(
            {
                "enabled": True,
                "model_id": "model-a-2026-08-01",
                "harness_id": "HAR-OPENFS",
                "harness_repository_url": "https://example.org/openfs",
                "harness_commit": "a" * 40,
            }
        )
        self.policy["formal_holdout"] = {
            "status": "available",
            "custodian_id": "independent-custodian-a",
            "task_set_digest": "sha256:" + "b" * 64,
            "answer_set_digest": "sha256:" + "c" * 64,
            "attestation_ref": "external:holdout-attestation-001",
        }
        self.write("config/agent-evaluation-policy.json", self.policy)
        self.write("config/agent-registry.json", {"agents": [self.agent]})
        self.write(
            "proposals/agent-evaluations/AEVAL-TEST-001.json",
            {
                "status": "accepted",
                "system_under_test": {
                    "agent_id": "discovery-a",
                    "role": "discovery",
                    "origin_group": "ORG-SYSTEM-A",
                    "prompt_profile": "discovery-v1",
                    "model": {"provider": "Provider A", "model_id": "model-a-2026-08-01"},
                    "harness": {
                        "harness_id": "HAR-OPENFS",
                        "repository_url": "https://example.org/openfs",
                        "commit": "a" * 40,
                    },
                },
                "benchmark": {"task_set_digest": "sha256:" + "b" * 64},
                "dataset_control": {
                    "reference_answer_digest": "sha256:" + "c" * 64,
                    "holdout_attestation_ref": "external:holdout-attestation-001",
                },
                "runs": [{}, {}, {}],
                "provenance": {"created_at": "2026-08-20T00:00:00Z"},
                "consensus_status": "accepted",
            },
        )

        report = evaluate(self.root, evaluated_at="2026-08-28T00:00:00Z")

        self.assertEqual("ready", report["status"])
        self.assertEqual("ready", report["agents"][0]["status"])
        self.assertEqual(
            ["proposals/agent-evaluations/AEVAL-TEST-001.json"],
            report["agents"][0]["accepted_bundle_refs"],
        )
        bundle_path = (
            self.root / "proposals/agent-evaluations/AEVAL-TEST-001.json"
        )
        mismatched = json.loads(bundle_path.read_text(encoding="utf-8"))
        mismatched["dataset_control"]["holdout_attestation_ref"] = (
            "external:different-holdout"
        )
        self.write(
            "proposals/agent-evaluations/AEVAL-TEST-001.json", mismatched
        )
        mismatched_report = evaluate(
            self.root, evaluated_at="2026-08-28T00:00:00Z"
        )
        self.assertEqual("blocked", mismatched_report["status"])
        self.assertIn(
            "current-accepted-evaluation-bundle-missing",
            mismatched_report["agents"][0]["blockers"],
        )

    @patch("evaluate_agent_evaluation_readiness.evaluate_bundle")
    @patch("evaluate_agent_evaluation_readiness.evaluate_suite")
    def test_stale_bundle_does_not_satisfy_gate(self, suite, bundle):
        suite.return_value = {"ready_for_public_development_runs": True}
        bundle.return_value = {"candidate_ready_for_consensus": True}
        self.agent.update(
            {
                "enabled": True,
                "model_id": "model-a",
                "harness_id": "HAR-OPENFS",
                "harness_repository_url": "https://example.org/openfs",
                "harness_commit": "a" * 40,
            }
        )
        self.policy["formal_holdout"] = {
            "status": "available",
            "custodian_id": "custodian-a",
            "task_set_digest": "sha256:" + "b" * 64,
            "answer_set_digest": "sha256:" + "c" * 64,
            "attestation_ref": "external:holdout-attestation-001",
        }
        self.write("config/agent-evaluation-policy.json", self.policy)
        self.write("config/agent-registry.json", {"agents": [self.agent]})
        self.write(
            "proposals/agent-evaluations/AEVAL-OLD-001.json",
            {
                "status": "accepted",
                "system_under_test": {
                    "agent_id": "discovery-a",
                    "role": "discovery",
                    "origin_group": "ORG-SYSTEM-A",
                    "prompt_profile": "discovery-v1",
                    "model": {"provider": "Provider A", "model_id": "model-a"},
                    "harness": {
                        "harness_id": "HAR-OPENFS",
                        "repository_url": "https://example.org/openfs",
                        "commit": "a" * 40,
                    },
                },
                "benchmark": {"task_set_digest": "sha256:" + "b" * 64},
                "dataset_control": {
                    "reference_answer_digest": "sha256:" + "c" * 64,
                    "holdout_attestation_ref": "external:holdout-attestation-001",
                },
                "runs": [{}, {}, {}],
                "provenance": {"created_at": "2026-06-01T00:00:00Z"},
                "consensus_status": "accepted",
            },
        )

        report = evaluate(self.root, evaluated_at="2026-08-28T00:00:00Z")

        self.assertEqual("blocked", report["status"])
        self.assertIn(
            "current-accepted-evaluation-bundle-missing",
            report["agents"][0]["blockers"],
        )

    def test_pinned_run_input_rejects_post_creation_mutation(self):
        source_ref = "config/agent-evaluation-policy.json"
        snapshot_ref = "runs/RUN-TEST/inputs/config/agent-evaluation-policy.json"
        payload = {"policy_id": "AEVALPOL-TEST-001"}
        self.write(snapshot_ref, payload)
        manifest = {
            "configuration_snapshots": {source_ref: snapshot_ref},
            "policy_hashes": {source_ref: stable_digest(payload)},
        }

        loaded, _ = _pinned_payload(self.root, manifest, source_ref)
        self.assertEqual(payload, loaded)

        self.write(snapshot_ref, {"policy_id": "AEVALPOL-MUTATED"})
        with self.assertRaisesRegex(ValueError, "digest differs"):
            _pinned_payload(self.root, manifest, source_ref)


if __name__ == "__main__":
    unittest.main()
