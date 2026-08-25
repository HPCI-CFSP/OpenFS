from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from analyze_dependency_impact import analyze, write_report  # noqa: E402


class DependencyImpactTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        run_dir = self.root / "runs" / "RUN-NEW"
        run_dir.mkdir(parents=True)
        self.write(
            "runs/RUN-NEW/manifest.json",
            {"run_id": "RUN-NEW", "metrics": {}},
        )

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, ref, value):
        path = self.root / ref
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def change_report(self, classification="changed"):
        return {
            "run_id": "RUN-NEW",
            "previous_run_id": "RUN-OLD",
            "changes": [
                {
                    "canonical_url": "https://example.org/source",
                    "observation_query": "assigned query",
                    "classification": classification,
                    "previous_source_ref": "proposals/sources/RUN-OLD/WORK-000001.json",
                    "current_source_ref": (
                        None
                        if classification == "not-observed"
                        else "proposals/sources/RUN-NEW/WORK-000001.json"
                    ),
                }
            ],
        }

    def add_dependency_chain(self):
        evidence_ref = "proposals/evidence/RUN-OLD/WORK-000002.json"
        self.write(
            evidence_ref,
            {
                "source_result_ref": "proposals/sources/RUN-OLD/WORK-000001.json"
            },
        )
        self.write(
            "proposals/claims/RUN-OLD/WORK-000003.json",
            {
                "proposal_id": "PRP-CLM-000001",
                "evidence_bundle_refs": [evidence_ref],
            },
        )
        self.write(
            "proposals/center-profiles/RUN-OLD/WORK-000004.json",
            {
                "proposal_id": "PRP-CENTER-000001",
                "evidence_bundle_refs": [evidence_ref],
            },
        )
        self.write(
            "decisions/RUN-OLD/PRP-CLM-000001.json",
            {"proposal_id": "PRP-CLM-000001"},
        )
        self.write(
            "decisions/RUN-OLD/PRP-CENTER-000001.json",
            {"proposal_id": "PRP-CENTER-000001"},
        )

    def test_changed_source_blocks_dependent_promotion(self):
        self.add_dependency_chain()
        report = analyze(
            self.root,
            run_id="RUN-NEW",
            change_report=self.change_report(),
            generated_at="2026-08-24T01:00:00Z",
        )

        self.assertTrue(report["summary"]["promotion_blocked"])
        self.assertEqual(1, report["summary"]["impacted_evidence_bundles"])
        self.assertEqual(1, report["summary"]["impacted_claim_proposals"])
        self.assertEqual(1, report["summary"]["impacted_center_profiles"])
        self.assertEqual(2, report["summary"]["impacted_decisions"])
        self.assertEqual("revalidate-dependents", report["impacts"][0]["action"])

        output = write_report(self.root, report)
        self.assertTrue(output.is_file())
        manifest = json.loads(
            (self.root / "runs" / "RUN-NEW" / "manifest.json").read_text()
        )
        self.assertEqual(
            "runs/RUN-NEW/dependency-impact.json",
            manifest["dependency_impact_ref"],
        )

    def test_not_observed_requests_reobservation_without_invalidation(self):
        self.add_dependency_chain()
        report = analyze(
            self.root,
            run_id="RUN-NEW",
            change_report=self.change_report("not-observed"),
        )

        self.assertFalse(report["summary"]["promotion_blocked"])
        self.assertEqual(1, report["summary"]["reobservation_gaps"])
        self.assertEqual("reobserve", report["impacts"][0]["action"])
        self.assertFalse(report["impacts"][0]["promotion_blocked"])


if __name__ == "__main__":
    unittest.main()
