import json
import tempfile
import unittest
from pathlib import Path

from tools.check_public_planning_surfaces import EXPECTED_SCALES, validate


ROOT = Path(__file__).resolve().parents[1]


class PublicPlanningSurfaceTests(unittest.TestCase):
    def test_repository_surfaces_pass(self):
        self.assertEqual(validate(ROOT), [])

    def test_standard_scales_are_fixed(self):
        self.assertEqual(EXPECTED_SCALES, [1, 4, 32, 128, 1024, 10000])

    def test_rejects_reused_calibration_data(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "config").mkdir()
            (root / "knowledge/public").mkdir(parents=True)
            for relative in (
                "config/hpci-center-registry.json",
                "knowledge/public/hpci-system-inventory.json",
                "knowledge/public/application-performance-forecasts.json",
            ):
                source = json.loads((ROOT / relative).read_text(encoding="utf-8"))
                (root / relative).write_text(
                    json.dumps(source, ensure_ascii=False), encoding="utf-8"
                )
            path = root / "knowledge/public/application-performance-forecasts.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["forecasts"] = [
                {
                    "forecast_id": "FORECAST-TEST-001",
                    "forecast_class": "validated",
                    "application_id": "APP-EEA1-GENESIS",
                    "candidate_system_id": "CANDIDATE-TEST",
                    "fugaku_nodes": 4,
                    "scaling_mode": "strong-scaling",
                    "comparison_basis": "same-node-count",
                    "metric_id": "time-to-solution",
                    "estimate": {"lower": 1.0, "base": 2.0, "upper": 3.0, "unit": "s"},
                    "model_card_id": "PMCARD-TEST-001",
                    "assumption_ids": ["ASM-PERF-GENESIS"],
                    "basis_source_ids": ["SRC-PERF001"],
                    "calibration_dataset_ids": ["DATA-SHARED"],
                    "validation_dataset_ids": ["DATA-SHARED"],
                    "confidence": "low",
                    "consensus_status": "incomplete",
                    "procurement_eligible": False,
                }
            ]
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            self.assertTrue(
                any("reuses calibration data" in error for error in validate(root))
            )

    def test_rejects_unknown_topic_decision_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for relative in (
                "config/research-baseline.json",
                "config/hpci-center-registry.json",
                "knowledge/public/hpci-system-inventory.json",
                "knowledge/public/application-performance-forecasts.json",
                "knowledge/public/topic-decision-support.json",
            ):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(
                    (ROOT / relative).read_text(encoding="utf-8"), encoding="utf-8"
                )
            path = root / "knowledge/public/topic-decision-support.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["actors"][0]["source_ids"] = ["SRC-UNKNOWN"]
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            self.assertTrue(
                any("unknown sources" in error for error in validate(root))
            )


if __name__ == "__main__":
    unittest.main()
