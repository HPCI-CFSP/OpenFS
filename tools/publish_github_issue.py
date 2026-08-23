#!/usr/bin/env python3
"""Publish one sanitized, deduplicated OpenFS Issue payload through GitHub's API."""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
from pathlib import Path
from typing import Any, Callable

from openfs_runtime import read_json


REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
Request = Callable[[str, str, dict[str, Any] | None], Any]


def _request_factory(repository: str, token: str) -> Request:
    base = f"https://api.github.com/repos/{repository}"

    def request(method: str, endpoint: str, body: dict[str, Any] | None = None):
        data = json.dumps(body).encode("utf-8") if body is not None else None
        request_object = urllib.request.Request(
            base + endpoint,
            data=data,
            method=method,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "OpenFS-weekly-coordinator",
            },
        )
        with urllib.request.urlopen(request_object, timeout=30) as response:
            return json.load(response)

    return request


def publish(payload: dict[str, Any], *, request: Request) -> dict[str, Any]:
    issue = payload.get("issue", payload)
    marker = issue["deduplication_marker"]
    existing = request(
        "GET", "/issues?state=all&per_page=100&sort=created&direction=desc", None
    )
    for item in existing:
        if marker in item.get("body", ""):
            return {
                "publication_status": "existing",
                "github_issue_number": item["number"],
                "github_issue_url": item["html_url"],
            }
    available_labels = {
        item["name"] for item in request("GET", "/labels?per_page=100", None)
    }
    created = request(
        "POST",
        "/issues",
        {
            "title": issue["title"][:256],
            "body": issue["body"],
            "labels": [name for name in issue.get("labels", []) if name in available_labels],
        },
    )
    return {
        "publication_status": "created",
        "github_issue_number": created["number"],
        "github_issue_url": created["html_url"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--payload", required=True, type=Path)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    args = parser.parse_args()
    if not args.repository or not REPOSITORY.fullmatch(args.repository):
        raise ValueError("repository must have owner/name form")
    token = os.environ.get(args.token_env)
    if not token:
        raise RuntimeError(f"missing token environment variable: {args.token_env}")
    result = publish(
        read_json(args.payload), request=_request_factory(args.repository, token)
    )
    print(json.dumps(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
