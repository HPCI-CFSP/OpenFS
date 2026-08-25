from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class ScenarioViewTests(unittest.TestCase):
    def test_example_scenarios_render_without_ranking(self):
        with tempfile.TemporaryDirectory() as directory:
            markdown_path = Path(directory) / "scenarios.md"
            json_path = Path(directory) / "scenarios.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "tools" / "generate_scenario_views.py"),
                    "--input",
                    str(ROOT / "evals" / "scenarios" / "candidate-scenarios.json"),
                    "--policy",
                    str(ROOT / "config" / "scenario-policy.json"),
                    "--output-markdown",
                    str(markdown_path),
                    "--output-json",
                    str(json_path),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(0, result.returncode, result.stderr)
            rendered = json.loads(json_path.read_text(encoding="utf-8"))
            policy = json.loads((ROOT / "config" / "scenario-policy.json").read_text(encoding="utf-8"))
            self.assertEqual(4, len(rendered["scenarios"]))
            self.assertFalse(rendered["ranking_enabled"])
            expected_criteria = {item["criterion_id"] for item in policy["evaluation_criteria"]}
            for scenario in rendered["scenarios"]:
                self.assertEqual(expected_criteria, set(scenario["evaluation"]))
                self.assertTrue(scenario["center_impacts"])
                self.assertTrue(scenario["technology_options"])
            markdown = markdown_path.read_text(encoding="utf-8")
            self.assertIn("Ranking: `disabled`", markdown)
            self.assertIn("センター特化・全国ポートフォリオ型", markdown)


if __name__ == "__main__":
    unittest.main()
