from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from publish_control_pr import create, find_open  # noqa: E402


class ControlPullRequestTests(unittest.TestCase):
    def test_find_open_recognizes_only_control_branch(self):
        pulls = [
            {
                "number": 3,
                "html_url": "https://example.test/3",
                "head": {
                    "user": {"login": "HPCI-CFSP"},
                    "ref": "automation/handoff-control-123",
                },
            }
        ]
        with patch("publish_control_pr._request", return_value=pulls):
            result = find_open("HPCI-CFSP/OpenFS", "token", base="main")
        self.assertEqual(3, result["number"])

    def test_create_does_not_open_second_control_pr(self):
        existing = {
            "number": 3,
            "html_url": "https://example.test/3",
            "head": {
                "user": {"login": "HPCI-CFSP"},
                "ref": "automation/handoff-control-123",
            },
        }
        with patch("publish_control_pr._request", return_value=[existing]) as request:
            result = create(
                "HPCI-CFSP/OpenFS",
                "token",
                head="automation/handoff-control-456",
                base="main",
                summary={"affected_run_ids": [], "accepted_handoff_refs": []},
            )
        self.assertEqual("blocked-by-existing", result["status"])
        self.assertEqual(1, request.call_count)


if __name__ == "__main__":
    unittest.main()
