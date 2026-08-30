#!/usr/bin/env python3
"""Validate OpenFS contract artifacts with JSON Schema Draft 2020-12."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

try:
    from jsonschema import Draft202012Validator, FormatChecker
    from referencing import Registry, Resource
except ModuleNotFoundError as exc:  # pragma: no cover - exercised by CI setup
    raise SystemExit(
        "JSON Schema validation dependencies are missing; install "
        "requirements-validation.txt"
    ) from exc


ROOT = Path(__file__).resolve().parents[1]


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def schema_registry(root: Path) -> tuple[dict[str, dict[str, Any]], Registry]:
    schemas: dict[str, dict[str, Any]] = {}
    registry = Registry()
    for path in sorted((root / "schemas").glob("*.schema.json")):
        schema = read_json(path)
        Draft202012Validator.check_schema(schema)
        schemas[path.name] = schema
        registry = registry.with_resource(
            schema["$id"], Resource.from_contents(schema)
        )
    return schemas, registry


def contract_schema(path: Path, root: Path, payload: dict[str, Any]) -> str | None:
    ref = str(path.relative_to(root))
    if ref.startswith("proposals/research-unit-updates/"):
        return "research-unit-update.schema.json"
    if ref == "config/budget-planning.json":
        return "budget-planning.schema.json"
    if ref == "knowledge/public/procurement-cost-register.json":
        return "procurement-cost-register.schema.json"
    if ref == "config/research-baseline.json":
        return "research-baseline.schema.json"
    if ref == "config/catalog-taxonomy.json":
        return "catalog-taxonomy.schema.json"
    if ref == "config/catalog-migration.json":
        return "catalog-migration.schema.json"
    if ref == "config/roadmap-portfolio.json":
        return "roadmap-portfolio.schema.json"
    if ref == "config/skill-registry.json":
        return "skill-registry.schema.json"
    if ref == "config/hpci-center-registry.json":
        return "hpci-center-registry.schema.json"
    if ref == "config/activation-policy.json":
        return "activation-policy.schema.json"
    if ref == "config/agent-evaluation-policy.json":
        return "agent-evaluation-policy.schema.json"
    if ref == "config/owner-controls.json":
        return "owner-controls.schema.json"
    if ref == "config/research-web-security-policy.json":
        return "research-web-security-policy.schema.json"
    if ref == "config/execution-security-profiles.json":
        return "execution-security-profile.schema.json"
    if ref == "config/roadmap-gap-query-overrides.json":
        return "roadmap-gap-query-overrides.schema.json"
    if ref == "config/roadmap-source-retrieval-reviews.json":
        return "roadmap-source-retrieval-reviews.schema.json"
    if ref == "config/source-watch-registry.json":
        return "source-watch-registry.schema.json"
    if ref == "knowledge/public/topic-summaries.json":
        return "public-topic-summary.schema.json"
    if ref == "knowledge/public/topic-decision-support.json":
        return "public-topic-decision-support.schema.json"
    if ref == "knowledge/public/consensus-receipts.json":
        return "public-consensus-receipt.schema.json"
    if ref == "knowledge/public/roadmap-reference-data.json":
        return "roadmap-reference-data.schema.json"
    if ref == "knowledge/public/hpci-system-inventory.json":
        return "public-hpci-system-inventory.schema.json"
    if ref == "knowledge/public/application-performance-forecasts.json":
        return "public-application-performance-forecast.schema.json"
    if ref == "knowledge/public/source-catalog-map.json":
        return "source-catalog-map.schema.json"
    if ref.startswith("knowledge/public/roadmaps/"):
        return "public-roadmap.schema.json"
    if ref == "knowledge/public/audits/roadmap-source-audit.json":
        return "roadmap-source-audit.schema.json"
    if ref == "knowledge/public/audits/roadmap-source-triage.json":
        return "roadmap-source-triage.schema.json"
    if ref == "knowledge/public/audits/roadmap-evidence-audit.json":
        return "roadmap-evidence-audit.schema.json"
    if ref == "knowledge/public/audits/roadmap-freshness-audit.json":
        return "roadmap-freshness-audit.schema.json"
    if ref == "knowledge/public/audits/roadmap-gap-queue.json":
        return "roadmap-gap-queue.schema.json"
    if ref == "knowledge/public/audits/center-profile-assurance.json":
        return "center-profile-assurance.schema.json"
    if ref == "knowledge/public/dependencies/p0-roadmap-dependencies.json":
        return "roadmap-dependency-register.schema.json"
    if ref.startswith("roadmaps/scenarios/accepted/"):
        return (
            "published-scenario-set.schema.json"
            if "scenarios" in payload
            else "system-scenario.schema.json"
        )
    if ref.startswith("queue/"):
        return "work-item.schema.json"
    if ref.endswith("/manifest.json") and ref.startswith("runs/"):
        return "run.schema.json"
    run_names = {
        "coverage.json": "coverage-report.schema.json",
        "changes.json": "change-report.schema.json",
        "dependency-impact.json": "dependency-impact.schema.json",
        "consensus-readiness.json": "consensus-readiness.schema.json",
        "temporal-integrity.json": "temporal-integrity.schema.json",
        "promotion-readiness.json": "promotion-readiness.schema.json",
        "followup-effectiveness.json": "followup-effectiveness.schema.json",
        "global-followup-effectiveness.json": "global-followup-effectiveness.schema.json",
        "profile-continuity.json": "profile-continuity.schema.json",
    }
    if ref.startswith("runs/") and path.name in run_names:
        return run_names[path.name]
    if ref.startswith("_automation/") and path.name == "agent-evaluation-readiness.json":
        return "agent-evaluation-readiness.schema.json"
    if ref.startswith("runs/") and "/worker-invocations/" in ref:
        return "worker-invocation.schema.json"
    if ref.startswith("runs/") and "/worker-results/" in ref:
        return "worker-result.schema.json"
    if ref.startswith("proposals/sources/"):
        return (
            "discovery-no-result.schema.json"
            if payload.get("object_type") == "discovery_no_result"
            else "source-discovery-result.schema.json"
        )
    if ref.startswith("proposals/evidence/"):
        return "evidence-bundle.schema.json"
    if ref.startswith("proposals/claims/"):
        return "claim-proposal.schema.json"
    if ref.startswith("proposals/center-profiles/"):
        return "center-profile.schema.json"
    if ref.startswith("proposals/benchmark-results/"):
        return "benchmark-result-bundle.schema.json"
    if ref.startswith("proposals/agent-evaluations/"):
        return "agent-evaluation-bundle.schema.json"
    if ref == "evals/agent-harness/public-pilot-suite.json":
        return "agent-evaluation-task-suite.schema.json"
    if ref.startswith("proposals/workload-observations/"):
        return "workload-observation-summary.schema.json"
    if ref.startswith("proposals/portability-capability-matrices/"):
        return "portability-capability-matrix.schema.json"
    if ref.startswith("proposals/research-topics/"):
        return "research-topic-proposal.schema.json"
    if ref.startswith("assessments/CRP-"):
        return "consensus-package-review.schema.json"
    if ref.startswith("assessments/"):
        return "assessment.schema.json"
    if ref.startswith("decisions/"):
        return "decision.schema.json"
    if ref.startswith("handoffs/"):
        return "handoff.schema.json"
    if ref.startswith("reviews/directives/"):
        return "directive.schema.json"
    if ref.startswith("reviews/digests/"):
        return "weekly-digest.schema.json"
    if ref.startswith("reviews/issues/"):
        return "issue-payload.schema.json"
    if ref.startswith("reviews/run-approvals/"):
        return "run-approval.schema.json"
    if ref.startswith("reviews/consensus-packages/") and path.name == "manifest.json":
        return "consensus-review-package.schema.json"
    if ref.startswith("reviews/consensus-packages/") and path.name == "gate-result.json":
        return "consensus-package-gate-result.schema.json"
    if ref == "knowledge/claims/index.json":
        return "knowledge-index.schema.json"
    if ref.startswith("knowledge/claims/CLM-"):
        return "canonical-claim.schema.json"
    if ref.startswith("knowledge/claim-status/CSE-"):
        return "canonical-claim-status.schema.json"
    return None


def validate(root: Path = ROOT) -> tuple[list[str], int]:
    schemas, registry = schema_registry(root)
    errors: list[str] = []
    validated = 0
    for path in sorted(root.rglob("*.json")):
        if ".git" in path.parts or "inputs" in path.parts:
            continue
        payload = read_json(path)
        if not isinstance(payload, dict):
            continue
        schema_name = contract_schema(path, root, payload)
        if schema_name is None:
            continue
        validated += 1
        validator = Draft202012Validator(
            schemas[schema_name], registry=registry, format_checker=FormatChecker()
        )
        for error in sorted(validator.iter_errors(payload), key=lambda item: list(item.path)):
            location = "/".join(str(item) for item in error.absolute_path) or "$"
            errors.append(
                f"{path.relative_to(root)} [{schema_name}] {location}: {error.message}"
            )
    if not errors and (root / "knowledge/public/topic-decision-support.json").exists():
        from apply_research_unit_update import audit_updates
        errors.extend(audit_updates(root))
    return errors, validated


def main() -> int:
    errors, validated = validate()
    if errors:
        print(f"JSON Schema validation failed ({validated} artifacts):")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"JSON Schema validation passed ({validated} artifacts).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
