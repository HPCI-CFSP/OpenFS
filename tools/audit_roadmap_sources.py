#!/usr/bin/env python3
"""Check public roadmap source URLs without retaining source contents."""

from __future__ import annotations

import argparse
import json
import ssl
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "knowledge" / "public" / "audits" / "roadmap-source-audit.json"
USER_AGENT = "OpenFS public-source-audit/0.1 (+https://github.com/HPCI-CFSP/OpenFS)"


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


def check_source(source: dict[str, Any], timeout: float) -> dict[str, Any]:
    request = urllib.request.Request(
        source["url"],
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/pdf,*/*;q=0.8"},
        method="GET",
    )
    status: int | None = None
    final_url = source["url"]
    content_type: str | None = None
    error_kind: str | None = None
    error_detail: str | None = None
    try:
        context = ssl.create_default_context()
        with urllib.request.urlopen(request, timeout=timeout, context=context) as response:
            status = response.status
            final_url = response.geturl()
            content_type = response.headers.get_content_type()
            response.read(1024)
    except urllib.error.HTTPError as exc:
        status = exc.code
        final_url = exc.geturl()
        content_type = exc.headers.get_content_type() if exc.headers else None
        error_kind = "http"
        error_detail = str(exc.reason)[:240]
    except TimeoutError as exc:
        error_kind = "timeout"
        error_detail = str(exc)[:240]
    except urllib.error.URLError as exc:
        reason = getattr(exc, "reason", exc)
        error_kind = "timeout" if isinstance(reason, TimeoutError) else "network"
        error_detail = str(reason)[:240]
    except Exception as exc:  # pragma: no cover - defensive boundary for remote servers
        error_kind = "unexpected"
        error_detail = f"{type(exc).__name__}: {exc}"[:240]

    result: dict[str, Any] = {
        **source,
        "status": classify(status, error_kind),
        "http_status": status,
        "final_url": final_url,
        "content_type": content_type,
    }
    if error_kind:
        result["error_kind"] = error_kind
    if error_detail:
        result["error_detail"] = error_detail
    return result


def build_audit(root: Path, timeout: float, workers: int) -> dict[str, Any]:
    checked_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    as_of = datetime.now(timezone(timedelta(hours=9))).date().isoformat()
    sources = collect_sources(root)
    results: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(check_source, source, timeout): source for source in sources
        }
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: (item["roadmap_id"], item["source_id"]))
    summary = {
        status: sum(result["status"] == status for result in results)
        for status in ("reachable", "access-restricted", "missing", "timeout", "error")
    }
    source_class_counts = Counter(source["source_class"] for source in sources)
    unique_urls = {source["url"] for source in sources}
    unique_external_urls = {
        source["url"]
        for source in sources
        if source["source_class"] != "openfs-governance"
    }
    return {
        "schema_version": "0.1.0",
        "export_id": "ROADMAP-SOURCE-AUDIT-001",
        "status": "published",
        "audit_id": f"RSA-{as_of.replace('-', '')}-001",
        "as_of": as_of,
        "checked_at": checked_at,
        "method": "HTTP GET with redirects; first 1 KiB read; source contents are not retained",
        "method_ja": "公開URLへリダイレクト追随GETを行い、先頭1KiBのみ取得した。本文は保存しない。",
        "method_en": "Follow redirects with HTTP GET and read only the first 1 KiB; source contents are not retained.",
        "caveat_ja": "到達性は機械クライアントの結果であり、主張の正しさを示さない。403、429、timeout等はブラウザで有効な資料でも発生し得る。",
        "caveat_en": "Reachability reflects one machine client and does not validate a claim. A valid browser-accessible source may still return 403, 429, or a timeout.",
        "user_agent": USER_AGENT,
        "summary": {
            "source_count": len(results),
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
            **summary,
        },
        "results": results,
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
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--timeout", type=float, default=20.0)
    parser.add_argument("--workers", type=int, default=8)
    args = parser.parse_args()
    audit = build_audit(args.root, args.timeout, args.workers)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(audit["summary"], ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
