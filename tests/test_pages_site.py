from __future__ import annotations

import json
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_pages_site import build, collect_scenarios  # noqa: E402


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
            self.assertEqual([], result["scenarios"])
            self.assertEqual([], result["reports"])
            self.assertEqual("public-only", result["publication"]["information_plane"])
            self.assertEqual("Apache-2.0", result["publication"]["license"])
            self.assertTrue(all(topic["title_en"] for topic in result["topics"]))
            self.assertTrue(
                all("research_summary_count" in topic for topic in result["topics"])
            )
            self.assertGreater(
                next(
                    topic["research_summary_count"]
                    for topic in result["topics"]
                    if topic["topic_id"] == "ARCH-03"
                ),
                0,
            )
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
