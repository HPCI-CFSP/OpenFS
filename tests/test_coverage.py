from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from evaluate_coverage import evaluate_coverage, record_coverage  # noqa: E402
from openfs_runtime import read_json, stable_digest  # noqa: E402
from run_controller import create_run  # noqa: E402


class CoverageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        monitor_relative = Path("config/monitors/MON-MEMORY-001.json")
        monitor_path = self.root / monitor_relative
        monitor_path.parent.mkdir(parents=True)
        shutil.copy2(ROOT / monitor_relative, monitor_path)
        run_id = "RUN-COVERAGE-TEST"
        run_path = self.root / "runs" / run_id
        run_path.mkdir(parents=True)
        manifest = {
            "run_id": run_id,
            "monitor_id": "MON-MEMORY-001",
            "policy_hashes": {
                monitor_relative.as_posix(): stable_digest(read_json(monitor_path))
            },
            "query_receipts": [],
            "research_status": "not-evaluated",
            "coverage_status": "not-evaluated",
            "metrics": {},
        }
        (run_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        source_path = self.root / "proposals" / "sources" / run_id
        source_path.mkdir(parents=True)
        result = {
            "query_receipt": {
                "query_receipt_id": "QRY-000000000001",
                "query": "HPC memory hierarchy roadmap",
                "failures": [],
            },
            "source_receipt": {
                "source_id": "SRC-000000000001",
                "source_class": "peer-reviewed-research",
                "language": "en",
                "primary_source": True,
                "origin_group_id": "ORG-000000000001",
                "rights": {"acquisition_decision": "evidence-excerpt"},
            },
        }
        (source_path / "WORK-000001.json").write_text(json.dumps(result), encoding="utf-8")

    def tearDown(self):
        self.temporary.cleanup()

    def test_incomplete_coverage_preserves_consensus_status_and_updates_receipts(self):
        report = evaluate_coverage(self.root, run_id="RUN-COVERAGE-TEST")
        self.assertEqual("incomplete", report["coverage_status"])
        self.assertTrue(report["monitor_snapshot_match"])
        self.assertIn("ja", report["gaps"]["missing_languages"])
        manifest = record_coverage(self.root, report)
        self.assertEqual("not-evaluated", manifest["research_status"])
        self.assertEqual("incomplete", manifest["coverage_status"])
        self.assertEqual(1, len(manifest["query_receipts"]))
        self.assertGreater(manifest["metrics"]["coverage"]["gap_count"], 0)

    def test_monitor_change_invalidates_coverage_snapshot(self):
        monitor = self.root / "config" / "monitors" / "MON-MEMORY-001.json"
        changed = json.loads(monitor.read_text(encoding="utf-8"))
        changed["maximum_unchecked_days"] += 1
        monitor.write_text(json.dumps(changed), encoding="utf-8")
        report = evaluate_coverage(self.root, run_id="RUN-COVERAGE-TEST")
        self.assertFalse(report["monitor_snapshot_match"])
        self.assertIn("monitor_snapshot_mismatch", report["gaps"])

    def test_standards_body_counts_toward_authoritative_primary_requirement(self):
        path = (
            self.root
            / "proposals"
            / "sources"
            / "RUN-COVERAGE-TEST"
            / "WORK-000001.json"
        )
        result = json.loads(path.read_text(encoding="utf-8"))
        result["source_receipt"]["source_class"] = "standards-body"
        path.write_text(json.dumps(result), encoding="utf-8")
        report = evaluate_coverage(self.root, run_id="RUN-COVERAGE-TEST")
        authoritative = next(
            item
            for item in report["observed"]["source_class_requirement_results"]
            if item["requirement_id"] == "authoritative-primary"
        )
        self.assertFalse(authoritative["met"])
        self.assertEqual(1, authoritative["observed_count"])

    def test_rights_exclusion_is_reported_as_warning(self):
        path = (
            self.root
            / "proposals"
            / "sources"
            / "RUN-COVERAGE-TEST"
            / "WORK-000001.json"
        )
        result = json.loads(path.read_text(encoding="utf-8"))
        result["query_receipt"]["failures"] = [
            {"kind": "rights-excluded", "detail": "Replacement selected."}
        ]
        path.write_text(json.dumps(result), encoding="utf-8")
        report = evaluate_coverage(self.root, run_id="RUN-COVERAGE-TEST")
        self.assertEqual([], report["gaps"]["query_failures"])
        self.assertEqual(
            "rights-excluded", report["observed"]["query_warnings"][0]["kind"]
        )

    def test_reused_source_is_counted_once_without_blocking_coverage(self):
        source_path = (
            self.root
            / "proposals"
            / "sources"
            / "RUN-COVERAGE-TEST"
            / "WORK-000001.json"
        )
        duplicate = json.loads(source_path.read_text(encoding="utf-8"))
        duplicate["query_receipt"]["query_receipt_id"] = "QRY-000000000002"
        (source_path.parent / "WORK-000002.json").write_text(
            json.dumps(duplicate), encoding="utf-8"
        )
        report = evaluate_coverage(self.root, run_id="RUN-COVERAGE-TEST")
        self.assertEqual(1, report["observed"]["source_count"])
        self.assertEqual(
            ["SRC-000000000001"], report["observed"]["reused_source_ids"]
        )
        self.assertNotIn("duplicate_source_selections", report["gaps"])

    def test_unclassified_failure_remains_blocking(self):
        path = (
            self.root
            / "proposals"
            / "sources"
            / "RUN-COVERAGE-TEST"
            / "WORK-000001.json"
        )
        result = json.loads(path.read_text(encoding="utf-8"))
        result["query_receipt"]["failures"] = [
            {"kind": "timeout", "detail": "Search endpoint timed out."}
        ]
        path.write_text(json.dumps(result), encoding="utf-8")
        report = evaluate_coverage(self.root, run_id="RUN-COVERAGE-TEST")
        self.assertEqual("timeout", report["gaps"]["query_failures"][0]["kind"])


class CenterCoverageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        for relative in (
            "config/acquisition-policy.json",
            "config/agent-registry.json",
            "config/autonomy-policy.json",
            "config/budgets.json",
            "config/consensus-policy.json",
            "config/role-permissions.json",
            "config/source-registry.json",
            "config/hpci-center-registry.json",
            "config/monitors/MON-HPCI-CENTERS-001.json",
        ):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        (self.root / "reviews" / "directives").mkdir(parents=True)
        create_run(
            self.root,
            run_id="RUN-CENTER-COVERAGE",
            task_id="OFS-003",
            monitor_id="MON-HPCI-CENTERS-001",
            pilot=True,
        )

    def tearDown(self):
        self.temporary.cleanup()

    def test_one_subject_search_cannot_claim_registry_coverage(self):
        run_id = "RUN-CENTER-COVERAGE"
        queue_items = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((self.root / "queue" / run_id).glob("*.json"))
        ]
        item = next(entry for entry in queue_items if entry["payload"].get("subject_ids"))
        result = {
            "query_receipt": {
                "query_receipt_id": "QRY-CENTER000001",
                "query": item["payload"]["query"],
                "failures": [],
            },
            "source_receipt": {
                "source_id": "SRC-CENTER000001",
                "source_class": "center-primary",
                "language": "ja",
                "primary_source": True,
                "origin_group_id": "ORG-CENTER000001",
                "rights": {"acquisition_decision": "evidence-excerpt"},
                "assignment_scope": {
                    "subject_ids": item["payload"]["subject_ids"],
                    "profile_fields": item["payload"]["profile_fields"],
                    "query_template_id": item["payload"]["query_template_id"],
                },
            },
        }
        output = self.root / "proposals" / "sources" / run_id / f"{item['work_item_id']}.json"
        output.parent.mkdir(parents=True)
        output.write_text(json.dumps(result), encoding="utf-8")
        report = evaluate_coverage(self.root, run_id=run_id)
        self.assertEqual("incomplete", report["coverage_status"])
        self.assertEqual(15, report["expected"]["subject_count"])
        self.assertEqual(1, report["observed"]["subject_count"])
        self.assertEqual(14, len(report["gaps"]["missing_subject_searches"]))
        self.assertEqual(15, len(report["gaps"]["missing_subject_profile_queries"]))

    def test_reused_source_preserves_each_subject_assignment(self):
        run_id = "RUN-CENTER-COVERAGE"
        queue_items = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((self.root / "queue" / run_id).glob("*.json"))
        ]
        subject_items = [
            entry for entry in queue_items if entry["payload"].get("subject_ids")
        ]
        selected = [
            subject_items[0],
            next(
                entry
                for entry in subject_items
                if entry["payload"]["subject_ids"] != subject_items[0]["payload"]["subject_ids"]
            ),
        ]
        source_path = self.root / "proposals" / "sources" / run_id
        source_path.mkdir(parents=True, exist_ok=True)
        for index, item in enumerate(selected, 1):
            result = {
                "query_receipt": {
                    "query_receipt_id": f"QRY-REUSED{index:06d}",
                    "query": item["payload"]["query"],
                    "failures": [],
                },
                "source_receipt": {
                    "source_id": "SRC-REUSEDCENTER",
                    "source_class": "official-primary",
                    "language": "ja",
                    "primary_source": True,
                    "origin_group_id": "ORG-REUSEDCENTER",
                    "rights": {"acquisition_decision": "evidence-excerpt"},
                    "assignment_scope": {
                        "subject_ids": item["payload"]["subject_ids"],
                        "profile_fields": item["payload"]["profile_fields"],
                        "query_template_id": item["payload"]["query_template_id"],
                    },
                },
            }
            (source_path / f"{item['work_item_id']}.json").write_text(
                json.dumps(result), encoding="utf-8"
            )
        report = evaluate_coverage(self.root, run_id=run_id)
        self.assertEqual(1, report["observed"]["source_count"])
        self.assertEqual(2, report["observed"]["subject_count"])


if __name__ == "__main__":
    unittest.main()
