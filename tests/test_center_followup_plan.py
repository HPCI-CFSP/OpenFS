from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from generate_center_followup_plan import build_plan  # noqa: E402


class CenterFollowupPlanTests(unittest.TestCase):
    def test_plan_bounds_and_prioritizes_planning_gaps(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_id = "RUN-CENTER-GAPS"
            run_dir = root / "runs" / run_id
            snapshot = run_dir / "inputs" / "config" / "hpci-center-registry.json"
            snapshot.parent.mkdir(parents=True)
            snapshot.write_text(
                json.dumps(
                    {
                        "centers": [
                            {
                                "center_id": "CENTER-TEST",
                                "name_ja": "試験センター",
                                "official_url": "https://example.jp/service",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (run_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "run_id": run_id,
                        "monitor_id": "MON-HPCI-CENTERS-001",
                        "task_id": "OFS-003",
                        "status": "completed",
                        "configuration_snapshots": {
                            "config/hpci-center-registry.json": str(
                                snapshot.relative_to(root)
                            )
                        },
                    }
                ),
                encoding="utf-8",
            )
            brief = root / "reviews" / "briefs" / f"{run_id}-center-research.json"
            brief.parent.mkdir(parents=True)
            brief.write_text(
                json.dumps(
                    {
                        "centers": [
                            {
                                "center_id": "CENTER-TEST",
                                "missing_or_partial_fields": [
                                    "users",
                                    "power",
                                    "facility",
                                    "refresh_window",
                                    "migration",
                                ],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            plan = build_plan(
                root,
                run_id=run_id,
                maximum_fields_per_query=3,
                generated_at="2026-08-24T06:00:00Z",
            )
            self.assertEqual(1, len(plan["queries"]))
            self.assertEqual(
                ["refresh_window", "power", "facility"],
                plan["queries"][0]["profile_fields"],
            )
            self.assertIn("site:example.jp", plan["queries"][0]["query"])
            self.assertEqual(1, plan["queries"][0]["search_generation"])
            self.assertEqual("center-domain", plan["queries"][0]["search_strategy"])

            predecessor_ref = "reviews/followups/RUN-PREVIOUS-center-gaps.json"
            predecessor_path = root / predecessor_ref
            predecessor_path.parent.mkdir(parents=True, exist_ok=True)
            predecessor_path.write_text(
                json.dumps(
                    {
                        "followup_plan_id": "CFP-000000000001",
                        "queries": [plan["queries"][0]],
                    }
                ),
                encoding="utf-8",
            )
            manifest_path = run_dir / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["followup_plan"] = {"source_ref": predecessor_ref}
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            second = build_plan(
                root,
                run_id=run_id,
                maximum_fields_per_query=3,
                generated_at="2026-08-25T06:00:00Z",
            )
            query = second["queries"][0]
            self.assertEqual(2, query["search_generation"])
            self.assertEqual(
                "institution-domain-and-procurement", query["search_strategy"]
            )
            self.assertIn("調達", query["query"])
            self.assertIn("official-primary", query["source_classes"])
            self.assertRegex(query["previous_query_digest"], r"^[0-9a-f]{64}$")
            self.assertEqual(
                "CFP-000000000001", second["predecessor_plan"]["plan_id"]
            )


if __name__ == "__main__":
    unittest.main()
