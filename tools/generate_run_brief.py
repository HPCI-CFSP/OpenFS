#!/usr/bin/env python3
"""Generate a human-review brief from a completed OpenFS Run."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json


ROOT = Path(__file__).resolve().parents[1]
GOVERNANCE_CONDITION_MARKERS = (
    "origin group",
    "assessment",
    "reviewer",
    "corroboration",
    "consensus",
)


def _optional_json(path: Path) -> dict[str, Any] | None:
    return read_json(path) if path.is_file() else None


def _source_for_evidence(root: Path, evidence_ref: str) -> dict[str, Any]:
    bundle = read_json(root / evidence_ref)
    source_result = read_json(root / bundle["source_result_ref"])
    receipt = source_result["source_receipt"]
    return {
        "source_id": receipt["source_id"],
        "title": receipt["title"],
        "publisher": receipt["publisher"],
        "canonical_url": receipt["canonical_url"],
        "source_class": receipt["source_class"],
        "primary_source": receipt["primary_source"],
        "origin_group_id": receipt["origin_group_id"],
        "evidence_ref": evidence_ref,
    }


def build_brief(
    root: Path, *, run_id: str, generated_at: str | None = None
) -> dict[str, Any]:
    manifest = read_json(root / "runs" / run_id / "manifest.json")
    coverage = _optional_json(root / "runs" / run_id / "coverage.json")
    changes = _optional_json(root / "runs" / run_id / "changes.json")
    decisions = {
        item["proposal_id"]: item
        for path in sorted((root / "decisions" / run_id).glob("*.json"))
        for item in [read_json(path)]
    }
    assessments: dict[str, list[dict[str, Any]]] = {}
    for path in sorted((root / "assessments" / run_id).rglob("*.json")):
        assessment = read_json(path)
        assessments.setdefault(assessment["proposal_id"], []).append(assessment)

    claims: list[dict[str, Any]] = []
    for path in sorted((root / "proposals" / "claims" / run_id).glob("*.json")):
        proposal = read_json(path)
        candidate = proposal["claim_candidate"]
        decision = decisions.get(proposal["proposal_id"])
        source_map: dict[str, dict[str, Any]] = {}
        for evidence_ref in proposal["evidence_bundle_refs"]:
            source = _source_for_evidence(root, evidence_ref)
            source_map[source["source_id"]] = source
        reviews = assessments.get(proposal["proposal_id"], [])
        condition_warnings = [
            "This condition encodes review or evidence governance state; use the "
            "structured Evidence summary and Consensus checks instead."
            for condition in candidate.get("conditions", [])
            if any(
                marker in condition.lower()
                for marker in GOVERNANCE_CONDITION_MARKERS
            )
        ]
        claims.append(
            {
                "proposal_id": proposal["proposal_id"],
                "claim_id": candidate["claim_id"],
                "statement": candidate["statement"],
                "claim_kind": candidate["claim_kind"],
                "temporal_scope": candidate.get("temporal_scope"),
                "conditions": candidate.get("conditions", []),
                "condition_warnings": condition_warnings,
                "evidence_summary": {
                    "source_count": len(source_map),
                    "origin_group_count": len(
                        {item["origin_group_id"] for item in source_map.values()}
                    ),
                    "primary_source_count": sum(
                        bool(item["primary_source"])
                        for item in source_map.values()
                    ),
                },
                "outcome": decision["outcome"] if decision else "not-evaluated",
                "unmet_consensus_checks": sorted(
                    key
                    for key, passed in (decision or {})
                    .get("policy_result", {})
                    .get("checks", {})
                    .items()
                    if not passed
                ),
                "sources": sorted(source_map.values(), key=lambda item: item["source_id"]),
                "assessments": [
                    {
                        "assessment_id": item["assessment_id"],
                        "verdict": item["verdict"],
                        "reviewer_agent_id": item["reviewer_agent_id"],
                        "agent_independence_group": item["agent_independence_group"],
                        "objections": item.get("objections", []),
                    }
                    for item in reviews
                ],
            }
        )

    outcomes: dict[str, int] = {}
    for claim in claims:
        outcomes[claim["outcome"]] = outcomes.get(claim["outcome"], 0) + 1
    return {
        "schema_version": "0.1.0",
        "brief_id": f"BRIEF-{run_id}",
        "run_id": run_id,
        "generated_at": generated_at or isoformat(),
        "publication_status": "internal-review-only",
        "review_status": (
            "human-review-required"
            if any(item["outcome"] != "accepted" for item in claims)
            else "eligible-for-publication-review"
        ),
        "run_status": manifest["status"],
        "research_status": manifest["research_status"],
        "coverage_status": (
            coverage["coverage_status"] if coverage else "not-evaluated"
        ),
        "consensus_readiness": manifest.get("metrics", {}).get(
            "consensus_readiness", "not-evaluated"
        ),
        "source_change_summary": changes["summary"] if changes else {},
        "claim_outcomes": outcomes,
        "claims": claims,
        "caveats": [
            "This brief is a generated review view, not primary evidence.",
            "Only accepted artifacts may enter the publication workflow.",
            "Source links and repository evidence records must be checked before use.",
        ],
    }


def _safe(value: Any) -> str:
    return str(value).replace("<", "&lt;").replace(">", "&gt;")


def render_markdown(brief: dict[str, Any]) -> str:
    lines = [
        f"# OpenFS Run Brief: {brief['run_id']}",
        "",
        f"Generated: `{brief['generated_at']}`",
        "",
        f"- Run: **{brief['run_status']}**",
        f"- Research: **{brief['research_status']}**",
        f"- Coverage: **{brief['coverage_status']}**",
        f"- Consensus capacity: **{brief['consensus_readiness']}**",
        f"- Review: **{brief['review_status']}**",
        "",
        "## Claims for review",
        "",
    ]
    for index, claim in enumerate(brief["claims"], 1):
        lines.extend(
            [
                f"### {index}. `{claim['claim_id']}` ({claim['outcome']})",
                "",
                _safe(claim["statement"]),
                "",
                "Structured Evidence: "
                f"**{claim['evidence_summary']['source_count']} Sources / "
                f"{claim['evidence_summary']['origin_group_count']} Origin Groups / "
                f"{claim['evidence_summary']['primary_source_count']} primary Sources**",
                "",
            ]
        )
        if claim["conditions"]:
            lines.append("Conditions:")
            lines.extend(f"- {_safe(item)}" for item in claim["conditions"])
            lines.append("")
        if claim["condition_warnings"]:
            lines.append("Condition warnings:")
            lines.extend(
                f"- **warning**: {_safe(item)}"
                for item in claim["condition_warnings"]
            )
            lines.append("")
        lines.append("Sources:")
        for source in claim["sources"]:
            lines.append(
                f"- [{_safe(source['title'])}]({source['canonical_url']}) "
                f"({_safe(source['publisher'])}, `{source['source_class']}`)"
            )
        lines.append("")
        if claim["unmet_consensus_checks"]:
            lines.append(
                "Unmet checks: "
                + ", ".join(f"`{item}`" for item in claim["unmet_consensus_checks"])
            )
            lines.append("")
        objections = [
            objection
            for assessment in claim["assessments"]
            for objection in assessment["objections"]
        ]
        if objections:
            lines.append("Reviewer objections:")
            lines.extend(
                f"- **{item['severity']}**: {_safe(item['message'])}"
                for item in objections
            )
            lines.append("")
    lines.extend(["## Caveats", ""])
    lines.extend(f"- {item}" for item in brief["caveats"])
    return "\n".join(lines) + "\n"


def write_brief(root: Path, brief: dict[str, Any]) -> tuple[Path, Path]:
    base = root / "reviews" / "briefs" / brief["run_id"]
    json_path = base.with_suffix(".json")
    markdown_path = base.with_suffix(".md")
    atomic_write_json(json_path, brief)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_markdown(brief), encoding="utf-8")
    return json_path, markdown_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--generated-at")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    brief = build_brief(
        args.root, run_id=args.run_id, generated_at=args.generated_at
    )
    outputs = write_brief(args.root, brief)
    print(json.dumps({"outputs": [str(path) for path in outputs]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
