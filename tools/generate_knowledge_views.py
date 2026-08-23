#!/usr/bin/env python3
"""Generate deterministic indexes and TBD.md from canonical knowledge only."""

from __future__ import annotations

import argparse
import json
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


def build_index(root: Path) -> dict[str, Any]:
    entries: list[dict[str, Any]] = []
    for path in sorted((root / "knowledge" / "claims").glob("CLM-*.json")):
        record = read_json(path)
        claim = record["claim"]
        if claim.get("status") != "accepted":
            raise ValueError(f"non-accepted Claim in canonical path: {path}")
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
    as_of = max((item["promoted_at"] for item in entries), default=None)
    return {
        "schema_version": "0.1.0",
        "as_of": as_of,
        "claim_count": len(entries),
        "knowledge_digest": stable_digest(entries),
        "claims": entries,
        "caveat": (
            "This is a generated view of accepted canonical Claims. It excludes "
            "Proposals, provisional Decisions, and Recommendation-Gate outputs."
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
        f"- Accepted Claim count: **{index['claim_count']}**",
        f"- Knowledge digest: `{index['knowledge_digest']}`",
        "",
        "## Accepted Claims",
        "",
    ]
    if not index["claims"]:
        lines.append("- No canonical Claims have been promoted.")
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
                "knowledge_digest": index["knowledge_digest"],
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
