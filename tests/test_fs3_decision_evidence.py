from __future__ import annotations

import json
import unittest
from pathlib import Path

from tools.build_fs3_decision_evidence import build_artifact, render_report


ROOT = Path(__file__).resolve().parents[1]


class Fs3DecisionEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.artifact = json.loads(
            (ROOT / "knowledge/public/fs3-decision-evidence.json").read_text(
                encoding="utf-8"
            )
        )

    def test_generated_artifact_is_current(self):
        self.assertEqual(build_artifact(), self.artifact)

    def test_snapshot_counts_and_boundaries(self):
        data = self.artifact
        self.assertEqual("provisional", data["research_status"])
        self.assertEqual("incomplete", data["consensus_status"])
        self.assertEqual("blocked", data["security_readiness"]["status"])
        self.assertIsNone(data["security_readiness"]["selected_profile_id"])
        triage = json.loads(
            (ROOT / "knowledge/public/audits/roadmap-source-triage.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            triage["summary"]["unresolved"],
            data["security_readiness"]["source_triage"]["unresolved"],
        )
        self.assertEqual(27, data["hpci_systems"]["summary"]["system_count"])
        procurement_register = json.loads(
            (ROOT / "knowledge/public/procurement-cost-register.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(
            len(procurement_register["cases"]),
            data["procurements"]["summary"]["case_count"],
        )
        self.assertGreaterEqual(data["procurements"]["summary"]["case_count"], 14)
        self.assertEqual(0, data["procurements"]["summary"]["component_itemized_count"])
        self.assertEqual(0, data["procurements"]["summary"]["complete_tco_count"])
        self.assertEqual(6, data["eea1"]["summary"]["application_count"])
        self.assertEqual(0, data["eea1"]["summary"]["complete_baseline_package_count"])
        self.assertEqual(0, data["eea1"]["summary"]["approved_threshold_count"])
        self.assertEqual(0, data["eea1"]["summary"]["validated_forecast_count"])
        self.assertEqual(19, data["roadmaps"]["summary"]["roadmap_count"])

    def test_report_preserves_unresolved_evidence(self):
        report = render_report(self.artifact)
        self.assertIn("## 2. Web調査自動化のセキュリティ境界", report)
        self.assertIn("費目別の価格内訳 0件、完全なTCO 0件", report)
        self.assertIn("完全な再現パッケージ 0件", report)
        self.assertIn("```mermaid", report)
        self.assertIn("Consensus: incomplete", report)

    def test_report_index_is_bilingual_and_directive_bound(self):
        index = json.loads(
            (ROOT / "reports/exports/index.json").read_text(encoding="utf-8")
        )
        report = index["reports"][0]
        self.assertTrue(report["title"])
        self.assertTrue(report["title_en"])
        self.assertTrue(report["summary"])
        self.assertTrue(report["summary_en"])
        self.assertEqual(
            "DIR-900105", report["publication"]["human_approval_directive_id"]
        )


if __name__ == "__main__":
    unittest.main()
