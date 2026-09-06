#!/usr/bin/env python3
"""Build default component layouts for active public Topic pages.

The research baseline owns the ordered research units and their evidence-section
references. This builder turns that structure into presentation components while
leaving existing curated layouts, comparison tables, and term mappings unchanged.
"""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
BASELINE_PATH = ROOT / "config/research-baseline.json"
PORTFOLIO_PATH = ROOT / "config/roadmap-portfolio.json"
SUPPORT_PATH = ROOT / "knowledge/public/topic-decision-support.json"
LEGACY_CURATED_TOPIC_IDS = {
    "ARCH-01", "ARCH-03", "ARCH-04", "SSW-05", "APP-02", "CROSS-08"
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def active_topics(baseline: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        topic
        for topic in baseline["topics"]
        if topic.get("status") == "partial" and not topic.get("retirement")
    ]


def compact_topic_id(topic_id: str) -> str:
    return topic_id.replace("-", "")


def roadmap_index(portfolio: dict[str, Any]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for roadmap in portfolio["roadmap_families"]:
        for topic_id in roadmap["source_topic_ids"]:
            result.setdefault(topic_id, []).append(roadmap["roadmap_id"])
    return result


def build_default_layout(
    topic: dict[str, Any],
    profile: dict[str, Any],
    topic_roadmaps: list[str],
) -> dict[str, Any]:
    """Build one layout, assigning a shared section to its first listed unit."""
    topic_id = topic["topic_id"]
    prefix = compact_topic_id(topic_id)
    archived = set(profile.get("archived_section_ids", []))
    active_sections = [
        section["section_id"]
        for section in profile["sections"]
        if section["section_id"] not in archived
    ]
    active_set = set(active_sections)
    assigned: set[str] = set()

    components: list[dict[str, Any]] = [
        {"component_id": f"TPC-{prefix}-OVERVIEW", "type": "topic-overview"},
        {
            "component_id": f"TPC-{prefix}-UNIT-INDEX",
            "type": "research-unit-index",
        },
        {
            "component_id": f"TPC-{prefix}-COMPARISONS",
            "type": "topic-comparisons",
        },
    ]

    for unit in topic.get("research_units", []):
        section_ids = [
            section_id
            for section_id in unit.get("evidence_section_ids", [])
            if section_id in active_set and section_id not in assigned
        ]
        if not section_ids:
            raise ValueError(
                f"{unit['unit_id']} has no uniquely assigned active evidence section"
            )
        assigned.update(section_ids)
        components.append(
            {
                "component_id": f"TPC-{prefix}-{unit['unit_id'].rsplit('-', 1)[-1]}",
                "type": "research-unit",
                "unit_id": unit["unit_id"],
                "section_ids": section_ids,
                "comparison_refs": [],
                "term_item_refs": [],
                "roadmap_ids": topic_roadmaps,
            }
        )

    missing = active_set - assigned
    if missing:
        raise ValueError(
            f"{topic_id} has active sections outside its research units: {sorted(missing)}"
        )

    if profile.get("related_surface_ids"):
        components.append(
            {"component_id": f"TPC-{prefix}-SURFACES", "type": "related-surfaces"}
        )
    components.extend(
        [
            {"component_id": f"TPC-{prefix}-GAPS", "type": "coverage-gaps"},
            {
                "component_id": f"TPC-{prefix}-HISTORY",
                "type": "research-history",
                "open_by_default": False,
            },
            {"component_id": f"TPC-{prefix}-RELATED", "type": "related-topics"},
        ]
    )
    return {
        "layout_version": "1.0",
        "layout_mode": "generated",
        "components": components,
    }


def populate_layouts(
    baseline: dict[str, Any],
    portfolio: dict[str, Any],
    support: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    result = deepcopy(support)
    profiles = {profile["topic_id"]: profile for profile in result["topic_profiles"]}
    roadmaps = roadmap_index(portfolio)
    changed: list[str] = []
    for topic in active_topics(baseline):
        topic_id = topic["topic_id"]
        profile = profiles.get(topic_id)
        if profile is None:
            raise ValueError(f"active Topic lacks a public profile: {topic_id}")
        layout = profile.get("page_layout")
        if layout and layout.get("layout_mode") == "curated":
            continue
        if layout and "layout_mode" not in layout and topic_id in LEGACY_CURATED_TOPIC_IDS:
            layout["layout_mode"] = "curated"
            changed.append(topic_id)
            continue
        topic_roadmaps = roadmaps.get(topic_id, [])
        if not topic_roadmaps:
            raise ValueError(f"active Topic lacks a roadmap association: {topic_id}")
        generated_layout = build_default_layout(topic, profile, topic_roadmaps)
        if layout != generated_layout:
            profile["page_layout"] = generated_layout
            changed.append(topic_id)
    return result, changed


def missing_layout_ids(
    baseline: dict[str, Any], support: dict[str, Any]
) -> list[str]:
    profiles = {profile["topic_id"]: profile for profile in support["topic_profiles"]}
    return [
        topic["topic_id"]
        for topic in active_topics(baseline)
        if not profiles.get(topic["topic_id"], {}).get("page_layout")
    ]


def stale_generated_layout_ids(
    baseline: dict[str, Any],
    portfolio: dict[str, Any],
    support: dict[str, Any],
) -> list[str]:
    profiles = {profile["topic_id"]: profile for profile in support["topic_profiles"]}
    roadmaps = roadmap_index(portfolio)
    stale: list[str] = []
    for topic in active_topics(baseline):
        topic_id = topic["topic_id"]
        profile = profiles[topic_id]
        layout = profile.get("page_layout")
        if not layout or layout.get("layout_mode") != "generated":
            continue
        if layout != build_default_layout(topic, profile, roadmaps[topic_id]):
            stale.append(topic_id)
    return stale


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail if an active Topic has no component layout",
    )
    parser.add_argument(
        "--write",
        action="store_true",
        help="write default layouts for active Topics that do not have one",
    )
    args = parser.parse_args()
    if args.check == args.write:
        parser.error("choose exactly one of --check or --write")

    baseline = load_json(BASELINE_PATH)
    portfolio = load_json(PORTFOLIO_PATH)
    support = load_json(SUPPORT_PATH)
    if args.check:
        missing = missing_layout_ids(baseline, support)
        if missing:
            print(f"active Topics without page_layout: {', '.join(missing)}")
            return 1
        invalid_modes = [
            profile["topic_id"]
            for profile in support["topic_profiles"]
            if profile["topic_id"] in {topic["topic_id"] for topic in active_topics(baseline)}
            and profile["page_layout"].get("layout_mode") not in {"curated", "generated"}
        ]
        if invalid_modes:
            print(f"active Topics without a layout mode: {', '.join(invalid_modes)}")
            return 1
        stale = stale_generated_layout_ids(baseline, portfolio, support)
        if stale:
            print(f"generated page_layout is stale: {', '.join(stale)}")
            return 1
        print(f"All {len(active_topics(baseline))} active Topics have current page_layout.")
        return 0

    updated, changed = populate_layouts(baseline, portfolio, support)
    SUPPORT_PATH.write_text(
        json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Created or refreshed page_layout for {len(changed)} Topics.")
    for topic_id in changed:
        print(topic_id)
    return 0


if __name__ == "__main__":
    sys.exit(main())
