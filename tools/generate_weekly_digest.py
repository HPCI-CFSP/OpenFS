#!/usr/bin/env python3
"""Generate an auditable weekly view of Runs, changes, gaps, and exceptions."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json


ROOT = Path(__file__).resolve().parents[1]


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _iso_week(value: datetime) -> str:
    year, week, _ = value.isocalendar()
    return f"{year:04d}-W{week:02d}"


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
    change_totals = {
        name: 0 for name in ("new", "changed", "unchanged", "unavailable", "not-observed")
    }

    for manifest in manifests:
        run_id = manifest["run_id"]
        coverage_path = root / "runs" / run_id / "coverage.json"
        coverage = read_json(coverage_path) if coverage_path.is_file() else None
        change_ref = manifest.get("change_report_ref")
        changes = read_json(root / change_ref) if change_ref else None
        if changes:
            for name, count in changes["summary"].items():
                change_totals[name] = change_totals.get(name, 0) + count
        readiness_ref = manifest.get("consensus_readiness_ref")
        readiness = read_json(root / readiness_ref) if readiness_ref else None
        run_summaries.append(
            {
                "run_id": run_id,
                "task_id": manifest["task_id"],
                "monitor_id": manifest["monitor_id"],
                "status": manifest["status"],
                "research_status": manifest["research_status"],
                "coverage_status": coverage.get("coverage_status") if coverage else "not-evaluated",
                "consensus_readiness": readiness.get("status") if readiness else "not-evaluated",
                "consensus_outcomes": manifest.get("metrics", {}).get("consensus_outcomes", {}),
                "cost": manifest.get("cost", {"measurement_status": "unreported"}),
            }
        )
        if coverage:
            for category, values in coverage.get("gaps", {}).items():
                if values:
                    gaps.append({"run_id": run_id, "category": category, "values": values})
        for path in sorted((root / "decisions" / run_id).glob("*.json")):
            decision = read_json(path)
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
        monitor_ref = next(
            (
                source
                for source in manifest.get("policy_hashes", {})
                if source.startswith("config/monitors/")
            ),
            None,
        )
        maximum_days = None
        if monitor_ref:
            snapshot = manifest.get("configuration_snapshots", {}).get(
                monitor_ref, monitor_ref
            )
            maximum_days = read_json(root / snapshot).get("maximum_unchecked_days")
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
        for path in sorted((root / "reviews" / "exceptions" / run_id).glob("*.json")):
            exception = read_json(path)
            if exception.get("status") == "open":
                exceptions.append(
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
    owner_actions = [
        {
            "action_id": f"ACTION-{item['exception_id']}",
            "kind": "resolve-exception",
            "run_id": item["run_id"],
            "exception_ref": item["exception_ref"],
        }
        for item in exceptions
        if item["requires_owner_action"]
    ]
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
        },
        "runs": run_summaries,
        "source_changes": change_totals,
        "coverage_gaps": gaps,
        "dissent": dissent,
        "stale_sources": stale,
        "failures": failures,
        "open_exceptions": exceptions,
        "pending_directives": pending_directives,
        "owner_actions": owner_actions,
        "caveats": [
            "This Digest is a generated operational view, not primary evidence.",
            "Unreported cost is unknown and must not be interpreted as zero.",
            "not-observed Sources are not inferred to be withdrawn or unavailable.",
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
        "| Run | Task / Monitor | Run status | Research | Coverage | Consensus capacity | Cost |",
        "|---|---|---|---|---|---|---|",
    ]
    for run in digest["runs"]:
        cost = run["cost"]
        amount = cost.get("reported_total_usd")
        cost_text = cost.get("measurement_status", "unreported")
        if amount is not None:
            cost_text += f" (${amount:.4f} reported)"
        lines.append(
            f"| `{run['run_id']}` | `{run['task_id']}` / `{run['monitor_id']}` | "
            f"{run['status']} | {run['research_status']} | {run['coverage_status']} | "
            f"{run['consensus_readiness']} | {cost_text} |"
        )
    if not digest["runs"]:
        lines.append("| None | - | - | - | - | - | - |")
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
            lines.append(
                f"- `{action['run_id']}`: resolve `{action['exception_ref']}`"
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
