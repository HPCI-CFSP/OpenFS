from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from check_agent_branch import parse_agent_id  # noqa: E402
from check_agent_permissions import check_paths, load_config  # noqa: E402


class AgentPermissionTests(unittest.TestCase):
    def setUp(self):
        self.config = load_config(ROOT / "config" / "role-permissions.json")

    def test_unknown_role_is_default_deny(self):
        _, denied = check_paths("unknown", ["proposals/sources/SRC.json"], self.config)
        self.assertTrue(denied)

    def test_discovery_cannot_write_canonical_data(self):
        allowed, denied = check_paths(
            "discovery",
            ["proposals/sources/PRP.json", "data/sources/SRC.json"],
            self.config,
        )
        self.assertEqual(["proposals/sources/PRP.json"], allowed)
        self.assertEqual(["data/sources/SRC.json"], denied)

    def test_validator_can_only_write_assessment_and_run_paths(self):
        allowed, denied = check_paths(
            "validator",
            ["assessments/PRP/ASM.json", "runs/RUN/summary.json", "proposals/evidence/EVD.json"],
            self.config,
        )
        self.assertEqual(2, len(allowed))
        self.assertEqual(["proposals/evidence/EVD.json"], denied)

    def test_maintainer_requires_explicit_human_authorization(self):
        _, denied = check_paths("maintainer", ["AGENTS.md"], self.config)
        self.assertTrue(denied)
        allowed, denied = check_paths(
            "maintainer", ["AGENTS.md"], self.config, human_authorized=True
        )
        self.assertEqual(["AGENTS.md"], allowed)
        self.assertEqual([], denied)

    def test_path_traversal_is_denied(self):
        _, denied = check_paths("discovery", ["../data/sources/SRC.json"], self.config)
        self.assertTrue(denied)

    def test_control_characters_in_path_are_denied(self):
        _, denied = check_paths("discovery", ["proposals/sources/ok\nDENY fake"], self.config)
        self.assertTrue(denied)

    def test_agent_branch_requires_expected_shape(self):
        self.assertEqual(
            "validator-public-01",
            parse_agent_id("agent/validator-public-01/RUN-001/WORK-001"),
        )
        self.assertIsNone(parse_agent_id("agent/validator-public-01/incomplete"))
        self.assertIsNone(parse_agent_id("agent/validator-public-01/RUN-001/WORK-001/extra"))


if __name__ == "__main__":
    unittest.main()
