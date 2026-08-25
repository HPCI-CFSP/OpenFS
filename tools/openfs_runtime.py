#!/usr/bin/env python3
"""Shared dependency-free runtime helpers for OpenFS control-plane tools."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def canonical_json(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_digest(value: Any) -> str:
    return sha256_bytes(canonical_json(value))


def manifest_control_digest(manifest: dict[str, Any]) -> str:
    """Hash immutable Run controls while allowing concurrent progress updates."""
    control_keys = (
        "schema_version",
        "run_id",
        "task_id",
        "monitor_id",
        "mode",
        "base_commit",
        "started_at",
        "assignment_contract_version",
        "policy_hashes",
        "configuration_snapshots",
        "skill_snapshots",
        "budget",
        "directive_ids",
        "directive_hashes",
        "directive_snapshots",
        "run_identity_hash",
    )
    return stable_digest({key: manifest.get(key) for key in control_keys})


def exception_group_key(exception: dict[str, Any]) -> tuple[str, tuple[str, ...], bool]:
    """Return the stable owner-action grouping dimensions for an Exception."""
    kind = exception.get(
        "exception_kind", exception.get("error", {}).get("kind", "work-item-failure")
    )
    return (
        kind,
        tuple(sorted(exception.get("unmet_requirements", []))),
        bool(exception.get("publication_blocked", False)),
    )


def language_in_scope(language: str | None, allowed_languages: list[str]) -> bool:
    """Accept an explicit language or any native language under source-language mode."""
    return bool(language) and (
        language in allowed_languages or "source-language" in allowed_languages
    )


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def isoformat(value: datetime | None = None) -> str:
    return (value or utc_now()).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rendered = json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            stream.write(rendered)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def git_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "unavailable"


def run_snapshot_path(root: Path, run_id: str, source_ref: str) -> Path:
    manifest = read_json(root / "runs" / run_id / "manifest.json")
    snapshot_ref = manifest.get("configuration_snapshots", {}).get(source_ref)
    if not snapshot_ref:
        raise ValueError(f"Run has no pinned configuration snapshot: {source_ref}")
    path = root / snapshot_ref
    if not path.is_file():
        raise ValueError(f"Pinned configuration snapshot is missing: {snapshot_ref}")
    return path
