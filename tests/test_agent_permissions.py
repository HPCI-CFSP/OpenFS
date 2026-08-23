from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from check_agent_branch import parse_agent_id, validate_branch_paths  # noqa: E402
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

    def test_topic_promotion_is_limited_to_catalog_and_auto_monitor(self):
        allowed, denied = check_paths(
            "topic-promotion",
            [
                "config/research-baseline.json",
                "config/publication-i18n.json",
                "config/monitors/MON-AUTO-TOPICS-001.json",
                "runs/RUN-001/topic-promotion.json",
                "config/consensus-policy.json",
                "docs/research-baseline/README.md",
            ],
            self.config,
        )
        self.assertEqual(4, len(allowed))
        self.assertEqual(
            ["config/consensus-policy.json", "docs/research-baseline/README.md"],
            denied,
        )

    def test_path_traversal_is_denied(self):
        _, denied = check_paths("discovery", ["../data/sources/SRC.json"], self.config)
        self.assertTrue(denied)

    def test_control_characters_in_path_are_denied(self):
        _, denied = check_paths("discovery", ["proposals/sources/ok\nDENY fake"], self.config)
        self.assertTrue(denied)

    def test_agent_branch_requires_expected_shape(self):
        self.assertEqual(
            "validator-public-01",
            parse_agent_id("agent/validator-public-01/RUN-001/WORK-000001"),
        )
        self.assertIsNone(parse_agent_id("agent/validator-public-01/incomplete"))
        self.assertIsNone(
            parse_agent_id("agent/validator-public-01/RUN-001/WORK-000001/extra")
        )
        self.assertIsNone(
            parse_agent_id("agent/validator-public-01/RUN-001/WORK-001")
        )

    def test_agent_branch_is_limited_to_assigned_outputs_and_handoff(self):
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            work_path = root / "queue" / "RUN-001" / "WORK-000001.json"
            work_path.parent.mkdir(parents=True)
            work_path.write_text(
                json.dumps(
                    {
                        "run_id": "RUN-001",
                        "work_item_id": "WORK-000001",
                        "required_role": "discovery",
                        "output_paths": [
                            "proposals/sources/RUN-001/WORK-000001.json"
                        ],
                    }
                ),
                encoding="utf-8",
            )
            manifest_path = root / "runs" / "RUN-001" / "manifest.json"
            manifest_path.parent.mkdir(parents=True)
            manifest_path.write_text(
                json.dumps({"mode": "production"}), encoding="utf-8"
            )
            registry = {
                "discovery-public-01": {
                    "agent_id": "discovery-public-01",
                    "role": "discovery",
                    "enabled": True,
                }
            }
            assigned = [
                "proposals/sources/RUN-001/WORK-000001.json",
                "handoffs/RUN-001/WORK-000001.json",
            ]
            allowed, denied = validate_branch_paths(
                root,
                branch="agent/discovery-public-01/RUN-001/WORK-000001",
                paths=assigned,
                registry=registry,
                permissions=self.config,
            )
            self.assertEqual(sorted(assigned), allowed)
            self.assertEqual([], denied)
            _, denied = validate_branch_paths(
                root,
                branch="agent/discovery-public-01/RUN-001/WORK-000001",
                paths=assigned + ["runs/RUN-001/manifest.json"],
                registry=registry,
                permissions=self.config,
            )
            self.assertIn(
                "path is outside branch assignment: runs/RUN-001/manifest.json",
                denied,
            )

    def test_disabled_agent_is_allowed_only_for_a_pinned_pilot_run(self):
        import json
        import tempfile

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            work = root / "queue/RUN-001/WORK-000001.json"
            work.parent.mkdir(parents=True)
            work.write_text(
                json.dumps(
                    {
                        "run_id": "RUN-001",
                        "work_item_id": "WORK-000001",
                        "required_role": "discovery",
                        "output_paths": ["proposals/sources/RUN-001/WORK-000001.json"],
                    }
                ),
                encoding="utf-8",
            )
            manifest = root / "runs/RUN-001/manifest.json"
            manifest.parent.mkdir(parents=True)
            manifest.write_text(json.dumps({"mode": "pilot"}), encoding="utf-8")
            paths = [
                "proposals/sources/RUN-001/WORK-000001.json",
                "handoffs/RUN-001/WORK-000001.json",
            ]
            allowed, denied = validate_branch_paths(
                root,
                branch="agent/discovery-public-01/RUN-001/WORK-000001",
                paths=paths,
                registry={
                    "discovery-public-01": {
                        "agent_id": "discovery-public-01",
                        "role": "discovery",
                        "enabled": False,
                    }
                },
                permissions=self.config,
            )
            self.assertEqual(sorted(paths), allowed)
            self.assertEqual([], denied)


if __name__ == "__main__":
    unittest.main()
