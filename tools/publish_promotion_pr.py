#!/usr/bin/env python3
"""Check for or create the single open OpenFS Claim promotion pull request."""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.parse
from pathlib import Path
from typing import Any

from publish_control_pr import _request


REPOSITORY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
BRANCH_PREFIX = "automation/claim-promotion-"


def find_open(repository: str, token: str, *, base: str) -> dict[str, Any] | None:
    owner = repository.split("/", 1)[0]
    query = urllib.parse.urlencode({"state": "open", "base": base, "per_page": 100})
    pulls = _request(repository, token, "GET", f"/pulls?{query}")
    for pull in pulls:
        if (
            pull.get("head", {}).get("user", {}).get("login") == owner
            and pull.get("head", {}).get("ref", "").startswith(BRANCH_PREFIX)
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
) -> dict[str, Any]:
    existing = find_open(repository, token, base=base)
    if existing:
        return {
            "status": "blocked-by-existing",
            "number": existing["number"],
            "url": existing["html_url"],
        }
    claims = ", ".join(
        f"`{item['canonical_claim_id']}`" for item in summary["prepared"]
    )
    runs = ", ".join(f"`{item}`" for item in summary["affected_run_ids"])
    body = "\n".join(
        [
            "<!-- openfs-claim-promotion -->",
            "",
            "Canonical Claim changes prepared from accepted Decisions and rechecked controls.",
            "",
            f"- Claims: {claims or 'none'}",
            f"- Source Runs: {runs or 'none'}",
            "",
            "This pull request does not contain Recommendations, auto-merge, or Pages publication. "
            "Review the pinned Proposal, Decision, Evidence, Policy, and dependency reports before merge.",
        ]
    )
    pull = _request(
        repository,
        token,
        "POST",
        "/pulls",
        {
            "title": "Promote accepted OpenFS Claims",
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
    parser.add_argument("--summary", type=Path)
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
    print(
        json.dumps(
            create(
                args.repository,
                token,
                head=args.head,
                base=args.base,
                summary=json.loads(args.summary.read_text(encoding="utf-8")),
            )
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
