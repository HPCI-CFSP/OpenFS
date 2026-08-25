#!/usr/bin/env python3
"""Turn Center Profile gaps into a bounded next-Run discovery plan."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from openfs_runtime import atomic_write_json, isoformat, read_json, stable_digest


ROOT = Path(__file__).resolve().parents[1]
FIELD_PRIORITY = (
    "refresh_window",
    "procurement",
    "budget",
    "power",
    "facility",
    "migration",
    "data_connectivity",
    "software",
    "users",
    "priority_domains",
    "operations",
    "current_system",
)
QUERY_TERMS_JA = {
    "users": "利用者 利用分野 利用実績",
    "priority_domains": "重点分野 主要用途",
    "current_system": "現行システム 稼働状況",
    "refresh_window": "更新時期 次期システム 調達",
    "power": "消費電力 電力制約",
    "facility": "設備 建屋 冷却",
    "budget": "予算 事業計画 概算要求",
    "procurement": "調達 入札 仕様書 契約",
    "software": "ソフトウェア 利用環境",
    "operations": "運用体制 利用支援",
    "migration": "移行計画 互換性",
    "data_connectivity": "ストレージ ネットワーク データ転送",
}


def _institution_domain(hostname: str | None) -> str | None:
    if not hostname:
        return None
    labels = hostname.lower().split(".")
    if len(labels) <= 2:
        return hostname.lower()
    if labels[-2:] == ["ac", "jp"] or labels[-2:] == ["go", "jp"]:
        return ".".join(labels[-3:])
    if labels[-2:] == ["co", "jp"] or labels[-2:] == ["or", "jp"]:
        return ".".join(labels[-3:])
    return ".".join(labels[-2:])


def _query_strategy(
    *,
    generation: int,
    center_name_ja: str,
    center_name_en: str,
    terms: str,
    center_domain: str | None,
) -> tuple[str, str, list[str]]:
    if generation == 1:
        site = f" site:{center_domain}" if center_domain else ""
        return (
            "center-domain",
            f"{center_name_ja} {terms} 公式{site}",
            ["center-primary", "procurement-primary"],
        )
    if generation == 2:
        domain = _institution_domain(center_domain)
        site = f" site:{domain}" if domain else ""
        return (
            "institution-domain-and-procurement",
            f"{center_name_ja} {terms} 調達 仕様書 入札 年報 事業報告{site}",
            ["center-primary", "procurement-primary", "official-primary"],
        )
    return (
        "cross-domain-primary-records",
        (
            f'"{center_name_ja}" "{center_name_en}" {terms} '
            "調達 仕様書 事業報告 government procurement"
        ),
        [
            "center-primary",
            "procurement-primary",
            "official-primary",
            "project-deliverable",
        ],
    )


def build_plan(
    root: Path,
    *,
    run_id: str,
    maximum_queries: int = 15,
    maximum_fields_per_query: int = 4,
    generated_at: str | None = None,
) -> dict[str, Any]:
    if maximum_queries < 1 or maximum_fields_per_query < 1:
        raise ValueError("follow-up limits must be positive")
    manifest = read_json(root / "runs" / run_id / "manifest.json")
    if manifest.get("status") not in {"completed", "partial"}:
        raise ValueError("follow-up planning requires a durable completed or partial Run")
    brief_ref = f"reviews/briefs/{run_id}-center-research.json"
    brief = read_json(root / brief_ref)
    registry_ref = "config/hpci-center-registry.json"
    snapshot_ref = manifest.get("configuration_snapshots", {}).get(registry_ref)
    if not snapshot_ref:
        raise ValueError("Run has no pinned HPCI center registry")
    registry = read_json(root / snapshot_ref)
    registry_centers = {
        center["center_id"]: center for center in registry.get("centers", [])
    }
    predecessor_plan_ref = manifest.get("followup_plan", {}).get("source_ref")
    predecessor_plan = (
        read_json(root / predecessor_plan_ref) if predecessor_plan_ref else None
    )
    predecessor_queries = {
        query["center_id"]: query
        for query in (predecessor_plan or {}).get("queries", [])
    }
    queries = []
    for center in brief.get("centers", []):
        center_id = center["center_id"]
        if center_id not in registry_centers:
            raise ValueError(f"brief contains a center outside the pinned registry: {center_id}")
        gaps = set(center.get("missing_or_partial_fields", []))
        selected = [field for field in FIELD_PRIORITY if field in gaps][
            :maximum_fields_per_query
        ]
        if not selected:
            continue
        registry_center = registry_centers[center_id]
        domain = urlparse(registry_center.get("official_url", "")).hostname
        terms = " ".join(QUERY_TERMS_JA[field] for field in selected)
        previous_query = predecessor_queries.get(center_id)
        generation = int((previous_query or {}).get("search_generation", 1)) + int(
            previous_query is not None
        )
        strategy, query_text, source_classes = _query_strategy(
            generation=generation,
            center_name_ja=registry_center["name_ja"],
            center_name_en=registry_center.get(
                "name_en", registry_center["name_ja"]
            ),
            terms=terms,
            center_domain=domain,
        )
        query_id = f"FOLLOWUP-{center_id}"
        query = {
            "query_id": query_id,
            "center_id": center_id,
            "name_ja": registry_center["name_ja"],
            "profile_fields": selected,
            "query": query_text,
            "query_role": "gap-followup",
            "source_classes": source_classes,
            "search_generation": generation,
            "search_strategy": strategy,
            "rationale": "Incomplete Center Profile fields from the preceding Run.",
        }
        if previous_query and predecessor_plan_ref:
            query["previous_query_ref"] = (
                f"{predecessor_plan_ref}#{previous_query['query_id']}"
            )
            query["previous_query_digest"] = stable_digest(previous_query)
        queries.append(query)
        if len(queries) >= maximum_queries:
            break
    timestamp = generated_at or isoformat()
    identity = {
        "base_run_id": run_id,
        "brief_digest": stable_digest(brief),
        "queries": queries,
    }
    return {
        "schema_version": "0.1.0",
        "followup_plan_id": f"CFP-{stable_digest(identity)[:12].upper()}",
        "monitor_id": manifest["monitor_id"],
        "task_id": manifest["task_id"],
        "base_run_id": run_id,
        "base_run_status": manifest["status"],
        "generated_at": timestamp,
        "status": "generated-for-research",
        "publication_status": "internal-review-only",
        "input_brief_ref": brief_ref,
        "input_brief_digest": stable_digest(brief),
        "predecessor_plan": {
            "plan_ref": predecessor_plan_ref,
            "plan_id": predecessor_plan["followup_plan_id"],
            "plan_digest": stable_digest(predecessor_plan),
        }
        if predecessor_plan
        else None,
        "limits": {
            "maximum_queries": maximum_queries,
            "maximum_fields_per_query": maximum_fields_per_query,
        },
        "queries": queries,
        "caveats": [
            "Follow-up queries are discovery instructions, not accepted findings.",
            "No public evidence may remain unknown; agents must not infer missing values.",
            "The next Run must snapshot this plan before execution.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--maximum-queries", type=int, default=15)
    parser.add_argument("--maximum-fields-per-query", type=int, default=4)
    parser.add_argument("--generated-at")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    plan = build_plan(
        args.root,
        run_id=args.run_id,
        maximum_queries=args.maximum_queries,
        maximum_fields_per_query=args.maximum_fields_per_query,
        generated_at=args.generated_at,
    )
    output = args.output or Path(
        f"reviews/followups/{args.run_id}-center-gaps.json"
    )
    output = output if output.is_absolute() else args.root / output
    atomic_write_json(output, plan)
    print(
        json.dumps(
            {
                "output": str(output),
                "followup_plan_id": plan["followup_plan_id"],
                "query_count": len(plan["queries"]),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
