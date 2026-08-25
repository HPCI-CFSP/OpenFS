#!/usr/bin/env python3
"""Generate a review brief and follow-up agenda from Center Profiles."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json


ROOT = Path(__file__).resolve().parents[1]
PROFILE_FIELDS = (
    "users",
    "priority_domains",
    "current_system",
    "refresh_window",
    "power",
    "facility",
    "software",
    "operations",
    "migration",
    "data_connectivity",
)


def _optional(root: Path, relative: str) -> dict[str, Any]:
    path = root / relative
    return read_json(path) if path.is_file() else {}


def _evidence_sources(root: Path, run_id: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "proposals" / "evidence" / run_id).glob("*.json")):
        bundle = read_json(path)
        source = read_json(root / bundle["source_result_ref"])["source_receipt"]
        source_view = {
            "source_id": source["source_id"],
            "title": source["title"],
            "publisher": source["publisher"],
            "canonical_url": source["canonical_url"],
            "source_class": source["source_class"],
            "primary_source": source["primary_source"],
        }
        for item in bundle.get("evidence_candidates", []):
            result[item["evidence_id"]] = source_view
    return result


def build_brief(
    root: Path, *, run_id: str, generated_at: str | None = None
) -> dict[str, Any]:
    manifest = read_json(root / "runs" / run_id / "manifest.json")
    coverage = _optional(root, f"runs/{run_id}/coverage.json")
    profile_coverage = _optional(
        root, f"runs/{run_id}/center-profile-coverage.json"
    )
    evidence_sources = _evidence_sources(root, run_id)
    centers = []
    gap_centers: dict[str, list[str]] = {field: [] for field in PROFILE_FIELDS}
    status_counts = {
        field: {"verified": 0, "partial": 0, "unknown": 0, "not-applicable": 0}
        for field in PROFILE_FIELDS
    }
    source_index: dict[str, dict[str, Any]] = {}
    transition_signals = []
    for path in sorted(
        (root / "proposals" / "center-profiles" / run_id).glob("*.json")
    ):
        profile = read_json(path)
        fields = {}
        missing_or_partial = []
        for field in PROFILE_FIELDS:
            value = profile[field]
            status = value["status"]
            status_counts[field][status] += 1
            fields[field] = {
                "status": status,
                "summary": value["summary"],
                "as_of": value["as_of"],
                "evidence_refs": value["evidence_refs"],
            }
            if status in {"partial", "unknown"}:
                gap_centers[field].append(profile["center_id"])
                missing_or_partial.append(field)
            for evidence_id in value["evidence_refs"]:
                source = evidence_sources.get(evidence_id)
                if source:
                    source_index[source["source_id"]] = source
        if profile["refresh_window"]["status"] in {"verified", "partial"}:
            transition_signals.append(
                {
                    "center_id": profile["center_id"],
                    "field": "refresh_window",
                    "status": profile["refresh_window"]["status"],
                    "summary": profile["refresh_window"]["summary"],
                    "evidence_refs": profile["refresh_window"]["evidence_refs"],
                }
            )
        if profile["current_system"]["status"] == "partial":
            transition_signals.append(
                {
                    "center_id": profile["center_id"],
                    "field": "current_system",
                    "status": "partial",
                    "summary": profile["current_system"]["summary"],
                    "evidence_refs": profile["current_system"]["evidence_refs"],
                }
            )
        centers.append(
            {
                "center_id": profile["center_id"],
                "name_ja": profile["name_ja"],
                "name_en": profile["name_en"],
                "proposal_id": profile.get("proposal_id"),
                "proposal_status": profile["profile_status"],
                "evidence_as_of": profile["evidence_as_of"],
                "evidence_count": len(profile["evidence_refs"]),
                "missing_or_partial_fields": missing_or_partial,
                "fields": fields,
            }
        )
    followups = [
        {
            "field": field,
            "affected_center_count": len(center_ids),
            "center_ids": sorted(center_ids),
            "research_instruction": (
                f"Find current official primary evidence for {field} for each listed "
                "center; retain unknown when no public evidence is found."
            ),
        }
        for field, center_ids in gap_centers.items()
        if center_ids
    ]
    followups.sort(key=lambda item: (-item["affected_center_count"], item["field"]))
    return {
        "schema_version": "0.1.0",
        "brief_id": f"CENTER-BRIEF-{run_id}",
        "run_id": run_id,
        "generated_at": generated_at or isoformat(),
        "publication_status": "internal-review-only",
        "run_status": manifest["status"],
        "web_coverage_status": coverage.get("coverage_status", "not-evaluated"),
        "profile_coverage_status": profile_coverage.get(
            "profile_coverage_status", "not-evaluated"
        ),
        "consensus_readiness": manifest.get("metrics", {}).get(
            "consensus_readiness", "not-evaluated"
        ),
        "summary": {
            "center_count": len(centers),
            "source_count": len(source_index),
            "accepted_current_count": profile_coverage.get("observed", {}).get(
                "accepted_current_count", 0
            ),
            "field_status_counts": status_counts,
        },
        "transition_signals": transition_signals,
        "priority_followups": followups,
        "centers": centers,
        "sources": sorted(source_index.values(), key=lambda item: item["source_id"]),
        "caveats": [
            "Center Profiles are proposals until independent review and Consensus Gate acceptance.",
            "Unknown and partial fields are research backlog, not negative findings about a center.",
            "This brief is generated from repository Evidence and is not itself a primary source.",
            "Publication requires a separate human publication Directive.",
        ],
    }


def render_markdown(brief: dict[str, Any]) -> str:
    summary = brief["summary"]
    lines = [
        f"# HPCI Center Research Brief: {brief['run_id']}",
        "",
        f"Generated: `{brief['generated_at']}`",
        "",
        f"- Web coverage: **{brief['web_coverage_status']}**",
        f"- Center profile coverage: **{brief['profile_coverage_status']}**",
        f"- Consensus capacity: **{brief['consensus_readiness']}**",
        f"- Centers profiled: **{summary['center_count']}**",
        f"- Unique sources used: **{summary['source_count']}**",
        f"- Accepted current profiles: **{summary['accepted_current_count']}**",
        "",
        "## Cross-center field coverage",
        "",
        "| Field | Verified | Partial | Unknown | N/A |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for field, counts in summary["field_status_counts"].items():
        lines.append(
            f"| `{field}` | {counts['verified']} | {counts['partial']} | "
            f"{counts['unknown']} | {counts['not-applicable']} |"
        )
    lines.extend(["", "## Time-sensitive signals", ""])
    if brief["transition_signals"]:
        for item in brief["transition_signals"]:
            lines.append(
                f"- **{item['center_id']}** `{item['field']}` ({item['status']}): "
                f"{item['summary']}"
            )
    else:
        lines.append("- No evidenced transition signal was produced.")
    lines.extend(["", "## Priority follow-up research", ""])
    for item in brief["priority_followups"]:
        lines.append(
            f"- **`{item['field']}` ({item['affected_center_count']} centers):** "
            + ", ".join(item["center_ids"])
        )
    lines.extend(["", "## Center profiles", ""])
    for center in brief["centers"]:
        current = center["fields"]["current_system"]
        refresh = center["fields"]["refresh_window"]
        lines.extend(
            [
                f"### {center['name_ja']} (`{center['center_id']}`)",
                "",
                f"- Current system ({current['status']}): {current['summary']}",
                f"- Refresh ({refresh['status']}): {refresh['summary']}",
                "- Follow-up: "
                + (", ".join(f"`{field}`" for field in center["missing_or_partial_fields"]) or "none"),
                "",
            ]
        )
    lines.extend(["## Sources", ""])
    for source in brief["sources"]:
        lines.append(
            f"- [{source['title']}]({source['canonical_url']}) "
            f"({source['publisher']}, `{source['source_class']}`)"
        )
    lines.extend(["", "## Caveats", ""])
    lines.extend(f"- {item}" for item in brief["caveats"])
    return "\n".join(lines) + "\n"


def write_brief(root: Path, brief: dict[str, Any]) -> tuple[Path, Path]:
    base = root / "reviews" / "briefs" / f"{brief['run_id']}-center-research"
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
