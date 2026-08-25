from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class RoadmapAssuranceTests(unittest.TestCase):
    def setUp(self):
        self.roadmaps = [
            load_json(path)
            for path in sorted((ROOT / "knowledge" / "public" / "roadmaps").glob("*.json"))
        ]
        self.evidence = load_json(
            ROOT / "knowledge" / "public" / "audits" / "roadmap-evidence-audit.json"
        )
        self.sources = load_json(
            ROOT / "knowledge" / "public" / "audits" / "roadmap-source-audit.json"
        )
        self.dependencies = load_json(
            ROOT / "knowledge" / "public" / "dependencies" / "p0-roadmap-dependencies.json"
        )
        self.scenarios = load_json(
            ROOT / "roadmaps" / "scenarios" / "accepted" / "hpci-p0-scenarios.json"
        )

    def test_evidence_audit_covers_every_milestone_exactly_once(self):
        milestone_items = [
            milestone
            for roadmap in self.roadmaps
            for lane in roadmap["lanes"]
            for milestone in lane["milestones"]
        ]
        milestones = {
            milestone["milestone_id"]: milestone
            for milestone in milestone_items
        }
        self.assertEqual(len(milestone_items), len(milestones), "milestone IDs must be globally unique")
        entries = {entry["milestone_id"]: entry for entry in self.evidence["entries"]}
        self.assertGreaterEqual(len(milestones), 130)
        self.assertEqual(set(milestones), set(entries))
        self.assertEqual(len(milestones), self.evidence["summary"]["milestone_count"])
        self.assertEqual(
            len(milestones),
            sum(
                self.evidence["summary"][key]
                for key in (
                    "classified_primary",
                    "classified_forward_looking",
                    "as_of_baseline",
                    "coverage_gap",
                    "openfs_provisional",
                )
            ),
        )

        expected_status = {
            "observed": "classified-primary-event",
            "standard-release": "classified-primary-event",
            "as-of-baseline": "as-of-baseline",
            "vendor-target": "classified-forward-looking",
            "project-target": "classified-forward-looking",
            "policy-target": "classified-forward-looking",
            "no-public-date": "coverage-gap",
            "openfs-provisional-plan": "openfs-provisional",
        }
        for milestone_id, milestone in milestones.items():
            self.assertEqual(
                expected_status[milestone["timing_basis"]],
                entries[milestone_id]["review_status"],
            )
            self.assertEqual(milestone["source_ids"], entries[milestone_id]["source_ids"])
            self.assertEqual(
                "pending-independent-review",
                entries[milestone_id]["semantic_verification"],
            )
        self.assertEqual(0, self.evidence["summary"]["independently_verified"])
        self.assertEqual(len(milestones), self.evidence["summary"]["pending_independent_review"])

    def test_source_audit_covers_every_registered_source_and_has_no_known_404(self):
        registered_items = [
            (roadmap["roadmap_id"], source["source_id"])
            for roadmap in self.roadmaps
            for source in roadmap["sources"]
        ]
        registered = {
            (roadmap["roadmap_id"], source["source_id"])
            for roadmap in self.roadmaps
            for source in roadmap["sources"]
        }
        self.assertEqual(len(registered_items), len(registered), "source IDs must be unique within each roadmap")
        audited = {
            (result["roadmap_id"], result["source_id"])
            for result in self.sources["results"]
        }
        self.assertGreaterEqual(len(registered), 91)
        self.assertEqual(registered, audited)
        summary = self.sources["summary"]
        self.assertEqual(len(registered), summary["source_count"])
        self.assertEqual(
            summary["source_count"],
            sum(
                summary[key]
                for key in ("reachable", "access-restricted", "missing", "timeout", "error")
            ),
        )
        self.assertEqual(0, summary["missing"])

    def test_every_registered_source_is_used_by_a_roadmap_assertion(self):
        for roadmap in self.roadmaps:
            registered = {source["source_id"] for source in roadmap["sources"]}
            used = {
                source_id
                for track in roadmap["tracks"]
                for source_id in track["source_ids"]
            }
            used.update(
                source_id
                for dependency in roadmap["dependencies"]
                for source_id in dependency["source_ids"]
            )
            used.update(
                source_id
                for lane in roadmap["lanes"]
                for milestone in lane["milestones"]
                for source_id in milestone["source_ids"]
            )
            self.assertEqual(registered, used, roadmap["roadmap_id"])

    def test_dependency_register_references_known_graph_objects(self):
        roadmap_ids = {roadmap["roadmap_id"] for roadmap in self.roadmaps}
        source_ids = {
            source["source_id"]
            for roadmap in self.roadmaps
            for source in roadmap["sources"]
        }
        milestone_ids = {
            milestone["milestone_id"]
            for roadmap in self.roadmaps
            for lane in roadmap["lanes"]
            for milestone in lane["milestones"]
        }
        gap_ids = {
            gap["gap_id"]
            for roadmap in self.roadmaps
            for gap in roadmap["coverage_gaps"]
        }
        dependency_ids = {
            dependency["dependency_id"]
            for roadmap in self.roadmaps
            for dependency in roadmap["dependencies"]
        }
        seen = set()
        for dependency in self.dependencies["dependencies"]:
            self.assertIn(dependency["upstream_roadmap_id"], roadmap_ids)
            self.assertIn(dependency["downstream_roadmap_id"], roadmap_ids)
            self.assertLessEqual(set(dependency["source_ids"]), source_ids)
            self.assertLessEqual(set(dependency["source_dependency_ids"]), dependency_ids)
            self.assertLessEqual(set(dependency["gate_refs"]), milestone_ids)
            self.assertLessEqual(set(dependency["coverage_gap_refs"]), gap_ids)
            pair = (
                dependency["upstream_roadmap_id"],
                dependency["downstream_roadmap_id"],
            )
            self.assertNotIn(pair, seen)
            seen.add(pair)

    def test_dependency_graph_is_acyclic_and_reaches_the_reference_blueprint(self):
        graph = {roadmap["roadmap_id"]: set() for roadmap in self.roadmaps}
        reverse = {roadmap_id: set() for roadmap_id in graph}
        for dependency in self.dependencies["dependencies"]:
            upstream = dependency["upstream_roadmap_id"]
            downstream = dependency["downstream_roadmap_id"]
            self.assertNotEqual(upstream, downstream)
            graph[upstream].add(downstream)
            reverse[downstream].add(upstream)

        indegree = {node: len(reverse[node]) for node in graph}
        ready = [node for node, count in indegree.items() if count == 0]
        visited = []
        while ready:
            node = ready.pop()
            visited.append(node)
            for downstream in graph[node]:
                indegree[downstream] -= 1
                if indegree[downstream] == 0:
                    ready.append(downstream)
        self.assertEqual(set(graph), set(visited), "cross-roadmap dependencies must remain acyclic")

        blueprint = "RM-X-BLUEPRINT"
        for roadmap_id in set(graph) - {blueprint}:
            frontier = [roadmap_id]
            reached = set()
            while frontier:
                node = frontier.pop()
                if node in reached:
                    continue
                reached.add(node)
                frontier.extend(graph[node])
            self.assertIn(blueprint, reached, roadmap_id)

    def test_every_coverage_gap_has_a_decision_priority(self):
        gaps = [
            gap
            for roadmap in self.roadmaps
            for gap in roadmap["coverage_gaps"]
        ]
        self.assertGreaterEqual(len(gaps), 30)
        self.assertEqual(len(gaps), len({gap["gap_id"] for gap in gaps}))
        self.assertTrue(all(gap["priority"] in {"P0", "P1", "P2"} for gap in gaps))
        self.assertTrue(any(gap["priority"] == "P0" for gap in gaps))
        self.assertTrue(any(gap["priority"] == "P2" for gap in gaps))

    def test_three_scenarios_are_unranked_and_use_common_criteria(self):
        scenarios = self.scenarios["scenarios"]
        self.assertEqual(
            {
                "SCN-HPCI-BALANCED-001",
                "SCN-HPCI-AI-DATA-001",
                "SCN-HPCI-STAGED-001",
            },
            {scenario["scenario_id"] for scenario in scenarios},
        )
        expected_criteria = {
            item["criterion_id"]
            for item in load_json(ROOT / "config" / "scenario-policy.json")["evaluation_criteria"]
        }
        known_evidence_refs = {
            *(roadmap["roadmap_id"] for roadmap in self.roadmaps),
            *(milestone["milestone_id"] for roadmap in self.roadmaps for lane in roadmap["lanes"] for milestone in lane["milestones"]),
            *(gap["gap_id"] for roadmap in self.roadmaps for gap in roadmap["coverage_gaps"]),
            *(dependency["dependency_id"] for dependency in self.dependencies["dependencies"]),
            *(constraint["constraint_id"] for constraint in self.dependencies["external_constraints"]),
            self.dependencies["export_id"],
            self.evidence["export_id"],
        }
        for scenario in scenarios:
            self.assertEqual("provisional", scenario["research_status"])
            self.assertEqual("incomplete", scenario["consensus_status"])
            self.assertEqual(expected_criteria, set(scenario["evaluation"]))
            self.assertTrue(
                all(item["score"] is None for item in scenario["evaluation"].values())
            )
            self.assertTrue(scenario["uncertainties"] and scenario["uncertainties_en"])
            self.assertTrue(scenario["decision_gates"] and scenario["decision_gates_en"])
            self.assertEqual(
                {"compute", "memory", "interconnect", "system-software", "applications"},
                {option["domain"] for option in scenario["technology_options"]},
            )
            self.assertEqual(5, len(scenario["technology_options"]))
            self.assertTrue(
                all(option["evidence_refs"] for option in scenario["technology_options"])
            )
            for option in scenario["technology_options"]:
                self.assertLessEqual(set(option["evidence_refs"]), known_evidence_refs)
            self.assertLessEqual(set(scenario["evidence_refs"]), known_evidence_refs)
            for evaluation in scenario["evaluation"].values():
                self.assertLessEqual(set(evaluation["evidence_refs"]), known_evidence_refs)


if __name__ == "__main__":
    unittest.main()
