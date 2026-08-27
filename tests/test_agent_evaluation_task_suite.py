from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tools.check_agent_evaluation_task_suite import evaluate


ROOT = Path(__file__).resolve().parents[1]


def suite_fixture():
    return json.loads(
        (ROOT / "evals" / "agent-harness" / "public-pilot-suite.json").read_text(
            encoding="utf-8"
        )
    )


class AgentEvaluationTaskSuiteTests(unittest.TestCase):
    def test_public_pilot_is_complete_but_not_a_formal_holdout(self):
        result = evaluate(suite_fixture(), ROOT)
        self.assertTrue(result["ready_for_public_development_runs"])
        self.assertFalse(result["formal_holdout_available"])
        self.assertEqual(6, result["counts"]["tasks"])
        self.assertEqual(6, result["counts"]["categories"])

    def test_missing_policy_denial_and_input_fail_closed(self):
        suite = suite_fixture()
        task = suite["tasks"][0]
        task["forbidden_actions"].remove("read-secrets")
        task["input_paths"].append("../private/answer.json")
        result = evaluate(suite, ROOT)
        self.assertFalse(result["ready_for_public_development_runs"])
        self.assertTrue(any("forbidden actions" in item for item in result["control_errors"]))
        self.assertTrue(any("unsafe input path" in item for item in result["control_errors"]))

    def test_duplicate_ids_unknown_rubric_and_bad_weights_fail_closed(self):
        suite = copy.deepcopy(suite_fixture())
        suite["tasks"][1]["task_id"] = suite["tasks"][0]["task_id"]
        suite["tasks"][0]["rubric_refs"].append("AERUB-UNKNOWN")
        suite["rubrics"][0]["weight"] = 0.2
        result = evaluate(suite, ROOT)
        self.assertFalse(result["ready_for_public_development_runs"])
        self.assertTrue(any("task_id" in item for item in result["control_errors"]))
        self.assertTrue(any("unknown rubric" in item for item in result["control_errors"]))
        self.assertTrue(any("sum to 1.0" in item for item in result["control_errors"]))

    def test_network_disabled_task_cannot_enable_browser_tool(self):
        suite = suite_fixture()
        suite["tasks"][0]["allowed_tools"].append("managed-browser")
        result = evaluate(suite, ROOT)
        self.assertFalse(result["ready_for_public_development_runs"])
        self.assertTrue(any("network-capable" in item for item in result["control_errors"]))

    def test_input_must_exist_in_the_pinned_commit(self):
        suite = suite_fixture()
        suite["source_commit"] = "f" * 40
        result = evaluate(suite, ROOT)
        self.assertFalse(result["ready_for_public_development_runs"])
        self.assertTrue(any("absent from source_commit" in item for item in result["control_errors"]))


if __name__ == "__main__":
    unittest.main()
