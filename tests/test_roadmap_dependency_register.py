from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from tools.check_roadmap_dependency_register import evaluate


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class RoadmapDependencyRegisterTests(unittest.TestCase):
    def setUp(self):
        self.register = load_json(
            ROOT / "knowledge" / "public" / "dependencies" / "p0-roadmap-dependencies.json"
        )
        self.roadmaps = [
            load_json(path)
            for path in sorted((ROOT / "knowledge" / "public" / "roadmaps").glob("*.json"))
        ]

    def evaluate(self, register=None):
        return evaluate(register or self.register, self.roadmaps)

    def test_current_register_is_structurally_ready_for_consensus(self):
        result = self.evaluate()
        self.assertTrue(result["candidate_ready_for_consensus"])
        self.assertEqual([], result["calculation_errors"])
        self.assertEqual(15, result["counts"]["open_p0_gaps"])
        self.assertEqual(14, result["counts"]["edge_propagated_p0_gaps"])
        self.assertEqual(1, result["counts"]["portfolio_gate_p0_gaps"])
        self.assertTrue(result["gaps_remain_open"])

    def test_cycle_fails_closed(self):
        changed = copy.deepcopy(self.register)
        dependency = next(
            item for item in changed["dependencies"]
            if item["dependency_id"] == "XDEP-COMP-BLUE"
        )
        dependency["downstream_roadmap_id"] = "RM-APP-WORKLOADS"
        result = self.evaluate(changed)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("contains a cycle" in item for item in result["calculation_errors"]))

    def test_unknown_reference_fails_closed(self):
        changed = copy.deepcopy(self.register)
        changed["dependencies"][0]["source_ids"].append("SRC-NOT-REGISTERED")
        result = self.evaluate(changed)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("unknown source_ids" in item for item in result["calculation_errors"]))

    def test_known_but_unrelated_source_fails_closed(self):
        changed = copy.deepcopy(self.register)
        dependency = next(
            item for item in changed["dependencies"]
            if item["dependency_id"] == "XDEP-MEM-COMP"
        )
        dependency["source_ids"].append("SRC-NET001")
        result = self.evaluate(changed)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(
            any("source_ids belong to unrelated roadmaps" in item for item in result["calculation_errors"])
        )

    def test_missing_p0_gap_propagation_fails_closed(self):
        changed = copy.deepcopy(self.register)
        for dependency in changed["dependencies"]:
            dependency["coverage_gap_refs"] = [
                gap_id for gap_id in dependency["coverage_gap_refs"] if gap_id != "GAP-MEM003"
            ]
        result = self.evaluate(changed)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("P0 Gap propagation mismatch" in item for item in result["calculation_errors"]))

    def test_portfolio_gate_cannot_be_misrepresented_as_a_causal_edge(self):
        changed = copy.deepcopy(self.register)
        changed["dependencies"][0]["coverage_gap_refs"].append("GAP-BLUE-006")
        result = self.evaluate(changed)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("must not also be assigned" in item for item in result["calculation_errors"]))


if __name__ == "__main__":
    unittest.main()
