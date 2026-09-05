#!/usr/bin/env python3
"""Run dependency-free structural checks for the OpenFS repository."""

from __future__ import annotations

import json
import re
import sys
import hashlib
from pathlib import Path
from typing import Any

from openfs_runtime import exception_group_key, language_in_scope, stable_digest
from register_source import canonicalize_url, publisher_authority
from generate_knowledge_views import build_index, render_tbd
from build_source_catalog_map import build as build_source_catalog_map
from catalog_lineage import validate_catalog_scope


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "README.md",
    "README.ja.md",
    "AGENTS.md",
    ".github/CODEOWNERS",
    "LICENSE",
    "NOTICE",
    "THIRD_PARTY_NOTICES.md",
    "requirements-validation.txt",
    "docs/agent-onboarding.md",
    "docs/architecture.md",
    "docs/research-baseline/README.md",
    "docs/research-baseline/source-corpus.md",
    "docs/research-baseline/fs2-fs3-corpus-review.md",
    "docs/research-baseline/topic-inheritance.md",
    "docs/research-baseline/gap-register.md",
    "docs/research-baseline/performance-model-validation.md",
    "docs/research-baseline/reproducible-benchmark-results.md",
    "docs/research-baseline/privacy-preserving-workload-observations.md",
    "docs/research-baseline/portability-capability-matrices.md",
    "docs/research-baseline/planning-evidence-integration.md",
    "proposals/portability-capability-matrices/README.md",
    "docs/planning/scenario-generation.md",
    "docs/planning/roadmap-portfolio.md",
    "docs/planning/university-center-baseline.md",
    "docs/planning/presentation-mechanism.md",
    "docs/publication/github-pages.md",
    "docs/operations/automation-setup.md",
    "docs/operations/production-readiness.md",
    "docs/operations/provider-worker-protocol.md",
    "docs/governance/license-decision.md",
    "docs/research-baseline/ai-topic-promotion.md",
    "docs/research-baseline/source-watch-and-evidence-map.md",
    "knowledge/README.md",
    "knowledge/public/README.md",
    "knowledge/public/topic-summaries.json",
    "knowledge/public/consensus-receipts.json",
    "knowledge/public/hpci-system-inventory.json",
    "knowledge/public/application-performance-forecasts.json",
    "knowledge/public/planning-evidence-readiness.json",
    "knowledge/public/fs3-decision-evidence.json",
    "knowledge/public/source-catalog-map.json",
    "reports/exports/index.json",
    "reports/exports/20260906_001_fs3-system-planning-evidence.md",
    "knowledge/public/roadmaps/compute-nodes-accelerators.json",
    "knowledge/public/roadmaps/interconnect-optics-disaggregation.json",
    "knowledge/public/roadmaps/memory-data-movement.json",
    "knowledge/public/roadmaps/portability-compilers-tuning.json",
    "knowledge/public/roadmaps/reference-blueprint-centers.json",
    "knowledge/public/roadmaps/workloads-benchmarks-models.json",
    "knowledge/public/audits/roadmap-gap-queue.json",
    "knowledge/public/audits/center-profile-assurance.json",
    "knowledge/claim-status/README.md",
    "knowledge/claims/index.json",
    "docs/policies/claim-acceptance.md",
    "docs/policies/information-boundary.md",
    "docs/policies/consensus-policy.md",
    "docs/policies/research-web-access.md",
    "docs/policies/language-and-terminology.md",
    "docs/security/threat-model.md",
    "docs/security/research-web-security-model.md",
    "config/consensus-policy.json",
    "config/acquisition-policy.json",
    "config/source-registry.json",
    "config/source-watch-registry.json",
    "config/agent-registry.json",
    "config/skill-registry.json",
    "config/role-permissions.json",
    "config/research-baseline.json",
    "config/catalog-taxonomy.json",
    "config/roadmap-portfolio.json",
    "config/scenario-policy.json",
    "config/global-technology-scope.json",
    "config/hpci-center-registry.json",
    "config/publication-policy.json",
    "config/publication-i18n.json",
    "config/activation-policy.json",
    "config/owner-controls.json",
    "config/roadmap-gap-query-overrides.json",
    "config/research-web-security-policy.json",
    "config/execution-security-profiles.json",
    "schemas/proposal.schema.json",
    "schemas/claim.schema.json",
    "schemas/canonical-claim.schema.json",
    "schemas/canonical-claim-status.schema.json",
    "schemas/knowledge-index.schema.json",
    "schemas/promotion-readiness.schema.json",
    "schemas/cost-summary.schema.json",
    "schemas/claim-proposal.schema.json",
    "schemas/source-lineage.schema.json",
    "schemas/source-watch-registry.schema.json",
    "schemas/source-catalog-map.schema.json",
    "schemas/assessment.schema.json",
    "schemas/decision.schema.json",
    "schemas/run.schema.json",
    "schemas/skill-registry.schema.json",
    "schemas/work-item.schema.json",
    "schemas/query-receipt.schema.json",
    "schemas/source-receipt.schema.json",
    "schemas/source-discovery-result.schema.json",
    "schemas/discovery-no-result.schema.json",
    "schemas/evidence.schema.json",
    "schemas/evidence-bundle.schema.json",
    "schemas/coverage-report.schema.json",
    "schemas/change-report.schema.json",
    "schemas/dependency-impact.schema.json",
    "schemas/consensus-readiness.schema.json",
    "schemas/weekly-digest.schema.json",
    "schemas/issue-payload.schema.json",
    "schemas/directive-application.schema.json",
    "schemas/run-brief.schema.json",
    "schemas/weekly-cycle.schema.json",
    "schemas/handoff.schema.json",
    "schemas/research-baseline.schema.json",
    "schemas/catalog-taxonomy.schema.json",
    "schemas/roadmap-portfolio.schema.json",
    "schemas/center-profile.schema.json",
    "schemas/center-profile-coverage.schema.json",
    "schemas/center-profile-assurance.schema.json",
    "schemas/followup-effectiveness.schema.json",
    "schemas/profile-continuity.schema.json",
    "schemas/temporal-integrity.schema.json",
    "schemas/center-research-brief.schema.json",
    "schemas/center-followup-plan.schema.json",
    "schemas/global-followup-plan.schema.json",
    "schemas/global-followup-effectiveness.schema.json",
    "schemas/run-approval.schema.json",
    "schemas/monitor-readiness.schema.json",
    "schemas/activation-policy.schema.json",
    "schemas/owner-controls.schema.json",
    "schemas/operational-readiness.schema.json",
    "schemas/worker-invocation.schema.json",
    "schemas/worker-result.schema.json",
    "schemas/hpci-center-registry.schema.json",
    "schemas/system-scenario.schema.json",
    "schemas/published-scenario-set.schema.json",
    "schemas/research-topic-proposal.schema.json",
    "schemas/public-topic-summary.schema.json",
    "schemas/public-consensus-receipt.schema.json",
    "schemas/public-roadmap.schema.json",
    "schemas/public-hpci-system-inventory.schema.json",
    "schemas/public-application-performance-forecast.schema.json",
    "schemas/planning-evidence-readiness.schema.json",
    "schemas/fs3-decision-evidence.schema.json",
    "schemas/roadmap-reference-data.schema.json",
    "knowledge/public/roadmap-reference-data.json",
    "schemas/roadmap-freshness-audit.schema.json",
    "schemas/roadmap-gap-queue.schema.json",
    "schemas/roadmap-gap-query-overrides.schema.json",
    "schemas/performance-model-card.schema.json",
    "schemas/benchmark-result-bundle.schema.json",
    "schemas/agent-evaluation-bundle.schema.json",
    "schemas/agent-evaluation-policy.schema.json",
    "schemas/agent-evaluation-readiness.schema.json",
    "schemas/agent-evaluation-task-suite.schema.json",
    "schemas/agent-evaluation-task-output.schema.json",
    "schemas/workload-observation-summary.schema.json",
    "schemas/portability-capability-matrix.schema.json",
    "schemas/roadmap-dependency-register.schema.json",
    "schemas/research-web-security-policy.schema.json",
    "schemas/execution-security-profile.schema.json",
    "schemas/web-retrieval-receipt.schema.json",
    "skills/source-discovery/SKILL.md",
    "skills/worldwide-technology-survey/SKILL.md",
    "skills/evidence-extraction/SKILL.md",
    "skills/structured-synthesis/SKILL.md",
    "skills/roadmap-planning/SKILL.md",
    "skills/source-validation/SKILL.md",
    "skills/falsification-review/SKILL.md",
    "docs/tasks/OFS-002.md",
    "docs/tasks/OFS-003.md",
    "docs/tasks/OFS-004.md",
    "docs/tasks/OFS-005.md",
    "config/monitors/MON-FS-BASELINE-001.json",
    "config/monitors/MON-HPCI-CENTERS-001.json",
    "config/monitors/MON-EMERGING-TOPICS-001.json",
    "config/monitors/MON-GLOBAL-TECH-001.json",
    "config/monitors/MON-AUTO-TOPICS-001.json",
    "evals/scenarios/candidate-scenarios.json",
    "tools/generate_scenario_views.py",
    "tools/validate_json_schemas.py",
    "tools/validate_readme_i18n.py",
    "tools/validate_workflows.py",
    "tools/promote_research_topic.py",
    "tools/promote_claim.py",
    "tools/record_claim_status.py",
    "tools/generate_knowledge_views.py",
    "tools/evaluate_promotion_readiness.py",
    "tools/expand_topic_monitor.py",
    "tools/build_pages_site.py",
    "tools/build_source_catalog_map.py",
    "tools/build_roadmap_freshness_audit.py",
    "tools/build_roadmap_gap_queue.py",
    "tools/build_p0_roadmap_wave.py",
    "tools/build_p0_dependency_wave.py",
    "tools/build_center_profile_assurance.py",
    "tools/check_performance_model_card.py",
    "tools/check_benchmark_result_bundle.py",
    "tools/check_workload_observation_summary.py",
    "tools/check_portability_capability_matrix.py",
    "tools/check_public_planning_surfaces.py",
    "tools/check_public_language.py",
    "tools/check_scenario_portfolio.py",
    "tools/check_research_web_security.py",
    "tools/check_roadmap_dependency_register.py",
    "tools/openfs_runtime.py",
    "tools/run_controller.py",
    "tools/ingest_directive.py",
    "tools/register_source.py",
    "tools/register_no_result.py",
    "tools/extract_evidence.py",
    "tools/propose_claim.py",
    "tools/create_assessment.py",
    "tools/consensus_gate.py",
    "tools/evaluate_coverage.py",
    "tools/evaluate_center_profiles.py",
    "tools/evaluate_followup_effectiveness.py",
    "tools/evaluate_profile_continuity.py",
    "tools/evaluate_temporal_integrity.py",
    "tools/generate_center_research_brief.py",
    "tools/generate_center_followup_plan.py",
    "tools/generate_global_followup_plan.py",
    "tools/evaluate_global_followup_effectiveness.py",
    "tools/propose_center_profile.py",
    "tools/detect_source_changes.py",
    "tools/analyze_dependency_impact.py",
    "tools/check_consensus_readiness.py",
    "tools/generate_weekly_digest.py",
    "tools/prepare_exception_issues.py",
    "tools/prepare_freshness_issue.py",
    "tools/apply_directive.py",
    "tools/generate_run_brief.py",
    "tools/prepare_weekly_cycle.py",
    "tools/publish_github_issue.py",
    "tools/create_handoff.py",
    "tools/accept_handoff.py",
    "tools/process_pending_handoffs.py",
    "tools/publish_control_pr.py",
    "tools/prepare_claim_promotions.py",
    "tools/publish_promotion_pr.py",
    "tools/evaluate_monitor_readiness.py",
    "tools/evaluate_operational_readiness.py",
    "tools/prepare_worker_invocation.py",
    "tools/accept_worker_result.py",
    "tools/prepare_run_approval.py",
    "queue/README.md",
    "runs/README.md",
    "state/README.md",
    "reviews/exceptions/README.md",
    "reviews/digests/README.md",
    "reviews/issues/README.md",
    "reviews/briefs/README.md",
    "reviews/followups/README.md",
    "reviews/run-approvals/README.md",
    "handoffs/README.md",
    "proposals/center-profiles/README.md",
    "proposals/benchmark-results/README.md",
    "proposals/agent-evaluations/README.md",
    "docs/research-baseline/agent-harness-evaluation.md",
    "tools/check_agent_evaluation_bundle.py",
    "tools/check_agent_evaluation_task_suite.py",
    "tools/evaluate_agent_evaluation_readiness.py",
    "evals/agent-harness/public-pilot-suite.json",
    "config/agent-evaluation-policy.json",
    "proposals/workload-observations/README.md",
    "site/index.html",
    "site/styles.css",
    "site/app.js",
    ".github/workflows/pages.yml",
    ".github/workflows/weekly-coordinator.yml",
    ".github/workflows/handoff-control.yml",
    ".github/workflows/weekly-review.yml",
    ".github/workflows/claim-promotion.yml",
]
ACTION_PATTERN = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)", re.MULTILINE)
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def usage_summary_from_items(items: list[dict[str, Any]]) -> dict[str, Any]:
    completed = [item for item in items if item.get("status") == "completed"]
    cost_values = [
        item.get("usage", {}).get("cost_usd")
        for item in completed
        if item.get("usage", {}).get("cost_usd") is not None
    ]
    reported = len(cost_values)
    if not completed or reported == 0:
        measurement_status = "unreported"
    elif reported == len(completed):
        measurement_status = "complete"
    else:
        measurement_status = "partial"

    def token_total(name: str) -> int | None:
        values = [
            item.get("usage", {}).get(name)
            for item in completed
            if item.get("usage", {}).get(name) is not None
        ]
        return sum(values) if values else None

    return {
        "currency": "USD",
        "measurement_status": measurement_status,
        "reported_total_usd": sum(cost_values) if cost_values else None,
        "reported_executions": reported,
        "unreported_executions": len(completed) - reported,
        "reported_input_tokens": token_total("input_tokens"),
        "reported_output_tokens": token_total("output_tokens"),
    }


def validate_json_files(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(root.rglob("*.json")):
        if ".git" in path.parts:
            continue
        try:
            load_json(path)
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON: {path.relative_to(root)}: {exc}")
    return errors


def validate_jsonl_files(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted(root.rglob("*.jsonl")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append(
                    f"invalid JSONL: {path.relative_to(root)}:{line_number}: {exc}"
                )
    return errors


def validate_run_approvals(root: Path) -> list[str]:
    errors: list[str] = []
    approval_ids: set[str] = set()
    required = {
        "schema_version",
        "approval_id",
        "run_id",
        "monitor_id",
        "status",
        "manifest_digest",
        "brief_ref",
        "brief_digest",
        "prepared_at",
        "reviewed_by",
        "reviewed_at",
        "checks",
        "notes",
    }
    required_checks = {
        "public_information_boundary",
        "citation_sample",
        "coverage",
        "false_positive_review",
        "dissent_review",
        "cost_review",
    }
    for path in sorted((root / "reviews" / "run-approvals").glob("RUN-*.json")):
        approval = load_json(path)
        missing = required - set(approval)
        if missing:
            errors.append(
                f"Run approval lacks required fields: {path.relative_to(root)}: {sorted(missing)}"
            )
            continue
        if path.stem != approval["run_id"]:
            errors.append(f"Run approval filename differs from run ID: {path.relative_to(root)}")
        approval_id = approval["approval_id"]
        if approval_id in approval_ids:
            errors.append(f"duplicate Run approval ID: {approval_id}")
        approval_ids.add(approval_id)
        checks = approval.get("checks", {})
        if set(checks) != required_checks or not all(
            isinstance(value, bool) for value in checks.values()
        ):
            errors.append(f"Run approval checks are incomplete: {path.relative_to(root)}")
        manifest_path = root / "runs" / approval["run_id"] / "manifest.json"
        brief_ref = Path(approval["brief_ref"])
        brief_path = root / brief_ref
        if not manifest_path.is_file():
            errors.append(f"Run approval manifest is missing: {path.relative_to(root)}")
        if (
            brief_ref.is_absolute()
            or ".." in brief_ref.parts
            or brief_ref.parts[:2] != ("reviews", "briefs")
            or not brief_path.is_file()
        ):
            errors.append(f"Run approval Brief reference is invalid: {path.relative_to(root)}")
        if approval["status"] == "reviewed-pass":
            if manifest_path.is_file() and stable_digest(load_json(manifest_path)) != approval[
                "manifest_digest"
            ]:
                errors.append(f"passing Run approval manifest digest differs: {path.relative_to(root)}")
            if brief_path.is_file() and stable_digest(load_json(brief_path)) != approval[
                "brief_digest"
            ]:
                errors.append(f"passing Run approval Brief digest differs: {path.relative_to(root)}")
    return errors


def validate_issue_payloads(root: Path) -> list[str]:
    errors: list[str] = []
    seen_groups: set[str] = set()
    for path in sorted((root / "reviews" / "issues" / "groups").glob("*.json")):
        payload = load_json(path)
        group_id = payload.get("exception_group_id")
        if not group_id or path.stem != group_id:
            errors.append(f"Issue group filename differs from identity: {path.relative_to(root)}")
            continue
        if group_id in seen_groups:
            errors.append(f"duplicate Issue group identity: {group_id}")
        seen_groups.add(group_id)
        exception_refs = payload.get("exception_refs", [])
        exceptions = []
        for ref in exception_refs:
            ref_path = root / ref
            if not ref_path.is_file():
                errors.append(f"Issue group Exception is missing: {path.relative_to(root)}: {ref}")
                continue
            exceptions.append(load_json(ref_path))
        if not exceptions:
            errors.append(f"Issue group has no Exception records: {path.relative_to(root)}")
            continue
        fingerprints = {exception_group_key(item) for item in exceptions}
        if len(fingerprints) != 1:
            errors.append(f"Issue group mixes owner actions: {path.relative_to(root)}")
            continue
        kind, unmet, publication_blocked = fingerprints.pop()
        expected_id = f"EXCGRP-{stable_digest({'exception_kind': kind, 'unmet_requirements': list(unmet), 'publication_blocked': publication_blocked})[:12].upper()}"
        if group_id != expected_id:
            errors.append(f"Issue group fingerprint differs: {path.relative_to(root)}")
        if payload.get("exception_ids") != sorted(
            item["exception_id"] for item in exceptions
        ):
            errors.append(f"Issue group Exception IDs differ: {path.relative_to(root)}")
        if payload.get("run_ids") != sorted({item["run_id"] for item in exceptions}):
            errors.append(f"Issue group Run IDs differ: {path.relative_to(root)}")
        active = any(
            item.get("status") == "open"
            and item.get("requires_owner_action", True)
            for item in exceptions
        )
        if payload.get("desired_issue_state") != ("open" if active else "closed"):
            errors.append(f"Issue group desired state differs: {path.relative_to(root)}")
        if payload.get("deduplication_marker") != (
            f"<!-- openfs-exception-group:{group_id} -->"
        ):
            errors.append(f"Issue group marker differs: {path.relative_to(root)}")
    return errors


def validate_schema_headers(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted((root / "schemas").glob("*.schema.json")):
        schema = load_json(path)
        for key in ("$schema", "$id", "title", "type"):
            if key not in schema:
                errors.append(f"schema missing {key}: {path.relative_to(root)}")
    return errors


def validate_workflow_action_pins(root: Path) -> list[str]:
    errors: list[str] = []
    workflow_dir = root / ".github" / "workflows"
    if not workflow_dir.exists():
        return errors
    for path in sorted(workflow_dir.glob("*.yml")):
        for reference in ACTION_PATTERN.findall(path.read_text(encoding="utf-8")):
            if reference.startswith("./"):
                continue
            if "@" not in reference:
                errors.append(f"action has no version: {path.relative_to(root)}: {reference}")
                continue
            action, revision = reference.rsplit("@", 1)
            if not FULL_SHA.fullmatch(revision):
                errors.append(
                    f"action is not pinned to a full SHA: {path.relative_to(root)}: "
                    f"{action}@{revision}"
                )
    return errors


def validate_required_files(root: Path) -> list[str]:
    return [f"missing required file: {path}" for path in REQUIRED_FILES if not (root / path).is_file()]


def validate_consensus_configuration(root: Path) -> list[str]:
    policy = load_json(root / "config" / "consensus-policy.json")
    required_rule_fields = {
        "minimum_assessments",
        "minimum_support",
        "minimum_support_independence_groups",
        "minimum_origin_groups",
    }
    errors: list[str] = []
    for object_type, rule in policy.get("rules", {}).items():
        missing = required_rule_fields - set(rule)
        if missing:
            errors.append(f"consensus rule {object_type} missing: {sorted(missing)}")
        if rule.get("minimum_support", 0) > rule.get("minimum_assessments", 0):
            errors.append(f"consensus rule {object_type} requires more support than assessments")
    if policy.get("rules", {}).get("claim", {}).get("minimum_publisher_groups", 0) < 2:
        errors.append("claim consensus requires at least two publisher groups")
    return errors


def validate_runtime_configuration(root: Path) -> list[str]:
    errors: list[str] = []
    budgets = load_json(root / "config" / "budgets.json")
    defaults = budgets.get("defaults", {})
    for key in (
        "maximum_run_minutes",
        "maximum_work_items",
        "maximum_retries_per_work_item",
        "maximum_parallel_agents",
        "maximum_sources_per_monitor",
    ):
        value = defaults.get(key)
        if not isinstance(value, int) or value < 0:
            errors.append(f"runtime budget must be a non-negative integer: {key}")
    kill_switch = budgets.get("kill_switch", {})
    if kill_switch.get("enabled") is not True or kill_switch.get("control_path") != "state/STOP":
        errors.append("runtime kill switch must use state/STOP")
    registry = load_json(root / "config" / "agent-registry.json")
    agent_ids = [agent.get("agent_id") for agent in registry.get("agents", [])]
    if len(agent_ids) != len(set(agent_ids)):
        errors.append("agent registry has duplicate agent IDs")
    orchestrators = [
        agent for agent in registry.get("agents", []) if agent.get("role") == "orchestrator"
    ]
    if len(orchestrators) != 1:
        errors.append("agent registry must define exactly one control-plane orchestrator template")
    configured_identities: dict[tuple[str, str, str], str] = {}
    for agent in registry.get("agents", []):
        identity = (
            agent.get("provider", ""),
            agent.get("model_family", ""),
            agent.get("prompt_profile", ""),
        )
        group = agent.get("agent_independence_group")
        if agent.get("enabled") and "unconfigured" in identity:
            errors.append(f"enabled agent has unconfigured identity: {agent.get('agent_id')}")
        if (
            agent.get("enabled")
            and agent.get("role") in {"discovery", "extraction", "validator", "critic", "synthesis"}
            and str(agent.get("model_id", "unconfigured")).lower() in {"", "none", "unconfigured"}
        ):
            errors.append(f"enabled provider agent lacks a requested model ID: {agent.get('agent_id')}")
        if agent.get("enabled") and agent.get("role") in {"validator", "critic"}:
            review_provenance = {
                "review_origin_group": agent.get("review_origin_group"),
                "harness_id": agent.get("harness_id"),
                "harness_repository_url": agent.get("harness_repository_url"),
                "harness_commit": agent.get("harness_commit"),
            }
            missing = sorted(key for key, value in review_provenance.items() if not value)
            if missing:
                errors.append(
                    f"enabled reviewer lacks pinned review provenance: {agent.get('agent_id')} ({', '.join(missing)})"
                )
            elif not re.fullmatch(r"HAR-[A-Z0-9-]+", review_provenance["harness_id"]):
                errors.append(f"enabled reviewer has invalid harness ID: {agent.get('agent_id')}")
            elif not re.fullmatch(r"https://[^\s]+", review_provenance["harness_repository_url"]):
                errors.append(f"enabled reviewer has invalid harness repository URL: {agent.get('agent_id')}")
            elif not re.fullmatch(r"[0-9a-f]{40}", review_provenance["harness_commit"]):
                errors.append(f"enabled reviewer has invalid harness commit: {agent.get('agent_id')}")
        if "unconfigured" in identity or not all(identity) or not group:
            continue
        previous = configured_identities.setdefault(identity, group)
        if previous != group:
            errors.append(
                "same provider/model/prompt identity is split across independence groups: "
                f"{agent.get('agent_id')}"
            )
    skill_registry = load_json(root / "config" / "skill-registry.json")
    skills = skill_registry.get("skills", [])
    skill_ids = [item.get("skill_id") for item in skills]
    if len(skill_ids) != len(set(skill_ids)):
        errors.append("Skill registry has duplicate Skill IDs")
    selector_keys: set[tuple[str, str | None]] = set()
    for skill in skills:
        source_ref = skill.get("source_ref", "")
        source_path = root / source_ref
        if not re.fullmatch(r"skills/[a-z0-9-]+/SKILL\.md", source_ref):
            errors.append(f"Skill registry has invalid source path: {source_ref}")
            continue
        if not source_path.is_file():
            errors.append(f"registered Skill source is missing: {source_ref}")
            continue
        frontmatter = source_path.read_text(encoding="utf-8").split("---", 2)
        expected_name = f"name: {skill.get('skill_id')}"
        if len(frontmatter) < 3 or expected_name not in frontmatter[1].splitlines():
            errors.append(f"registered Skill frontmatter name differs: {source_ref}")
        monitors = skill.get("monitor_ids") or [None]
        for kind in skill.get("work_item_kinds", []):
            for monitor_id in monitors:
                key = (kind, monitor_id)
                if key in selector_keys:
                    errors.append(
                        f"Skill selector is ambiguous: {kind}/{monitor_id or '*'}"
                    )
                selector_keys.add(key)
    return errors


def validate_source_acquisition_configuration(root: Path) -> list[str]:
    errors: list[str] = []
    registry = load_json(root / "config" / "source-registry.json")
    class_ids = [item.get("class_id") for item in registry.get("source_classes", [])]
    if len(class_ids) != len(set(class_ids)):
        errors.append("source registry has duplicate source classes")
    known_classes = set(class_ids)
    for path in sorted((root / "config" / "monitors").glob("*.json")):
        monitor = load_json(path)
        unknown = set(monitor.get("source_classes", [])) - known_classes
        if unknown:
            errors.append(
                f"monitor {monitor.get('monitor_id')} uses unknown source classes: {sorted(unknown)}"
            )
        for requirement in monitor.get("source_class_requirements", []):
            requirement_unknown = set(requirement.get("one_of", [])) - known_classes
            if requirement_unknown:
                errors.append(
                    f"monitor {monitor.get('monitor_id')} source requirement uses unknown "
                    f"classes: {sorted(requirement_unknown)}"
                )
            if int(requirement.get("minimum_count", 0)) < 1:
                errors.append(
                    f"monitor {monitor.get('monitor_id')} has a non-positive Source requirement"
                )
        persistent_ids = [
            item.get("persistent_query_id")
            for item in monitor.get("persistent_query_families", [])
        ]
        if len(persistent_ids) != len(set(persistent_ids)):
            errors.append(
                f"monitor {monitor.get('monitor_id')} has duplicate persistent query IDs"
            )
        for persistent in monitor.get("persistent_query_families", []):
            if not persistent.get("persistent_query_id") or not persistent.get("query"):
                errors.append(
                    f"monitor {monitor.get('monitor_id')} has an incomplete persistent query"
                )
            persistent_unknown = set(persistent.get("source_classes", [])) - known_classes
            if persistent_unknown or not persistent.get("source_classes"):
                errors.append(
                    f"monitor {monitor.get('monitor_id')} persistent query has invalid "
                    f"Source classes: {sorted(persistent_unknown)}"
                )
            promotion = persistent.get("promotion_evidence", {})
            effectiveness_ref = promotion.get("effectiveness_ref")
            if not effectiveness_ref or not (root / effectiveness_ref).is_file():
                errors.append(
                    f"monitor {monitor.get('monitor_id')} persistent query lacks "
                    "effectiveness evidence"
                )
                continue
            effectiveness = load_json(root / effectiveness_ref)
            matching = [
                query
                for query in effectiveness.get("queries", [])
                if query.get("query_id") == promotion.get("source_followup_query_id")
            ]
            source_plan_ref = effectiveness.get("followup_plan_snapshot_ref")
            source_plan = (
                load_json(root / source_plan_ref)
                if source_plan_ref and (root / source_plan_ref).is_file()
                else {}
            )
            source_queries = [
                query
                for query in source_plan.get("queries", [])
                if query.get("query_id") == promotion.get("source_followup_query_id")
            ]
            if (
                effectiveness.get("run_id") != promotion.get("effective_run_id")
                or len(matching) != 1
                or matching[0].get("effective") is not True
                or len(source_queries) != 1
                or persistent.get("query") != source_queries[0].get("query")
                or persistent.get("source_classes")
                != source_queries[0].get("source_classes")
            ):
                errors.append(
                    f"monitor {monitor.get('monitor_id')} persistent query promotion "
                    "is not backed by an effective query"
                )
        slots = int(monitor.get("discovery_slots_per_query", 1))
        minimum_per_query = int(monitor.get("minimum_sources_per_query", 1))
        if slots < minimum_per_query:
            errors.append(
                f"monitor {monitor.get('monitor_id')} cannot meet minimum sources per query"
            )
        minimum_evidence = int(
            monitor.get("minimum_evidence_sources_per_claim", 2)
        )
        if (
            monitor.get("query_families")
            and monitor.get("synthesis_product") != "center-profile"
            and slots < minimum_evidence
        ):
            errors.append(
                f"monitor {monitor.get('monitor_id')} cannot meet minimum Evidence "
                "sources per Claim"
            )
    policy = load_json(root / "config" / "acquisition-policy.json")
    required_rights_states = {
        "permitted",
        "prohibited",
        "restricted",
        "not-stated",
        "not-applicable",
    }
    missing_states = required_rights_states - set(policy.get("rights_rules", {}))
    if missing_states:
        errors.append(f"acquisition policy lacks rights states: {sorted(missing_states)}")
    if policy.get("maximum_candidate_passage_characters", 0) < 1:
        errors.append("acquisition policy must limit candidate passage length")
    scope = load_json(root / "config" / "global-technology-scope.json")
    taxonomy = scope.get("coverage_taxonomy", {})
    required = taxonomy.get("required_for_initial_cycle", {})
    for dimension in (
        "world_regions",
        "technology_categories",
        "organization_types",
        "maturity_signals",
        "result_signals",
    ):
        values = taxonomy.get(dimension, [])
        if not values or len(values) != len(set(values)):
            errors.append(f"global coverage taxonomy is empty or duplicated: {dimension}")
        unknown_required = set(required.get(dimension, [])) - set(values)
        if unknown_required:
            errors.append(
                f"global coverage requirements use unknown {dimension}: {sorted(unknown_required)}"
            )
    global_monitor = load_json(
        root / "config" / "monitors" / "MON-GLOBAL-TECH-001.json"
    )
    if global_monitor.get("scope_ref") != "config/global-technology-scope.json":
        errors.append("global technology Monitor does not pin the canonical scope")
    return errors


def validate_center_registry(root: Path) -> list[str]:
    errors: list[str] = []
    registry_ref = "config/hpci-center-registry.json"
    registry = load_json(root / registry_ref)
    center_ids = [center.get("center_id") for center in registry.get("centers", [])]
    if len(center_ids) != len(set(center_ids)):
        errors.append("HPCI center registry has duplicate center IDs")
    if len(center_ids) < 10:
        errors.append("HPCI center registry unexpectedly contains fewer than ten providers")
    default_fields = set(registry.get("default_profile_fields", []))
    if len(default_fields) != len(registry.get("default_profile_fields", [])):
        errors.append("HPCI center registry has duplicate default profile fields")
    for center in registry.get("centers", []):
        if not all(center.get(key) for key in ("center_id", "name_ja", "name_en", "official_url")):
            errors.append(f"HPCI center registry entry is incomplete: {center.get('center_id')}")
    monitor = load_json(root / "config" / "monitors" / "MON-HPCI-CENTERS-001.json")
    if monitor.get("subject_registry_ref") != registry_ref:
        errors.append("HPCI center Monitor does not reference the canonical registry")
    template_ids = [
        item.get("template_id") for item in monitor.get("subject_query_templates", [])
    ]
    if len(template_ids) != len(set(template_ids)):
        errors.append("HPCI center Monitor has duplicate subject query template IDs")
    covered_fields = {
        field
        for item in monitor.get("subject_query_templates", [])
        for field in item.get("profile_fields", [])
    }
    if covered_fields != default_fields or set(monitor.get("profile_fields", [])) != default_fields:
        errors.append("HPCI center Monitor query templates do not cover every profile field")
    if int(monitor.get("profile_max_age_days", 0)) < 1:
        errors.append("HPCI center Monitor must define a positive profile freshness limit")
    if monitor.get("synthesis_product") != "center-profile":
        errors.append("HPCI center Monitor must synthesize center profiles")
    return errors


def validate_runtime_artifacts(root: Path) -> list[str]:
    errors: list[str] = []
    for manifest_path in sorted((root / "runs").glob("RUN-*/manifest.json")):
        manifest = load_json(manifest_path)
        run_id = manifest.get("run_id")
        if manifest_path.parent.name != run_id:
            errors.append(f"Run manifest path does not match run_id: {manifest_path}")
            continue
        queue_dir = root / "queue" / run_id
        work_paths = sorted(queue_dir.glob("WORK-*.json"))
        work_items = [load_json(path) for path in work_paths]
        actual_ids = [item.get("work_item_id") for item in work_items]
        if actual_ids != manifest.get("work_item_ids", []):
            errors.append(f"Run {run_id} manifest Work Item IDs differ from queue files")
        idempotency_keys = [item.get("idempotency_key") for item in work_items]
        if len(idempotency_keys) != len(set(idempotency_keys)):
            errors.append(f"Run {run_id} has duplicate Work Item idempotency keys")
        for path, item in zip(work_paths, work_items, strict=True):
            if path.stem != item.get("work_item_id") or item.get("run_id") != run_id:
                errors.append(f"Work Item identity mismatch: {path.relative_to(root)}")
            skill = item.get("skill")
            if skill:
                pinned = manifest.get("skill_snapshots", {}).get(skill.get("source_ref"))
                if not pinned or any(
                    skill.get(key) != pinned.get(key)
                    for key in ("skill_id", "version", "snapshot_ref", "digest")
                ):
                    errors.append(
                        f"Work Item Skill differs from Run snapshot: {path.relative_to(root)}"
                    )
            if item.get("status") != "completed":
                continue
            for output_ref, expected_digest in item.get("output_digests", {}).items():
                output_path = root / output_ref
                if not output_path.is_file():
                    errors.append(f"completed Work Item output is missing: {output_ref}")
                    continue
                actual_digest = hashlib.sha256(output_path.read_bytes()).hexdigest()
                if actual_digest != expected_digest:
                    errors.append(f"completed Work Item output digest changed: {output_ref}")
        if manifest.get("cost") is not None and manifest.get("status") in {
            "completed",
            "partial",
            "failed",
            "cancelled",
            "stopped",
        }:
            expected_cost = usage_summary_from_items(work_items)
            if manifest.get("cost") != expected_cost:
                errors.append(f"Run {run_id} cost summary differs from Work Item usage")
        receipt_ids = [item.get("query_receipt_id") for item in manifest.get("query_receipts", [])]
        if len(receipt_ids) != len(set(receipt_ids)):
            errors.append(f"Run {run_id} has duplicate Query Receipt IDs")
        previous_run_id = manifest.get("previous_run_id")
        if previous_run_id:
            previous_path = root / "runs" / previous_run_id / "manifest.json"
            if not previous_path.is_file():
                errors.append(f"Run {run_id} predecessor is missing: {previous_run_id}")
            else:
                previous = load_json(previous_path)
                if previous.get("status") != "completed":
                    errors.append(f"Run {run_id} predecessor is not completed")
                if (
                    previous.get("task_id") != manifest.get("task_id")
                    or previous.get("monitor_id") != manifest.get("monitor_id")
                ):
                    errors.append(f"Run {run_id} predecessor scope differs")
                if previous.get("started_at", "") >= manifest.get("started_at", ""):
                    errors.append(f"Run {run_id} predecessor is not earlier")
        change_report_ref = manifest.get("change_report_ref")
        if change_report_ref:
            change_report_path = root / change_report_ref
            if not change_report_path.is_file():
                errors.append(f"Run {run_id} change report is missing: {change_report_ref}")
            else:
                change_report = load_json(change_report_path)
                if change_report.get("run_id") != run_id:
                    errors.append(f"Run {run_id} change report identity differs")
                if change_report.get("previous_run_id") != manifest.get(
                    "previous_run_id"
                ):
                    errors.append(f"Run {run_id} previous Run identity differs")
        dependency_impact_ref = manifest.get("dependency_impact_ref")
        if dependency_impact_ref:
            impact_path = root / dependency_impact_ref
            if not impact_path.is_file():
                errors.append(
                    f"Run {run_id} dependency impact report is missing: {dependency_impact_ref}"
                )
            else:
                impact = load_json(impact_path)
                if impact.get("run_id") != run_id:
                    errors.append(f"Run {run_id} dependency impact identity differs")
                if impact.get("previous_run_id") != manifest.get("previous_run_id"):
                    errors.append(f"Run {run_id} dependency impact predecessor differs")
                if impact.get("summary") != manifest.get("metrics", {}).get(
                    "dependency_impact"
                ):
                    errors.append(f"Run {run_id} dependency impact metrics differ")
        promotion_readiness_ref = manifest.get("promotion_readiness_ref")
        if promotion_readiness_ref:
            promotion_path = root / promotion_readiness_ref
            if not promotion_path.is_file():
                errors.append(
                    f"Run {run_id} promotion readiness report is missing: {promotion_readiness_ref}"
                )
            else:
                promotion = load_json(promotion_path)
                if promotion.get("run_id") != run_id:
                    errors.append(f"Run {run_id} promotion readiness identity differs")
                if promotion.get("summary") != manifest.get("metrics", {}).get(
                    "promotion_readiness"
                ):
                    errors.append(f"Run {run_id} promotion readiness metrics differ")
        readiness_ref = manifest.get("consensus_readiness_ref")
        if readiness_ref:
            readiness_path = root / readiness_ref
            if not readiness_path.is_file():
                errors.append(
                    f"Run {run_id} Consensus readiness report is missing: {readiness_ref}"
                )
            else:
                readiness = load_json(readiness_path)
                if readiness.get("run_id") != run_id:
                    errors.append(f"Run {run_id} Consensus readiness identity differs")
                if readiness.get("status") != manifest.get("metrics", {}).get(
                    "consensus_readiness"
                ):
                    errors.append(f"Run {run_id} Consensus readiness status differs")
        continuity_ref = manifest.get("profile_continuity_ref")
        if continuity_ref:
            continuity_path = root / continuity_ref
            if not continuity_path.is_file():
                errors.append(
                    f"Run {run_id} profile continuity report is missing: {continuity_ref}"
                )
            else:
                continuity = load_json(continuity_path)
                continuity_metric = manifest.get("metrics", {}).get(
                    "profile_continuity", {}
                )
                if continuity.get("run_id") != run_id:
                    errors.append(f"Run {run_id} profile continuity identity differs")
                if continuity.get("status") != continuity_metric.get("status"):
                    errors.append(f"Run {run_id} profile continuity status differs")
                if continuity.get("regression_count") != continuity_metric.get(
                    "regression_count"
                ):
                    errors.append(
                        f"Run {run_id} profile continuity regression count differs"
                    )
        effectiveness_ref = manifest.get("followup_effectiveness_ref")
        if effectiveness_ref:
            effectiveness_path = root / effectiveness_ref
            if not effectiveness_path.is_file():
                errors.append(
                    f"Run {run_id} follow-up effectiveness report is missing: {effectiveness_ref}"
                )
            else:
                effectiveness = load_json(effectiveness_path)
                effectiveness_metric = manifest.get("metrics", {}).get(
                    "followup_effectiveness", {}
                )
                if effectiveness.get("run_id") != run_id:
                    errors.append(f"Run {run_id} follow-up effectiveness identity differs")
                if effectiveness.get("status") != effectiveness_metric.get("status"):
                    errors.append(f"Run {run_id} follow-up effectiveness status differs")
                if effectiveness.get("effective_query_count") != effectiveness_metric.get(
                    "effective_query_count"
                ):
                    errors.append(
                        f"Run {run_id} follow-up effectiveness count differs"
                    )
        temporal_ref = manifest.get("temporal_integrity_ref")
        if temporal_ref:
            temporal_path = root / temporal_ref
            if not temporal_path.is_file():
                errors.append(f"Run {run_id} temporal integrity report is missing: {temporal_ref}")
            else:
                temporal = load_json(temporal_path)
                temporal_metric = manifest.get("metrics", {}).get("temporal_integrity", {})
                if temporal.get("run_id") != run_id:
                    errors.append(f"Run {run_id} temporal integrity identity differs")
                if temporal.get("status") != temporal_metric.get("status"):
                    errors.append(f"Run {run_id} temporal integrity status differs")
                if temporal.get("anomaly_count") != temporal_metric.get("anomaly_count"):
                    errors.append(f"Run {run_id} temporal integrity anomaly count differs")
        snapshots = manifest.get("configuration_snapshots", {})
        for source_ref, expected_digest in manifest.get("policy_hashes", {}).items():
            snapshot_ref = snapshots.get(source_ref)
            if not snapshot_ref:
                continue
            snapshot_path = root / snapshot_ref
            if not snapshot_path.is_file():
                errors.append(f"Run {run_id} configuration snapshot is missing: {snapshot_ref}")
            else:
                snapshot_digest = hashlib.sha256(
                    json.dumps(
                        load_json(snapshot_path),
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest()
                if snapshot_digest != expected_digest:
                    errors.append(
                        f"Run {run_id} configuration snapshot digest differs: {snapshot_ref}"
                    )
        for source_ref, skill in manifest.get("skill_snapshots", {}).items():
            snapshot_ref = skill.get("snapshot_ref")
            snapshot_path = root / str(snapshot_ref)
            if not snapshot_path.is_file():
                errors.append(f"Run {run_id} Skill snapshot is missing: {snapshot_ref}")
                continue
            actual_digest = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
            if actual_digest != skill.get("digest"):
                errors.append(f"Run {run_id} Skill snapshot digest differs: {source_ref}")
        directive_snapshots = manifest.get("directive_snapshots", {})
        for source_ref, expected_digest in manifest.get("directive_hashes", {}).items():
            snapshot_ref = directive_snapshots.get(source_ref)
            if not snapshot_ref or not (root / snapshot_ref).is_file():
                errors.append(f"Run {run_id} Directive snapshot is missing: {source_ref}")
                continue
            actual_digest = hashlib.sha256(
                json.dumps(
                    load_json(root / snapshot_ref),
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()
            if actual_digest != expected_digest:
                errors.append(
                    f"Run {run_id} Directive snapshot digest differs: {snapshot_ref}"
                )
            directive_id = Path(source_ref).stem
            receipt_ref = f"runs/{run_id}/directives/{directive_id}.json"
            receipt_path = root / receipt_ref
            if not receipt_path.is_file():
                continue
            receipt = load_json(receipt_path)
            snapshot = load_json(root / snapshot_ref)
            if (
                receipt.get("directive_id") != directive_id
                or receipt.get("run_id") != run_id
                or receipt.get("status") != "applied"
                or receipt.get("directive_digest") != stable_digest(snapshot)
                or receipt.get("instruction_digest")
                != stable_digest(snapshot.get("instruction"))
            ):
                errors.append(f"Run {run_id} Directive application receipt differs: {receipt_ref}")
            work_ref = (
                root
                / "queue"
                / run_id
                / f"{receipt.get('work_item_id', '')}.json"
            )
            if not work_ref.is_file():
                errors.append(f"Run {run_id} Directive Work Item is missing: {receipt_ref}")
            else:
                work_item = load_json(work_ref)
                if (
                    work_item.get("kind") != "apply-directive"
                    or work_item.get("payload", {}).get("directive_id") != directive_id
                    or receipt_ref not in work_item.get("output_refs", [])
                ):
                    errors.append(
                        f"Run {run_id} Directive receipt is not bound to its Work Item: {receipt_ref}"
                    )

    source_ids_by_run: dict[str, list[str]] = {}
    content_hash_origins: dict[tuple[str, str], dict[str, list[str]]] = {}
    for path in sorted((root / "proposals" / "sources").glob("RUN-*/*.json")):
        result = load_json(path)
        if result.get("run_id") != path.parent.name:
            errors.append(f"Source result Run mismatch: {path.relative_to(root)}")
        if result.get("work_item_id") != path.stem:
            errors.append(f"Source result Work Item mismatch: {path.relative_to(root)}")
        if result.get("object_type") == "source":
            source_ids_by_run.setdefault(path.parent.name, []).append(
                result.get("source_receipt", {}).get("source_id")
            )
        work_path = root / "queue" / path.parent.name / f"{path.stem}.json"
        if not work_path.is_file():
            errors.append(f"Source result Work Item is missing: {path.relative_to(root)}")
            continue
        work_item = load_json(work_path)
        run_manifest_path = root / "runs" / path.parent.name / "manifest.json"
        run_manifest = load_json(run_manifest_path) if run_manifest_path.is_file() else {}
        strict_assignment = run_manifest.get("assignment_contract_version") == "0.2.0"
        payload = work_item.get("payload", {})
        query_receipt = result.get("query_receipt", {})
        source_receipt = result.get("source_receipt", {})
        source_lineage = result.get("source_lineage", {})
        if source_receipt.get("schema_version") == "0.2.0":
            expected_authority = publisher_authority(
                source_receipt.get("canonical_url", "")
            )
            expected_publisher_group = (
                f"PUB-{stable_digest(expected_authority)[:12].upper()}"
            )
            if source_receipt.get("publisher_authority") != expected_authority:
                errors.append(
                    f"Source Publisher authority is not canonical: {path.relative_to(root)}"
                )
            if source_receipt.get("publisher_group_id") != expected_publisher_group:
                errors.append(
                    f"Source Publisher Group is not authority-derived: {path.relative_to(root)}"
                )
        if source_lineage.get("schema_version") == "0.2.0":
            origin_url = source_lineage.get("canonical_origin_url", "")
            policy_path = (
                root
                / "runs"
                / path.parent.name
                / "inputs"
                / "config"
                / "acquisition-policy.json"
            )
            try:
                policy = load_json(policy_path if policy_path.is_file() else root / "config" / "acquisition-policy.json")
                canonical_origin_url = canonicalize_url(origin_url, policy)
            except (KeyError, TypeError, ValueError):
                canonical_origin_url = None
                errors.append(
                    f"Source canonical Origin URL is invalid: {path.relative_to(root)}"
                )
            if canonical_origin_url is not None:
                expected_origin_group = (
                    f"ORG-{stable_digest(canonical_origin_url)[:12].upper()}"
                )
                if canonical_origin_url != origin_url:
                    errors.append(
                        f"Source canonical Origin URL is not canonical: {path.relative_to(root)}"
                    )
                if source_lineage.get("origin_group_id") != expected_origin_group:
                    errors.append(
                        f"Source Origin Group is not origin-derived: {path.relative_to(root)}"
                    )
            if source_receipt.get("origin_group_id") != source_lineage.get("origin_group_id"):
                errors.append(
                    f"Source Receipt and Lineage Origin Groups differ: {path.relative_to(root)}"
                )
            relationship = source_lineage.get("relationship")
            if relationship == "original":
                if origin_url != source_receipt.get("canonical_url"):
                    errors.append(
                        f"Original Source Origin URL differs from canonical URL: {path.relative_to(root)}"
                    )
                if source_lineage.get("canonical_origin_source_id") != source_receipt.get("source_id"):
                    errors.append(
                        f"Original Source does not identify itself as canonical origin: {path.relative_to(root)}"
                    )
            else:
                if origin_url == source_receipt.get("canonical_url"):
                    errors.append(
                        f"Derivative Source uses itself as canonical origin: {path.relative_to(root)}"
                    )
                if source_receipt.get("primary_source"):
                    errors.append(
                        f"Derivative Source is marked primary: {path.relative_to(root)}"
                    )
            if (
                source_receipt.get("source_class") == "derivative-reporting"
                and relationship == "original"
            ):
                errors.append(
                    f"Derivative reporting is marked original: {path.relative_to(root)}"
                )
        content_hash = source_receipt.get("retrieved_content_sha256")
        origin_group = source_receipt.get("origin_group_id")
        if content_hash and origin_group:
            content_hash_origins.setdefault(
                (path.parent.name, content_hash), {}
            ).setdefault(origin_group, []).append(str(path.relative_to(root)))
        if strict_assignment and work_item.get("kind") != "source-discovery":
            errors.append(f"Source result belongs to a non-discovery Work Item: {path.relative_to(root)}")
        if strict_assignment and query_receipt.get("query") != payload.get("query"):
            errors.append(f"Source result query differs from its assignment: {path.relative_to(root)}")
        expected_scope = (
            {
                key: payload[key]
                for key in ("subject_ids", "profile_fields", "query_template_id")
                if key in payload
            }
            if payload.get("subject_ids")
            else {}
        )
        if result.get("object_type") == "discovery_no_result":
            if strict_assignment and not language_in_scope(
                query_receipt.get("language"), payload.get("languages", [])
            ):
                errors.append(
                    f"No-result language differs from its assignment: {path.relative_to(root)}"
                )
            if strict_assignment and result.get("assignment_scope", {}) != expected_scope:
                errors.append(
                    f"No-result subject scope differs from its assignment: {path.relative_to(root)}"
                )
            continue
        if strict_assignment and source_receipt.get("source_class") not in payload.get("source_classes", []):
            errors.append(f"Source result class differs from its assignment: {path.relative_to(root)}")
        if strict_assignment and not language_in_scope(
            source_receipt.get("language"), payload.get("languages", [])
        ):
            errors.append(f"Source result language differs from its assignment: {path.relative_to(root)}")
        if strict_assignment and source_receipt.get("assignment_scope", {}) != expected_scope:
            errors.append(f"Source result subject scope differs from its assignment: {path.relative_to(root)}")
    for (run_id, content_hash), origins in sorted(content_hash_origins.items()):
        if len(origins) > 1:
            refs = sorted(ref for paths in origins.values() for ref in paths)
            errors.append(
                "Identical Source content is assigned to multiple Origin Groups "
                f"in {run_id} ({content_hash[:12]}): {', '.join(refs)}"
            )
    for path in sorted((root / "proposals" / "evidence").glob("RUN-*/*.json")):
        bundle = load_json(path)
        if bundle.get("run_id") != path.parent.name:
            errors.append(f"Evidence bundle Run mismatch: {path.relative_to(root)}")
        source_ref = bundle.get("source_result_ref")
        if not source_ref or not (root / source_ref).is_file():
            errors.append(f"Evidence bundle source result is missing: {path.relative_to(root)}")
        elif bundle.get("schema_version") == "0.2.0":
            source_result = load_json(root / source_ref)
            expected_publishers = [
                source_result.get("source_receipt", {}).get("publisher_group_id")
            ]
            if bundle.get("publisher_group_ids") != expected_publishers:
                errors.append(
                    f"Evidence bundle Publisher Group differs from Source: {path.relative_to(root)}"
                )
    for path in sorted((root / "proposals" / "claims").glob("RUN-*/*.json")):
        proposal = load_json(path)
        if proposal.get("run_id") != path.parent.name:
            errors.append(f"Claim proposal Run mismatch: {path.relative_to(root)}")
        bundles = []
        for evidence_ref in proposal.get("evidence_bundle_refs", []):
            if not (root / evidence_ref).is_file():
                errors.append(f"Claim proposal Evidence is missing: {path.relative_to(root)}")
            else:
                bundles.append(load_json(root / evidence_ref))
        if bundles:
            expected_evidence_ids = {
                evidence["evidence_id"]
                for bundle in bundles
                for evidence in bundle.get("evidence_candidates", [])
            }
            expected_lineage_ids = {
                evidence["source_lineage_id"]
                for bundle in bundles
                for evidence in bundle.get("evidence_candidates", [])
            }
            expected_origins = {
                origin
                for bundle in bundles
                for origin in bundle.get("origin_group_ids", [])
            }
            expected_publishers = {
                publisher
                for bundle in bundles
                for publisher in bundle.get("publisher_group_ids", [])
            }
            candidate = proposal.get("claim_candidate", {})
            if set(candidate.get("evidence_ids", [])) != expected_evidence_ids:
                errors.append(f"Claim proposal Evidence IDs differ from bundles: {path.relative_to(root)}")
            if set(candidate.get("source_lineage_ids", [])) != expected_lineage_ids:
                errors.append(f"Claim proposal Lineage IDs differ from bundles: {path.relative_to(root)}")
            if set(proposal.get("origin_group_ids", [])) != expected_origins:
                errors.append(f"Claim proposal Origin Groups differ from bundles: {path.relative_to(root)}")
            if set(proposal.get("publisher_group_ids", [])) != expected_publishers:
                errors.append(
                    f"Claim proposal Publisher Groups differ from bundles: {path.relative_to(root)}"
                )
    for path in sorted((root / "proposals" / "center-profiles").glob("RUN-*/*.json")):
        profile = load_json(path)
        if profile.get("run_id") != path.parent.name:
            errors.append(f"Center Profile Run mismatch: {path.relative_to(root)}")
        bundle_refs = profile.get("evidence_bundle_refs")
        if bundle_refs:
            bundles: list[dict[str, Any]] = []
            for bundle_ref in bundle_refs:
                bundle_path = root / bundle_ref
                if not bundle_path.is_file():
                    errors.append(
                        f"Center Profile Evidence bundle is missing: {path.relative_to(root)}"
                    )
                else:
                    bundles.append(load_json(bundle_path))
            evidence_ids = set(profile.get("evidence_refs", []))
            bundle_evidence_ids = {
                evidence["evidence_id"]
                for bundle in bundles
                for evidence in bundle.get("evidence_candidates", [])
            }
            if not evidence_ids <= bundle_evidence_ids:
                errors.append(
                    f"Center Profile Evidence IDs are not covered by bundles: {path.relative_to(root)}"
                )
            evidence_run_ids = {
                bundle.get("run_id")
                for bundle in bundles
                if any(
                    evidence.get("evidence_id") in evidence_ids
                    for evidence in bundle.get("evidence_candidates", [])
                )
            }
            if set(profile.get("evidence_run_ids", [])) != evidence_run_ids:
                errors.append(
                    f"Center Profile Evidence Run IDs differ from bundles: {path.relative_to(root)}"
                )
        predecessor = profile.get("predecessor")
        if predecessor:
            predecessor_path = root / predecessor.get("profile_ref", "")
            if not predecessor_path.is_file():
                errors.append(
                    f"Center Profile predecessor is missing: {path.relative_to(root)}"
                )
                continue
            predecessor_profile = load_json(predecessor_path)
            predecessor_digest = hashlib.sha256(
                json.dumps(
                    predecessor_profile,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()
            if predecessor.get("profile_digest") != predecessor_digest:
                errors.append(
                    f"Center Profile predecessor digest differs: {path.relative_to(root)}"
                )
            if predecessor_profile.get("run_id") != predecessor.get("run_id"):
                errors.append(
                    f"Center Profile predecessor Run differs: {path.relative_to(root)}"
                )
            if predecessor_profile.get("center_id") != profile.get("center_id"):
                errors.append(
                    f"Center Profile predecessor center differs: {path.relative_to(root)}"
                )
            for field in predecessor.get("inherited_fields", []):
                if profile.get(field) != predecessor_profile.get(field):
                    errors.append(
                        f"Center Profile inherited field differs from predecessor: "
                        f"{path.relative_to(root)}#{field}"
                    )
    assessments_by_run_and_id: dict[tuple[str, str], dict[str, Any]] = {}
    for path in sorted((root / "assessments").glob("RUN-*/**/*.json")):
        assessment = load_json(path)
        run_id = path.relative_to(root / "assessments").parts[0]
        if assessment.get("run_id") != run_id:
            errors.append(f"Assessment Run mismatch: {path.relative_to(root)}")
        manifest_path = root / "runs" / assessment.get("run_id", "") / "manifest.json"
        registry_path = root / "config" / "agent-registry.json"
        if manifest_path.is_file():
            manifest = load_json(manifest_path)
            snapshot_ref = manifest.get("configuration_snapshots", {}).get(
                "config/agent-registry.json"
            )
            if snapshot_ref:
                registry_path = root / snapshot_ref
        if registry_path.is_file():
            registry = load_json(registry_path)
            registry_digest = hashlib.sha256(
                json.dumps(
                    registry,
                    ensure_ascii=False,
                    sort_keys=True,
                    separators=(",", ":"),
                ).encode("utf-8")
            ).hexdigest()
            if assessment.get("agent_registry_digest") != registry_digest:
                errors.append(
                    f"Assessment registry digest differs from Run snapshot: {path.relative_to(root)}"
                )
        assessments_by_run_and_id[(run_id, assessment.get("assessment_id"))] = assessment
    proposals_by_run_and_id: dict[tuple[str, str], dict[str, Any]] = {}
    for path in sorted((root / "proposals").glob("**/*.json")):
        proposal = load_json(path)
        run_id = proposal.get("run_id")
        proposal_id = proposal.get("proposal_id")
        if not run_id or not proposal_id:
            continue
        key = (run_id, proposal_id)
        if key in proposals_by_run_and_id:
            errors.append(
                f"Duplicate Proposal ID in Run: {run_id}/{proposal_id}"
            )
        proposals_by_run_and_id[key] = proposal
    for path in sorted((root / "decisions").glob("RUN-*/*.json")):
        decision = load_json(path)
        run_id = path.parent.name
        proposal = proposals_by_run_and_id.get((run_id, decision.get("proposal_id")))
        if proposal is None:
            errors.append(f"Decision Proposal is missing: {path.relative_to(root)}")
        elif proposal.get("object_type") != decision.get("object_type"):
            errors.append(
                f"Decision Proposal object type differs: {path.relative_to(root)}"
            )
        for assessment_id in decision.get("assessment_ids", []):
            assessment = assessments_by_run_and_id.get((run_id, assessment_id))
            if assessment is None:
                errors.append(f"Decision Assessment is missing: {path.relative_to(root)}")
            elif assessment.get("proposal_id") != decision.get("proposal_id"):
                errors.append(f"Decision Assessment targets another proposal: {path.relative_to(root)}")
        manifest_path = root / "runs" / run_id / "manifest.json"
        if manifest_path.is_file():
            manifest = load_json(manifest_path)
            registry_ref = manifest.get("configuration_snapshots", {}).get(
                "config/agent-registry.json"
            )
            if registry_ref:
                registry = load_json(root / registry_ref)
                registry_digest = hashlib.sha256(
                    json.dumps(
                        registry,
                        ensure_ascii=False,
                        sort_keys=True,
                        separators=(",", ":"),
                    ).encode("utf-8")
                ).hexdigest()
                if decision.get("agent_registry_digest") != registry_digest:
                    errors.append(
                        f"Decision registry digest differs from Run snapshot: {path.relative_to(root)}"
                    )
    return errors


def validate_research_baseline(root: Path) -> list[str]:
    baseline = load_json(root / "config" / "research-baseline.json")
    errors: list[str] = validate_catalog_scope(root)
    source_corpus = baseline.get("source_corpus", [])
    source_ids = [source.get("source_id") for source in source_corpus]
    if len(source_ids) != len(set(source_ids)):
        errors.append("research baseline has duplicate source IDs")
    declared_sources = set(baseline.get("source_refs", []))
    if declared_sources != set(source_ids):
        errors.append("research baseline source_refs do not match source_corpus IDs")
    for source in source_corpus:
        if not re.fullmatch(r"[0-9a-f]{64}", source.get("sha256", "")):
            errors.append(f"research baseline source has invalid sha256: {source.get('source_id')}")

    topics = baseline.get("topics", [])
    topic_ids = [topic.get("topic_id") for topic in topics]
    if len(topic_ids) != len(set(topic_ids)):
        errors.append("research baseline has duplicate topic IDs")
    required_domains = {"architecture", "system-software", "applications", "cross-cutting"}
    actual_domains = {topic.get("domain") for topic in topics}
    if not required_domains.issubset(actual_domains):
        errors.append(f"research baseline missing domains: {sorted(required_domains - actual_domains)}")
    for topic in topics:
        for field in ("research_questions", "evidence_expected", "outputs", "source_refs"):
            if not topic.get(field):
                errors.append(f"research baseline topic {topic.get('topic_id')} has no {field}")
        unknown_sources = set(topic.get("source_refs", [])) - declared_sources
        if unknown_sources:
            errors.append(
                f"research baseline topic {topic.get('topic_id')} references unknown sources: "
                f"{sorted(unknown_sources)}"
            )
        retirement = topic.get("retirement")
        if topic.get("status") == "retired" and not retirement:
            errors.append(f"retired research baseline topic lacks lineage: {topic.get('topic_id')}")
        if topic.get("status") != "retired" and retirement:
            errors.append(f"active research baseline topic declares retirement: {topic.get('topic_id')}")
        if retirement:
            successor_ids = set(retirement.get("successor_topic_ids", []))
            if topic.get("topic_id") in successor_ids:
                errors.append(f"retired topic points to itself: {topic.get('topic_id')}")

    initial_topic_ids = [
        "ARCH-01", "ARCH-02", "ARCH-03", "ARCH-04", "ARCH-05", "ARCH-06", "ARCH-07",
        "SSW-01", "SSW-02", "SSW-03", "SSW-04", "SSW-05", "SSW-06", "SSW-07", "SSW-08", "SSW-09",
        "APP-01", "APP-02", "APP-03", "APP-04", "APP-05", "APP-06", "APP-07",
        "CROSS-01", "CROSS-02", "CROSS-03", "CROSS-04", "CROSS-05", "CROSS-06", "CROSS-07",
    ]
    protected = baseline.get("initial_catalog", {})
    if protected.get("topic_ids") != initial_topic_ids:
        errors.append("research baseline protected initial catalog changed")
    missing_initial_topics = set(initial_topic_ids) - set(topic_ids)
    if missing_initial_topics:
        errors.append(f"research baseline removed initial topics: {sorted(missing_initial_topics)}")
    required_additive_topics = {"CROSS-17", "CROSS-18"}
    missing_additive_topics = required_additive_topics - set(topic_ids)
    if missing_additive_topics:
        errors.append(f"research baseline missing continuing-discovery topics: {sorted(missing_additive_topics)}")
    known_topic_ids = set(topic_ids)
    for topic in topics:
        retirement = topic.get("retirement", {})
        unknown_successors = set(retirement.get("successor_topic_ids", [])) - known_topic_ids
        if unknown_successors:
            errors.append(
                f"retired topic {topic.get('topic_id')} has unknown successors: {sorted(unknown_successors)}"
            )

    official_sources = [
        source for source in source_corpus
        if source.get("source_id", "") >= "FSBASE-SRC-006"
    ]
    if len(official_sources) != 26:
        errors.append(f"research baseline must register 26 official FS2/FS3 PDFs, found {len(official_sources)}")
    for source in official_sources:
        for field in ("public_url", "source_page_url", "fiscal_year", "team", "part", "page_count"):
            if not source.get(field):
                errors.append(f"official source {source.get('source_id')} has no {field}")
    if baseline.get("complete") is not False:
        errors.append("research baseline must declare complete=false while source gaps remain")
    required_gaps = {"FSBASE-GAP-001"}
    missing_gaps = required_gaps - set(baseline.get("open_gap_ids", []))
    if missing_gaps:
        errors.append(f"research baseline missing historical FS gaps: {sorted(missing_gaps)}")
    incorrectly_open = {"FSBASE-GAP-002", "FSBASE-GAP-004"} & set(baseline.get("open_gap_ids", []))
    if incorrectly_open:
        errors.append(f"research baseline still marks reviewed official gaps open: {sorted(incorrectly_open)}")
    return errors


def validate_global_technology_scope(root: Path) -> list[str]:
    errors: list[str] = []
    scope = load_json(root / "config" / "global-technology-scope.json")
    if len(scope.get("technology_categories", [])) < 10:
        errors.append("global technology scope must cover at least ten broad categories")
    if not scope.get("coverage_requirements", {}).get("search_beyond_seed_list"):
        errors.append("global technology scope must search beyond known candidates")
    coverage = scope.get("coverage_requirements", {})
    if not coverage.get("worldwide_region_coverage"):
        errors.append("global technology scope must require worldwide region coverage")
    if scope.get("priority_regions") != ["Japan"]:
        errors.append("global technology scope must prioritize coverage of Japan")
    monitor = load_json(root / "config" / "monitors" / "MON-GLOBAL-TECH-001.json")
    if monitor.get("scope_ref") != "config/global-technology-scope.json":
        errors.append("MON-GLOBAL-TECH-001 does not reference the canonical global scope")
    selector = monitor.get("topic_selector", {})
    if selector.get("catalog_ref") != "config/research-baseline.json" or not selector.get("include_all_active_topics"):
        errors.append("MON-GLOBAL-TECH-001 must dynamically include all active research topics")
    return errors


def validate_catalog_taxonomy(root: Path) -> list[str]:
    errors: list[str] = []
    taxonomy = load_json(root / "config" / "catalog-taxonomy.json")
    baseline = load_json(root / "config" / "research-baseline.json")
    portfolio = load_json(root / "config" / "roadmap-portfolio.json")
    expected_categories = [
        "architecture-hardware",
        "system-software",
        "applications",
        "operations-procurement",
        "access-governance",
        "cross-cutting",
    ]
    categories = taxonomy.get("categories", [])
    if [item.get("category_id") for item in categories] != expected_categories:
        errors.append("catalog taxonomy category IDs or order changed")
    if [item.get("order") for item in categories] != list(range(1, 7)):
        errors.append("catalog taxonomy orders must be 1 through 6")

    expected_prefixes = ["ARCH", "SSW", "APP", "OPS", "GOV", "CROSS"]
    if [item.get("display_prefix") for item in categories] != expected_prefixes:
        errors.append("catalog taxonomy display prefixes or order changed")

    active_topic_ids = {
        topic["topic_id"] for topic in baseline.get("topics", [])
        if topic.get("status") != "retired"
    }
    assigned_topics = [
        topic_id for category in categories for topic_id in category.get("topic_ids", [])
    ]
    if len(assigned_topics) != len(set(assigned_topics)):
        errors.append("catalog taxonomy assigns a topic to more than one category")
    missing_topics = active_topic_ids - set(assigned_topics)
    unknown_topics = set(assigned_topics) - active_topic_ids
    if missing_topics:
        errors.append(f"catalog taxonomy omits active topics: {sorted(missing_topics)}")
    if unknown_topics:
        errors.append(f"catalog taxonomy references unknown or retired topics: {sorted(unknown_topics)}")
    assigned_codes: list[str] = []
    for category in categories:
        topic_codes = category.get("topic_codes", {})
        if set(topic_codes) != set(category.get("topic_ids", [])):
            errors.append(
                f"catalog taxonomy code coverage differs for {category.get('category_id')}"
            )
        prefix = category.get("display_prefix", "") + "-"
        if taxonomy.get("schema_version") == "0.3.0":
            reserved = category.get("reserved_topic_codes", [])
            if set(topic_codes.values()) - set(reserved) or len(reserved) != len(set(reserved)):
                errors.append(f"catalog reserved codes are incomplete or duplicated for {category.get('category_id')}")
            if any(not code.startswith(prefix) for code in reserved):
                errors.append(f"catalog reserved code has wrong prefix for {category.get('category_id')}")
        for topic_id, catalog_code in topic_codes.items():
            if not catalog_code.startswith(prefix):
                errors.append(
                    f"catalog code {catalog_code} does not match category prefix for {topic_id}"
                )
            assigned_codes.append(catalog_code)
    if len(assigned_codes) != len(set(assigned_codes)):
        errors.append("catalog taxonomy assigns a display code more than once")

    roadmap_ids = {
        item["roadmap_id"] for item in portfolio.get("roadmap_families", [])
    }
    assigned_roadmaps = [
        roadmap_id
        for category in categories
        for roadmap_id in category.get("roadmap_ids", [])
    ]
    if len(assigned_roadmaps) != len(set(assigned_roadmaps)):
        errors.append("catalog taxonomy assigns a roadmap to more than one category")
    missing_roadmaps = roadmap_ids - set(assigned_roadmaps)
    unknown_roadmaps = set(assigned_roadmaps) - roadmap_ids
    if missing_roadmaps:
        errors.append(f"catalog taxonomy omits roadmaps: {sorted(missing_roadmaps)}")
    if unknown_roadmaps:
        errors.append(f"catalog taxonomy references unknown roadmaps: {sorted(unknown_roadmaps)}")
    return errors


def validate_research_topic_configuration(root: Path) -> list[str]:
    errors: list[str] = []
    policy = load_json(root / "config" / "consensus-policy.json")
    rule = policy.get("rules", {}).get("research_topic", {})
    if rule.get("minimum_support_independence_groups", 0) < 2:
        errors.append("research_topic consensus requires at least two support independence groups")
    if rule.get("minimum_origin_groups", 0) < 2:
        errors.append("research_topic consensus requires at least two source origin groups")
    if rule.get("require_falsification_review") is not True:
        errors.append("research_topic consensus requires falsification review")
    permissions = load_json(root / "config" / "role-permissions.json")
    allowed = set(permissions.get("roles", {}).get("topic-promotion", {}).get("allowed_write_patterns", []))
    expected = {
        "config/research-baseline.json",
        "config/catalog-taxonomy.json",
        "config/publication-i18n.json",
        "config/monitors/MON-AUTO-TOPICS-001.json",
        "runs/**",
    }
    if allowed != expected:
        errors.append("topic-promotion role has unexpected write permissions")
    monitor = load_json(root / "config" / "monitors" / "MON-AUTO-TOPICS-001.json")
    baseline_topics = {
        topic["topic_id"] for topic in load_json(root / "config" / "research-baseline.json")["topics"]
    }
    for entry in monitor.get("topic_entries", []):
        if entry.get("topic_id") not in baseline_topics:
            errors.append(f"auto-topic monitor references unknown topic: {entry.get('topic_id')}")
        if not entry.get("decision_id"):
            errors.append(f"auto-topic monitor entry lacks decision: {entry.get('topic_id')}")
    return errors


def validate_source_watch_registry(root: Path) -> list[str]:
    errors: list[str] = []
    registry = load_json(root / "config" / "source-watch-registry.json")
    baseline = load_json(root / "config" / "research-baseline.json")
    portfolio = load_json(root / "config" / "roadmap-portfolio.json")
    active_topics = {
        topic["topic_id"]
        for topic in baseline["topics"]
        if topic["status"] != "retired"
    }
    roadmap_ids = {item["roadmap_id"] for item in portfolio["roadmap_families"]}
    monitor_ids = {
        load_json(path)["monitor_id"]
        for path in (root / "config" / "monitors").glob("*.json")
    }
    targets = registry.get("targets", [])
    watch_ids = [item.get("watch_id") for item in targets]
    urls = [item.get("canonical_url") for item in targets if item.get("active")]
    if len(watch_ids) != len(set(watch_ids)):
        errors.append("source watch registry has duplicate Watch IDs")
    if len(urls) != len(set(urls)):
        errors.append("source watch registry has duplicate active URLs")
    for target in targets:
        watch_id = target.get("watch_id")
        unknown_topics = set(target.get("topic_ids", [])) - active_topics
        unknown_roadmaps = set(target.get("roadmap_ids", [])) - roadmap_ids
        unknown_monitors = set(target.get("monitor_ids", [])) - monitor_ids
        if unknown_topics:
            errors.append(f"{watch_id} references unknown or retired Topics: {sorted(unknown_topics)}")
        if unknown_roadmaps:
            errors.append(f"{watch_id} references unknown Roadmaps: {sorted(unknown_roadmaps)}")
        if unknown_monitors:
            errors.append(f"{watch_id} references unknown Monitors: {sorted(unknown_monitors)}")
        change_policy = target.get("change_policy", {})
        if not all(change_policy.values()):
            errors.append(f"{watch_id} weakens semantic-change or Consensus requirements")
    map_path = root / "knowledge" / "public" / "source-catalog-map.json"
    if map_path.is_file() and load_json(map_path) != build_source_catalog_map(root):
        errors.append("generated source catalog map is stale or non-deterministic")
    return errors


def validate_publication_configuration(root: Path) -> list[str]:
    errors: list[str] = []
    policy = load_json(root / "config" / "publication-policy.json")
    if policy.get("information_plane") != "public-only":
        errors.append("publication policy must be public-only")
    if policy.get("accepted_scenario_statuses") != ["published"]:
        errors.append("publication policy must allow published scenarios only")
    if policy.get("accepted_report_statuses") != ["published"]:
        errors.append("publication policy must allow published reports only")
    required_metadata = policy.get("required_publication_metadata", {})
    if required_metadata != {
        "information_classification": "public",
        "publication_approved": True,
    }:
        errors.append("publication policy lacks strict public-classification metadata")
    for key in ("scenario_public_fields", "report_public_fields"):
        if not policy.get(key) or "publication" not in policy[key]:
            errors.append(f"publication policy lacks an explicit {key} allowlist")
    for key in (
        "consensus_receipt_public_fields",
        "consensus_participant_public_fields",
        "consensus_harness_public_fields",
    ):
        if not policy.get(key):
            errors.append(f"publication policy lacks an explicit {key} allowlist")
    if policy.get("license_status") != "active" or policy.get("license") != "Apache-2.0":
        errors.append("publication policy must expose the active Apache-2.0 license")
    if not policy.get("human_publication_directive_glob"):
        errors.append("publication policy lacks human publication Directives")
    i18n = load_json(root / policy.get("included_i18n", "config/publication-i18n.json"))
    if i18n.get("supported_languages") != ["ja", "en"]:
        errors.append("publication i18n must support Japanese and English")
    baseline = load_json(root / policy["included_catalog"])
    topic_ids = {topic["topic_id"] for topic in baseline["topics"]}
    translated_ids = set(i18n.get("topic_titles_en", {}))
    if translated_ids != topic_ids:
        errors.append(
            f"publication i18n Topic coverage differs: missing={sorted(topic_ids - translated_ids)}, "
            f"unknown={sorted(translated_ids - topic_ids)}"
        )
    technology_scope = load_json(root / "config" / "global-technology-scope.json")
    technology_i18n = i18n.get("technology_landscape", {})
    category_ja = technology_i18n.get("technology_categories_ja", [])
    if len(category_ja) != len(technology_scope.get("technology_categories", [])):
        errors.append("publication i18n technology landscape category counts differ")
    for key in ("scope_rule_ja", "priority_rule_ja"):
        if not technology_i18n.get(key):
            errors.append(f"publication i18n technology landscape lacks {key}")
    workflow = (root / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
    if "OPENFS_PAGES_ENABLED" not in workflow:
        errors.append("Pages workflow lacks explicit activation variable")
    return errors


def validate_scenario_configuration(root: Path) -> list[str]:
    errors: list[str] = []
    policy = load_json(root / "config" / "scenario-policy.json")
    payload = load_json(root / "evals" / "scenarios" / "candidate-scenarios.json")
    scenarios = payload.get("scenarios", [])
    minimum = policy.get("minimum_scenarios", 0)
    if minimum < 3:
        errors.append("scenario policy must require at least three scenarios")
    if len(scenarios) < minimum:
        errors.append(f"illustrative scenario set has fewer than {minimum} scenarios")
    required_sections = set(policy.get("required_sections", []))
    required_sections.update({"architecture", "system_software", "applications"})
    for scenario in scenarios:
        missing = required_sections - set(scenario)
        if missing:
            errors.append(f"scenario {scenario.get('scenario_id')} missing: {sorted(missing)}")
        if not scenario.get("center_impacts"):
            errors.append(f"scenario {scenario.get('scenario_id')} has no center impacts")
        if not scenario.get("technology_options"):
            errors.append(f"scenario {scenario.get('scenario_id')} has no worldwide technology comparison")
    criterion_ids = [item.get("criterion_id") for item in policy.get("evaluation_criteria", [])]
    if len(criterion_ids) != len(set(criterion_ids)):
        errors.append("scenario policy has duplicate criterion IDs")
    return errors


def validate_activation_configuration(root: Path) -> list[str]:
    errors: list[str] = []
    policy = load_json(root / "config" / "activation-policy.json")
    attestations = load_json(root / "config" / "owner-controls.json")

    for key in (
        "research_web_security_policy_ref",
        "execution_security_profiles_ref",
    ):
        ref = policy.get(key, "")
        parts = Path(ref).parts
        if not ref or Path(ref).is_absolute() or ".." in parts or not (root / ref).is_file():
            errors.append(f"activation policy has invalid or missing {key}: {ref}")
    if policy.get("production_security_profile_required") is not True:
        errors.append("activation policy must require a production Research Web security profile")

    def unique_ids(items: list[dict[str, Any]], label: str) -> set[str]:
        values = [item.get("control_id", "") for item in items]
        if len(values) != len(set(values)):
            errors.append(f"activation configuration has duplicate {label} control IDs")
        return set(values)

    workflow_ids = unique_ids(policy.get("required_workflow_gates", []), "workflow")
    component_ids = unique_ids(
        policy.get("required_production_components", []), "component"
    )
    if workflow_ids & component_ids:
        errors.append("activation workflow and component control IDs overlap")

    required_owner = policy.get("required_owner_controls", [])
    if len(required_owner) != len(set(required_owner)):
        errors.append("activation policy has duplicate owner control IDs")
    attested_owner = unique_ids(attestations.get("controls", []), "owner")
    if set(required_owner) != attested_owner:
        errors.append("owner-control attestations differ from activation policy")

    path_items = [
        (item.get("workflow_ref", ""), item.get("variable", ""))
        for item in policy.get("required_workflow_gates", [])
    ]
    path_items.extend(
        (item.get("path", ""), None)
        for item in policy.get("required_production_components", [])
    )
    for ref, variable in path_items:
        parts = Path(ref).parts
        if not ref or Path(ref).is_absolute() or ".." in parts:
            errors.append(f"activation reference is not repository-relative: {ref}")
            continue
        if variable:
            path = root / ref
            if not path.is_file() or variable not in path.read_text(encoding="utf-8"):
                errors.append(f"activation workflow lacks declared gate {variable}: {ref}")
    return errors


def validate_codeowners(root: Path) -> list[str]:
    errors: list[str] = []
    path = root / ".github" / "CODEOWNERS"
    rules: dict[str, list[str]] = {}
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        fields = line.split()
        if len(fields) < 2 or not all(owner.startswith("@") for owner in fields[1:]):
            errors.append(f"CODEOWNERS line {line_number} lacks a valid owner")
            continue
        if fields[0] in rules:
            errors.append(f"CODEOWNERS has duplicate pattern: {fields[0]}")
        rules[fields[0]] = fields[1:]
    required_patterns = {
        "/AGENTS.md",
        "/.github/**",
        "/config/**",
        "/schemas/**",
        "/skills/**",
        "/tools/**",
        "/docs/policies/**",
        "/docs/security/**",
        "/data/**",
        "/knowledge/**",
        "/roadmaps/**",
        "/reports/**",
        "/reviews/directives/**",
        "/reviews/run-approvals/**",
        "/LICENSE",
        "/NOTICE",
        "/requirements-validation.txt",
    }
    missing = sorted(required_patterns - set(rules))
    if missing:
        errors.append(f"CODEOWNERS lacks protected control-plane patterns: {missing}")
    return errors


def validate_canonical_claims(root: Path) -> list[str]:
    errors: list[str] = []
    for path in sorted((root / "knowledge" / "claims").glob("CLM-*.json")):
        record = load_json(path)
        claim = record.get("claim", {})
        provenance = record.get("provenance", {})
        claim_id = record.get("canonical_claim_id")
        relative = path.relative_to(root)
        if path.stem != claim_id or claim.get("claim_id") != claim_id:
            errors.append(f"Canonical Claim identity differs: {relative}")
        if claim.get("status") != "accepted":
            errors.append(f"Canonical Claim is not accepted: {relative}")
        expected_promotion_digest = stable_digest(
            {"claim": claim, "provenance": provenance}
        )
        if record.get("promotion_digest") != expected_promotion_digest:
            errors.append(f"Canonical Claim promotion digest differs: {relative}")

        proposal_ref = provenance.get("proposal_ref", "")
        decision_ref = provenance.get("decision_ref", "")
        proposal_path = root / proposal_ref
        decision_path = root / decision_ref
        if not proposal_path.is_file():
            errors.append(f"Canonical Claim Proposal is missing: {relative}")
            continue
        if not decision_path.is_file():
            errors.append(f"Canonical Claim Decision is missing: {relative}")
            continue
        proposal = load_json(proposal_path)
        decision = load_json(decision_path)
        if provenance.get("proposal_digest") != stable_digest(proposal):
            errors.append(f"Canonical Claim Proposal digest differs: {relative}")
        if provenance.get("decision_digest") != stable_digest(decision):
            errors.append(f"Canonical Claim Decision digest differs: {relative}")
        if (
            decision.get("proposal_id") != proposal.get("proposal_id")
            or decision.get("outcome") != "accepted"
        ):
            errors.append(f"Canonical Claim Decision is not accepted for Proposal: {relative}")
        if provenance.get("policy_id") != decision.get("policy_id"):
            errors.append(f"Canonical Claim Policy identity differs: {relative}")
        if proposal.get("claim_candidate", {}).get("claim_id") != claim_id:
            errors.append(f"Canonical Claim Proposal identity differs: {relative}")

        bundle_refs = provenance.get("evidence_bundle_refs", [])
        if bundle_refs != proposal.get("evidence_bundle_refs", []):
            errors.append(f"Canonical Claim Evidence references differ: {relative}")
        declared_digests = provenance.get("evidence_bundle_digests", {})
        if set(declared_digests) != set(bundle_refs):
            errors.append(f"Canonical Claim Evidence digest keys differ: {relative}")
        for bundle_ref in bundle_refs:
            bundle_path = root / bundle_ref
            if not bundle_path.is_file():
                errors.append(
                    f"Canonical Claim Evidence bundle is missing: {bundle_ref}"
                )
            elif declared_digests.get(bundle_ref) != stable_digest(
                load_json(bundle_path)
            ):
                errors.append(
                    f"Canonical Claim Evidence bundle digest differs: {bundle_ref}"
                )
    return errors


def validate_claim_status_events(root: Path) -> list[str]:
    errors: list[str] = []
    seen_claim_ids: set[str] = set()
    for path in sorted((root / "knowledge" / "claim-status").glob("CSE-*.json")):
        event = load_json(path)
        relative = path.relative_to(root)
        claim_id = event.get("claim_id", "")
        if event.get("event_id") != path.stem:
            errors.append(f"Canonical Claim status event identity differs: {relative}")
        if claim_id in seen_claim_ids:
            errors.append(f"Canonical Claim has multiple terminal status events: {claim_id}")
        seen_claim_ids.add(claim_id)
        if not isinstance(claim_id, str) or not re.fullmatch(r"CLM-[0-9]{6}", claim_id):
            errors.append(f"Canonical Claim status event has invalid Claim ID: {relative}")
            continue

        digest_payload = dict(event)
        event_digest = digest_payload.pop("event_digest", None)
        if event_digest != stable_digest(digest_payload):
            errors.append(f"Canonical Claim status event digest differs: {relative}")

        canonical_ref = event.get("canonical_claim_ref", "")
        expected_ref = f"knowledge/claims/{claim_id}.json"
        if canonical_ref != expected_ref:
            errors.append(f"Canonical Claim status event reference differs: {relative}")
        canonical_path = root / expected_ref
        if not canonical_path.is_file():
            errors.append(f"Status-event canonical Claim is missing: {relative}")
        else:
            canonical = load_json(canonical_path)
            if event.get("canonical_claim_digest") != stable_digest(canonical):
                errors.append(f"Status-event canonical Claim digest differs: {relative}")
            if canonical.get("claim", {}).get("status") != "accepted":
                errors.append(f"Status-event canonical Claim is not accepted: {relative}")

        directive_ref = event.get("directive_ref", "")
        directive_id = event.get("directive_id")
        if not isinstance(directive_id, str) or not re.fullmatch(
            r"DIR-[0-9]{6}", directive_id
        ):
            errors.append(f"Canonical status event has invalid Directive ID: {relative}")
            continue
        expected_directive_ref = f"reviews/directives/{directive_id}.json"
        directive_path = root / expected_directive_ref
        if directive_ref != expected_directive_ref:
            errors.append(f"Canonical status Directive reference differs: {relative}")
        if not directive_path.is_file():
            errors.append(f"Canonical status Directive is missing: {relative}")
            continue
        directive = load_json(directive_path)
        if event.get("directive_digest") != stable_digest(directive):
            errors.append(f"Canonical status Directive digest differs: {relative}")
        if (
            directive.get("directive_id") != event.get("directive_id")
            or directive.get("directive_type") != "canonical-status"
            or directive.get("status") not in {"approved", "completed"}
            or directive.get("public_information_confirmed") is not True
            or directive.get("claim_targets") != [claim_id]
        ):
            errors.append(f"Canonical status Directive does not authorize event: {relative}")
        if (
            directive.get("canonical_status_action") != event.get("action")
            or directive.get("canonical_status_reason", "").strip()
            != event.get("reason")
            or directive.get("replacement_claim_id")
            != event.get("replacement_claim_id")
        ):
            errors.append(f"Canonical status event differs from Directive: {relative}")

        replacement_id = event.get("replacement_claim_id")
        if event.get("action") == "superseded":
            replacement_path = root / "knowledge" / "claims" / f"{replacement_id}.json"
            if replacement_id == claim_id or not replacement_path.is_file():
                errors.append(f"Canonical status replacement Claim is invalid: {relative}")
            elif load_json(replacement_path).get("claim", {}).get("status") != "accepted":
                errors.append(f"Canonical status replacement Claim is not accepted: {relative}")
        elif replacement_id is not None:
            errors.append(f"Withdrawn Claim names a replacement: {relative}")
    return errors


def validate_knowledge_views(root: Path) -> list[str]:
    errors: list[str] = []
    index_path = root / "knowledge" / "claims" / "index.json"
    tbd_path = root / "TBD.md"
    if not index_path.is_file() or not tbd_path.is_file():
        return errors
    expected = build_index(root)
    if load_json(index_path) != expected:
        errors.append("Canonical knowledge index is stale or non-deterministic")
    if tbd_path.read_text(encoding="utf-8") != render_tbd(expected):
        errors.append("TBD.md differs from accepted canonical knowledge")
    return errors


def run(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_required_files(root))
    errors.extend(validate_json_files(root))
    errors.extend(validate_jsonl_files(root))
    if (root / "knowledge/public/conferences/HC2026.json").exists():
        from check_conference_coverage import validate_coverage
        try:
            validate_coverage(load_json(root / "knowledge/public/conferences/HC2026.json"),
                              load_json(root / "config/research-baseline.json"),
                              load_json(root / "knowledge/public/topic-decision-support.json"))
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f"Conference coverage: {exc}")
    if (root / "knowledge/public/procurement-cost-register.json").exists():
        from check_procurement_costs import validate_register
        try:
            validate_register(load_json(root / "knowledge/public/procurement-cost-register.json"),
                              load_json(root / "config/budget-planning.json"))
        except (ValueError, KeyError, TypeError) as exc:
            errors.append(f"Procurement cost register: {exc}")
    errors.extend(validate_run_approvals(root))
    errors.extend(validate_issue_payloads(root))
    if (root / "schemas").exists():
        errors.extend(validate_schema_headers(root))
    errors.extend(validate_workflow_action_pins(root))
    if (root / ".github" / "CODEOWNERS").exists():
        errors.extend(validate_codeowners(root))
    if (root / "config" / "consensus-policy.json").exists():
        errors.extend(validate_consensus_configuration(root))
    if (root / "config" / "budgets.json").exists():
        errors.extend(validate_runtime_configuration(root))
    if (root / "config" / "acquisition-policy.json").exists():
        errors.extend(validate_source_acquisition_configuration(root))
    if (root / "config" / "hpci-center-registry.json").exists():
        errors.extend(validate_center_registry(root))
    if (root / "config" / "research-baseline.json").exists():
        errors.extend(validate_research_baseline(root))
    if (root / "config" / "catalog-taxonomy.json").exists():
        errors.extend(validate_catalog_taxonomy(root))
    if (root / "config" / "source-watch-registry.json").exists():
        errors.extend(validate_source_watch_registry(root))
    if (root / "config" / "scenario-policy.json").exists():
        errors.extend(validate_scenario_configuration(root))
    if (root / "config" / "activation-policy.json").exists():
        errors.extend(validate_activation_configuration(root))
    if (root / "knowledge" / "claims").exists():
        errors.extend(validate_canonical_claims(root))
        errors.extend(validate_claim_status_events(root))
        errors.extend(validate_knowledge_views(root))
    if (root / "config" / "global-technology-scope.json").exists():
        errors.extend(validate_global_technology_scope(root))
    if (root / "config" / "monitors" / "MON-AUTO-TOPICS-001.json").exists():
        errors.extend(validate_research_topic_configuration(root))
    if (root / "config" / "publication-policy.json").exists():
        errors.extend(validate_publication_configuration(root))
    if (root / "runs").exists():
        errors.extend(validate_runtime_artifacts(root))
    return errors


def main() -> int:
    errors = run()
    if errors:
        print("OpenFS repository validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("OpenFS repository validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
