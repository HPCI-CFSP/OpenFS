#!/usr/bin/env python3
"""Check for or create the single open OpenFS Handoff control pull request."""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

from automation_pr_description import prepare_body
from check_pull_request_description import validate_pull_request


REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def _request(repository: str, token: str, method: str, endpoint: str, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}{endpoint}",
        data=data,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "OpenFS-handoff-control",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def find_open(repository: str, token: str, *, base: str) -> dict[str, Any] | None:
    owner = repository.split("/", 1)[0]
    query = urllib.parse.urlencode(
        {"state": "open", "base": base, "per_page": 100}
    )
    pulls = _request(repository, token, "GET", f"/pulls?{query}")
    for pull in pulls:
        if (
            pull.get("head", {}).get("user", {}).get("login") == owner
            and pull.get("head", {}).get("ref", "").startswith(
                "automation/handoff-control-"
            )
        ):
            return pull
    return None


def create(
    repository: str,
    token: str,
    *,
    head: str,
    base: str,
    summary: dict[str, Any],
    prepared_description: tuple[str, str] | None = None,
) -> dict[str, Any]:
    existing = find_open(repository, token, base=base)
    if existing:
        return {
            "status": "blocked-by-existing",
            "number": existing["number"],
            "url": existing["html_url"],
        }
    if prepared_description is None:
        raise ValueError("a validated bilingual PR description is required")
    title, body = prepared_description
    if errors := validate_pull_request({"title": title, "body": body}):
        raise ValueError("; ".join(errors))
    pull = _request(
        repository,
        token,
        "POST",
        "/pulls",
        {
            "title": title,
            "head": head,
            "base": base,
            "body": body,
        },
    )
    return {"status": "created", "number": pull["number"], "url": pull["html_url"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--token-env", default="GITHUB_TOKEN")
    parser.add_argument("--base", default="main")
    parser.add_argument("--head")
    parser.add_argument("--summary")
    parser.add_argument("--base-commit", default=os.environ.get("GITHUB_SHA"))
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    if not args.repository or not REPOSITORY.fullmatch(args.repository):
        raise ValueError("repository must have owner/name form")
    token = os.environ.get(args.token_env)
    if not token:
        raise RuntimeError(f"missing token environment variable: {args.token_env}")
    existing = find_open(args.repository, token, base=args.base)
    if args.check_only:
        print(
            json.dumps(
                {
                    "existing": existing is not None,
                    "number": existing.get("number") if existing else None,
                    "url": existing.get("html_url") if existing else None,
                }
            )
        )
        return 0
    if not args.head or not args.summary:
        raise ValueError("--head and --summary are required when creating a PR")
    summary = json.loads(open(args.summary, encoding="utf-8").read())
    description = prepare_body(Path(__file__).resolve().parents[1], "control", summary,
                               args.base_commit or "", args.head)
    print(
        json.dumps(
            create(
                args.repository,
                token,
                head=args.head,
                base=args.base,
                summary=summary,
                prepared_description=description,
            )
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
