#!/usr/bin/env python3
"""Validate a comparable compiler capability matrix for GAP-PORT-001."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:  # pragma: no cover
    Draft202012Validator = None
    FormatChecker = None


REQUIRED_VENDORS = {"gcc", "llvm", "fujitsu", "intel", "nvidia", "amd"}
TEST_BASES = {"compile-test", "conformance-test", "application-test"}


def _duplicates(values: list[str]) -> set[str]:
    return {value for value in values if values.count(value) > 1}


def evaluate(matrix: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    acceptance = matrix["acceptance"]
    required_vendors = set(matrix["required_vendors"])
    if required_vendors != REQUIRED_VENDORS:
        errors.append(
            "required_vendors: must contain exactly GCC, LLVM, Fujitsu, Intel, NVIDIA, and AMD"
        )

    feature_ids = [item["feature_id"] for item in matrix["required_features"]]
    required_features = set(feature_ids)
    for value in sorted(_duplicates(feature_ids)):
        errors.append(f"required_features: duplicate feature_id {value}")

    environments = matrix["test_environments"]
    environment_ids = [item["environment_id"] for item in environments]
    known_environments = set(environment_ids)
    for value in sorted(_duplicates(environment_ids)):
        errors.append(f"test_environments: duplicate environment_id {value}")
    if len(environments) < acceptance["minimum_test_environments"]:
        errors.append("test_environments: below the declared minimum")
    origin_groups = {item["origin_group_id"] for item in environments}
    if len(origin_groups) < acceptance["minimum_origin_groups"]:
        errors.append("test_environments: origin-group diversity is below the declared minimum")

    implementations = matrix["implementations"]
    implementation_ids = [item["implementation_id"] for item in implementations]
    vendors = [item["vendor"] for item in implementations]
    for value in sorted(_duplicates(implementation_ids)):
        errors.append(f"implementations: duplicate implementation_id {value}")
    for value in sorted(_duplicates(vendors)):
        errors.append(f"implementations: duplicate vendor {value}")
    if set(vendors) != required_vendors or len(vendors) < acceptance["minimum_vendors"]:
        errors.append("implementations: must cover every required vendor exactly once")

    source_refs = set(matrix["source_refs"])
    tested_vendors: set[str] = set()
    for implementation in implementations:
        implementation_id = implementation["implementation_id"]
        results = implementation["feature_results"]
        result_ids = [item["feature_id"] for item in results]
        for value in sorted(_duplicates(result_ids)):
            errors.append(f"{implementation_id}: duplicate feature result {value}")
        if set(result_ids) != required_features:
            errors.append(
                f"{implementation_id}: feature grid mismatch; "
                f"missing={sorted(required_features - set(result_ids))}, "
                f"extra={sorted(set(result_ids) - required_features)}"
            )
        for result in results:
            feature_id = result["feature_id"]
            if not set(result["evidence_refs"]) <= source_refs:
                errors.append(f"{implementation_id}/{feature_id}: unknown evidence reference")
            basis = result["verification_basis"]
            referenced_environments = set(result["environment_ids"])
            if not referenced_environments <= known_environments:
                errors.append(f"{implementation_id}/{feature_id}: unknown test environment")
            if basis in TEST_BASES:
                tested_vendors.add(implementation["vendor"])
                if not referenced_environments or not result["test_artifact_ref"]:
                    errors.append(f"{implementation_id}/{feature_id}: tested result lacks reproducible artifact")
            elif referenced_environments or result["test_artifact_ref"] is not None:
                errors.append(f"{implementation_id}/{feature_id}: documentation-only result cites a test")
            if acceptance["require_no_unknown"] and result["support_status"] == "unknown":
                errors.append(f"{implementation_id}/{feature_id}: support status remains unknown")

    if len(tested_vendors) < acceptance["minimum_tested_vendors"]:
        errors.append(
            f"tested vendors: {len(tested_vendors)} is below {acceptance['minimum_tested_vendors']}"
        )

    return {
        "matrix_id": matrix["matrix_id"],
        "roadmap_gap_refs": matrix["roadmap_gap_refs"],
        "counts": {
            "vendors": len(set(vendors)),
            "required_features": len(required_features),
            "test_environments": len(environments),
            "origin_groups": len(origin_groups),
            "tested_vendors": len(tested_vendors),
        },
        "calculation_errors": errors,
        "candidate_ready_for_consensus": not errors,
        "consensus_status": matrix["consensus_status"],
        "gaps_remain_open": True,
        "note": (
            "Validator success only makes the matrix eligible for independent review. "
            "It does not convert documentation into conformance, close GAP-PORT-001, "
            "or establish a procurement ranking."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("matrix", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.matrix.read_text(encoding="utf-8"))
    if Draft202012Validator is None:
        parser.error("jsonschema is required; install requirements-validation.txt")
    schema_path = Path(__file__).resolve().parents[1] / "schemas" / "portability-capability-matrix.schema.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    schema_errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(payload),
        key=lambda item: list(item.path),
    )
    if schema_errors:
        for error in schema_errors:
            location = "/".join(str(item) for item in error.absolute_path) or "$"
            print(f"{location}: {error.message}")
        return 1
    result = evaluate(payload)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["candidate_ready_for_consensus"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
