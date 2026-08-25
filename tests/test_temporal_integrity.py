from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from evaluate_temporal_integrity import evaluate, record  # noqa: E402


class TemporalIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.run_id = "RUN-TEMPORAL-TEST"
        manifest_path = self.root / "runs" / self.run_id / "manifest.json"
        manifest_path.parent.mkdir(parents=True)
        manifest_path.write_text(
            json.dumps(
                {
                    "run_id": self.run_id,
                    "started_at": "2026-08-24T00:00:00Z",
                    "completed_at": "2026-08-24T00:10:00Z",
                    "metrics": {},
                }
            ),
            encoding="utf-8",
        )
        self.work_path = self.root / "queue" / self.run_id / "WORK-000001.json"
        self.work_path.parent.mkdir(parents=True)

    def tearDown(self):
        self.temporary.cleanup()

    def write_work(self, executed_at: str) -> None:
        output_ref = f"proposals/sources/{self.run_id}/WORK-000001.json"
        self.work_path.write_text(
            json.dumps(
                {
                    "run_id": self.run_id,
                    "work_item_id": "WORK-000001",
                    "created_at": "2026-08-24T00:00:00Z",
                    "updated_at": "2026-08-24T00:09:00Z",
                    "output_refs": [output_ref],
                }
            ),
            encoding="utf-8",
        )
        output_path = self.root / output_ref
        output_path.parent.mkdir(parents=True)
        output_path.write_text(
            json.dumps(
                {
                    "run_id": self.run_id,
                    "query_receipt": {"executed_at": executed_at},
                    "source_receipt": {"retrieved_at": executed_at},
                }
            ),
            encoding="utf-8",
        )

    def test_future_artifact_blocks_publication_and_opens_exception(self):
        self.write_work("2026-08-24T00:20:00Z")
        report = evaluate(
            self.root,
            run_id=self.run_id,
            evaluated_at="2026-08-24T00:10:00Z",
        )
        self.assertEqual("failed", report["status"])
        self.assertEqual(2, report["anomaly_count"])
        manifest = record(self.root, report)
        self.assertTrue(manifest["metrics"]["temporal_integrity"]["publication_blocked"])
        exception = json.loads(
            (
                self.root
                / "reviews"
                / "exceptions"
                / self.run_id
                / "TEMPORAL-INTEGRITY.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual("open", exception["status"])
        self.assertTrue(exception["publication_blocked"])

    def test_valid_rerun_resolves_existing_exception(self):
        self.write_work("2026-08-24T00:05:00Z")
        exception_path = (
            self.root
            / "reviews"
            / "exceptions"
            / self.run_id
            / "TEMPORAL-INTEGRITY.json"
        )
        exception_path.parent.mkdir(parents=True)
        exception_path.write_text(
            json.dumps({"status": "open", "publication_blocked": True}),
            encoding="utf-8",
        )
        report = evaluate(
            self.root,
            run_id=self.run_id,
            evaluated_at="2026-08-24T00:10:00Z",
        )
        self.assertEqual("passed", report["status"])
        record(self.root, report)
        exception = json.loads(exception_path.read_text(encoding="utf-8"))
        self.assertEqual("resolved", exception["status"])
        self.assertFalse(exception["publication_blocked"])


if __name__ == "__main__":
    unittest.main()
