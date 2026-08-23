from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from detect_source_changes import compare_runs, write_report  # noqa: E402


class SourceChangeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def add_run(self, run_id, started_at, sources, status="completed"):
        run_dir = self.root / "runs" / run_id
        run_dir.mkdir(parents=True)
        manifest = {
            "run_id": run_id,
            "task_id": "OFS-001",
            "monitor_id": "MON-MEMORY-001",
            "started_at": started_at,
            "status": status,
            "metrics": {},
        }
        (run_dir / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        source_dir = self.root / "proposals" / "sources" / run_id
        source_dir.mkdir(parents=True)
        for number, source in enumerate(sources, 1):
            result = {
                "query_receipt": {"query": source.get("query", source["url"])},
                "source_receipt": {
                    "canonical_url": source["url"],
                    "title": source.get("title", "Title"),
                    "publisher": "Publisher",
                    "publication_date": "2026-01-01",
                    "media_type": "text/html",
                    "language": "en",
                    "retrieval_status": source.get("status", "success"),
                    "retrieved_content_sha256": source.get("digest"),
                    "rights": {
                        "acquisition_decision": source.get(
                            "decision", "evidence-excerpt"
                        )
                    },
                },
                "candidate_passages": source.get(
                    "passages", [{"text": "stable", "locator": "p1"}]
                ),
            }
            (source_dir / f"WORK-{number:06d}.json").write_text(
                json.dumps(result), encoding="utf-8"
            )

    def test_classifies_changes_without_treating_omission_as_withdrawal(self):
        self.add_run(
            "RUN-OLD",
            "2026-08-17T00:00:00Z",
            [
                {"url": "https://example.org/same"},
                {"url": "https://example.org/changed", "passages": [{"text": "old", "locator": "p1"}]},
                {"url": "https://example.org/omitted"},
                {"url": "https://example.org/down"},
            ],
        )
        self.add_run(
            "RUN-NEW",
            "2026-08-24T00:00:00Z",
            [
                {"url": "https://example.org/same"},
                {"url": "https://example.org/changed", "passages": [{"text": "new", "locator": "p1"}]},
                {"url": "https://example.org/down", "status": "unavailable", "decision": "metadata-only", "passages": []},
                {"url": "https://example.org/new"},
            ],
        )

        report = compare_runs(
            self.root,
            run_id="RUN-NEW",
            generated_at="2026-08-24T01:00:00Z",
        )
        observed = {
            item["canonical_url"]: item["classification"] for item in report["changes"]
        }
        self.assertEqual("unchanged", observed["https://example.org/same"])
        self.assertEqual("changed", observed["https://example.org/changed"])
        self.assertEqual("not-observed", observed["https://example.org/omitted"])
        self.assertEqual("unavailable", observed["https://example.org/down"])
        self.assertEqual("new", observed["https://example.org/new"])

        output = write_report(self.root, report)
        self.assertTrue(output.is_file())
        manifest = json.loads(
            (self.root / "runs" / "RUN-NEW" / "manifest.json").read_text()
        )
        self.assertEqual("RUN-OLD", manifest["previous_run_id"])
        self.assertEqual(report["summary"], manifest["metrics"]["source_changes"])

    def test_same_url_can_be_observed_for_multiple_assigned_queries(self):
        shared = "https://example.org/shared-report"
        self.add_run(
            "RUN-OLD",
            "2026-08-17T00:00:00Z",
            [
                {"url": shared, "query": "center A", "passages": [{"text": "A", "locator": "row A"}]},
                {"url": shared, "query": "center B", "passages": [{"text": "B", "locator": "row B"}]},
            ],
        )
        self.add_run(
            "RUN-NEW",
            "2026-08-24T00:00:00Z",
            [
                {"url": shared, "query": "center A", "passages": [{"text": "A", "locator": "row A"}]},
                {"url": shared, "query": "center B", "passages": [{"text": "B", "locator": "row B"}]},
                {"url": shared, "query": "center C", "passages": [{"text": "C", "locator": "row C"}]},
            ],
        )

        report = compare_runs(self.root, run_id="RUN-NEW")
        self.assertEqual(2, report["summary"]["unchanged"])
        self.assertEqual(1, report["summary"]["new"])
        self.assertEqual(
            {"center A", "center B", "center C"},
            {item["observation_query"] for item in report["changes"]},
        )


if __name__ == "__main__":
    unittest.main()
