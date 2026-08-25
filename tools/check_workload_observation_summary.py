#!/usr/bin/env python3
"""Validate privacy and comparability of an aggregate workload observation."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:  # pragma: no cover
    Draft202012Validator = None
    FormatChecker = None


SENSITIVE_STRING_PATTERNS = (
    ("email address", re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")),
    ("home or scratch path", re.compile(r"(?:^|\s)(?:/Users/|/home/|/scratch/|[A-Za-z]:\\\\Users\\\\)")),
    ("credential-like assignment", re.compile(r"\b(?:token|password|secret|api[_-]?key)\s*[:=]", re.IGNORECASE)),
)


def _scan_strings(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            errors.extend(_scan_strings(item, f"{path}/{key}"))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(_scan_strings(item, f"{path}/{index}"))
    elif isinstance(value, str):
        for name, pattern in SENSITIVE_STRING_PATTERNS:
            if pattern.search(value):
                errors.append(f"{path}: contains {name}")
    return errors


def evaluate(summary: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = _scan_strings(summary)
    privacy = summary["privacy_release"]
    acceptance = summary["acceptance"]
    observations = summary["observations"]

    start = date.fromisoformat(summary["scope"]["period_start"])
    end = date.fromisoformat(summary["scope"]["period_end"])
    observation_days = (end - start).days + 1
    if observation_days < acceptance["minimum_observation_days"]:
        errors.append(
            f"scope: {observation_days} observation days is below "
            f"{acceptance['minimum_observation_days']}"
        )

    observation_ids = [item["observation_id"] for item in observations]
    system_ids = [item["system_id"] for item in observations]
    if len(observation_ids) != len(set(observation_ids)):
        errors.append("observations: observation_id values must be unique")
    if len(system_ids) != len(set(system_ids)):
        errors.append("observations: system_id values must be unique")

    institutions = {item["institution_id"] for item in observations}
    origins = {item["origin_group_id"] for item in observations}
    if len(institutions) < acceptance["minimum_institutions"]:
        errors.append("observations: institution diversity is below acceptance minimum")
    if len(origins) < acceptance["minimum_origin_groups"]:
        errors.append("observations: origin-group diversity is below acceptance minimum")

    required_dimensions = set(acceptance["required_dimensions"])
    for observation in observations:
        observation_id = observation["observation_id"]
        if observation["population_rounding_base"] != privacy["rounding_base"]:
            errors.append(f"{observation_id}: population rounding base differs from release policy")
        if observation["rounded_population_jobs"] % privacy["rounding_base"]:
            errors.append(f"{observation_id}: population count is not rounded to the declared base")

        distributions = observation["distributions"]
        dimension_ids = [item["dimension_id"] for item in distributions]
        if len(dimension_ids) != len(set(dimension_ids)):
            errors.append(f"{observation_id}: dimension_id values must be unique")
        missing = required_dimensions - set(dimension_ids)
        if missing:
            errors.append(f"{observation_id}: missing required dimensions {sorted(missing)}")

        for distribution in distributions:
            dimension_id = distribution["dimension_id"]
            bins = distribution["bins"]
            bin_ids = [item["bin_id"] for item in bins]
            if len(bin_ids) != len(set(bin_ids)):
                errors.append(f"{observation_id}/{dimension_id}: bin_id values must be unique")
            suppressed = [item for item in bins if item["suppressed"]]
            if suppressed and len(suppressed) < 2:
                errors.append(
                    f"{observation_id}/{dimension_id}: at least two cells must be hidden "
                    "for complementary suppression"
                )
            for item in bins:
                count = item["rounded_job_count"]
                if count is None:
                    continue
                if count < privacy["minimum_cell_count"]:
                    errors.append(
                        f"{observation_id}/{dimension_id}/{item['bin_id']}: "
                        "published count is below minimum cell count"
                    )
                if count % privacy["rounding_base"]:
                    errors.append(
                        f"{observation_id}/{dimension_id}/{item['bin_id']}: "
                        "published count is not rounded to the declared base"
                    )
                lower = item["lower_bound"]
                upper = item["upper_bound"]
                if lower is not None and upper is not None and upper <= lower:
                    errors.append(
                        f"{observation_id}/{dimension_id}/{item['bin_id']}: "
                        "upper_bound must exceed lower_bound"
                    )

    publication = summary["publication"]
    if publication["publication_approved"]:
        if not publication["publication_decision_id"] or not publication["human_approval_directive_id"]:
            errors.append("publication: approval requires decision and human Directive IDs")
    elif publication["publication_decision_id"] or publication["human_approval_directive_id"]:
        errors.append("publication: IDs must be null before approval")

    if summary["status"] == "accepted" and summary["consensus_status"] != "accepted":
        errors.append("status: accepted requires accepted Consensus")

    return {
        "summary_id": summary["summary_id"],
        "roadmap_gap_refs": summary["roadmap_gap_refs"],
        "counts": {
            "observation_days": observation_days,
            "institutions": len(institutions),
            "origin_groups": len(origins),
            "systems": len(set(system_ids)),
            "distributions": sum(len(item["distributions"]) for item in observations),
        },
        "calculation_errors": errors,
        "candidate_ready_for_consensus": not errors,
        "consensus_status": summary["consensus_status"],
        "gaps_remain_open": True,
        "note": (
            "Validator success establishes only a privacy/comparability candidate. "
            "It does not prove national representativeness or close a Coverage Gap."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("summary", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.summary.read_text(encoding="utf-8"))
    if Draft202012Validator is None:
        parser.error("jsonschema is required; install requirements-validation.txt")
    schema_path = Path(__file__).resolve().parents[1] / "schemas" / "workload-observation-summary.schema.json"
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
