#!/usr/bin/env python3
"""Run dependency-free structural checks for the OpenFS repository."""

from __future__ import annotations

import json
import re
import sys
import hashlib
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
    "LICENSE",
    "NOTICE",
    "THIRD_PARTY_NOTICES.md",
    "docs/agent-onboarding.md",
    "docs/architecture.md",
    "docs/research-baseline/README.md",
    "docs/research-baseline/source-corpus.md",
    "docs/research-baseline/fs2-fs3-corpus-review.md",
    "docs/research-baseline/topic-inheritance.md",
    "docs/research-baseline/gap-register.md",
    "docs/planning/scenario-generation.md",
    "docs/planning/university-center-baseline.md",
    "docs/planning/presentation-mechanism.md",
    "docs/publication/github-pages.md",
    "docs/operations/automation-setup.md",
    "docs/governance/license-decision.md",
    "docs/research-baseline/ai-topic-promotion.md",
    "docs/policies/claim-acceptance.md",
    "docs/policies/information-boundary.md",
    "docs/policies/consensus-policy.md",
    "docs/security/threat-model.md",
    "config/consensus-policy.json",
    "config/acquisition-policy.json",
    "config/source-registry.json",
    "config/agent-registry.json",
    "config/role-permissions.json",
    "config/research-baseline.json",
    "config/scenario-policy.json",
    "config/global-technology-scope.json",
    "config/hpci-center-registry.json",
    "config/publication-policy.json",
    "config/publication-i18n.json",
    "schemas/proposal.schema.json",
    "schemas/claim.schema.json",
    "schemas/claim-proposal.schema.json",
    "schemas/source-lineage.schema.json",
    "schemas/assessment.schema.json",
    "schemas/decision.schema.json",
    "schemas/run.schema.json",
    "schemas/work-item.schema.json",
    "schemas/query-receipt.schema.json",
    "schemas/source-receipt.schema.json",
    "schemas/source-discovery-result.schema.json",
    "schemas/discovery-no-result.schema.json",
    "schemas/evidence.schema.json",
    "schemas/evidence-bundle.schema.json",
    "schemas/coverage-report.schema.json",
    "schemas/change-report.schema.json",
    "schemas/consensus-readiness.schema.json",
    "schemas/weekly-digest.schema.json",
    "schemas/issue-payload.schema.json",
    "schemas/directive-application.schema.json",
    "schemas/run-brief.schema.json",
    "schemas/weekly-cycle.schema.json",
    "schemas/handoff.schema.json",
    "schemas/research-baseline.schema.json",
    "schemas/center-profile.schema.json",
    "schemas/center-profile-coverage.schema.json",
    "schemas/profile-continuity.schema.json",
    "schemas/temporal-integrity.schema.json",
    "schemas/center-research-brief.schema.json",
    "schemas/center-followup-plan.schema.json",
    "schemas/hpci-center-registry.schema.json",
    "schemas/system-scenario.schema.json",
    "schemas/research-topic-proposal.schema.json",
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
    "tools/promote_research_topic.py",
    "tools/expand_topic_monitor.py",
    "tools/build_pages_site.py",
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
    "tools/evaluate_profile_continuity.py",
    "tools/evaluate_temporal_integrity.py",
    "tools/generate_center_research_brief.py",
    "tools/generate_center_followup_plan.py",
    "tools/propose_center_profile.py",
    "tools/detect_source_changes.py",
    "tools/check_consensus_readiness.py",
    "tools/generate_weekly_digest.py",
    "tools/prepare_exception_issues.py",
    "tools/apply_directive.py",
    "tools/generate_run_brief.py",
    "tools/prepare_weekly_cycle.py",
    "tools/publish_github_issue.py",
    "tools/create_handoff.py",
    "tools/accept_handoff.py",
    "tools/process_pending_handoffs.py",
    "tools/publish_control_pr.py",
    "queue/README.md",
    "runs/README.md",
    "state/README.md",
    "reviews/exceptions/README.md",
    "reviews/digests/README.md",
    "reviews/issues/README.md",
    "reviews/briefs/README.md",
    "reviews/followups/README.md",
    "handoffs/README.md",
    "proposals/center-profiles/README.md",
    "site/index.html",
    "site/styles.css",
    "site/app.js",
    ".github/workflows/pages.yml",
    ".github/workflows/weekly-coordinator.yml",
    ".github/workflows/handoff-control.yml",
]
ACTION_PATTERN = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)", re.MULTILINE)
FULL_SHA = re.compile(r"^[0-9a-f]{40}$")


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


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
        if "unconfigured" in identity or not all(identity) or not group:
            continue
        previous = configured_identities.setdefault(identity, group)
        if previous != group:
            errors.append(
                "same provider/model/prompt identity is split across independence groups: "
                f"{agent.get('agent_id')}"
            )
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
        slots = int(monitor.get("discovery_slots_per_query", 1))
        minimum_per_query = int(monitor.get("minimum_sources_per_query", 1))
        if slots < minimum_per_query:
            errors.append(
                f"monitor {monitor.get('monitor_id')} cannot meet minimum sources per query"
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
        receipt_ids = [item.get("query_receipt_id") for item in manifest.get("query_receipts", [])]
        if len(receipt_ids) != len(set(receipt_ids)):
            errors.append(f"Run {run_id} has duplicate Query Receipt IDs")
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

    source_ids_by_run: dict[str, list[str]] = {}
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
        if strict_assignment and work_item.get("kind") != "source-discovery":
            errors.append(f"Source result belongs to a non-discovery Work Item: {path.relative_to(root)}")
        if strict_assignment and query_receipt.get("query") != payload.get("query"):
            errors.append(f"Source result query differs from its assignment: {path.relative_to(root)}")
        expected_scope = {
            key: payload[key]
            for key in ("subject_ids", "profile_fields", "query_template_id")
            if key in payload
        }
        if result.get("object_type") == "discovery_no_result":
            if strict_assignment and query_receipt.get("language") not in payload.get("languages", []):
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
        if strict_assignment and source_receipt.get("language") not in payload.get("languages", []):
            errors.append(f"Source result language differs from its assignment: {path.relative_to(root)}")
        if strict_assignment and source_receipt.get("assignment_scope", {}) != expected_scope:
            errors.append(f"Source result subject scope differs from its assignment: {path.relative_to(root)}")
    for path in sorted((root / "proposals" / "evidence").glob("RUN-*/*.json")):
        bundle = load_json(path)
        if bundle.get("run_id") != path.parent.name:
            errors.append(f"Evidence bundle Run mismatch: {path.relative_to(root)}")
        source_ref = bundle.get("source_result_ref")
        if not source_ref or not (root / source_ref).is_file():
            errors.append(f"Evidence bundle source result is missing: {path.relative_to(root)}")
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
            candidate = proposal.get("claim_candidate", {})
            if set(candidate.get("evidence_ids", [])) != expected_evidence_ids:
                errors.append(f"Claim proposal Evidence IDs differ from bundles: {path.relative_to(root)}")
            if set(candidate.get("source_lineage_ids", [])) != expected_lineage_ids:
                errors.append(f"Claim proposal Lineage IDs differ from bundles: {path.relative_to(root)}")
            if set(proposal.get("origin_group_ids", [])) != expected_origins:
                errors.append(f"Claim proposal Origin Groups differ from bundles: {path.relative_to(root)}")
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
    errors: list[str] = []
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
        if not scenario.get("domestic_technology"):
            errors.append(f"scenario {scenario.get('scenario_id')} has no priority Japan technology comparison")
    criterion_ids = [item.get("criterion_id") for item in policy.get("evaluation_criteria", [])]
    if len(criterion_ids) != len(set(criterion_ids)):
        errors.append("scenario policy has duplicate criterion IDs")
    return errors


def run(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    errors.extend(validate_required_files(root))
    errors.extend(validate_json_files(root))
    errors.extend(validate_jsonl_files(root))
    if (root / "schemas").exists():
        errors.extend(validate_schema_headers(root))
    errors.extend(validate_workflow_action_pins(root))
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
    if (root / "config" / "scenario-policy.json").exists():
        errors.extend(validate_scenario_configuration(root))
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
