from __future__ import annotations

import json
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_pages_site import (  # noqa: E402
    build,
    collect_consensus_receipts,
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

    def test_page_fragment_navigation_has_unique_existing_targets(self):
        parser = PageStructureParser()
        parser.feed((ROOT / "site" / "index.html").read_text(encoding="utf-8"))
        self.assertEqual(len(parser.ids), len(set(parser.ids)))
        self.assertTrue(parser.fragment_links)
        self.assertEqual([], sorted(set(parser.fragment_links) - set(parser.ids)))

    def test_build_publishes_catalog_but_not_illustrative_scenarios(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            result = build(ROOT, output)
            self.assertEqual(58, len(result["topics"]))
            self.assertEqual(3, len(result["research_summaries"]))
            self.assertEqual([], result["consensus_receipts"])
            self.assertEqual([], result["scenarios"])
            self.assertEqual([], result["reports"])
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
            rendered = (output / "data" / "openfs-public.js").read_text(encoding="utf-8")
            self.assertNotIn("SCN-EXAMPLE", rendered)
            self.assertNotIn("Illustrative archetypes", rendered)
            self.assertIn("SUM-MEMORY-PILOT-003", rendered)
            self.assertIn("https://www.usenix.org/conference/nsdi26", rendered)
            index = (output / "index.html").read_text(encoding="utf-8")
            self.assertIn('href="#technology-landscape"', index)
            self.assertNotIn('href="#domestic"', index)
            app = (output / "app.js").read_text(encoding="utf-8")
            for public_copy in (index, app, rendered):
                self.assertNotIn("調査対象地域", public_copy)
                self.assertNotIn("日本発技術を優先", public_copy)
                self.assertNotIn("Priority coverage for Japan", public_copy)
            self.assertIn('id="topic-dialog"', index)
            self.assertIn("openTopicDetail", app)
            self.assertIn('tr("findingAvailable")', app)
            self.assertIn('tr("sourceSurvey")', app)
            self.assertIn("renderConsensusReceipt", app)
            self.assertIn("consensusProof", app)
            self.assertIn("/commit/${harness.commit_sha}", app)
            self.assertNotIn("summary.summary_ja", app)
            self.assertNotIn("summary.summary_en", app)

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
            result = collect_scenarios(root, policy)
            self.assertEqual("SCN-PUBLIC-001", result[0]["scenario_id"])
            self.assertNotIn("nda_internal_note", result[0])

            scenario["publication"].pop("publication_decision_id")
            (target / "scenario.json").write_text(json.dumps(scenario), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "publication decision"):
                collect_scenarios(root, policy)

    def test_published_scenario_requires_matching_human_directive(self):
        policy = json.loads((ROOT / "config" / "publication-policy.json").read_text(encoding="utf-8"))
        scenario = {
            "scenario_id": "SCN-PUBLIC-002",
            "title_ja": "公開候補",
            "title_en": "Publication candidate",
            "status": "published",
            "objective": "要約",
            "objective_en": "Summary",
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
                collect_scenarios(root, policy)


if __name__ == "__main__":
    unittest.main()
