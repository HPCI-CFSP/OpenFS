#!/usr/bin/env python3
"""Build a commit-pinned independent-review package for the P0 portfolio."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_ID = "CRP-P0-ROADMAPS-V02"
DEFAULT_OUTPUT = ROOT / "reviews" / "consensus-packages" / PACKAGE_ID
ROADMAP_PATHS = [
    f"knowledge/public/roadmaps/{name}.json"
    for name in (
        "compute-nodes-accelerators",
        "interconnect-optics-disaggregation",
        "memory-data-movement",
        "portability-compilers-tuning",
        "reference-blueprint-centers",
        "workloads-benchmarks-models",
    )
]
ARTIFACTS = [
    *[(path, "roadmap") for path in ROADMAP_PATHS],
    ("knowledge/public/audits/roadmap-source-audit.json", "source-audit"),
    ("knowledge/public/audits/roadmap-evidence-audit.json", "evidence-audit"),
    ("knowledge/public/dependencies/p0-roadmap-dependencies.json", "dependency-register"),
    ("roadmaps/scenarios/accepted/hpci-p0-scenarios.json", "scenario-set"),
    ("config/consensus-policy.json", "policy"),
    ("config/scenario-policy.json", "policy"),
    ("config/agent-registry.json", "registry"),
    ("schemas/public-roadmap.schema.json", "schema"),
    ("schemas/system-scenario.schema.json", "schema"),
    ("schemas/consensus-review-package.schema.json", "schema"),
    ("schemas/consensus-package-review.schema.json", "schema"),
    ("schemas/consensus-package-gate-result.schema.json", "schema"),
    ("tools/build_consensus_review_package.py", "tool"),
    ("tools/evaluate_consensus_review_package.py", "tool"),
    ("reviews/directives/DIR-900006.json", "directive"),
]


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def committed_bytes(root: Path, commit: str, path: str) -> bytes:
    result = subprocess.run(
        ["git", "show", f"{commit}:{path}"],
        cwd=root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    return result.stdout


def artifact_manifest(root: Path, commit: str) -> list[dict[str, str]]:
    return [
        {
            "path": path,
            "sha256": hashlib.sha256(committed_bytes(root, commit, path)).hexdigest(),
            "object_type": object_type,
        }
        for path, object_type in ARTIFACTS
    ]


def roadmap_unit(path: str, roadmap: dict[str, Any]) -> dict[str, Any]:
    return {
        "unit_id": f"CRU-{roadmap['roadmap_id'].removeprefix('RM-')}",
        "kind": "roadmap",
        "title_ja": roadmap["title_ja"],
        "title_en": roadmap["title_en"],
        "artifact_paths": [path, "knowledge/public/audits/roadmap-evidence-audit.json", "knowledge/public/audits/roadmap-source-audit.json"],
        "selectors": [
            roadmap["roadmap_id"],
            *[track["track_id"] for track in roadmap["tracks"]],
            *[gap["gap_id"] for gap in roadmap["coverage_gaps"]],
        ],
        "required_checks": [
            "source-identity", "citation-entailment", "temporal-validity",
            "scope-alignment", "coverage-gap-completeness",
        ],
        "falsification_prompts_ja": [
            "出来事と将来目標が混同されていないか。",
            "四半期を直接支えない資料からQ1-Q4を推定していないか。",
            "重要な反例、競合候補、製品中止、時期変更がCoverage Gapから漏れていないか。",
        ],
        "falsification_prompts_en": [
            "Are observed events and forward targets kept distinct?",
            "Is any quarter inferred from a source that supports only a year or wider interval?",
            "Are material counterexamples, alternatives, cancellations, or schedule changes missing from Coverage Gaps?",
        ],
    }


def shared_units() -> list[dict[str, Any]]:
    return [
        {
            "unit_id": "CRU-CROSS-ROADMAP",
            "kind": "cross-roadmap",
            "title_ja": "ロードマップ間依存関係",
            "title_en": "Cross-roadmap dependencies",
            "artifact_paths": ["knowledge/public/dependencies/p0-roadmap-dependencies.json", *ROADMAP_PATHS],
            "selectors": ["ROADMAP-DEPENDENCY-REGISTER-001", "XDEP-*"],
            "required_checks": ["source-identity", "scope-alignment", "dependency-validity", "temporal-validity"],
            "falsification_prompts_ja": ["依存の向き、重要度、判断ゲートに逆転・循環・欠落がないか。", "技術的な可能性を調達・導入可能性と誤認していないか。"],
            "falsification_prompts_en": ["Are dependency direction, criticality, and gates free of inversions, cycles, or omissions?", "Is technical feasibility being mistaken for procurement or deployment readiness?"],
        },
        {
            "unit_id": "CRU-COVERAGE-GAPS",
            "kind": "coverage-gap",
            "title_ja": "優先度付きCoverage Gap",
            "title_en": "Prioritized Coverage Gaps",
            "artifact_paths": ROADMAP_PATHS,
            "selectors": ["GAP-*", "P0", "P1", "P2"],
            "required_checks": ["scope-alignment", "coverage-gap-completeness", "dependency-validity", "fallback-viability"],
            "falsification_prompts_ja": ["P0がHPCI判断への影響ではなく情報の入手しやすさで決まっていないか。", "未公表事項を否定的事実として扱っていないか。"],
            "falsification_prompts_en": ["Is P0 driven by HPCI decision impact rather than ease of research?", "Is absence of public information incorrectly treated as negative fact?"],
        },
        {
            "unit_id": "CRU-HPCI-SCENARIOS",
            "kind": "scenario",
            "title_ja": "HPCI整備計画3シナリオ",
            "title_en": "Three HPCI infrastructure scenarios",
            "artifact_paths": ["roadmaps/scenarios/accepted/hpci-p0-scenarios.json", "config/scenario-policy.json", "knowledge/public/dependencies/p0-roadmap-dependencies.json", *ROADMAP_PATHS],
            "selectors": ["SCN-HPCI-BALANCED-001", "SCN-HPCI-AI-DATA-001", "SCN-HPCI-STAGED-001", "TOPT-*"],
            "required_checks": ["scope-alignment", "scenario-coherence", "fallback-viability", "dependency-validity", "coverage-gap-completeness"],
            "falsification_prompts_ja": ["3案が実質的に同じ案の言い換えになっていないか。", "アーキテクチャ、ソフトウェア、アプリケーション、センター制約が一体で成立するか。", "fallbackが技術的・運用的に実行可能か。"],
            "falsification_prompts_en": ["Are the three options genuinely distinct rather than paraphrases?", "Do architecture, software, applications, and center constraints form coherent plans?", "Are fallbacks technically and operationally viable?"],
        },
        {
            "unit_id": "CRU-PUBLICATION-ASSURANCE",
            "kind": "publication-assurance",
            "title_ja": "公開境界・来歴・表示",
            "title_en": "Publication boundary, provenance, and presentation",
            "artifact_paths": ["reviews/directives/DIR-900006.json", "config/consensus-policy.json", "knowledge/public/audits/roadmap-source-audit.json", "knowledge/public/audits/roadmap-evidence-audit.json", "schemas/consensus-review-package.schema.json", "schemas/consensus-package-review.schema.json", "schemas/consensus-package-gate-result.schema.json", "tools/build_consensus_review_package.py", "tools/evaluate_consensus_review_package.py"],
            "selectors": ["DIR-900006", "consensus_status", "research_status", "publication"],
            "required_checks": ["publication-boundary", "scope-alignment", "source-identity", "temporal-validity", "review-protocol-integrity"],
            "falsification_prompts_ja": ["未完了のConsensusを受理済みと読める表示がないか。", "URL到達性を主張の正しさとして表示していないか。", "公開承認範囲外の情報が含まれていないか。"],
            "falsification_prompts_en": ["Could incomplete Consensus be read as accepted?", "Is URL reachability presented as claim correctness?", "Does any content exceed the approved public-information boundary?"],
        },
    ]


def build_manifest(root: Path, base_commit: str, created_at: str) -> dict[str, Any]:
    policy = read_json(root / "config" / "consensus-policy.json")
    rule = policy["rules"]["high_impact_recommendation"]
    units = [
        roadmap_unit(path, read_json(root / path))
        for path in ROADMAP_PATHS
    ] + shared_units()
    roadmaps = [read_json(root / path) for path in ROADMAP_PATHS]
    source_audit = read_json(root / "knowledge/public/audits/roadmap-source-audit.json")
    dependency_register = read_json(root / "knowledge/public/dependencies/p0-roadmap-dependencies.json")
    scenarios = read_json(root / "roadmaps/scenarios/accepted/hpci-p0-scenarios.json")
    portfolio_summary = {
        "roadmap_count": len(roadmaps),
        "milestone_count": sum(
            len(lane["milestones"])
            for roadmap in roadmaps
            for lane in roadmap["lanes"]
        ),
        "source_count": source_audit["summary"]["source_count"],
        "coverage_gap_count": sum(len(roadmap["coverage_gaps"]) for roadmap in roadmaps),
        "dependency_count": len(dependency_register["dependencies"]),
        "external_constraint_count": len(dependency_register["external_constraints"]),
        "scenario_count": len(scenarios["scenarios"]),
    }
    return {
        "schema_version": "0.1.0",
        "package_id": PACKAGE_ID,
        "status": "awaiting-independent-review",
        "object_type": "high-impact-recommendation",
        "base_commit": base_commit,
        "created_at": created_at,
        "portfolio_summary": portfolio_summary,
        "consensus_policy": {"policy_id": policy["policy_id"], **rule},
        "artifact_manifest": artifact_manifest(root, base_commit),
        "review_units": units,
        "independence_requirements": {
            "author_group": "openai-gpt5-codex-interactive",
            "reviewer_rule_ja": "支持票には少なくとも3つの独立group、3つのorigin group、登録済みの3モデル系統、2プロバイダが必要。作成モデルと同じgroup、同一会話のfork、同一出力を共有したreviewerは独立票として数えない。",
            "reviewer_rule_en": "Supporting votes require at least three independent groups and three origin groups, three registered model families, and two registered providers. The author group, forks of the same conversation, and reviewers sharing generated conclusions do not count as independent votes.",
            "disallowed_as_independent": ["openai-gpt5-codex-interactive", "same-conversation-fork", "shared-conclusion-context"],
        },
        "known_limitations": [
            {
                "limitation_id": "LIM-CONSENSUS-CAPACITY",
                "description_ja": "agent registryには現時点で有効な独立validator/criticが構成されていない。",
                "description_en": "The agent registry currently has no enabled independent validator or critic.",
                "effect": "blocks-consensus",
            },
            {
                "limitation_id": "LIM-CENTER-PROFILES",
                "description_ja": "15センターの受理済みProfile、施設条件、調達価格・供給確約が揃っていない。",
                "description_en": "Accepted profiles for all 15 centers, facility constraints, procurement prices, and supply commitments are incomplete.",
                "effect": "requires-caveat",
            },
            {
                "limitation_id": "LIM-HUMAN-WEIGHTS",
                "description_ja": "11評価軸の重みと最終採用判断は人によるDirectiveが必要。",
                "description_en": "Weights for the eleven criteria and final adoption require a human Directive.",
                "effect": "requires-human-decision",
            },
        ],
        "submission": {
            "assessment_directory": f"assessments/{PACKAGE_ID}/",
            "assessment_schema": "schemas/consensus-package-review.schema.json",
            "gate_command": f"python3 tools/evaluate_consensus_review_package.py reviews/consensus-packages/{PACKAGE_ID}/manifest.json",
        },
    }


def review_template(manifest: dict[str, Any]) -> dict[str, Any]:
    roadmap_units = [unit for unit in manifest["review_units"] if unit["kind"] == "roadmap"]
    return {
        "_template_notice": "Replace every angle-bracket placeholder and remove this field before submission.",
        "schema_version": "0.1.0",
        "review_id": "<CRV-UNIQUE-ID>",
        "package_id": manifest["package_id"],
        "base_commit": manifest["base_commit"],
        "reviewer": {
            "agent_id": "<agent-id>", "role": "validator", "provider": "<provider>",
            "model_family": "<model-family>", "prompt_profile": "<prompt-profile>",
            "independence_group": "<independence-group>", "origin_group": "<origin-group>",
            "harness_id": "<HAR-ID>", "harness_repository_url": "https://example.invalid/harness",
            "harness_commit": "<40-hex-commit>",
        },
        "registry_snapshot_digest": "<64-hex-sha256>",
        "overall_verdict": "uncertain",
        "primary_source_checks": [
            {
                "unit_id": unit["unit_id"], "source_id": "<SRC-ID>",
                "source_url": "https://example.invalid/primary-source",
                "source_class": "vendor-official",
                "outcome": "inconclusive",
                "notes": "<record the exact claim checked and what the primary source says>",
            }
            for unit in roadmap_units
        ],
        "unit_assessments": [
            {
                "unit_id": unit["unit_id"], "verdict": "uncertain", "confidence": 0,
                "checks": {check: "unknown" for check in unit["required_checks"]},
                "observations": ["<record evidence inspected and result>"], "objections": [],
            }
            for unit in manifest["review_units"]
        ],
        "critical_objections": [],
        "reviewed_at": "<RFC3339-date-time>",
    }


def readme(manifest: dict[str, Any]) -> str:
    commit = manifest["base_commit"]
    summary = manifest["portfolio_summary"]
    return f"""# P0 roadmap v0.2 independent review package

This package pins {summary['roadmap_count']} P0 roadmaps, {summary['milestone_count']}
milestone records, {summary['source_count']} registered sources,
{summary['dependency_count']} cross-roadmap dependencies,
{summary['coverage_gap_count']} prioritized Coverage Gaps, and
{summary['scenario_count']} provisional HPCI scenarios to commit `{commit}`.

## Review protocol

1. Check out exactly `{commit}` and verify every `artifact_manifest.sha256`.
2. Review every `review_unit` independently. Inspect cited public primary sources;
   URL reachability alone is not evidence that a claim is correct.
   Record at least one conclusive primary-source check for every roadmap unit.
3. Actively seek counterevidence using each unit's falsification prompts. Keep
   unsupported timing as a Coverage Gap; do not infer a quarter.
4. Fill `review-template.json`, remove `_template_notice`, assign a unique review
   ID, and save it under `assessments/{PACKAGE_ID}/`. Do not edit the package manifest.
5. Record provider, model family, prompt profile, independence/origin groups,
   harness repository, and harness commit. A fork of the author conversation is
   not an independent vote. The agent must be enabled in the commit-pinned Agent
   Registry, and `registry_snapshot_digest` is the SHA-256 of its exact Git object.
6. Run schema and repository validation. Consensus remains incomplete until the
   configured policy passes and a human makes the required high-impact decision.

## 日本語要約

このパッケージは、P0の{summary['roadmap_count']}ロードマップ、
{summary['milestone_count']}マイルストーン、{summary['source_count']}情報源、
{summary['dependency_count']}相互依存、{summary['coverage_gap_count']}件の優先度付きCoverage Gap、
HPCI整備計画{summary['scenario_count']}案をコミット `{commit}` に固定します。
各review unitを独立に検証し、反証を探索してください。URL到達性を内容の正しさと
みなさず、四半期を推定で補わないでください。同一会話のforkや作成モデルと同じ
independence groupは独立票に数えません。Consensus成立後も最終採用には人の判断が必要です。
"""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--base-commit", required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--created-at")
    args = parser.parse_args()
    commit = subprocess.run(
        ["git", "rev-parse", "--verify", f"{args.base_commit}^{{commit}}"],
        cwd=args.root, check=True, text=True, stdout=subprocess.PIPE,
    ).stdout.strip()
    created_at = args.created_at or datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    manifest = build_manifest(args.root, commit, created_at)
    args.output.mkdir(parents=True, exist_ok=True)
    (args.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output / "review-template.json").write_text(json.dumps(review_template(manifest), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (args.output / "README.md").write_text(readme(manifest), encoding="utf-8")
    print(json.dumps({"package_id": PACKAGE_ID, "base_commit": commit, "artifacts": len(manifest["artifact_manifest"]), "review_units": len(manifest["review_units"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
