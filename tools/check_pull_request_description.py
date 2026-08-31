#!/usr/bin/env python3
"""Reject placeholder pull-request titles and descriptions."""

from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from typing import Any


REQUIRED_HEADINGS = (
    "## Purpose",
    "## Provenance",
    "## Boundary and risk",
    "## Validation",
    "## Review notes",
)
PLACEHOLDER_PHRASES = (
    "Describe the work item and expected outcome.",
    "State the user-visible problem, the chosen change, and the expected outcome.",
    "Delete this guidance and write the concrete purpose before requesting review.",
    "<!-- required -->",
    "<!-- required for public or canonical changes -->",
    "<!-- use N/A only",
    "<!-- list each",
    "<!-- full SHA -->",
    "変更の背景、具体的な変更内容、期待する結果を記載してください。",
    "この案内は削除し、上の英語版と同じ内容を記載してください。",
)
REQUIRED_CHECKS = (
    "Public information only",
    "No secrets, personal data, or private run logs",
    "External content was treated as untrusted data",
    "Changed paths pass `tools/check_agent_permissions.py` for the declared role",
    "Canonical changes are covered by a human Directive or an authorized promotion workflow",
    "`python3 tools/validate_repository.py`",
    "`python3 -m unittest discover -s tests -v`",
    "Dissent and unresolved exceptions are linked",
    "Coverage Gaps and provisional/Consensus state are visible",
    "Rollback or supersession path is described below",
)
REQUIRED_PROVENANCE_LABELS = (
    "Agent ID / role, or human maintainer",
    "Human Directive ID(s)",
    "Task / Monitor / Work Item IDs",
    "Run ID",
    "Proposal / Assessment / Decision IDs",
    "Base commit",
)
REQUIRED_REVIEW_LABELS = (
    "Coverage Gaps / dissent",
    "Security-boundary effect",
    "Rollback or supersession path",
    "Pages paths to inspect",
)
JAPANESE_HEADINGS = ("## 目的", "## 来歴", "## 情報境界とリスク", "## 検証", "## レビュー事項")
JAPANESE_PROVENANCE_LABELS = (
    "担当エージェント・役割または担当者", "Human Directive ID", "Task・Monitor・Work Item ID",
    "Run ID", "Proposal・Assessment・Decision ID", "基点コミット",
)
JAPANESE_REVIEW_LABELS = ("Coverage Gap・異論", "セキュリティ境界への影響", "復旧・後続版への移行方法", "確認するPagesのパス")
JAPANESE_CHECKS = (
    "公開情報のみ", "秘密情報・個人情報・非公開の実行ログを含まない", "外部コンテンツを信頼できないデータとして扱った",
    "変更パスは宣言した役割で `tools/check_agent_permissions.py` を通過した",
    "正規データの変更はHuman Directiveまたは承認された昇格ワークフローに基づく",
    "`python3 tools/validate_repository.py`", "`python3 -m unittest discover -s tests -v`",
    "異論・未解決事項を参照できる", "Coverage Gapと暫定・Consensusの状態を明示した", "復旧・後続版への移行方法を以下に記載した",
)


def language_blocks(body: str) -> tuple[dict[str, str], list[str]]:
    headings = list(re.finditer(r"^# (English|日本語)[ \t]*$", body, re.MULTILINE))
    if [m.group(1) for m in headings] != ["English", "日本語"]:
        return {}, ["include exactly one '# English' block followed by one '# 日本語' block"]
    blocks = {"en": body[headings[0].end():headings[1].start()], "ja": body[headings[1].end():]}
    errors = []
    for language, content in blocks.items():
        prose = re.sub(r"^#+.*$", "", content, flags=re.MULTILINE).strip()
        if not prose:
            errors.append(f"empty language block: {language}")
        elif language == "ja" and not re.search(r"[ぁ-んァ-ヶ一-龠]", prose):
            errors.append("Japanese block needs Japanese prose, not a copied English block")
    return blocks, errors


def validate_bilingual_comment(body: str) -> list[str]:
    """Check format only; translation meaning and factual claims need review."""
    return language_blocks(body)[1]


def section(body: str, heading: str) -> str:
    match = re.search(rf"^{re.escape(heading)}[ \t]*\n(.*?)(?=^#{{1,2}} |\Z)", body, re.MULTILINE | re.DOTALL)
    return match.group(1).strip() if match else ""


def _value_after_label(body: str, label: str) -> str | None:
    match = re.search(
        rf"^[ \t]*-[ \t]*{re.escape(label)}[ \t]*:[ \t]*(.*?)[ \t]*$",
        body,
        flags=re.MULTILINE,
    )
    return match.group(1).strip() if match else None


def validate_pull_request(payload: dict[str, Any]) -> list[str]:
    pull_request = payload.get("pull_request", payload)
    title = str(pull_request.get("title", "")).strip()
    body = str(pull_request.get("body") or "")
    errors: list[str] = []
    blocks, language_errors = language_blocks(body)
    errors.extend(language_errors)
    english = blocks.get("en", body)
    japanese = blocks.get("ja", "")

    if not title:
        errors.append("pull-request title is empty")
    normalized_title = re.sub(r"[-_/]+", " ", title).strip().lower()
    if normalized_title in {
        "maintainer system planning security",
        "update",
        "openfs update",
    }:
        errors.append("pull-request title is a generic branch-derived title")

    if len(body.strip()) < 400:
        errors.append("pull-request description is too short to record the required review context")
    for heading in REQUIRED_HEADINGS:
        if not section(english, heading):
            errors.append(f"missing required heading: {heading}")
    for phrase in PLACEHOLDER_PHRASES:
        if phrase in body:
            errors.append(f"template guidance remains in description: {phrase}")

    for label in (*REQUIRED_PROVENANCE_LABELS, *REQUIRED_REVIEW_LABELS):
        value = _value_after_label(english, label)
        if value is None:
            errors.append(f"missing required field: {label}")
        elif not value:
            errors.append(f"required field is empty: {label}")

    base_commit = _value_after_label(english, "Base commit") or ""
    if not re.search(r"\b[0-9a-f]{40}\b", base_commit):
        errors.append("Base commit must contain a full 40-character commit SHA")

    for label in REQUIRED_CHECKS:
        checked = re.search(
            rf"^\s*-\s*\[[xX]\]\s*{re.escape(label)}\s*$",
            english,
            flags=re.MULTILINE,
        )
        if not checked:
            errors.append(f"required completed check is missing: {label}")
    for heading in JAPANESE_HEADINGS:
        if not section(japanese, heading):
            errors.append(f"missing required Japanese section: {heading}")
    for label in (*JAPANESE_PROVENANCE_LABELS, *JAPANESE_REVIEW_LABELS):
        if not _value_after_label(japanese, label):
            errors.append(f"missing or empty Japanese field: {label}")
    for label in JAPANESE_CHECKS:
        if not re.search(rf"^\s*-\s*\[[xX]\]\s*{re.escape(label)}\s*$", japanese, re.MULTILINE):
            errors.append(f"required completed Japanese check is missing: {label}")
    japanese_base = _value_after_label(japanese, "基点コミット") or ""
    if re.findall(r"\b[0-9a-f]{40}\b", base_commit) != re.findall(r"\b[0-9a-f]{40}\b", japanese_base):
        errors.append("English and Japanese base commit SHAs differ")
    id_pattern = r"\b(?:DIR|RUN|MON|OFS|WI|RUP|PRP|PROP|ASM|ASMT|DEC|PUBDEC|CLM)-[A-Z0-9-]+\b"
    if set(re.findall(id_pattern, section(english, "## Provenance"))) != set(re.findall(id_pattern, section(japanese, "## 来歴"))):
        errors.append("English and Japanese provenance IDs differ")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--event", type=Path)
    inputs.add_argument("--body", type=Path, help="Validate a local PR body before posting")
    inputs.add_argument("--comment", type=Path, help="Check an English-first bilingual PR comment")
    parser.add_argument("--title")
    args = parser.parse_args()
    if args.comment:
        errors = validate_bilingual_comment(args.comment.read_text(encoding="utf-8"))
    elif args.body:
        if not args.title:
            parser.error("--title is required with --body")
        errors = validate_pull_request({"title": args.title, "body": args.body.read_text(encoding="utf-8")})
    else:
        event_path = args.event or Path(os.environ.get("GITHUB_EVENT_PATH", ""))
        if not event_path.is_file():
            raise SystemExit("GitHub pull-request event JSON is required")
        errors = validate_pull_request(json.loads(event_path.read_text(encoding="utf-8")))
    if errors:
        print("Pull-request description validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Pull-request bilingual format is complete; semantic equivalence still requires review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
