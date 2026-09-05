from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

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

    def test_publication_schema_binds_each_authorized_directive_to_its_decision(self):
        schema = load_json(ROOT / "schemas/roadmap-dependency-register.schema.json")
        validator = Draft202012Validator(schema["properties"]["publication"])
        publication = self.register["publication"]
        validator.validate(publication)
        decisions = {
            "DIR-900006": "PUBDEC-20260826-003",
            "DIR-900015": "PUBDEC-20260826-003",
            "DIR-900018": "PUBDEC-HARDWARE-RESEARCH-20260831",
            "DIR-900019": "PUBDEC-CROSS-DOMAIN-RESEARCH-20260901",
            "DIR-900103": "PUBDEC-P0-ROADMAP-PLANNING-20260905-001",
        }
        for directive, decision in decisions.items():
            expected = {**publication, "human_approval_directive_id": directive,
                        "publication_decision_id": decision}
            validator.validate(expected)
            for other in set(decisions.values()) - {decision}:
                with self.subTest(directive=directive, wrong_decision=other):
                    self.assertTrue(list(validator.iter_errors({**expected,
                        "publication_decision_id": other})))
        self.assertTrue(list(validator.iter_errors({**publication,
            "human_approval_directive_id": "DIR-900099"})))

    def test_current_register_is_structurally_ready_for_consensus(self):
        result = self.evaluate()
        expected_p0 = sum(
            gap["priority"] == "P0" and gap["status"] == "open"
            for roadmap in self.roadmaps
            for gap in roadmap["coverage_gaps"]
        )
        self.assertTrue(result["candidate_ready_for_consensus"])
        self.assertEqual([], result["calculation_errors"])
        self.assertEqual(expected_p0, result["counts"]["open_p0_gaps"])
        self.assertEqual(
            expected_p0,
            result["counts"]["edge_propagated_p0_gaps"]
            + result["counts"]["portfolio_gate_p0_gaps"],
        )
        self.assertGreaterEqual(result["counts"]["portfolio_gate_p0_gaps"], 1)
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

    def test_shared_primary_source_retains_every_roadmap_owner(self):
        memory = next(r for r in self.roadmaps if r["roadmap_id"] == "RM-HW-MEMORY")
        unrelated = next(r for r in self.roadmaps if r["roadmap_id"] == "RM-HW-STORAGE")
        source = next(s for s in memory["sources"] if s["source_id"] == "SRC-MEM008")
        unrelated["sources"].append(copy.deepcopy(source))
        for roadmaps in (self.roadmaps, list(reversed(self.roadmaps))):
            self.assertEqual([], evaluate(self.register, roadmaps)["calculation_errors"])

    def test_shared_source_cannot_silently_change_its_url(self):
        memory = next(r for r in self.roadmaps if r["roadmap_id"] == "RM-HW-MEMORY")
        unrelated = next(r for r in self.roadmaps if r["roadmap_id"] == "RM-HW-STORAGE")
        source = copy.deepcopy(next(s for s in memory["sources"] if s["source_id"] == "SRC-MEM008"))
        source["url"] = "https://example.org/different-publication"
        unrelated["sources"].append(source)
        result = self.evaluate()
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("shared source ID has conflicting URLs" in e for e in result["calculation_errors"]))

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
