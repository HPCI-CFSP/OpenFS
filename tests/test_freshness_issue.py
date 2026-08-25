from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from prepare_freshness_issue import MARKER, build_payload  # noqa: E402


class FreshnessIssueTests(unittest.TestCase):
    def audit(self, attention_items):
        return {
            "audit_id": "RFA-20260826-001",
            "generated_at": "2026-08-26T03:00:00Z",
            "summary": {"roadmap_count": 6, "milestone_count": 146},
            "attention_items": attention_items,
        }

    def validate(self, payload):
        schema = json.loads(
            (ROOT / "schemas" / "issue-payload.schema.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertTrue(set(schema["required"]).issubset(payload))
        self.assertTrue(set(payload).issubset(schema["properties"]))
        self.assertIn(
            payload["desired_issue_state"],
            schema["properties"]["desired_issue_state"]["enum"],
        )

    def test_includes_only_critical_and_high_attention(self):
        payload = build_payload(
            self.audit(
                [
                    {
                        "attention_id": "RFAI-0002",
                        "severity": "low",
                        "roadmap_id": "RM-B",
                        "object_id": "SRC-B",
                        "reason": "source-date-unknown",
                    },
                    {
                        "attention_id": "RFAI-0001",
                        "severity": "high",
                        "roadmap_id": "RM-A",
                        "object_id": "MS-A",
                        "reason": "no-public-date",
                    },
                ]
            )
        )
        self.validate(payload)
        self.assertEqual("open", payload["desired_issue_state"])
        self.assertEqual(["RFAI-0001"], payload["exception_ids"])
        self.assertIn("`MS-A`", payload["body"])
        self.assertNotIn("`SRC-B`", payload["body"])
        self.assertEqual(MARKER, payload["deduplication_marker"])

    def test_requests_close_when_priority_queue_is_empty(self):
        payload = build_payload(self.audit([]))
        self.validate(payload)
        self.assertEqual("closed", payload["desired_issue_state"])
        self.assertEqual(["RFAI-NONE"], payload["exception_ids"])
        self.assertIn("resolved", payload["title"])


if __name__ == "__main__":
    unittest.main()
