from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from run_controller import (  # noqa: E402
    _acquire_lock,
    _lock_path,
    _release_lock,
    complete_work_item,
    create_run,
    fail_work_item,
    finalize_run,
    lease_next,
    expand_followups,
)
from openfs_runtime import stable_digest  # noqa: E402


class RunControllerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        for relative in (
            "config/acquisition-policy.json",
            "config/autonomy-policy.json",
            "config/budgets.json",
            "config/consensus-policy.json",
            "config/role-permissions.json",
            "config/source-registry.json",
            "config/agent-registry.json",
            "config/monitors/MON-MEMORY-001.json",
        ):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        (self.root / "reviews" / "directives").mkdir(parents=True)

    def tearDown(self):
        self.temporary.cleanup()

    def add_directive(self):
        directive = {
            "schema_version": "0.1.0",
            "directive_id": "DIR-000123",
            "directive_type": "research-instruction",
            "title": "Pilot focus",
            "instruction": "Include memory pooling failure modes.",
            "priority": "high",
            "status": "approved",
            "submitted_by": "test-owner",
            "submitted_at": "2026-08-24T00:00:00Z",
            "scope": ["OFS-001"],
            "processed_run_ids": [],
            "result_decision_ids": [],
        }
        (self.root / "reviews" / "directives" / "DIR-000123.json").write_text(
            json.dumps(directive), encoding="utf-8"
        )

    @staticmethod
    def source_result(acquisition_decision="evidence-excerpt", source_id="SRC-TEST"):
        return {
            "source_receipt": {
                "source_id": source_id,
                "rights": {"acquisition_decision": acquisition_decision}
            }
        }

    def test_create_is_idempotent_and_includes_approved_directive(self):
        self.add_directive()
        now = datetime(2026, 8, 24, tzinfo=timezone.utc)
        first = create_run(
            self.root,
            run_id="RUN-PILOT-001",
            task_id="OFS-001",
            monitor_id="MON-MEMORY-001",
            pilot=True,
            now=now,
        )
        second = create_run(
            self.root,
            run_id="RUN-PILOT-001",
            task_id="OFS-001",
            monitor_id="MON-MEMORY-001",
            pilot=True,
            now=now + timedelta(hours=1),
        )
        self.assertEqual(first, second)
        self.assertEqual(["DIR-000123"], first["directive_ids"])
        self.assertEqual("0.2.0", first["assignment_contract_version"])
        self.assertEqual("not-evaluated", first["coverage_status"])
        self.assertEqual(13, len(first["work_item_ids"]))
        self.assertEqual(
            13,
            len(list((self.root / "queue" / "RUN-PILOT-001").glob("WORK-*.json"))),
        )
        self.assertTrue(
            (
                self.root
                / first["configuration_snapshots"]["config/agent-registry.json"]
            ).is_file()
        )
        directive_source = "reviews/directives/DIR-000123.json"
        self.assertTrue((self.root / first["directive_snapshots"][directive_source]).is_file())
        self.assertEqual(64, len(first["directive_hashes"][directive_source]))

    def test_center_monitor_expands_and_snapshots_every_registered_subject(self):
        for relative in (
            "config/hpci-center-registry.json",
            "config/monitors/MON-HPCI-CENTERS-001.json",
        ):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        manifest = create_run(
            self.root,
            run_id="RUN-CENTER-PILOT",
            task_id="OFS-003",
            monitor_id="MON-HPCI-CENTERS-001",
            pilot=True,
            now=datetime(2026, 8, 24, tzinfo=timezone.utc),
        )
        registry_ref = "config/hpci-center-registry.json"
        self.assertIn(registry_ref, manifest["policy_hashes"])
        self.assertTrue(
            (self.root / manifest["configuration_snapshots"][registry_ref]).is_file()
        )
        items = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((self.root / "queue" / "RUN-CENTER-PILOT").glob("*.json"))
        ]
        subject_items = [item for item in items if item["payload"].get("subject_ids")]
        self.assertEqual(33, len(items))
        self.assertEqual(30, len(subject_items))
        self.assertEqual(
            15,
            len({item["payload"]["subject_ids"][0] for item in subject_items}),
        )
        self.assertTrue(
            all(item["payload"].get("query_template_id") for item in subject_items)
        )

    def test_center_run_snapshots_latest_gap_followup_plan(self):
        for relative in (
            "config/hpci-center-registry.json",
            "config/monitors/MON-HPCI-CENTERS-001.json",
        ):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        brief_ref = "reviews/briefs/RUN-PRIOR-center-research.json"
        brief = {"run_id": "RUN-PRIOR", "centers": []}
        brief_path = self.root / brief_ref
        brief_path.parent.mkdir(parents=True, exist_ok=True)
        brief_path.write_text(json.dumps(brief), encoding="utf-8")
        plan_ref = "reviews/followups/RUN-PRIOR-center-gaps.json"
        plan = {
            "followup_plan_id": "CFP-TEST00000001",
            "monitor_id": "MON-HPCI-CENTERS-001",
            "task_id": "OFS-003",
            "base_run_id": "RUN-PRIOR",
            "generated_at": "2026-08-24T00:00:00Z",
            "status": "generated-for-research",
            "input_brief_ref": brief_ref,
            "input_brief_digest": stable_digest(brief),
            "queries": [
                {
                    "query_id": "FOLLOWUP-CENTER-AIST-IHF",
                    "center_id": "CENTER-AIST-IHF",
                    "profile_fields": ["power", "facility"],
                    "query": "AIST power facility official",
                    "query_role": "gap-followup",
                    "source_classes": ["center-primary"],
                }
            ],
        }
        plan_path = self.root / plan_ref
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        plan_path.write_text(json.dumps(plan), encoding="utf-8")

        manifest = create_run(
            self.root,
            run_id="RUN-CENTER-FOLLOWUP",
            task_id="OFS-003",
            monitor_id="MON-HPCI-CENTERS-001",
            pilot=True,
        )
        self.assertEqual(34, len(manifest["work_item_ids"]))
        self.assertEqual(plan_ref, manifest["followup_plan"]["source_ref"])
        self.assertTrue((self.root / manifest["followup_plan"]["snapshot_ref"]).is_file())
        items = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in (self.root / "queue" / "RUN-CENTER-FOLLOWUP").glob("*.json")
        ]
        followups = [item for item in items if item["payload"].get("followup_plan_id")]
        self.assertEqual(1, len(followups))
        self.assertEqual(["power", "facility"], followups[0]["payload"]["profile_fields"])

    def test_center_evidence_expands_one_profile_synthesis_per_subject(self):
        for relative in (
            "config/hpci-center-registry.json",
            "config/monitors/MON-HPCI-CENTERS-001.json",
        ):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        run_id = "RUN-CENTER-EXPANSION"
        create_run(
            self.root,
            run_id=run_id,
            task_id="OFS-003",
            monitor_id="MON-HPCI-CENTERS-001",
            pilot=True,
        )
        queue = self.root / "queue" / run_id
        items = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(queue.glob("*.json"))
        ]
        subject_id = next(
            item["payload"]["subject_ids"][0]
            for item in items
            if item["payload"].get("subject_ids")
        )
        subject_items = [
            item
            for item in items
            if item["payload"].get("subject_ids") == [subject_id]
        ]
        for index, item in enumerate(subject_items, 1):
            output_ref = item["output_paths"][0]
            output = self.root / output_ref
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                json.dumps(
                    {
                        "source_receipt": {
                            "source_id": f"SRC-CENTER-{index}",
                            "rights": {"acquisition_decision": "evidence-excerpt"}
                        }
                    }
                ),
                encoding="utf-8",
            )
            item["status"] = "completed"
            item["output_refs"] = [output_ref]
            (queue / f"{item['work_item_id']}.json").write_text(
                json.dumps(item), encoding="utf-8"
            )
        first = expand_followups(self.root, run_id=run_id)
        evidence_items = [
            item
            for item in first["created"]
            if item["kind"] == "evidence-extraction"
        ]
        self.assertEqual(2, len(evidence_items))
        for item in evidence_items:
            output_ref = item["output_paths"][0]
            output = self.root / output_ref
            output.parent.mkdir(parents=True, exist_ok=True)
            output.write_text(
                json.dumps({"object_type": "evidence", "run_id": run_id}),
                encoding="utf-8",
            )
            persisted = json.loads(
                (queue / f"{item['work_item_id']}.json").read_text(encoding="utf-8")
            )
            persisted["status"] = "completed"
            persisted["output_refs"] = [output_ref]
            (queue / f"{item['work_item_id']}.json").write_text(
                json.dumps(persisted), encoding="utf-8"
            )
        second = expand_followups(self.root, run_id=run_id)
        profile_items = [
            item
            for item in second["created"]
            if item["kind"] == "center-profile-synthesis"
        ]
        self.assertEqual(1, len(profile_items))
        self.assertEqual(subject_id, profile_items[0]["payload"]["center_id"])
        self.assertEqual(
            10, len(profile_items[0]["payload"]["profile_fields"])
        )

    def test_completed_profile_expands_reviewer_bound_validation(self):
        for relative in (
            "config/hpci-center-registry.json",
            "config/monitors/MON-HPCI-CENTERS-001.json",
        ):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        run_id = "RUN-CENTER-REVIEW"
        create_run(
            self.root,
            run_id=run_id,
            task_id="OFS-003",
            monitor_id="MON-HPCI-CENTERS-001",
            pilot=True,
        )
        queue = self.root / "queue" / run_id
        synthetic = {
            "schema_version": "0.1.0",
            "work_item_id": "WORK-000034",
            "run_id": run_id,
            "task_id": "OFS-003",
            "monitor_id": "MON-HPCI-CENTERS-001",
            "kind": "center-profile-synthesis",
            "required_role": "synthesis",
            "status": "completed",
            "idempotency_key": "profile-test",
            "payload": {"center_id": "CENTER-TEST"},
            "output_paths": [f"proposals/center-profiles/{run_id}/CENTER-TEST.json"],
            "output_refs": [f"proposals/center-profiles/{run_id}/CENTER-TEST.json"],
            "attempt": 1,
            "maximum_attempts": 3,
            "created_at": "2026-08-24T00:00:00Z",
            "updated_at": "2026-08-24T00:00:00Z",
        }
        output = self.root / synthetic["output_refs"][0]
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(
                {
                    "proposal_id": "PRP-CTR-000001",
                    "object_type": "center_profile",
                    "run_id": run_id,
                }
            ),
            encoding="utf-8",
        )
        (queue / "WORK-000034.json").write_text(
            json.dumps(synthetic), encoding="utf-8"
        )
        manifest_path = self.root / "runs" / run_id / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["work_item_ids"].append("WORK-000034")
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        expansion = expand_followups(self.root, run_id=run_id)
        validations = [
            item for item in expansion["created"] if item["kind"] == "validation"
        ]
        self.assertEqual(1, len(validations))
        self.assertEqual(
            "validator-public-01",
            validations[0]["payload"]["assigned_reviewer_agent_id"],
        )
        self.assertIn("validator-public-01", validations[0]["output_paths"][0])

    def test_run_control_lock_blocks_competing_mutation_and_recovers(self):
        create_run(
            self.root,
            run_id="RUN-PILOT-LOCK",
            task_id="OFS-001",
            monitor_id="MON-MEMORY-001",
            pilot=True,
        )
        lock = _lock_path(self.root, "RUN-PILOT-LOCK", "run-control")
        descriptor = _acquire_lock(lock)
        try:
            with self.assertRaisesRegex(RuntimeError, "another Run control operation"):
                lease_next(
                    self.root,
                    run_id="RUN-PILOT-LOCK",
                    agent_id="discovery-public-01",
                    allow_disabled_pilot_agent=True,
                )
        finally:
            _release_lock(lock, descriptor)
        leased = lease_next(
            self.root,
            run_id="RUN-PILOT-LOCK",
            agent_id="discovery-public-01",
            allow_disabled_pilot_agent=True,
        )
        self.assertEqual("leased", leased["status"])
        self.assertTrue(lock.exists())

    def test_run_uses_pinned_agent_registry_after_live_registry_changes(self):
        create_run(
            self.root,
            run_id="RUN-PILOT-PINNED",
            task_id="OFS-001",
            monitor_id="MON-MEMORY-001",
            pilot=True,
        )
        live_path = self.root / "config" / "agent-registry.json"
        live = json.loads(live_path.read_text(encoding="utf-8"))
        for agent in live["agents"]:
            if agent["agent_id"] == "discovery-public-01":
                agent["role"] = "critic"
        live_path.write_text(json.dumps(live), encoding="utf-8")
        leased = lease_next(
            self.root,
            run_id="RUN-PILOT-PINNED",
            agent_id="discovery-public-01",
            allow_disabled_pilot_agent=True,
        )
        self.assertEqual("source-discovery", leased["kind"])

    def test_lease_completion_records_output_digest(self):
        create_run(
            self.root,
            run_id="RUN-PILOT-002",
            task_id="OFS-001",
            monitor_id="MON-MEMORY-001",
            pilot=True,
        )
        leased = lease_next(
            self.root,
            run_id="RUN-PILOT-002",
            agent_id="discovery-public-01",
            allow_disabled_pilot_agent=True,
        )
        self.assertEqual("leased", leased["status"])
        output_ref = leased["output_paths"][0]
        output_path = self.root / output_ref
        output_path.parent.mkdir(parents=True)
        output_path.write_text('{"result":"ok"}\n', encoding="utf-8")
        completed = complete_work_item(
            self.root,
            run_id="RUN-PILOT-002",
            work_item_id=leased["work_item_id"],
            agent_id="discovery-public-01",
            output_refs=[output_ref],
        )
        self.assertEqual("completed", completed["status"])
        self.assertEqual(64, len(completed["output_digests"][output_ref]))

    def test_retry_exhaustion_creates_dead_letter_exception(self):
        create_run(
            self.root,
            run_id="RUN-PILOT-003",
            task_id="OFS-001",
            monitor_id="MON-MEMORY-001",
            pilot=True,
        )
        final = None
        for _ in range(3):
            leased = lease_next(
                self.root,
                run_id="RUN-PILOT-003",
                agent_id="discovery-public-01",
                allow_disabled_pilot_agent=True,
            )
            final = fail_work_item(
                self.root,
                run_id="RUN-PILOT-003",
                work_item_id=leased["work_item_id"],
                agent_id="discovery-public-01",
                error_kind="retrieval-timeout",
                error_message="test timeout",
                retryable=True,
            )
        self.assertEqual("dead-letter", final["status"])
        exception_path = (
            self.root
            / "reviews"
            / "exceptions"
            / "RUN-PILOT-003"
            / f"{final['work_item_id']}.json"
        )
        self.assertTrue(exception_path.is_file())

    def test_expired_lease_is_recovered(self):
        start = datetime(2026, 8, 24, tzinfo=timezone.utc)
        create_run(
            self.root,
            run_id="RUN-PILOT-004",
            task_id="OFS-001",
            monitor_id="MON-MEMORY-001",
            pilot=True,
            now=start,
        )
        first = lease_next(
            self.root,
            run_id="RUN-PILOT-004",
            agent_id="discovery-public-01",
            allow_disabled_pilot_agent=True,
            lease_seconds=60,
            now=start,
        )
        recovered = lease_next(
            self.root,
            run_id="RUN-PILOT-004",
            agent_id="discovery-public-01",
            allow_disabled_pilot_agent=True,
            now=start + timedelta(seconds=61),
        )
        self.assertEqual(first["work_item_id"], recovered["work_item_id"])
        self.assertEqual(2, recovered["attempt"])

    def test_kill_switch_blocks_new_run(self):
        (self.root / "state").mkdir()
        (self.root / "state" / "STOP").write_text("test\n", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "kill switch"):
            create_run(
                self.root,
                run_id="RUN-PILOT-005",
                task_id="OFS-001",
                monitor_id="MON-MEMORY-001",
                pilot=True,
            )

    def test_finalize_reports_completed_run(self):
        manifest = create_run(
            self.root,
            run_id="RUN-PILOT-006",
            task_id="OFS-001",
            monitor_id="MON-MEMORY-001",
            pilot=True,
        )
        for _ in manifest["work_item_ids"]:
            leased = lease_next(
                self.root,
                run_id="RUN-PILOT-006",
                agent_id="discovery-public-01",
                allow_disabled_pilot_agent=True,
            )
            output_ref = leased["output_paths"][0]
            path = self.root / output_ref
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("{}\n", encoding="utf-8")
            complete_work_item(
                self.root,
                run_id="RUN-PILOT-006",
                work_item_id=leased["work_item_id"],
                agent_id="discovery-public-01",
                output_refs=[output_ref],
            )
        completed = finalize_run(self.root, run_id="RUN-PILOT-006")
        self.assertEqual("completed", completed["status"])
        self.assertEqual({"completed": 12}, completed["metrics"]["work_items_by_status"])
        self.assertEqual("unreported", completed["cost"]["measurement_status"])
        self.assertIsNone(completed["cost"]["reported_total_usd"])

    def test_completed_discovery_expands_one_idempotent_extraction_item(self):
        create_run(
            self.root,
            run_id="RUN-PILOT-007",
            task_id="OFS-001",
            monitor_id="MON-MEMORY-001",
            pilot=True,
        )
        leased = lease_next(
            self.root,
            run_id="RUN-PILOT-007",
            agent_id="discovery-public-01",
            allow_disabled_pilot_agent=True,
        )
        output_ref = leased["output_paths"][0]
        output_path = self.root / output_ref
        output_path.parent.mkdir(parents=True)
        output_path.write_text(
            json.dumps(self.source_result()) + "\n", encoding="utf-8"
        )
        complete_work_item(
            self.root,
            run_id="RUN-PILOT-007",
            work_item_id=leased["work_item_id"],
            agent_id="discovery-public-01",
            output_refs=[output_ref],
        )
        first = expand_followups(self.root, run_id="RUN-PILOT-007")
        second = expand_followups(self.root, run_id="RUN-PILOT-007")
        self.assertEqual(1, len(first["created"]))
        self.assertEqual([], second["created"])
        self.assertEqual("evidence-extraction", first["created"][0]["kind"])
        self.assertEqual("extraction", first["created"][0]["required_role"])

    def test_two_source_slots_expand_one_query_synthesis(self):
        create_run(
            self.root,
            run_id="RUN-PILOT-008",
            task_id="OFS-001",
            monitor_id="MON-MEMORY-001",
            pilot=True,
        )
        for slot in range(2):
            leased = lease_next(
                self.root,
                run_id="RUN-PILOT-008",
                agent_id="discovery-public-01",
                allow_disabled_pilot_agent=True,
            )
            output_ref = leased["output_paths"][0]
            output_path = self.root / output_ref
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(
                json.dumps(self.source_result(source_id=f"SRC-SLOT-{slot}")) + "\n",
                encoding="utf-8",
            )
            complete_work_item(
                self.root,
                run_id="RUN-PILOT-008",
                work_item_id=leased["work_item_id"],
                agent_id="discovery-public-01",
                output_refs=[output_ref],
            )
        extraction_expansion = expand_followups(self.root, run_id="RUN-PILOT-008")
        self.assertEqual(2, len(extraction_expansion["created"]))
        for _ in range(2):
            leased = lease_next(
                self.root,
                run_id="RUN-PILOT-008",
                agent_id="extraction-public-01",
                allow_disabled_pilot_agent=True,
            )
            output_ref = leased["output_paths"][0]
            output_path = self.root / output_ref
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("{}\n", encoding="utf-8")
            complete_work_item(
                self.root,
                run_id="RUN-PILOT-008",
                work_item_id=leased["work_item_id"],
                agent_id="extraction-public-01",
                output_refs=[output_ref],
            )
        synthesis_expansion = expand_followups(self.root, run_id="RUN-PILOT-008")
        synthesis = [
            item for item in synthesis_expansion["created"] if item["kind"] == "synthesis"
        ]
        self.assertEqual(1, len(synthesis))
        self.assertEqual(2, len(synthesis[0]["payload"]["evidence_bundle_refs"]))

    def test_metadata_only_source_is_skipped_and_replaced_idempotently(self):
        create_run(
            self.root,
            run_id="RUN-PILOT-009",
            task_id="OFS-001",
            monitor_id="MON-MEMORY-001",
            pilot=True,
        )
        leased = lease_next(
            self.root,
            run_id="RUN-PILOT-009",
            agent_id="discovery-public-01",
            allow_disabled_pilot_agent=True,
        )
        output_ref = leased["output_paths"][0]
        output_path = self.root / output_ref
        output_path.parent.mkdir(parents=True)
        output_path.write_text(
            json.dumps(self.source_result("metadata-only")) + "\n",
            encoding="utf-8",
        )
        complete_work_item(
            self.root,
            run_id="RUN-PILOT-009",
            work_item_id=leased["work_item_id"],
            agent_id="discovery-public-01",
            output_refs=[output_ref],
        )

        first = expand_followups(self.root, run_id="RUN-PILOT-009")
        second = expand_followups(self.root, run_id="RUN-PILOT-009")

        self.assertEqual(1, len(first["created"]))
        replacement = first["created"][0]
        self.assertEqual("source-discovery", replacement["kind"])
        self.assertEqual(
            leased["work_item_id"],
            replacement["payload"]["replacement_for_work_item_id"],
        )
        self.assertEqual([], second["created"])
        self.assertEqual(
            "metadata-only",
            second["manifest"]["skipped_evidence_sources"][0][
                "acquisition_decision"
            ],
        )

    def test_elapsed_run_budget_stops_and_records_exception(self):
        start = datetime(2026, 8, 24, tzinfo=timezone.utc)
        create_run(
            self.root,
            run_id="RUN-PILOT-010",
            task_id="OFS-001",
            monitor_id="MON-MEMORY-001",
            pilot=True,
            now=start,
        )

        leased = lease_next(
            self.root,
            run_id="RUN-PILOT-010",
            agent_id="discovery-public-01",
            allow_disabled_pilot_agent=True,
            now=start + timedelta(minutes=120),
        )

        self.assertIsNone(leased)
        manifest = json.loads(
            (self.root / "runs" / "RUN-PILOT-010" / "manifest.json").read_text()
        )
        self.assertEqual("stopped", manifest["status"])
        self.assertEqual("maximum-run-minutes", manifest["stop"]["reason"])
        self.assertTrue(
            (
                self.root
                / "reviews"
                / "exceptions"
                / "RUN-PILOT-010"
                / "STOP-MAXIMUM-RUN-MINUTES.json"
            ).is_file()
        )
        queue = [
            json.loads(path.read_text())
            for path in (self.root / "queue" / "RUN-PILOT-010").glob("*.json")
        ]
        self.assertEqual({"cancelled"}, {item["status"] for item in queue})

    def test_reported_cost_budget_is_enforced_before_next_lease(self):
        start = datetime(2026, 8, 24, tzinfo=timezone.utc)
        create_run(
            self.root,
            run_id="RUN-PILOT-011",
            task_id="OFS-001",
            monitor_id="MON-MEMORY-001",
            pilot=True,
            now=start,
        )
        manifest_path = self.root / "runs" / "RUN-PILOT-011" / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["budget"]["maximum_cost_usd"] = 0.5
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        leased = lease_next(
            self.root,
            run_id="RUN-PILOT-011",
            agent_id="discovery-public-01",
            allow_disabled_pilot_agent=True,
            now=start,
        )
        output_ref = leased["output_paths"][0]
        output_path = self.root / output_ref
        output_path.parent.mkdir(parents=True)
        output_path.write_text("{}\n", encoding="utf-8")
        complete_work_item(
            self.root,
            run_id="RUN-PILOT-011",
            work_item_id=leased["work_item_id"],
            agent_id="discovery-public-01",
            output_refs=[output_ref],
            usage={"input_tokens": 100, "output_tokens": 20, "cost_usd": 0.6},
            now=start + timedelta(seconds=1),
        )

        next_item = lease_next(
            self.root,
            run_id="RUN-PILOT-011",
            agent_id="discovery-public-01",
            allow_disabled_pilot_agent=True,
            now=start + timedelta(seconds=2),
        )
        self.assertIsNone(next_item)
        stopped = json.loads(manifest_path.read_text())
        self.assertEqual("maximum-cost-usd", stopped["stop"]["reason"])
        self.assertEqual(0.6, stopped["cost"]["reported_total_usd"])

    def test_parallel_lease_limit_throttles_without_stopping_run(self):
        start = datetime(2026, 8, 24, tzinfo=timezone.utc)
        create_run(
            self.root,
            run_id="RUN-PILOT-012",
            task_id="OFS-001",
            monitor_id="MON-MEMORY-001",
            pilot=True,
            now=start,
        )
        manifest_path = self.root / "runs" / "RUN-PILOT-012" / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["budget"]["maximum_parallel_agents"] = 1
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
        first = lease_next(
            self.root,
            run_id="RUN-PILOT-012",
            agent_id="discovery-public-01",
            allow_disabled_pilot_agent=True,
            now=start,
        )
        second = lease_next(
            self.root,
            run_id="RUN-PILOT-012",
            agent_id="discovery-public-01",
            allow_disabled_pilot_agent=True,
            now=start + timedelta(seconds=1),
        )
        self.assertIsNotNone(first)
        self.assertIsNone(second)
        self.assertNotEqual("stopped", json.loads(manifest_path.read_text())["status"])


if __name__ == "__main__":
    unittest.main()
