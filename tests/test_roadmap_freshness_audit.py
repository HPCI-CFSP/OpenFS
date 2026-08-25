from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_roadmap_freshness_audit import build  # noqa: E402


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class RoadmapFreshnessAuditTests(unittest.TestCase):
    def test_published_audit_matches_the_current_portfolio(self):
        audit = load_json(ROOT / "knowledge/public/audits/roadmap-freshness-audit.json")
        roadmaps = [load_json(path) for path in sorted((ROOT / "knowledge/public/roadmaps").glob("*.json"))]
        self.assertEqual(len(roadmaps), audit["summary"]["roadmap_count"])
        self.assertEqual(
            sum(len(lane["milestones"]) for roadmap in roadmaps for lane in roadmap["lanes"]),
            audit["summary"]["milestone_count"],
        )
        self.assertEqual(
            sum(len(roadmap["sources"]) for roadmap in roadmaps),
            audit["summary"]["source_count"],
        )
        self.assertEqual(0, audit["summary"]["future_observed_conflicts"])
        self.assertEqual(1, audit["summary"]["retrospective_timing_checks"])
        self.assertEqual(
            len(audit["attention_items"]),
            len({item["attention_id"] for item in audit["attention_items"]}),
        )

    def test_timing_conflicts_and_passed_targets_are_queued_without_inference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "knowledge/public/roadmaps").mkdir(parents=True)
            (root / "knowledge/public/audits").mkdir(parents=True)
            roadmap = {
                "roadmap_id": "RM-HW-TEST",
                "as_of": "2026-08-26",
                "sources": [
                    {
                        "source_id": "SRC-TEST001",
                        "url": "https://example.com/source",
                        "source_class": "vendor-official",
                        "published_at": "2026-01-01",
                    }
                ],
                "lanes": [
                    {
                        "milestones": [
                            {
                                "milestone_id": "MS-TEST-TARGET",
                                "year": 2026,
                                "quarter": "Q2",
                                "timing_precision": "quarter",
                                "timing_basis": "vendor-target",
                                "comparison_priority": "key",
                                "source_ids": ["SRC-TEST001"],
                            },
                            {
                                "milestone_id": "MS-TEST-FUTURE",
                                "year": 2026,
                                "quarter": "Q4",
                                "timing_precision": "quarter",
                                "timing_basis": "observed",
                                "comparison_priority": "key",
                                "source_ids": ["SRC-TEST001"],
                            },
                            {
                                "milestone_id": "MS-TEST-RETROSPECTIVE",
                                "year": 2025,
                                "quarter": "Q4",
                                "timing_precision": "quarter",
                                "timing_basis": "observed",
                                "comparison_priority": "key",
                                "source_ids": ["SRC-TEST001"],
                            },
                        ]
                    }
                ],
            }
            (root / "knowledge/public/roadmaps/test.json").write_text(json.dumps(roadmap), encoding="utf-8")
            source_audit = {
                "results": [
                    {"roadmap_id": "RM-HW-TEST", "source_id": "SRC-TEST001", "status": "reachable"}
                ]
            }
            (root / "knowledge/public/audits/roadmap-source-audit.json").write_text(json.dumps(source_audit), encoding="utf-8")
            result = build(root, "2026-08-26T00:00:00Z")
            by_reason = {item["reason"]: item for item in result["attention_items"]}
            self.assertEqual("high", by_reason["target-date-passed"]["severity"])
            self.assertEqual("critical", by_reason["future-observed-conflict"]["severity"])
            self.assertEqual("low", by_reason["retrospective-source-timing-check"]["severity"])
            self.assertEqual(1, result["summary"]["past_target_rechecks"])
            self.assertEqual(1, result["summary"]["future_observed_conflicts"])
            self.assertEqual(1, result["summary"]["retrospective_timing_checks"])


if __name__ == "__main__":
    unittest.main()
