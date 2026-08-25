from __future__ import annotations

import copy
import unittest

from tools.check_performance_model_card import evaluate


def valid_card():
    return {
        "schema_version": "0.1.0",
        "model_card_id": "PMCARD-TEST-001",
        "status": "provisional",
        "roadmap_gap_refs": ["GAP-WORK-003"],
        "model": {
            "name": "test model",
            "version": "1",
            "model_type": "analytical",
            "description_ja": "検証用",
            "description_en": "test",
            "equation_ja": "y=x",
            "equation_en": "y=x",
        },
        "inputs": [{"quantity_id": "IN-X", "name_ja": "入力", "name_en": "input", "unit": "s"}],
        "outputs": [{"quantity_id": "OUT-TIME", "name_ja": "時間", "name_en": "time", "unit": "s"}],
        "applicability": {
            "architecture_ids": ["ARCH-A", "ARCH-B"],
            "workload_ids": ["WORK-A", "WORK-B"],
            "scale_min": 1,
            "scale_max": 1024,
            "exclusions_ja": "範囲外なし",
            "exclusions_en": "none in range",
        },
        "calibration_dataset_ids": ["DATA-CAL"],
        "validations": [
            {"measurement_id": "PMVAL-A", "dataset_id": "DATA-VAL-A", "system_id": "SYS-A", "workload_id": "WORK-A", "origin_group_id": "ORG-A", "output_id": "OUT-TIME", "predicted": 10.0, "observed": 10.5, "unit": "s", "absolute_error": 0.5, "relative_error": 0.5 / 10.5, "measurement_source_ids": ["SRC-A"]},
            {"measurement_id": "PMVAL-B", "dataset_id": "DATA-VAL-B", "system_id": "SYS-B", "workload_id": "WORK-B", "origin_group_id": "ORG-B", "output_id": "OUT-TIME", "predicted": 20.0, "observed": 21.0, "unit": "s", "absolute_error": 1.0, "relative_error": 1.0 / 21.0, "measurement_source_ids": ["SRC-B"]},
        ],
        "acceptance": {
            "minimum_systems": 2,
            "minimum_workloads": 2,
            "minimum_origin_groups": 2,
            "metric_thresholds": [{"output_id": "OUT-TIME", "maximum_relative_error": 0.05}],
        },
        "provenance": {
            "created_at": "2026-08-26T00:00:00Z",
            "base_commit": "a" * 40,
            "agent_id": "AGT-TEST",
            "model_identity": "test-model",
            "skill_version": "test@1",
            "evidence_refs": ["SRC-A", "SRC-B"],
        },
        "consensus_status": "incomplete",
    }


class PerformanceModelCardTests(unittest.TestCase):
    def test_reproducible_multi_origin_card_is_only_consensus_candidate(self):
        result = evaluate(valid_card())
        self.assertTrue(result["candidate_ready_for_consensus"])
        self.assertTrue(result["gap_remains_open"])
        self.assertEqual(2, result["counts"]["systems"])
        self.assertEqual(2, result["counts"]["origin_groups"])

    def test_calibration_leakage_and_bad_error_fail_closed(self):
        card = copy.deepcopy(valid_card())
        card["validations"][0]["dataset_id"] = "DATA-CAL"
        card["validations"][1]["absolute_error"] = 0.1
        result = evaluate(card)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("overlaps calibration" in error for error in result["calculation_errors"]))
        self.assertTrue(any("not reproducible" in error for error in result["calculation_errors"]))

    def test_single_origin_does_not_meet_declared_minimum(self):
        card = copy.deepcopy(valid_card())
        card["validations"][1]["origin_group_id"] = "ORG-A"
        result = evaluate(card)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any(error.startswith("origin_groups:") for error in result["calculation_errors"]))

    def test_duplicate_outputs_and_invalid_scale_fail_closed(self):
        card = copy.deepcopy(valid_card())
        card["outputs"].append(copy.deepcopy(card["outputs"][0]))
        card["applicability"]["scale_max"] = card["applicability"]["scale_min"]
        result = evaluate(card)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any(error.startswith("outputs:") for error in result["calculation_errors"]))
        self.assertTrue(any(error.startswith("applicability:") for error in result["calculation_errors"]))


if __name__ == "__main__":
    unittest.main()
