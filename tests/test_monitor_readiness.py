from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from evaluate_monitor_readiness import evaluate  # noqa: E402
from openfs_runtime import stable_digest  # noqa: E402
from prepare_weekly_cycle import build_plan  # noqa: E402
from prepare_run_approval import prepare  # noqa: E402


class MonitorReadinessTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.monitor = {
            "monitor_id": "MON-TEST-001",
            "task_id": "OFS-001",
            "enabled": True,
            "manual_run_requirement": 1,
            "consensus_object_types": ["claim"],
        }
        self.write("config/monitors/MON-TEST-001.json", self.monitor)
        self.write(
            "config/budgets.json",
            {
                "status": "approved",
                "defaults": {"maximum_cost_usd": 10.0},
            },
        )
        self.write(
            "config/consensus-policy.json",
            {
                "policy_id": "CONSENSUS-TEST-001",
                "calibration_status": "calibrated",
                "rules": {
                    "claim": {
                        "minimum_assessments": 3,
                        "minimum_support_independence_groups": 2,
                        "require_falsification_review": True,
                    }
                },
            },
        )
        self.write(
            "config/agent-registry.json",
            {
                "agents": [
                    self.agent("author", "synthesis", "provider-a", "author-group"),
                    self.agent("validator-b", "validator", "provider-b", "group-b"),
                    self.agent("validator-c", "validator", "provider-c", "group-c"),
                    self.agent("critic-d", "critic", "provider-d", "group-d"),
                ]
            },
        )

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, relative: str, value: dict) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")
        return path

    @staticmethod
    def agent(agent_id: str, role: str, provider: str, group: str) -> dict:
        return {
            "agent_id": agent_id,
            "enabled": True,
            "role": role,
            "provider": provider,
            "model_family": f"{provider}-model",
            "agent_independence_group": group,
        }

    def add_reviewed_run(self) -> tuple[Path, Path]:
        run_id = "RUN-TEST-PILOT-001"
        manifest = {
            "run_id": run_id,
            "monitor_id": self.monitor["monitor_id"],
            "task_id": self.monitor["task_id"],
            "mode": "pilot",
            "started_at": "2026-08-20T00:00:00Z",
            "status": "completed",
            "coverage_status": "met-declared-scope",
            "research_status": "accepted",
            "metrics": {"temporal_integrity": {"status": "passed"}},
        }
        manifest_path = self.write(f"runs/{run_id}/manifest.json", manifest)
        brief = {"run_id": run_id, "review_status": "eligible-for-publication-review"}
        brief_path = self.write(f"reviews/briefs/{run_id}.json", brief)
        self.write(
            f"reviews/run-approvals/{run_id}.json",
            {
                "schema_version": "0.1.0",
                "approval_id": "RUNAPP-TEST-001",
                "run_id": run_id,
                "monitor_id": self.monitor["monitor_id"],
                "status": "reviewed-pass",
                "manifest_digest": stable_digest(manifest),
                "brief_ref": str(brief_path.relative_to(self.root)),
                "brief_digest": stable_digest(brief),
                "prepared_at": "2026-08-21T00:00:00Z",
                "reviewed_by": "human-owner",
                "reviewed_at": "2026-08-21T00:00:00Z",
                "checks": {
                    "public_information_boundary": True,
                    "citation_sample": True,
                    "coverage": True,
                    "false_positive_review": True,
                    "dissent_review": True,
                    "cost_review": True,
                },
                "notes": "Calibration Run reviewed.",
            },
        )
        return manifest_path, brief_path

    def test_prepared_review_is_default_deny_and_idempotent(self):
        self.add_reviewed_run()
        approval_path = (
            self.root / "reviews" / "run-approvals" / "RUN-TEST-PILOT-001.json"
        )
        approval_path.unlink()

        first, output = prepare(
            self.root,
            run_id="RUN-TEST-PILOT-001",
            prepared_at="2026-08-21T00:00:00Z",
        )
        second, _ = prepare(
            self.root,
            run_id="RUN-TEST-PILOT-001",
            prepared_at="2026-08-21T00:00:00Z",
        )

        self.assertEqual(first, second)
        self.assertEqual("draft", first["status"])
        self.assertIsNone(first["reviewed_by"])
        self.assertFalse(any(first["checks"].values()))
        self.assertTrue(output.is_file())
        report = evaluate(
            self.root,
            monitor_id=self.monitor["monitor_id"],
            evaluated_at="2026-08-24T00:00:00Z",
        )
        self.assertEqual("blocked", report["status"])

    def test_ready_requires_digest_pinned_human_reviewed_run(self):
        self.add_reviewed_run()

        report = evaluate(
            self.root,
            monitor_id=self.monitor["monitor_id"],
            evaluated_at="2026-08-24T00:00:00Z",
        )

        self.assertEqual("ready", report["status"])
        self.assertEqual(1, report["manual_runs"]["valid_reviewed_count"])
        plan = build_plan(
            self.root,
            week="2026-W35",
            generated_at="2026-08-24T00:00:00Z",
        )
        self.assertEqual("ready", plan["status"])
        self.assertEqual(
            "ready", plan["monitors"][0]["production_readiness"]["status"]
        )

    def test_manifest_mutation_invalidates_approval_and_blocks_cycle(self):
        manifest_path, _ = self.add_reviewed_run()
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["research_status"] = "contested"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        report = evaluate(
            self.root,
            monitor_id=self.monitor["monitor_id"],
            evaluated_at="2026-08-24T00:00:00Z",
        )
        plan = build_plan(
            self.root,
            week="2026-W35",
            generated_at="2026-08-24T00:00:00Z",
        )

        self.assertEqual("blocked", report["status"])
        self.assertIn("reviewed_manual_runs_complete", report["blockers"])
        self.assertIn(
            "run-manifest-digest-mismatch",
            report["manual_runs"]["invalid"][0]["reasons"],
        )
        self.assertEqual("blocked", plan["status"])
        self.assertEqual(
            ["monitor-not-production-ready:MON-TEST-001"], plan["blockers"]
        )


if __name__ == "__main__":
    unittest.main()
