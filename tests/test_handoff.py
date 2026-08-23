from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from accept_handoff import accept_handoff  # noqa: E402
from create_handoff import create_handoff  # noqa: E402
from openfs_runtime import atomic_write_json, read_json  # noqa: E402
from process_pending_handoffs import process  # noqa: E402
from run_controller import create_run  # noqa: E402


class HandoffTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        for relative in (
            "config/acquisition-policy.json",
            "config/autonomy-policy.json",
            "config/budgets.json",
            "config/consensus-policy.json",
            "config/role-permissions.json",
            "config/skill-registry.json",
            "config/source-registry.json",
            "config/agent-registry.json",
            "config/monitors/MON-MEMORY-001.json",
        ):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        for source in (ROOT / "skills").glob("*/SKILL.md"):
            target = self.root / source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        (self.root / "reviews" / "directives").mkdir(parents=True)
        create_run(
            self.root,
            run_id="RUN-HANDOFF-001",
            task_id="OFS-001",
            monitor_id="MON-MEMORY-001",
            pilot=True,
            now=datetime(2026, 8, 24, tzinfo=timezone.utc),
        )

    def tearDown(self):
        self.temporary.cleanup()

    def make_handoff(self):
        output_ref = "proposals/sources/RUN-HANDOFF-001/WORK-000001.json"
        atomic_write_json(
            self.root / output_ref,
            {
                "run_id": "RUN-HANDOFF-001",
                "work_item_id": "WORK-000001",
                "source_receipt": {
                    "rights": {"acquisition_decision": "evidence-excerpt"}
                },
            },
        )
        handoff = create_handoff(
            self.root,
            run_id="RUN-HANDOFF-001",
            work_item_id="WORK-000001",
            agent_id="discovery-public-01",
            usage={"cost_usd": 0.25, "measurement_note": "provider receipt"},
            created_at="2026-08-24T00:01:00Z",
            allow_disabled_pilot_agent=True,
        )
        handoff_ref = "handoffs/RUN-HANDOFF-001/WORK-000001.json"
        atomic_write_json(self.root / handoff_ref, handoff)
        return handoff_ref

    def test_merged_handoff_completes_control_state_idempotently(self):
        handoff_ref = self.make_handoff()
        item = accept_handoff(
            self.root,
            handoff_ref=handoff_ref,
            allow_disabled_pilot_agent=True,
            now="2026-08-24T00:02:00Z",
        )
        self.assertEqual("completed", item["status"])
        self.assertEqual("merged-handoff", item["completion_mode"])
        self.assertEqual(1, item["attempt"])
        self.assertEqual(handoff_ref, item["handoff_ref"])
        second = accept_handoff(
            self.root,
            handoff_ref=handoff_ref,
            allow_disabled_pilot_agent=True,
            now="2026-08-24T00:03:00Z",
        )
        self.assertEqual(item, second)
        manifest = read_json(self.root / "runs/RUN-HANDOFF-001/manifest.json")
        execution = manifest["agent_executions"][0]
        self.assertEqual("discovery-public-01", execution["agent_id"])
        self.assertEqual(1, execution["attempt"])

    def test_changed_output_is_rejected_after_handoff_creation(self):
        handoff_ref = self.make_handoff()
        output = self.root / "proposals/sources/RUN-HANDOFF-001/WORK-000001.json"
        output.write_text(json.dumps({"run_id": "RUN-HANDOFF-001", "changed": True}))
        with self.assertRaisesRegex(ValueError, "digest mismatch"):
            accept_handoff(
                self.root,
                handoff_ref=handoff_ref,
                allow_disabled_pilot_agent=True,
            )

    def test_stale_attempt_is_rejected(self):
        handoff_ref = self.make_handoff()
        handoff_path = self.root / handoff_ref
        handoff = read_json(handoff_path)
        handoff["attempt"] = 2
        atomic_write_json(handoff_path, handoff)
        with self.assertRaisesRegex(ValueError, "attempt"):
            accept_handoff(
                self.root,
                handoff_ref=handoff_ref,
                allow_disabled_pilot_agent=True,
            )

    def test_pending_processor_accepts_once_and_expands_followup(self):
        handoff_ref = self.make_handoff()
        result = process(
            self.root,
            allow_disabled_pilot_agent=True,
            processed_at="2026-08-24T00:02:00Z",
        )
        self.assertEqual([handoff_ref], result["accepted_handoff_refs"])
        self.assertEqual(
            ["WORK-000013"], result["expansions"][0]["created_work_item_ids"]
        )
        second = process(
            self.root,
            allow_disabled_pilot_agent=True,
            processed_at="2026-08-24T00:03:00Z",
        )
        self.assertEqual([], second["accepted_handoff_refs"])
        self.assertEqual([handoff_ref], second["already_accepted_handoff_refs"])


if __name__ == "__main__":
    unittest.main()
