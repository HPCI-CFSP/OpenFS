#!/usr/bin/env python3
"""Evaluate review-package integrity and high-impact Consensus readiness."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from build_consensus_review_package import review_source_class


ROOT = Path(__file__).resolve().parents[1]
MAXIMUM_CLOCK_SKEW_SECONDS = 60


def parse_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("date-time must include an explicit UTC offset")
    return parsed.astimezone(timezone.utc)


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


def evaluate(
    root: Path,
    manifest_path: Path,
    *,
    evaluated_at: str | None = None,
    maximum_clock_skew_seconds: int = MAXIMUM_CLOCK_SKEW_SECONDS,
) -> dict[str, Any]:
    manifest_digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
    manifest = read_json(manifest_path)
    evaluated = parse_time(evaluated_at) if evaluated_at else datetime.now(timezone.utc)
    skew = timedelta(seconds=maximum_clock_skew_seconds)
    integrity_errors: list[str] = []
    try:
        package_created = parse_time(manifest["created_at"])
    except (KeyError, TypeError, ValueError):
        package_created = None
        integrity_errors.append("package_created_at_invalid")
    if package_created is not None and package_created > evaluated + skew:
        integrity_errors.append("package_created_after_evaluation_window")
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
    reviews: list[dict[str, Any]] = []
    review_file_digests: dict[str, str] = {}
    for path in sorted(assessment_dir.glob("*.json")):
        review = read_json(path)
        reviews.append(review)
        review_id = review.get("review_id", "<missing>")
        review_file_digests.setdefault(
            review_id,
            hashlib.sha256(path.read_bytes()).hexdigest(),
        )
    expected_units = {unit["unit_id"] for unit in manifest["review_units"]}
    required_primary_checks: dict[str, dict[str, set[tuple[str, str, str]]]] = {}
    for unit in manifest["review_units"]:
        if unit["unit_id"] == "CRU-TOPIC-DECISION-SUPPORT":
            artifact = committed_json(
                root,
                manifest["base_commit"],
                "knowledge/public/topic-decision-support.json",
            )
            review_source_classes = {
                "official-vendor": "vendor-official",
                "official-standard": "standards-body",
                "official-project": "project-official",
                "peer-reviewed": "academic-primary",
                "research-artifact": "research-organization",
            }
            expected = {
                source["source_id"]: {
                    (
                        source["source_id"],
                        source["url"],
                        review_source_classes[source["source_class"]],
                    )
                }
                for source in artifact["sources"]
            }
            declared = {
                requirement["selector"]: {
                    (
                        option["source_id"],
                        option["source_url"],
                        option["source_class"],
                    )
                    for option in requirement["source_options"]
                }
                for requirement in unit.get("primary_source_requirements", [])
            }
            if declared != expected:
                integrity_errors.append(
                    "primary_source_requirement_manifest_mismatch:"
                    f"{unit['unit_id']}"
                )
            required_primary_checks[unit["unit_id"]] = expected
            continue
        if unit["kind"] != "roadmap":
            continue
        roadmap_paths = [
            path for path in unit["artifact_paths"]
            if path.startswith("knowledge/public/roadmaps/") and path.endswith(".json")
        ]
        roadmap = committed_json(root, manifest["base_commit"], roadmap_paths[0]) if len(roadmap_paths) == 1 else None
        if roadmap is None:
            integrity_errors.append(f"roadmap_source_registry_unavailable:{unit['unit_id']}")
            required_primary_checks[unit["unit_id"]] = {}
        else:
            source_registry = {source["source_id"]: source for source in roadmap["sources"]}
            milestone_requirements = {
                milestone["milestone_id"]: {
                    (
                        source_id,
                        source_registry[source_id]["url"],
                        source_registry[source_id]["source_class"],
                    )
                    for source_id in milestone["source_ids"]
                    if source_registry[source_id]["source_class"] != "openfs-governance"
                }
                for lane in roadmap["lanes"]
                for milestone in lane["milestones"]
                if milestone["comparison_priority"] == "key"
                and milestone["timing_basis"] not in {"openfs-provisional-plan", "no-public-date"}
            }
            generation_band_requirements = {
                band["generation_band_id"]: {
                    (
                        source_id,
                        source_registry[source_id]["url"],
                        source_registry[source_id]["source_class"],
                    )
                    for source_id in band["source_ids"]
                    if source_registry[source_id]["source_class"] != "openfs-governance"
                }
                for track in roadmap.get("tracks", [])
                for band in track.get("generation_bands", [])
            }
            expected = {
                selector: options
                for selector, options in {
                    **milestone_requirements,
                    **generation_band_requirements,
                }.items()
                if options
            }
            supplement_paths = [
                path
                for path in unit["artifact_paths"]
                if path in {
                    "knowledge/public/hpci-system-inventory.json",
                    "knowledge/public/application-performance-forecasts.json",
                    "knowledge/public/procurement-cost-register.json",
                    "knowledge/public/planning-evidence-readiness.json",
                }
            ]
            for supplement_path in supplement_paths:
                supplement = committed_json(
                    root, manifest["base_commit"], supplement_path
                )
                for source in supplement.get("sources", []):
                    expected[source["source_id"]] = {
                        (
                            source["source_id"],
                            source["url"],
                            review_source_class(source),
                        )
                    }
            declared = {
                requirement["selector"]: {
                    (option["source_id"], option["source_url"], option["source_class"])
                    for option in requirement["source_options"]
                }
                for requirement in unit.get("primary_source_requirements", [])
            }
            if declared != expected:
                integrity_errors.append(f"primary_source_requirement_manifest_mismatch:{unit['unit_id']}")
            required_primary_checks[unit["unit_id"]] = expected
    seen_ids: set[str] = set()
    seen_agents: set[str] = set()
    eligible: list[dict[str, Any]] = []
    ineligible_reviews: list[dict[str, Any]] = []
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
            expected_provenance = {
                "origin_group": registered.get("review_origin_group"),
                "harness_id": registered.get("harness_id"),
                "harness_repository_url": registered.get("harness_repository_url"),
                "harness_commit": registered.get("harness_commit"),
            }
            if not all(expected_provenance.values()):
                review_errors.append(
                    f"reviewer_registry_provenance_unconfigured:{review_id}:{agent_id}"
                )
            else:
                observed_provenance = {
                    key: reviewer_identity.get(key) for key in expected_provenance
                }
                if observed_provenance != expected_provenance:
                    review_errors.append(
                        f"reviewer_registry_provenance_mismatch:{review_id}:{agent_id}"
                    )
            if registered.get("network_access") != "public-web":
                review_errors.append(f"reviewer_lacks_public_web:{review_id}:{agent_id}")
            if registered.get("data_clearance") != "public":
                review_errors.append(f"reviewer_clearance_mismatch:{review_id}:{agent_id}")
            if "assessments" not in registered.get("write_scope", []):
                review_errors.append(f"reviewer_write_scope_mismatch:{review_id}:{agent_id}")
        if review.get("registry_snapshot_digest") != registry_digest:
            review_errors.append(f"agent_registry_digest_mismatch:{review_id}")
        if review.get("package_manifest_digest") != manifest_digest:
            review_errors.append(f"package_manifest_digest_mismatch:{review_id}")
        if review.get("package_id") != manifest["package_id"]:
            review_errors.append(f"package_id_mismatch:{review_id}")
        if review.get("base_commit") != manifest["base_commit"]:
            review_errors.append(f"base_commit_mismatch:{review_id}")
        try:
            reviewed_at = parse_time(review["reviewed_at"])
        except (KeyError, TypeError, ValueError):
            reviewed_at = None
            review_errors.append(f"reviewed_at_invalid:{review_id}")
        if reviewed_at is not None:
            if package_created is not None and reviewed_at < package_created - skew:
                review_errors.append(f"review_before_package_created:{review_id}")
            if reviewed_at > evaluated + skew:
                review_errors.append(f"review_after_evaluation_window:{review_id}")
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
        seen_primary_checks: set[tuple[str, str, str]] = set()
        conclusive_selectors: set[tuple[str, str]] = set()
        for check in primary_checks:
            unit_id = check.get("unit_id", "<missing>")
            selector = check.get("selector", "<missing>")
            source_id = check.get("source_id", "<missing>")
            key = (unit_id, selector, source_id)
            if key in seen_primary_checks:
                review_errors.append(f"duplicate_primary_source_check:{review_id}:{unit_id}:{selector}:{source_id}")
            seen_primary_checks.add(key)
            unit_requirements = required_primary_checks.get(unit_id)
            if unit_requirements is None:
                review_errors.append(f"primary_source_unit_mismatch:{review_id}:{unit_id}")
                continue
            source_options = unit_requirements.get(selector)
            observed_source = (source_id, check.get("source_url"), check.get("source_class"))
            if source_options is None:
                review_errors.append(f"primary_source_selector_mismatch:{review_id}:{unit_id}:{selector}")
                continue
            if observed_source not in source_options:
                review_errors.append(f"primary_source_identity_mismatch:{review_id}:{unit_id}:{selector}:{source_id}")
                continue
            if check.get("outcome") in {"supports", "contradicts"}:
                conclusive_selectors.add((unit_id, selector))
        if manifest["consensus_policy"]["require_primary_source"]:
            for unit_id, requirements in required_primary_checks.items():
                for selector in requirements:
                    if (unit_id, selector) not in conclusive_selectors:
                        review_errors.append(f"primary_source_coverage_mismatch:{review_id}:{unit_id}:{selector}")
        if review.get("overall_verdict") == "support":
            non_support_units = [
                item.get("unit_id", "<missing>")
                for item in assessments
                if item.get("verdict") != "support"
            ]
            if non_support_units:
                review_errors.append(
                    f"support_verdict_has_non_support_units:{review_id}:{','.join(sorted(non_support_units))}"
                )
            non_passing_checks = [
                f"{item.get('unit_id', '<missing>')}:{check}={outcome}"
                for item in assessments
                for check, outcome in item.get("checks", {}).items()
                if outcome != "pass"
            ]
            if non_passing_checks:
                review_errors.append(
                    f"support_verdict_has_non_passing_checks:{review_id}:{','.join(sorted(non_passing_checks))}"
                )
            non_supporting_sources = [
                f"{item.get('unit_id', '<missing>')}:{item.get('selector', '<missing>')}={item.get('outcome', '<missing>')}"
                for item in primary_checks
                if item.get("outcome") != "supports"
            ]
            if non_supporting_sources:
                review_errors.append(
                    f"support_verdict_has_non_supporting_sources:{review_id}:{','.join(sorted(non_supporting_sources))}"
                )
            blocking_objections = [
                f"{item.get('unit_id', '<missing>')}:{objection.get('severity', '<missing>')}"
                for item in assessments
                for objection in item.get("objections", [])
                if objection.get("severity") in {"major", "critical"}
            ]
            if review.get("critical_objections") or blocking_objections:
                review_errors.append(
                    f"support_verdict_has_blocking_objections:{review_id}"
                )
        if review.get("reviewer", {}).get("independence_group") in disallowed:
            review_errors.append(f"disallowed_independence_group:{review_id}")
        integrity_errors.extend(review_errors)
        if not review_errors:
            eligible.append(review)
        else:
            ineligible_reviews.append(
                {"review_id": review_id, "reasons": sorted(set(review_errors))}
            )

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
        "support_harnesses": len({
            review["reviewer"]["harness_repository_url"].removesuffix("/").removesuffix(".git").lower()
            for review in support
        }),
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
    if counts["support_harnesses"] < policy["minimum_harnesses"]:
        unmet.append("minimum_harnesses")
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
        "package_manifest_digest": manifest_digest,
        "evaluated_at": evaluated.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": status,
        "counts": counts,
        "review_results": {
            "eligible_review_ids": sorted(review["review_id"] for review in eligible),
            "ineligible_reviews": sorted(
                ineligible_reviews, key=lambda item: item["review_id"]
            ),
            "review_file_digests": dict(sorted(review_file_digests.items())),
        },
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
