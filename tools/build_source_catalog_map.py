#!/usr/bin/env python3
"""Build the generated URL-to-catalog and roadmap evidence map."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit


ROADMAP_DIR = Path("knowledge/public/roadmaps")
PORTFOLIO_PATH = Path("config/roadmap-portfolio.json")
DECISION_SUPPORT_PATH = Path("knowledge/public/topic-decision-support.json")
WATCH_REGISTRY_PATH = Path("config/source-watch-registry.json")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _matching_watch_ids(url: str, watches: list[dict[str, Any]]) -> list[str]:
    parsed = urlsplit(url)
    matches = []
    for watch in watches:
        target = urlsplit(watch["canonical_url"])
        if parsed.scheme != target.scheme or parsed.netloc != target.netloc:
            continue
        target_path = target.path.rstrip("/")
        if url.rstrip("/") == watch["canonical_url"].rstrip("/"):
            matches.append(watch["watch_id"])
        elif target_path in {"", "/"}:
            matches.append(watch["watch_id"])
        elif parsed.path.startswith(target_path.rstrip("/") + "/"):
            matches.append(watch["watch_id"])
    return sorted(set(matches))


def _nested_source_ids(value: Any) -> set[str]:
    if isinstance(value, dict):
        result = set(value.get("source_ids", []))
        for child in value.values():
            result.update(_nested_source_ids(child))
        return result
    if isinstance(value, list):
        result: set[str] = set()
        for child in value:
            result.update(_nested_source_ids(child))
        return result
    return set()


def build(root: Path) -> dict[str, Any]:
    portfolio = read_json(root / PORTFOLIO_PATH)
    decision_support = read_json(root / DECISION_SUPPORT_PATH)
    active_ids = {
        topic["topic_id"] for topic in read_json(root / "config/research-baseline.json")["topics"]
        if topic["status"] != "retired"
    }
    decision_support["topic_profiles"] = [
        profile for profile in decision_support["topic_profiles"]
        if profile["topic_id"] in active_ids
    ]
    watch_registry = read_json(root / WATCH_REGISTRY_PATH)
    active_watches = [item for item in watch_registry["targets"] if item["active"]]
    family_by_id = {
        item["roadmap_id"]: item for item in portfolio["roadmap_families"]
    }

    direct_topics_by_source: dict[str, set[str]] = defaultdict(set)
    for profile in decision_support["topic_profiles"]:
        for section in profile["sections"]:
            if section["section_id"] in profile.get("archived_section_ids", []):
                continue
            for item in section["items"]:
                for source_id in item["source_ids"]:
                    direct_topics_by_source[source_id].add(profile["topic_id"])
    topics_by_surface: dict[str, set[str]] = defaultdict(set)
    for profile in decision_support["topic_profiles"]:
        for surface_id in profile.get("related_surface_ids", []):
            topics_by_surface[surface_id].add(profile["topic_id"])
    for surface_id, payload_key in (
        ("platform-software", "platform_matrix"),
        ("numerical-methods", "numerical_method_matrix"),
    ):
        for source_id in _nested_source_ids(decision_support[payload_key]):
            direct_topics_by_source[source_id].update(topics_by_surface[surface_id])
    decision_source_by_id = {
        source["source_id"]: source for source in decision_support["sources"]
    }
    direct_topics_by_url: dict[str, set[str]] = defaultdict(set)
    for source_id, topic_ids in direct_topics_by_source.items():
        direct_topics_by_url[decision_source_by_id[source_id]["url"]].update(topic_ids)

    by_url: dict[str, dict[str, Any]] = {}

    def ensure_entry(source: dict[str, Any]) -> dict[str, Any]:
        url = source["url"]
        return by_url.setdefault(
            url,
            {
                "canonical_url": url,
                "title": source["title"],
                "publisher": source["publisher"],
                "source_classes": set(),
                "roadmap_source_refs": set(),
                "catalog_source_refs": defaultdict(set),
                "topic_links": {},
                "roadmap_ids": set(),
                "track_ids": set(),
                "watch_ids": set(),
            },
        )

    for path in sorted((root / ROADMAP_DIR).glob("*.json")):
        roadmap = read_json(path)
        roadmap_id = roadmap["roadmap_id"]
        family = family_by_id[roadmap_id]
        tracks_by_source: dict[str, set[str]] = defaultdict(set)
        for track in roadmap["tracks"]:
            source_ids = set(track.get("source_ids", []))
            for band in track.get("generation_bands", []):
                source_ids.update(band.get("source_ids", []))
            for source_id in source_ids:
                tracks_by_source[source_id].add(track["track_id"])
        for lane in roadmap["lanes"]:
            for milestone in lane["milestones"]:
                for source_id in milestone["source_ids"]:
                    tracks_by_source[source_id].add(lane["track_id"])

        for source in roadmap["sources"]:
            url = source["url"]
            entry = ensure_entry(source)
            entry["source_classes"].add(source["source_class"])
            entry["roadmap_source_refs"].add((roadmap_id, source["source_id"]))
            entry["roadmap_ids"].add(roadmap_id)
            entry["track_ids"].update(tracks_by_source.get(source["source_id"], set()))
            direct_topics = direct_topics_by_url.get(url, set())
            for topic_id in family["source_topic_ids"]:
                basis = (
                    "direct-topic-evidence"
                    if topic_id in direct_topics
                    else "roadmap-family-context"
                )
                previous = entry["topic_links"].get(topic_id)
                if previous != "direct-topic-evidence":
                    entry["topic_links"][topic_id] = basis
            entry["watch_ids"].update(_matching_watch_ids(url, active_watches))

    for source in decision_support["sources"]:
        topic_ids = direct_topics_by_source.get(source["source_id"], set())
        if not topic_ids:
            continue
        entry = ensure_entry(source)
        entry["source_classes"].add(source["source_class"])
        entry["catalog_source_refs"][source["source_id"]].update(topic_ids)
        for topic_id in topic_ids:
            entry["topic_links"][topic_id] = "direct-topic-evidence"
        entry["watch_ids"].update(
            _matching_watch_ids(source["url"], active_watches)
        )

    entries = []
    for url in sorted(by_url):
        entry = by_url[url]
        entries.append(
            {
                "canonical_url": entry["canonical_url"],
                "title": entry["title"],
                "publisher": entry["publisher"],
                "source_classes": sorted(entry["source_classes"]),
                "roadmap_source_refs": [
                    {"roadmap_id": roadmap_id, "source_id": source_id}
                    for roadmap_id, source_id in sorted(entry["roadmap_source_refs"])
                ],
                "catalog_source_refs": [
                    {"source_id": source_id, "topic_ids": sorted(topic_ids)}
                    for source_id, topic_ids in sorted(entry["catalog_source_refs"].items())
                ],
                "topic_links": [
                    {"topic_id": topic_id, "mapping_basis": basis}
                    for topic_id, basis in sorted(entry["topic_links"].items())
                ],
                "roadmap_ids": sorted(entry["roadmap_ids"]),
                "track_ids": sorted(entry["track_ids"]),
                "watch_ids": sorted(entry["watch_ids"]),
            }
        )
    return {
        "schema_version": "0.2.0",
        "map_id": "SOURCE-CATALOG-MAP-001",
        "generated_from": [
            str(PORTFOLIO_PATH),
            str(DECISION_SUPPORT_PATH),
            str(WATCH_REGISTRY_PATH),
            str(ROADMAP_DIR),
        ],
        "unmapped_catalog_source_ids": sorted(
            source["source_id"]
            for source in decision_support["sources"]
            if not direct_topics_by_source.get(source["source_id"])
        ),
        "entries": entries,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("knowledge/public/source-catalog-map.json"),
    )
    args = parser.parse_args()
    result = build(args.root)
    output = args.output if args.output.is_absolute() else args.root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Wrote {len(result['entries'])} URL mappings to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
