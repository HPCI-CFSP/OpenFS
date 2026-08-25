#!/usr/bin/env python3
"""Normalize a structured public-Web capture into traceable Source receipts."""

from __future__ import annotations

import argparse
import ipaddress
import json
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from openfs_runtime import (
    atomic_write_json,
    isoformat,
    language_in_scope,
    read_json,
    run_snapshot_path,
    stable_digest,
)


ROOT = Path(__file__).resolve().parents[1]

# Common multi-label public suffixes. Unknown suffixes fall back to the final
# two labels, which is conservative for publisher-independence counting.
MULTI_LABEL_PUBLIC_SUFFIXES = {
    "ac.jp",
    "co.jp",
    "go.jp",
    "ne.jp",
    "or.jp",
    "com.au",
    "edu.au",
    "gov.au",
    "org.au",
    "ac.uk",
    "co.uk",
    "gov.uk",
    "org.uk",
    "com.br",
    "com.cn",
    "edu.cn",
    "gov.cn",
    "org.cn",
    "github.io",
}

LINEAGE_RELATIONSHIPS = {
    "original",
    "reprint",
    "summary",
    "translation",
    "derived_analysis",
    "shared_dataset",
}


def _public_host(hostname: str) -> bool:
    lowered = hostname.lower().rstrip(".")
    if lowered in {"localhost", "localhost.localdomain"} or lowered.endswith(".local"):
        return False
    try:
        address = ipaddress.ip_address(lowered)
    except ValueError:
        return True
    return not (
        address.is_private
        or address.is_loopback
        or address.is_link_local
        or address.is_multicast
        or address.is_reserved
        or address.is_unspecified
    )


def canonicalize_url(url: str, policy: dict[str, Any]) -> str:
    parsed = urlsplit(url.strip())
    if parsed.scheme not in policy["allowed_url_schemes"]:
        raise ValueError(f"URL scheme is not allowed: {parsed.scheme}")
    if not parsed.hostname or not _public_host(parsed.hostname):
        raise ValueError(f"URL host is not a public Internet host: {parsed.hostname}")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not allowed")
    prefixes = tuple(policy.get("tracking_query_prefixes", []))
    keys = set(policy.get("tracking_query_keys", []))
    query = sorted(
        (key, value)
        for key, value in parse_qsl(parsed.query, keep_blank_values=True)
        if key not in keys and not key.startswith(prefixes)
    )
    host = parsed.hostname.lower()
    port = parsed.port
    netloc = host if port is None else f"{host}:{port}"
    path = parsed.path or "/"
    return urlunsplit((parsed.scheme.lower(), netloc, path, urlencode(query), ""))


def publisher_authority(url: str) -> str:
    """Return a stable, conservative Web authority for publisher grouping."""
    hostname = (urlsplit(url).hostname or "").lower().rstrip(".")
    labels = hostname.split(".")
    if len(labels) <= 2:
        return hostname
    suffix = ".".join(labels[-2:])
    if suffix in MULTI_LABEL_PUBLIC_SUFFIXES and len(labels) >= 3:
        return ".".join(labels[-3:])
    return suffix


def _identifier(prefix: str, value: Any) -> str:
    return f"{prefix}-{stable_digest(value)[:12].upper()}"


def _numeric_proposal_id(value: Any) -> str:
    number = int(stable_digest(value)[:12], 16) % 1_000_000
    return f"PRP-SRC-{number:06d}"


def _validate_rights(
    rights: dict[str, Any],
    passages: list[dict[str, Any]],
    policy: dict[str, Any],
) -> None:
    required = {"access", "ai_processing", "acquisition_decision", "basis", "terms_url"}
    missing = required - set(rights)
    if missing:
        raise ValueError(f"rights record is missing: {sorted(missing)}")
    allowed = policy["rights_rules"].get(rights["ai_processing"])
    if allowed is None or rights["acquisition_decision"] not in allowed:
        raise ValueError(
            "acquisition decision is not allowed for the declared AI-processing terms"
        )
    if rights["acquisition_decision"] in {"metadata-only", "blocked"} and passages:
        raise ValueError("metadata-only or blocked sources cannot contain candidate passages")
    if rights["access"] == "clickthrough" and rights["acquisition_decision"] not in {
        "metadata-only",
        "blocked",
    }:
        raise ValueError("clickthrough sources require metadata-only or blocked handling")


def _validate_coverage_tags(tags: Any) -> None:
    if tags is None:
        return
    if not isinstance(tags, dict):
        raise ValueError("coverage_tags must be an object")
    allowed = {
        "world_regions",
        "technology_categories",
        "organization_types",
        "maturity_signals",
        "result_signals",
    }
    unknown = set(tags) - allowed
    if unknown:
        raise ValueError(f"coverage_tags has unknown dimensions: {sorted(unknown)}")
    for dimension, values in tags.items():
        if (
            not isinstance(values, list)
            or not values
            or not all(isinstance(value, str) and value for value in values)
            or len(values) != len(set(values))
        ):
            raise ValueError(f"coverage_tags.{dimension} must be unique non-empty strings")


def register_capture(
    capture: dict[str, Any],
    *,
    run_id: str,
    work_item_id: str,
    agent_id: str,
    policy: dict[str, Any],
    source_registry: dict[str, Any],
    assignment_scope: dict[str, Any] | None = None,
) -> dict[str, Any]:
    required = {"query", "source", "candidate_passages"}
    missing = required - set(capture)
    if missing:
        raise ValueError(f"capture is missing: {sorted(missing)}")
    query = capture["query"]
    source = capture["source"]
    passages = capture["candidate_passages"]
    if not isinstance(passages, list):
        raise ValueError("candidate_passages must be an array")
    if len(passages) > policy["maximum_candidate_passages_per_source"]:
        raise ValueError("capture has too many candidate passages")
    for passage in passages:
        if not passage.get("text") or not passage.get("locator"):
            raise ValueError("each candidate passage requires text and locator")
        if len(passage["text"]) > policy["maximum_candidate_passage_characters"]:
            raise ValueError("candidate passage exceeds the configured character limit")

    source_classes = {item["class_id"]: item for item in source_registry["source_classes"]}
    if source.get("source_class") not in source_classes:
        raise ValueError(f"unknown source class: {source.get('source_class')}")
    _validate_rights(source.get("rights", {}), passages, policy)
    _validate_coverage_tags(source.get("coverage_tags"))
    for failure in query.get("failures", []):
        impact = failure.get("coverage_impact")
        if impact is not None and impact not in {"blocking", "warning"}:
            raise ValueError("query failure coverage_impact must be blocking or warning")

    canonical_url = canonicalize_url(source["canonical_url"], policy)
    retrieved_url = canonicalize_url(source.get("retrieved_url", canonical_url), policy)
    origin_url = canonicalize_url(source.get("origin_url", canonical_url), policy)
    relationship = source.get("relationship", "original")
    if relationship not in LINEAGE_RELATIONSHIPS:
        raise ValueError(f"unknown Source lineage relationship: {relationship}")
    if relationship == "original":
        if origin_url != canonical_url:
            raise ValueError("an original Source must use its canonical URL as origin_url")
    else:
        if not source.get("origin_url"):
            raise ValueError("a derivative Source requires an explicit origin_url")
        if origin_url == canonical_url:
            raise ValueError("a derivative Source origin_url must differ from canonical_url")
    if source.get("source_class") == "derivative-reporting" and relationship == "original":
        raise ValueError("derivative-reporting cannot use the original relationship")

    publisher_domain = publisher_authority(canonical_url)
    source_id = _identifier(
        "SRC",
        {
            "canonical_url": canonical_url,
            "publication_date": source.get("publication_date"),
            "title": source["title"],
        },
    )
    origin_group_id = _identifier("ORG", origin_url)
    publisher_group_id = _identifier("PUB", publisher_domain)
    lineage_id = _identifier("LIN", {"source_id": source_id, "origin": origin_url})
    query_receipt_id = _identifier(
        "QRY",
        {
            "run_id": run_id,
            "work_item_id": work_item_id,
            "query": query["text"],
            "executed_at": query["executed_at"],
        },
    )
    all_text = "\n".join(passage["text"] for passage in passages).lower()
    matched_markers = sorted(
        marker
        for marker in policy.get("prompt_injection_markers", [])
        if marker.lower() in all_text
    )
    rights = source["rights"]
    primary_source = bool(
        source.get(
            "primary_source",
            source_classes[source["source_class"]]["default_primary"],
        )
    )
    if relationship != "original" and primary_source:
        raise ValueError("a derivative Source cannot be marked as primary_source")
    retrieval_status = source.get("retrieval_status", "success")
    if rights["acquisition_decision"] == "metadata-only":
        retrieval_status = "metadata-only"
    elif rights["acquisition_decision"] == "blocked":
        retrieval_status = "blocked"

    query_receipt = {
        "schema_version": "0.1.0",
        "query_receipt_id": query_receipt_id,
        "run_id": run_id,
        "work_item_id": work_item_id,
        "query": query["text"],
        "language": query["language"],
        "retrieval_method": query["retrieval_method"],
        "executed_at": query["executed_at"],
        "results": [
            {"url": canonical_url, "rank": int(query.get("rank", 1)), "selected": True}
        ],
        "failures": query.get("failures", []),
    }
    source_receipt = {
        "schema_version": "0.2.0",
        "source_id": source_id,
        "run_id": run_id,
        "work_item_id": work_item_id,
        "canonical_url": canonical_url,
        "retrieved_url": retrieved_url,
        "title": source["title"],
        "publisher": source["publisher"],
        "publisher_authority": publisher_domain,
        "publisher_group_id": publisher_group_id,
        "publisher_group_rationale": (
            "Publisher authority is conservatively derived from the canonical "
            f"URL domain {publisher_domain}"
        ),
        "source_class": source["source_class"],
        "primary_source": primary_source,
        "publication_date": source.get("publication_date"),
        "retrieved_at": source["retrieved_at"],
        "retrieval_method": query["retrieval_method"],
        "retrieval_status": retrieval_status,
        "media_type": source.get("media_type", "text/html"),
        "language": source["language"],
        "retrieved_content_sha256": source.get("retrieved_content_sha256"),
        "retention_class": (
            "metadata-only"
            if rights["acquisition_decision"] == "blocked"
            else rights["acquisition_decision"]
        ),
        "rights": rights,
        "origin_group_id": origin_group_id,
        "origin_rationale": source.get(
            "origin_rationale",
            f"Origin identity is derived from canonical origin URL {origin_url}",
        ),
        "security": {
            "untrusted_content": True,
            "prompt_injection_suspected": bool(matched_markers),
            "matched_markers": matched_markers,
        },
    }
    if assignment_scope:
        source_receipt["assignment_scope"] = assignment_scope
    if source.get("coverage_tags"):
        source_receipt["coverage_tags"] = source["coverage_tags"]
    source_lineage = {
        "schema_version": "0.2.0",
        "lineage_id": lineage_id,
        "origin_group_id": origin_group_id,
        "canonical_origin_url": origin_url,
        "canonical_origin_source_id": (
            source_id
            if relationship == "original"
            else source.get(
                "canonical_origin_source_id",
                _identifier("UNRESOLVED", origin_url),
            )
        ),
        "member_source_ids": [source_id],
        "relationship": relationship,
        "rationale": source_receipt["origin_rationale"],
        "review_state": "provisional",
    }
    normalized_passages = [
        {
            "passage_id": _identifier(
                "PASSAGE", {"source_id": source_id, "locator": item["locator"], "text": item["text"]}
            ),
            "text": item["text"],
            "locator": item["locator"],
            "passage_kind": item.get("passage_kind", "paraphrase"),
            "candidate_claim": item.get("candidate_claim"),
            "untrusted_content": True,
        }
        for item in passages
    ]
    created_at = capture.get("created_at") or isoformat()
    return {
        "schema_version": "0.2.0",
        "proposal_id": _numeric_proposal_id(
            {
                "source_id": source_id,
                "run_id": run_id,
                "work_item_id": work_item_id,
            }
        ),
        "object_type": "source",
        "run_id": run_id,
        "work_item_id": work_item_id,
        "created_by_agent_id": agent_id,
        "created_at": created_at,
        "query_receipt": query_receipt,
        "source_receipt": source_receipt,
        "source_lineage": source_lineage,
        "candidate_passages": normalized_passages,
        "capture_digest": stable_digest(capture),
    }


def write_result(path: Path, result: dict[str, Any]) -> None:
    if path.exists():
        existing = read_json(path)
        if existing != result:
            raise RuntimeError(f"source result already exists with different content: {path}")
        return
    atomic_write_json(path, result)


def validate_assignment(
    capture: dict[str, Any],
    work_item: dict[str, Any],
    *,
    agent_id: str,
    output_ref: str,
) -> None:
    if work_item.get("kind") != "source-discovery":
        raise ValueError("Work Item is not assigned to Source discovery")
    lease = work_item.get("lease", {})
    if work_item.get("status") != "leased" or lease.get("agent_id") != agent_id:
        raise RuntimeError("Source registration requires the current Work Item lease")
    if output_ref not in work_item.get("output_paths", []):
        raise ValueError("Source output is outside the Work Item's declared paths")
    payload = work_item.get("payload", {})
    query = capture.get("query", {})
    source = capture.get("source", {})
    if query.get("text") != payload.get("query"):
        raise ValueError("Capture query differs from the assigned Monitor query")
    if not language_in_scope(query.get("language"), payload.get("languages", [])):
        raise ValueError("Capture language is outside the assigned Monitor scope")
    if source.get("source_class") not in payload.get("source_classes", []):
        raise ValueError("Capture Source class is outside the assigned Monitor scope")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--work-item-id", required=True)
    parser.add_argument("--agent-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    capture = read_json(args.capture)
    work_item = read_json(
        args.root / "queue" / args.run_id / f"{args.work_item_id}.json"
    )
    output_path = args.output if args.output.is_absolute() else args.root / args.output
    output_ref = str(output_path.relative_to(args.root))
    validate_assignment(
        capture,
        work_item,
        agent_id=args.agent_id,
        output_ref=output_ref,
    )
    result = register_capture(
        capture,
        run_id=args.run_id,
        work_item_id=args.work_item_id,
        agent_id=args.agent_id,
        policy=read_json(
            run_snapshot_path(
                args.root, args.run_id, "config/acquisition-policy.json"
            )
        ),
        source_registry=read_json(
            run_snapshot_path(args.root, args.run_id, "config/source-registry.json")
        ),
        assignment_scope={
            key: work_item.get("payload", {})[key]
            for key in (
                "subject_ids",
                "profile_fields",
                "query_template_id",
                "coverage_gap_refs",
                "coverage_gap_queue_id",
                "coverage_gap_queue_item_id",
                "query_seed_language",
            )
            if key in work_item.get("payload", {})
        },
    )
    write_result(output_path, result)
    print(json.dumps({"source_id": result["source_receipt"]["source_id"], "output": output_ref}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
