#!/usr/bin/env python3
"""Evaluate review-package integrity and high-impact Consensus readiness."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def committed_digest(root: Path, commit: str, path: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"{commit}:{path}"], cwd=root,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return hashlib.sha256(result.stdout).hexdigest() if result.returncode == 0 else None


def evaluate(root: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    integrity_errors: list[str] = []
    for artifact in manifest["artifact_manifest"]:
        actual = committed_digest(root, manifest["base_commit"], artifact["path"])
        if actual is None:
            integrity_errors.append(f"artifact_missing_at_base_commit:{artifact['path']}")
        elif actual != artifact["sha256"]:
            integrity_errors.append(f"artifact_digest_mismatch:{artifact['path']}")

    assessment_dir = root / manifest["submission"]["assessment_directory"]
    reviews = [read_json(path) for path in sorted(assessment_dir.glob("*.json"))]
    expected_units = {unit["unit_id"] for unit in manifest["review_units"]}
    seen_ids: set[str] = set()
    seen_agents: set[str] = set()
    eligible: list[dict[str, Any]] = []
    disallowed = set(manifest["independence_requirements"]["disallowed_as_independent"])
    for review in reviews:
        review_errors: list[str] = []
        review_id = review.get("review_id", "<missing>")
        if review_id in seen_ids:
            review_errors.append(f"duplicate_review_id:{review_id}")
        seen_ids.add(review_id)
        agent_id = review.get("reviewer", {}).get("agent_id", "<missing>")
        if agent_id in seen_agents:
            review_errors.append(f"duplicate_reviewer_agent:{agent_id}")
        seen_agents.add(agent_id)
        if review.get("package_id") != manifest["package_id"]:
            review_errors.append(f"package_id_mismatch:{review_id}")
        if review.get("base_commit") != manifest["base_commit"]:
            review_errors.append(f"base_commit_mismatch:{review_id}")
        assessments = review.get("unit_assessments", [])
        assessed = [item.get("unit_id") for item in assessments]
        if len(assessed) != len(expected_units) or set(assessed) != expected_units:
            review_errors.append(f"review_unit_coverage_mismatch:{review_id}")
        required_checks = {
            unit["unit_id"]: set(unit["required_checks"])
            for unit in manifest["review_units"]
        }
        for assessment in assessments:
            unit_id = assessment.get("unit_id")
            if unit_id in required_checks and set(assessment.get("checks", {})) != required_checks[unit_id]:
                review_errors.append(f"required_check_coverage_mismatch:{review_id}:{unit_id}")
        if review.get("reviewer", {}).get("independence_group") in disallowed:
            review_errors.append(f"disallowed_independence_group:{review_id}")
        integrity_errors.extend(review_errors)
        if not review_errors:
            eligible.append(review)

    support = [review for review in eligible if review.get("overall_verdict") == "support"]
    critical_objections = sum(
        len(review.get("critical_objections", []))
        + sum(
            objection.get("severity") == "critical"
            for unit in review.get("unit_assessments", [])
            for objection in unit.get("objections", [])
        )
        for review in eligible
    )
    counts = {
        "assessments": len(eligible),
        "support": len(support),
        "support_independence_groups": len({review["reviewer"]["independence_group"] for review in support}),
        "support_origin_groups": len({review["reviewer"]["origin_group"] for review in support}),
        "critic_reviews": sum(review["reviewer"]["role"] == "critic" for review in eligible),
        "critical_objections": critical_objections,
    }
    policy = manifest["consensus_policy"]
    unmet: list[str] = []
    if counts["assessments"] < policy["minimum_assessments"]:
        unmet.append("minimum_assessments")
    if counts["support"] < policy["minimum_support"]:
        unmet.append("minimum_support")
    if counts["support_independence_groups"] < policy["minimum_support_independence_groups"]:
        unmet.append("minimum_support_independence_groups")
    if counts["support_origin_groups"] < policy["minimum_origin_groups"]:
        unmet.append("minimum_origin_groups")
    if policy["require_falsification_review"] and counts["critic_reviews"] < 1:
        unmet.append("falsification_review")
    if policy["block_on_critical_objection"] and critical_objections:
        unmet.append("critical_objection")
    if integrity_errors:
        unmet.append("package_integrity")
    status = "ready-for-human-decision" if not unmet else "incomplete"
    effect = (
        "Independent review thresholds are met; the artifact remains provisional until the required human decision is recorded."
        if status == "ready-for-human-decision"
        else "Consensus remains incomplete; no roadmap or scenario may be labeled accepted from this package."
    )
    return {
        "schema_version": "0.1.0",
        "package_id": manifest["package_id"],
        "base_commit": manifest["base_commit"],
        "evaluated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": status,
        "counts": counts,
        "unmet_requirements": sorted(set(unmet)),
        "integrity_errors": sorted(set(integrity_errors)),
        "effect": effect,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate(args.root, args.manifest)
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if not result["integrity_errors"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
