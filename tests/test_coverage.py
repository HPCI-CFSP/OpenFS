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
from openfs_runtime import sha256_file  # noqa: E402


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
            "policy_hashes": {monitor_relative.as_posix(): sha256_file(monitor_path)},
            "query_receipts": [],
            "research_status": "not-evaluated",
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

    def test_incomplete_coverage_updates_research_status_and_receipts(self):
        report = evaluate_coverage(self.root, run_id="RUN-COVERAGE-TEST")
        self.assertEqual("incomplete", report["coverage_status"])
        self.assertTrue(report["monitor_snapshot_match"])
        self.assertIn("ja", report["gaps"]["missing_languages"])
        manifest = record_coverage(self.root, report)
        self.assertEqual("coverage-incomplete", manifest["research_status"])
        self.assertEqual(1, len(manifest["query_receipts"]))
        self.assertGreater(manifest["metrics"]["coverage"]["gap_count"], 0)

    def test_monitor_change_invalidates_coverage_snapshot(self):
        monitor = self.root / "config" / "monitors" / "MON-MEMORY-001.json"
        monitor.write_text(monitor.read_text(encoding="utf-8") + "\n", encoding="utf-8")
        report = evaluate_coverage(self.root, run_id="RUN-COVERAGE-TEST")
        self.assertFalse(report["monitor_snapshot_match"])
        self.assertIn("monitor_snapshot_mismatch", report["gaps"])


if __name__ == "__main__":
    unittest.main()
