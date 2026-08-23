#!/usr/bin/env python3
"""Promote an accepted additive research-topic proposal into the catalog."""

from __future__ import annotations

import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any


TOPIC_ID = re.compile(r"^(ARCH|SSW|APP|CROSS)-[0-9]{2}$")
DOMAINS = {"architecture", "system-software", "applications", "cross-cutting"}
CADENCES = {"weekly", "monthly", "quarterly", "annual", "event-driven"}


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def validate_and_promote(
    proposal: dict[str, Any],
    decision: dict[str, Any],
    baseline: dict[str, Any],
    monitor: dict[str, Any],
    i18n: dict[str, Any],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    if proposal.get("object_type") != "research_topic":
        raise ValueError("proposal object_type must be research_topic")
    if proposal.get("change_type") != "additive":
        raise ValueError("automatic topic promotion is additive-only")
    if decision.get("proposal_id") != proposal.get("proposal_id"):
        raise ValueError("decision does not match proposal")
    if decision.get("object_type") != "research_topic":
        raise ValueError("decision object_type must be research_topic")
    if decision.get("outcome") != "accepted":
        raise ValueError("only an accepted decision can promote a research topic")
    checks = decision.get("policy_result", {}).get("checks", {})
    if not checks or not all(checks.values()):
        raise ValueError("accepted decision must contain passing policy checks")

    candidate = deepcopy(proposal.get("candidate_topic", {}))
    topic_id = candidate.get("topic_id", "")
    if not TOPIC_ID.fullmatch(topic_id):
        raise ValueError(f"invalid topic ID: {topic_id}")
    if candidate.get("domain") not in DOMAINS:
        raise ValueError(f"invalid topic domain: {candidate.get('domain')}")
    if candidate.get("review_cadence") not in CADENCES:
        raise ValueError(f"invalid review cadence: {candidate.get('review_cadence')}")
    for field in ("title_ja", "title_en", "research_questions", "evidence_expected", "outputs", "source_refs"):
        if not candidate.get(field):
            raise ValueError(f"candidate topic has no {field}")

    existing_ids = {item["topic_id"] for item in baseline.get("topics", [])}
    if topic_id in existing_ids:
        raise ValueError(f"topic already exists: {topic_id}")
    protected_before = deepcopy(baseline.get("initial_catalog"))

    sources = {item["source_id"]: item for item in baseline.get("source_corpus", [])}
    unknown_sources = set(candidate["source_refs"]) - set(sources)
    if unknown_sources:
        raise ValueError(f"candidate references unknown sources: {sorted(unknown_sources)}")
    actual_origins = {sources[source_id]["origin_group_id"] for source_id in candidate["source_refs"]}
    declared_origins = set(proposal.get("origin_group_ids", []))
    if len(actual_origins) < 2:
        raise ValueError("research-topic promotion requires at least two source origin groups")
    if not declared_origins.issubset(actual_origins):
        raise ValueError("proposal declares origin groups not supported by candidate source_refs")
    if not proposal.get("falsification_queries"):
        raise ValueError("research-topic proposal requires falsification queries")

    promoted_baseline = deepcopy(baseline)
    title_en = candidate.pop("title_en")
    candidate.update(
        {
            "status": "not-started",
            "catalog_origin": "ai-consensus",
            "proposal_id": proposal["proposal_id"],
            "added_by_decision_id": decision["decision_id"],
        }
    )
    promoted_baseline["topics"].append(candidate)
    promoted_baseline["catalog_revision"] = promoted_baseline.get("catalog_revision", 1) + 1
    created_at = proposal.get("created_at", "")
    if len(created_at) >= 10:
        promoted_baseline["derived_at"] = created_at[:10]
    if promoted_baseline.get("initial_catalog") != protected_before:
        raise ValueError("promotion attempted to change the protected initial catalog")

    promoted_monitor = deepcopy(monitor)
    entries = promoted_monitor.setdefault("topic_entries", [])
    if any(item.get("topic_id") == topic_id for item in entries):
        raise ValueError(f"monitor already contains topic: {topic_id}")
    query_plan = proposal["query_plan"]
    entries.append(
        {
            "topic_id": topic_id,
            "proposal_id": proposal["proposal_id"],
            "decision_id": decision["decision_id"],
            "languages": query_plan["languages"],
            "source_classes": query_plan["source_classes"],
            "query_families": query_plan["query_families"],
            "falsification_queries": proposal["falsification_queries"],
            "maximum_unchecked_days": query_plan["maximum_unchecked_days"],
            "status": "active",
        }
    )
    promoted_i18n = deepcopy(i18n)
    titles_en = promoted_i18n.setdefault("topic_titles_en", {})
    if topic_id in titles_en:
        raise ValueError(f"publication i18n already contains topic: {topic_id}")
    titles_en[topic_id] = title_en
    return promoted_baseline, promoted_monitor, promoted_i18n


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposal", required=True, type=Path)
    parser.add_argument("--decision", required=True, type=Path)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--monitor", required=True, type=Path)
    parser.add_argument("--i18n", required=True, type=Path)
    parser.add_argument("--output-baseline", required=True, type=Path)
    parser.add_argument("--output-monitor", required=True, type=Path)
    parser.add_argument("--output-i18n", required=True, type=Path)
    args = parser.parse_args()

    promoted_baseline, promoted_monitor, promoted_i18n = validate_and_promote(
        load_json(args.proposal),
        load_json(args.decision),
        load_json(args.baseline),
        load_json(args.monitor),
        load_json(args.i18n),
    )
    write_json(args.output_baseline, promoted_baseline)
    write_json(args.output_monitor, promoted_monitor)
    write_json(args.output_i18n, promoted_i18n)
    print(
        f"Promoted {promoted_baseline['topics'][-1]['topic_id']} via "
        f"{promoted_baseline['topics'][-1]['added_by_decision_id']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
