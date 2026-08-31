from __future__ import annotations

import json
import unittest
from collections import defaultdict
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
        self.assertEqual(
            max(roadmap["as_of"] for roadmap in self.roadmaps),
            self.evidence["as_of"],
        )
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
        milestone_source_classes = {
            milestone["milestone_id"]: {
                source_classes[source_id]
                for source_id in milestone["source_ids"]
            }
            for roadmap in self.roadmaps
            for source_classes in [{source["source_id"]: source["source_class"] for source in roadmap["sources"]}]
            for lane in roadmap["lanes"]
            for milestone in lane["milestones"]
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
                    "openfs_governance_event",
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
            expected_review_status = expected_status[milestone["timing_basis"]]
            if (
                milestone_source_classes[milestone_id] == {"openfs-governance"}
                and milestone["timing_basis"] not in {"openfs-provisional-plan", "no-public-date"}
            ):
                expected_review_status = "openfs-governance-event"
            self.assertEqual(
                expected_review_status,
                entries[milestone_id]["review_status"],
            )
            self.assertEqual(milestone["source_ids"], entries[milestone_id]["source_ids"])
            self.assertEqual(
                "pending-independent-review",
                entries[milestone_id]["semantic_verification"],
            )
        self.assertEqual(0, self.evidence["summary"]["independently_verified"])
        self.assertEqual(
            len(milestones) + self.evidence["summary"]["generation_band_count"],
            self.evidence["summary"]["pending_independent_review"],
        )
        timing_summary = self.evidence["summary"]
        self.assertEqual(
            len(milestones),
            sum(
                timing_summary[key]
                for key in (
                    "source_supported_quarter",
                    "source_supported_half_year",
                    "source_supported_quarter_range",
                    "source_supported_year",
                    "undated",
                    "openfs_provisional_quarter",
                    "openfs_provisional_half_year",
                    "openfs_provisional_quarter_range",
                    "openfs_provisional_year",
                    "openfs_governance_quarter",
                    "openfs_governance_half_year",
                    "openfs_governance_quarter_range",
                    "openfs_governance_year",
                )
            ),
        )
        self.assertGreater(timing_summary["source_supported_quarter"], 0)
        self.assertEqual(timing_summary["coverage_gap"], timing_summary["undated"])
        self.assertEqual(
            timing_summary["openfs_provisional"],
            timing_summary["openfs_provisional_quarter"]
            + timing_summary["openfs_provisional_half_year"]
            + timing_summary["openfs_provisional_quarter_range"]
            + timing_summary["openfs_provisional_year"],
        )

    def test_evidence_audit_covers_every_generation_band_exactly_once(self):
        bands = {
            band["generation_band_id"]: band
            for roadmap in self.roadmaps
            for track in roadmap["tracks"]
            for band in track.get("generation_bands", [])
        }
        entries = {
            entry["generation_band_id"]: entry
            for entry in self.evidence["generation_band_entries"]
        }
        self.assertEqual(7, len(bands))
        self.assertEqual(set(bands), set(entries))
        self.assertEqual(len(bands), self.evidence["summary"]["generation_band_count"])
        for band_id, band in bands.items():
            self.assertEqual(band["source_ids"], entries[band_id]["source_ids"])
            self.assertEqual(band["confidence"], entries[band_id]["confidence"])
            self.assertEqual("openfs-synthesis-pending", entries[band_id]["review_status"])

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
        unchecked = {r["url"] for r in self.sources["results"] if r.get("error_kind") == "not-audited"}
        self.assertLessEqual(summary["unique_url_count"] - len(unchecked), summary["fetch_count"])
        self.assertEqual(
            summary["unique_url_count"],
            sum(summary["unique_url_status_counts"].values()),
        )
        self.assertEqual(
            summary["source_count"] - summary["unique_url_count"],
            summary["duplicate_registration_count"],
        )
        self.assertLessEqual(
            summary["unique_external_url_count"], summary["unique_url_count"]
        )
        self.assertEqual(
            summary["source_count"],
            sum(
                summary[key]
                for key in ("reachable", "access-restricted", "missing", "timeout", "error")
            ),
        )
        self.assertEqual(0, summary["missing"])
        self.assertEqual(
            summary["source_count"],
            summary["external_first_party_source_count"]
            + summary["openfs_governance_source_count"],
        )
        self.assertEqual(summary["source_count"], sum(summary["source_class_counts"].values()))
        self.assertEqual(
            {
                source["source_class"]
                for roadmap in self.roadmaps
                for source in roadmap["sources"]
            },
            {key for key, value in summary["source_class_counts"].items() if value},
        )

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

    def test_duplicate_urls_use_identical_canonical_metadata(self):
        by_url = defaultdict(list)
        for roadmap in self.roadmaps:
            for source in roadmap["sources"]:
                by_url[source["url"]].append(source)
        for url, registrations in by_url.items():
            if len(registrations) < 2:
                continue
            metadata = {
                (
                    source["title"],
                    source["publisher"],
                    source["source_class"],
                    source.get("published_at"),
                )
                for source in registrations
            }
            self.assertEqual(1, len(metadata), url)

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

        open_p0_gaps = {
            gap["gap_id"]
            for roadmap in self.roadmaps
            for gap in roadmap["coverage_gaps"]
            if gap["priority"] == "P0" and gap["status"] == "open"
        }
        edge_gap_refs = {
            gap_id
            for dependency in self.dependencies["dependencies"]
            for gap_id in dependency["coverage_gap_refs"]
            if gap_id in open_p0_gaps
        }
        portfolio_gate_gap_refs = set(self.dependencies["portfolio_gate_gap_refs"])
        self.assertFalse(edge_gap_refs & portfolio_gate_gap_refs)
        self.assertEqual(open_p0_gaps, edge_gap_refs | portfolio_gate_gap_refs)

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
        p0_gap_refs = {
            gap["gap_id"]
            for roadmap in self.roadmaps
            for gap in roadmap["coverage_gaps"]
            if gap["priority"] == "P0"
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
            self.assertEqual(p0_gap_refs, set(scenario["decision_blocking_gap_refs"]))
            for evaluation in scenario["evaluation"].values():
                self.assertLessEqual(set(evaluation["evidence_refs"]), known_evidence_refs)

    def test_decision_evidence_contracts_cover_each_open_p0_gap_exactly_once(self):
        p0_gap_refs = {
            gap["gap_id"]
            for roadmap in self.roadmaps
            for gap in roadmap["coverage_gaps"]
            if gap["priority"] == "P0" and gap["status"] == "open"
        }
        contracts = self.scenarios["decision_evidence_contracts"]
        self.assertEqual(6, len(contracts))
        self.assertEqual(len(contracts), len({item["contract_id"] for item in contracts}))
        assigned = [gap_id for contract in contracts for gap_id in contract["gap_refs"]]
        self.assertEqual(p0_gap_refs, set(assigned))
        self.assertEqual(len(assigned), len(set(assigned)))
        for contract in contracts:
            self.assertEqual("candidate-only", contract["acceptance_effect"])
            for relative_path in contract["schema_paths"] + contract["validator_paths"]:
                self.assertTrue((ROOT / relative_path).is_file(), relative_path)


if __name__ == "__main__":
    unittest.main()
