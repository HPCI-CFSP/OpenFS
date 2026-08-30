"""Resolve current catalog ownership without rewriting historical evidence."""
from __future__ import annotations

import json
from pathlib import Path


def load_catalog(root: Path):
    return json.loads((root / "config/research-baseline.json").read_text(encoding="utf-8"))


def active_successors(topic_id: str, topics: dict, trail=()) -> list[str]:
    if topic_id in trail:
        raise ValueError(f"catalog retirement cycle: {' -> '.join((*trail, topic_id))}")
    topic = topics.get(topic_id)
    if topic is None:
        raise ValueError(f"unknown catalog Topic: {topic_id}")
    if topic["status"] != "retired":
        return [topic_id]
    return sorted({
        successor
        for target in topic.get("retirement", {}).get("successor_topic_ids", [])
        for successor in active_successors(target, topics, (*trail, topic_id))
    })


def catalog_aliases(root: Path, baseline: dict, i18n: dict, codes: dict) -> list[dict]:
    topics = {t["topic_id"]: t for t in baseline["topics"]}
    migration = json.loads((root / "config/catalog-migration.json").read_text(encoding="utf-8"))
    previous = {entry["source_topic_id"]: entry for entry in migration["entries"]}
    aliases = []
    for tid, topic in topics.items():
        entry = previous.get(tid, {})
        old_code = entry.get("source_catalog_code")
        if topic["status"] != "retired" and (not old_code or old_code == codes.get(tid)):
            continue
        successors = active_successors(tid, topics)
        output_path = "#catalog" if tid == "CROSS-18" else "scenarios/" if tid in {"CROSS-01", "CROSS-13"} else None
        paths = topic.get("retirement", {}).get("successor_paths", [])
        if not successors and output_path is None and paths:
            output_path = f"https://github.com/HPCI-CFSP/OpenFS/blob/{migration['base_commit']}/{paths[0]}"
        aliases.append({
            "topic_id": tid, "legacy_code": old_code,
            "title_ja": entry.get("source_title_ja", topic["title_ja"]),
            "title_en": entry.get("source_title_en", i18n["topic_titles_en"][tid]),
            "target_topic_ids": successors,
            "kind": topic.get("retirement", {}).get("kind", "moved"),
            "output_path": output_path,
        })
    return aliases


def current_finding_topics(finding: dict, topics: dict) -> list[str]:
    # Historical broad buckets do not imply relevance to every new successor.
    # These routes retain the narrower classification already present in the findings.
    routes = {"ARCH-11": ["CROSS-11"], "CROSS-09": ["CROSS-06"],
              "CROSS-12": ["CROSS-08"], "CROSS-13": ["CROSS-06"]}
    return sorted({target for tid in finding["topic_ids"]
                   for target in ([tid] if topics[tid]["status"] != "retired" else routes.get(tid, []))})


def validate_catalog_scope(root: Path) -> list[str]:
    baseline = load_catalog(root)
    if baseline.get("catalog_revision", 0) < 5:
        return []
    errors = []
    topics = {t["topic_id"]: t for t in baseline["topics"]}
    active = {tid for tid, t in topics.items() if t["status"] != "retired"}
    artifact = json.loads((root / "knowledge/public/topic-decision-support.json").read_text(encoding="utf-8"))
    sections = {s["section_id"]: p["topic_id"] for p in artifact["topic_profiles"] for s in p["sections"]}
    unit_ids = set()
    for tid, topic in topics.items():
        try:
            active_successors(tid, topics)
        except ValueError as exc:
            errors.append(str(exc))
        if tid not in active:
            continue
        # AI additions have their own proposal/query-plan contract until decomposed.
        if topic.get("catalog_origin") == "ai-consensus" and "research_units" not in topic:
            continue
        for field in ("summary_ja", "summary_en", "research_units"):
            if not topic.get(field):
                errors.append(f"{tid} lacks {field}")
        if set(topic.get("related_topic_ids", [])) - active:
            errors.append(f"{tid} has inactive related Topics")
        units = topic.get("research_units", [])
        for unit in units:
            uid = unit["unit_id"]
            if uid in unit_ids or not uid.startswith(tid + "-U"):
                errors.append(f"duplicate or misowned research unit {uid}")
            unit_ids.add(uid)
            refs = unit["evidence_section_ids"]
            if any(sections.get(ref) != tid for ref in refs):
                errors.append(f"{uid} references a section owned by another Topic or missing")
            if unit["status"] != "not-started" and not refs:
                errors.append(f"{uid} claims progress without evidence")
            if unit["status"] == "reviewed":
                errors.append(f"{uid} lacks a unit-bound independent Consensus receipt")
        if topic["status"] == "reviewed" and any(u["status"] != "reviewed" for u in units):
            errors.append(f"{tid} is reviewed despite incomplete research units")
    migration = json.loads((root / "config/catalog-migration.json").read_text(encoding="utf-8"))
    directive = json.loads((root / f"reviews/directives/{migration['human_directive_id']}.json").read_text(encoding="utf-8"))
    if directive.get("status") != "approved" or not directive.get("public_information_confirmed"):
        errors.append("catalog migration lacks reviewed human authorization")
    sources = [e["source_topic_id"] for e in migration["entries"]]
    if len(sources) != 54 or len(set(sources)) != 54 or set(sources) - topics.keys():
        errors.append("catalog migration must preserve all 54 source Topics exactly once")
    for entry in migration["entries"]:
        tid = entry["source_topic_id"]
        if set(entry["target_topic_ids"]) - active:
            errors.append(f"{tid} migration points to inactive Topics")
        if not entry["target_topic_ids"] and not entry["target_paths"]:
            errors.append(f"{tid} lost its successor")
        for path in entry["target_paths"]:
            if not (root / path).exists():
                errors.append(f"{tid} missing scope successor {path}")
        if entry["action"] == "retired" and topics[tid]["status"] != "retired":
            errors.append(f"{tid} migration and baseline disagree")
    for move in migration["section_moves"]:
        if sections.get(move["section_id"]) != move["target_topic_id"]:
            errors.append(f"section migration not applied: {move['section_id']}")
    item_locations = {item["item_id"]: (p["topic_id"], s["section_id"])
                      for p in artifact["topic_profiles"] for s in p["sections"] for item in s["items"]}
    for move in migration.get("item_moves", []):
        if item_locations.get(move["item_id"]) != (move["target_topic_id"], move["target_section_id"]):
            errors.append(f"item migration not applied: {move['item_id']}")
    if {pair["domain"] for pair in migration["workload_pairs"]} != {"simulation", "ai", "experimental-realtime"}:
        errors.append("workload pairs must cover all three distinct domains")
    for pair in migration["workload_pairs"]:
        if {pair["needs_topic_id"], pair["evaluation_topic_id"]} - active:
            errors.append("workload pair references inactive Topics")
    return errors
