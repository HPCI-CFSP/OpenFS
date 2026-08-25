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


def committed_json(root: Path, commit: str, path: str) -> dict[str, Any] | None:
    result = subprocess.run(
        ["git", "show", f"{commit}:{path}"], cwd=root,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def evaluate(root: Path, manifest_path: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    integrity_errors: list[str] = []
    for artifact in manifest["artifact_manifest"]:
        actual = committed_digest(root, manifest["base_commit"], artifact["path"])
        if actual is None:
            integrity_errors.append(f"artifact_missing_at_base_commit:{artifact['path']}")
        elif actual != artifact["sha256"]:
            integrity_errors.append(f"artifact_digest_mismatch:{artifact['path']}")

    registry_path = "config/agent-registry.json"
    registry = committed_json(root, manifest["base_commit"], registry_path)
    registry_digest = committed_digest(root, manifest["base_commit"], registry_path)
    if registry is None or registry_digest is None:
        integrity_errors.append("agent_registry_unavailable")
        registered_agents: dict[str, dict[str, Any]] = {}
    else:
        registered_agents = {
            agent["agent_id"]: agent
            for agent in registry.get("agents", [])
            if agent.get("agent_id")
        }

    assessment_dir = root / manifest["submission"]["assessment_directory"]
    reviews = [read_json(path) for path in sorted(assessment_dir.glob("*.json"))]
    expected_units = {unit["unit_id"] for unit in manifest["review_units"]}
    primary_sources_by_unit: dict[str, dict[str, tuple[str, str]]] = {}
    for unit in manifest["review_units"]:
        if unit["kind"] != "roadmap":
            continue
        roadmap_paths = [
            path for path in unit["artifact_paths"]
            if path.startswith("knowledge/public/roadmaps/") and path.endswith(".json")
        ]
        roadmap = committed_json(root, manifest["base_commit"], roadmap_paths[0]) if len(roadmap_paths) == 1 else None
        if roadmap is None:
            integrity_errors.append(f"roadmap_source_registry_unavailable:{unit['unit_id']}")
            primary_sources_by_unit[unit["unit_id"]] = {}
        else:
            primary_sources_by_unit[unit["unit_id"]] = {
                source["source_id"]: (source["url"], source["source_class"])
                for source in roadmap["sources"]
                if source["source_class"] != "openfs-governance"
            }
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
        reviewer_identity = review.get("reviewer", {})
        registered = registered_agents.get(agent_id)
        if registered is None:
            review_errors.append(f"reviewer_not_registered:{review_id}:{agent_id}")
        else:
            if registered.get("enabled") is not True:
                review_errors.append(f"reviewer_not_enabled:{review_id}:{agent_id}")
            expected_identity = {
                "role": registered.get("role"),
                "provider": registered.get("provider"),
                "model_family": registered.get("model_family"),
                "prompt_profile": registered.get("prompt_profile"),
                "independence_group": registered.get("agent_independence_group"),
            }
            observed_identity = {
                key: reviewer_identity.get(key) for key in expected_identity
            }
            if observed_identity != expected_identity:
                review_errors.append(f"reviewer_registry_identity_mismatch:{review_id}:{agent_id}")
            if registered.get("network_access") != "public-web":
                review_errors.append(f"reviewer_lacks_public_web:{review_id}:{agent_id}")
            if registered.get("data_clearance") != "public":
                review_errors.append(f"reviewer_clearance_mismatch:{review_id}:{agent_id}")
            if "assessments" not in registered.get("write_scope", []):
                review_errors.append(f"reviewer_write_scope_mismatch:{review_id}:{agent_id}")
        if review.get("registry_snapshot_digest") != registry_digest:
            review_errors.append(f"agent_registry_digest_mismatch:{review_id}")
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
        primary_checks = review.get("primary_source_checks", [])
        seen_primary_checks: set[tuple[str, str]] = set()
        conclusive_units: set[str] = set()
        for check in primary_checks:
            unit_id = check.get("unit_id", "<missing>")
            source_id = check.get("source_id", "<missing>")
            key = (unit_id, source_id)
            if key in seen_primary_checks:
                review_errors.append(f"duplicate_primary_source_check:{review_id}:{unit_id}:{source_id}")
            seen_primary_checks.add(key)
            registered = primary_sources_by_unit.get(unit_id)
            if registered is None:
                review_errors.append(f"primary_source_unit_mismatch:{review_id}:{unit_id}")
                continue
            if registered.get(source_id) != (check.get("source_url"), check.get("source_class")):
                review_errors.append(f"primary_source_identity_mismatch:{review_id}:{unit_id}:{source_id}")
                continue
            if check.get("outcome") in {"supports", "contradicts"}:
                conclusive_units.add(unit_id)
        if manifest["consensus_policy"]["require_primary_source"]:
            for unit_id in primary_sources_by_unit:
                if unit_id not in conclusive_units:
                    review_errors.append(f"primary_source_coverage_mismatch:{review_id}:{unit_id}")
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
        "support_model_families": len({(review["reviewer"]["provider"], review["reviewer"]["model_family"]) for review in support}),
        "support_providers": len({review["reviewer"]["provider"] for review in support}),
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
    if counts["support_model_families"] < policy["minimum_model_families"]:
        unmet.append("minimum_model_families")
    if counts["support_providers"] < policy["minimum_providers"]:
        unmet.append("minimum_providers")
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
