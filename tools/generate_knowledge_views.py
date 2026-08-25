#!/usr/bin/env python3
"""Generate deterministic indexes and TBD.md from canonical knowledge only."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, read_json, stable_digest


ROOT = Path(__file__).resolve().parents[1]
KIND_LABELS = {
    "observed_fact": "Observed facts",
    "reported_claim": "Reported claims",
    "forecast": "Forecasts",
    "interpretation": "Interpretations",
    "recommendation": "Recommendations",
}


def _timestamp(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def build_index(root: Path) -> dict[str, Any]:
    status_by_claim: dict[str, dict[str, Any]] = {}
    for path in sorted((root / "knowledge" / "claim-status").glob("CSE-*.json")):
        event = read_json(path)
        claim_id = event["claim_id"]
        if claim_id in status_by_claim:
            raise ValueError(f"multiple terminal status events for canonical Claim: {claim_id}")
        status_by_claim[claim_id] = {
            "claim_id": claim_id,
            "action": event["action"],
            "reason": event["reason"],
            "replacement_claim_id": event.get("replacement_claim_id"),
            "status_event_ref": str(path.relative_to(root)),
            "directive_id": event["directive_id"],
            "recorded_at": event["recorded_at"],
            "event_digest": event["event_digest"],
        }
    entries: list[dict[str, Any]] = []
    canonical_ids: set[str] = set()
    for path in sorted((root / "knowledge" / "claims").glob("CLM-*.json")):
        record = read_json(path)
        claim = record["claim"]
        if claim.get("status") != "accepted":
            raise ValueError(f"non-accepted Claim in canonical path: {path}")
        canonical_ids.add(claim["claim_id"])
        if claim["claim_id"] in status_by_claim:
            continue
        entries.append(
            {
                "claim_id": claim["claim_id"],
                "claim_kind": claim["claim_kind"],
                "statement": claim["statement"],
                "temporal_scope": claim["temporal_scope"],
                "conditions": claim.get("conditions", []),
                "evidence_count": len(claim["evidence_ids"]),
                "source_lineage_count": len(claim["source_lineage_ids"]),
                "canonical_ref": str(path.relative_to(root)),
                "proposal_ref": record["provenance"]["proposal_ref"],
                "decision_ref": record["provenance"]["decision_ref"],
                "promoted_at": record["promoted_at"],
                "promotion_digest": record["promotion_digest"],
            }
        )
    entries.sort(key=lambda item: item["claim_id"])
    unknown_status_ids = set(status_by_claim) - canonical_ids
    if unknown_status_ids:
        raise ValueError(
            "status event refers to missing canonical Claim: "
            + ", ".join(sorted(unknown_status_ids))
        )
    inactive = sorted(status_by_claim.values(), key=lambda item: item["claim_id"])
    timestamps = [item["promoted_at"] for item in entries]
    timestamps.extend(item["recorded_at"] for item in inactive)
    as_of = max(timestamps, key=_timestamp) if timestamps else None
    return {
        "schema_version": "0.1.0",
        "as_of": as_of,
        "claim_count": len(entries),
        "canonical_claim_count": len(canonical_ids),
        "status_event_count": len(inactive),
        "knowledge_digest": stable_digest({"active": entries, "inactive": inactive}),
        "claims": entries,
        "inactive_claims": inactive,
        "caveat": (
            "This is a generated view of active accepted canonical Claims. It excludes "
            "Proposals, provisional Decisions, Recommendation-Gate outputs, and Claims "
            "with append-only withdrawn or superseded status events."
        ),
    }


def _one_line(value: str) -> str:
    return " ".join(value.split())


def render_tbd(index: dict[str, Any]) -> str:
    lines = [
        "# OpenFS Integrated Draft",
        "",
        "This file is generated from accepted canonical records. It is not a primary record.",
        "",
        f"- As of: `{index['as_of'] or 'no-promotions'}`",
        f"- Active accepted Claim count: **{index['claim_count']}**",
        f"- Canonical Claim count: **{index['canonical_claim_count']}**",
        f"- Withdrawn or superseded Claim count: **{index['status_event_count']}**",
        f"- Knowledge digest: `{index['knowledge_digest']}`",
        "",
        "## Active Accepted Claims",
        "",
    ]
    if not index["claims"]:
        lines.append("- No canonical Claims are currently active.")
    else:
        for kind in KIND_LABELS:
            claims = [item for item in index["claims"] if item["claim_kind"] == kind]
            if not claims:
                continue
            lines.extend([f"### {KIND_LABELS[kind]}", ""])
            for item in claims:
                lines.append(
                    f"- **{item['claim_id']}** ({_one_line(item['temporal_scope'])}): "
                    f"{_one_line(item['statement'])}"
                )
                lines.append(
                    f"  Evidence: {item['evidence_count']}; Source lineages: "
                    f"{item['source_lineage_count']}; Record: `{item['canonical_ref']}`"
                )
            lines.append("")
    lines.extend(["", "## Withdrawn Or Superseded Claims", ""])
    if not index["inactive_claims"]:
        lines.append("- No canonical Claim status events have been recorded.")
    else:
        for item in index["inactive_claims"]:
            replacement = (
                f"; replacement: **{item['replacement_claim_id']}**"
                if item.get("replacement_claim_id")
                else ""
            )
            lines.append(
                f"- **{item['claim_id']}**: `{item['action']}`{replacement}; "
                f"Directive: `{item['directive_id']}`; reason: {_one_line(item['reason'])}"
            )
    lines.extend(
        [
            "",
            "## Caveat",
            "",
            f"- {index['caveat']}",
            "- HPCI roadmap recommendations require their separate human-accountable gate and are not inferred from this list.",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def generate(root: Path) -> tuple[Path, Path, dict[str, Any]]:
    index = build_index(root)
    index_path = root / "knowledge" / "claims" / "index.json"
    tbd_path = root / "TBD.md"
    atomic_write_json(index_path, index)
    tbd_path.write_text(render_tbd(index), encoding="utf-8")
    return index_path, tbd_path, index


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    index_path, tbd_path, index = generate(args.root)
    print(
        json.dumps(
            {
                "outputs": [str(index_path), str(tbd_path)],
                "claim_count": index["claim_count"],
                "canonical_claim_count": index["canonical_claim_count"],
                "status_event_count": index["status_event_count"],
                "knowledge_digest": index["knowledge_digest"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
