#!/usr/bin/env python3
"""Verify the integrity and disclosure boundary of an OpenFS public bundle."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import sys


ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = ROOT / "PUBLICATION_MANIFEST.json"
ALLOWED_PREFIXES = (
    "assets/branding/",
    "knowledge/public/",
    "reports/exports/",
    "roadmaps/scenarios/accepted/",
    "public-site/",
)
PRIVATE_TOP_LEVEL = {
    "assessments",
    "config",
    "decisions",
    "docs",
    "evals",
    "handoffs",
    "operations",
    "proposals",
    "queue",
    "reviews",
    "runs",
    "schemas",
    "site",
    "skills",
    "state",
    "tests",
    "tools",
}
PRIVATE_REPOSITORY_MARKER = b"github.com/" + b"HPCI-CFSP/" + b"OpenFS" + b"-Control"
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


def fail(message: str) -> None:
    raise ValueError(message)


def load_manifest() -> dict:
    if not MANIFEST_PATH.is_file():
        fail("PUBLICATION_MANIFEST.json is missing")
    with MANIFEST_PATH.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def validate_path(value: str) -> str:
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        fail(f"unsafe manifest path: {value}")
    if not value.startswith(ALLOWED_PREFIXES):
        fail(f"path is outside the public allowlist: {value}")
    return value


def files_under_public_roots() -> set[str]:
    files: set[str] = set()
    for prefix in ALLOWED_PREFIXES:
        base = ROOT / prefix.rstrip("/")
        if not base.is_dir():
            fail(f"required public directory is missing: {prefix}")
        for path in base.rglob("*"):
            if path.is_symlink():
                fail(f"public bundle contains a symlink: {path.relative_to(ROOT)}")
            if path.is_file():
                files.add(path.relative_to(ROOT).as_posix())
    return files


def verify() -> None:
    manifest = load_manifest()
    if manifest.get("information_classification") != "public":
        fail("manifest classification must be public")
    if manifest.get("validation", {}).get("status") != "passed":
        fail("control-side validation did not pass")
    source = manifest.get("source", {})
    for key in ("public_input_commit", "control_commit", "migration_source_commit"):
        if not COMMIT_PATTERN.fullmatch(str(source.get(key, ""))):
            fail(f"manifest source.{key} must be a full Git commit")

    present_private = sorted(name for name in PRIVATE_TOP_LEVEL if (ROOT / name).exists())
    if present_private:
        fail("private control paths are present: " + ", ".join(present_private))

    contents = manifest.get("contents", {})
    records = contents.get("files")
    if not isinstance(records, list):
        fail("manifest contents.files must be an array")

    expected: set[str] = set()
    tree = hashlib.sha256()
    total_bytes = 0
    for record in records:
        relative = validate_path(str(record.get("path", "")))
        if relative in expected:
            fail(f"duplicate manifest path: {relative}")
        expected.add(relative)
        path = ROOT / relative
        if not path.is_file() or path.is_symlink():
            fail(f"manifest file is missing or unsafe: {relative}")
        payload = path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if len(payload) != record.get("bytes"):
            fail(f"byte count mismatch: {relative}")
        if digest != record.get("sha256"):
            fail(f"SHA-256 mismatch: {relative}")
        if PRIVATE_REPOSITORY_MARKER in payload:
            fail(f"private repository URL found in public content: {relative}")
        tree.update(relative.encode("utf-8"))
        tree.update(b"\0")
        tree.update(digest.encode("ascii"))
        tree.update(b"\n")
        total_bytes += len(payload)

    actual = files_under_public_roots()
    if expected != actual:
        missing = sorted(expected - actual)
        extra = sorted(actual - expected)
        fail(f"manifest file set mismatch; missing={missing}, extra={extra}")
    if len(records) != contents.get("file_count"):
        fail("manifest file_count mismatch")
    if total_bytes != contents.get("total_bytes"):
        fail("manifest total_bytes mismatch")
    if tree.hexdigest() != contents.get("tree_sha256"):
        fail("manifest tree_sha256 mismatch")
    if not (ROOT / "public-site" / "index.html").is_file():
        fail("public-site/index.html is missing")


def main() -> int:
    try:
        verify()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"OpenFS publication verification failed: {exc}", file=sys.stderr)
        return 1
    print("OpenFS publication verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
