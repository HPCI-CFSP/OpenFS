from __future__ import annotations

import copy
import unittest

from tools.check_agent_evaluation_bundle import evaluate


DIGEST = "sha256:" + "a" * 64


def valid_bundle():
    run_template = {
        "started_at": "2026-08-28T00:00:00Z",
        "ended_at": "2026-08-28T00:10:00Z",
        "outcome_score": 0.8,
        "policy_pass": True,
        "trace_digest": DIGEST,
        "artifact_digest": DIGEST,
        "usage": {
            "input_tokens": 1000,
            "output_tokens": 500,
            "cache_read_tokens": 0,
            "cache_write_tokens": 0,
            "wall_seconds": 600,
            "cost": 1.0,
            "currency": "USD",
        },
    }
    runs = []
    for index in range(1, 4):
        run = copy.deepcopy(run_template)
        run["run_id"] = f"AERUN-TEST-{index}"
        run["repetition"] = index
        runs.append(run)
    return {
        "schema_version": "0.1.0",
        "evaluation_id": "AEVAL-TEST-001",
        "status": "provisional",
        "benchmark": {
            "name": "OpenFS agent evaluation",
            "version": "1",
            "official_source_urls": ["https://example.org/benchmark"],
            "task_set_digest": DIGEST,
            "score_metric": "outcome score",
            "higher_is_better": True,
            "rubric": [
                {"criterion_id": "AEC-EVIDENCE", "description_ja": "根拠", "description_en": "evidence", "weight": 0.6, "partial_credit": True, "evaluator_type": "programmatic"},
                {"criterion_id": "AEC-POLICY", "description_ja": "方針", "description_en": "policy", "weight": 0.4, "partial_credit": False, "evaluator_type": "independent-model"},
            ],
        },
        "system_under_test": {
            "model": {"provider": "Provider A", "model_id": "model-a", "release": "2026-08-01"},
            "harness": {"harness_id": "HAR-OPENFS", "repository_url": "https://example.org/harness", "commit": "b" * 40},
            "prompt_digest": DIGEST,
            "toolset_digest": DIGEST,
            "skillset_digest": DIGEST,
        },
        "protocol": {
            "protocol_version": "1",
            "protocol_digest": DIGEST,
            "evaluator": {"evaluator_id": "eval-a", "version": "1", "implementation_digest": DIGEST, "origin_group": "ORG-EVALUATOR"},
            "minimum_repetitions": 3,
            "timeout_seconds": 900,
            "budget": {"maximum_wall_seconds": 900, "maximum_total_tokens": 5000, "maximum_cost": 2.0, "currency": "USD", "cost_basis": "provider list price"},
        },
        "execution_boundary": {
            "environment_type": "container",
            "privilege_level": "unprivileged",
            "network_access": "allowlisted-public-web",
            "outbound_path": "safe-fetch-broker",
            "network_policy_digest": DIGEST,
            "write_policy": "allowlist-only",
            "write_roots": ["proposals/agent-evaluations"],
            "credential_policy": "scoped-allowlist",
            "enforcement_evidence_digest": DIGEST,
            "secret_scan_passed": True,
        },
        "dataset_control": {
            "development_visibility": "public",
            "validation_visibility": "aggregate-only",
            "test_visibility": "hidden",
            "dynamic_web": True,
            "dataset_digest": DIGEST,
            "reference_answer_digest": DIGEST,
            "reference_answer_location": "hidden-external",
            "web_snapshot_at": "2026-08-28T00:00:00Z",
            "web_receipt_bundle_digest": DIGEST,
            "contamination_assessment": "unknown",
            "prior_test_exposures": 0,
        },
        "runs": runs,
        "acceptance": {
            "minimum_policy_pass_rate": 1.0,
            "score_threshold": 0.7,
            "require_hidden_holdout": True,
            "require_independent_evaluator": True,
        },
        "provenance": {
            "created_at": "2026-08-28T01:00:00Z",
            "base_commit": "c" * 40,
            "author_agent_id": "AGT-AUTHOR",
            "author_model_id": "model-a",
            "author_origin_group": "ORG-AUTHOR",
            "evidence_refs": ["SRC-WORK020"],
            "raw_bundle_uri": "https://example.org/raw/evaluation.json",
            "raw_bundle_digest": DIGEST,
        },
        "consensus_status": "incomplete",
    }


class AgentEvaluationBundleTests(unittest.TestCase):
    def test_controlled_repeated_evaluation_is_only_consensus_candidate(self):
        result = evaluate(valid_bundle())
        self.assertTrue(result["candidate_ready_for_consensus"])
        self.assertEqual(3, result["counts"]["runs"])
        self.assertEqual(1.0, result["metrics"]["policy_pass_rate"])
        self.assertEqual(3.0, result["metrics"]["total_cost_usd"])

    def test_direct_network_and_privileged_execution_fail_closed(self):
        bundle = valid_bundle()
        bundle["execution_boundary"]["network_access"] = "public-web"
        bundle["execution_boundary"]["outbound_path"] = "direct"
        bundle["execution_boundary"]["privilege_level"] = "privileged"
        result = evaluate(bundle)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("direct outbound" in item for item in result["control_errors"]))
        self.assertTrue(any("privileged" in item for item in result["control_errors"]))

    def test_visible_test_and_same_origin_evaluator_fail_closed(self):
        bundle = valid_bundle()
        bundle["dataset_control"]["test_visibility"] = "public"
        bundle["protocol"]["evaluator"]["origin_group"] = "ORG-AUTHOR"
        result = evaluate(bundle)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("hidden test" in item for item in result["control_errors"]))
        self.assertTrue(any("not independent" in item for item in result["control_errors"]))

    def test_duplicate_runs_policy_failure_and_budget_overage_fail_closed(self):
        bundle = valid_bundle()
        bundle["runs"][1]["run_id"] = bundle["runs"][0]["run_id"]
        bundle["runs"][2]["policy_pass"] = False
        bundle["runs"][0]["usage"]["cost"] = 3.0
        result = evaluate(bundle)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("run_id" in item for item in result["control_errors"]))
        self.assertTrue(any("policy pass rate" in item for item in result["control_errors"]))
        self.assertTrue(any("cost exceeds" in item for item in result["control_errors"]))

    def test_policy_threshold_cannot_be_relaxed(self):
        bundle = valid_bundle()
        bundle["acceptance"]["minimum_policy_pass_rate"] = 0.5
        result = evaluate(bundle)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("must be 1.0" in item for item in result["control_errors"]))

    def test_rubric_and_hidden_answer_controls_fail_closed(self):
        bundle = valid_bundle()
        bundle["benchmark"]["rubric"][1]["criterion_id"] = "AEC-EVIDENCE"
        bundle["benchmark"]["rubric"][1]["weight"] = 0.3
        bundle["dataset_control"]["reference_answer_location"] = "public"
        result = evaluate(bundle)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("criterion_id" in item for item in result["control_errors"]))
        self.assertTrue(any("sum to 1.0" in item for item in result["control_errors"]))
        self.assertTrue(any("public reference" in item for item in result["control_errors"]))


if __name__ == "__main__":
    unittest.main()
