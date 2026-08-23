from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from prepare_weekly_cycle import build_plan  # noqa: E402
from publish_github_issue import publish  # noqa: E402


class WeeklyCoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def write_json(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_manual_pilot_can_plan_one_disabled_monitor(self):
        self.write_json(
            "config/monitors/MON-TEST-001.json",
            {"monitor_id": "MON-TEST-001", "task_id": "OFS-001", "enabled": False},
        )
        self.write_json(
            "reviews/directives/DIR-000001.json",
            {
                "directive_id": "DIR-000001",
                "status": "approved",
                "scope": ["OFS-001"],
            },
        )
        plan = build_plan(
            self.root,
            week="2026-W35",
            monitor_ids=["MON-TEST-001"],
            pilot=True,
            generated_at="2026-08-24T00:00:00Z",
        )
        self.assertEqual("ready", plan["status"])
        self.assertEqual("RUN-2026W35-TEST-001", plan["monitors"][0]["suggested_run_id"])
        self.assertEqual(["DIR-000001"], plan["monitors"][0]["pending_directive_ids"])
        self.assertNotIn("Candidate statement", plan["issue"]["body"])

    def test_scheduled_cycle_without_enabled_monitors_is_blocked(self):
        self.write_json(
            "config/monitors/MON-TEST-001.json",
            {"monitor_id": "MON-TEST-001", "task_id": "OFS-001", "enabled": False},
        )
        plan = build_plan(
            self.root,
            week="2026-W35",
            generated_at="2026-08-24T00:00:00Z",
        )
        self.assertEqual("blocked", plan["status"])
        self.assertEqual(["no-eligible-monitors"], plan["blockers"])

    def test_issue_publication_is_deduplicated_by_marker(self):
        calls = []

        def request(method, endpoint, body):
            calls.append((method, endpoint, body))
            if endpoint.startswith("/issues?"):
                return [
                    {
                        "number": 7,
                        "html_url": "https://github.com/example/repo/issues/7",
                        "body": "<!-- openfs-weekly-cycle:CYCLE-2026-W35 -->",
                    }
                ]
            raise AssertionError("No create call is expected")

        result = publish(
            {
                "issue": {
                    "title": "Weekly",
                    "body": "<!-- openfs-weekly-cycle:CYCLE-2026-W35 -->",
                    "labels": ["openfs-weekly-cycle"],
                    "deduplication_marker": (
                        "<!-- openfs-weekly-cycle:CYCLE-2026-W35 -->"
                    ),
                }
            },
            request=request,
        )
        self.assertEqual("existing", result["publication_status"])
        self.assertEqual(1, len(calls))


if __name__ == "__main__":
    unittest.main()
