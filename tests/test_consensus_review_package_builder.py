from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_consensus_review_package import build_manifest, committed_json  # noqa: E402
from evaluate_consensus_review_package import evaluate  # noqa: E402


class ConsensusReviewPackageBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=ROOT,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        ).stdout.strip()
        cls.manifest = build_manifest(
            ROOT,
            cls.commit,
            "2026-09-06T00:00:00Z",
            "CRP-P0-ROADMAPS-TEST",
        )

    def test_current_builder_covers_every_published_p0_roadmap(self):
        portfolio = committed_json(ROOT, self.commit, "config/roadmap-portfolio.json")
        expected = {
            item["roadmap_id"]
            for item in portfolio["roadmap_families"]
            if item["priority"] == "P0" and item["status"] == "published"
        }
        actual = {
            unit["unit_id"].removeprefix("CRU-")
            for unit in self.manifest["review_units"]
            if unit["kind"] == "roadmap"
        }
        self.assertEqual({item.removeprefix("RM-") for item in expected}, actual)
        self.assertEqual(15, self.manifest["portfolio_summary"]["roadmap_count"])
        self.assertEqual(26, self.manifest["portfolio_summary"]["dependency_count"])

    def test_procurement_and_readiness_evidence_are_reviewable(self):
        artifacts = {item["path"] for item in self.manifest["artifact_manifest"]}
        expected_artifacts = {
            "knowledge/public/procurement-cost-register.json",
            "knowledge/public/planning-evidence-readiness.json",
            "schemas/procurement-cost-register.schema.json",
            "schemas/planning-evidence-readiness.schema.json",
            "tools/check_procurement_costs.py",
        }
        self.assertLessEqual(expected_artifacts, artifacts)

        unit = next(
            item
            for item in self.manifest["review_units"]
            if item["unit_id"] == "CRU-X-PROCUREMENT"
        )
        register = committed_json(
            ROOT, self.commit, "knowledge/public/procurement-cost-register.json"
        )
        readiness = committed_json(
            ROOT, self.commit, "knowledge/public/planning-evidence-readiness.json"
        )
        self.assertLessEqual(
            {item["case_id"] for item in register["cases"]}, set(unit["selectors"])
        )
        self.assertLessEqual(
            {item["dimension_id"] for item in readiness["dimensions"]},
            set(unit["selectors"]),
        )
        procurement_checks = {
            item["selector"]: item
            for item in unit["primary_source_requirements"]
            if item["selector"].startswith("PCS-")
        }
        self.assertEqual(
            {item["source_id"] for item in register["sources"]},
            set(procurement_checks),
        )
        allowed_classes = {
            "vendor-official",
            "standards-body",
            "government-official",
            "research-organization",
            "project-official",
            "academic-primary",
        }
        self.assertTrue(
            all(
                option["source_class"] in allowed_classes
                for requirement in procurement_checks.values()
                for option in requirement["source_options"]
            )
        )

    def test_generated_manifest_matches_the_consensus_schema(self):
        schema = json.loads(
            (ROOT / "schemas/consensus-review-package.schema.json").read_text(
                encoding="utf-8"
            )
        )
        Draft202012Validator(schema).validate(self.manifest)

    def test_generated_manifest_has_no_integrity_errors_before_review(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest_path = Path(directory) / "manifest.json"
            manifest_path.write_text(
                json.dumps(self.manifest, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            result = evaluate(
                ROOT,
                manifest_path,
                evaluated_at="2026-09-06T01:00:00Z",
            )
        self.assertEqual("incomplete", result["status"])
        self.assertEqual([], result["integrity_errors"])
        self.assertEqual(0, result["counts"]["assessments"])


if __name__ == "__main__":
    unittest.main()
