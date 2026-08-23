#!/usr/bin/env python3
"""Run dependency-free structural checks for the OpenFS repository."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = [
    "README.md",
    "AGENTS.md",
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
    "docs/policies/claim-acceptance.md",
    "docs/policies/information-boundary.md",
    "docs/policies/consensus-policy.md",
    "docs/security/threat-model.md",
    "config/consensus-policy.json",
    "config/agent-registry.json",
    "config/role-permissions.json",
    "config/research-baseline.json",
    "config/scenario-policy.json",
    "schemas/proposal.schema.json",
    "schemas/claim.schema.json",
    "schemas/source-lineage.schema.json",
    "schemas/assessment.schema.json",
    "schemas/decision.schema.json",
    "schemas/run.schema.json",
    "schemas/research-baseline.schema.json",
    "schemas/center-profile.schema.json",
    "schemas/system-scenario.schema.json",
    "docs/tasks/OFS-002.md",
    "docs/tasks/OFS-003.md",
    "docs/tasks/OFS-004.md",
    "config/monitors/MON-FS-BASELINE-001.json",
    "config/monitors/MON-HPCI-CENTERS-001.json",
    "config/monitors/MON-EMERGING-TOPICS-001.json",
    "evals/scenarios/candidate-scenarios.json",
    "tools/generate_scenario_views.py",
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
            errors.append(f"scenario {scenario.get('scenario_id')} has no domestic technology")
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
    if (root / "config" / "research-baseline.json").exists():
        errors.extend(validate_research_baseline(root))
    if (root / "config" / "scenario-policy.json").exists():
        errors.extend(validate_scenario_configuration(root))
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
