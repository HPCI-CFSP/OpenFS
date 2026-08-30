#!/usr/bin/env python3
"""Audit roadmap URLs through the Safe Web Fetch Broker without retaining source bodies."""

from __future__ import annotations

import argparse
import copy
import json
import os
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from safe_web_fetch_broker import FetchBlocked, FetchFailed, SafeWebFetchBroker


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "knowledge" / "public" / "audits" / "roadmap-source-audit.json"
CAPTURE_LIMIT = 1024


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def collect_sources(root: Path) -> list[dict[str, Any]]:
    collected: list[dict[str, Any]] = []
    for path in sorted((root / "knowledge" / "public" / "roadmaps").glob("*.json")):
        roadmap = read_json(path)
        for source in roadmap["sources"]:
            collected.append(
                {
                    "roadmap_id": roadmap["roadmap_id"],
                    "source_id": source["source_id"],
                    "url": source["url"],
                    "source_class": source["source_class"],
                }
            )
    return collected


def classify(status: int | None, error_kind: str | None) -> str:
    if status is not None and 200 <= status < 400:
        return "reachable"
    if status in {401, 403, 406, 429}:
        return "access-restricted"
    if status in {404, 410}:
        return "missing"
    if error_kind == "timeout":
        return "timeout"
    return "error"


def check_source(source: dict[str, Any], broker: SafeWebFetchBroker) -> dict[str, Any]:
    error_kind: str | None = None
    error_detail: str | None = None
    try:
        receipt = broker.fetch(source["url"], method="GET", capture_limit=CAPTURE_LIMIT).receipt
    except FetchBlocked as exc:
        receipt = exc.receipt
        error_kind = "policy-block"
        error_detail = str(exc)[:240]
    except FetchFailed as exc:
        receipt = exc.receipt
        detail = str(receipt.get("retrieval_error") or exc)
        error_kind = "timeout" if "timeout" in detail.lower() else "network"
        error_detail = detail[:240]

    status = receipt.get("http_status")
    result: dict[str, Any] = {
        **source,
        "status": classify(status, error_kind),
        "http_status": status,
        "final_url": receipt["final_url"],
        "content_type": receipt.get("media_type"),
        "retrieval_receipt_id": receipt["receipt_id"],
        "security_profile_id": receipt["security_profile_id"],
        "fetch_policy_decision": receipt["policy_decision"],
        "body_truncated": receipt["body_truncated"],
    }
    if error_kind:
        result["error_kind"] = error_kind
    if error_detail:
        result["error_detail"] = error_detail
    return result


def build_audit(root: Path, broker: SafeWebFetchBroker, workers: int) -> dict[str, Any]:
    checked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    as_of = datetime.now(timezone(timedelta(hours=9))).date().isoformat()
    sources = collect_sources(root)
    sources_by_url: dict[str, list[dict[str, Any]]] = {}
    for source in sources:
        sources_by_url.setdefault(source["url"], []).append(source)
    results: list[dict[str, Any]] = []
    unique_url_results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(check_source, registrations[0], broker): registrations
            for registrations in sources_by_url.values()
        }
        for future in as_completed(futures):
            result = future.result()
            unique_url_results.append(result)
            for registration in futures[future]:
                results.append({**result, **registration})
    results.sort(key=lambda item: (item["roadmap_id"], item["source_id"]))
    summary = {
        status: sum(result["status"] == status for result in results)
        for status in ("reachable", "access-restricted", "missing", "timeout", "error")
    }
    unique_url_status_counts = {
        status: sum(result["status"] == status for result in unique_url_results)
        for status in ("reachable", "access-restricted", "missing", "timeout", "error")
    }
    source_class_counts = Counter(source["source_class"] for source in sources)
    unique_urls = {source["url"] for source in sources}
    unique_external_urls = {
        source["url"]
        for source in sources
        if source["source_class"] != "openfs-governance"
    }
    public_results = [
        {key: value for key, value in result.items() if key != "error_detail"}
        for result in results
    ]
    return {
        "schema_version": "0.1.0",
        "export_id": "ROADMAP-SOURCE-AUDIT-001",
        "status": "published",
        "audit_id": f"RSA-{as_of.replace('-', '')}-001",
        "as_of": as_of,
        "checked_at": checked_at,
        "method": "One anonymous HTTP GET per distinct URL through the Safe Web Fetch Broker; redirects, DNS answers, and connection destinations are validated at every hop; at most the first 1 KiB is retained in memory and source bodies are not stored. The result is mapped to every Source ID registered for that URL.",
        "method_ja": "重複を除いたURLごとに、Safe Web Fetch Brokerを介して匿名のHTTP GETリクエストを1回送り、各ホップでリダイレクト先、DNS応答、実際の接続先を検証します。本文はメモリ上で先頭1 KiBまで取得し、保存しません。同じURLを登録した各Source IDには同一の取得結果を対応付けます。",
        "method_en": "The audit sends one anonymous HTTP GET per distinct URL through the Safe Web Fetch Broker. It validates redirects, DNS answers, and actual connection destinations at every hop, retains at most the first 1 KiB in memory, and does not store source bodies. The same retrieval result is mapped to every Source ID registered for that URL.",
        "caveat_ja": "到達性は、特定の実行環境から公開URLへ接続できたかを示すだけであり、資料中の主張の妥当性を保証しません。ブラウザで閲覧できる資料でも、403、429、タイムアウトなどが発生する場合があります。重複を除いたURL数は、独立した情報源の数とは限りません。",
        "caveat_en": "Reachability shows only whether a public URL was accessible from one execution environment; it does not validate claims in the source. A browser-accessible source may still return 403 or 429, or time out. The deduplicated URL count is not necessarily the number of independent information sources.",
        "user_agent": "OpenFS Safe Web Fetch Broker/0.1 (+https://github.com/HPCI-CFSP/OpenFS)",
        "summary": {
            "source_count": len(results),
            "fetch_count": len(unique_url_results),
            "unique_url_count": len(unique_urls),
            "duplicate_registration_count": len(results) - len(unique_urls),
            "unique_external_url_count": len(unique_external_urls),
            "external_first_party_source_count": len(results)
            - source_class_counts["openfs-governance"],
            "openfs_governance_source_count": source_class_counts["openfs-governance"],
            "source_class_counts": {
                source_class: source_class_counts[source_class]
                for source_class in (
                    "vendor-official",
                    "standards-body",
                    "government-official",
                    "research-organization",
                    "project-official",
                    "academic-primary",
                    "openfs-governance",
                )
            },
            "unique_url_status_counts": unique_url_status_counts,
            **summary,
        },
        "results": public_results,
        "publication": {
            "information_classification": "public",
            "publication_approved": True,
            "publication_decision_id": "PUBDEC-20260826-002",
            "human_approval_directive_id": "DIR-900006",
        },
    }


def reconcile_offline(root: Path, previous: dict[str, Any]) -> dict[str, Any]:
    """Refresh registrations without changing retrieval dates or inventing a fetch."""
    audit = copy.deepcopy(previous)
    by_url = {item["url"]: item for item in previous["results"]}
    results = []
    for source in collect_sources(root):
        old = by_url.get(source["url"])
        result = dict(old) if old else {
            "status": "error", "http_status": None, "final_url": source["url"],
            "content_type": None, "error_kind": "not-audited",
        }
        results.append({**result, **source})
    results.sort(key=lambda item: (item["roadmap_id"], item["source_id"]))
    unique = {item["url"]: item for item in results}
    classes = Counter(item["source_class"] for item in results)
    summary = audit["summary"]
    summary.update(source_count=len(results), unique_url_count=len(unique),
                   duplicate_registration_count=len(results) - len(unique),
                   unique_external_url_count=len({r["url"] for r in results if r["source_class"] != "openfs-governance"}),
                   external_first_party_source_count=len(results) - classes["openfs-governance"],
                   openfs_governance_source_count=classes["openfs-governance"])
    for key in summary["source_class_counts"]:
        summary["source_class_counts"][key] = classes[key]
    for status in ("reachable", "access-restricted", "missing", "timeout", "error"):
        summary[status] = sum(r["status"] == status for r in results)
        summary["unique_url_status_counts"][status] = sum(r["status"] == status for r in unique.values())
    audit["results"] = results
    audit["method_ja"] = "オフラインで現行の情報源登録と過去のURL到達性監査を対応付けています。URL完全一致の結果のみ再利用し、監査日と過去の取得回数は更新しません。新規・変更URLはerror（not-audited、HTTP状態なし）として未監査を明示します。別途記録する管理されたWebツールでの内容確認はHTTP監査や独立検証の代わりにはなりません。"
    audit["method"] = audit["method_en"] = "Offline reconciliation of current source registrations with the previous URL reachability audit. Only exact-URL results are reused; the audit date and historical fetch count are unchanged. New or changed URLs are error/not-audited with no HTTP status. Separately recorded managed-Web content reviews are not HTTP audits or independent validation."
    return audit


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--profile-id", default=os.environ.get("OPENFS_SECURITY_PROFILE_ID"))
    parser.add_argument("--offline-reconcile", action="store_true", help="Reuse exact-URL audit results; no network, no refreshed retrieval dates")
    args = parser.parse_args()
    if not args.offline_reconcile and not args.profile_id:
        raise SystemExit("--profile-id or OPENFS_SECURITY_PROFILE_ID is required")
    if not 1 <= args.workers <= 32:
        raise SystemExit("--workers must be between 1 and 32")
    if args.offline_reconcile:
        audit = reconcile_offline(args.root, read_json(args.output))
    else:
        broker = SafeWebFetchBroker.from_file(security_profile_id=args.profile_id)
        audit = build_audit(args.root, broker, args.workers)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
