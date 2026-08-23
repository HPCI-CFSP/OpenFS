#!/usr/bin/env python3
"""Compare Source observations between Runs without overstating search omissions."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json, stable_digest


ROOT = Path(__file__).resolve().parents[1]
UNAVAILABLE_STATUSES = {"unavailable", "paywalled", "blocked", "malformed"}


def content_fingerprint(result: dict[str, Any]) -> str:
    receipt = result["source_receipt"]
    retrieved_hash = receipt.get("retrieved_content_sha256")
    if retrieved_hash:
        return retrieved_hash
    passages = [
        {
            "text": item.get("text"),
            "locator": item.get("locator"),
            "passage_kind": item.get("passage_kind"),
            "candidate_claim": item.get("candidate_claim"),
        }
        for item in result.get("candidate_passages", [])
    ]
    return stable_digest(
        {
            "title": receipt.get("title"),
            "publisher": receipt.get("publisher"),
            "publication_date": receipt.get("publication_date"),
            "media_type": receipt.get("media_type"),
            "language": receipt.get("language"),
            "passages": passages,
        }
    )


def load_run_sources(root: Path, run_id: str) -> dict[str, tuple[str, dict[str, Any]]]:
    sources: dict[str, tuple[str, dict[str, Any]]] = {}
    directory = root / "proposals" / "sources" / run_id
    for path in sorted(directory.glob("*.json")):
        result = read_json(path)
        url = result["source_receipt"]["canonical_url"]
        if url in sources:
            raise ValueError(f"Run {run_id} has duplicate canonical URL: {url}")
        sources[url] = (str(path.relative_to(root)), result)
    return sources


def find_previous_run(root: Path, run_id: str) -> str | None:
    current = read_json(root / "runs" / run_id / "manifest.json")
    candidates: list[tuple[str, str]] = []
    for path in sorted((root / "runs").glob("RUN-*/manifest.json")):
        manifest = read_json(path)
        candidate_id = manifest.get("run_id")
        if candidate_id == run_id or manifest.get("status") != "completed":
            continue
        if manifest.get("task_id") != current.get("task_id"):
            continue
        if manifest.get("monitor_id") != current.get("monitor_id"):
            continue
        if manifest.get("started_at", "") >= current.get("started_at", ""):
            continue
        candidates.append((manifest.get("started_at", ""), candidate_id))
    return max(candidates)[1] if candidates else None


def compare_runs(
    root: Path,
    *,
    run_id: str,
    previous_run_id: str | None = None,
    generated_at: str | None = None,
) -> dict[str, Any]:
    previous_run_id = previous_run_id or find_previous_run(root, run_id)
    current = load_run_sources(root, run_id)
    previous = load_run_sources(root, previous_run_id) if previous_run_id else {}
    changes: list[dict[str, Any]] = []

    for url in sorted(set(current) | set(previous)):
        current_entry = current.get(url)
        previous_entry = previous.get(url)
        current_ref, current_result = current_entry if current_entry else (None, None)
        previous_ref, previous_result = previous_entry if previous_entry else (None, None)
        current_fingerprint = content_fingerprint(current_result) if current_result else None
        previous_fingerprint = content_fingerprint(previous_result) if previous_result else None
        reasons: list[str] = []

        if current_result is None:
            classification = "not-observed"
            reasons.append("The prior URL was not selected in this Run; availability was not retested")
        else:
            current_receipt = current_result["source_receipt"]
            status = current_receipt["retrieval_status"]
            if status in UNAVAILABLE_STATUSES:
                classification = "unavailable"
                reasons.append(f"Current retrieval status is {status}")
            elif previous_result is None:
                classification = "new"
                reasons.append("No matching canonical URL exists in the previous Run")
            elif current_fingerprint != previous_fingerprint:
                classification = "changed"
                reasons.append("The stable content fingerprint differs from the previous Run")
            else:
                prior_receipt = previous_result["source_receipt"]
                current_access = current_receipt["rights"]["acquisition_decision"]
                prior_access = prior_receipt["rights"]["acquisition_decision"]
                if status != prior_receipt["retrieval_status"] or current_access != prior_access:
                    classification = "changed"
                    reasons.append("Retrieval or acquisition status differs from the previous Run")
                else:
                    classification = "unchanged"
                    reasons.append("Stable content, retrieval status, and acquisition decision match")

        changes.append(
            {
                "canonical_url": url,
                "classification": classification,
                "current_source_ref": current_ref,
                "previous_source_ref": previous_ref,
                "current_fingerprint": current_fingerprint,
                "previous_fingerprint": previous_fingerprint,
                "reasons": reasons,
            }
        )

    summary = {
        name: sum(item["classification"] == name for item in changes)
        for name in ("new", "changed", "unchanged", "unavailable", "not-observed")
    }
    return {
        "schema_version": "0.1.0",
        "run_id": run_id,
        "previous_run_id": previous_run_id,
        "generated_at": generated_at or isoformat(),
        "comparison_basis": {
            "identity_key": "canonical_url",
            "preferred_fingerprint": "retrieved_content_sha256",
            "fallback_fingerprint": "stable source metadata and retained candidate passages",
        },
        "summary": summary,
        "changes": changes,
        "caveat": (
            "not-observed means only that a prior URL was not selected in this Run; "
            "it is not evidence that the source was withdrawn or became unavailable."
        ),
    }


def write_report(root: Path, report: dict[str, Any], output: Path | None = None) -> Path:
    path = output or Path("runs") / report["run_id"] / "changes.json"
    if not path.is_absolute():
        path = root / path
    try:
        report_ref = str(path.relative_to(root))
    except ValueError as exc:
        raise ValueError("Change report output must be inside the repository") from exc
    atomic_write_json(path, report)
    manifest_path = root / "runs" / report["run_id"] / "manifest.json"
    manifest = read_json(manifest_path)
    manifest["previous_run_id"] = report["previous_run_id"]
    manifest["change_report_ref"] = report_ref
    manifest.setdefault("metrics", {})["source_changes"] = report["summary"]
    atomic_write_json(manifest_path, manifest)
    return path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--previous-run-id")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = compare_runs(
        args.root, run_id=args.run_id, previous_run_id=args.previous_run_id
    )
    output = write_report(args.root, report, args.output)
    print(json.dumps({"output": str(output), "summary": report["summary"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
