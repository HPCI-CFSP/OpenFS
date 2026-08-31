"""Prepare bilingual review context for trusted, deterministic PR publishers."""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

from check_agent_permissions import check_paths, load_config, normalize_repository_path
from check_pull_request_description import (
    JAPANESE_CHECKS, JAPANESE_PROVENANCE_LABELS, JAPANESE_REVIEW_LABELS,
    REQUIRED_CHECKS, REQUIRED_PROVENANCE_LABELS, REQUIRED_REVIEW_LABELS,
    validate_pull_request,
)


def identifiers(values: list[str]) -> str:
    if any(not re.fullmatch(r"[A-Z][A-Z0-9-]+", value) for value in values):
        raise ValueError("automation PR identifiers must be plain machine IDs")
    return ", ".join(f"`{value}`" for value in sorted(set(values))) or "N/A"


def references(values: list[str]) -> str:
    for value in values:
        normalize_repository_path(value)
        if not re.fullmatch(r"[A-Za-z0-9_./-]+", value):
            raise ValueError("automation PR references must be repository paths")
    return ", ".join(f"`{value}`" for value in sorted(set(values))) or "N/A"


def format_body(kind: str, summary: dict, base_commit: str) -> tuple[str, str]:
    if not re.fullmatch(r"[0-9a-f]{40}", base_commit):
        raise ValueError("a full base commit SHA is required")
    runs = identifiers(summary["affected_run_ids"])
    if kind == "control":
        if not summary["accepted_handoff_refs"]:
            raise ValueError("control PR needs at least one accepted Handoff")
        title = "Accept merged OpenFS agent handoffs"
        role = "openfs-control[bot] / orchestrator"
        refs = references(summary["accepted_handoff_refs"])
        work = identifiers([wid for expansion in summary.get("expansions", [])
                            for wid in expansion.get("created_work_item_ids", [])])
        purpose = (
            f"Accept {len(summary['accepted_handoff_refs'])} merged, digest-verified Handoffs: {refs}. "
            "Update Queue/Run control state and prepare deterministic follow-up Work Items. "
            "This does not promote or publish research findings.",
            f"マージ済みでダイジェストを検証した{len(summary['accepted_handoff_refs'])}件のHandoffを受理します: {refs}。"
            "Queue・Runの制御状態を更新し、決定的な手順で後続Work Itemを準備します。調査結果の昇格・公開は行いません。",
        )
        provenance = (f"N/A; control processing only. Handoff records: {refs}", f"N/A; 制御処理のみ。Handoff記録: {refs}")
        authority = ("N/A; trusted Handoff control workflow, not a canonical publication", "N/A; 信頼されたHandoff制御処理。正規データの公開ではありません")
        notes = (
            "Research Consensus is unchanged; inspect linked Handoffs and reviews/exceptions for unresolved controls.",
            "調査結果のConsensus状態は変更しません。未解決の制御上の問題は、Handoffとreviews/exceptionsを確認してください。",
        )
    elif kind == "promotion":
        if not summary["prepared"] or any(not item.get("proposal_ref") or not item.get("decision_ref")
                                          for item in summary["prepared"]):
            raise ValueError("each promoted Claim needs pinned Proposal and Decision references")
        title = "Promote accepted OpenFS Claims"
        role = "openfs-promotion[bot] / promotion"
        claims = identifiers([item["canonical_claim_id"] for item in summary["prepared"]])
        refs = references([item[key] for item in summary["prepared"] for key in ("proposal_ref", "decision_ref")])
        work = "N/A"
        purpose = (
            f"Prepare canonical Claim changes from accepted Decisions and rechecked controls: {claims}. "
            "This pull request does not contain Recommendations, auto-merge, or Pages publication. "
            "Review the pinned Proposal, Decision, Evidence, Policy, and dependency reports before merge.",
            f"受理済みDecisionと再確認した制御条件に基づき、正規Claimの変更を準備します: {claims}。"
            "Recommendation、自動マージ、Pages公開は含みません。マージ前に、固定されたProposal・Decision・Evidence・Policy・依存関係の記録を確認してください。",
        )
        provenance = (refs, refs)
        authority = ("N/A; authorized Claim promotion workflow; no new publication approval", "N/A; 承認されたClaim昇格ワークフロー。新たな公開承認はありません")
        notes = (
            f"Inspect dissent, dependencies and Coverage Gaps in {refs}; this PR does not create a new independent review.",
            f"{refs}に記録された異論・依存関係・Coverage Gapを確認してください。このPRは新たな独立レビューではありません。",
        )
    else:
        raise ValueError("unknown automation PR kind")

    sections = []
    for language, heading, purpose_heading, provenance_heading, boundary_heading, validation_heading, review_heading in (
        (0, "English", "Purpose", "Provenance", "Boundary and risk", "Validation", "Review notes"),
        (1, "日本語", "目的", "来歴", "情報境界とリスク", "検証", "レビュー事項"),
    ):
        provenance_labels = (REQUIRED_PROVENANCE_LABELS, JAPANESE_PROVENANCE_LABELS)[language]
        checks = (REQUIRED_CHECKS, JAPANESE_CHECKS)[language]
        review_labels = (REQUIRED_REVIEW_LABELS, JAPANESE_REVIEW_LABELS)[language]
        provenance_values = (role, authority[language], work, runs, provenance[language], base_commit)
        review_values = (
            notes[language],
            ("Trusted local control processing only; no research network fallback, new permissions or unattended activation.",
             "信頼されたローカル制御処理のみ。調査用ネットワークの迂回、権限追加、無人運転の有効化はありません。")[language],
            ("Revert the merge commit; reconcile dependent Queue/Run or Claim records before retrying. Do not erase historical evidence.",
             "マージコミットをrevertし、再実行前に依存するQueue・RunまたはClaimの記録を照合します。過去の根拠は削除しません。")[language],
            ("N/A; this PR does not authorize Pages publication.", "N/A; このPRはPages公開を承認しません。")[language],
        )
        validation_note = (
            "Repository validation, the full unittest suite and role/path checks passed on the committed branch before this body was prepared. These are software checks, not independent scientific review.",
            "この本文を準備する前に、コミット済みのブランチでリポジトリ検証、全unittest、役割別パス検査が成功しました。ソフトウェアの検査であり、科学的内容の独立レビューではありません。",
        )[language]
        sections.append("\n".join([
            f"# {heading}", "", f"## {purpose_heading}", "", purpose[language], "",
            f"## {provenance_heading}", "",
            *[f"- {label}: {value}" for label, value in zip(provenance_labels, provenance_values)], "",
            f"## {boundary_heading}", "", *[f"- [x] {label}" for label in checks[:5]], "",
            f"## {validation_heading}", "", *[f"- [x] {label}" for label in checks[5:]], "", validation_note, "",
            f"## {review_heading}", "", *[f"- {label}: {value}" for label, value in zip(review_labels, review_values)],
        ]))
    body = "\n\n".join(sections) + "\n"
    if errors := validate_pull_request({"title": title, "body": body}):
        raise ValueError("; ".join(errors))
    return title, body


def prepare_body(root: Path, kind: str, summary: dict, base_commit: str,
                 head_branch: str) -> tuple[str, str]:
    """Run checks on committed outputs; never infer success from a summary file."""
    if not re.fullmatch(r"[0-9a-f]{40}", base_commit):
        raise ValueError("a full base commit SHA is required")
    validation_env = {key: os.environ[key] for key in (
        "PATH", "HOME", "TMPDIR", "TMP", "TEMP", "LANG", "LC_ALL", "SYSTEMROOT", "OPENFS_NODE",
    ) if key in os.environ}
    def run(args, *, capture=True):
        result = subprocess.run(args, cwd=root, check=True, text=True, capture_output=capture,
                                env=validation_env)
        return (result.stdout or "").strip()

    head = run(["git", "rev-parse", "HEAD"])
    run(["git", "check-ref-format", "--branch", head_branch])
    if run(["git", "rev-parse", "--verify", f"refs/heads/{head_branch}"]) != head:
        raise ValueError("requested PR branch does not match the validated HEAD")
    run(["git", "merge-base", "--is-ancestor", base_commit, head])
    if run(["git", "status", "--porcelain", "--untracked-files=no"]):
        raise ValueError("automation PR validation requires a clean committed branch")
    paths = run(["git", "diff", "--name-only", base_commit, head]).splitlines()
    if not paths:
        raise ValueError("automation PR has no committed changes")
    role = {"control": "orchestrator", "promotion": "promotion"}[kind]
    _, denied = check_paths(role, paths, load_config(root / "config/role-permissions.json"))
    if denied:
        raise ValueError(f"automation PR contains disallowed paths: {denied}")
    run([sys.executable, "tools/validate_repository.py"], capture=False)
    run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], capture=False)
    if (run(["git", "rev-parse", "HEAD"]) != head
            or run(["git", "rev-parse", "--verify", f"refs/heads/{head_branch}"]) != head
            or run(["git", "status", "--porcelain", "--untracked-files=no"])):
        raise ValueError("branch changed during validation; revalidate before creating the PR")
    return format_body(kind, summary, base_commit)
