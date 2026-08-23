from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from generate_center_research_brief import build_brief, render_markdown  # noqa: E402


class CenterResearchBriefTests(unittest.TestCase):
    def test_brief_prioritizes_cross_center_unknowns(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            run_id = "RUN-CENTER-BRIEF"
            run_dir = root / "runs" / run_id
            run_dir.mkdir(parents=True)
            (run_dir / "manifest.json").write_text(
                json.dumps(
                    {
                        "status": "completed",
                        "metrics": {"consensus_readiness": "incomplete"},
                    }
                ),
                encoding="utf-8",
            )
            (run_dir / "coverage.json").write_text(
                json.dumps({"coverage_status": "met-declared-scope"}),
                encoding="utf-8",
            )
            (run_dir / "center-profile-coverage.json").write_text(
                json.dumps(
                    {
                        "profile_coverage_status": "incomplete",
                        "observed": {"accepted_current_count": 0},
                    }
                ),
                encoding="utf-8",
            )
            profile_dir = root / "proposals" / "center-profiles" / run_id
            profile_dir.mkdir(parents=True)
            profile = {
                "center_id": "CENTER-TEST",
                "name_ja": "試験センター",
                "name_en": "Test Center",
                "profile_status": "provisional",
                "evidence_as_of": "2026-08-24",
                "evidence_refs": [],
            }
            for field in (
                "users", "priority_domains", "current_system", "refresh_window",
                "power", "facility", "software", "operations", "migration",
                "data_connectivity",
            ):
                status = "verified" if field == "current_system" else "unknown"
                profile[field] = {
                    "status": status,
                    "summary": "Current system documented." if status == "verified" else "No Evidence.",
                    "as_of": "2026-08-24" if status == "verified" else None,
                    "evidence_refs": [],
                }
            (profile_dir / "CENTER-TEST.json").write_text(
                json.dumps(profile), encoding="utf-8"
            )
            brief = build_brief(
                root, run_id=run_id, generated_at="2026-08-24T05:00:00Z"
            )
            self.assertEqual(1, brief["summary"]["center_count"])
            self.assertEqual("met-declared-scope", brief["web_coverage_status"])
            self.assertEqual(9, len(brief["priority_followups"]))
            self.assertIn("power", {item["field"] for item in brief["priority_followups"]})
            self.assertIn("CENTER-TEST", render_markdown(brief))


if __name__ == "__main__":
    unittest.main()
