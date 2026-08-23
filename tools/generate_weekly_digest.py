#!/usr/bin/env python3
"""Generate an auditable weekly view of Runs, changes, gaps, and exceptions."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, exception_group_key, isoformat, read_json


ROOT = Path(__file__).resolve().parents[1]


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _iso_week(value: datetime) -> str:
    year, week, _ = value.isocalendar()
    return f"{year:04d}-W{week:02d}"


def _monitor_snapshot(root: Path, manifest: dict[str, Any]) -> dict[str, Any]:
    monitor_ref = next(
        (
            source
            for source in manifest.get("policy_hashes", {})
            if source.startswith("config/monitors/")
        ),
        None,
    )
    if not monitor_ref:
        return {}
    snapshot = manifest.get("configuration_snapshots", {}).get(
        monitor_ref, monitor_ref
    )
    return read_json(root / snapshot)


def _selected_manifests(root: Path, week: str, run_ids: list[str] | None) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    paths = (
        [root / "runs" / run_id / "manifest.json" for run_id in run_ids]
        if run_ids
        else sorted((root / "runs").glob("RUN-*/manifest.json"))
    )
    for path in paths:
        if not path.is_file():
            raise ValueError(f"Run manifest is missing: {path}")
        manifest = read_json(path)
        observed_at = manifest.get("completed_at") or manifest["started_at"]
        if run_ids or _iso_week(_parse_time(observed_at)) == week:
            selected.append(manifest)
    return sorted(selected, key=lambda item: item["run_id"])


def build_digest(
    root: Path,
    *,
    week: str,
    run_ids: list[str] | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    generated_at = generated_at or isoformat()
    generated_time = _parse_time(generated_at)
    manifests = _selected_manifests(root, week, run_ids)
    selected_ids = [item["run_id"] for item in manifests]
    run_summaries: list[dict[str, Any]] = []
    gaps: list[dict[str, Any]] = []
    dissent: list[dict[str, Any]] = []
    stale: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    exceptions: list[dict[str, Any]] = []
    dependency_impacts: list[dict[str, Any]] = []
    temporal_failure_count = 0
    continuity_failure_count = 0
    ineffective_followup_count = 0
    ineffective_global_followup_count = 0
    publisher_independence_failure_count = 0
    persistent_query_count = 0
    publication_blocked_count = 0
    dependency_promotion_block_count = 0
    reobservation_gap_count = 0
    change_totals = {
        name: 0 for name in ("new", "changed", "unchanged", "unavailable", "not-observed")
    }

    for manifest in manifests:
        run_id = manifest["run_id"]
        monitor = _monitor_snapshot(root, manifest)
        coverage_path = root / "runs" / run_id / "coverage.json"
        coverage = read_json(coverage_path) if coverage_path.is_file() else None
        change_ref = manifest.get("change_report_ref")
        changes = read_json(root / change_ref) if change_ref else None
        if changes:
            for name, count in changes["summary"].items():
                change_totals[name] = change_totals.get(name, 0) + count
        dependency_ref = manifest.get("dependency_impact_ref")
        dependency = read_json(root / dependency_ref) if dependency_ref else None
        dependency_summary = dependency.get("summary", {}) if dependency else {}
        if dependency_summary.get("promotion_blocked"):
            dependency_promotion_block_count += 1
        reobservation_gap_count += int(
            dependency_summary.get("reobservation_gaps", 0)
        )
        if dependency:
            for item in dependency.get("impacts", []):
                if item.get("action") == "none":
                    continue
                dependency_impacts.append(
                    {
                        "run_id": run_id,
                        "dependency_impact_ref": dependency_ref,
                        "canonical_url": item["canonical_url"],
                        "classification": item["classification"],
                        "action": item["action"],
                        "promotion_blocked": item["promotion_blocked"],
                        "artifact_refs": sorted(
                            set(
                                item.get("claim_proposal_refs", [])
                                + item.get("center_profile_refs", [])
                                + item.get("decision_refs", [])
                            )
                        ),
                    }
                )
        readiness_ref = manifest.get("consensus_readiness_ref")
        readiness = read_json(root / readiness_ref) if readiness_ref else None
        temporal_ref = manifest.get("temporal_integrity_ref")
        temporal = read_json(root / temporal_ref) if temporal_ref else None
        temporal_status = temporal.get("status", "not-evaluated") if temporal else "not-evaluated"
        continuity_ref = manifest.get("profile_continuity_ref")
        continuity = read_json(root / continuity_ref) if continuity_ref else None
        continuity_status = (
            continuity.get("status", "not-evaluated")
            if continuity
            else "not-evaluated"
        )
        effectiveness_ref = manifest.get("followup_effectiveness_ref")
        effectiveness = read_json(root / effectiveness_ref) if effectiveness_ref else None
        effectiveness_status = (
            effectiveness.get("status", "not-evaluated")
            if effectiveness
            else "not-evaluated"
        )
        global_effectiveness_ref = manifest.get("global_followup_effectiveness_ref")
        global_effectiveness = (
            read_json(root / global_effectiveness_ref)
            if global_effectiveness_ref
            else None
        )
        global_effectiveness_status = (
            global_effectiveness.get("status", "not-evaluated")
            if global_effectiveness
            else "not-evaluated"
        )
        run_decisions = [
            read_json(path)
            for path in sorted((root / "decisions" / run_id).glob("*.json"))
        ]
        publisher_failures = sum(
            decision.get("policy_result", {})
            .get("checks", {})
            .get("minimum_publisher_groups")
            is False
            for decision in run_decisions
        )
        learned_queries = len(monitor.get("persistent_query_families", []))
        publisher_independence_failure_count += publisher_failures
        persistent_query_count += learned_queries
        run_exceptions = []
        for path in sorted((root / "reviews" / "exceptions" / run_id).glob("*.json")):
            exception = read_json(path)
            if exception.get("status") != "open":
                continue
            run_exceptions.append(
                {
                    "exception_id": exception["exception_id"],
                    "run_id": run_id,
                    "exception_kind": exception.get(
                        "exception_kind",
                        exception.get("error", {}).get("kind", "work-item-failure"),
                    ),
                    "exception_ref": str(path.relative_to(root)),
                    "requires_owner_action": exception.get(
                        "requires_owner_action", True
                    ),
                    "publication_blocked": exception.get(
                        "publication_blocked", False
                    ),
                    "unmet_requirements": sorted(
                        exception.get("unmet_requirements", [])
                    ),
                }
            )
        exceptions.extend(run_exceptions)
        publication_block_reasons = []
        if temporal and temporal.get("publication_blocked"):
            publication_block_reasons.append("temporal-integrity")
        if continuity and continuity.get("publication_blocked"):
            publication_block_reasons.append("profile-continuity")
        publication_block_reasons.extend(
            item["exception_kind"]
            for item in run_exceptions
            if item["publication_blocked"]
        )
        publication_block_reasons = sorted(set(publication_block_reasons))
        publication_blocked = bool(publication_block_reasons)
        if temporal_status == "failed":
            temporal_failure_count += 1
        if continuity_status == "failed":
            continuity_failure_count += 1
        if effectiveness_status == "ineffective":
            ineffective_followup_count += 1
        if global_effectiveness_status == "ineffective":
            ineffective_global_followup_count += 1
        if publication_blocked:
            publication_blocked_count += 1
        run_summaries.append(
            {
                "run_id": run_id,
                "task_id": manifest["task_id"],
                "monitor_id": manifest["monitor_id"],
                "status": manifest["status"],
                "research_status": manifest["research_status"],
                "coverage_status": coverage.get("coverage_status") if coverage else "not-evaluated",
                "consensus_readiness": readiness.get("status") if readiness else "not-evaluated",
                "temporal_integrity": temporal_status,
                "profile_continuity": continuity_status,
                "followup_effectiveness": effectiveness_status,
                "effective_followup_queries": (
                    effectiveness.get("effective_query_count") if effectiveness else None
                ),
                "followup_query_count": (
                    effectiveness.get("query_count") if effectiveness else None
                ),
                "global_followup_effectiveness": global_effectiveness_status,
                "effective_global_followup_queries": (
                    global_effectiveness.get("effective_query_count")
                    if global_effectiveness
                    else None
                ),
                "global_followup_query_count": (
                    global_effectiveness.get("query_count")
                    if global_effectiveness
                    else None
                ),
                "persistent_query_count": learned_queries,
                "publisher_independence_failures": publisher_failures,
                "publication_blocked": publication_blocked,
                "publication_block_reasons": publication_block_reasons,
                "dependency_promotion_blocked": bool(
                    dependency_summary.get("promotion_blocked", False)
                ),
                "reobservation_gaps": int(
                    dependency_summary.get("reobservation_gaps", 0)
                ),
                "consensus_outcomes": manifest.get("metrics", {}).get("consensus_outcomes", {}),
                "cost": manifest.get("cost", {"measurement_status": "unreported"}),
            }
        )
        if coverage:
            for category, values in coverage.get("gaps", {}).items():
                if values:
                    gaps.append({"run_id": run_id, "category": category, "values": values})
        for decision in run_decisions:
            if decision.get("dissent_assessment_ids") or decision.get("outcome") in {
                "contested",
                "rejected",
            }:
                dissent.append(
                    {
                        "run_id": run_id,
                        "decision_id": decision["decision_id"],
                        "outcome": decision["outcome"],
                        "dissent_assessment_ids": decision.get("dissent_assessment_ids", []),
                    }
                )
        maximum_days = monitor.get("maximum_unchecked_days")
        if maximum_days is not None:
            for path in sorted((root / "proposals" / "sources" / run_id).glob("*.json")):
                result = read_json(path)
                if result.get("object_type") == "discovery_no_result":
                    continue
                receipt = result["source_receipt"]
                age_days = (generated_time - _parse_time(receipt["retrieved_at"])).total_seconds() / 86400
                if age_days > float(maximum_days):
                    stale.append(
                        {
                            "run_id": run_id,
                            "source_id": receipt["source_id"],
                            "canonical_url": receipt["canonical_url"],
                            "age_days": round(age_days, 2),
                            "maximum_unchecked_days": maximum_days,
                        }
                    )
        for path in sorted((root / "queue" / run_id).glob("*.json")):
            item = read_json(path)
            if item.get("status") == "dead-letter":
                failures.append(
                    {
                        "run_id": run_id,
                        "work_item_id": item["work_item_id"],
                        "error_kind": item.get("last_error", {}).get("kind", "unknown"),
                    }
                )
    pending_directives = []
    for path in sorted((root / "reviews" / "directives").glob("DIR-*.json")):
        directive = read_json(path)
        if directive.get("status") in {"proposed", "approved", "scheduled", "running"}:
            pending_directives.append(
                {
                    "directive_id": directive["directive_id"],
                    "title": directive["title"],
                    "status": directive["status"],
                    "scope": directive.get("scope", []),
                }
            )
    grouped_actions: dict[tuple[str, tuple[str, ...], bool], list[dict[str, Any]]] = {}
    for item in exceptions:
        if not item["requires_owner_action"]:
            continue
        fingerprint = exception_group_key(item)
        grouped_actions.setdefault(fingerprint, []).append(item)
    owner_actions = []
    for sequence, (fingerprint, items) in enumerate(
        sorted(grouped_actions.items()), 1
    ):
        owner_actions.append(
            {
                "action_id": f"ACTION-GROUP-{sequence:03d}",
                "kind": "resolve-exception-group",
                "exception_kind": fingerprint[0],
                "unmet_requirements": list(fingerprint[1]),
                "publication_blocked": fingerprint[2],
                "run_ids": sorted({item["run_id"] for item in items}),
                "exception_refs": sorted(item["exception_ref"] for item in items),
            }
        )
    grouped_dependency_actions: dict[str, list[dict[str, Any]]] = {}
    for item in dependency_impacts:
        grouped_dependency_actions.setdefault(item["action"], []).append(item)
    for action, items in sorted(grouped_dependency_actions.items()):
        owner_actions.append(
            {
                "action_id": f"ACTION-GROUP-{len(owner_actions) + 1:03d}",
                "kind": "review-dependency-impact",
                "dependency_action": action,
                "promotion_blocked": any(item["promotion_blocked"] for item in items),
                "run_ids": sorted({item["run_id"] for item in items}),
                "dependency_impact_refs": sorted(
                    {item["dependency_impact_ref"] for item in items}
                ),
                "canonical_urls": sorted({item["canonical_url"] for item in items}),
                "artifact_refs": sorted(
                    {ref for item in items for ref in item["artifact_refs"]}
                ),
            }
        )
    return {
        "schema_version": "0.1.0",
        "digest_id": f"DIGEST-{week}",
        "week": week,
        "generated_at": generated_at,
        "run_ids": selected_ids,
        "summary": {
            "run_count": len(manifests),
            "open_exception_count": len(exceptions),
            "owner_action_count": len(owner_actions),
            "coverage_gap_count": len(gaps),
            "failure_count": len(failures),
            "temporal_failure_count": temporal_failure_count,
            "continuity_failure_count": continuity_failure_count,
            "ineffective_followup_count": ineffective_followup_count,
            "ineffective_global_followup_count": ineffective_global_followup_count,
            "publisher_independence_failure_count": publisher_independence_failure_count,
            "persistent_query_count": persistent_query_count,
            "publication_blocked_count": publication_blocked_count,
            "dependency_promotion_block_count": dependency_promotion_block_count,
            "reobservation_gap_count": reobservation_gap_count,
        },
        "runs": run_summaries,
        "source_changes": change_totals,
        "coverage_gaps": gaps,
        "dissent": dissent,
        "stale_sources": stale,
        "failures": failures,
        "open_exceptions": exceptions,
        "dependency_impacts": dependency_impacts,
        "pending_directives": pending_directives,
        "owner_actions": owner_actions,
        "caveats": [
            "This Digest is a generated operational view, not primary evidence.",
            "Unreported cost is unknown and must not be interpreted as zero.",
            "not-observed Sources are not inferred to be withdrawn or unavailable.",
            "Dependency promotion blocks remain until recorded revalidation; the Digest does not clear them.",
        ],
    }


def render_markdown(digest: dict[str, Any]) -> str:
    lines = [
        f"# OpenFS Weekly Digest: {digest['week']}",
        "",
        f"Generated: `{digest['generated_at']}`",
        "",
        "## Run summary",
        "",
        "| Run | Task / Monitor | Run status | Research | Coverage | Consensus capacity | Time audit | Continuity | Follow-up yield | Loop learning | Publication | Cost |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for run in digest["runs"]:
        cost = run["cost"]
        amount = cost.get("reported_total_usd")
        cost_text = cost.get("measurement_status", "unreported")
        if amount is not None:
            cost_text += f" (${amount:.4f} reported)"
        followup_parts = []
        followup_text = run["followup_effectiveness"]
        if run["followup_query_count"] is not None:
            followup_text += (
                f" ({run['effective_followup_queries']}/{run['followup_query_count']})"
            )
        if followup_text != "not-evaluated":
            followup_parts.append(f"center: {followup_text}")
        global_followup_text = run["global_followup_effectiveness"]
        if run["global_followup_query_count"] is not None:
            global_followup_text += (
                f" ({run['effective_global_followup_queries']}/"
                f"{run['global_followup_query_count']})"
            )
        if global_followup_text != "not-evaluated":
            followup_parts.append(f"global: {global_followup_text}")
        followup_text = "; ".join(followup_parts) or "not-evaluated"
        learning_text = (
            f"persistent {run['persistent_query_count']}; "
            f"publisher gaps {run['publisher_independence_failures']}"
        )
        lines.append(
            f"| `{run['run_id']}` | `{run['task_id']}` / `{run['monitor_id']}` | "
            f"{run['status']} | {run['research_status']} | {run['coverage_status']} | "
            f"{run['consensus_readiness']} | {run['temporal_integrity']} | "
            f"{run['profile_continuity']} | "
            f"{followup_text} | "
            f"{learning_text} | "
            f"{'blocked: ' + ', '.join(run['publication_block_reasons']) if run['publication_blocked'] else 'not blocked'} | {cost_text} |"
        )
    if not digest["runs"]:
        lines.append("| None | - | - | - | - | - | - | - | - | - | - | - |")
    lines.extend(
        [
            "",
            "## Source changes",
            "",
            " | ".join(f"{key}: **{value}**" for key, value in digest["source_changes"].items()),
            "",
            "## Owner actions",
            "",
        ]
    )
    if digest["owner_actions"]:
        for action in digest["owner_actions"]:
            if action["kind"] == "resolve-exception-group":
                lines.append(
                    f"- **{action['exception_kind']}**: resolve "
                    f"{len(action['exception_refs'])} related Exception(s) across "
                    f"{len(action['run_ids'])} Run(s)."
                )
                if action["unmet_requirements"]:
                    lines.append(
                        "  Requirements: "
                        + ", ".join(
                            f"`{item}`" for item in action["unmet_requirements"]
                        )
                    )
                lines.extend(f"  - `{item}`" for item in action["exception_refs"])
            else:
                block_text = "promotion blocked" if action["promotion_blocked"] else "reobservation requested"
                lines.append(
                    f"- **{action['dependency_action']}**: review "
                    f"{len(action['canonical_urls'])} Source observation(s) across "
                    f"{len(action['run_ids'])} Run(s); {block_text}."
                )
                lines.extend(
                    f"  - `{item}`" for item in action["dependency_impact_refs"]
                )
    else:
        lines.append("- None.")
    lines.extend(["", "## Caveats", ""])
    lines.extend(f"- {item}" for item in digest["caveats"])
    return "\n".join(lines) + "\n"


def write_digest(root: Path, digest: dict[str, Any]) -> tuple[Path, Path]:
    base = root / "reviews" / "digests" / digest["week"]
    json_path = base.with_suffix(".json")
    markdown_path = base.with_suffix(".md")
    atomic_write_json(json_path, digest)
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    markdown_path.write_text(render_markdown(digest), encoding="utf-8")
    return json_path, markdown_path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--week", required=True)
    parser.add_argument("--run-id", action="append")
    parser.add_argument("--generated-at")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    digest = build_digest(
        args.root,
        week=args.week,
        run_ids=args.run_id,
        generated_at=args.generated_at,
    )
    outputs = write_digest(args.root, digest)
    print(json.dumps({"outputs": [str(path) for path in outputs], "summary": digest["summary"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
