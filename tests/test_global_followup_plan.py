from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from generate_global_followup_plan import build_plan  # noqa: E402


class GlobalFollowupPlanTests(unittest.TestCase):
    def test_plan_deduplicates_and_prioritizes_worldwide_coverage_gaps(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_id = "RUN-GLOBAL-GAPS"
            monitor_ref = "config/monitors/MON-GLOBAL-TECH-001.json"
            snapshot_ref = f"runs/{run_id}/inputs/{monitor_ref}"
            snapshot = root / snapshot_ref
            snapshot.parent.mkdir(parents=True)
            shutil.copy2(ROOT / monitor_ref, snapshot)
            run_dir = root / "runs" / run_id
            (run_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "run_id": run_id,
                        "monitor_id": "MON-GLOBAL-TECH-001",
                        "task_id": "OFS-005",
                        "status": "completed",
                        "configuration_snapshots": {monitor_ref: snapshot_ref},
                    }
                ),
                encoding="utf-8",
            )
            (run_dir / "coverage.json").write_text(
                json.dumps(
                    {
                        "gaps": {
                            "missing_source_requirements": [
                                "standards-body",
                                "peer-reviewed-research",
                            ],
                            "missing_organization_types": ["standards-body"],
                            "missing_world_regions": [],
                            "missing_technology_categories": [],
                            "missing_maturity_signals": [],
                            "missing_result_signals": [],
                            "missing_languages": [],
                        }
                    }
                ),
                encoding="utf-8",
            )
            brief = root / "reviews" / "briefs" / f"{run_id}.json"
            brief.parent.mkdir(parents=True)
            brief.write_text(json.dumps({"run_id": run_id}), encoding="utf-8")

            plan = build_plan(
                root,
                run_id=run_id,
                generated_at="2026-08-24T06:00:00Z",
            )

            self.assertEqual(2, len(plan["queries"]))
            standards = next(
                query
                for query in plan["queries"]
                if query["source_classes"] == ["standards-body"]
            )
            self.assertEqual(
                [
                    {
                        "dimension": "missing_source_requirements",
                        "value": "standards-body",
                    },
                    {
                        "dimension": "missing_organization_types",
                        "value": "standards-body",
                    },
                ],
                standards["coverage_targets"],
            )
            self.assertEqual(1, standards["search_generation"])
            self.assertEqual("targeted-primary", standards["search_strategy"])


if __name__ == "__main__":
    unittest.main()
