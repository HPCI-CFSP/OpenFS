from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_pages_site import (  # noqa: E402
    build,
    collect_consensus_packages,
    collect_consensus_receipts,
    collect_roadmaps,
    collect_roadmap_reference_data,
    collect_scenarios,
    collect_topic_summaries,
)


class PageStructureParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.fragment_links = []

    def handle_starttag(self, _tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"])
        if values.get("href", "").startswith("#"):
            self.fragment_links.append(values["href"][1:])


class PagesSiteTests(unittest.TestCase):
    def publication_policy(self):
        return json.loads(
            (ROOT / "config" / "publication-policy.json").read_text(encoding="utf-8")
        )

    def write_roadmap_fixture(self, root):
        (root / "config").mkdir(parents=True)
        shutil.copy2(
            ROOT / "config" / "roadmap-portfolio.json",
            root / "config" / "roadmap-portfolio.json",
        )
        shutil.copytree(
            ROOT / "knowledge" / "public" / "roadmaps",
            root / "knowledge" / "public" / "roadmaps",
        )
        directives = root / "reviews" / "directives"
        directives.mkdir(parents=True)
        for name in ("DIR-900004.json", "DIR-900005.json"):
            shutil.copy2(ROOT / "reviews" / "directives" / name, directives / name)
        return root / "knowledge" / "public" / "roadmaps" / "memory-data-movement.json"

    def write_consensus_fixture(self, root, commit_sha="a" * 40):
        directives = root / "reviews" / "directives"
        directives.mkdir(parents=True)
        directive = {
            "directive_id": "DIR-000003",
            "directive_type": "publication-approval",
            "status": "approved",
            "submitted_by": "test-human",
            "submitted_at": "2026-08-25T00:00:00Z",
            "publication_targets": [
                "CONSENSUS-RECEIPT-EXPORT-999",
                "TOPIC-SUMMARY-EXPORT-999",
            ],
        }
        (directives / "DIR-000003.json").write_text(
            json.dumps(directive), encoding="utf-8"
        )
        receipts = {
            "schema_version": "0.1.0",
            "export_id": "CONSENSUS-RECEIPT-EXPORT-999",
            "status": "published",
            "as_of": "2026-08-25",
            "receipts": [
                {
                    "receipt_id": "CSR-TEST-001",
                    "decision_id": "DEC-TEST-001",
                    "finding_ids": ["FND-TEST-001"],
                    "outcome": "accepted",
                    "decided_at": "2026-08-25T00:00:00Z",
                    "policy_id": "CONSENSUS-001",
                    "policy_requirements": {
                        "minimum_assessments": 2,
                        "minimum_support": 2,
                        "minimum_independence_groups": 2,
                        "falsification_review_required": True,
                    },
                    "policy_result": {
                        "assessment_count": 2,
                        "support_count": 2,
                        "independence_groups": ["group-a", "group-b"],
                        "falsification_review_passed": True,
                        "critical_objection_count": 0,
                    },
                    "independence_group_count": 2,
                    "participants": [
                        {
                            "agent_id": "validator-a",
                            "role": "validator",
                            "provider": "Provider A",
                            "model_family": "Model A",
                            "prompt_profile": "validator-v1",
                            "independence_group": "group-a",
                            "contribution": "supporting-validator",
                            "assessment_id": "ASM-TEST-001",
                            "harness_id": "HAR-OPENFS",
                        },
                        {
                            "agent_id": "validator-b",
                            "role": "falsification-validator",
                            "provider": "Provider B",
                            "model_family": "Model B",
                            "prompt_profile": "critic-v1",
                            "independence_group": "group-b",
                            "contribution": "falsification-critic",
                            "assessment_id": "ASM-TEST-002",
                            "harness_id": "HAR-OPENFS",
                        },
                    ],
                    "harnesses": [
                        {
                            "harness_id": "HAR-OPENFS",
                            "name": "OpenFS",
                            "repository_url": "https://github.com/HPCI-CFSP/OpenFS",
                            "commit_sha": commit_sha,
                            "run_id": "RUN-TEST-001",
                            "agent_registry_digest": "b" * 64,
                            "configuration_digest": "c" * 64,
                        }
                    ],
                }
            ],
            "publication": {
                "information_classification": "public",
                "publication_approved": True,
                "publication_decision_id": "PUBDEC-TEST-001",
                "human_approval_directive_id": "DIR-000003",
            },
        }
        receipt_path = root / "knowledge" / "public"
        receipt_path.mkdir(parents=True)
        (receipt_path / "consensus-receipts.json").write_text(
            json.dumps(receipts), encoding="utf-8"
        )

        summaries = {
            "schema_version": "0.1.0",
            "export_id": "TOPIC-SUMMARY-EXPORT-999",
            "status": "published",
            "as_of": "2026-08-25",
            "summaries": [
                {
                    "summary_id": "SUM-TEST-001",
                    "topic_ids": ["ARCH-03"],
                    "title_ja": "テスト",
                    "title_en": "Test",
                    "summary_ja": "テスト要約",
                    "summary_en": "Test summary",
                    "source_run_id": "RUN-TEST-001",
                    "generated_at": "2026-08-25T00:00:00Z",
                    "research_status": "accepted",
                    "coverage_status": "complete",
                    "consensus_status": "accepted",
                    "findings": [
                        {
                            "finding_id": "FND-TEST-001",
                            "topic_ids": ["ARCH-03"],
                            "statement_ja": "検証済みの知見",
                            "statement_en": "Validated finding",
                            "consensus_receipt_id": "CSR-TEST-001",
                            "sources": [
                                {
                                    "source_id": "SRC-TEST001",
                                    "title": "Public source",
                                    "publisher": "Publisher",
                                    "url": "https://example.org/source",
                                }
                            ],
                        }
                    ],
                    "caveat_ja": "公開用の注意事項",
                    "caveat_en": "Public caveat",
                }
            ],
            "publication": {
                "information_classification": "public",
                "publication_approved": True,
                "publication_decision_id": "PUBDEC-TEST-002",
                "human_approval_directive_id": "DIR-000003",
            },
        }
        (receipt_path / "topic-summaries.json").write_text(
            json.dumps(summaries), encoding="utf-8"
        )

    def test_pages_workflow_installs_pinned_validators_before_tests(self):
        workflow = (
            ROOT / ".github" / "workflows" / "pages.yml"
        ).read_text(encoding="utf-8")
        install_step = "Install pinned contract validators"
        test_step = "Run unit tests"
        self.assertIn('- "requirements-validation.txt"', workflow)
        self.assertIn("--requirement requirements-validation.txt", workflow)
        self.assertLess(workflow.index(install_step), workflow.index(test_step))
        self.assertIn('"knowledge/public/**"', workflow)
        self.assertIn("fetch-depth: 0", workflow)

    def test_pr_preview_is_artifact_only_and_read_only(self):
        workflow = (
            ROOT / ".github" / "workflows" / "pages-preview.yml"
        ).read_text(encoding="utf-8")
        self.assertIn("pull_request:", workflow)
        self.assertIn("contents: read", workflow)
        self.assertIn("actions/upload-artifact@", workflow)
        self.assertIn("retention-days: 14", workflow)
        self.assertNotIn("pages: write", workflow)
        self.assertNotIn("id-token: write", workflow)
        self.assertNotIn("actions/deploy-pages@", workflow)
        self.assertIn('"knowledge/public/**"', workflow)
        self.assertIn("fetch-depth: 0", workflow)

    def test_page_fragment_navigation_has_unique_existing_targets(self):
        parser = PageStructureParser()
        parser.feed((ROOT / "site" / "index.html").read_text(encoding="utf-8"))
        self.assertEqual(len(parser.ids), len(set(parser.ids)))
        self.assertTrue(parser.fragment_links)
        self.assertEqual([], sorted(set(parser.fragment_links) - set(parser.ids)))

    def test_roadmap_reference_data_and_detail_ui_are_connected(self):
        policy = self.publication_policy()
        roadmaps = collect_roadmaps(ROOT, policy, False)
        reference_data = collect_roadmap_reference_data(
            ROOT, policy, roadmaps, False
        )
        self.assertEqual(46, len(reference_data["terms"]))
        self.assertEqual(7, len(reference_data["comparison_sets"]))
        detail = (ROOT / "site" / "roadmap-detail.html").read_text(encoding="utf-8")
        for element_id in (
            'id="roadmap-comparisons"',
            'id="roadmap-glossary"',
            'id="roadmap-term-dialog"',
            'id="hpci-system-inventory-section"',
            'id="hpci-inventory-table"',
            'id="application-performance-section"',
            'id="application-performance-table"',
        ):
            self.assertIn(element_id, detail)
        script = (ROOT / "site" / "roadmaps.js").read_text(encoding="utf-8")
        self.assertIn("function renderHPCIInventory", script)
        self.assertIn("function renderApplicationPerformance", script)
        performance_rows = script[script.index("performance.applications.forEach") :]
        self.assertLess(
            performance_rows.index("row.append(app);"),
            performance_rows.index("performance.standard_fugaku_node_scales.forEach"),
        )
        self.assertNotIn("row.append(app, cell)", performance_rows)

    def test_timeline_uses_evidence_window_spans_without_q_unknown_column(self):
        script = (ROOT / "site" / "roadmaps.js").read_text(encoding="utf-8")
        self.assertIn("function milestoneGridRange", script)
        self.assertIn('milestone.half === "H1" ? [1, 3] : [3, 5]', script)
        self.assertIn('return [1, 5]', script)
        self.assertIn('Array(years.length).fill("roadmap-year-column")', script)
        self.assertIn("function generationBandGridRange", script)
        self.assertIn("function generationBandPeriodLabel", script)
        self.assertIn("function renderRoadmapGenerationBandDialog", script)
        self.assertIn("roadmap.horizon.end_year", script)
        self.assertNotIn("const years = [2026, 2027, 2028, 2029, 2030, 2031, 2032]", script)
        self.assertNotIn('fill("roadmap-quarter-column")', script)

    def test_build_publishes_catalog_and_approved_scenarios_only(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            result = build(ROOT, output)
            self.assertEqual(58, len(result["topics"]))
            self.assertEqual(3, len(result["research_summaries"]))
            decision_support = result["topic_decision_support"]
            self.assertEqual(5, len(decision_support["topic_profiles"]))
            self.assertEqual(6, len(decision_support["platform_matrix"]["platforms"]))
            self.assertEqual(6, len(decision_support["numerical_method_matrix"]["methods"]))
            self.assertNotIn("publication", decision_support)
            arch02 = next(
                profile
                for profile in decision_support["topic_profiles"]
                if profile["topic_id"] == "ARCH-02"
            )
            self.assertTrue(
                any(
                    "MN-Core" in item["name_en"]
                    for section in arch02["sections"]
                    for item in section["items"]
                )
            )
            topics_by_id = {topic["topic_id"]: topic for topic in result["topics"]}
            self.assertGreater(topics_by_id["SSW-04"]["decision_item_count"], 0)
            self.assertEqual([], result["consensus_receipts"])
            self.assertEqual(1, len(result["consensus_packages"]))
            package = result["consensus_packages"][0]
            self.assertEqual("CRP-P0-ROADMAPS-V02", package["package_id"])
            self.assertEqual("incomplete", package["gate"]["status"])
            self.assertEqual([], package["eligible_reviewers"])
            self.assertGreaterEqual(package["artifact_count"], 20)
            self.assertEqual(40, len(package["base_commit"]))
            self.assertEqual(64, len(package["manifest_sha256"]))
            self.assertEqual(46, len(result["roadmap_reference_data"]["terms"]))
            self.assertEqual(
                7, len(result["roadmap_reference_data"]["comparison_sets"])
            )
            self.assertNotIn("publication", result["roadmap_reference_data"])
            self.assertEqual(27, len(result["hpci_system_inventory"]["systems"]))
            self.assertNotIn("publication", result["hpci_system_inventory"])
            self.assertEqual(
                [1, 4, 32, 128, 1024, 10000],
                result["application_performance_forecasts"]["standard_fugaku_node_scales"],
            )
            self.assertEqual(36, len(result["application_performance_forecasts"]["forecasts"]))
            self.assertEqual(2, len(result["application_performance_forecasts"]["candidate_systems"]))
            self.assertEqual(8, len(result["application_performance_forecasts"]["baseline_observations"]))
            self.assertEqual(6, len(result["application_performance_forecasts"]["assumptions"]))
            self.assertNotIn("publication", result["application_performance_forecasts"])
            self.assertEqual(
                package["manifest_sha256"],
                package["gate"]["package_manifest_digest"],
            )
            self.assertEqual(3, len(result["scenarios"]))
            self.assertEqual(
                {
                    "SCN-HPCI-BALANCED-001",
                    "SCN-HPCI-AI-DATA-001",
                    "SCN-HPCI-STAGED-001",
                },
                {scenario["scenario_id"] for scenario in result["scenarios"]},
            )
            self.assertTrue(
                all(
                    scenario["research_status"] == "provisional"
                    and scenario["consensus_status"] == "incomplete"
                    and len(scenario["decision_blocking_gap_refs"]) == 16
                    and len(scenario["decision_evidence_contracts"]) == 6
                    for scenario in result["scenarios"]
                )
            )
            scenario_html = (
                output / result["scenarios"][0]["path"] / "index.html"
            ).read_text(encoding="utf-8")
            self.assertIn('id="scenario-blocking-gaps"', scenario_html)
            self.assertIn('id="scenario-evidence-contracts"', scenario_html)
            self.assertTrue(
                all(
                    scenario["path"].startswith("scenarios/scn-hpci-")
                    and len(scenario["source_commit"]) == 40
                    and "publication" not in scenario
                    for scenario in result["scenarios"]
                )
            )
            assurance = result["roadmap_assurance"]
            self.assertGreaterEqual(assurance["source_audit"]["summary"]["source_count"], 91)
            self.assertLess(
                assurance["source_audit"]["summary"]["unique_url_count"],
                assurance["source_audit"]["summary"]["source_count"],
            )
            self.assertEqual(
                assurance["source_audit"]["summary"]["source_count"]
                - assurance["source_audit"]["summary"]["unique_url_count"],
                assurance["source_audit"]["summary"]["duplicate_registration_count"],
            )
            self.assertEqual(
                assurance["source_audit"]["summary"]["source_count"]
                - assurance["source_audit"]["summary"]["reachable"],
                assurance["source_triage"]["summary"]["non_reachable_count"],
            )
            self.assertEqual(0, assurance["source_triage"]["summary"]["unresolved"])
            center_profiles = assurance["center_profile_assurance"]
            self.assertEqual(15, center_profiles["summary"]["center_count"])
            self.assertEqual(0, center_profiles["summary"]["accepted_current_count"])
            self.assertEqual(30, center_profiles["summary"]["not_collected"])
            self.assertEqual(
                {"GAP-BLUE-001", "GAP-BLUE-003"},
                {item["gap_id"] for item in center_profiles["gap_status"]},
            )
            self.assertTrue(
                all(item["status"] == "open" for item in center_profiles["gap_status"])
            )
            self.assertGreaterEqual(assurance["evidence_audit"]["summary"]["milestone_count"], 130)
            self.assertGreaterEqual(assurance["freshness_audit"]["summary"]["milestone_count"], 130)
            self.assertEqual(0, assurance["freshness_audit"]["summary"]["future_observed_conflicts"])
            self.assertEqual(34, assurance["gap_queue"]["summary"]["gap_count"])
            self.assertEqual(16, assurance["gap_queue"]["summary"]["p0"])
            self.assertEqual(
                16,
                len(
                    [
                        item
                        for item in assurance["gap_queue"]["assignments"]
                        if item["priority"] == "P0"
                    ]
                ),
            )
            self.assertTrue(
                all(
                    item["closure_state"] == "criteria-unverified"
                    and item["closure_plan"]["minimum_independent_origin_groups"] >= 2
                    and item["closure_plan"]["requires_consensus_gate"] is True
                    and item["closure_plan"]["criteria"]
                    for item in assurance["gap_queue"]["assignments"]
                    if item["priority"] == "P0"
                )
            )
            self.assertEqual(
                14,
                len(assurance["dependency_register"]["dependencies"]),
            )
            self.assertTrue(
                all("publication" not in artifact for artifact in assurance.values())
            )
            self.assertIn(
                'id="center-profile-centers"',
                (output / "roadmaps" / "evidence" / "index.html").read_text(
                    encoding="utf-8"
                ),
            )
            self.assertGreaterEqual(
                sum(len(roadmap["coverage_gaps"]) for roadmap in result["roadmap_artifacts"]),
                30,
            )
            self.assertEqual([], result["reports"])
            self.assertEqual("2026-08-23", result["catalog_as_of"])
            self.assertEqual(40, len(result["site"]["commit_sha"]))
            self.assertTrue(result["site"]["commit_url"].endswith(result["site"]["commit_sha"]))
            self.assertIn("T", result["site"]["updated_at"])
            self.assertEqual(6, len(result["roadmaps"]))
            roadmap_index_by_id = {
                roadmap["roadmap_id"]: roadmap for roadmap in result["roadmaps"]
            }
            memory_index = roadmap_index_by_id["RM-HW-MEMORY"]
            self.assertEqual("hardware", memory_index["domain"])
            self.assertEqual(
                "roadmaps/hardware/memory-data-movement/",
                memory_index["path"],
            )
            self.assertEqual("common-quarterly", memory_index["renderer"])
            self.assertEqual(11, memory_index["track_count"])
            self.assertGreaterEqual(memory_index["milestone_count"], 50)
            roadmap_by_id = {
                roadmap["roadmap_id"]: roadmap
                for roadmap in result["roadmap_artifacts"]
            }
            memory_roadmap = roadmap_by_id["RM-HW-MEMORY"]
            self.assertEqual(
                "MEMORY-ROADMAP-EXPORT-001",
                memory_roadmap["export_id"],
            )
            self.assertEqual(
                {
                    "start_year": 2026,
                    "end_year": 2032,
                    "extension_policy": "extend-to-latest-dated-evidence",
                },
                memory_roadmap["horizon"],
            )
            self.assertEqual("quarter", memory_roadmap["timeline_granularity"])
            self.assertEqual(11, len(memory_roadmap["tracks"]))
            self.assertEqual(
                "JEDEC",
                next(
                    lane["owner"]
                    for lane in memory_roadmap["lanes"]
                    if lane["track_id"] == "MEMTECH-DDR"
                ),
            )
            generation_band_ids = {
                band["generation_band_id"]
                for track in memory_roadmap["tracks"]
                for band in track.get("generation_bands", [])
            }
            self.assertEqual(
                {
                    "GB-DDR5-ECOSYSTEM",
                    "GB-DDR6-PROJECTION-2028",
                    "GB-LPDDR6-INTRODUCTION",
                    "GB-HBM4-COMMERCIAL",
                    "GB-HBM4E-SAMPLE-PRODUCTION",
                    "GB-SOCAMM2-COMMERCIAL",
                    "GB-CXL2-3-PRODUCTS",
                },
                generation_band_ids,
            )
            self.assertEqual("hardware", memory_roadmap["domain"])
            self.assertEqual(
                "hardware/memory-data-movement", memory_roadmap["slug"]
            )
            self.assertEqual(40, len(memory_roadmap["source_commit"]))
            self.assertTrue(
                any(
                    milestone["year"] == 2032
                    for lane in memory_roadmap["lanes"]
                    for milestone in lane["milestones"]
                )
            )
            self.assertTrue(
                any(
                    milestone["year"] is None
                    for lane in memory_roadmap["lanes"]
                    for milestone in lane["milestones"]
                )
            )
            milestones = {
                milestone["milestone_id"]: milestone
                for lane in memory_roadmap["lanes"]
                for milestone in lane["milestones"]
            }
            self.assertEqual("Q1", milestones["MS-HBM-MICRON-2026"]["quarter"])
            self.assertEqual("Q2", milestones["MS-DDR-MICRON-2026B"]["quarter"])
            self.assertEqual("Q3", milestones["MS-3D-DRAM-SAMSUNG-2026"]["quarter"])
            self.assertIsNone(milestones["MS-HBM-MICRON-2027"]["quarter"])
            self.assertEqual("year", milestones["MS-HBM-MICRON-2027"]["timing_precision"])
            self.assertEqual(
                "undated",
                milestones["MS-CXL-MICRON-UNDATED"]["timing_precision"],
            )
            self.assertGreaterEqual(
                len(
                    {
                        lane["owner"]
                        for lane in memory_roadmap["lanes"]
                        if lane["track_id"] == "MEMTECH-HBM"
                    }
                ),
                3,
            )
            self.assertNotIn("publication", memory_roadmap)
            self.assertEqual("public-only", result["publication"]["information_plane"])
            self.assertEqual("Apache-2.0", result["publication"]["license"])
            self.assertTrue(all(topic["title_en"] for topic in result["topics"]))
            self.assertTrue(
                all(
                    "research_summary_count" in topic
                    and "research_finding_count" in topic
                    for topic in result["topics"]
                )
            )
            topic_by_id = {topic["topic_id"]: topic for topic in result["topics"]}
            self.assertGreater(topic_by_id["ARCH-03"]["research_finding_count"], 0)
            self.assertEqual(2, topic_by_id["ARCH-04"]["research_summary_count"])
            self.assertEqual(3, topic_by_id["ARCH-04"]["research_finding_count"])
            self.assertTrue(
                all(
                    finding["sources"]
                    for summary in result["research_summaries"]
                    for finding in summary["findings"]
                )
            )
            self.assertTrue(
                all(
                    summary["research_status"] in {"provisional", "accepted"}
                    for summary in result["research_summaries"]
                )
            )
            self.assertTrue(
                all("publication" not in summary for summary in result["research_summaries"])
            )
            for summary in result["research_summaries"]:
                represented_topics = {
                    topic_id
                    for finding in summary["findings"]
                    for topic_id in finding["topic_ids"]
                }
                self.assertEqual(set(summary["topic_ids"]), represented_topics)
            app02_findings = [
                finding
                for summary in result["research_summaries"]
                for finding in summary["findings"]
                if "APP-02" in finding["topic_ids"]
            ]
            self.assertTrue(app02_findings)
            self.assertTrue(
                all("富岳" in finding["statement_ja"] for finding in app02_findings)
            )
            self.assertNotIn("domestic_technology", result)
            self.assertEqual(12, len(result["technology_landscape"]["categories"]))
            self.assertTrue(
                all(set(category) == {"ja", "en"} for category in result["technology_landscape"]["categories"])
            )
            self.assertNotIn("scope_rule", result["technology_landscape"])
            self.assertNotIn("priority_rule", result["technology_landscape"])
            self.assertNotIn("priority_regions", result["technology_landscape"])
            self.assertTrue((output / "index.html").is_file())
            self.assertTrue((output / "data" / "openfs-public.js").is_file())
            self.assertTrue((output / "roadmaps.js").is_file())
            self.assertTrue((output / "planning.js").is_file())
            self.assertTrue((output / "roadmaps" / "index.html").is_file())
            self.assertTrue((output / "roadmaps" / "compare" / "index.html").is_file())
            self.assertTrue((output / "roadmaps" / "evidence" / "index.html").is_file())
            self.assertTrue((output / "scenarios" / "index.html").is_file())
            self.assertTrue((output / "consensus" / "index.html").is_file())
            self.assertTrue(
                (output / "consensus" / "crp-p0-roadmaps-v02" / "index.html").is_file()
            )
            self.assertTrue(
                (
                    output
                    / "scenarios"
                    / "scn-hpci-balanced-001"
                    / "index.html"
                ).is_file()
            )
            self.assertTrue(
                (
                    output
                    / "roadmaps"
                    / "hardware"
                    / "memory-data-movement"
                    / "index.html"
                ).is_file()
            )
            rendered = (output / "data" / "openfs-public.js").read_text(encoding="utf-8")
            self.assertNotIn("SCN-EXAMPLE", rendered)
            self.assertNotIn("Illustrative archetypes", rendered)
            self.assertIn("SUM-MEMORY-PILOT-003", rendered)
            self.assertIn("https://www.usenix.org/conference/nsdi26", rendered)
            self.assertIn("SRC-MEM037", rendered)
            self.assertIn("MEMTECH-SOCAMM", rendered)
            self.assertIn("ROADMAP-EVIDENCE-AUDIT-001", rendered)
            self.assertIn("ROADMAP-DEPENDENCY-REGISTER-001", rendered)
            self.assertIn("SCN-HPCI-BALANCED-001", rendered)
            self.assertIn("CRP-P0-ROADMAPS-V02", rendered)
            self.assertIn('"catalog_as_of":"2026-08-23"', rendered)
            self.assertIn('"path":"roadmaps/hardware/memory-data-movement/"', rendered)
            index = (output / "index.html").read_text(encoding="utf-8")
            asset_version = result["site"]["commit_sha"]
            self.assertIn(f'href="roadmaps/?v={asset_version}"', index)
            self.assertNotIn('href="#roadmaps"', index)
            self.assertIn(f'src="data/openfs-public.js?v={asset_version}"', index)
            self.assertIn(f'src="app.js?v={asset_version}"', index)
            self.assertNotIn('href="#domestic"', index)
            app = (output / "app.js").read_text(encoding="utf-8")
            roadmap_app = (output / "roadmaps.js").read_text(encoding="utf-8")
            roadmap_index = (output / "roadmaps" / "index.html").read_text(
                encoding="utf-8"
            )
            evidence_index = (
                output / "roadmaps" / "evidence" / "index.html"
            ).read_text(encoding="utf-8")
            roadmap_detail = (
                output
                / "roadmaps"
                / "hardware"
                / "memory-data-movement"
                / "index.html"
            ).read_text(encoding="utf-8")
            for public_copy in (index, app, rendered):
                self.assertNotIn("調査対象地域", public_copy)
                self.assertNotIn("日本発技術を優先", public_copy)
                self.assertNotIn("Priority coverage for Japan", public_copy)
            self.assertIn('id="topic-dialog"', index)
            self.assertNotIn('id="roadmap-dialog"', index)
            self.assertNotIn('id="memory-roadmap-timeline"', index)
            self.assertIn('id="roadmap-home-rows"', index)
            self.assertIn('id="roadmap-rows"', roadmap_index)
            self.assertIn('id="source-class-summary"', evidence_index)
            self.assertIn("sourceClassOrder", (output / "planning.js").read_text(encoding="utf-8"))
            self.assertIn('id="roadmap-timeline"', roadmap_detail)
            self.assertIn('id="roadmap-comparisons"', roadmap_detail)
            self.assertIn('id="roadmap-glossary"', roadmap_detail)
            self.assertIn('id="roadmap-term-dialog"', roadmap_detail)
            self.assertIn('data-roadmap-id="MEMORY-ROADMAP-EXPORT-001"', roadmap_detail)
            self.assertNotIn("{{ROOT_PREFIX}}", roadmap_index)
            self.assertNotIn("{{ROOT_PREFIX}}", roadmap_detail)
            self.assertNotIn("{{ASSET_VERSION}}", index)
            self.assertNotIn("{{ASSET_VERSION}}", roadmap_index)
            self.assertNotIn("{{ASSET_VERSION}}", roadmap_detail)
            self.assertIn(
                f'src="../data/openfs-public.js?v={asset_version}"', roadmap_index
            )
            self.assertIn("roadmap-quarter-scale", roadmap_app)
            self.assertIn("milestonePeriodLabel", roadmap_app)
            self.assertNotIn('tr("quarterUnknown")', roadmap_app)
            self.assertNotIn('data-i18n="scopeMetric"', index)
            self.assertIn("openTopicDetail", app)
            self.assertIn("renderRoadmapHome", app)
            self.assertIn("formatJst", app)
            self.assertIn("openRoadmapMilestone", roadmap_app)
            self.assertIn("renderRoadmapDetail", roadmap_app)
            self.assertIn("renderRoadmapIndex", roadmap_app)
            self.assertIn("renderComparison", roadmap_app)
            self.assertIn('tr("findingAvailable")', app)
            self.assertNotIn('tr("sourceSurvey")', app)
            self.assertNotIn("research-source-title", app)
            self.assertIn("decisionProfileForTopic", app)
            self.assertIn("renderRegionFilter", app)
            self.assertIn("renderPlatformMatrix", app)
            self.assertIn("renderNumericalMatrix", app)
            self.assertIn('localized(summary, "summary")', app)
            self.assertIn("renderConsensusReceipt", app)
            self.assertIn("consensusProof", app)
            self.assertIn("/commit/${harness.commit_sha}", app)
            self.assertNotIn("summary.summary_ja", app)
            self.assertNotIn("summary.summary_en", app)
            self.assertNotIn('scopeMetric:', app)

    def test_consensus_package_requires_explicit_publication_directive(self):
        policy = self.publication_policy()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = ROOT / "reviews" / "consensus-packages" / "CRP-P0-ROADMAPS-V02"
            shutil.copytree(
                source,
                root / "reviews" / "consensus-packages" / "CRP-P0-ROADMAPS-V02",
            )
            with self.assertRaisesRegex(ValueError, "no human publication Directive"):
                collect_consensus_packages(root, policy, include_commit_metadata=False)

    def test_consensus_package_rejects_stale_gate_manifest_digest(self):
        policy = self.publication_policy()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = ROOT / "reviews" / "consensus-packages" / "CRP-P0-ROADMAPS-V02"
            target = root / "reviews" / "consensus-packages" / "CRP-P0-ROADMAPS-V02"
            shutil.copytree(source, target)
            directives = root / "reviews" / "directives"
            directives.mkdir(parents=True)
            shutil.copy2(ROOT / "reviews" / "directives" / "DIR-900007.json", directives)
            gate_path = target / "gate-result.json"
            gate = json.loads(gate_path.read_text(encoding="utf-8"))
            gate["package_manifest_digest"] = "f" * 64
            gate_path.write_text(json.dumps(gate), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "gate manifest digest mismatch"):
                collect_consensus_packages(root, policy, include_commit_metadata=False)

    def test_consensus_package_rejects_stale_review_digest_set(self):
        policy = self.publication_policy()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = ROOT / "reviews" / "consensus-packages" / "CRP-P0-ROADMAPS-V02"
            target = root / "reviews" / "consensus-packages" / "CRP-P0-ROADMAPS-V02"
            shutil.copytree(source, target)
            directives = root / "reviews" / "directives"
            directives.mkdir(parents=True)
            shutil.copy2(ROOT / "reviews" / "directives" / "DIR-900007.json", directives)
            gate_path = target / "gate-result.json"
            gate = json.loads(gate_path.read_text(encoding="utf-8"))
            gate["review_results"]["review_file_digests"] = {
                "CRV-STALE": "f" * 64
            }
            gate_path.write_text(json.dumps(gate), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "gate review digest set mismatch"):
                collect_consensus_packages(root, policy, include_commit_metadata=False)

    def test_memory_roadmap_rejects_unknown_source_reference(self):
        policy = self.publication_policy()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_roadmap_fixture(root)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["lanes"][0]["milestones"][0]["source_ids"] = ["SRC-MEM999"]
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unknown sources"):
                collect_roadmaps(root, policy, include_commit_metadata=False)

    def test_memory_roadmap_extends_to_later_dated_evidence(self):
        policy = self.publication_policy()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_roadmap_fixture(root)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["lanes"][0]["milestones"][0]["year"] = 2034
            path.write_text(json.dumps(payload), encoding="utf-8")
            result = collect_roadmaps(root, policy, include_commit_metadata=False)
            memory = next(item for item in result if item["roadmap_id"] == "RM-HW-MEMORY")
            self.assertEqual(2034, memory["horizon"]["end_year"])

    def test_fixed_horizon_rejects_later_dated_evidence(self):
        policy = self.publication_policy()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_roadmap_fixture(root)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["horizon"]["extension_policy"] = "fixed"
            payload["lanes"][0]["milestones"][0]["year"] = 2034
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "outside its fixed horizon"):
                collect_roadmaps(root, policy, include_commit_metadata=False)

    def test_generation_band_rejects_unknown_source(self):
        policy = self.publication_policy()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_roadmap_fixture(root)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["tracks"][0]["generation_bands"][0]["source_ids"] = ["SRC-MEM999"]
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "generation band .* unknown sources"):
                collect_roadmaps(root, policy, include_commit_metadata=False)

    def test_generation_band_rejects_reversed_range(self):
        policy = self.publication_policy()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_roadmap_fixture(root)
            payload = json.loads(path.read_text(encoding="utf-8"))
            band = payload["tracks"][0]["generation_bands"][1]
            band["end"] = {"year": 2027, "quarter": None, "half": None, "precision": "year"}
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "reversed range"):
                collect_roadmaps(root, policy, include_commit_metadata=False)

    def test_memory_roadmap_rejects_quarter_without_quarter_precision(self):
        policy = self.publication_policy()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_roadmap_fixture(root)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["lanes"][0]["milestones"][0]["quarter"] = "Q1"
            payload["lanes"][0]["milestones"][0]["timing_precision"] = "year"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "inconsistent timing precision"):
                collect_roadmaps(root, policy, include_commit_metadata=False)

    def test_half_year_milestone_requires_named_half(self):
        policy = self.publication_policy()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_roadmap_fixture(root)
            payload = json.loads(path.read_text(encoding="utf-8"))
            milestone = next(
                item
                for lane in payload["lanes"]
                for item in lane["milestones"]
                if item["milestone_id"] == "MS-LPDDR-SKHYNIX-2026"
            )
            milestone.pop("half")
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "half-year roadmap milestone"):
                collect_roadmaps(root, policy, include_commit_metadata=False)

    def test_non_half_year_milestone_rejects_half_value(self):
        policy = self.publication_policy()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = self.write_roadmap_fixture(root)
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["lanes"][0]["milestones"][0]["half"] = "H1"
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unexpected half-year value"):
                collect_roadmaps(root, policy, include_commit_metadata=False)

    def test_accepted_finding_publishes_consensus_receipt(self):
        policy = self.publication_policy()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_consensus_fixture(root)
            receipts = collect_consensus_receipts(root, policy)
            receipt_by_id = {item["receipt_id"]: item for item in receipts}
            summaries = collect_topic_summaries(
                root, policy, {"ARCH-03"}, receipt_by_id
            )
            finding = summaries[0]["findings"][0]
            self.assertEqual("CSR-TEST-001", finding["consensus_receipt_id"])
            self.assertEqual(2, receipts[0]["independence_group_count"])
            self.assertEqual("a" * 40, receipts[0]["harnesses"][0]["commit_sha"])

    def test_consensus_receipt_rejects_abbreviated_commit_sha(self):
        policy = self.publication_policy()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_consensus_fixture(root, commit_sha="abcdef1")
            with self.assertRaisesRegex(ValueError, "invalid harness commit SHA"):
                collect_consensus_receipts(root, policy)

    def test_consensus_receipt_rejects_one_model_under_multiple_agents(self):
        policy = self.publication_policy()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_consensus_fixture(root)
            path = root / "knowledge" / "public" / "consensus-receipts.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            participants = payload["receipts"][0]["participants"]
            participants[1]["provider"] = participants[0]["provider"]
            participants[1]["model_family"] = participants[0]["model_family"]
            path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "fewer than two model identities"):
                collect_consensus_receipts(root, policy)

    def test_accepted_finding_requires_matching_consensus_receipt(self):
        policy = self.publication_policy()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.write_consensus_fixture(root)
            with self.assertRaisesRegex(ValueError, "no matching Consensus Receipt"):
                collect_topic_summaries(root, policy, {"ARCH-03"}, {})

    def test_publication_policy_rejects_candidate_scenario_status(self):
        policy = json.loads((ROOT / "config" / "publication-policy.json").read_text(encoding="utf-8"))
        self.assertNotIn("accepted", policy["accepted_scenario_statuses"])
        self.assertNotIn("candidate", policy["accepted_scenario_statuses"])
        self.assertNotIn("illustrative-example", policy["accepted_scenario_statuses"])

    def test_published_scenario_is_allowlisted_and_requires_publication_decision(self):
        policy = json.loads((ROOT / "config" / "publication-policy.json").read_text(encoding="utf-8"))
        scenario = {
            "scenario_id": "SCN-PUBLIC-001",
            "title_ja": "公開シナリオ",
            "title_en": "Published scenario",
            "status": "published",
            "objective": "公開用の要約",
            "objective_en": "Public summary",
            "uncertainties": ["未確認条件"],
            "uncertainties_en": ["Unverified condition"],
            "decision_gates": ["人による判断"],
            "decision_gates_en": ["Human decision"],
            "caveat_ja": "公開用注意",
            "caveat_en": "Publication caveat",
            "nda_internal_note": "must never be emitted",
            "publication": {
                "information_classification": "public",
                "publication_approved": True,
                "publication_decision_id": "DEC-PUB-001",
                "human_approval_directive_id": "DIR-000001",
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "roadmaps" / "scenarios" / "accepted"
            target.mkdir(parents=True)
            directives = root / "reviews" / "directives"
            directives.mkdir(parents=True)
            directive = {
                "directive_id": "DIR-000001",
                "directive_type": "publication-approval",
                "status": "approved",
                "submitted_by": "test-human",
                "submitted_at": "2026-08-23T00:00:00Z",
                "publication_targets": ["SCN-PUBLIC-001"],
            }
            (directives / "DIR-000001.json").write_text(json.dumps(directive), encoding="utf-8")
            (target / "scenario.json").write_text(json.dumps(scenario), encoding="utf-8")
            result = collect_scenarios(root, policy, include_commit_metadata=False)
            self.assertEqual("SCN-PUBLIC-001", result[0]["scenario_id"])
            self.assertNotIn("nda_internal_note", result[0])

            scenario["publication"].pop("publication_decision_id")
            (target / "scenario.json").write_text(json.dumps(scenario), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "publication decision"):
                collect_scenarios(root, policy, include_commit_metadata=False)

    def test_published_scenario_requires_matching_human_directive(self):
        policy = json.loads((ROOT / "config" / "publication-policy.json").read_text(encoding="utf-8"))
        scenario = {
            "scenario_id": "SCN-PUBLIC-002",
            "title_ja": "公開候補",
            "title_en": "Publication candidate",
            "status": "published",
            "objective": "要約",
            "objective_en": "Summary",
            "uncertainties": ["未確認条件"],
            "uncertainties_en": ["Unverified condition"],
            "decision_gates": ["人による判断"],
            "decision_gates_en": ["Human decision"],
            "caveat_ja": "公開用注意",
            "caveat_en": "Publication caveat",
            "publication": {
                "information_classification": "public",
                "publication_approved": True,
                "publication_decision_id": "DEC-PUB-002",
                "human_approval_directive_id": "DIR-000002",
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "roadmaps" / "scenarios" / "accepted"
            target.mkdir(parents=True)
            (target / "scenario.json").write_text(json.dumps(scenario), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "human publication Directive"):
                collect_scenarios(root, policy, include_commit_metadata=False)


if __name__ == "__main__":
    unittest.main()
