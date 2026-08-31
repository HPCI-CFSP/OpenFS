from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_pages_site import (  # noqa: E402
    PUBLIC_BRAND_ASSETS,
    build,
    collect_consensus_packages,
    collect_consensus_receipts,
    collect_roadmaps,
    collect_roadmap_reference_data,
    collect_scenarios,
    collect_topic_summaries,
    copy_brand_assets,
    render_template,
)


class PageStructureParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.fragment_links = []
        self.images = []
        self.links = []
        self.headings = []
        self.heading_level = None

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if values.get("id"):
            self.ids.append(values["id"])
        if values.get("href", "").startswith("#"):
            self.fragment_links.append(values["href"][1:])
        if tag == "a":
            self.links.append(values)
        if tag in {"h1", "h2", "h3"}:
            self.heading_level = tag
            self.headings.append(tag)
        if tag == "img":
            self.images.append({**values, "heading": self.heading_level})

    def handle_endtag(self, tag):
        if tag == self.heading_level:
            self.heading_level = None


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
        for name in ("DIR-900004.json", "DIR-900005.json", "DIR-900013.json", "DIR-900015.json"):
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
        self.assertIn('- "requirements-validation.txt"', workflow)
        self.assertIn("--requirement requirements-validation.txt", workflow)
        self.assertLess(workflow.index("Install pinned contract validators"), workflow.index("Run Pages tests"))
        self.assertLess(workflow.index("Install pinned contract validators"), workflow.index("Build static preview"))
        self.assertIn('- "config/budget-planning.json"', workflow)
        self.assertIn('- "config/catalog-taxonomy.json"', workflow)

    def test_page_fragment_navigation_has_unique_existing_targets(self):
        parser = PageStructureParser()
        parser.feed((ROOT / "site" / "index.html").read_text(encoding="utf-8"))
        self.assertEqual(len(parser.ids), len(set(parser.ids)))
        self.assertTrue(parser.fragment_links)
        self.assertEqual([], sorted(set(parser.fragment_links) - set(parser.ids)))

    def test_readmes_share_the_standard_logo_and_pages_link(self):
        logo_headers = []
        for filename in ("README.md", "README.ja.md"):
            with self.subTest(filename=filename):
                text = (ROOT / filename).read_text(encoding="utf-8")
                header = text.split("</h1>", 1)[0] + "</h1>"
                logo_headers.append(header)
                parser = PageStructureParser()
                parser.feed(header)
                self.assertEqual(["h1"], parser.headings)
                self.assertEqual(1, len(parser.images))
                self.assertEqual(
                    {"src": "assets/branding/openfs-logo.svg", "alt": "OpenFS",
                     "width": "285", "height": "130", "heading": "h1"},
                    parser.images[0],
                )
                self.assertEqual(
                    [{"href": "https://hpci-cfsp.github.io/OpenFS/"}], parser.links
                )
                self.assertNotIn("# OpenFS", text)
        self.assertEqual(*logo_headers)

    def test_brand_assets_are_self_contained_outlined_vectors(self):
        namespace = {"s": "http://www.w3.org/2000/svg"}
        allowed = {"svg", "title", "desc", "defs", "linearGradient", "stop", "mask", "path", "polygon", "g"}
        allowed_attributes = {"id", "viewBox", "width", "height", "role", "aria-labelledby",
                              "gradientUnits", "x1", "y1", "x2", "y2", "offset", "stop-color",
                              "maskUnits", "x", "y", "style", "d", "fill", "points",
                              "data-corner", "transform", "mask", "data-loop"}
        definitions = []
        faces = []
        for filename in PUBLIC_BRAND_ASSETS:
            with self.subTest(filename=filename):
                root = ET.parse(ROOT / "assets" / "branding" / filename).getroot()
                identifiers = [el.get("id") for el in root.iter() if el.get("id")]
                self.assertEqual(len(identifiers), len(set(identifiers)))
                self.assertEqual("OpenFS", root.find("s:title", namespace).text)
                self.assertEqual(11, len(root.findall("s:defs/s:linearGradient", namespace)))
                self.assertEqual(9, len(root.findall("s:defs/s:mask/s:polygon", namespace)))
                for element in root.iter():
                    self.assertIn(element.tag.split("}")[-1], allowed)
                    self.assertTrue(set(element.attrib) <= allowed_attributes)
                    for name, value in element.attrib.items():
                        if name == "style":
                            self.assertEqual("mask-type:luminance", value)
                        if "url(" in value:
                            self.assertTrue(value.startswith("url(#") and value.endswith(")"))
                            self.assertIn(value[5:-1], identifiers)
                wordmark = root.find("s:path[@id='wordmark']", namespace)
                if filename == "openfs-symbol.svg":
                    self.assertIsNone(wordmark)
                else:
                    self.assertEqual("#767676", wordmark.get("fill"))
                    self.assertGreater(len(wordmark.get("d")), 1000)
                definitions.append(ET.tostring(root.find("s:defs", namespace)))
                faces.append([
                    ET.tostring(group)
                    for group in root.find("s:g[@id='symbol']", namespace)
                ])
        self.assertTrue(all(item == definitions[0] for item in definitions))
        self.assertTrue(all(item == faces[0] for item in faces))

    def test_brand_asset_copy_uses_an_allowlist(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "input"
            source = root / "assets" / "branding"
            source.mkdir(parents=True)
            for filename in PUBLIC_BRAND_ASSETS:
                shutil.copy2(ROOT / "assets" / "branding" / filename, source / filename)
            for filename in ("logo-concept.md", "draft.svg", "comparison.html", "assets.zip"):
                (source / filename).write_text("not for publication", encoding="utf-8")
            output = Path(directory) / "output"
            copy_brand_assets(root, output)
            self.assertEqual(
                set(PUBLIC_BRAND_ASSETS),
                {path.name for path in (output / "assets" / "branding").iterdir()},
            )
            for filename in PUBLIC_BRAND_ASSETS:
                self.assertEqual(
                    (source / filename).read_bytes(),
                    (output / "assets" / "branding" / filename).read_bytes(),
                )

    def test_missing_brand_asset_fails_the_build_step(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "input"
            source = root / "assets" / "branding"
            source.mkdir(parents=True)
            for filename in PUBLIC_BRAND_ASSETS[:-1]:
                shutil.copy2(ROOT / "assets" / "branding" / filename, source / filename)
            with self.assertRaises(FileNotFoundError):
                copy_brand_assets(root, Path(directory) / "output")

    def test_brand_asset_changes_trigger_pages_and_preview(self):
        for name in ("pages.yml", "pages-preview.yml"):
            workflow = (ROOT / ".github" / "workflows" / name).read_text(encoding="utf-8")
            self.assertIn('      - "assets/branding/**"', workflow)

    def test_home_branding_does_not_replace_controls_or_publish_concept(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            data = build(ROOT, output)
            html = (output / "index.html").read_text(encoding="utf-8")
            parser = PageStructureParser()
            parser.feed(html)
            logo = next(image for image in parser.images if image.get("class") == "brand-logo")
            self.assertEqual("h1", logo["heading"])
            self.assertEqual("OpenFS", logo["alt"])
            self.assertEqual(("344", "128"), (logo["width"], logo["height"]))
            url = urlsplit(logo["src"])
            self.assertEqual("assets/branding/openfs-logo-compact.svg", url.path)
            self.assertEqual(f"v={data['site']['commit_sha']}", url.query)
            self.assertEqual(
                (ROOT / url.path).read_bytes(), (output / url.path).read_bytes()
            )
            self.assertEqual(1, parser.headings.count("h1"))
            self.assertIn('data-i18n="tagline"', html)
            self.assertIn('data-language="ja"', html)
            self.assertIn('data-language="en"', html)
            self.assertIn('id="site-updated"', html)
            self.assertIn('data-i18n="aboutLead"', html)
            self.assertTrue(any(link.get("class") == "brand-link" and link["href"] == "./" for link in parser.links))
            self.assertFalse((output / "docs").exists())
            self.assertEqual(set(PUBLIC_BRAND_ASSETS), {p.name for p in (output / "assets" / "branding").iterdir()})
            for page in output.rglob("*.html"):
                contents = page.read_text(encoding="utf-8")
                self.assertNotIn("logo-concept", contents)
                self.assertNotIn("調べ、確かめ、未来を描き続ける。", contents)
            for stylesheet in (ROOT / "site" / "styles.css", output / "styles.css"):
                css = stylesheet.read_text(encoding="utf-8")
                self.assertIn(".identity.identity-branded", css)
                self.assertIn("width: 150.5px; height: 56px;", css)
                self.assertIn("width: 129px; height: 48px;", css)

    def test_every_page_uses_one_shared_logo_with_valid_relative_paths(self):
        for template in (ROOT / "site").glob("*.html"):
            content = template.read_text(encoding="utf-8")
            with self.subTest(template=template.name):
                self.assertEqual(1, content.count("{{SITE_IDENTITY}}"))
                self.assertNotIn("openfs-logo", content)
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            data = build(ROOT, output)
            pages = list(output.rglob("*.html"))
            self.assertGreaterEqual(len(pages), 19)
            for page in pages:
                with self.subTest(page=page.relative_to(output)):
                    content = page.read_text(encoding="utf-8")
                    parser = PageStructureParser()
                    parser.feed(content)
                    logos = [item for item in parser.images if item.get("class") == "brand-logo"]
                    links = [item for item in parser.links if item.get("class") == "brand-link"]
                    self.assertEqual(1, len(logos))
                    self.assertEqual(1, len(links))
                    self.assertEqual(1, parser.headings.count("h1"))
                    self.assertEqual("h1", logos[0]["heading"])
                    self.assertEqual("OpenFS", logos[0]["alt"])
                    self.assertEqual(("344", "128"), (logos[0]["width"], logos[0]["height"]))
                    url = urlsplit(logos[0]["src"])
                    asset = (page.parent / url.path).resolve()
                    self.assertEqual((output / "assets/branding/openfs-logo-compact.svg").resolve(), asset)
                    self.assertTrue(asset.is_file())
                    self.assertEqual(f"v={data['site']['commit_sha']}", url.query)
                    self.assertEqual(output.resolve(), (page.parent / links[0]["href"]).resolve())
                    self.assertIn('data-i18n="tagline"', content)
                    self.assertIn('data-feedback-copy="tagline"', content)
                    self.assertIn('data-language="ja"', content)
                    self.assertIn('data-language="en"', content)
                    self.assertNotIn("{{", content)
            self.assertFalse((output / "partials").exists())

    def test_missing_shared_identity_fails_template_generation(self):
        with tempfile.TemporaryDirectory() as directory:
            template = Path(directory) / "index.html"
            template.write_text("{{SITE_IDENTITY}}", encoding="utf-8")
            with self.assertRaises(FileNotFoundError):
                render_template(template, {"ASSET_VERSION": "test"})

    def test_logo_concept_has_both_languages_and_local_asset_links(self):
        document = ROOT / "docs" / "branding" / "logo-concept.md"
        text = document.read_text(encoding="utf-8")
        self.assertIn("## 日本語", text)
        self.assertIn("## English", text)
        self.assertIn("### 短い紹介文", text)
        self.assertIn("### Short Description", text)
        for name in PUBLIC_BRAND_ASSETS:
            self.assertIn(f"../../assets/branding/{name}", text)
            self.assertTrue((document.parent / "../../assets/branding" / name).is_file())

    def test_roadmap_reference_data_and_detail_ui_are_connected(self):
        policy = self.publication_policy()
        roadmaps = collect_roadmaps(ROOT, policy, False)
        reference_data = collect_roadmap_reference_data(
            ROOT, policy, roadmaps, False
        )
        self.assertGreaterEqual(len(reference_data["terms"]), 57)
        self.assertGreaterEqual(len(reference_data["comparison_sets"]), 10)
        detail = (ROOT / "site" / "roadmap-detail.html").read_text(encoding="utf-8")
        for element_id in (
            'id="roadmap-comparisons"',
            'id="roadmap-glossary"',
            'id="roadmap-term-dialog"',
            'id="hpci-system-inventory-section"',
            'id="hpci-inventory-table"',
            'id="application-performance-section"',
            'id="application-code-availability"',
            'id="application-performance-table"',
        ):
            self.assertIn(element_id, detail)
        script = (ROOT / "site" / "roadmaps.js").read_text(encoding="utf-8")
        self.assertIn("function renderHPCIInventory", script)
        self.assertIn("function renderApplicationPerformance", script)
        self.assertIn("application.code_availability.source_ids", script)
        self.assertIn("publicSourceConfirmed", script)
        self.assertIn('sourceLinks.className = "comparison-row-sources"', script)
        self.assertIn("row.source_refs.forEach", script)
        performance_matrix = 'table.className = "supplement-table performance-matrix"'
        performance_rows = script[script.index(performance_matrix) :]
        performance_rows = performance_rows[
            performance_rows.index("performance.applications.forEach((application)") :
        ]
        self.assertLess(
            performance_rows.index("row.append(app);"),
            performance_rows.index("performance.standard_fugaku_node_scales.forEach"),
        )
        self.assertNotIn("row.append(app, cell)", performance_rows)

        planning = (ROOT / "site" / "planning.js").read_text(encoding="utf-8")
        self.assertIn("source.summary.fetch_count", planning)
        self.assertIn("source.summary.unique_url_status_counts.reachable", planning)

        search = (ROOT / "site" / "search.js").read_text(encoding="utf-8")
        self.assertIn("data.application_performance_forecasts.applications", search)
        self.assertIn("data.hpci_system_inventory.systems", search)

    def test_timeline_uses_evidence_window_spans_without_q_unknown_column(self):
        script = (ROOT / "site" / "roadmaps.js").read_text(encoding="utf-8")
        self.assertIn("function milestoneGridRange", script)
        self.assertIn('milestone.half === "H1" ? [1, 3] : [3, 5]', script)
        self.assertIn('return [1, 5]', script)
        self.assertIn('Array(years.length).fill("roadmap-year-column")', script)
        self.assertIn("function generationBandGridRange", script)
        self.assertIn("function generationBandPeriodLabel", script)
        self.assertIn("function renderRoadmapGenerationBandDialog", script)
        self.assertGreaterEqual(script.count('localized(lane, "owner")'), 3)
        self.assertIn("roadmap.horizon.end_year", script)
        self.assertNotIn("const years = [2026, 2027, 2028, 2029, 2030, 2031, 2032]", script)
        self.assertNotIn('fill("roadmap-quarter-column")', script)

    def test_build_publishes_catalog_and_approved_scenarios_only(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            result = build(ROOT, output)
            self.assertEqual(40, len(result["topics"]))
            self.assertEqual(64, result["baseline"]["historical_topic_count"])
            self.assertTrue(all(topic["status"] != "retired" for topic in result["topics"]))
            self.assertEqual(6, len(result["catalog_taxonomy"]["categories"]))
            self.assertTrue(all(topic.get("catalog_category_id") for topic in result["topics"]))
            self.assertTrue(all(roadmap.get("catalog_category_id") for roadmap in result["roadmaps"]))
            self.assertEqual(3, len(result["research_summaries"]))
            decision_support = result["topic_decision_support"]
            partial_topic_ids = {
                topic["topic_id"]
                for topic in json.loads(
                    (ROOT / "config/research-baseline.json").read_text(encoding="utf-8")
                )["topics"]
                if topic["status"] == "partial"
            }
            self.assertEqual(
                partial_topic_ids,
                {profile["topic_id"] for profile in decision_support["topic_profiles"]},
            )
            self.assertEqual(6, len(decision_support["platform_matrix"]["platforms"]))
            self.assertEqual(6, len(decision_support["numerical_method_matrix"]["methods"]))
            self.assertNotIn("publication", decision_support)
            arch02 = next(
                profile
                for profile in decision_support["topic_profiles"]
                if profile["topic_id"] == "ARCH-12"
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
            self.assertNotIn("review_cadence", topics_by_id["ARCH-01"])
            self.assertNotIn("catalog_origin", topics_by_id["ARCH-01"])
            self.assertEqual(
                "independent-review-pending",
                topics_by_id["ARCH-01"]["verification_status"],
            )
            self.assertGreater(topics_by_id["ARCH-01"]["coverage_gap_count"], 0)
            self.assertEqual([], result["consensus_receipts"])
            self.assertEqual(2, len(result["consensus_packages"]))
            self.assertEqual(
                {"CRP-P0-ROADMAPS-V02", "CRP-P0-ROADMAPS-V03"},
                {package["package_id"] for package in result["consensus_packages"]},
            )
            for package in result["consensus_packages"]:
                self.assertEqual("incomplete", package["gate"]["status"])
                self.assertEqual([], package["eligible_reviewers"])
                self.assertGreaterEqual(package["artifact_count"], 20)
                self.assertEqual(40, len(package["base_commit"]))
                self.assertEqual(64, len(package["manifest_sha256"]))
            self.assertGreaterEqual(
                len(result["roadmap_reference_data"]["terms"]), 57
            )
            self.assertGreaterEqual(
                len(result["roadmap_reference_data"]["comparison_sets"]), 10
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
            open_p0_count = sum(
                gap["priority"] == "P0" and gap["status"] == "open"
                for path in (ROOT / "knowledge/public/roadmaps").glob("*.json")
                for gap in json.loads(path.read_text(encoding="utf-8"))["coverage_gaps"]
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
                    and scenario["plan_version"] == "0.5"
                    and [option["tier"] for option in scenario["budget_options"]]
                    == ["jpy-10", "jpy-30", "jpy-100", "jpy-300", "jpy-1000"]
                    and len(scenario["implementation_path"]["phases"]) == 12
                    and {note["scope"] for note in scenario["context_notes"]}
                    == {"reusable", "hpci-specific"}
                    and len(scenario["decision_blocking_gap_refs"]) == open_p0_count
                    and len(scenario["decision_evidence_contracts"]) == 6
                    for scenario in result["scenarios"]
                )
            )
            planning_js = (ROOT / "site" / "planning.js").read_text(
                encoding="utf-8"
            )
            self.assertIn('`${tr("hpciSpecific")} · `', planning_js)
            scenario_html = (
                output / result["scenarios"][0]["path"] / "index.html"
            ).read_text(encoding="utf-8")
            self.assertIn('id="scenario-blocking-gaps"', scenario_html)
            self.assertIn('id="scenario-evidence-contracts"', scenario_html)
            self.assertIn('id="scenario-detail-timeline"', scenario_html)
            self.assertIn('id="scenario-context-notes"', scenario_html)
            self.assertIn('id="scenario-budget-options"', scenario_html)
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
            unchecked = {r["url"] for r in assurance["source_audit"]["results"]
                         if r.get("error_kind") == "not-audited"}
            self.assertLessEqual(
                assurance["source_audit"]["summary"]["unique_url_count"] - len(unchecked),
                assurance["source_audit"]["summary"]["fetch_count"],
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
            expected_gap_count = sum(
                len(json.loads(path.read_text(encoding="utf-8"))["coverage_gaps"])
                for path in (ROOT / "knowledge/public/roadmaps").glob("*.json")
            )
            self.assertEqual(
                expected_gap_count, assurance["gap_queue"]["summary"]["gap_count"]
            )
            self.assertEqual(open_p0_count, assurance["gap_queue"]["summary"]["p0"])
            self.assertEqual(
                open_p0_count,
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
            dependency_register = json.loads(
                (ROOT / "knowledge/public/dependencies/p0-roadmap-dependencies.json")
                .read_text(encoding="utf-8")
            )
            self.assertEqual(
                dependency_register["dependencies"],
                assurance["dependency_register"]["dependencies"],
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
            baseline = json.loads((ROOT / "config/research-baseline.json").read_text(encoding="utf-8"))
            self.assertEqual(baseline["derived_at"], result["catalog_as_of"])
            self.assertEqual(40, len(result["site"]["commit_sha"]))
            self.assertTrue(result["site"]["commit_url"].endswith(result["site"]["commit_sha"]))
            self.assertIn("T", result["site"]["updated_at"])
            roadmap_portfolio = json.loads(
                (ROOT / "config/roadmap-portfolio.json").read_text(encoding="utf-8")
            )
            self.assertEqual(
                {
                    roadmap["roadmap_id"]
                    for roadmap in roadmap_portfolio["roadmap_families"]
                    if roadmap["status"] == "published"
                },
                {roadmap["roadmap_id"] for roadmap in result["roadmaps"]},
            )
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
            self.assertEqual(
                len(result["topics"]),
                len({topic["catalog_code"] for topic in result["topics"]}),
            )
            self.assertTrue(all(topic["related_roadmaps"] for topic in result["topics"]))
            self.assertTrue(
                all(roadmap["related_topics"] for roadmap in result["roadmap_artifacts"])
            )
            published_roadmap_ids = {
                roadmap["roadmap_id"] for roadmap in result["roadmap_artifacts"]
            }
            for topic in result["topics"]:
                for roadmap in topic["related_roadmaps"]:
                    if roadmap["status"] == "published":
                        self.assertIn(roadmap["roadmap_id"], published_roadmap_ids)
                        self.assertTrue(roadmap["path"])
                    else:
                        self.assertNotEqual("published", roadmap["status"])
                        self.assertIsNone(roadmap["path"])
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
            self.assertTrue(f'"catalog_as_of":"{baseline["derived_at"]}"' in rendered)
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
            self.assertIn("<title>ロードマップ一覧 | OpenFS</title>", roadmap_index)
            self.assertIn("<title>根拠情報の監査 | OpenFS</title>", evidence_index)
            self.assertIn('id="source-class-summary"', evidence_index)
            planning_app = (output / "planning.js").read_text(encoding="utf-8")
            self.assertIn("sourceClassOrder", planning_app)
            self.assertIn('"roadmap-evidence": "evidenceTitle"', planning_app)
            self.assertIn('"scenario-index": "scenarioIndexTitle"', planning_app)
            self.assertIn('"consensus-index": "consensusIndexTitle"', planning_app)
            self.assertIn('"roadmap-index": "libraryTitle"', roadmap_app)
            self.assertIn('"roadmap-compare": "compareTitle"', roadmap_app)
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

    def test_search_is_the_rightmost_primary_navigation_item(self):
        for path in sorted((ROOT / "site").glob("*.html")):
            text = path.read_text(encoding="utf-8")
            if 'class="tabs"' not in text:
                continue
            first_tabs = text.split('class="tabs"', 1)[1].split("</nav>", 1)[0]
            with self.subTest(path=path.name):
                self.assertGreater(
                    first_tabs.rfind('data-i18n="navSearch"'),
                    first_tabs.rfind('data-i18n="navReports"'),
                )

    def test_public_planning_copy_uses_general_name_and_clear_update_wording(self):
        paths = [
            ROOT / "site" / "index.html",
            ROOT / "site" / "app.js",
            ROOT / "site" / "planning.js",
            ROOT / "site" / "scenarios-index.html",
            ROOT / "site" / "scenario-detail.html",
            ROOT / "site" / "roadmap-evidence.html",
        ]
        combined = "\n".join(path.read_text(encoding="utf-8") for path in paths)
        self.assertIn("システム整備計画案", combined)
        self.assertIn("情報の更新日と確認状況", combined)
        self.assertNotIn("HPCIシステム整備計画案", combined)
        self.assertNotIn("整備シナリオ", combined)
        self.assertNotIn("情報の鮮度", combined)
        self.assertIn("let activeRoadmapMilestoneId = null;", combined)

    def test_consensus_index_uses_each_package_version(self):
        planning = (ROOT / "site" / "planning.js").read_text(encoding="utf-8")
        self.assertIn('item.package_id.split("-").at(-1)', planning)
        self.assertNotIn("P0 roadmaps · v0.2", planning)

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
            "context_notes": [{"note_ja": "一般条件", "note_en": "Reusable condition"}],
            "implementation_path": {"timeline_granularity": "quarter", "phases": []},
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
            "context_notes": [{"note_ja": "一般条件", "note_en": "Reusable condition"}],
            "implementation_path": {"timeline_granularity": "quarter", "phases": []},
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

    def test_build_publishes_cross_site_search_and_deep_links(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "site"
            build(ROOT, output)
            search_page = (output / "search" / "index.html").read_text(encoding="utf-8")
            search_script = (output / "search.js").read_text(encoding="utf-8")
            home = (output / "index.html").read_text(encoding="utf-8")
            self.assertIn('id="global-search-input"', search_page)
            self.assertIn('data-i18n-aria-label="languageControl"', search_page)
            self.assertIn('data-i18n-aria-label="siteNavigation"', search_page)
            self.assertIn('data-i18n-aria-label="breadcrumbs"', search_page)
            self.assertIn('href="search/"', home)
            for item_type in ("topic", "roadmap", "track", "term", "comparison", "scenario", "source"):
                self.assertIn(f'type: "{item_type}"', search_script)
            self.assertIn("topic_decision_support?.topic_profiles", search_script)
            self.assertIn('"independent-review-pending": "independentReviewPending"', search_script)
            self.assertIn('sourceVendor: "ベンダー公式情報"', search_script)
            self.assertIn('siteNavigation: "Site navigation"', search_script)
            self.assertIn('element.setAttribute("aria-label"', search_script)
            self.assertIn('?topic=', search_script)
            self.assertIn('?track=', search_script)
            self.assertIn('?term=', search_script)
            self.assertIn('new URLSearchParams(window.location.search).get("topic")', (output / "app.js").read_text(encoding="utf-8"))
            roadmap_script = (output / "roadmaps.js").read_text(encoding="utf-8")
            self.assertIn('params.get("track")', roadmap_script)
            self.assertIn('params.get("term")', roadmap_script)


if __name__ == "__main__":
    unittest.main()
