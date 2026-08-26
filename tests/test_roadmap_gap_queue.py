from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_roadmap_gap_queue import build  # noqa: E402


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class RoadmapGapQueueTests(unittest.TestCase):
    def test_published_queue_assigns_every_current_gap_exactly_once(self):
        queue = load_json(ROOT / "knowledge/public/audits/roadmap-gap-queue.json")
        roadmaps = [
            load_json(path)
            for path in sorted((ROOT / "knowledge/public/roadmaps").glob("*.json"))
        ]
        expected = {
            gap["gap_id"]: (roadmap["roadmap_id"], gap["priority"])
            for roadmap in roadmaps
            for gap in roadmap["coverage_gaps"]
        }
        actual = {
            item["gap_id"]: (item["roadmap_id"], item["priority"])
            for item in queue["assignments"]
        }
        self.assertEqual(expected, actual)
        self.assertEqual(len(expected), queue["summary"]["gap_count"])
        self.assertEqual(16, queue["summary"]["p0"])
        self.assertTrue(
            all(
                item["cadence"] in {"weekly", "continuous-until-quorum"}
                for item in queue["assignments"]
                if item["priority"] == "P0"
            )
        )
        p0_discovery = [
            item
            for item in queue["assignments"]
            if item["priority"] == "P0" and item["workstream"] == "source-discovery"
        ]
        self.assertEqual(15, len(p0_discovery))
        self.assertTrue(
            all(item["query_plan_origin"] == "explicit-override" for item in p0_discovery)
        )
        self.assertEqual(15, queue["summary"]["explicit_query_overrides"])
        self.assertEqual(15, queue["summary"]["p0_explicit_query_overrides"])
        self.assertEqual(0, queue["summary"]["p0_generated_query_fallbacks"])
        p0_items = [item for item in queue["assignments"] if item["priority"] == "P0"]
        self.assertTrue(
            all(item["closure_state"] == "criteria-unverified" for item in p0_items)
        )
        self.assertTrue(
            all(
                item["closure_plan"]["minimum_independent_origin_groups"] >= 2
                and item["closure_plan"]["requires_consensus_gate"] is True
                and item["closure_plan"]["criteria"]
                for item in p0_items
            )
        )
        self.assertTrue(
            all(
                item["closure_plan_origin"] == "explicit-override"
                for item in p0_discovery
            )
        )

    def test_builder_preserves_monitor_readiness_and_consensus_assignment(self):
        result = build(ROOT, "2026-08-26T12:00:00Z")
        by_gap = {item["gap_id"]: item for item in result["assignments"]}
        self.assertEqual("MON-MEMORY-001", by_gap["GAP-MEM001"]["assignment_ref"])
        self.assertEqual("MON-FS-BASELINE-001", by_gap["GAP-BLUE-002"]["assignment_ref"])
        self.assertEqual("CRP-P0-ROADMAPS-V02", by_gap["GAP-BLUE-006"]["assignment_ref"])
        self.assertEqual(
            "consensus-policy", by_gap["GAP-BLUE-006"]["closure_plan_origin"]
        )
        self.assertEqual(
            "awaiting-independent-review",
            by_gap["GAP-BLUE-006"]["execution_state"],
        )
        self.assertGreater(result["summary"]["staged_monitor_disabled"], 0)
        self.assertEqual(0, result["summary"]["ready_for_scheduled_discovery"])


if __name__ == "__main__":
    unittest.main()
