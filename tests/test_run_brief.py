from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from generate_run_brief import build_brief, render_markdown  # noqa: E402


class RunBriefTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.run_id = "RUN-BRIEF-001"

    def tearDown(self):
        self.temporary.cleanup()

    def write_json(self, relative, value):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def test_brief_traces_claim_to_source_and_surfaces_unmet_checks(self):
        self.write_json(
            f"runs/{self.run_id}/manifest.json",
            {
                "status": "completed",
                "research_status": "provisional",
                "metrics": {"consensus_readiness": "incomplete"},
            },
        )
        self.write_json(
            f"runs/{self.run_id}/coverage.json",
            {"coverage_status": "met-declared-scope"},
        )
        self.write_json(
            f"proposals/sources/{self.run_id}/WORK-000001.json",
            {
                "source_receipt": {
                    "source_id": "SRC-1",
                    "title": "Source <script>",
                    "publisher": "Example",
                    "canonical_url": "https://example.org/source",
                    "source_class": "official-primary",
                    "primary_source": True,
                    "origin_group_id": "ORG-1",
                }
            },
        )
        evidence_ref = f"proposals/evidence/{self.run_id}/WORK-000002.json"
        self.write_json(
            evidence_ref,
            {
                "source_result_ref": (
                    f"proposals/sources/{self.run_id}/WORK-000001.json"
                )
            },
        )
        self.write_json(
            f"proposals/claims/{self.run_id}/WORK-000003.json",
            {
                "proposal_id": "PRP-1",
                "evidence_bundle_refs": [evidence_ref],
                "claim_candidate": {
                    "claim_id": "CLM-1",
                    "statement": "Candidate statement.",
                    "claim_kind": "interpretation",
                    "conditions": ["Configuration-specific."],
                },
            },
        )
        self.write_json(
            f"assessments/{self.run_id}/WORK-000004.json",
            {
                "assessment_id": "ASM-1",
                "proposal_id": "PRP-1",
                "verdict": "uncertain",
                "reviewer_agent_id": "validator-1",
                "agent_independence_group": "group-1",
                "objections": [{"severity": "major", "message": "Needs another model."}],
            },
        )
        self.write_json(
            f"decisions/{self.run_id}/PRP-1.json",
            {
                "proposal_id": "PRP-1",
                "outcome": "provisional",
                "policy_result": {
                    "checks": {"minimum_support": False, "primary_source": True}
                },
            },
        )

        brief = build_brief(
            self.root,
            run_id=self.run_id,
            generated_at="2026-08-24T00:00:00Z",
        )

        self.assertEqual("human-review-required", brief["review_status"])
        self.assertEqual(["minimum_support"], brief["claims"][0]["unmet_consensus_checks"])
        self.assertEqual(
            "https://example.org/source",
            brief["claims"][0]["sources"][0]["canonical_url"],
        )
        self.assertEqual(
            {
                "source_count": 1,
                "origin_group_count": 1,
                "primary_source_count": 1,
            },
            brief["claims"][0]["evidence_summary"],
        )
        rendered = render_markdown(brief)
        self.assertIn("1 Sources / 1 Origin Groups / 1 primary Sources", rendered)
        self.assertIn("Source &lt;script&gt;", rendered)
        self.assertNotIn("Source <script>", rendered)


if __name__ == "__main__":
    unittest.main()
