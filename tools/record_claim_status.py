#!/usr/bin/env python3
"""Record a human-authorized append-only canonical Claim status event."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json, stable_digest


ROOT = Path(__file__).resolve().parents[1]
ALLOWED_DIRECTIVE_STATUSES = {"approved", "completed"}
CLAIM_ID_PATTERN = re.compile(r"^CLM-[0-9]{6}$")
DIRECTIVE_ID_PATTERN = re.compile(r"^DIR-[0-9]{6}$")


def _repository_ref(ref: str, prefix: str) -> PurePosixPath:
    relative = PurePosixPath(ref)
    if relative.is_absolute() or ".." in relative.parts or not ref.startswith(prefix):
        raise ValueError(f"reference must be repository-relative under {prefix}")
    return relative


def _status_events(root: Path, claim_id: str) -> list[Path]:
    matches = []
    for path in sorted((root / "knowledge" / "claim-status").glob("CSE-*.json")):
        if read_json(path).get("claim_id") == claim_id:
            matches.append(path)
    return matches


def prepare_event(
    root: Path,
    *,
    claim_id: str,
    directive_ref: str,
    recorded_by: str,
    recorded_at: str,
    allow_existing: bool = False,
) -> dict[str, Any]:
    if not recorded_by.strip():
        raise ValueError("recorded_by is required")
    if not CLAIM_ID_PATTERN.fullmatch(claim_id):
        raise ValueError("claim_id has an invalid format")
    _repository_ref(directive_ref, "reviews/directives/")
    expected_directive_ref = f"reviews/directives/{Path(directive_ref).stem}.json"
    if directive_ref != expected_directive_ref:
        raise ValueError("Directive reference must use its canonical path")

    canonical_ref = f"knowledge/claims/{claim_id}.json"
    canonical_path = root / canonical_ref
    if not canonical_path.is_file():
        raise ValueError(f"canonical Claim does not exist: {claim_id}")
    canonical = read_json(canonical_path)
    if (
        canonical.get("canonical_claim_id") != claim_id
        or canonical.get("claim", {}).get("claim_id") != claim_id
        or canonical.get("claim", {}).get("status") != "accepted"
    ):
        raise ValueError("canonical Claim identity or acceptance status differs")
    if _status_events(root, claim_id) and not allow_existing:
        raise RuntimeError("canonical Claim already has a terminal status event")

    directive_path = root / directive_ref
    if not directive_path.is_file():
        raise ValueError("canonical-status Directive does not exist")
    directive = read_json(directive_path)
    directive_id = directive.get("directive_id")
    if not isinstance(directive_id, str) or not DIRECTIVE_ID_PATTERN.fullmatch(
        directive_id
    ):
        raise ValueError("Directive ID has an invalid format")
    if directive_ref != f"reviews/directives/{directive_id}.json":
        raise ValueError("Directive identity differs from its path")
    if directive.get("directive_type") != "canonical-status":
        raise ValueError("Directive does not authorize a canonical status change")
    if directive.get("status") not in ALLOWED_DIRECTIVE_STATUSES:
        raise ValueError("canonical-status Directive is not approved")
    if directive.get("public_information_confirmed") is not True:
        raise ValueError("canonical-status Directive lacks public-information confirmation")
    if directive.get("claim_targets") != [claim_id]:
        raise ValueError("canonical-status Directive must name exactly this Claim")
    if not directive.get("submitted_by") or not directive.get("submitted_at"):
        raise ValueError("canonical-status Directive lacks human accountability")

    action = directive.get("canonical_status_action")
    if action not in {"withdrawn", "superseded"}:
        raise ValueError("canonical-status Directive has an invalid action")
    reason = directive.get("canonical_status_reason", "").strip()
    if not reason:
        raise ValueError("canonical-status Directive requires a reason")
    replacement_claim_id = directive.get("replacement_claim_id")
    if action == "withdrawn" and replacement_claim_id:
        raise ValueError("withdrawn action cannot name a replacement Claim")
    if action == "superseded":
        if (
            not isinstance(replacement_claim_id, str)
            or not CLAIM_ID_PATTERN.fullmatch(replacement_claim_id)
            or replacement_claim_id == claim_id
        ):
            raise ValueError("superseded action requires a different replacement Claim")
        replacement_path = root / "knowledge" / "claims" / f"{replacement_claim_id}.json"
        if not replacement_path.is_file():
            raise ValueError("replacement canonical Claim does not exist")
        replacement = read_json(replacement_path)
        if replacement.get("claim", {}).get("status") != "accepted":
            raise ValueError("replacement canonical Claim is not accepted")
        if _status_events(root, replacement_claim_id):
            raise ValueError("replacement canonical Claim is not active")

    core: dict[str, Any] = {
        "schema_version": "0.1.0",
        "claim_id": claim_id,
        "action": action,
        "reason": reason,
        "canonical_claim_ref": canonical_ref,
        "canonical_claim_digest": stable_digest(canonical),
        "directive_id": directive_id,
        "directive_ref": directive_ref,
        "directive_digest": stable_digest(directive),
        "recorded_at": recorded_at,
        "recorded_by": recorded_by.strip(),
    }
    if replacement_claim_id:
        core["replacement_claim_id"] = replacement_claim_id
    event_id = "CSE-" + stable_digest(core)[:12].upper()
    event = {"event_id": event_id, **core}
    event["event_digest"] = stable_digest(event)
    return event


def record(
    root: Path,
    *,
    claim_id: str,
    directive_ref: str,
    recorded_by: str,
    recorded_at: str | None = None,
) -> tuple[Path, dict[str, Any]]:
    existing_paths = _status_events(root, claim_id)
    if existing_paths:
        if len(existing_paths) != 1:
            raise RuntimeError("canonical Claim has multiple terminal status events")
        existing = read_json(existing_paths[0])
        if existing.get("directive_ref") != directive_ref:
            raise RuntimeError("canonical Claim already has a different status event")
        expected = prepare_event(
            root,
            claim_id=claim_id,
            directive_ref=directive_ref,
            recorded_by=existing.get("recorded_by", ""),
            recorded_at=existing.get("recorded_at", ""),
            allow_existing=True,
        )
        if existing != expected:
            raise RuntimeError("existing canonical Claim status event failed revalidation")
        from generate_knowledge_views import generate

        generate(root)
        return existing_paths[0], existing
    event = prepare_event(
        root,
        claim_id=claim_id,
        directive_ref=directive_ref,
        recorded_by=recorded_by,
        recorded_at=recorded_at or isoformat(),
    )
    output = root / "knowledge" / "claim-status" / f"{event['event_id']}.json"
    if output.is_file():
        if read_json(output) != event:
            raise RuntimeError("Claim status event ID collision")
    else:
        atomic_write_json(output, event)
    from generate_knowledge_views import generate

    generate(root)
    return output, event


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--claim-id", required=True)
    parser.add_argument("--directive-ref", required=True)
    parser.add_argument("--recorded-by", required=True)
    parser.add_argument("--recorded-at")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    output, event = record(
        args.root,
        claim_id=args.claim_id,
        directive_ref=args.directive_ref,
        recorded_by=args.recorded_by,
        recorded_at=args.recorded_at,
    )
    print(json.dumps({"output": str(output), "event_id": event["event_id"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
