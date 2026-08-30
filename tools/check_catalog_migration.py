#!/usr/bin/env python3
"""Audit catalog migration against pinned pre-migration Git objects."""
from __future__ import annotations
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def audit(root: Path) -> dict:
    def read(path):
        return json.loads((root / path).read_text(encoding="utf-8"))
    migration = read("config/catalog-migration.json")
    commit = migration["base_commit"]
    if not re.fullmatch(r"[0-9a-f]{40}", commit):
        raise ValueError("migration base must be a full Git commit hash")
    def before(path):
        result = subprocess.run(["git", "show", f"{commit}:{path}"], cwd=root,
                                text=True, capture_output=True, check=True)
        return json.loads(result.stdout)
    old_topics = {t["topic_id"]: t for t in before("config/research-baseline.json")["topics"]}
    current_topics = {t["topic_id"]: t for t in read("config/research-baseline.json")["topics"]}
    errors = []
    if old_topics.keys() - current_topics.keys():
        errors.append("historical canonical Topic IDs were removed")
    entries = {entry["source_topic_id"]: entry for entry in migration["entries"]}
    if entries.keys() != {tid for tid, t in old_topics.items() if t["status"] != "retired"}:
        errors.append("migration does not cover the exact pre-migration active catalog")
    for tid, entry in entries.items():
        if entry["source_questions"] != old_topics[tid]["research_questions"]:
            errors.append(f"original questions changed or lost for {tid}")
    old_artifact = before("knowledge/public/topic-decision-support.json")
    artifact = read("knowledge/public/topic-decision-support.json")
    def items(data):
        return {i["item_id"]: i for p in data["topic_profiles"] for s in p["sections"] for i in s["items"]}
    old_items, current_items = items(old_artifact), items(artifact)
    for iid, item in old_items.items():
        if current_items.get(iid) != item:
            errors.append(f"existing claim payload changed or disappeared: {iid}")
    old_taxonomy = before("config/catalog-taxonomy.json")
    taxonomy = read("config/catalog-taxonomy.json")
    old_codes = {code: tid for c in old_taxonomy["categories"] for tid, code in c["topic_codes"].items()}
    reserved = {code for c in taxonomy["categories"] for code in c["reserved_topic_codes"]}
    current_codes = {code: tid for c in taxonomy["categories"] for tid, code in c["topic_codes"].items()}
    if old_codes.keys() - reserved:
        errors.append("a historical public display code is no longer reserved")
    for code, tid in current_codes.items():
        if code in old_codes and tid != old_codes[code]:
            errors.append(f"historical public code reused for a different Topic: {code}")
    return {"base_commit": commit, "preserved_topic_count": len(old_topics),
            "migration_entry_count": len(entries), "preserved_item_count": len(old_items),
            "as_of_before": old_artifact["as_of"], "as_of_after": artifact["as_of"], "errors": errors}


if __name__ == "__main__":
    report = audit(ROOT)
    print(json.dumps(report, indent=2))
    raise SystemExit(bool(report["errors"]))
