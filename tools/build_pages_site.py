#!/usr/bin/env python3
"""Build the public OpenFS GitHub Pages site from approved repository paths."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import os
import shutil
import subprocess
from pathlib import Path
from typing import Any
from check_procurement_costs import validate_register
from check_public_planning_surfaces import validate_inventory_links
from estimate_system_cost import allocate_budget, contract_breakdown, five_year_known_cost_floor, lease_period_total
from catalog_lineage import catalog_aliases, current_finding_topics
from roadmap_timing import milestone_quarter_window


ROOT = Path(__file__).resolve().parents[1]
REPOSITORY_URL = "https://github.com/HPCI-CFSP/OpenFS"
PUBLIC_BRAND_ASSETS = (
    "openfs-logo.svg",
    "openfs-logo-compact.svg",
    "openfs-symbol.svg",
)


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def git_output(root: Path, arguments: list[str]) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def source_commit_metadata(root: Path, relative_path: str | None = None) -> dict[str, str]:
    if relative_path:
        value = git_output(
            root,
            ["log", "-1", "--format=%H%x00%cI", "--", relative_path],
        )
        if not value:
            raise ValueError(f"no source commit found for {relative_path}")
        commit_sha, updated_at = value.split("\x00", 1)
    else:
        commit_sha = os.environ.get("OPENFS_SOURCE_COMMIT") or os.environ.get(
            "GITHUB_SHA"
        )
        if not commit_sha:
            commit_sha = git_output(root, ["rev-parse", "HEAD"])
        updated_at = git_output(root, ["show", "-s", "--format=%cI", commit_sha])
    if len(commit_sha) != 40 or any(
        character not in "0123456789abcdef" for character in commit_sha
    ):
        raise ValueError(f"invalid source commit SHA: {commit_sha}")
    return {
        "commit_sha": commit_sha,
        "updated_at": updated_at,
        "commit_url": f"{REPOSITORY_URL}/commit/{commit_sha}",
    }


def roadmap_index_entry(
    roadmap: dict[str, Any], category_by_roadmap: dict[str, str]
) -> dict[str, Any]:
    return {
        "export_id": roadmap["export_id"],
        "roadmap_id": roadmap["roadmap_id"],
        "domain": roadmap["domain"],
        "catalog_category_id": category_by_roadmap[roadmap["roadmap_id"]],
        "slug": roadmap["slug"],
        "path": f"roadmaps/{roadmap['slug']}/",
        "renderer": "common-quarterly",
        "title_ja": roadmap["title_ja"],
        "title_en": roadmap["title_en"],
        "summary_ja": roadmap["summary_ja"],
        "summary_en": roadmap["summary_en"],
        "horizon": roadmap["horizon"],
        "timeline_granularity": roadmap["timeline_granularity"],
        "as_of": roadmap["as_of"],
        "updated_at": roadmap["updated_at"],
        "source_commit": roadmap["source_commit"],
        "source_commit_url": roadmap["source_commit_url"],
        "research_status": roadmap["research_status"],
        "coverage_status": roadmap["coverage_status"],
        "consensus_status": roadmap["consensus_status"],
        "track_count": len(roadmap["tracks"]),
        "milestone_count": sum(
            len(lane["milestones"]) for lane in roadmap["lanes"]
        ),
        "source_count": roadmap["source_coverage"]["source_count"],
        "primary_source_count": roadmap["source_coverage"]["primary_source_count"],
        "coverage_gap_count": len(roadmap["coverage_gaps"]),
        "dependency_count": len(roadmap["dependencies"]),
    }


def render_template(path: Path, replacements: dict[str, str]) -> str:
    value = path.read_text(encoding="utf-8")
    if "{{SITE_IDENTITY}}" in value:
        identity = (path.parent / "partials" / "identity.html").read_text(encoding="utf-8")
        value = value.replace("{{SITE_IDENTITY}}", identity.rstrip())
    variables = {"ROOT_PREFIX": "", "HOME_HREF": replacements.get("ROOT_PREFIX") or "./", **replacements}
    for key, replacement in variables.items():
        value = value.replace(f"{{{{{key}}}}}", replacement)
    return value


def timing_boundary_ordinal(boundary: dict[str, Any], edge: str) -> int:
    """Return an inclusive quarter ordinal for a generation-band boundary."""
    precision = boundary["precision"]
    if precision == "quarter":
        quarter = int(boundary["quarter"][1])
    elif precision == "half-year":
        if boundary["half"] == "H1":
            quarter = 1 if edge == "start" else 2
        else:
            quarter = 3 if edge == "start" else 4
    else:
        quarter = 1 if edge == "start" else 4
    return boundary["year"] * 4 + quarter - 1


def public_projection(
    artifact: dict[str, Any],
    fields: list[str],
    required_metadata: dict[str, Any],
    required_bilingual_fields: list[str],
    approved_directives: dict[str, set[str]],
    label: str,
) -> dict[str, Any]:
    publication = artifact.get("publication")
    if not isinstance(publication, dict):
        raise ValueError(f"{label} has no publication metadata")
    for key, expected in required_metadata.items():
        if publication.get(key) != expected:
            raise ValueError(f"{label} has invalid publication metadata: {key}")
    if not publication.get("publication_decision_id"):
        raise ValueError(f"{label} has no publication decision")
    directive_id = publication.get("human_approval_directive_id")
    artifact_id = (
        artifact.get("scenario_id")
        or artifact.get("report_id")
        or artifact.get("export_id")
        or artifact.get("artifact_id")
    )
    if not directive_id or artifact_id not in approved_directives.get(directive_id, set()):
        raise ValueError(f"{label} has no matching human publication Directive")
    missing_languages = [key for key in required_bilingual_fields if not artifact.get(key)]
    if missing_languages:
        raise ValueError(f"{label} lacks bilingual fields: {missing_languages}")
    return {key: artifact[key] for key in fields if key in artifact}


def approved_publication_directives(root: Path, policy: dict[str, Any]) -> dict[str, set[str]]:
    allowed_statuses = set(policy["human_publication_directive_statuses"])
    approvals: dict[str, set[str]] = {}
    for path in sorted(root.glob(policy["human_publication_directive_glob"])):
        directive = load_json(path)
        if directive.get("directive_type") != "publication-approval":
            continue
        if directive.get("status") not in allowed_statuses:
            continue
        if not directive.get("submitted_by") or not directive.get("submitted_at"):
            continue
        approvals[directive["directive_id"]] = set(directive.get("publication_targets", []))
    return approvals


def collect_scenarios(
    root: Path, policy: dict[str, Any], include_commit_metadata: bool = True
) -> list[dict[str, Any]]:
    allowed = set(policy["accepted_scenario_statuses"])
    directives = approved_publication_directives(root, policy)
    scenarios: list[dict[str, Any]] = []
    for path in sorted(root.glob(policy["accepted_scenario_glob"])):
        payload = load_json(path)
        candidates = payload.get("scenarios", [payload]) if isinstance(payload, dict) else []
        for scenario in candidates:
            status = scenario.get("status")
            if status not in allowed:
                raise ValueError(f"non-publishable scenario in accepted path: {path}: {status}")
            scenario_with_contracts = dict(scenario)
            if "decision_evidence_contracts" in payload:
                scenario_with_contracts["decision_evidence_contracts"] = payload["decision_evidence_contracts"]
            projected = public_projection(
                scenario_with_contracts,
                policy["scenario_public_fields"],
                policy["required_publication_metadata"],
                policy["scenario_required_bilingual_fields"],
                directives,
                f"scenario {scenario.get('scenario_id', path.name)}",
            )
            projected.pop("publication", None)
            projected["path"] = f"scenarios/{projected['scenario_id'].lower()}/"
            if include_commit_metadata:
                metadata = source_commit_metadata(root, str(path.relative_to(root)))
                projected.update(
                    updated_at=metadata["updated_at"],
                    source_commit=metadata["commit_sha"],
                    source_commit_url=metadata["commit_url"],
                )
            scenarios.append(projected)
    return scenarios


def collect_scenario_budget_references(
    root: Path, policy: dict[str, Any]
) -> list[dict[str, Any]]:
    """Collect the single-source public budget reference cases for scenarios."""
    references: dict[str, dict[str, Any]] = {}
    for path in sorted(root.glob(policy["accepted_scenario_glob"])):
        payload = load_json(path)
        for item in payload.get("budget_reference_cases", []):
            case_id = item["case_id"]
            if case_id in references and references[case_id] != item:
                raise ValueError(f"conflicting scenario budget reference: {case_id}")
            references[case_id] = item
    return sorted(references.values(), key=lambda item: item["case_id"])


def collect_procurement_costs(root: Path, policy: dict[str, Any]) -> tuple[dict, dict]:
    from validate_json_schemas import schema_registry, Draft202012Validator, FormatChecker
    register = load_json(root / policy["procurement_register_path"])
    config = load_json(root / "config/budget-planning.json")
    schemas, registry = schema_registry(root)
    for payload, schema_name in [(register, "procurement-cost-register.schema.json"),
                                  (config, "budget-planning.schema.json")]:
        Draft202012Validator(schemas[schema_name], registry=registry,
                             format_checker=FormatChecker()).validate(payload)
    validate_register(register, config)
    projected = public_projection(
        register, policy["procurement_public_fields"], policy["required_publication_metadata"],
        ["title_ja", "title_en", "caveat_ja", "caveat_en"],
        approved_publication_directives(root, policy), "procurement register")
    projected = json.loads(json.dumps(projected))
    for case in projected["cases"]:
        case["breakdown"] = contract_breakdown(case)
        case["lease_period_total"] = lease_period_total(case)
        case["five_year_known_cost_floor"] = five_year_known_cost_floor(case)
    return projected, config


def collect_conference_coverage(root: Path, policy: dict[str, Any]) -> dict:
    from check_conference_coverage import load_and_validate
    payload = load_and_validate(root)
    return public_projection(
        payload, policy["conference_public_fields"], policy["required_publication_metadata"],
        ["title_ja", "title_en", "scope_ja", "scope_en", "caveat_ja", "caveat_en"],
        approved_publication_directives(root, policy), "conference coverage")


def link_inventory_evidence(inventory: dict, register: dict, roadmaps: list[dict]) -> None:
    errors = validate_inventory_links(inventory, register, roadmaps)
    if errors:
        raise ValueError("; ".join(errors))
    systems = {system["system_id"]: system for system in inventory["systems"]}
    inventory_roadmap = next((roadmap for roadmap in roadmaps if roadmap["roadmap_id"] == "RM-X-BLUEPRINT"), None)
    if any(case.get("linked_system_ids") for case in register["cases"]) and not inventory_roadmap:
        raise ValueError("linked inventory needs its published roadmap page")
    milestones = {(roadmap["roadmap_id"], milestone["milestone_id"]): {
                      **milestone, "roadmap_id": roadmap["roadmap_id"],
                      "roadmap_slug": roadmap["slug"], "track_id": lane["track_id"]}
                  for roadmap in roadmaps for lane in roadmap["lanes"]
                  for milestone in lane["milestones"]}
    for system in systems.values():
        system["lifecycle_events"] = [
            milestones[(ref["roadmap_id"], ref["milestone_id"])]
            for ref in system.get("lifecycle_milestone_refs", [])]
        system["procurement_links"] = []
    for case in register["cases"]:
        case["linked_systems"] = []
        for system_id in case.get("linked_system_ids", []):
            system = systems[system_id]
            case["linked_systems"].append({
                **{key: system[key] for key in ("system_id", "name_ja", "name_en")},
                "inventory_path": f"roadmaps/{inventory_roadmap['slug']}/",
            })
            system["procurement_links"].append({key: case[key] for key in ("case_id", "title_ja", "title_en")})


def collect_reports(root: Path, policy: dict[str, Any]) -> list[dict[str, Any]]:
    index_path = root / policy["report_index"]
    if not index_path.exists():
        return []
    allowed = set(policy["accepted_report_statuses"])
    directives = approved_publication_directives(root, policy)
    reports = load_json(index_path).get("reports", [])
    projected_reports = []
    for report in reports:
        if report.get("status") not in allowed:
            raise ValueError(
                f"non-publishable report in public index: {report.get('report_id')}"
            )
        projected = public_projection(
                report,
                policy["report_public_fields"],
                policy["required_publication_metadata"],
                policy["report_required_bilingual_fields"],
                directives,
                f"report {report.get('report_id', 'unknown')}",
            )
        projected.pop("publication", None)
        projected_reports.append(projected)
    return projected_reports


def collect_consensus_receipts(
    root: Path, policy: dict[str, Any]
) -> list[dict[str, Any]]:
    path = root / policy["included_public_consensus_receipts"]
    if not path.exists():
        return []
    export = load_json(path)
    if export.get("status") not in set(
        policy["accepted_consensus_receipt_statuses"]
    ):
        raise ValueError("public Consensus Receipt export is not published")
    directives = approved_publication_directives(root, policy)
    projected = public_projection(
        export,
        ["export_id", "status", "as_of", "receipts"],
        policy["required_publication_metadata"],
        [],
        directives,
        f"Consensus Receipt export {export.get('export_id', path.name)}",
    )

    receipt_fields = policy["consensus_receipt_public_fields"]
    participant_fields = policy["consensus_participant_public_fields"]
    harness_fields = policy["consensus_harness_public_fields"]
    safe_receipts: list[dict[str, Any]] = []
    seen_receipt_ids: set[str] = set()
    represented_findings: set[str] = set()
    for receipt in projected.get("receipts", []):
        receipt_id = receipt.get("receipt_id", "unknown")
        if receipt_id in seen_receipt_ids:
            raise ValueError(f"duplicate public Consensus Receipt: {receipt_id}")
        seen_receipt_ids.add(receipt_id)
        if receipt.get("outcome") != "accepted":
            raise ValueError(f"Consensus Receipt {receipt_id} is not accepted")

        finding_ids = set(receipt.get("finding_ids", []))
        if not finding_ids:
            raise ValueError(f"Consensus Receipt {receipt_id} has no Findings")
        duplicates = finding_ids & represented_findings
        if duplicates:
            raise ValueError(
                f"public Findings have multiple Consensus Receipts: {sorted(duplicates)}"
            )
        represented_findings.update(finding_ids)

        harnesses = receipt.get("harnesses", [])
        harness_ids = [item.get("harness_id") for item in harnesses]
        known_harness_ids = set(harness_ids)
        if not harness_ids or len(harness_ids) != len(set(harness_ids)):
            raise ValueError(
                f"Consensus Receipt {receipt_id} has missing or duplicate harness IDs"
            )
        for harness in harnesses:
            commit_sha = harness.get("commit_sha", "")
            if len(commit_sha) != 40 or any(
                character not in "0123456789abcdef" for character in commit_sha
            ):
                raise ValueError(
                    f"Consensus Receipt {receipt_id} has an invalid harness commit SHA"
                )

        participants = receipt.get("participants", [])
        participant_ids = [item.get("agent_id") for item in participants]
        if not participant_ids or len(participant_ids) != len(set(participant_ids)):
            raise ValueError(
                f"Consensus Receipt {receipt_id} has missing or duplicate Agent IDs"
            )
        if any(item.get("harness_id") not in known_harness_ids for item in participants):
            raise ValueError(
                f"Consensus Receipt {receipt_id} has an Agent with an unknown harness"
            )
        voting_participants = [
            item
            for item in participants
            if item.get("contribution") != "consensus-controller"
            and item.get("independence_group") != "non-voting-control-plane"
        ]
        if any(
            str(item.get(field, "")).strip().lower()
            in {"", "none", "unconfigured"}
            for item in voting_participants
            for field in ("provider", "model_family", "independence_group")
        ):
            raise ValueError(
                f"Consensus Receipt {receipt_id} contains an unconfigured participant"
            )
        model_identities = {
            (item.get("provider"), item.get("model_family"))
            for item in voting_participants
        }
        if len(model_identities) < 2:
            raise ValueError(
                f"Consensus Receipt {receipt_id} has fewer than two model identities"
            )

        requirements = receipt.get("policy_requirements", {})
        result = receipt.get("policy_result", {})
        result_groups = set(result.get("independence_groups", []))
        participant_groups = {
            item.get("independence_group")
            for item in voting_participants
        }
        group_count = receipt.get("independence_group_count")
        minimum_groups = requirements.get("minimum_independence_groups")
        if (
            not isinstance(group_count, int)
            or not isinstance(minimum_groups, int)
            or not result_groups
            or not result_groups <= participant_groups
            or group_count != len(result_groups)
            or group_count < 2
            or group_count < minimum_groups
        ):
            raise ValueError(
                f"Consensus Receipt {receipt_id} has inconsistent independence groups"
            )
        assessment_count = result.get("assessment_count")
        support_count = result.get("support_count")
        minimum_assessments = requirements.get("minimum_assessments")
        minimum_support = requirements.get("minimum_support")
        if (
            not all(
                isinstance(value, int)
                for value in (
                    assessment_count,
                    support_count,
                    minimum_assessments,
                    minimum_support,
                )
            )
            or assessment_count < minimum_assessments
            or support_count < minimum_support
            or result.get("falsification_review_passed") is not True
            or result.get("critical_objection_count") != 0
        ):
            raise ValueError(
                f"Consensus Receipt {receipt_id} does not satisfy its public policy result"
            )

        safe_receipt = {key: receipt[key] for key in receipt_fields if key in receipt}
        safe_receipt["participants"] = [
            {key: item[key] for key in participant_fields if key in item}
            for item in participants
        ]
        safe_receipt["harnesses"] = [
            {key: item[key] for key in harness_fields if key in item}
            for item in harnesses
        ]
        safe_receipts.append(safe_receipt)
    return safe_receipts


def collect_consensus_packages(
    root: Path, policy: dict[str, Any], include_commit_metadata: bool = True
) -> list[dict[str, Any]]:
    directives = approved_publication_directives(root, policy)
    approved_targets = {
        target for targets in directives.values() for target in targets
    }
    allowed_package_statuses = set(policy["accepted_consensus_package_statuses"])
    allowed_gate_statuses = set(policy["accepted_consensus_package_gate_statuses"])
    packages: list[dict[str, Any]] = []
    for manifest_path in sorted(root.glob(policy["included_consensus_package_glob"])):
        manifest_digest = hashlib.sha256(manifest_path.read_bytes()).hexdigest()
        manifest = load_json(manifest_path)
        package_id = manifest.get("package_id", manifest_path.parent.name)
        if package_id not in approved_targets:
            raise ValueError(f"Consensus package {package_id} has no human publication Directive")
        if manifest.get("status") not in allowed_package_statuses:
            raise ValueError(f"Consensus package {package_id} has non-public status")
        gate_path = manifest_path.parent / "gate-result.json"
        if not gate_path.exists():
            raise ValueError(f"Consensus package {package_id} has no gate result")
        gate = load_json(gate_path)
        if gate.get("package_id") != package_id or gate.get("base_commit") != manifest.get("base_commit"):
            raise ValueError(f"Consensus package {package_id} gate identity mismatch")
        if gate.get("package_manifest_digest") != manifest_digest:
            raise ValueError(f"Consensus package {package_id} gate manifest digest mismatch")
        if gate.get("status") not in allowed_gate_statuses:
            raise ValueError(f"Consensus package {package_id} has non-public gate status")

        projected = {
            key: manifest[key]
            for key in policy["consensus_package_public_fields"]
            if key in manifest
        }
        projected["gate"] = {
            key: gate[key]
            for key in policy["consensus_package_gate_public_fields"]
            if key in gate
        }
        eligible_ids = set(
            gate.get("review_results", {}).get("eligible_review_ids", [])
        )
        gate_review_digests = gate.get("review_results", {}).get(
            "review_file_digests", {}
        )
        assessments = {}
        assessment_digests = {}
        assessment_dir = root / manifest["submission"]["assessment_directory"]
        for assessment_path in sorted(assessment_dir.glob("*.json")):
            assessment = load_json(assessment_path)
            if (
                assessment.get("package_id") != package_id
                or assessment.get("base_commit") != manifest.get("base_commit")
                or assessment.get("package_manifest_digest") != manifest_digest
            ):
                raise ValueError(f"Consensus package {package_id} contains a mismatched assessment")
            review_id = assessment.get("review_id")
            if review_id in assessments:
                raise ValueError(f"Consensus package {package_id} contains duplicate review ID {review_id}")
            assessments[review_id] = assessment
            assessment_digests[review_id] = hashlib.sha256(
                assessment_path.read_bytes()
            ).hexdigest()
        if assessment_digests != gate_review_digests:
            raise ValueError(
                f"Consensus package {package_id} gate review digest set mismatch"
            )
        missing_eligible = eligible_ids - set(assessments)
        if missing_eligible:
            raise ValueError(f"Consensus package {package_id} gate references missing reviews: {sorted(missing_eligible)}")
        reviewers = []
        reviewer_fields = policy["consensus_package_reviewer_public_fields"]
        for review_id in sorted(eligible_ids):
            assessment = assessments[review_id]
            reviewer = {
                key: assessment["reviewer"][key]
                for key in reviewer_fields
                if key in assessment["reviewer"]
            }
            reviewer.update(
                review_id=review_id,
                overall_verdict=assessment["overall_verdict"],
                reviewed_at=assessment["reviewed_at"],
            )
            repository_url = reviewer.get("harness_repository_url", "")
            harness_commit = reviewer.get("harness_commit", "")
            if repository_url.startswith("https://github.com/") and len(harness_commit) == 40:
                reviewer["harness_commit_url"] = f"{repository_url.removesuffix('.git')}/commit/{harness_commit}"
            reviewers.append(reviewer)
        projected["eligible_reviewers"] = reviewers
        projected["artifact_count"] = len(manifest["artifact_manifest"])
        projected["manifest_sha256"] = manifest_digest
        projected["path"] = f"consensus/{package_id.lower()}/"
        projected["base_commit_url"] = f"{REPOSITORY_URL}/commit/{manifest['base_commit']}"
        if include_commit_metadata:
            relative = str(manifest_path.relative_to(root))
            metadata = source_commit_metadata(root, relative)
            projected.update(
                updated_at=metadata["updated_at"],
                source_commit=metadata["commit_sha"],
                source_commit_url=metadata["commit_url"],
                manifest_url=f"{REPOSITORY_URL}/blob/{metadata['commit_sha']}/{relative}",
            )
        packages.append(projected)
    return packages


def collect_topic_summaries(
    root: Path,
    policy: dict[str, Any],
    valid_topic_ids: set[str],
    consensus_receipts: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    path = root / policy["included_public_topic_summaries"]
    if not path.exists():
        return []
    export = load_json(path)
    if export.get("status") not in set(policy["accepted_topic_summary_statuses"]):
        raise ValueError("public Topic summary export is not published")
    directives = approved_publication_directives(root, policy)
    projected = public_projection(
        export,
        ["export_id", "status", "as_of", "summaries"],
        policy["required_publication_metadata"],
        [],
        directives,
        f"Topic summary export {export.get('export_id', path.name)}",
    )

    summary_fields = policy["topic_summary_public_fields"]
    finding_fields = policy["topic_finding_public_fields"]
    source_fields = policy["topic_source_public_fields"]
    required_bilingual = policy["topic_summary_required_bilingual_fields"]
    safe_summaries: list[dict[str, Any]] = []
    seen_summary_ids: set[str] = set()
    for summary in projected.get("summaries", []):
        summary_id = summary.get("summary_id", "unknown")
        if summary_id in seen_summary_ids:
            raise ValueError(f"duplicate public Topic summary: {summary_id}")
        seen_summary_ids.add(summary_id)
        missing_languages = [key for key in required_bilingual if not summary.get(key)]
        if missing_languages:
            raise ValueError(
                f"Topic summary {summary_id} lacks bilingual fields: {missing_languages}"
            )
        topic_ids = set(summary.get("topic_ids", []))
        unknown_topics = topic_ids - valid_topic_ids
        if unknown_topics:
            raise ValueError(
                f"Topic summary {summary_id} references unknown Topics: {sorted(unknown_topics)}"
            )
        safe_summary = {key: summary[key] for key in summary_fields if key in summary}
        safe_findings = []
        represented_topics: set[str] = set()
        for finding in summary.get("findings", []):
            finding_id = finding.get("finding_id", "unknown")
            finding_topics = set(finding.get("topic_ids", []))
            if not finding_topics or not finding_topics <= topic_ids:
                raise ValueError(
                    f"Topic summary {summary_id} has Finding outside its Topic set"
                )
            represented_topics.update(finding_topics)
            receipt_id = finding.get("consensus_receipt_id")
            if summary.get("consensus_status") == "accepted":
                if summary.get("research_status") != "accepted":
                    raise ValueError(
                        f"accepted Consensus summary {summary_id} is not research-accepted"
                    )
                if not receipt_id:
                    raise ValueError(
                        f"accepted Finding {finding_id} has no Consensus Receipt"
                    )
                receipt = consensus_receipts.get(receipt_id)
                if not receipt or finding_id not in receipt.get("finding_ids", []):
                    raise ValueError(
                        f"accepted Finding {finding_id} has no matching Consensus Receipt"
                    )
            elif receipt_id:
                raise ValueError(
                    f"provisional Finding {finding_id} cannot reference a Consensus Receipt"
                )
            safe_finding = {key: finding[key] for key in finding_fields if key in finding}
            safe_finding["sources"] = [
                {key: source[key] for key in source_fields if key in source}
                for source in finding.get("sources", [])
            ]
            safe_findings.append(safe_finding)
        missing_findings = topic_ids - represented_topics
        if missing_findings:
            raise ValueError(
                f"Topic summary {summary_id} has no Finding for Topics: "
                f"{sorted(missing_findings)}"
            )
        safe_summary["findings"] = safe_findings
        safe_summaries.append(safe_summary)
    return safe_summaries


def collect_roadmaps(
    root: Path, policy: dict[str, Any], include_commit_metadata: bool = True
) -> list[dict[str, Any]]:
    portfolio = load_json(root / "config" / "roadmap-portfolio.json")
    portfolio_by_id = {
        item["roadmap_id"]: item for item in portfolio["roadmap_families"]
    }
    expected_exports = {
        export_id
        for item in portfolio["roadmap_families"]
        if item["status"] == "published"
        for export_id in item["published_artifact_ids"]
    }
    directives = approved_publication_directives(root, policy)
    roadmaps: list[dict[str, Any]] = []
    seen_exports: set[str] = set()
    seen_roadmaps: set[str] = set()
    seen_slugs: set[str] = set()
    seen_dependencies: set[str] = set()
    for path in sorted(root.glob(policy["included_public_roadmap_glob"])):
        export = load_json(path)
        if export.get("status") not in set(policy["accepted_roadmap_statuses"]):
            raise ValueError(f"non-publishable roadmap in accepted path: {path}")
        label = f"roadmap {export.get('export_id', path.name)}"
        projected = public_projection(
            export,
            policy["roadmap_public_fields"],
            policy["required_publication_metadata"],
            policy["roadmap_required_bilingual_fields"],
            directives,
            label,
        )
        export_id = projected["export_id"]
        roadmap_id = projected["roadmap_id"]
        slug = projected["slug"]
        if export_id in seen_exports or roadmap_id in seen_roadmaps or slug in seen_slugs:
            raise ValueError(f"duplicate roadmap export, roadmap ID, or slug: {label}")
        seen_exports.add(export_id)
        seen_roadmaps.add(roadmap_id)
        seen_slugs.add(slug)

        portfolio_item = portfolio_by_id.get(roadmap_id)
        if not portfolio_item:
            raise ValueError(f"{label} is absent from the roadmap portfolio")
        if (
            portfolio_item["slug"] != slug
            or portfolio_item["domain"] != projected["domain"]
            or export_id not in portfolio_item["published_artifact_ids"]
        ):
            raise ValueError(f"{label} disagrees with its roadmap portfolio entry")

        start_year = projected["horizon"]["start_year"]
        configured_end_year = projected["horizon"]["end_year"]
        extension_policy = projected["horizon"].get("extension_policy", "fixed")
        if start_year > configured_end_year:
            raise ValueError(f"{label} has an invalid horizon")
        group_ids = [item["group_id"] for item in projected["groups"]]
        track_ids = [item["track_id"] for item in projected["tracks"]]
        source_ids = [item["source_id"] for item in projected["sources"]]
        for kind, identifiers in (
            ("group", group_ids), ("track", track_ids), ("source", source_ids)
        ):
            if len(identifiers) != len(set(identifiers)):
                raise ValueError(f"{label} has duplicate {kind} IDs")
        known_groups = set(group_ids)
        known_tracks = set(track_ids)
        known_sources = set(source_ids)
        latest_dated_year = configured_end_year
        generation_band_ids: set[str] = set()
        for track in projected["tracks"]:
            if track["group"] not in known_groups:
                raise ValueError(f"track {track['track_id']} has an unknown group")
            unknown = set(track["source_ids"]) - known_sources
            if unknown:
                raise ValueError(f"track {track['track_id']} references unknown sources: {sorted(unknown)}")
            for band in track.get("generation_bands", []):
                band_id = band["generation_band_id"]
                if band_id in generation_band_ids:
                    raise ValueError(f"duplicate roadmap generation band: {band_id}")
                generation_band_ids.add(band_id)
                unknown_sources = set(band["source_ids"]) - known_sources
                if unknown_sources:
                    raise ValueError(
                        f"generation band {band_id} references unknown sources: "
                        f"{sorted(unknown_sources)}"
                    )
                start = band["start"]
                end = band["end"]
                if start["year"] < start_year:
                    raise ValueError(
                        f"generation band {band_id} starts before the roadmap horizon"
                    )
                if end is not None and timing_boundary_ordinal(
                    end, "end"
                ) < timing_boundary_ordinal(start, "start"):
                    raise ValueError(f"generation band {band_id} has a reversed range")
                latest_dated_year = max(
                    latest_dated_year,
                    start["year"],
                    end["year"] if end is not None else start["year"],
                )

        for lane in projected["lanes"]:
            for milestone in lane["milestones"]:
                window = milestone_quarter_window(milestone)
                if window is not None:
                    latest_dated_year = max(latest_dated_year, window[1] // 4)
        if extension_policy == "fixed" and latest_dated_year > configured_end_year:
            raise ValueError(f"{label} has dated evidence outside its fixed horizon")
        end_year = (
            latest_dated_year
            if extension_policy == "extend-to-latest-dated-evidence"
            else configured_end_year
        )
        projected["horizon"]["end_year"] = end_year

        dependency_ids = {item["dependency_id"] for item in projected["dependencies"]}
        if len(dependency_ids) != len(projected["dependencies"]):
            raise ValueError(f"{label} has duplicate dependency IDs")
        duplicate_dependencies = dependency_ids & seen_dependencies
        if duplicate_dependencies:
            raise ValueError(f"duplicate cross-roadmap dependency IDs: {sorted(duplicate_dependencies)}")
        seen_dependencies.update(dependency_ids)
        for dependency in projected["dependencies"]:
            unknown_roadmaps = {
                dependency["upstream_roadmap_id"], dependency["downstream_roadmap_id"]
            } - set(portfolio_by_id)
            unknown_sources = set(dependency["source_ids"]) - known_sources
            if unknown_roadmaps or unknown_sources:
                raise ValueError(
                    f"dependency {dependency['dependency_id']} has unknown roadmap or source references"
                )

        lane_ids: set[str] = set()
        all_milestone_ids = {
            milestone["milestone_id"]
            for lane in projected["lanes"]
            for milestone in lane["milestones"]
        }
        milestone_ids: set[str] = set()
        for lane in projected["lanes"]:
            lane_id = lane["lane_id"]
            if lane_id in lane_ids:
                raise ValueError(f"duplicate roadmap lane: {lane_id}")
            lane_ids.add(lane_id)
            if lane["track_id"] not in known_tracks:
                raise ValueError(f"roadmap lane {lane_id} has an unknown track")
            for milestone in lane["milestones"]:
                milestone_id = milestone["milestone_id"]
                if milestone_id in milestone_ids:
                    raise ValueError(f"duplicate roadmap milestone: {milestone_id}")
                milestone_ids.add(milestone_id)
                unknown_sources = set(milestone["source_ids"]) - known_sources
                if unknown_sources:
                    raise ValueError(f"milestone {milestone_id} references unknown sources: {sorted(unknown_sources)}")
                year = milestone["year"]
                window = milestone_quarter_window(milestone)
                basis = milestone["timing_basis"]
                maturity = milestone["maturity"]
                if year is None:
                    if basis != "no-public-date":
                        raise ValueError(f"undated roadmap milestone {milestone_id} has inconsistent timing fields")
                elif window[0] < start_year * 4 or window[1] >= (end_year + 1) * 4:
                    raise ValueError(f"roadmap milestone {milestone_id} is outside the horizon")
                elif basis == "no-public-date" or maturity == "undated":
                    raise ValueError(f"dated roadmap milestone {milestone_id} is marked undated")
                if basis == "openfs-provisional-plan" and milestone["event_type"] not in {"hpci-evaluation", "hpci-adoption"}:
                    raise ValueError(f"OpenFS provisional milestone {milestone_id} is not an HPCI gate")
                allowed_refs = dependency_ids | all_milestone_ids | set(portfolio_by_id)
                unknown_refs = set(milestone["dependency_refs"]) - allowed_refs
                if unknown_refs:
                    raise ValueError(f"milestone {milestone_id} has unknown dependency references: {sorted(unknown_refs)}")

        primary_source_count = sum(
            source["source_class"] != "openfs-governance"
            for source in projected["sources"]
        )
        projected["source_coverage"] = {
            "source_count": len(projected["sources"]),
            "primary_source_count": primary_source_count,
            "primary_source_ratio": round(primary_source_count / len(projected["sources"]), 3),
        }
        if include_commit_metadata:
            metadata = source_commit_metadata(root, str(path.relative_to(root)))
            projected.update(
                updated_at=metadata["updated_at"],
                source_commit=metadata["commit_sha"],
                source_commit_url=metadata["commit_url"],
            )
        roadmaps.append(projected)

    if seen_exports != expected_exports:
        raise ValueError(
            "published roadmap artifacts disagree with portfolio: "
            f"missing={sorted(expected_exports - seen_exports)}, "
            f"unexpected={sorted(seen_exports - expected_exports)}"
        )
    return roadmaps


def collect_roadmap_reference_data(
    root: Path,
    policy: dict[str, Any],
    roadmaps: list[dict[str, Any]],
    include_commit_metadata: bool = True,
    catalog_sources: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Project and validate the single public glossary/comparison source."""
    relative_path = policy["included_public_roadmap_reference_data"]
    artifact = load_json(root / relative_path)
    directives = approved_publication_directives(root, policy)
    projected = public_projection(
        artifact,
        policy["roadmap_reference_data_public_fields"],
        policy["required_publication_metadata"],
        policy["roadmap_reference_data_required_bilingual_fields"],
        directives,
        f"roadmap reference data {artifact.get('export_id', relative_path)}",
    )

    roadmap_by_id = {roadmap["roadmap_id"]: roadmap for roadmap in roadmaps}
    sources_by_roadmap = {
        roadmap_id: {source["source_id"] for source in roadmap["sources"]}
        for roadmap_id, roadmap in roadmap_by_id.items()
    }
    if catalog_sources is None:
        catalog_path = root / policy["included_public_topic_decision_support"]
        catalog_sources = load_json(catalog_path).get("sources", []) if catalog_path.is_file() else []
    catalog_source_ids = {source["source_id"] for source in catalog_sources}

    def validate_source_refs(source_refs: list[dict[str, str]], label: str) -> None:
        seen: set[tuple[str, str]] = set()
        for source_ref in source_refs:
            if "catalog_source_id" in source_ref:
                source_id = source_ref["catalog_source_id"]
                key = ("catalog", source_id)
                if key in seen:
                    raise ValueError(f"{label} has a duplicate source reference: {key}")
                seen.add(key)
                if source_id not in catalog_source_ids:
                    raise ValueError(f"{label} references unknown catalog source: {source_id}")
                continue
            roadmap_id = source_ref["roadmap_id"]
            source_id = source_ref["source_id"]
            key = (roadmap_id, source_id)
            if key in seen:
                raise ValueError(f"{label} has a duplicate source reference: {key}")
            seen.add(key)
            if roadmap_id not in roadmap_by_id:
                raise ValueError(f"{label} references unknown roadmap: {roadmap_id}")
            if source_id not in sources_by_roadmap[roadmap_id]:
                raise ValueError(
                    f"{label} references unknown source {source_id} in {roadmap_id}"
                )

    term_ids = [term["term_id"] for term in projected["terms"]]
    if len(term_ids) != len(set(term_ids)):
        raise ValueError("roadmap reference data has duplicate term IDs")
    known_terms = set(term_ids)
    alias_owners: dict[str, str] = {}
    for term in projected["terms"]:
        term_id = term["term_id"]
        unknown_roadmaps = set(term["roadmap_ids"]) - set(roadmap_by_id)
        if unknown_roadmaps:
            raise ValueError(
                f"term {term_id} references unknown roadmaps: {sorted(unknown_roadmaps)}"
            )
        unknown_related = set(term["related_term_ids"]) - known_terms
        if unknown_related:
            raise ValueError(
                f"term {term_id} references unknown related terms: {sorted(unknown_related)}"
            )
        if term_id in term["related_term_ids"]:
            raise ValueError(f"term {term_id} cannot relate to itself")
        for alias in term["aliases"]:
            normalized = alias.casefold()
            owner = alias_owners.get(normalized)
            if owner and owner != term_id:
                raise ValueError(
                    f"roadmap reference alias {alias!r} is shared by {owner} and {term_id}"
                )
            alias_owners[normalized] = term_id
        validate_source_refs(term["source_refs"], f"term {term_id}")

    comparison_ids = [item["comparison_id"] for item in projected["comparison_sets"]]
    if len(comparison_ids) != len(set(comparison_ids)):
        raise ValueError("roadmap reference data has duplicate comparison IDs")
    for comparison in projected["comparison_sets"]:
        comparison_id = comparison["comparison_id"]
        comparison_roadmaps = set(comparison["roadmap_ids"])
        unknown_roadmaps = comparison_roadmaps - set(roadmap_by_id)
        if unknown_roadmaps:
            raise ValueError(
                f"comparison {comparison_id} references unknown roadmaps: "
                f"{sorted(unknown_roadmaps)}"
            )
        column_ids = [column["column_id"] for column in comparison["columns"]]
        if len(column_ids) != len(set(column_ids)):
            raise ValueError(f"comparison {comparison_id} has duplicate column IDs")
        row_terms = [row["term_id"] for row in comparison["rows"]]
        if len(row_terms) != len(set(row_terms)):
            raise ValueError(f"comparison {comparison_id} has duplicate term rows")
        for row in comparison["rows"]:
            term_id = row["term_id"]
            if term_id not in known_terms:
                raise ValueError(
                    f"comparison {comparison_id} references unknown term: {term_id}"
                )
            term = next(item for item in projected["terms"] if item["term_id"] == term_id)
            if not comparison_roadmaps.intersection(term["roadmap_ids"]):
                raise ValueError(
                    f"comparison {comparison_id} term {term_id} has no shared roadmap"
                )
            cell_ids = [cell["column_id"] for cell in row["cells"]]
            if len(cell_ids) != len(set(cell_ids)) or set(cell_ids) != set(column_ids):
                raise ValueError(
                    f"comparison {comparison_id} term {term_id} cells do not match columns"
                )
            validate_source_refs(
                row["source_refs"], f"comparison {comparison_id} term {term_id}"
            )

    if include_commit_metadata:
        metadata = source_commit_metadata(root, relative_path)
        projected.update(
            updated_at=metadata["updated_at"],
            source_commit=metadata["commit_sha"],
            source_commit_url=metadata["commit_url"],
        )
    return projected


def collect_public_supplement(
    root: Path,
    policy: dict[str, Any],
    path_key: str,
    fields_key: str,
    bilingual_key: str,
    label: str,
) -> dict[str, Any]:
    """Project one Directive-approved public planning supplement."""
    relative_path = policy[path_key]
    artifact = load_json(root / relative_path)
    directives = approved_publication_directives(root, policy)
    projected = public_projection(
        artifact,
        policy[fields_key],
        policy["required_publication_metadata"],
        policy[bilingual_key],
        directives,
        f"{label} {artifact.get('export_id', relative_path)}",
    )
    metadata = source_commit_metadata(root, relative_path)
    projected.update(
        updated_at=metadata["updated_at"],
        source_commit=metadata["commit_sha"],
        source_commit_url=metadata["commit_url"],
    )
    return projected


def collect_roadmap_assurance(
    root: Path, policy: dict[str, Any]
) -> dict[str, Any]:
    directives = approved_publication_directives(root, policy)
    specifications = (
        (
            "source_audit",
            policy["included_public_roadmap_source_audit"],
            policy["roadmap_source_audit_public_fields"],
            ["method_ja", "method_en", "caveat_ja", "caveat_en"],
        ),
        (
            "source_triage",
            policy["included_public_roadmap_source_triage"],
            policy["roadmap_source_triage_public_fields"],
            ["caveat_ja", "caveat_en"],
        ),
        (
            "evidence_audit",
            policy["included_public_roadmap_evidence_audit"],
            policy["roadmap_evidence_audit_public_fields"],
            ["method_ja", "method_en"],
        ),
        (
            "freshness_audit",
            policy["included_public_roadmap_freshness_audit"],
            policy["roadmap_freshness_audit_public_fields"],
            ["method_ja", "method_en", "caveat_ja", "caveat_en"],
        ),
        (
            "gap_queue",
            policy["included_public_roadmap_gap_queue"],
            policy["roadmap_gap_queue_public_fields"],
            ["method_ja", "method_en", "caveat_ja", "caveat_en"],
        ),
        (
            "center_profile_assurance",
            policy["included_public_center_profile_assurance"],
            policy["center_profile_assurance_public_fields"],
            ["method_ja", "method_en", "caveat_ja", "caveat_en"],
        ),
        (
            "dependency_register",
            policy["included_public_roadmap_dependencies"],
            policy["roadmap_dependency_public_fields"],
            ["title_ja", "title_en", "summary_ja", "summary_en"],
        ),
    )
    assurance: dict[str, Any] = {}
    for key, relative_path, fields, bilingual_fields in specifications:
        path = root / relative_path
        artifact = load_json(path)
        projected = public_projection(
            artifact,
            fields,
            policy["required_publication_metadata"],
            bilingual_fields,
            directives,
            f"roadmap assurance artifact {artifact.get('export_id', path.name)}",
        )
        metadata = source_commit_metadata(root, relative_path)
        projected.update(
            updated_at=metadata["updated_at"],
            source_commit=metadata["commit_sha"],
            source_commit_url=metadata["commit_url"],
        )
        assurance[key] = projected
    return assurance


def build_public_data(root: Path, policy: dict[str, Any]) -> dict[str, Any]:
    from apply_research_unit_update import audit_updates
    update_errors = audit_updates(root)
    if update_errors:
        raise ValueError("Research update provenance failed: " + "; ".join(update_errors))
    baseline = load_json(root / policy["included_catalog"])
    i18n = load_json(root / policy["included_i18n"])
    catalog_taxonomy = load_json(root / "config" / "catalog-taxonomy.json")
    roadmap_portfolio = load_json(root / "config" / "roadmap-portfolio.json")
    technology_scope = load_json(root / "config" / "global-technology-scope.json")
    category_by_topic = {
        topic_id: category["category_id"]
        for category in catalog_taxonomy["categories"]
        for topic_id in category["topic_ids"]
    }
    catalog_code_by_topic = {
        topic_id: catalog_code
        for category in catalog_taxonomy["categories"]
        for topic_id, catalog_code in category["topic_codes"].items()
    }
    roadmap_refs_by_topic: dict[str, list[dict[str, Any]]] = {}
    for family in roadmap_portfolio["roadmap_families"]:
        roadmap_ref = {
            "roadmap_id": family["roadmap_id"],
            "status": family["status"],
            "path": (
                f"roadmaps/{family['slug']}/"
                if family["status"] == "published"
                else None
            ),
            "title_ja": family["title_ja"],
            "title_en": family["title_en"],
        }
        for topic_id in family["source_topic_ids"]:
            roadmap_refs_by_topic.setdefault(topic_id, []).append(roadmap_ref)
    category_by_roadmap = {
        roadmap_id: category["category_id"]
        for category in catalog_taxonomy["categories"]
        for roadmap_id in category["roadmap_ids"]
    }
    initial_ids = set(baseline["initial_catalog"]["topic_ids"])
    valid_topic_ids = {topic["topic_id"] for topic in baseline["topics"]}
    active_topics = [topic for topic in baseline["topics"] if topic["status"] != "retired"]
    consensus_receipts = collect_consensus_receipts(root, policy)
    receipt_by_id = {
        receipt["receipt_id"]: receipt for receipt in consensus_receipts
    }
    research_summaries = collect_topic_summaries(
        root, policy, valid_topic_ids, receipt_by_id
    )
    topic_by_id = {topic["topic_id"]: topic for topic in baseline["topics"]}
    for summary in research_summaries:
        for finding in summary["findings"]:
            finding["catalog_topic_ids"] = current_finding_topics(finding, topic_by_id)
        summary["catalog_topic_ids"] = sorted({
            tid for finding in summary["findings"] for tid in finding["catalog_topic_ids"]
        })
    topic_decision_support = collect_public_supplement(
        root,
        policy,
        "included_public_topic_decision_support",
        "topic_decision_support_public_fields",
        "topic_decision_support_required_bilingual_fields",
        "topic decision support surface",
    )
    active_topic_ids = {topic["topic_id"] for topic in active_topics}
    for profile in topic_decision_support["topic_profiles"]:
        profile["sections"] = [section for section in profile["sections"]
                               if section["section_id"] not in profile.get("archived_section_ids", [])]
    topic_decision_support["topic_profiles"] = [
        profile
        for profile in topic_decision_support["topic_profiles"]
        if profile["topic_id"] in active_topic_ids
    ]
    decision_profile_by_topic = {
        profile["topic_id"]: profile
        for profile in topic_decision_support["topic_profiles"]
    }
    public_finding_ids = {
        finding["finding_id"]
        for summary in research_summaries
        for finding in summary["findings"]
    }
    receipt_finding_ids = {
        finding_id
        for receipt in consensus_receipts
        for finding_id in receipt["finding_ids"]
    }
    unlinked_receipts = receipt_finding_ids - public_finding_ids
    if unlinked_receipts:
        raise ValueError(
            "Consensus Receipts reference unpublished Findings: "
            f"{sorted(unlinked_receipts)}"
        )
    topics = []
    for topic in active_topics:
        decision_profile = decision_profile_by_topic.get(topic["topic_id"])
        decision_item_count = sum(
            len(section["items"])
            for section in decision_profile["sections"]
        ) if decision_profile else 0
        summary_count = sum(
            topic["topic_id"] in summary["catalog_topic_ids"]
            for summary in research_summaries
        )
        finding_count = sum(
            topic["topic_id"] in finding["catalog_topic_ids"]
            for summary in research_summaries
            for finding in summary["findings"]
        )
        topics.append(
            {
                "topic_id": topic["topic_id"],
                "catalog_code": catalog_code_by_topic[topic["topic_id"]],
                "domain": topic["domain"],
                "catalog_category_id": category_by_topic[topic["topic_id"]],
                "title_ja": topic["title_ja"],
                "title_en": i18n["topic_titles_en"][topic["topic_id"]],
                "summary_ja": topic.get("summary_ja", ""),
                "summary_en": topic.get("summary_en", ""),
                "research_units": [
                    {key: unit[key] for key in (
                        "unit_id", "title_ja", "title_en", "question_ja", "question_en",
                        "status", "evidence_section_ids", "latest_update_id", "last_researched_at",
                    ) if key in unit}
                    for unit in topic.get("research_units", [])
                ],
                "related_topic_ids": topic.get("related_topic_ids", []),
                "status": topic["status"],
                "verification_status": (
                    "consensus-verified"
                    if decision_profile and topic_decision_support["consensus_status"] == "accepted"
                    else "independent-review-pending"
                    if decision_profile
                    else "evidence-collected"
                    if finding_count
                    else "not-yet-reviewed"
                ),
                "last_updated_at": (
                    topic_decision_support["updated_at"] if decision_profile else None
                ),
                "last_updated_commit_url": (
                    topic_decision_support["source_commit_url"] if decision_profile else None
                ),
                "coverage_gap_count": (
                    len(decision_profile["coverage_gap_ids"])
                    if decision_profile
                    else 0
                ),
                "research_summary_count": summary_count,
                "research_finding_count": finding_count,
                "decision_item_count": decision_item_count,
                "related_roadmaps": roadmap_refs_by_topic.get(topic["topic_id"], []),
            }
        )

    scenarios = collect_scenarios(root, policy)
    scenario_budget_references = collect_scenario_budget_references(root, policy)
    procurement_register, budget_planning = collect_procurement_costs(root, policy)
    for scenario in scenarios:
        options = scenario["budget_options"]
        expected_levels = budget_planning["budget_ceilings_oku_jpy"]
        if [o.get("tier") for o in options] != [f"jpy-{v}" for v in expected_levels]:
            raise ValueError("scenario budget levels disagree with budget planning config")
        for option, ceiling in zip(options, expected_levels):
            expected = allocate_budget(budget_planning, scenario["scenario_id"], ceiling,
                                       budget_planning["default_deployment_year"])
            if option.get("budget_allocation") != expected:
                raise ValueError("scenario budget allocation is stale or unsupported")
            if any(c["quantity"] is not None for c in option["components"]):
                raise ValueError("uncalibrated procurement model cannot publish node quantities")
            if any(option["aggregate"][key] is not None
                   for key in ("cpu_nodes", "accelerator_nodes", "accelerators", "storage_pb")):
                raise ValueError("uncalibrated procurement model cannot publish system totals")
    consensus_packages = collect_consensus_packages(root, policy)
    reports = collect_reports(root, policy)
    roadmap_artifacts = collect_roadmaps(root, policy)
    topic_ref_by_id = {
        topic["topic_id"]: {
            "topic_id": topic["topic_id"],
            "catalog_code": topic["catalog_code"],
            "title_ja": topic["title_ja"],
            "title_en": topic["title_en"],
        }
        for topic in topics
    }
    family_by_roadmap = {
        family["roadmap_id"]: family for family in roadmap_portfolio["roadmap_families"]
    }
    for roadmap in roadmap_artifacts:
        family = family_by_roadmap[roadmap["roadmap_id"]]
        roadmap["related_topics"] = [
            topic_ref_by_id[topic_id]
            for topic_id in family["source_topic_ids"]
            if topic_id in topic_ref_by_id
        ]
    roadmap_reference_data = collect_roadmap_reference_data(
        root, policy, roadmap_artifacts, catalog_sources=topic_decision_support["sources"]
    )
    hpci_system_inventory = collect_public_supplement(
        root,
        policy,
        "included_public_hpci_system_inventory",
        "hpci_system_inventory_public_fields",
        "hpci_system_inventory_required_bilingual_fields",
        "HPCI system inventory",
    )
    link_inventory_evidence(hpci_system_inventory, procurement_register, roadmap_artifacts)
    application_performance_forecasts = collect_public_supplement(
        root,
        policy,
        "included_public_application_performance_forecasts",
        "application_performance_forecast_public_fields",
        "application_performance_forecast_required_bilingual_fields",
        "application performance forecast surface",
    )
    planning_evidence_readiness = collect_public_supplement(
        root,
        policy,
        "included_public_planning_evidence_readiness",
        "planning_evidence_readiness_public_fields",
        "planning_evidence_readiness_required_bilingual_fields",
        "planning evidence readiness",
    )
    roadmap_assurance = collect_roadmap_assurance(root, policy)
    roadmaps = [
        roadmap_index_entry(roadmap, category_by_roadmap)
        for roadmap in roadmap_artifacts
    ]
    for roadmap in roadmaps:
        roadmap["related_topics"] = roadmap_artifacts[
            next(
                index
                for index, artifact in enumerate(roadmap_artifacts)
                if artifact["roadmap_id"] == roadmap["roadmap_id"]
            )
        ]["related_topics"]
    roadmaps.sort(key=lambda item: item["updated_at"], reverse=True)
    site_metadata = source_commit_metadata(root)
    official_sources = [
        source for source in baseline["source_corpus"]
        if source.get("availability") == "registered-public-url"
    ]
    return {
        "schema_version": "0.2.0",
        "catalog_as_of": baseline["derived_at"],
        "conference_coverage": collect_conference_coverage(root, policy),
        "site": site_metadata,
        "baseline": {
            "baseline_id": baseline["baseline_id"],
            "catalog_revision": baseline["catalog_revision"],
            "topic_count": len(topics),
            "historical_topic_count": len(baseline["topics"]),
            "protected_initial_count": len(initial_ids),
            "official_source_count": len(official_sources),
            "complete": baseline["complete"],
            "open_gap_ids": baseline["open_gap_ids"],
        },
        "topics": topics,
        "catalog_aliases": catalog_aliases(root, baseline, i18n, catalog_code_by_topic),
        "catalog_taxonomy": catalog_taxonomy,
        "research_summaries": research_summaries,
        "topic_decision_support": topic_decision_support,
        "consensus_receipts": consensus_receipts,
        "consensus_packages": consensus_packages,
        "technology_landscape": {
            "scope_id": technology_scope["scope_id"],
            "categories": [
                {"ja": ja, "en": en}
                for ja, en in zip(
                    i18n["technology_landscape"]["technology_categories_ja"],
                    technology_scope["technology_categories"],
                    strict=True,
                )
            ],
            "evaluation_dimensions": technology_scope["required_evaluation_dimensions"],
        },
        "roadmap_artifacts": roadmap_artifacts,
        "roadmap_reference_data": roadmap_reference_data,
        "hpci_system_inventory": hpci_system_inventory,
        "application_performance_forecasts": application_performance_forecasts,
        "planning_evidence_readiness": planning_evidence_readiness,
        "roadmap_assurance": roadmap_assurance,
        "roadmaps": roadmaps,
        "scenarios": scenarios,
        "scenario_budget_references": scenario_budget_references,
        "procurement_register": procurement_register,
        "budget_planning": budget_planning,
        "reports": reports,
        "publication": {
            "policy_id": policy["policy_id"],
            "information_plane": policy["information_plane"],
            "license_status": policy["license_status"],
            "license": policy["license"],
            "repository_url": REPOSITORY_URL,
        },
    }


def copy_brand_assets(root: Path, output: Path) -> None:
    source = root / "assets" / "branding"
    destination = output / "assets" / "branding"
    destination.mkdir(parents=True, exist_ok=True)
    # Publish selected artwork only, not concept documents or design archives.
    for filename in PUBLIC_BRAND_ASSETS:
        shutil.copy2(source / filename, destination / filename)


def build(root: Path, output: Path) -> dict[str, Any]:
    policy = load_json(root / "config" / "publication-policy.json")
    source = root / policy["site_source"]
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for filename in ("styles.css", "app.js", "roadmaps.js", "planning.js", "budget-planning.js", "search.js", "feedback.js", "conferences.js"):
        shutil.copy2(source / filename, output / filename)
    copy_brand_assets(root, output)
    data_dir = output / "data"
    data_dir.mkdir()
    public_data = build_public_data(root, policy)
    asset_version = public_data["site"]["commit_sha"]
    (output / "index.html").write_text(
        render_template(
            source / "index.html",
            {"ASSET_VERSION": asset_version},
        ),
        encoding="utf-8",
    )
    serialized = json.dumps(public_data, ensure_ascii=False, separators=(",", ":"))
    (data_dir / "openfs-public.js").write_text(
        f"window.OPENFS_PUBLIC_DATA={serialized};\n", encoding="utf-8"
    )
    search_index = output / "search" / "index.html"
    conference_index = output / "conferences" / "hot-chips-2026" / "index.html"
    conference_index.parent.mkdir(parents=True)
    conference_index.write_text(render_template(
        source / "conference-detail.html",
        {"ROOT_PREFIX": "../../", "ASSET_VERSION": asset_version}), encoding="utf-8")
    search_index.parent.mkdir(parents=True)
    search_index.write_text(
        render_template(
            source / "search.html",
            {"ROOT_PREFIX": "../", "ASSET_VERSION": asset_version},
        ),
        encoding="utf-8",
    )
    feedback_index = output / "feedback" / "index.html"
    feedback_index.parent.mkdir(parents=True)
    feedback_index.write_text(
        render_template(
            source / "feedback.html",
            {"ROOT_PREFIX": "../", "ASSET_VERSION": asset_version},
        ),
        encoding="utf-8",
    )
    roadmap_index = output / "roadmaps" / "index.html"
    roadmap_index.parent.mkdir(parents=True)
    roadmap_index.write_text(
        render_template(
            source / "roadmaps-index.html",
            {"ROOT_PREFIX": "../", "ASSET_VERSION": asset_version},
        ),
        encoding="utf-8",
    )
    comparison = output / "roadmaps" / "compare" / "index.html"
    comparison.parent.mkdir(parents=True)
    comparison.write_text(
        render_template(
            source / "roadmaps-compare.html",
            {"ROOT_PREFIX": "../../", "ASSET_VERSION": asset_version},
        ),
        encoding="utf-8",
    )
    assurance = output / "roadmaps" / "evidence" / "index.html"
    assurance.parent.mkdir(parents=True)
    assurance.write_text(
        render_template(
            source / "roadmap-evidence.html",
            {"ROOT_PREFIX": "../../", "ASSET_VERSION": asset_version},
        ),
        encoding="utf-8",
    )
    detail_template = source / "roadmap-detail.html"
    for roadmap in public_data["roadmaps"]:
        detail = output / "roadmaps" / roadmap["slug"] / "index.html"
        detail.parent.mkdir(parents=True)
        depth = len(detail.parent.relative_to(output).parts)
        root_prefix = "../" * depth
        detail.write_text(
            render_template(
                detail_template,
                {
                    "ROOT_PREFIX": root_prefix,
                    "ROADMAP_ID": html.escape(roadmap["export_id"], quote=True),
                    "ASSET_VERSION": asset_version,
                },
            ),
            encoding="utf-8",
        )
    scenarios_index = output / "scenarios" / "index.html"
    scenarios_index.parent.mkdir(parents=True, exist_ok=True)
    scenarios_index.write_text(
        render_template(
            source / "scenarios-index.html",
            {"ROOT_PREFIX": "../", "ASSET_VERSION": asset_version},
        ),
        encoding="utf-8",
    )
    consensus_index = output / "consensus" / "index.html"
    consensus_index.parent.mkdir(parents=True, exist_ok=True)
    consensus_index.write_text(
        render_template(
            source / "consensus-index.html",
            {"ROOT_PREFIX": "../", "ASSET_VERSION": asset_version},
        ),
        encoding="utf-8",
    )
    consensus_template = source / "consensus-detail.html"
    for package in public_data["consensus_packages"]:
        detail = output / package["path"] / "index.html"
        detail.parent.mkdir(parents=True, exist_ok=True)
        depth = len(detail.parent.relative_to(output).parts)
        detail.write_text(
            render_template(
                consensus_template,
                {
                    "ROOT_PREFIX": "../" * depth,
                    "PACKAGE_ID": html.escape(package["package_id"], quote=True),
                    "ASSET_VERSION": asset_version,
                },
            ),
            encoding="utf-8",
        )
    scenario_template = source / "scenario-detail.html"
    for scenario in public_data["scenarios"]:
        detail = output / scenario["path"] / "index.html"
        detail.parent.mkdir(parents=True, exist_ok=True)
        depth = len(detail.parent.relative_to(output).parts)
        detail.write_text(
            render_template(
                scenario_template,
                {
                    "ROOT_PREFIX": "../" * depth,
                    "SCENARIO_ID": html.escape(scenario["scenario_id"], quote=True),
                    "ASSET_VERSION": asset_version,
                },
            ),
            encoding="utf-8",
        )
    (output / ".nojekyll").write_text("", encoding="utf-8")
    return public_data


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    args = parser.parse_args()
    result = build(ROOT, args.output)
    print(
        f"Built OpenFS Pages: topics={len(result['topics'])}, "
        f"summaries={len(result['research_summaries'])}, "
        f"receipts={len(result['consensus_receipts'])}, "
        f"consensus_packages={len(result['consensus_packages'])}, "
        f"roadmaps={len(result['roadmaps'])}, "
        f"scenarios={len(result['scenarios'])}, reports={len(result['reports'])}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
