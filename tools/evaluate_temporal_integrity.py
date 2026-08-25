#!/usr/bin/env python3
"""Check that recorded Run events fall inside the Run's auditable time window."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from openfs_runtime import atomic_write_json, isoformat, read_json


ROOT = Path(__file__).resolve().parents[1]
MAXIMUM_CLOCK_SKEW_SECONDS = 60
EVENT_KEYS = {
    "acquired_at",
    "completed_at",
    "created_at",
    "decided_at",
    "executed_at",
    "expanded_at",
    "extracted_at",
    "generated_at",
    "recorded_at",
    "retrieved_at",
    "reviewed_at",
    "started_at",
    "updated_at",
}


def _time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def _events(value: Any, *, pointer: str = "$") -> list[tuple[str, str, str]]:
    found: list[tuple[str, str, str]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            child_pointer = f"{pointer}.{key}"
            if key in EVENT_KEYS and isinstance(child, str):
                found.append((child_pointer, key, child))
            found.extend(_events(child, pointer=child_pointer))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(_events(child, pointer=f"{pointer}[{index}]"))
    return found


def evaluate(
    root: Path,
    *,
    run_id: str,
    evaluated_at: str | None = None,
    maximum_clock_skew_seconds: int = MAXIMUM_CLOCK_SKEW_SECONDS,
) -> dict[str, Any]:
    manifest_path = root / "runs" / run_id / "manifest.json"
    manifest = read_json(manifest_path)
    evaluated = _time(evaluated_at) if evaluated_at else datetime.now(timezone.utc)
    started = _time(manifest["started_at"])
    upper_value = manifest.get("completed_at") or isoformat(evaluated)
    upper = _time(upper_value)
    skew = timedelta(seconds=maximum_clock_skew_seconds)
    documents: list[tuple[str, dict[str, Any]]] = [
        (str(manifest_path.relative_to(root)), manifest)
    ]
    for work_path in sorted((root / "queue" / run_id).glob("WORK-*.json")):
        work_item = read_json(work_path)
        documents.append((str(work_path.relative_to(root)), work_item))
        for output_ref in work_item.get("output_refs", []):
            output_path = root / output_ref
            if output_path.is_file():
                documents.append((output_ref, read_json(output_path)))

    anomalies: list[dict[str, Any]] = []
    observation_count = 0
    seen: set[tuple[str, str, str]] = set()
    for document_ref, document in documents:
        for pointer, key, value in _events(document):
            identity = (document_ref, pointer, value)
            if identity in seen:
                continue
            seen.add(identity)
            observation_count += 1
            try:
                observed = _time(value)
            except ValueError:
                anomalies.append(
                    {
                        "document_ref": document_ref,
                        "pointer": pointer,
                        "event_key": key,
                        "value": value,
                        "reason": "invalid-date-time",
                        "offset_seconds": None,
                    }
                )
                continue
            if observed < started - skew:
                anomalies.append(
                    {
                        "document_ref": document_ref,
                        "pointer": pointer,
                        "event_key": key,
                        "value": value,
                        "reason": "before-run-window",
                        "offset_seconds": round((observed - started).total_seconds(), 6),
                    }
                )
            elif observed > upper + skew:
                anomalies.append(
                    {
                        "document_ref": document_ref,
                        "pointer": pointer,
                        "event_key": key,
                        "value": value,
                        "reason": "after-run-window",
                        "offset_seconds": round((observed - upper).total_seconds(), 6),
                    }
                )
    return {
        "schema_version": "0.1.0",
        "run_id": run_id,
        "evaluated_at": isoformat(evaluated),
        "status": "failed" if anomalies else "passed",
        "publication_blocked": bool(anomalies),
        "window": {
            "started_at": manifest["started_at"],
            "ended_at": upper_value,
            "maximum_clock_skew_seconds": maximum_clock_skew_seconds,
        },
        "observation_count": observation_count,
        "anomaly_count": len(anomalies),
        "anomalies": anomalies,
    }


def record(root: Path, report: dict[str, Any]) -> dict[str, Any]:
    run_id = report["run_id"]
    report_ref = f"runs/{run_id}/temporal-integrity.json"
    atomic_write_json(root / report_ref, report)
    manifest_path = root / "runs" / run_id / "manifest.json"
    manifest = read_json(manifest_path)
    manifest["temporal_integrity_ref"] = report_ref
    manifest.setdefault("metrics", {})["temporal_integrity"] = {
        "status": report["status"],
        "anomaly_count": report["anomaly_count"],
        "publication_blocked": report["publication_blocked"],
    }
    atomic_write_json(manifest_path, manifest)
    exception_path = root / "reviews" / "exceptions" / run_id / "TEMPORAL-INTEGRITY.json"
    if report["status"] == "failed":
        atomic_write_json(
            exception_path,
            {
                "schema_version": "0.1.0",
                "exception_id": f"EXC-{run_id}-TEMPORAL-INTEGRITY",
                "run_id": run_id,
                "status": "open",
                "recorded_at": report["evaluated_at"],
                "exception_kind": "temporal-integrity",
                "report_ref": report_ref,
                "anomaly_count": report["anomaly_count"],
                "publication_blocked": True,
                "requires_owner_action": True,
            },
        )
    elif exception_path.is_file():
        exception = read_json(exception_path)
        exception["status"] = "resolved"
        exception["resolved_at"] = report["evaluated_at"]
        exception["publication_blocked"] = False
        atomic_write_json(exception_path, exception)
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--evaluated-at")
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    report = evaluate(args.root, run_id=args.run_id, evaluated_at=args.evaluated_at)
    record(args.root, report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["status"] == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
