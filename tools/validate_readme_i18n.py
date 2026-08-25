#!/usr/bin/env python3
"""Validate structural and change parity for the English and Japanese READMEs."""

from __future__ import annotations

import argparse
import re
import subprocess
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README_EN = ROOT / "README.md"
README_JA = ROOT / "README.ja.md"
EXPECTED_SECTIONS = [
    "overview",
    "status",
    "core-principles",
    "repository-map",
    "research-baseline",
    "local-validation",
    "human-directions",
    "license",
]
SECTION_PATTERN = re.compile(
    r"^<!-- i18n-section: ([a-z0-9-]+) -->$", re.MULTILINE
)
LINK_PATTERN = re.compile(r"!?(?:\[[^\]]*\])\(([^)]+)\)")
INLINE_CODE_PATTERN = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
FENCE_PATTERN = re.compile(r"^```([^\n]*)\n(.*?)^```$", re.MULTILINE | re.DOTALL)


def section_ids(text: str) -> list[str]:
    return SECTION_PATTERN.findall(text)


def sections(text: str) -> dict[str, str]:
    matches = list(SECTION_PATTERN.finditer(text))
    return {
        match.group(1): text[
            match.end() : matches[index + 1].start()
            if index + 1 < len(matches)
            else len(text)
        ].strip()
        for index, match in enumerate(matches)
    }


def markdown_shape(text: str) -> dict[str, object]:
    fences = FENCE_PATTERN.findall(text)
    without_fences = FENCE_PATTERN.sub("", text)
    paragraphs = [
        block
        for block in re.split(r"\n\s*\n", without_fences)
        if block.strip()
        and not block.lstrip().startswith("<!--")
    ]
    return {
        "headings": [
            len(match.group(1))
            for match in re.finditer(r"^(#{1,6})\s+", without_fences, re.MULTILINE)
        ],
        "list_items": len(re.findall(r"^-\s+", without_fences, re.MULTILINE)),
        "table_rows": len(re.findall(r"^\|.*\|$", without_fences, re.MULTILINE)),
        "fence_languages": [language.strip() for language, _body in fences],
        "paragraphs": len(paragraphs),
    }


def link_targets(text: str) -> Counter[str]:
    ignored = {"README.md", "README.ja.md"}
    return Counter(
        target for target in LINK_PATTERN.findall(text) if target not in ignored
    )


def inline_code_tokens(text: str) -> Counter[str]:
    without_fences = FENCE_PATTERN.sub("", text)
    return Counter(INLINE_CODE_PATTERN.findall(without_fences))


def executable_blocks(text: str) -> list[tuple[str, str]]:
    return [
        (language.strip(), body.strip())
        for language, body in FENCE_PATTERN.findall(text)
        if language.strip() in {"bash", "sh", "shell", "console"}
    ]


def validate_pair(english: str, japanese: str) -> list[str]:
    errors: list[str] = []
    english_ids = section_ids(english)
    japanese_ids = section_ids(japanese)
    if english_ids != EXPECTED_SECTIONS:
        errors.append(f"README.md section order is invalid: {english_ids}")
    if japanese_ids != EXPECTED_SECTIONS:
        errors.append(f"README.ja.md section order is invalid: {japanese_ids}")
    if english_ids != japanese_ids:
        errors.append("README section IDs or order differ between languages")
    if "**English** | [日本語](README.ja.md)" not in english:
        errors.append("README.md lacks the language switcher")
    if "[English](README.md) | **日本語**" not in japanese:
        errors.append("README.ja.md lacks the language switcher")

    english_badges = [line for line in english.splitlines() if line.startswith("[![")]
    japanese_badges = [line for line in japanese.splitlines() if line.startswith("[![")]
    if english_badges != japanese_badges:
        errors.append("README badges differ between languages")
    if link_targets(english) != link_targets(japanese):
        errors.append("README link targets differ between languages")
    if inline_code_tokens(english) != inline_code_tokens(japanese):
        errors.append("README inline code, paths, or identifiers differ between languages")
    if executable_blocks(english) != executable_blocks(japanese):
        errors.append("README executable examples differ between languages")

    english_sections = sections(english)
    japanese_sections = sections(japanese)
    for section_id in EXPECTED_SECTIONS:
        if not english_sections.get(section_id) or not japanese_sections.get(section_id):
            errors.append(f"README section {section_id} is empty in one language")
            continue
        if markdown_shape(english_sections[section_id]) != markdown_shape(
            japanese_sections[section_id]
        ):
            errors.append(f"README structure differs in section {section_id}")
    return errors


def validate_changed_paths(paths: set[str]) -> list[str]:
    readme_changes = paths & {"README.md", "README.ja.md"}
    if readme_changes and readme_changes != {"README.md", "README.ja.md"}:
        return [
            "README.md and README.ja.md must be changed together in the same PR"
        ]
    return []


def changed_paths(base: str, head: str) -> set[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", base, head, "--", "README.md", "README.ja.md"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return {line for line in result.stdout.splitlines() if line}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Base Git revision for paired-change validation")
    parser.add_argument("--head", help="Head Git revision for paired-change validation")
    args = parser.parse_args()
    if bool(args.base) != bool(args.head):
        parser.error("--base and --head must be supplied together")

    errors = validate_pair(
        README_EN.read_text(encoding="utf-8"),
        README_JA.read_text(encoding="utf-8"),
    )
    if args.base and args.head:
        errors.extend(validate_changed_paths(changed_paths(args.base, args.head)))
    if errors:
        for error in errors:
            print(f"README i18n validation error: {error}")
        return 1
    print("Bilingual README validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
