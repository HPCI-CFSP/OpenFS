#!/usr/bin/env python3
"""Validate AI-agent evaluation controls and compute review-candidate readiness."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
except ImportError:  # pragma: no cover
    Draft202012Validator = None
    FormatChecker = None


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def evaluate(bundle: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    runs = bundle["runs"]
    protocol = bundle["protocol"]
    boundary = bundle["execution_boundary"]
    dataset = bundle["dataset_control"]
    acceptance = bundle["acceptance"]

    run_ids = [run["run_id"] for run in runs]
    repetitions = [run["repetition"] for run in runs]
    if len(run_ids) != len(set(run_ids)):
        errors.append("runs: run_id values must be unique")
    if len(repetitions) != len(set(repetitions)):
        errors.append("runs: repetition values must be unique")
    if len(runs) < protocol["minimum_repetitions"]:
        errors.append("runs: fewer runs than protocol.minimum_repetitions")

    total_tokens = 0
    total_cost = 0.0
    policy_passes = 0
    scores: list[float] = []
    for run in runs:
        run_id = run["run_id"]
        if _timestamp(run["ended_at"]) <= _timestamp(run["started_at"]):
            errors.append(f"{run_id}: ended_at must be after started_at")
        usage = run["usage"]
        run_tokens = usage["input_tokens"] + usage["output_tokens"]
        total_tokens += run_tokens
        total_cost += usage["cost"]
        if run_tokens > protocol["budget"]["maximum_total_tokens"]:
            errors.append(f"{run_id}: token use exceeds the per-run budget")
        if usage["wall_seconds"] > protocol["budget"]["maximum_wall_seconds"]:
            errors.append(f"{run_id}: wall time exceeds the per-run budget")
        if usage["cost"] > protocol["budget"]["maximum_cost"]:
            errors.append(f"{run_id}: cost exceeds the per-run budget")
        policy_passes += int(run["policy_pass"])
        scores.append(run["outcome_score"])

    policy_pass_rate = policy_passes / len(runs)
    mean_score = sum(scores) / len(scores)
    if acceptance["minimum_policy_pass_rate"] != 1.0:
        errors.append("acceptance: minimum_policy_pass_rate must be 1.0")
    if policy_pass_rate < 1.0:
        errors.append("runs: policy pass rate is below the acceptance threshold")
    score_pass = (
        mean_score >= acceptance["score_threshold"]
        if bundle["benchmark"]["higher_is_better"]
        else mean_score <= acceptance["score_threshold"]
    )
    if not score_pass:
        errors.append("runs: mean outcome score does not meet the acceptance threshold")

    if boundary["privilege_level"] != "unprivileged":
        errors.append("execution_boundary: privileged execution is not review-candidate eligible")
    if boundary["outbound_path"] == "direct":
        errors.append("execution_boundary: direct outbound network access is not eligible")
    if boundary["network_access"] == "public-web" and boundary["outbound_path"] not in {
        "safe-fetch-broker",
        "managed-browser",
    }:
        errors.append("execution_boundary: public web access requires a controlled outbound path")
    if acceptance["require_hidden_holdout"] and dataset["test_visibility"] != "hidden":
        errors.append("dataset_control: a hidden test partition is required")
    if dataset["dynamic_web"] and dataset.get("web_receipt_bundle_digest") is None:
        errors.append("dataset_control: dynamic web evaluation requires retrieval receipts")
    if acceptance["require_independent_evaluator"]:
        if protocol["evaluator"]["origin_group"] == bundle["provenance"]["author_origin_group"]:
            errors.append("protocol: evaluator origin group is not independent of the author")

    if bundle["status"] == "accepted" and bundle["consensus_status"] != "accepted":
        errors.append("status: accepted requires accepted Consensus")
    if bundle["consensus_status"] == "accepted" and not bundle.get("consensus_receipt_ids"):
        errors.append("consensus_status: accepted requires Consensus Receipt IDs")

    candidate_ready = not errors
    return {
        "evaluation_id": bundle["evaluation_id"],
        "counts": {
            "runs": len(runs),
            "policy_passes": policy_passes,
            "total_tokens": total_tokens,
        },
        "metrics": {
            "mean_outcome_score": mean_score,
            "policy_pass_rate": policy_pass_rate,
            "total_cost_usd": total_cost,
        },
        "control_errors": errors,
        "candidate_ready_for_consensus": candidate_ready,
        "consensus_status": bundle["consensus_status"],
        "note": (
            "Validator success only makes the evaluation eligible for independent Consensus review; "
            "it does not establish safety, generalization, or publication approval."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    payload = json.loads(args.bundle.read_text(encoding="utf-8"))
    if Draft202012Validator is None:
        parser.error("jsonschema is required; install requirements-validation.txt")
    schema_path = Path(__file__).resolve().parents[1] / "schemas" / "agent-evaluation-bundle.schema.json"
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
