#!/usr/bin/env python3
"""Check program coverage without equating a program entry with technical review."""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REGISTER = "knowledge/public/conferences/HC2026.json"


def validate_coverage(payload: dict, baseline: dict, surface: dict) -> None:
    def indexed(records, key):
        result = {record[key]: record for record in records}
        if len(result) != len(records):
            raise ValueError(f"duplicate {key}")
        return result

    sources = indexed(payload["sources"], "source_id")
    entries = indexed(payload["entries"], "entry_id")
    active = {t["topic_id"] for t in baseline["topics"] if t["status"] != "retired"}
    claims = {i["item_id"]: (p["topic_id"], i) for p in surface["topic_profiles"]
              for s in p["sections"] if s["section_id"] not in p.get("archived_section_ids", [])
              for i in s["items"]}
    if payload["research_status"] != "provisional" or payload["consensus_status"] != "incomplete":
        raise ValueError("conference research must remain provisional and Consensus-incomplete")
    counts = Counter(e["kind"] for e in entries.values())
    if counts != payload["expected_counts"]:
        raise ValueError("program count mismatch")
    # The HC2026 snapshot is an explicit denominator, not a count inferred from successes.
    if payload["conference_id"] == "HC2026":
        expected = {f"HC26-{prefix}{n:02d}" for prefix, total in
                    [("T", 10), ("C", 26), ("K", 1), ("P", 11)] for n in range(1, total + 1)}
        if set(entries) != expected or counts != {"tutorial": 10, "technical": 26, "keynote": 1, "poster": 11}:
            raise ValueError("HC2026 snapshot requires all 48 entries")
    program = sources[payload["program_source_id"]]
    if program["role"] != "program" or program["retrieval_status"] != "read":
        raise ValueError("a checked program is required")
    for source in sources.values():
        url = urlparse(source["url"])
        if url.scheme != "https" or not url.hostname or url.username or url.password:
            raise ValueError("anonymous HTTPS sources required")
    for entry in entries.values():
        topics = {entry["primary_topic_id"], *entry["related_topic_ids"]}
        if topics - active:
            raise ValueError("unknown or retired catalog topic")
        refs = set(entry["source_ids"])
        if refs - sources.keys() or payload["program_source_id"] not in refs:
            raise ValueError("unresolved source or missing program reference")
        if not entry["gap_ja"] or not entry["gap_en"]:
            raise ValueError("unfinished verification requires bilingual gaps")
        state = entry["coverage_state"]
        if (state == "related-primary-checked") != bool(entry["technical_item_ids"]):
            raise ValueError("program/abstract checks cannot imply technical claims")
        if state == "abstract-only" and not any(sources[s]["retrieval_status"] == "abstract-read" for s in refs):
            raise ValueError("abstract-only requires a checked abstract")
        for item_id in entry["technical_item_ids"]:
            if item_id not in claims or claims[item_id][0] not in topics:
                raise ValueError("claim belongs to a missing or unrelated topic")
            claim = claims[item_id][1]
            if claim["consensus_status"] != "incomplete" or not set(claim["source_ids"]) <= refs:
                raise ValueError("claim status/source mismatch")
            if any(sources[s]["role"] != "primary" or sources[s]["retrieval_status"] != "read"
                   for s in claim["source_ids"]):
                raise ValueError("technical claims require read primary content, not snippets or abstracts")
    for partnership in payload["partnerships"]:
        if set(partnership["entry_ids"]) - entries.keys() or set(partnership["source_ids"]) - sources.keys():
            raise ValueError("unresolved partnership reference")
    for announcement in payload["related_announcements"]:
        claim = claims.get(announcement["technical_item_id"])
        if (not claim or claim[0] != announcement["topic_id"]
                or set(announcement["source_ids"]) - sources.keys()):
            raise ValueError("unresolved related announcement")
    for gap in payload["coverage_gaps"]:
        if set(gap["source_ids"]) - sources.keys():
            raise ValueError("unresolved gap source")


def load_and_validate(root: Path) -> dict:
    from jsonschema import Draft202012Validator, FormatChecker
    from validate_json_schemas import schema_registry
    def read(ref):
        return json.loads((root / ref).read_text(encoding="utf-8"))
    payload = read(REGISTER)
    schemas, registry = schema_registry(root)
    Draft202012Validator(schemas["conference-coverage.schema.json"], registry=registry,
                         format_checker=FormatChecker()).validate(payload)
    validate_coverage(payload, read("config/research-baseline.json"),
                      read("knowledge/public/topic-decision-support.json"))
    return payload


if __name__ == "__main__":
    result = load_and_validate(ROOT)
    print(f"PASS conference coverage: {len(result['entries'])} entries; Consensus incomplete")
