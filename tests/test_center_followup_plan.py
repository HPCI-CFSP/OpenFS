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


if __name__ == "__main__":
    unittest.main()
