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
                "directive_type": "research-instruction",
                "status": "approved",
                "submitted_at": "2026-08-23T00:00:00Z",
                "application_mode": "once",
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

    def test_issue_surfaces_sanitized_operational_readiness(self):
        self.write_json(
            "config/monitors/MON-TEST-001.json",
            {"monitor_id": "MON-TEST-001", "task_id": "OFS-001", "enabled": False},
        )
        readiness = {
            "status": "blocked",
            "blockers": ["production_components_present", "owner_controls_verified"],
            "owner_actions": [
                {
                    "action_id": "implement-provider-worker",
                    "summary": "Implement the reviewed provider Worker.",
                    "refs": ["tools/worker.py"],
                }
            ],
            "checks": {
                "production_components_present": False,
                "owner_controls_verified": False,
            },
            "monitors": {"enabled_count": 0, "ready_enabled_count": 0},
        }
        plan = build_plan(
            self.root,
            week="2026-W35",
            monitor_ids=["MON-TEST-001"],
            pilot=True,
            generated_at="2026-08-24T00:00:00Z",
            operational_readiness=readiness,
            operational_readiness_ref="_automation/operational-readiness.json",
        )
        self.assertEqual("ready", plan["status"])
        self.assertEqual("blocked", plan["operational_readiness"]["status"])
        self.assertIn("production_components_present", plan["issue"]["body"])
        self.assertIn("implement-provider-worker", plan["issue"]["body"])
        self.assertIn("Implement the reviewed provider Worker.", plan["issue"]["body"])
        self.assertNotIn("secret", plan["issue"]["body"].lower())

    def test_weekly_review_is_variable_gated_and_has_no_research_secret(self):
        workflow = (ROOT / ".github" / "workflows" / "weekly-review.yml").read_text(
            encoding="utf-8"
        )
        self.assertIn("OPENFS_REVIEW_ENABLED", workflow)
        self.assertIn("issues: write", workflow)
        self.assertNotIn("contents: write", workflow)
        self.assertNotIn("OPENAI_API_KEY", workflow)
        self.assertNotIn("ANTHROPIC_API_KEY", workflow)
        self.assertIn("7 days ago", workflow)

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
                        "title": "Weekly",
                        "body": "<!-- openfs-weekly-cycle:CYCLE-2026-W35 -->",
                        "labels": [{"name": "openfs-weekly-cycle"}],
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

    def test_existing_issue_is_updated_when_group_members_change(self):
        calls = []

        def request(method, endpoint, body):
            calls.append((method, endpoint, body))
            if endpoint.startswith("/issues?"):
                return [
                    {
                        "number": 7,
                        "html_url": "https://github.com/example/repo/issues/7",
                        "title": "Old title",
                        "body": "<!-- openfs-exception-group:EXCGRP-001 -->\nOld",
                        "labels": [{"name": "openfs-exception"}],
                    }
                ]
            if method == "PATCH" and endpoint == "/issues/7":
                self.assertEqual("New body", body["body"].splitlines()[-1])
                return {
                    "number": 7,
                    "html_url": "https://github.com/example/repo/issues/7",
                }
            raise AssertionError(f"Unexpected request: {method} {endpoint}")

        result = publish(
            {
                "title": "Current grouped exception",
                "body": "<!-- openfs-exception-group:EXCGRP-001 -->\nNew body",
                "labels": ["openfs-exception"],
                "deduplication_marker": (
                    "<!-- openfs-exception-group:EXCGRP-001 -->"
                ),
            },
            request=request,
        )

        self.assertEqual("updated", result["publication_status"])
        self.assertEqual(2, len(calls))

    def test_marker_without_managed_label_cannot_capture_publication(self):
        calls = []

        def request(method, endpoint, body):
            calls.append((method, endpoint, body))
            if endpoint.startswith("/issues?"):
                return [
                    {
                        "number": 3,
                        "html_url": "https://github.com/example/repo/issues/3",
                        "title": "Unmanaged",
                        "body": "<!-- openfs-weekly-cycle:CYCLE-2026-W35 -->",
                        "labels": [],
                    }
                ]
            if endpoint.startswith("/labels?"):
                return [{"name": "openfs-weekly-cycle"}]
            if method == "POST" and endpoint == "/issues":
                return {
                    "number": 8,
                    "html_url": "https://github.com/example/repo/issues/8",
                }
            raise AssertionError(f"Unexpected request: {method} {endpoint}")

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

        self.assertEqual("created", result["publication_status"])
        self.assertEqual(3, len(calls))

    def test_github_actions_bot_issue_is_managed_even_if_legacy_label_is_missing(self):
        calls = []
        body = "<!-- openfs-weekly-cycle:CYCLE-2026-W35 -->"

        def request(method, endpoint, request_body):
            calls.append((method, endpoint, request_body))
            return [
                {
                    "number": 7,
                    "html_url": "https://github.com/example/repo/issues/7",
                    "title": "Weekly",
                    "body": body,
                    "labels": [],
                    "user": {"login": "github-actions[bot]", "type": "Bot"},
                }
            ]

        result = publish(
            {
                "issue": {
                    "title": "Weekly",
                    "body": body,
                    "labels": ["openfs-weekly-cycle"],
                    "deduplication_marker": body,
                }
            },
            request=request,
        )

        self.assertEqual("existing", result["publication_status"])
        self.assertEqual(1, len(calls))

    def test_publication_fails_closed_when_required_label_is_missing(self):
        calls = []

        def request(method, endpoint, body):
            calls.append((method, endpoint, body))
            if endpoint.startswith("/issues?") or endpoint.startswith("/labels?"):
                return []
            raise AssertionError("Issue must not be created without managed labels")

        with self.assertRaisesRegex(RuntimeError, "required managed Issue labels"):
            publish(
                {
                    "title": "Exception",
                    "body": "<!-- openfs-exception-group:EXCGRP-001 -->",
                    "labels": ["openfs-exception", "needs-owner-action"],
                    "deduplication_marker": (
                        "<!-- openfs-exception-group:EXCGRP-001 -->"
                    ),
                },
                request=request,
            )
        self.assertEqual(2, len(calls))

    def test_resolved_group_closes_existing_issue_but_never_creates_one(self):
        calls = []
        marker = "<!-- openfs-exception-group:EXCGRP-001 -->"

        def request(method, endpoint, body):
            calls.append((method, endpoint, body))
            if endpoint.startswith("/issues?"):
                return [
                    {
                        "number": 9,
                        "html_url": "https://github.com/example/repo/issues/9",
                        "title": "Open",
                        "body": marker,
                        "state": "open",
                        "labels": [{"name": "openfs-exception"}],
                    }
                ]
            if method == "PATCH" and endpoint == "/issues/9":
                self.assertEqual("closed", body["state"])
                return {
                    "number": 9,
                    "html_url": "https://github.com/example/repo/issues/9",
                }
            raise AssertionError(f"Unexpected request: {method} {endpoint}")

        payload = {
            "title": "Resolved",
            "body": marker + "\nResolved",
            "labels": ["openfs-exception"],
            "deduplication_marker": marker,
            "desired_issue_state": "closed",
        }
        result = publish(payload, request=request)
        self.assertEqual("updated", result["publication_status"])
        self.assertEqual(2, len(calls))

        empty_calls = []

        def empty_request(method, endpoint, body):
            empty_calls.append((method, endpoint, body))
            return []

        result = publish(payload, request=empty_request)
        self.assertEqual("not-found", result["publication_status"])
        self.assertEqual(1, len(empty_calls))


if __name__ == "__main__":
    unittest.main()
