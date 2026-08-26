from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tools.check_scenario_portfolio import evaluate


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class ScenarioPortfolioTests(unittest.TestCase):
    def setUp(self):
        self.scenario_set = load_json(
            ROOT / "roadmaps" / "scenarios" / "accepted" / "hpci-p0-scenarios.json"
        )
        self.roadmaps = [
            load_json(path)
            for path in sorted((ROOT / "knowledge" / "public" / "roadmaps").glob("*.json"))
        ]
        self.policy = load_json(ROOT / "config" / "scenario-policy.json")

    def evaluate(self, scenario_set=None):
        return evaluate(scenario_set or self.scenario_set, self.roadmaps, ROOT, self.policy)

    def test_current_portfolio_is_structurally_ready_for_consensus(self):
        result = self.evaluate()
        self.assertTrue(result["candidate_ready_for_consensus"])
        self.assertEqual([], result["calculation_errors"])
        self.assertEqual(15, result["counts"]["open_p0_gaps"])
        self.assertEqual(6, result["counts"]["decision_evidence_contracts"])
        self.assertGreaterEqual(result["counts"]["known_evidence_references"], 300)
        self.assertGreaterEqual(result["counts"]["minimum_pairwise_candidate_domain_differences"], 3)
        self.assertGreaterEqual(result["counts"]["minimum_pairwise_fallback_domain_differences"], 3)
        self.assertTrue(result["gaps_remain_open"])

    def test_missing_gap_assignment_fails_closed(self):
        changed = copy.deepcopy(self.scenario_set)
        changed["decision_evidence_contracts"][0]["gap_refs"].pop()
        result = self.evaluate(changed)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("Gap coverage mismatch" in item for item in result["calculation_errors"]))

    def test_numeric_scenario_score_fails_without_approved_weights(self):
        changed = copy.deepcopy(self.scenario_set)
        changed["scenarios"][0]["evaluation"]["application-coverage"]["score"] = 4
        result = self.evaluate(changed)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("scores require approved weights" in item for item in result["calculation_errors"]))

    def test_missing_domain_and_contract_path_fail_closed(self):
        changed = copy.deepcopy(self.scenario_set)
        changed["scenarios"][0]["technology_options"].pop()
        changed["decision_evidence_contracts"][0]["validator_paths"] = ["tools/not-present.py"]
        result = self.evaluate(changed)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("option domains mismatch" in item for item in result["calculation_errors"]))
        self.assertTrue(any("missing repository path" in item for item in result["calculation_errors"]))

    def test_three_labels_cannot_hide_two_substantively_identical_scenarios(self):
        changed = copy.deepcopy(self.scenario_set)
        changed["scenarios"][1]["technology_options"] = copy.deepcopy(
            changed["scenarios"][0]["technology_options"]
        )
        for option in changed["scenarios"][1]["technology_options"]:
            option["candidate_en"] = f"  {option['candidate_en'].upper()}  "
            option["fallback_en"] = f"  {option['fallback_en'].upper()}  "
        result = self.evaluate(changed)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("candidate domains differ" in item for item in result["calculation_errors"]))
        self.assertTrue(any("fallback domains differ" in item for item in result["calculation_errors"]))

    def test_dangling_evidence_reference_fails_closed(self):
        changed = copy.deepcopy(self.scenario_set)
        changed["scenarios"][0]["technology_options"][0]["evidence_refs"].append(
            "MS-NOT-REGISTERED"
        )
        result = self.evaluate(changed)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("unresolved evidence reference" in item for item in result["calculation_errors"]))

    def test_option_must_reference_its_domain_roadmap(self):
        changed = copy.deepcopy(self.scenario_set)
        changed["scenarios"][0]["technology_options"][0]["evidence_refs"].remove(
            "RM-HW-COMPUTE"
        )
        result = self.evaluate(changed)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("missing domain roadmap" in item for item in result["calculation_errors"]))

    def test_decision_gate_periods_must_match_and_be_chronological(self):
        changed = copy.deepcopy(self.scenario_set)
        changed["scenarios"][0]["decision_gates"][0] = "2027 Q4: 遅いゲート"
        result = self.evaluate(changed)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("out of order" in item for item in result["calculation_errors"]))
        self.assertTrue(any("differ between Japanese and English" in item for item in result["calculation_errors"]))


if __name__ == "__main__":
    unittest.main()
