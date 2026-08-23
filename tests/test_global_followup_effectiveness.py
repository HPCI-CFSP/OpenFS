from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from evaluate_global_followup_effectiveness import evaluate  # noqa: E402


class GlobalFollowupEffectivenessTests(unittest.TestCase):
    def test_reports_resolved_and_unresolved_targets(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_id = "RUN-GLOBAL-FOLLOWUP"
            snapshot_ref = (
                f"runs/{run_id}/inputs/reviews/followups/previous.json"
            )
            snapshot = root / snapshot_ref
            snapshot.parent.mkdir(parents=True)
            snapshot.write_text(
                json.dumps(
                    {
                        "followup_plan_id": "GFP-TEST",
                        "queries": [
                            {
                                "query_id": "Q-1",
                                "coverage_targets": [
                                    {
                                        "dimension": "missing_source_requirements",
                                        "value": "standards-body",
                                    },
                                    {
                                        "dimension": "missing_organization_types",
                                        "value": "standards-body",
                                    },
                                ],
                            },
                            {
                                "query_id": "Q-2",
                                "coverage_targets": [
                                    {
                                        "dimension": "missing_world_regions",
                                        "value": "africa",
                                    }
                                ],
                            },
                        ],
                    }
                ),
                encoding="utf-8",
            )
            run_dir = root / "runs" / run_id
            (run_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "followup_plan": {
                            "base_run_id": "RUN-PREVIOUS",
                            "snapshot_ref": snapshot_ref,
                        }
                    }
                ),
                encoding="utf-8",
            )
            (run_dir / "coverage.json").write_text(
                json.dumps(
                    {
                        "gaps": {
                            "missing_source_requirements": [],
                            "missing_organization_types": [],
                            "missing_world_regions": ["africa"],
                        }
                    }
                ),
                encoding="utf-8",
            )

            report = evaluate(
                root,
                run_id=run_id,
                evaluated_at="2026-08-24T08:00:00Z",
            )

            self.assertEqual("partially-effective", report["status"])
            self.assertEqual(1, report["effective_query_count"])
            self.assertEqual(2, report["resolved_target_count"])
            self.assertEqual(1, report["unresolved_target_count"])


if __name__ == "__main__":
    unittest.main()
