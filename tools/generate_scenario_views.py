#!/usr/bin/env python3
"""Validate HPCI scenarios and render reviewable Markdown and JSON views."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def normalize_scenarios(payload: dict[str, Any], policy: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    errors: list[str] = []
    scenarios = deepcopy(payload.get("scenarios", []))
    if len(scenarios) < policy["minimum_scenarios"]:
        errors.append(
            f"scenario set has {len(scenarios)} scenarios; policy requires "
            f"{policy['minimum_scenarios']}"
        )

    criterion_ids = [item["criterion_id"] for item in policy["evaluation_criteria"]]
    known_criteria = set(criterion_ids)
    scenario_ids: list[str] = []
    for scenario in scenarios:
        scenario_id = scenario.get("scenario_id", "<missing>")
        scenario_ids.append(scenario_id)
        for field in policy["required_sections"]:
            if field not in scenario or scenario[field] in (None, [], {}):
                if field != "evaluation":
                    errors.append(f"{scenario_id} has no {field}")

        evaluation = scenario.setdefault("evaluation", {})
        unknown = set(evaluation) - known_criteria
        if unknown:
            errors.append(f"{scenario_id} has unknown evaluation criteria: {sorted(unknown)}")
        for criterion_id in criterion_ids:
            evaluation.setdefault(
                criterion_id,
                {
                    "score": None,
                    "rationale": "Current accepted evidence and a human-approved weight are required.",
                    "evidence_refs": [],
                },
            )

    if len(scenario_ids) != len(set(scenario_ids)):
        errors.append("scenario IDs are not unique")

    weights = [item.get("weight") for item in policy["evaluation_criteria"]]
    ranking_enabled = all(isinstance(weight, (int, float)) for weight in weights)
    if ranking_enabled and abs(sum(weights) - 1.0) > 1e-9:
        errors.append("scenario weights must sum to 1.0")

    normalized = {
        "schema_version": payload.get("schema_version", "0.1.0"),
        "set_id": payload.get("set_id", "UNKNOWN"),
        "as_of": payload.get("as_of"),
        "status": payload.get("status", "candidate"),
        "notice": payload.get("notice", ""),
        "policy_id": policy["policy_id"],
        "ranking_enabled": ranking_enabled,
        "scenarios": scenarios,
    }
    return normalized, errors


def text_value(value: Any) -> str:
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    if isinstance(value, dict):
        return "; ".join(f"{key}: {text_value(item)}" for key, item in value.items())
    return str(value)


def render_object(title: str, value: dict[str, Any]) -> list[str]:
    lines = [f"### {title}", ""]
    for key, item in value.items():
        lines.append(f"- **{key}:** {text_value(item)}")
    lines.append("")
    return lines


def render_markdown(payload: dict[str, Any], policy: dict[str, Any]) -> str:
    criteria = {item["criterion_id"]: item for item in policy["evaluation_criteria"]}
    lines = [
        "# HPCI System Development Scenario Comparison",
        "",
        f"- Scenario set: `{payload['set_id']}`",
        f"- As of: `{payload.get('as_of') or 'not-specified'}`",
        f"- Status: `{payload['status']}`",
        f"- Policy: `{payload['policy_id']}`",
        f"- Ranking: `{'enabled' if payload['ranking_enabled'] else 'disabled'}`",
        "",
        f"> {payload['notice'] or 'Candidate material. Human approval is required before recommendation or publication.'}",
        "",
        "## Scenario overview",
        "",
        "| Scenario | Objective | Architecture | System software | Applications |",
        "|---|---|---|---|---|",
    ]
    for scenario in payload["scenarios"]:
        lines.append(
            f"| `{scenario['scenario_id']}` {scenario['title_ja']} | {scenario['objective']} | "
            f"{text_value(scenario['architecture'])} | {text_value(scenario['system_software'])} | "
            f"{text_value(scenario['applications'])} |"
        )

    for scenario in payload["scenarios"]:
        lines.extend(["", f"## {scenario['title_ja']} (`{scenario['scenario_id']}`)", "", scenario["objective"], ""])
        lines.extend(render_object("Architecture", scenario["architecture"]))
        lines.extend(render_object("System software", scenario["system_software"]))
        lines.extend(render_object("Applications", scenario["applications"]))
        lines.extend(["### Center impacts", "", "| Center group | Fit | Migration | Unverified conditions |", "|---|---|---|---|"])
        for impact in scenario["center_impacts"]:
            lines.append(
                f"| {impact['center_group']} | {impact['fit']} | {impact['migration']} | "
                f"{text_value(impact['unverified_conditions'])} |"
            )
        lines.extend(["", "### Technology options", "", "| Candidate | Role | Maturity gate | Fallback |", "|---|---|---|---|"])
        for item in scenario["technology_options"]:
            lines.append(
                f"| {item['candidate']} | {item['role']} | {item['maturity_gate']} | {item['fallback']} |"
            )
        lines.extend(["", "### Evaluation", "", "| Criterion | Score | Rationale | Evidence |", "|---|---:|---|---|"])
        for criterion_id, criterion in criteria.items():
            evaluation = scenario["evaluation"][criterion_id]
            score = evaluation["score"] if evaluation["score"] is not None else "not scored"
            lines.append(
                f"| {criterion['title_ja']} | {score} | {evaluation['rationale']} | "
                f"{text_value(evaluation['evidence_refs'])} |"
            )
        lines.extend(["", "### Uncertainties", ""])
        lines.extend(f"- {item}" for item in scenario["uncertainties"])
        lines.extend(["", "### Decision gates", ""])
        lines.extend(f"- {item}" for item in scenario["decision_gates"])
        lines.extend(["", "### Traceability", "", f"Evidence references: {text_value(scenario['evidence_refs'])}", ""])

    return "\n".join(lines).rstrip() + "\n"


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--policy", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    parser.add_argument("--output-json", type=Path, required=True)
    args = parser.parse_args()

    policy = load_json(args.policy)
    normalized, errors = normalize_scenarios(load_json(args.input), policy)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    write_text(args.output_markdown, render_markdown(normalized, policy))
    write_text(args.output_json, json.dumps(normalized, ensure_ascii=False, indent=2) + "\n")
    print(
        f"Rendered {len(normalized['scenarios'])} scenarios; "
        f"ranking_enabled={normalized['ranking_enabled']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
