from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "reviews" / "consensus-packages" / "CRP-P0-ROADMAPS-V02"
sys.path.insert(0, str(ROOT / "tools"))

from evaluate_consensus_review_package import evaluate  # noqa: E402


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class ConsensusReviewPackageTests(unittest.TestCase):
    def setUp(self):
        self.manifest_path = PACKAGE / "manifest.json"
        self.assertTrue(self.manifest_path.exists(), "commit-pinned package must be generated")
        self.manifest = load_json(self.manifest_path)

    def test_package_covers_six_roadmaps_and_shared_review_units(self):
        units = self.manifest["review_units"]
        self.assertEqual(10, len(units))
        self.assertEqual(6, sum(unit["kind"] == "roadmap" for unit in units))
        self.assertEqual(
            {"cross-roadmap", "coverage-gap", "scenario", "publication-assurance"},
            {unit["kind"] for unit in units if unit["kind"] != "roadmap"},
        )
        self.assertTrue(all(len(unit["required_checks"]) >= 4 for unit in units))
        self.assertTrue(all(unit["falsification_prompts_ja"] for unit in units))
        summary = self.manifest["portfolio_summary"]
        self.assertEqual(6, summary["roadmap_count"])
        self.assertGreaterEqual(summary["milestone_count"], 130)
        self.assertGreaterEqual(summary["source_count"], 91)
        self.assertEqual(30, summary["coverage_gap_count"])
        self.assertEqual(14, summary["dependency_count"])
        self.assertEqual(3, summary["scenario_count"])

    def test_every_artifact_digest_matches_the_pinned_git_object(self):
        for artifact in self.manifest["artifact_manifest"]:
            result = subprocess.run(
                ["git", "show", f"{self.manifest['base_commit']}:{artifact['path']}"],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(
                artifact["sha256"],
                hashlib.sha256(result.stdout).hexdigest(),
                artifact["path"],
            )

    def test_empty_review_set_is_honestly_incomplete(self):
        result = evaluate(ROOT, self.manifest_path)
        self.assertEqual("incomplete", result["status"])
        self.assertEqual([], result["integrity_errors"])
        self.assertEqual(0, result["counts"]["assessments"])
        self.assertIn("minimum_assessments", result["unmet_requirements"])
        self.assertIn("falsification_review", result["unmet_requirements"])

    def test_author_group_is_explicitly_disallowed(self):
        independence = self.manifest["independence_requirements"]
        self.assertIn(independence["author_group"], independence["disallowed_as_independent"])
        self.assertTrue(self.manifest["consensus_policy"]["require_human_decision"])


if __name__ == "__main__":
    unittest.main()
