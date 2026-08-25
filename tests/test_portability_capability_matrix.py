from __future__ import annotations

import copy
import unittest

from tools.check_portability_capability_matrix import evaluate


VENDORS = ["gcc", "llvm", "fujitsu", "intel", "nvidia", "amd"]


def valid_matrix():
    environments = [
        {
            "environment_id": "ENV-HPCI-A",
            "institution_id": "CENTER-A",
            "origin_group_id": "ORG-A",
            "system": "System A",
            "operating_system": "Linux A",
            "harness_commit": "a" * 40,
        },
        {
            "environment_id": "ENV-HPCI-B",
            "institution_id": "CENTER-B",
            "origin_group_id": "ORG-B",
            "system": "System B",
            "operating_system": "Linux B",
            "harness_commit": "b" * 40,
        },
    ]
    source_refs = [f"SRC-{vendor.upper()}" for vendor in VENDORS]
    implementations = []
    for index, vendor in enumerate(VENDORS):
        environment_id = environments[index % 2]["environment_id"]
        implementations.append(
            {
                "implementation_id": f"IMPL-{vendor.upper()}",
                "vendor": vendor,
                "compiler_name": vendor,
                "compiler_version": "test-version",
                "backend_targets": ["cpu"],
                "feature_results": [
                    {
                        "feature_id": "FEAT-OPENMP-TARGET",
                        "support_status": "supported",
                        "verification_basis": "conformance-test",
                        "evidence_refs": [f"SRC-{vendor.upper()}"],
                        "environment_ids": [environment_id],
                        "test_artifact_ref": f"artifacts/{vendor}/result.json",
                    }
                ],
            }
        )
    return {
        "schema_version": "0.1.0",
        "matrix_id": "PCM-TEST-001",
        "status": "candidate",
        "as_of": "2026-08-26",
        "roadmap_gap_refs": ["GAP-PORT-001"],
        "required_vendors": VENDORS,
        "required_features": [
            {
                "feature_id": "FEAT-OPENMP-TARGET",
                "name": "OpenMP target",
                "standard": "openmp",
                "specification_version": "6.1",
            }
        ],
        "test_environments": environments,
        "implementations": implementations,
        "source_refs": source_refs,
        "acceptance": {
            "minimum_vendors": 6,
            "minimum_tested_vendors": 6,
            "minimum_test_environments": 2,
            "minimum_origin_groups": 2,
            "require_complete_feature_grid": True,
            "require_no_unknown": True,
        },
        "consensus_status": "incomplete",
    }


class PortabilityCapabilityMatrixTests(unittest.TestCase):
    def test_complete_matrix_is_candidate_only(self):
        result = evaluate(valid_matrix())
        self.assertTrue(result["candidate_ready_for_consensus"])
        self.assertEqual([], result["calculation_errors"])
        self.assertEqual(6, result["counts"]["tested_vendors"])
        self.assertTrue(result["gaps_remain_open"])

    def test_missing_vendor_fails_closed(self):
        matrix = valid_matrix()
        matrix["implementations"].pop()
        result = evaluate(matrix)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("every required vendor" in item for item in result["calculation_errors"]))

    def test_inconsistent_feature_grid_fails_closed(self):
        matrix = valid_matrix()
        matrix["implementations"][0]["feature_results"] = []
        result = evaluate(matrix)
        self.assertFalse(result["candidate_ready_for_consensus"])
        self.assertTrue(any("feature grid mismatch" in item for item in result["calculation_errors"]))

    def test_documentation_only_does_not_count_as_test(self):
        matrix = copy.deepcopy(valid_matrix())
        result = matrix["implementations"][0]["feature_results"][0]
        result["verification_basis"] = "vendor-documentation"
        result["environment_ids"] = []
        result["test_artifact_ref"] = None
        outcome = evaluate(matrix)
        self.assertFalse(outcome["candidate_ready_for_consensus"])
        self.assertTrue(any("tested vendors" in item for item in outcome["calculation_errors"]))


if __name__ == "__main__":
    unittest.main()
