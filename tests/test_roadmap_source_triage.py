from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from tools.build_roadmap_source_triage import build_triage


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class RoadmapSourceTriageTests(unittest.TestCase):
    def test_committed_triage_covers_every_non_reachable_source(self):
        audit = load_json(ROOT / "knowledge/public/audits/roadmap-source-audit.json")
        triage = load_json(ROOT / "knowledge/public/audits/roadmap-source-triage.json")
        warned = {
            (item["roadmap_id"], item["source_id"])
            for item in audit["results"]
            if item["status"] != "reachable"
        }
        triaged = {(item["roadmap_id"], item["source_id"]) for item in triage["entries"]}
        self.assertEqual(warned, triaged)
        self.assertEqual(len(warned), triage["summary"]["non_reachable_count"])
        self.assertEqual(0, triage["summary"]["stale_review_count"])
        self.assertEqual("incomplete", triage["reviewer"]["consensus_status"])

    def test_changed_source_url_invalidates_pinned_review(self):
        config = load_json(ROOT / "config/roadmap-source-retrieval-reviews.json")
        audit = load_json(ROOT / "knowledge/public/audits/roadmap-source-audit.json")
        changed = dict(config)
        changed["entries"] = [dict(item) for item in config["entries"]]
        changed["entries"][0]["url"] = "https://example.invalid/stale"
        with tempfile.TemporaryDirectory() as directory:
            temp = Path(directory)
            config_path = temp / "config.json"
            audit_path = temp / "audit.json"
            config_path.write_text(json.dumps(changed), encoding="utf-8")
            audit_path.write_text(json.dumps(audit), encoding="utf-8")
            triage = build_triage(ROOT, config_path, audit_path)
        self.assertEqual(1, triage["summary"]["stale_review_count"])
        self.assertEqual(
            "unresolved",
            next(item for item in triage["entries"] if item["source_id"] == changed["entries"][0]["source_id"])["review_outcome"],
        )
        self.assertIsNone(next(item for item in triage["entries"] if item["source_id"] == changed["entries"][0]["source_id"])["reviewed_at"])

    def test_new_manual_checks_do_not_rewrite_http_audit_results(self):
        config = ROOT / "config/roadmap-source-retrieval-reviews.json"
        audit = ROOT / "knowledge/public/audits/roadmap-source-audit.json"
        result = build_triage(ROOT, config, audit)
        added = [e for e in result["entries"] if e["source_id"] in {"SRC-BLUE033", "SRC-BLUE034"}]
        self.assertEqual(2, len(added))
        self.assertTrue(all(e["http_audit_status"] == "error" and e["http_status"] is None for e in added))
        self.assertTrue(all(e["review_outcome"] == "exact-url-content-confirmed" for e in added))


if __name__ == "__main__":
    unittest.main()
