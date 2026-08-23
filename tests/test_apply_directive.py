from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from apply_directive import apply  # noqa: E402
from openfs_runtime import stable_digest  # noqa: E402


class ApplyDirectiveTests(unittest.TestCase):
    def setUp(self):
        self.directive = {
            "directive_id": "DIR-000001",
            "directive_type": "research-instruction",
            "instruction": "Investigate public evidence.",
            "status": "approved",
            "scope": ["OFS-001"],
        }
        self.manifest = {"run_id": "RUN-TEST", "task_id": "OFS-001"}
        self.work_item = {
            "work_item_id": "WORK-000001",
            "run_id": "RUN-TEST",
            "kind": "apply-directive",
            "payload": {
                "directive_id": "DIR-000001",
                "instruction_digest": stable_digest(self.directive["instruction"]),
            },
        }

    def test_records_bounds_without_inventing_publication_authority(self):
        result = apply(
            directive=self.directive,
            manifest=self.manifest,
            work_item=self.work_item,
            agent_id="orchestrator-local-01",
            applied_at="2026-08-24T00:00:00Z",
        )
        self.assertEqual("applied", result["status"])
        self.assertFalse(result["authorization_bounds"]["publication_approved"])
        self.assertEqual("public", result["authorization_bounds"]["information_plane"])

    def test_rejects_instruction_changed_after_run_creation(self):
        self.directive["instruction"] = "Changed instruction"
        with self.assertRaisesRegex(ValueError, "changed"):
            apply(
                directive=self.directive,
                manifest=self.manifest,
                work_item=self.work_item,
                agent_id="orchestrator-local-01",
            )


if __name__ == "__main__":
    unittest.main()
