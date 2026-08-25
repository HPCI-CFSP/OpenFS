from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from tools.check_benchmark_result_bundle import evaluate


ROOT = Path(__file__).resolve().parents[1]
DIGEST_A = "sha256:" + "a" * 64
DIGEST_B = "sha256:" + "b" * 64


def valid_bundle():
    configurations = []
    runs = []
    aggregates = []
    trials = []
    for index, (config_id, institution, origin, elapsed_base, energy_base) in enumerate(
        (("CFG-A", "INST-A", "ORG-A", 10.0, 100.0), ("CFG-B", "INST-B", "ORG-B", 20.0, 200.0))
    ):
        configurations.append(
            {
                "configuration_id": config_id,
                "institution_id": institution,
                "origin_group_id": origin,
                "system_id": f"SYS-{index}",
                "hardware": {"cpu": "CPU", "accelerator": "none", "memory": "DDR", "interconnect": "fabric", "node_count": 2},
                "software": {"os": "Linux", "kernel": "6", "compiler": "cc 1", "mpi": f"MPI-{index}", "fabric_provider": f"provider-{index}", "libraries": ["lib 1"], "environment_digest": DIGEST_A},
                "measurement_boundary": "node",
            }
        )
        for repetition in range(1, 4):
            runs.append(
                {
                    "run_id": f"RUN-{config_id[-1]}-{repetition}",
                    "configuration_id": config_id,
                    "repetition": repetition,
                    "started_at": f"2026-08-25T0{repetition}:00:00Z",
                    "ended_at": f"2026-08-25T0{repetition}:01:00Z",
                    "success": True,
                    "correctness_error": 0.001,
                    "correctness_pass": True,
                    "elapsed_seconds": elapsed_base + repetition - 1,
                    "energy_joules": energy_base + 10 * (repetition - 1),
                    "result_digest": DIGEST_A,
                    "log_digest": DIGEST_B,
                }
            )
        aggregates.append(
            {
                "configuration_id": config_id,
                "valid_run_count": 3,
                "median_elapsed_seconds": elapsed_base + 1,
                "median_energy_joules": energy_base + 10,
            }
        )
        trials.append(
            {
                "trial_id": f"FAIL-{config_id[-1]}",
                "configuration_id": config_id,
                "fault_type": "process termination",
                "detected": True,
                "recovered": True,
                "correct_result": True,
                "recovery_seconds": 3.0,
                "log_digest": DIGEST_B,
            }
        )
    return {
        "schema_version": "0.1.0",
        "bundle_id": "BMR-TEST-001",
        "status": "provisional",
        "roadmap_gap_refs": ["GAP-COMP-004"],
        "campaign": {"name": "test", "version": "1", "objective_ja": "比較", "objective_en": "comparison", "protocol_uri": "https://example.org/protocol", "protocol_digest": DIGEST_A},
        "workload": {"workload_id": "WORK-A", "version": "1", "input_id": "INPUT-A", "input_digest": DIGEST_A, "scale": "2 nodes", "precision": "FP64", "correctness_metric": "relative error", "correctness_tolerance": 0.01},
        "configurations": configurations,
        "runs": runs,
        "aggregates": aggregates,
        "failure_recovery_trials": trials,
        "porting_records": [],
        "acceptance": {"minimum_configurations": 2, "minimum_runs_per_configuration": 3, "minimum_institutions": 2, "minimum_origin_groups": 2, "maximum_correctness_error": 0.01},
        "provenance": {"created_at": "2026-08-25T00:00:00Z", "base_commit": "a" * 40, "agent_id": "AGT-TEST", "model_identity": "test-model", "harness_repository": "https://example.org/harness", "harness_commit": "b" * 40, "raw_data_uri": "https://example.org/raw.json", "raw_data_digest": DIGEST_B},
        "consensus_status": "incomplete",
    }


class BenchmarkResultBundleTests(unittest.TestCase):
    def test_valid_multi_institution_bundle_is_only_consensus_candidate(self):
        payload = valid_bundle()
        schema = json.loads((ROOT / "schemas/benchmark-result-bundle.schema.json").read_text())
        self.assertEqual([], list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload)))
        result = evaluate(payload)
        self.assertTrue(result["candidate_ready_for_consensus"])
        self.assertTrue(result["gaps_remain_open"])

    def test_bad_aggregate_duplicate_repetition_and_correctness_fail_closed(self):
        payload = copy.deepcopy(valid_bundle())
        payload["aggregates"][0]["median_elapsed_seconds"] = 99
        payload["runs"][1]["repetition"] = 1
        payload["runs"][2]["correctness_pass"] = False
        result = evaluate(payload)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("duplicate repetition" in error for error in result["calculation_errors"]))
        self.assertTrue(any("correctness_pass" in error for error in result["calculation_errors"]))
        self.assertTrue(any("median_elapsed_seconds" in error for error in result["calculation_errors"]))

    def test_energy_and_failure_trials_are_required_for_compute_gap(self):
        payload = copy.deepcopy(valid_bundle())
        payload["runs"][0]["energy_joules"] = None
        payload["failure_recovery_trials"] = []
        result = evaluate(payload)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("system energy" in error for error in result["calculation_errors"]))
        self.assertEqual(2, sum("failure/recovery trial" in error for error in result["calculation_errors"]))

    def test_loose_correctness_mixed_boundaries_and_failed_ras_fail_closed(self):
        payload = copy.deepcopy(valid_bundle())
        payload["acceptance"]["maximum_correctness_error"] = 0.02
        payload["configurations"][1]["measurement_boundary"] = "rack"
        payload["failure_recovery_trials"][0]["correct_result"] = False
        result = evaluate(payload)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("workload tolerance" in error for error in result["calculation_errors"]))
        self.assertTrue(any("boundaries must match" in error for error in result["calculation_errors"]))
        self.assertTrue(any("no successful" in error for error in result["calculation_errors"]))

    def test_portability_gap_specific_requirements_fail_closed(self):
        payload = copy.deepcopy(valid_bundle())
        payload["roadmap_gap_refs"] = ["GAP-PORT-004", "GAP-PORT-006"]
        for configuration in payload["configurations"]:
            configuration["software"]["mpi"] = "one-mpi"
            configuration["software"]["fabric_provider"] = "one-provider"
        result = evaluate(payload)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any(error.startswith("porting_records:") for error in result["calculation_errors"]))
        self.assertTrue(any("two MPI" in error for error in result["calculation_errors"]))
        self.assertTrue(any("two fabric" in error for error in result["calculation_errors"]))


if __name__ == "__main__":
    unittest.main()
