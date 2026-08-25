from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

from tools.check_workload_observation_summary import evaluate


ROOT = Path(__file__).resolve().parents[1]
DIGEST_A = "sha256:" + "a" * 64
DIGEST_B = "sha256:" + "b" * 64


def distribution(dimension: str, prefix: str):
    return {
        "dimension_id": dimension,
        "unit": "jobs",
        "bins": [
            {"bin_id": f"BIN-{prefix}-A", "label_ja": "区分A", "label_en": "Bin A", "lower_bound": 0, "upper_bound": 10, "rounded_job_count": 60, "suppressed": False, "suppression_reason": None},
            {"bin_id": f"BIN-{prefix}-B", "label_ja": "区分B", "label_en": "Bin B", "lower_bound": 10, "upper_bound": 100, "rounded_job_count": 40, "suppressed": False, "suppression_reason": None},
        ],
    }


def valid_summary():
    observations = []
    for suffix in ("A", "B"):
        observations.append(
            {
                "observation_id": f"OBS-{suffix}",
                "institution_id": f"INST-{suffix}",
                "origin_group_id": f"ORG-{suffix}",
                "system_id": f"SYS-{suffix}",
                "rounded_population_jobs": 100,
                "population_rounding_base": 5,
                "source_receipt_digest": DIGEST_A,
                "distributions": [
                    distribution("job-size-nodes", f"{suffix}-SIZE"),
                    distribution("walltime-seconds", f"{suffix}-TIME"),
                    distribution("application-domain", f"{suffix}-DOMAIN"),
                ],
            }
        )
    return {
        "schema_version": "0.1.0",
        "summary_id": "WOS-TEST-001",
        "status": "provisional",
        "roadmap_gap_refs": ["GAP-WORK-001"],
        "scope": {
            "objective_ja": "需要分布を比較する",
            "objective_en": "Compare demand distributions",
            "period_start": "2026-06-01",
            "period_end": "2026-06-30",
            "population_definition": "Completed and failed batch jobs in the period",
            "included_job_states": ["completed", "failed"],
            "excluded_job_states": ["test"],
        },
        "privacy_release": {
            "aggregation_inside_approved_boundary": True,
            "direct_identifiers_removed": True,
            "row_level_jobs_exported": False,
            "minimum_cell_count": 10,
            "rounding_base": 5,
            "small_cell_action": "suppress",
            "complementary_suppression": True,
            "free_text_exported": False,
            "source_data_classification": "internal-aggregate",
            "release_reviewer": "REVIEWER-PRIVACY-001",
        },
        "observations": observations,
        "acceptance": {
            "minimum_institutions": 2,
            "minimum_origin_groups": 2,
            "minimum_observation_days": 28,
            "required_dimensions": ["application-domain", "job-size-nodes", "walltime-seconds"],
        },
        "provenance": {
            "created_at": "2026-08-26T00:00:00Z",
            "base_commit": "a" * 40,
            "agent_id": "AGT-TEST",
            "model_identity": "test-model",
            "harness_repository": "https://example.org/harness",
            "harness_commit": "b" * 40,
            "aggregation_code_digest": DIGEST_A,
            "input_receipt_digest": DIGEST_B,
        },
        "publication": {
            "information_classification": "public-aggregate",
            "publication_approved": False,
            "publication_decision_id": None,
            "human_approval_directive_id": None,
        },
        "consensus_status": "incomplete",
    }


class WorkloadObservationSummaryTests(unittest.TestCase):
    def test_valid_summary_is_only_consensus_candidate(self):
        payload = valid_summary()
        schema = json.loads((ROOT / "schemas/workload-observation-summary.schema.json").read_text())
        self.assertEqual([], list(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload)))
        result = evaluate(payload)
        self.assertTrue(result["candidate_ready_for_consensus"])
        self.assertTrue(result["gaps_remain_open"])

    def test_short_window_and_single_origin_fail_closed(self):
        payload = copy.deepcopy(valid_summary())
        payload["scope"]["period_end"] = "2026-06-10"
        payload["observations"][1]["origin_group_id"] = "ORG-A"
        result = evaluate(payload)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("observation days" in error for error in result["calculation_errors"]))
        self.assertTrue(any("origin-group diversity" in error for error in result["calculation_errors"]))

    def test_small_and_unrounded_published_cells_fail_closed(self):
        payload = copy.deepcopy(valid_summary())
        bins = payload["observations"][0]["distributions"][0]["bins"]
        bins[0]["rounded_job_count"] = 5
        bins[1]["rounded_job_count"] = 42
        result = evaluate(payload)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("below minimum cell" in error for error in result["calculation_errors"]))
        self.assertTrue(any("not rounded" in error for error in result["calculation_errors"]))

    def test_single_suppressed_cell_fails_complementary_suppression(self):
        payload = copy.deepcopy(valid_summary())
        item = payload["observations"][0]["distributions"][0]["bins"][0]
        item.update({"rounded_job_count": None, "suppressed": True, "suppression_reason": "small cell"})
        result = evaluate(payload)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("complementary suppression" in error for error in result["calculation_errors"]))

    def test_missing_dimension_and_bad_interval_fail_closed(self):
        payload = copy.deepcopy(valid_summary())
        payload["observations"][0]["distributions"].pop()
        item = payload["observations"][1]["distributions"][0]["bins"][0]
        item["upper_bound"] = 0
        result = evaluate(payload)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("missing required dimensions" in error for error in result["calculation_errors"]))
        self.assertTrue(any("upper_bound" in error for error in result["calculation_errors"]))

    def test_publication_and_acceptance_states_fail_closed(self):
        payload = copy.deepcopy(valid_summary())
        payload["publication"]["publication_approved"] = True
        payload["status"] = "accepted"
        result = evaluate(payload)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("approval requires" in error for error in result["calculation_errors"]))
        self.assertTrue(any("accepted requires" in error for error in result["calculation_errors"]))

    def test_identifier_path_and_credential_strings_fail_closed(self):
        payload = copy.deepcopy(valid_summary())
        payload["scope"]["objective_en"] = "contact alice@example.org"
        payload["scope"]["population_definition"] = "input /home/alice/jobs"
        payload["scope"]["objective_ja"] = "token=exposed"
        result = evaluate(payload)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("email address" in error for error in result["calculation_errors"]))
        self.assertTrue(any("home or scratch path" in error for error in result["calculation_errors"]))
        self.assertTrue(any("credential-like" in error for error in result["calculation_errors"]))


if __name__ == "__main__":
    unittest.main()
