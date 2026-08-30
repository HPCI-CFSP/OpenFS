from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from ingest_directive import ingest_issue, write_directive  # noqa: E402


class DirectiveIngestionTests(unittest.TestCase):
    def issue(self):
        return {
            "issue_number": 42,
            "html_url": "https://github.com/HPCI-CFSP/OpenFS/issues/42",
            "title": "Investigate memory pooling failure modes",
            "author": "research-owner",
            "created_at": "2026-08-24T00:00:00Z",
            "objective": "Assess failure domains and fallback behavior.",
            "scope": ["OFS-001"],
            "expected_output": "A comparison with evidence gaps.",
            "suggested_sources": ["https://www.computeexpresslink.org/"],
            "priority": "high",
            "public_information_confirmed": True,
            "labels": ["research-directive", "directive-approved"],
        }

    def test_approved_issue_becomes_traceable_directive(self):
        directive = ingest_issue(self.issue())
        self.assertEqual("DIR-000042", directive["directive_id"])
        self.assertEqual("approved", directive["status"])
        self.assertTrue(directive["source"]["untrusted_input"])
        self.assertEqual(64, len(directive["source"]["content_digest"]))

    def test_unapproved_issue_remains_proposed(self):
        issue = self.issue()
        issue["labels"].remove("directive-approved")
        self.assertEqual("proposed", ingest_issue(issue)["status"])

    def test_private_boundary_confirmation_is_required(self):
        issue = self.issue()
        issue["public_information_confirmed"] = False
        with self.assertRaisesRegex(ValueError, "public-information"):
            ingest_issue(issue)

    def test_public_feedback_cannot_be_promoted_by_adding_approval_labels(self):
        for label in ("public-feedback", "correction-report", "research-request", "improvement-proposal"):
            with self.subTest(label=label):
                issue = self.issue()
                issue["labels"].append(label)
                with self.assertRaisesRegex(ValueError, "Public feedback"):
                    ingest_issue(issue)

    def test_write_is_idempotent_and_rejects_changed_content(self):
        directive = ingest_issue(self.issue())
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            first = write_directive(output, directive)
            second = write_directive(output, directive)
            self.assertEqual(first, second)
            changed = dict(directive)
            changed["title"] = "Changed"
            with self.assertRaisesRegex(RuntimeError, "different content"):
                write_directive(output, changed)


if __name__ == "__main__":
    unittest.main()
