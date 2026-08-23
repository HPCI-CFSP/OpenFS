from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from evaluate_operational_readiness import evaluate  # noqa: E402
from validate_repository import validate_activation_configuration  # noqa: E402


class OperationalReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.write(
            "config/activation-policy.json",
            {
                "required_workflow_gates": [
                    {
                        "control_id": "gate",
                        "workflow_ref": ".github/workflows/worker.yml",
                        "variable": "OPENFS_WORKER_ENABLED",
                    }
                ],
                "required_production_components": [
                    {
                        "control_id": "worker",
                        "path": "tools/worker.py",
                        "purpose": "Execute provider work.",
                    }
                ],
                "required_owner_controls": ["budget"],
                "production_monitor_minimum_manual_runs": 1,
                "effect": "Default deny.",
            },
        )
        self.write(
            "config/owner-controls.json",
            {
                "controls": [
                    {
                        "control_id": "budget",
                        "status": "unverified",
                        "verified_by": None,
                        "verified_at": None,
                        "expires_at": None,
                        "evidence_note": "",
                    }
                ]
            },
        )
        self.write(
            "config/monitors/MON-TEST.json",
            {
                "monitor_id": "MON-TEST",
                "enabled": False,
                "manual_run_requirement": 1,
            },
        )

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, ref, value):
        path = self.root / ref
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(value, str):
            path.write_text(value, encoding="utf-8")
        else:
            path.write_text(json.dumps(value), encoding="utf-8")

    @patch("evaluate_operational_readiness.evaluate_monitor")
    def test_missing_worker_owner_attestation_and_enabled_monitor_block(self, monitor):
        monitor.return_value = {"status": "blocked", "blockers": ["monitor_enabled"]}
        report = evaluate(self.root, evaluated_at="2026-08-24T05:00:00Z")
        self.assertEqual("blocked", report["status"])
        self.assertEqual(
            [
                "enabled_monitors_ready",
                "owner_controls_verified",
                "production_components_present",
                "research_monitor_enabled",
                "workflow_gates_present",
            ],
            report["blockers"],
        )

    @patch("evaluate_operational_readiness.evaluate_monitor")
    def test_all_local_and_owner_gates_can_reach_ready(self, monitor):
        self.write(
            ".github/workflows/worker.yml",
            "if: vars.OPENFS_WORKER_ENABLED == 'true'\n",
        )
        self.write("tools/worker.py", "# tested fixture\n")
        self.write(
            "config/owner-controls.json",
            {
                "controls": [
                    {
                        "control_id": "budget",
                        "status": "verified",
                        "verified_by": "Repository Owner",
                        "verified_at": "2026-08-24T04:00:00Z",
                        "expires_at": "2026-09-24T04:00:00Z",
                        "evidence_note": "Provider hard limit reviewed; no secret recorded.",
                    }
                ]
            },
        )
        self.write(
            "config/monitors/MON-TEST.json",
            {
                "monitor_id": "MON-TEST",
                "enabled": True,
                "manual_run_requirement": 1,
            },
        )
        monitor.return_value = {"status": "ready", "blockers": []}
        report = evaluate(self.root, evaluated_at="2026-08-24T05:00:00Z")
        self.assertEqual("ready", report["status"])
        self.assertEqual([], report["blockers"])

    @patch("evaluate_operational_readiness.evaluate_monitor")
    def test_expired_owner_attestation_fails_closed(self, monitor):
        self.write(".github/workflows/worker.yml", "OPENFS_WORKER_ENABLED\n")
        self.write("tools/worker.py", "# fixture\n")
        controls = json.loads((self.root / "config/owner-controls.json").read_text())
        controls["controls"][0].update(
            {
                "status": "verified",
                "verified_by": "Owner",
                "verified_at": "2026-07-01T00:00:00Z",
                "expires_at": "2026-08-01T00:00:00Z",
                "evidence_note": "Reviewed.",
            }
        )
        self.write("config/owner-controls.json", controls)
        monitor.return_value = {"status": "ready", "blockers": []}
        report = evaluate(self.root, evaluated_at="2026-08-24T05:00:00Z")
        self.assertFalse(report["checks"]["owner_controls_verified"])
        self.assertEqual("owner attestation is expired or incomplete", report["owner_controls"][0]["reason"])

    def test_repository_validation_detects_duplicate_owner_controls(self):
        controls = json.loads((self.root / "config/owner-controls.json").read_text())
        controls["controls"].append(dict(controls["controls"][0]))
        self.write("config/owner-controls.json", controls)
        errors = validate_activation_configuration(self.root)
        self.assertTrue(any("duplicate owner" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
