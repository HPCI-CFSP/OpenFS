#!/usr/bin/env python3
"""Prepare a verified Pages artifact with deployment-time public provenance."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil


COMMIT = re.compile(r"^[0-9a-f]{40}$")
RUN_ID = re.compile(r"^[1-9][0-9]*$")


def require_commit(value: str, label: str) -> str:
    if not COMMIT.fullmatch(value):
        raise ValueError(f"{label} must be a lowercase 40-hex Git commit")
    return value


def require_run_id(value: str) -> str:
    if not RUN_ID.fullmatch(value):
        raise ValueError("workflow run ID must contain decimal digits")
    return value


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as stream:
        return json.load(stream)


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as stream:
        json.dump(payload, stream, ensure_ascii=False, indent=2)
        stream.write("\n")


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def prepare(args: argparse.Namespace) -> dict:
    manifest = load_json(args.manifest)
    source = manifest.get("source", {})
    public_input = require_commit(str(source.get("public_input_commit", "")), "public input commit")
    control_commit = require_commit(str(source.get("control_commit", "")), "control commit")
    public_commit = require_commit(args.public_commit, "public repository commit")
    workflow_run_id = require_run_id(args.workflow_run_id)
    public_repository = str(source.get("public_repository", "")).rstrip("/")
    if public_repository != "https://github.com/HPCI-CFSP/OpenFS":
        raise ValueError("unexpected public repository URL in publication manifest")
    site = args.site.resolve()
    output = args.output.resolve()
    if (
        not site.is_dir()
        or site == output
        or site in output.parents
        or output in site.parents
    ):
        raise ValueError("site input must be a directory distinct from output")
    if args.output.exists():
        raise ValueError("output already exists; use a new disposable directory")
    shutil.copytree(args.site, args.output)
    shutil.copy2(args.manifest, args.output / "publication-manifest.json")

    preview = args.mode == "preview"
    payload = {
        "schema_version": "0.1.0",
        "bundle_id": manifest["bundle_id"],
        "generated_at": manifest["generated_at"],
        "manifest_url": "../publication-manifest.json",
        "public_input": {
            "commit": public_input,
            "commit_url": f"{public_repository}/commit/{public_input}",
        },
        "control_generation": {
            "commit": control_commit,
            "repository_visibility": "private",
        },
        "public_repository": {
            "commit": public_commit,
            "commit_url": f"{public_repository}/commit/{public_commit}",
            "status": "preview-source" if preview else "published-source",
        },
        "pages_deployment": {
            "status": "preview-artifact" if preview else "serving-this-artifact",
            "source_commit": public_commit,
            "workflow_run_id": workflow_run_id,
            "workflow_run_url": f"{public_repository}/actions/runs/{workflow_run_id}",
            "artifact_built_at": utc_now(),
        },
    }
    write_json(args.output / "data" / "openfs-deployment.json", payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=Path("PUBLICATION_MANIFEST.json"))
    parser.add_argument("--site", type=Path, default=Path("public-site"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mode", choices=("preview", "production"), required=True)
    parser.add_argument("--public-commit", default=os.environ.get("GITHUB_SHA", ""))
    parser.add_argument("--workflow-run-id", default=os.environ.get("GITHUB_RUN_ID", ""))
    args = parser.parse_args()
    payload = prepare(args)
    print(
        "Prepared Pages artifact: "
        f"mode={args.mode}, commit={payload['public_repository']['commit']}, "
        f"run={payload['pages_deployment']['workflow_run_id']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
