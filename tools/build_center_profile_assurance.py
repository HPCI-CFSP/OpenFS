#!/usr/bin/env python3
"""Build a public, aggregate assurance view of the latest pinned Center Run."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RUN_ID = "RUN-OFS003-PILOT-005"
DEFAULT_OUTPUT = (
    ROOT / "knowledge" / "public" / "audits" / "center-profile-assurance.json"
)
COMPLETE_STATES = {"verified", "not-applicable"}
GAP_FIELDS = {
    "GAP-BLUE-001": (
        "users",
        "priority_domains",
        "current_system",
        "refresh_window",
        "software",
        "operations",
        "migration",
        "data_connectivity",
    ),
    "GAP-BLUE-003": (
        "refresh_window",
        "power",
        "facility",
        "budget",
        "procurement",
        "migration",
    ),
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build(root: Path, *, run_id: str = DEFAULT_RUN_ID) -> dict[str, Any]:
    registry = load_json(root / "config" / "hpci-center-registry.json")
    coverage = load_json(root / "runs" / run_id / "center-profile-coverage.json")
    effectiveness = load_json(root / "runs" / run_id / "followup-effectiveness.json")
    fields = registry["default_profile_fields"]
    profiles = {
        profile["center_id"]: profile
        for path in sorted(
            (root / "proposals" / "center-profiles" / run_id).glob("*.json")
        )
        for profile in [load_json(path)]
    }
    coverage_by_center = {
        item["center_id"]: item for item in coverage["observed"]["profiles"]
    }
    centers = []
    all_counts: Counter[str] = Counter()
    field_counts = {field: Counter() for field in fields}
    for center in registry["centers"]:
        center_id = center["center_id"]
        profile = profiles.get(center_id)
        coverage_item = coverage_by_center.get(center_id, {})
        states = []
        for field in fields:
            if profile is None or field not in profile:
                status = "not-collected"
            else:
                status = profile[field].get("status", "unknown")
            states.append({"field": field, "status": status})
            field_counts[field][status] += 1
            all_counts[status] += 1
        centers.append(
            {
                "center_id": center_id,
                "name_ja": center["name_ja"],
                "name_en": center["name_en"],
                "official_url": center["official_url"],
                "profile_status": coverage_item.get("profile_status", "missing"),
                "decision_outcome": coverage_item.get("decision_outcome", "missing"),
                "evidence_as_of": profile.get("evidence_as_of") if profile else None,
                "field_states": states,
                "field_evidence_complete": coverage_item.get(
                    "field_evidence_complete", False
                ),
                "accepted_current": coverage_item.get("accepted_current", False),
            }
        )

    gap_status = []
    for gap_id, gap_fields in GAP_FIELDS.items():
        affected = []
        incomplete_slots = 0
        for center in centers:
            states = {item["field"]: item["status"] for item in center["field_states"]}
            incomplete = [field for field in gap_fields if states[field] not in COMPLETE_STATES]
            incomplete_slots += len(incomplete)
            if incomplete or not center["accepted_current"]:
                affected.append(center["center_id"])
        gap_status.append(
            {
                "gap_id": gap_id,
                "required_fields": list(gap_fields),
                "affected_center_count": len(affected),
                "affected_center_ids": affected,
                "incomplete_field_slot_count": incomplete_slots,
                "status": "open" if affected else "resolved",
            }
        )

    return {
        "schema_version": "0.1.0",
        "export_id": "CENTER-PROFILE-ASSURANCE-001",
        "status": "published",
        "as_of": registry["as_of"],
        "generated_at": coverage["evaluated_at"],
        "source_run_id": run_id,
        "registry_id": registry["registry_id"],
        "profile_contract_target": "0.3.0",
        "consensus_status": "incomplete",
        "method_ja": "最新の固定済みCenter Runを、現行12項目Profile契約に投影した。旧契約に存在しない項目は未収集とし、推測で補完しない。検索実行、項目証拠、Consensus受理を別々に集計する。",
        "method_en": "Projects the latest pinned Center Run onto the current twelve-field profile contract. Fields absent from the older contract are marked not collected and are never inferred. Search execution, field evidence, and Consensus acceptance are counted separately.",
        "caveat_ja": "これは公開情報による単一モデルの暫定監査である。未確認は各機関に制約が存在しないことを意味せず、全15 Profileは未受理である。個別の暫定記述は公開投影していない。",
        "caveat_en": "This is a provisional single-model audit of public information. Unknown does not mean that a center has no constraint; all fifteen profiles remain unaccepted. Individual provisional narrative fields are not projected publicly.",
        "summary": {
            "center_count": len(registry["centers"]),
            "profile_count": len(profiles),
            "accepted_current_count": coverage["observed"]["accepted_current_count"],
            "field_evidence_complete_count": coverage["observed"][
                "field_evidence_complete_count"
            ],
            "field_slot_count": len(registry["centers"]) * len(fields),
            "verified": all_counts["verified"],
            "partial": all_counts["partial"],
            "unknown": all_counts["unknown"],
            "not_applicable": all_counts["not-applicable"],
            "not_collected": all_counts["not-collected"],
            "followup_query_count": effectiveness["query_count"],
            "effective_followup_query_count": effectiveness["effective_query_count"],
            "ineffective_followup_query_count": effectiveness[
                "ineffective_query_count"
            ],
        },
        "field_summary": [
            {
                "field": field,
                "verified": counts["verified"],
                "partial": counts["partial"],
                "unknown": counts["unknown"],
                "not_applicable": counts["not-applicable"],
                "not_collected": counts["not-collected"],
            }
            for field, counts in field_counts.items()
        ],
        "gap_status": gap_status,
        "centers": centers,
        "publication": {
            "information_classification": "public",
            "publication_approved": True,
            "publication_decision_id": "PUBDEC-20260826-006",
            "human_approval_directive_id": "DIR-900006",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--run-id", default=DEFAULT_RUN_ID)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = build(args.root, run_id=args.run_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(result["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
