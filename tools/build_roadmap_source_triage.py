#!/usr/bin/env python3
"""Merge live URL audit warnings with pinned single-model retrieval reviews."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "config" / "roadmap-source-retrieval-reviews.json"
DEFAULT_AUDIT = ROOT / "knowledge" / "public" / "audits" / "roadmap-source-audit.json"
DEFAULT_OUTPUT = ROOT / "knowledge" / "public" / "audits" / "roadmap-source-triage.json"


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def registered_sources(root: Path) -> dict[tuple[str, str], str]:
    sources: dict[tuple[str, str], str] = {}
    for path in sorted((root / "knowledge" / "public" / "roadmaps").glob("*.json")):
        roadmap = read_json(path)
        for source in roadmap["sources"]:
            key = (roadmap["roadmap_id"], source["source_id"])
            if key in sources:
                raise ValueError(f"duplicate roadmap source: {key}")
            sources[key] = source["url"]
    return sources


def build_triage(root: Path, config_path: Path, audit_path: Path) -> dict[str, Any]:
    config = read_json(config_path)
    audit = read_json(audit_path)
    sources = registered_sources(root)
    reviews: dict[tuple[str, str], dict[str, Any]] = {}
    stale_review_count = 0
    for review in config["entries"]:
        key = (review["roadmap_id"], review["source_id"])
        if key in reviews:
            raise ValueError(f"duplicate retrieval review: {key}")
        if key not in sources or sources[key] != review["url"]:
            stale_review_count += 1
        reviews[key] = review

    entries: list[dict[str, Any]] = []
    for result in audit["results"]:
        if result["status"] == "reachable":
            continue
        key = (result["roadmap_id"], result["source_id"])
        review = reviews.get(key)
        current = sources.get(key)
        review_is_current = review is not None and current == review["url"] == result["url"]
        entries.append(
            {
                "roadmap_id": result["roadmap_id"],
                "source_id": result["source_id"],
                "url": result["url"],
                "http_audit_status": result["status"],
                "http_status": result["http_status"],
                "reviewed_at": review["reviewed_at"] if review_is_current else config["as_of"],
                "review_outcome": review["review_outcome"] if review_is_current else "unresolved",
                "note_ja": review["note_ja"] if review_is_current else "現在登録されているURLに一致する本文確認記録がないため、再確認が必要です。",
                "note_en": review["note_en"] if review_is_current else "No semantic retrieval review matches the current URL; follow-up is required.",
            }
        )

    entries.sort(key=lambda item: (item["roadmap_id"], item["source_id"]))
    confirmed = sum(item["review_outcome"] == "exact-url-content-confirmed" for item in entries)
    return {
        "schema_version": "0.1.0",
        "export_id": "ROADMAP-SOURCE-TRIAGE-001",
        "status": "published",
        "triage_id": f"RST-{config['as_of'].replace('-', '')}-001",
        "as_of": config["as_of"],
        "review_set_id": config["review_set_id"],
        "review_status": config["review_status"],
        "reviewer": config["reviewer"],
        "caveat_ja": "HTTP到達性の警告を単一のAIモデルが再確認した暫定記録です。主張全体を独立に検証したことや、合意判定で受理されたことを意味しません。",
        "caveat_en": "This is a provisional, single-model follow-up to HTTP-reachability warnings. It does not independently validate the full claim or indicate acceptance by the Consensus Gate.",
        "summary": {
            "non_reachable_count": len(entries),
            "reviewed_count": sum(item["review_outcome"] != "unresolved" for item in entries),
            "exact_url_content_confirmed": confirmed,
            "unresolved": len(entries) - confirmed,
            "stale_review_count": stale_review_count,
        },
        "entries": entries,
        "publication": {
            "information_classification": "public",
            "publication_approved": True,
            "publication_decision_id": "PUBDEC-20260826-002",
            "human_approval_directive_id": "DIR-900006",
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--audit", type=Path, default=DEFAULT_AUDIT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    triage = build_triage(args.root, args.config, args.audit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(triage, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(triage["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
