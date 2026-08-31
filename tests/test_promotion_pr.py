from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from publish_promotion_pr import create, find_open  # noqa: E402
from automation_pr_description import format_body


class PromotionPullRequestTests(unittest.TestCase):
    def test_find_open_recognizes_only_promotion_branch(self):
        pulls = [
            {
                "number": 7,
                "html_url": "https://example.test/7",
                "head": {
                    "user": {"login": "HPCI-CFSP"},
                    "ref": "automation/claim-promotion-123",
                },
            }
        ]
        with patch("publish_promotion_pr._request", return_value=pulls):
            result = find_open("HPCI-CFSP/OpenFS", "token", base="main")
        self.assertEqual(7, result["number"])

    def test_create_uses_review_only_claim_language(self):
        created = {"number": 8, "html_url": "https://example.test/8"}
        summary = {"affected_run_ids": ["RUN-1"], "prepared": [{
            "canonical_claim_id": "CLM-000001", "proposal_ref": "proposals/claims/PRP-000001.json",
            "decision_ref": "decisions/DEC-000001.json"}]}
        with patch(
            "publish_promotion_pr._request", side_effect=[[], created]
        ) as request:
            result = create(
                "HPCI-CFSP/OpenFS",
                "token",
                head="automation/claim-promotion-456",
                base="main",
                summary=summary,
                prepared_description=format_body("promotion", summary, "a" * 40),
            )
        self.assertEqual("created", result["status"])
        body = request.call_args_list[1].args[4]["body"]
        self.assertIn("does not contain Recommendations", body)
        self.assertIn("Review the pinned Proposal", body)
        self.assertLess(body.index("# English"), body.index("# 日本語"))

    def test_missing_validation_context_cannot_post(self):
        with patch("publish_promotion_pr._request", return_value=[]) as request:
            with self.assertRaises(ValueError):
                create("HPCI-CFSP/OpenFS", "token", head="automation/claim-promotion-1", base="main", summary={})
        self.assertEqual(1, request.call_count)


if __name__ == "__main__":
    unittest.main()
