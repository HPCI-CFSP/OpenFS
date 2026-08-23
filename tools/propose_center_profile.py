#!/usr/bin/env python3
"""Create a provisional, field-evidenced HPCI center profile."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import (
    atomic_write_json,
    isoformat,
    read_json,
    run_snapshot_path,
    stable_digest,
)


ROOT = Path(__file__).resolve().parents[1]
EVIDENCED_STATES = {"verified", "partial", "not-applicable"}
ALL_STATES = EVIDENCED_STATES | {"unknown"}


def _synthesis_agent(agent_id: str, registry: dict[str, Any]) -> None:
    matches = [
        item for item in registry.get("agents", []) if item.get("agent_id") == agent_id
    ]
    if len(matches) != 1 or matches[0].get("role") != "synthesis":
        raise ValueError(f"agent is not uniquely registered for synthesis: {agent_id}")
    if (
        matches[0].get("provider") == "unconfigured"
        or matches[0].get("model_family") == "unconfigured"
    ):
        raise ValueError(f"agent identity is unconfigured: {agent_id}")


def propose(
    bundles: list[dict[str, Any]],
    *,
    bundle_refs: list[str],
    center_id: str,
    draft: dict[str, Any],
    run_id: str,
    agent_id: str,
    agent_registry: dict[str, Any],
    center_registry: dict[str, Any],
    created_at: str | None = None,
) -> dict[str, Any]:
    _synthesis_agent(agent_id, agent_registry)
    if len(bundles) != len(bundle_refs) or not bundles:
        raise ValueError("Evidence bundles and references must be non-empty and aligned")
    centers = {
        center["center_id"]: center for center in center_registry.get("centers", [])
    }
    if center_id not in centers:
        raise ValueError(f"center is not present in the pinned registry: {center_id}")
    center = centers[center_id]
    required_fields = center.get(
        "profile_fields", center_registry.get("default_profile_fields", [])
    )
    fields = draft.get("fields", {})
    if set(fields) != set(required_fields):
        raise ValueError("draft fields must exactly match the registered profile fields")
    allowed_top_level = {"evidence_as_of", "fields", "unknowns"}
    if set(draft) - allowed_top_level:
        raise ValueError(f"draft contains unsupported fields: {sorted(set(draft) - allowed_top_level)}")

    evidence: dict[str, dict[str, Any]] = {}
    origin_group_ids: set[str] = set()
    has_primary_source = False
    for bundle in bundles:
        if bundle.get("object_type") != "evidence" or bundle.get("run_id") != run_id:
            raise ValueError("all inputs must be Evidence bundles from this Run")
        origin_group_ids.update(bundle.get("origin_group_ids", []))
        has_primary_source = has_primary_source or bundle.get("has_primary_source") is True
        for item in bundle.get("evidence_candidates", []):
            evidence[item["evidence_id"]] = item

    normalized_fields: dict[str, dict[str, Any]] = {}
    used_evidence: set[str] = set()
    unknowns: set[str] = set(draft.get("unknowns", []))
    for field in required_fields:
        value = fields[field]
        if set(value) != {"status", "summary", "as_of", "evidence_refs"}:
            raise ValueError(f"profile field has an invalid shape: {field}")
        status = value["status"]
        refs = value["evidence_refs"]
        if status not in ALL_STATES:
            raise ValueError(f"unsupported profile field status for {field}: {status}")
        if len(refs) != len(set(refs)):
            raise ValueError(f"profile field has duplicate Evidence references: {field}")
        unknown_refs = set(refs) - set(evidence)
        if unknown_refs:
            raise ValueError(
                f"profile field references Evidence outside assigned bundles: {field}"
            )
        if status == "unknown":
            if refs or value["as_of"] is not None:
                raise ValueError(f"unknown profile field cannot claim Evidence or date: {field}")
            unknowns.add(field)
        elif not refs or not value["summary"].strip() or not value["as_of"]:
            raise ValueError(
                f"evidenced profile field requires summary, date, and Evidence: {field}"
            )
        used_evidence.update(refs)
        normalized_fields[field] = {
            "status": status,
            "summary": value["summary"].strip(),
            "as_of": value["as_of"],
            "evidence_refs": sorted(refs),
        }
    if not used_evidence:
        raise ValueError("a Center Profile requires at least one assigned Evidence record")
    timestamp = created_at or isoformat()
    identity = {
        "run_id": run_id,
        "center_id": center_id,
        "evidence_refs": sorted(used_evidence),
        "fields": normalized_fields,
    }
    proposal_number = int(stable_digest(identity)[:12], 16) % 1_000_000
    profile = {
        "schema_version": "0.1.0",
        "proposal_contract_version": "0.2.0",
        "proposal_id": f"PRP-CTR-{proposal_number:06d}",
        "object_type": "center_profile",
        "run_id": run_id,
        "center_id": center_id,
        "name_ja": center["name_ja"],
        "name_en": center["name_en"],
        "profile_status": "provisional",
        "evidence_as_of": draft["evidence_as_of"],
        "evidence_refs": sorted(used_evidence),
        "origin_group_ids": sorted(origin_group_ids),
        "has_primary_source": has_primary_source,
        **normalized_fields,
        "unknowns": sorted(unknowns),
        "created_by_agent_id": agent_id,
        "created_at": timestamp,
    }
    return profile


def validate_assignment(
    work_item: dict[str, Any],
    *,
    center_id: str,
    bundle_refs: list[str],
    agent_id: str,
    output_ref: str,
) -> None:
    if work_item.get("kind") != "center-profile-synthesis":
        raise ValueError("Work Item is not assigned to Center Profile synthesis")
    lease = work_item.get("lease", {})
    if work_item.get("status") != "leased" or lease.get("agent_id") != agent_id:
        raise RuntimeError("Center Profile synthesis requires the current Work Item lease")
    payload = work_item.get("payload", {})
    if center_id != payload.get("center_id"):
        raise ValueError("Center differs from the assigned Work Item")
    if sorted(bundle_refs) != sorted(payload.get("evidence_bundle_refs", [])):
        raise ValueError("Evidence bundle references differ from the assigned Work Item")
    if output_ref not in work_item.get("output_paths", []):
        raise ValueError("Center Profile output is outside the Work Item's declared paths")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--draft", required=True, type=Path)
    parser.add_argument("--evidence-bundle-ref", action="append", required=True)
    parser.add_argument("--center-id", required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--work-item-id", required=True)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    work_item = read_json(
        args.root / "queue" / args.run_id / f"{args.work_item_id}.json"
    )
    output_path = args.output if args.output.is_absolute() else args.root / args.output
    output_ref = str(output_path.relative_to(args.root))
    validate_assignment(
        work_item,
        center_id=args.center_id,
        bundle_refs=args.evidence_bundle_ref,
        agent_id=args.agent_id,
        output_ref=output_ref,
    )
    manifest = read_json(args.root / "runs" / args.run_id / "manifest.json")
    monitor_ref = next(
        ref for ref in manifest["policy_hashes"] if ref.startswith("config/monitors/")
    )
    monitor = read_json(run_snapshot_path(args.root, args.run_id, monitor_ref))
    profile = propose(
        [read_json(args.root / ref) for ref in args.evidence_bundle_ref],
        bundle_refs=args.evidence_bundle_ref,
        center_id=args.center_id,
        draft=read_json(args.draft),
        run_id=args.run_id,
        agent_id=args.agent_id,
        agent_registry=read_json(
            run_snapshot_path(args.root, args.run_id, "config/agent-registry.json")
        ),
        center_registry=read_json(
            run_snapshot_path(
                args.root, args.run_id, monitor["subject_registry_ref"]
            )
        ),
        created_at=work_item.get("lease", {}).get("acquired_at")
        or work_item.get("updated_at"),
    )
    if output_path.exists():
        if read_json(output_path) != profile:
            raise RuntimeError("Center Profile already exists with different content")
    else:
        atomic_write_json(output_path, profile)
    print(json.dumps({"center_id": args.center_id, "output": output_ref}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
