#!/usr/bin/env python3
"""Project a bounded human-authorized update, never a Consensus promotion."""
from __future__ import annotations

import argparse
import copy
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

from openfs_runtime import stable_digest

ROOT = Path(__file__).resolve().parents[1]
BASELINE = "config/research-baseline.json"
SURFACE = "knowledge/public/topic-decision-support.json"


def read(root, ref):
    return json.loads((root / ref).read_text(encoding="utf-8"))


def profile_for(surface, topic_id):
    return next(p for p in surface["topic_profiles"] if p["topic_id"] == topic_id)


def validate_contract(root, bundle):
    from jsonschema import Draft202012Validator, FormatChecker
    from validate_json_schemas import schema_registry
    schemas, registry = schema_registry(root)
    Draft202012Validator(schemas["research-unit-update.schema.json"], registry=registry,
                         format_checker=FormatChecker()).validate(bundle)


def verify_pinned_input(root, bundle):
    commit = bundle["base_commit"]
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("base commit must be a full hash")
    def at_base(ref):
        return json.loads(subprocess.run(["git", "show", f"{commit}:{ref}"], cwd=root,
                          capture_output=True, text=True, check=True).stdout)
    baseline, surface = at_base(BASELINE), at_base(SURFACE)
    predecessors = bundle.get("predecessor_updates", [])
    seen = {bundle["update_id"]}
    for index, ref in enumerate(predecessors):
        if ref["update_id"] in seen:
            raise ValueError("cyclic or duplicate predecessor")
        seen.add(ref["update_id"])
        previous = read(root, f"proposals/research-unit-updates/{ref['update_id']}.json")
        if (stable_digest(previous) != ref["bundle_sha256"]
                or previous["base_commit"] != commit or previous["topic_id"] != bundle["topic_id"]
                or previous.get("predecessor_updates", []) != predecessors[:index]
                or datetime.fromisoformat(previous["created_at"]) > datetime.fromisoformat(bundle["created_at"])):
            raise ValueError("predecessor chain does not match pinned input")
        baseline, surface, _ = project(root, previous, baseline, surface)
    profile = profile_for(surface, bundle["topic_id"])
    if stable_digest(profile) != bundle["before_profile_sha256"]:
        raise ValueError("profile input does not match the pinned commit")
    topic = next(t for t in baseline["topics"] if t["topic_id"] == bundle["topic_id"])
    units = {u["unit_id"]: u for u in topic["research_units"]}
    for assignment in bundle["units"]:
        if stable_digest(units.get(assignment["unit_id"])) != assignment["before_sha256"]:
            raise ValueError("unit input does not match the pinned commit")


def project(root, bundle, baseline, surface):
    """Pure projection; all conflicts are checked before returning new documents."""
    validate_contract(root, bundle)
    verify_authorization(root, bundle)
    return project_authorized(bundle, baseline, surface)


def verify_authorization(root, bundle):
    directive = read(root, f"reviews/directives/{bundle['human_directive_id']}.json")
    if (directive.get("status") != "approved" or not directive.get("public_information_confirmed")
            or directive.get("directive_type") != "publication-approval"
            or bundle["update_id"] not in directive.get("publication_targets", [])
            or "TOPIC-DECISION-SUPPORT-001" not in directive.get("publication_targets", [])):
        raise ValueError("update lacks explicit human publication authorization")


def project_authorized(bundle, baseline, surface):
    bundle = copy.deepcopy(bundle)
    topic = next(t for t in baseline["topics"] if t["topic_id"] == bundle["topic_id"])
    if topic["status"] not in {"not-started", "partial"}:
        raise ValueError("retired or reviewed Topics cannot use provisional updates")
    profile = profile_for(surface, bundle["topic_id"])
    digest = stable_digest(bundle)
    prior = next((u for u in profile.get("research_updates", [])
                  if u["update_id"] == bundle["update_id"]), None)
    if prior:
        if prior["bundle_sha256"] != digest:
            raise ValueError("an applied update is immutable; create a new update")
        verify_applied(bundle, baseline, surface)
        return baseline, surface, False
    if stable_digest(profile) != bundle["before_profile_sha256"]:
        raise ValueError("stale profile: rebase and review the new input")
    units = {u["unit_id"]: u for u in topic["research_units"]}
    assignments = {u["unit_id"]: u for u in bundle["units"]}
    if len(assignments) != len(bundle["units"]) or set(assignments) - units.keys():
        raise ValueError("duplicate, missing, or wrongly owned unit")
    for uid, assignment in assignments.items():
        if stable_digest(units[uid]) != assignment["before_sha256"]:
            raise ValueError(f"stale research unit: {uid}")
    old_sections = {s["section_id"] for s in profile["sections"]}
    archived = set(profile.get("archived_section_ids", [])) | set(bundle["archive_section_ids"])
    if set(bundle["archive_section_ids"]) - old_sections:
        raise ValueError("cannot archive an unknown or foreign section")
    section_ids = [s["section_id"] for s in bundle["sections"]]
    item_ids = [i["item_id"] for s in bundle["sections"] for i in s["items"]]
    existing_sections = {s["section_id"] for p in surface["topic_profiles"] for s in p["sections"]}
    existing_items = {i["item_id"] for p in surface["topic_profiles"] for s in p["sections"] for i in s["items"]}
    if (len(set(section_ids)) != len(section_ids) or set(section_ids) & existing_sections
            or len(set(item_ids)) != len(item_ids) or set(item_ids) & existing_items):
        raise ValueError("sections and claims must be appended with new IDs")
    active_sections = (old_sections | set(section_ids)) - archived
    for uid, unit in units.items():
        refs = assignments.get(uid, unit)["evidence_section_ids"]
        if set(refs) - active_sections:
            raise ValueError(f"{uid} points to missing or archived evidence")
    linked = {sid for a in assignments.values() for sid in a["evidence_section_ids"]}
    if set(section_ids) - linked:
        raise ValueError("new sections must belong to a selected research unit")
    checks = {c["source"]["source_id"]: c for c in bundle["source_checks"]}
    if len(checks) != len(bundle["source_checks"]):
        raise ValueError("duplicate source check")
    sources = {s["source_id"]: s for s in surface["sources"]}
    for sid, check in checks.items():
        source = check["source"]
        if sid in sources and sources[sid] != source:
            raise ValueError(f"source metadata changed under an existing ID: {sid}")
        if not source["url"].startswith("https://"):
            raise ValueError("public source URL must use HTTPS")
        if datetime.fromisoformat(check["checked_at"]) > datetime.fromisoformat(bundle["created_at"]):
            raise ValueError("source check occurs after update creation")
    for section in bundle["sections"]:
        for item in section["items"]:
            if set(item["source_ids"]) - checks.keys():
                raise ValueError("every new claim needs its own checked primary sources")
            if set(item["actor_ids"]) - {a["actor_id"] for a in surface["actors"]}:
                raise ValueError("unknown actor")
    gaps = {g["gap_id"]: g for g in surface["coverage_gaps"]}
    new_gaps = {g["gap_id"]: g for g in bundle["coverage_gaps"]}
    if len(new_gaps) != len(bundle["coverage_gaps"]) or new_gaps.keys() & gaps.keys():
        raise ValueError("Coverage Gaps must be append-only")
    if any(bundle["topic_id"] not in g["topic_ids"] for g in new_gaps.values()):
        raise ValueError("gap does not cover selected Topic")

    baseline, surface = copy.deepcopy(baseline), copy.deepcopy(surface)
    topic = next(t for t in baseline["topics"] if t["topic_id"] == bundle["topic_id"])
    profile = profile_for(surface, bundle["topic_id"])
    for unit in topic["research_units"]:
        if unit["unit_id"] in assignments:
            unit.update(status="partial", evidence_section_ids=assignments[unit["unit_id"]]["evidence_section_ids"],
                        latest_update_id=bundle["update_id"], last_researched_at=bundle["created_at"])
    topic["status"] = "partial"
    profile.update(summary_ja=bundle["summary_ja"], summary_en=bundle["summary_en"],
                   archived_section_ids=sorted(archived))
    profile["sections"].extend(bundle["sections"])
    profile["coverage_gap_ids"].extend(new_gaps)
    profile.setdefault("research_updates", []).append({
        "update_id": bundle["update_id"], "bundle_sha256": digest,
        "base_commit": bundle["base_commit"], "unit_ids": list(assignments),
        "created_at": bundle["created_at"], "consensus_status": "incomplete"})
    surface["sources"].extend(c["source"] for sid, c in checks.items() if sid not in sources)
    surface["coverage_gaps"].extend(bundle["coverage_gaps"])
    surface["as_of"] = max(surface["as_of"], bundle["created_at"][:10])
    surface["publication"].update(human_approval_directive_id=bundle["human_directive_id"],
                                 publication_decision_id="PUBDEC-PROVISIONAL-UNIT-UPDATES-001")
    return baseline, surface, True


def verify_applied(bundle, baseline, surface):
    profile = profile_for(surface, bundle["topic_id"])
    receipt = next(u for u in profile["research_updates"] if u["update_id"] == bundle["update_id"])
    expected = {"update_id": bundle["update_id"], "bundle_sha256": stable_digest(bundle),
                "base_commit": bundle["base_commit"],
                "unit_ids": [u["unit_id"] for u in bundle["units"]],
                "created_at": bundle["created_at"], "consensus_status": "incomplete"}
    if receipt != expected:
        raise ValueError("applied bundle receipt mismatch")
    if set(bundle["archive_section_ids"]) - set(profile.get("archived_section_ids", [])):
        raise ValueError("archived history was reactivated")
    gaps = {g["gap_id"]: g for g in surface["coverage_gaps"]}
    for gap in bundle["coverage_gaps"]:
        if gaps.get(gap["gap_id"]) != gap or gap["gap_id"] not in profile["coverage_gap_ids"]:
            raise ValueError("applied Coverage Gap differs from immutable update")
    if profile["research_updates"][-1]["update_id"] == bundle["update_id"] and any(
            profile[key] != bundle[key] for key in ("summary_ja", "summary_en")):
        raise ValueError("latest research summary drifted")
    sections = {s["section_id"]: s for s in profile["sections"]}
    for section in bundle["sections"]:
        if sections.get(section["section_id"]) != section:
            raise ValueError("applied section differs from immutable update")
    sources = {s["source_id"]: s for s in surface["sources"]}
    for check in bundle["source_checks"]:
        if sources.get(check["source"]["source_id"]) != check["source"]:
            raise ValueError("applied source differs from immutable update")
    topic = next(t for t in baseline["topics"] if t["topic_id"] == bundle["topic_id"])
    for assignment in bundle["units"]:
        unit = next(u for u in topic["research_units"] if u["unit_id"] == assignment["unit_id"])
        if unit.get("latest_update_id") == bundle["update_id"] and (
                unit["status"] != "partial" or unit["evidence_section_ids"] != assignment["evidence_section_ids"]
                or unit.get("last_researched_at") != bundle["created_at"]):
            raise ValueError("applied research unit drifted")


def audit_updates(root=ROOT):
    from jsonschema import ValidationError
    errors = []
    baseline, surface = read(root, BASELINE), read(root, SURFACE)
    seen = set()
    for profile in surface["topic_profiles"]:
        for receipt in profile.get("research_updates", []):
            try:
                if receipt["update_id"] in seen:
                    raise ValueError("duplicate research receipt")
                seen.add(receipt["update_id"])
                bundle = read(root, f"proposals/research-unit-updates/{receipt['update_id']}.json")
                validate_contract(root, bundle)
                if bundle["topic_id"] != profile["topic_id"]:
                    raise ValueError("receipt belongs to another Topic")
                verify_authorization(root, bundle)
                verify_pinned_input(root, bundle)
                verify_applied(bundle, baseline, surface)
            except (ValueError, OSError, KeyError, StopIteration, ValidationError, subprocess.CalledProcessError) as exc:
                errors.append(f"{receipt['update_id']}: {exc}")
        latest_by_unit = {uid: receipt["update_id"] for receipt in profile.get("research_updates", [])
                          for uid in receipt["unit_ids"]}
        topic = next(t for t in baseline["topics"] if t["topic_id"] == profile["topic_id"])
        for unit in topic.get("research_units", []):
            if unit.get("latest_update_id") != latest_by_unit.get(unit["unit_id"]):
                errors.append(f"{unit['unit_id']}: latest update does not match receipt history")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bundle", nargs="?")
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--human-authorized", action="store_true")
    args = parser.parse_args()
    if args.audit:
        errors = audit_updates()
        print(json.dumps({"errors": errors, "consensus_status": "incomplete"}, indent=2))
        return bool(errors)
    if not args.bundle:
        parser.error("bundle is required unless --audit is set")
    bundle_path = Path(args.bundle).resolve()
    bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
    expected = ROOT / "proposals/research-unit-updates" / f"{bundle['update_id']}.json"
    if bundle_path != expected:
        raise ValueError("bundle must be at its declared repository path")
    verify_pinned_input(ROOT, bundle)
    baseline, surface, changed = project(ROOT, bundle, read(ROOT, BASELINE), read(ROOT, SURFACE))
    if args.apply:
        if not args.human_authorized:
            raise ValueError("interactive human authorization is required; not a scheduled worker")
        subprocess.run(["python3", "tools/check_agent_permissions.py", "--role", "maintainer",
                        "--human-authorized", BASELINE, SURFACE], cwd=ROOT, check=True)
        if changed:
            for ref, value in ((BASELINE, baseline), (SURFACE, surface)):
                (ROOT / ref).write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"update_id": bundle["update_id"], "changed": changed,
                      "applied": args.apply, "consensus_status": "incomplete"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
