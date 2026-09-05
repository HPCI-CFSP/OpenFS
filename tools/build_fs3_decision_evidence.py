#!/usr/bin/env python3
"""Build a report-ready FS3.0 decision-evidence package without inferring gaps."""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AS_OF = "2026-09-06"
ARTIFACT_PATH = ROOT / "knowledge/public/fs3-decision-evidence.json"
REPORT_PATH = ROOT / "reports/exports/20260906_001_fs3-system-planning-evidence.md"
REPORT_INDEX_PATH = ROOT / "reports/exports/index.json"
DIRECTIVE_ID = "DIR-900105"
DECISION_ID = "PUBDEC-RESEARCH-READINESS-20260906-001"


def read_json(relative: str) -> dict[str, Any]:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def reference_id(ref: dict[str, Any]) -> str:
    return f"{ref['roadmap_id']}:{ref['milestone_id']}"


def build_security() -> dict[str, Any]:
    profiles = read_json("config/execution-security-profiles.json")
    controls = read_json("config/owner-controls.json")
    triage = read_json("knowledge/public/audits/roadmap-source-triage.json")
    required = set(profiles["required_verified_controls_for_production"])
    eligible = [
        item["profile_id"]
        for item in profiles["profiles"]
        if item.get("production_eligible") is True
        and required <= {
            key for key, value in item.get("controls", {}).items()
            if value == "verified"
        }
        and item.get("verification_evidence")
    ]
    owner_verified = all(
        item.get("status") == "verified"
        and item.get("verified_by")
        and item.get("verified_at")
        and item.get("expires_at")
        and item.get("evidence_note")
        for item in controls["controls"]
    )
    checks = {
        "production_security_profile_available": bool(eligible),
        "owner_controls_verified": owner_verified,
        "security_profile_selected": False,
        "full_safe_fetch_refresh_completed": False,
        "source_triage_resolved": triage["summary"]["unresolved"] == 0,
    }
    actions = [
        {
            "action_id": "deploy-and-verify-security-profile",
            "summary_ja": "管理Web検索、匿名Safe Fetch、SSRF防止、Shell外向き通信遮断、依存取得分離、Git公開制限を実環境で検証します。",
            "summary_en": "Deploy and verify managed search, anonymous Safe Fetch, SSRF protection, shell-egress blocking, dependency-egress separation, and restricted Git publication.",
            "refs": ["config/research-web-security-policy.json", "config/execution-security-profiles.json"],
        },
        {
            "action_id": "record-owner-attestations",
            "summary_ja": "GitHubとプロバイダー側の外部設定を確認し、秘密情報を含まない有効期限付き証明を記録します。",
            "summary_en": "Verify external GitHub and provider settings and record expiring, non-secret attestations.",
            "refs": ["config/owner-controls.json", "docs/operations/production-readiness.md"],
        },
        {
            "action_id": "select-production-profile",
            "summary_ja": "上記の検証後だけ、`OPENFS_SECURITY_PROFILE_ID`にproduction_eligibleなProfile IDを設定します。",
            "summary_en": "Only after verification, set `OPENFS_SECURITY_PROFILE_ID` to a production-eligible profile ID.",
            "refs": ["docs/operations/automation-setup.md"],
        },
        {
            "action_id": "refresh-and-triage-roadmap-sources",
            "summary_ja": "Safe Web Fetch Brokerによる全URL監査を実行し、取得結果と本文確認を分離したまま未解決項目を再審査します。",
            "summary_en": "Run the full URL audit through the Safe Web Fetch Broker and reassess unresolved entries while keeping retrieval and semantic review separate.",
            "refs": ["tools/audit_roadmap_sources_via_fetch_broker.py", "knowledge/public/audits/roadmap-source-triage.json"],
        },
    ]
    return {
        "status": "ready" if all(checks.values()) else "blocked",
        "selected_profile_id": None,
        "production_eligible_profile_ids": eligible,
        "checks": checks,
        "blockers": [key for key, value in checks.items() if not value],
        "owner_actions": actions,
        "source_triage": {
            "reviewed": triage["summary"]["reviewed_count"],
            "confirmed": triage["summary"]["exact_url_content_confirmed"],
            "unresolved": triage["summary"]["unresolved"],
            "full_refresh_status": "blocked" if not eligible else "complete",
        },
    }


def build_systems(roadmaps: list[dict[str, Any]]) -> dict[str, Any]:
    inventory = read_json("knowledge/public/hpci-system-inventory.json")
    milestones = {
        (roadmap["roadmap_id"], item["milestone_id"]): item
        for roadmap in roadmaps
        for lane in roadmap["lanes"]
        for item in lane["milestones"]
    }
    operational: dict[str, list[str]] = defaultdict(list)
    facility: dict[str, list[str]] = defaultdict(list)
    for item in inventory["operational_observations"]:
        for system_id in item["system_ids"]:
            operational[system_id].append(item["observation_id"])
            if item["metric"] in {"design-power", "operating-power"}:
                facility[system_id].append(item["observation_id"])
    for item in inventory["operational_data_products"]:
        for system_id in item["system_ids"]:
            operational[system_id].append(item["product_id"])

    rows = []
    for system in inventory["systems"]:
        refs = system.get("lifecycle_milestone_refs", [])
        future = [
            ref for ref in refs
            if milestones[(ref["roadmap_id"], ref["milestone_id"])]["year"] is not None
            and milestones[(ref["roadmap_id"], ref["milestone_id"])]["year"] >= 2026
            and milestones[(ref["roadmap_id"], ref["milestone_id"])]["timing_basis"]
            in {"project-target", "vendor-target", "policy-target"}
        ]
        operation_refs = sorted(operational[system["system_id"]])
        facility_refs = sorted(facility[system["system_id"]])
        missing = []
        if not future:
            missing.append("更新・終了・増強の将来時期")
        if not operation_refs:
            missing.append("稼働率・可用性・ジョブ履歴等の運用実績")
        if not facility_refs:
            missing.append("同一境界の設計・運転電力と冷却条件")
        rows.append({
            "system_id": system["system_id"],
            "name_ja": system["name_ja"],
            "name_en": system["name_en"],
            "center_id": system["center_id"],
            "lifecycle_status": "future-public-timing" if future else "history-only",
            "lifecycle_refs": [reference_id(ref) for ref in refs],
            "operations_status": "registered" if operation_refs else "coverage-gap",
            "operational_evidence_refs": operation_refs,
            "facility_status": "power-evidence-registered" if facility_refs else "coverage-gap",
            "facility_evidence_refs": facility_refs,
            "next_action_ja": "確認済みの範囲を維持する。" if not missing else "公開一次情報で" + "、".join(missing) + "を確認する。",
            "next_action_en": "Maintain the verified scope." if not missing else "Confirm public primary evidence for " + ", ".join({
                "更新・終了・増強の将来時期": "future refresh, retirement, or expansion timing",
                "稼働率・可用性・ジョブ履歴等の運用実績": "utilization, availability, job history, or other operating evidence",
                "同一境界の設計・運転電力と冷却条件": "design/operating power and cooling under a defined boundary",
            }[item] for item in missing) + ".",
        })
    return {
        "summary": {
            "system_count": len(rows),
            "future_lifecycle_count": sum(item["lifecycle_status"] == "future-public-timing" for item in rows),
            "operations_evidence_count": sum(item["operations_status"] == "registered" for item in rows),
            "facility_power_evidence_count": sum(item["facility_status"] == "power-evidence-registered" for item in rows),
        },
        "systems": rows,
    }


def specification_access(documents: list[dict[str, Any]]) -> str:
    specs = [item for item in documents if item["kind"] in {"draft-specification", "final-specification"}]
    if any(item["access_status"] == "public-read" for item in specs):
        return "public-read"
    if any(item["access_status"] in {"registration-required", "confidentiality-required"} for item in specs):
        return "restricted"
    if specs:
        return "not-obtained"
    return "none"


def build_procurements() -> dict[str, Any]:
    register = read_json("knowledge/public/procurement-cost-register.json")
    rows = []
    for case in register["cases"]:
        assessment = case["five_year_cost_assessment"]
        amount = case.get("amount")
        known_scopes = [item for item in assessment["scope_coverage"] if item["evidence_status"] != "unknown"]
        unknown_scopes = [item for item in assessment["scope_coverage"] if item["evidence_status"] == "unknown"]
        if assessment["known_cost_floor_jpy"] is not None:
            use_ja = "公表された契約範囲に限る60か月費用下限として利用できます。完全なTCOではありません。"
            use_en = "Usable only as a 60-month contractual floor for the published scope; it is not complete TCO."
        elif amount is not None:
            use_ja = "公表総額の比較には使えますが、部品単価や5年間TCOへ分解しません。"
            use_en = "Usable as a published total, but not decomposed into component prices or five-year TCO."
        else:
            use_ja = "価格根拠がないため費用比較には使用できません。"
            use_en = "Not usable for cost comparison because no public price is registered."
        rows.append({
            "case_id": case["case_id"], "title_ja": case["title_ja"], "title_en": case["title_en"],
            "amount_jpy": amount["value_jpy"] if amount else None,
            "amount_basis": f"{amount['kind']}:{amount['payment_basis']}:{amount['tax_basis']}" if amount else None,
            "public_document_count": sum(item["access_status"] == "public-read" for item in case["documents"]),
            "specification_access": specification_access(case["documents"]),
            "component_scope_evidence_count": len(known_scopes),
            "component_itemization_count": len(case["itemized_costs"]),
            "five_year_status": assessment["status"],
            "known_five_year_floor_jpy": assessment["known_cost_floor_jpy"],
            "unknown_scope_count": len(unknown_scopes),
            "decision_use_ja": use_ja, "decision_use_en": use_en,
        })
    return {
        "summary": {
            "case_count": len(rows),
            "public_amount_count": sum(item["amount_jpy"] is not None for item in rows),
            "public_specification_count": sum(item["specification_access"] == "public-read" for item in rows),
            "component_itemized_count": sum(item["component_itemization_count"] > 0 for item in rows),
            "known_five_year_floor_count": sum(item["known_five_year_floor_jpy"] is not None for item in rows),
            "complete_tco_count": sum(case["five_year_cost_assessment"]["complete_tco"] for case in register["cases"]),
        },
        "cases": rows,
    }


def build_eea1() -> tuple[dict[str, Any], dict[str, Any]]:
    forecasts = read_json("knowledge/public/application-performance-forecasts.json")
    packages = {item["application_id"]: item for item in forecasts["baseline_package_readiness"]}
    criteria = {item["application_id"]: item for item in forecasts["draft_acceptance_criteria"]}
    requirements: dict[str, list[str]] = defaultdict(list)
    for item in forecasts["quantitative_requirements"]:
        requirements[item["application_id"]].append(item["requirement_id"])
    observed: dict[str, set[int]] = defaultdict(set)
    for item in forecasts["baseline_observations"]:
        if item.get("fugaku_nodes"):
            observed[item["application_id"]].add(item["fugaku_nodes"])
    rows = []
    for application in forecasts["applications"]:
        app_id = application["application_id"]
        package = packages[app_id]
        criterion = criteria[app_id]
        required = package["closure_plan"]["required_artifacts"]
        verified = package["closure_plan"]["verified_artifacts"]
        rows.append({
            "application_id": app_id, "name": application["name"],
            "domain_ja": application["domain_ja"], "domain_en": application["domain_en"],
            "package_status": package["status"], "code_version": package["code_version"],
            "input_version": package["input_version"], "eea1_input_match": package["eea1_input_match"],
            "verified_artifacts": verified, "missing_artifacts": [item for item in required if item not in verified],
            "observed_node_scales": sorted(observed[app_id]),
            "standard_scale_readiness": application["scale_readiness"],
            "measurement_contract_complete": criterion["readiness"]["measurement_contract_complete"],
            "threshold_status": "not-approved", "correctness_rule_status": "draft-not-approved",
            "quantitative_requirement_ids": sorted(requirements[app_id]),
        })
    eea = {
        "summary": {
            "application_count": len(rows),
            "code_version_pinned_count": sum(item["code_version"] is not None for item in rows),
            "input_version_pinned_count": sum(item["input_version"] is not None for item in rows),
            "complete_baseline_package_count": sum(not item["missing_artifacts"] for item in rows),
            "approved_threshold_count": 0,
            "validated_forecast_count": len(forecasts["forecasts"]),
            "isolated_illustration_count": len(forecasts["illustrations"]),
        },
        "standard_node_scales": forecasts["standard_fugaku_node_scales"],
        "applications": rows,
    }
    matrix = forecasts["infrastructure_requirements_matrix"]
    requirement_rows = []
    for row in matrix["rows"]:
        levels = {item["dimension_id"]: item["demand_level"] for item in row["cells"]}
        source_ids = sorted({source for item in row["cells"] for source in item["source_ids"]})
        requirement_rows.append({
            "application_id": row["application_id"],
            "demand_levels": levels,
            "high_dimension_ids": sorted(key for key, value in levels.items() if value == "high"),
            "measurement_gap_count": sum(bool(item.get("measurement_gap_ja")) for item in row["cells"]),
            "quantitative_requirement_ids": sorted(requirements[row["application_id"]]),
            "source_ids": source_ids,
            "threshold_status": "not-approved",
        })
    return eea, {"dimensions": matrix["dimensions"], "applications": requirement_rows}


def build_roadmaps(roadmaps: list[dict[str, Any]], dependency_register: dict[str, Any]) -> dict[str, Any]:
    rows = []
    gaps = Counter()
    milestone_count = 0
    undated_count = 0
    for roadmap in sorted(roadmaps, key=lambda item: item["roadmap_id"]):
        milestones = [item for lane in roadmap["lanes"] for item in lane["milestones"]]
        priorities = Counter(item["priority"] for item in roadmap["coverage_gaps"])
        gaps.update(priorities)
        milestone_count += len(milestones)
        undated_count += sum(item["timing_precision"] == "undated" for item in milestones)
        rows.append({
            "roadmap_id": roadmap["roadmap_id"], "title_ja": roadmap["title_ja"],
            "title_en": roadmap["title_en"], "slug": roadmap["slug"],
            "milestone_count": len(milestones),
            "undated_milestone_count": sum(item["timing_precision"] == "undated" for item in milestones),
            "coverage_gap_counts": {key: priorities[key] for key in ("P0", "P1", "P2")},
            "consensus_status": roadmap["consensus_status"],
        })
    return {
        "summary": {
            "roadmap_count": len(rows), "milestone_count": milestone_count,
            "undated_milestone_count": undated_count,
            "dependency_count": len(dependency_register["dependencies"]),
            "p0_gap_count": gaps["P0"], "p1_gap_count": gaps["P1"], "p2_gap_count": gaps["P2"],
        },
        "roadmaps": rows,
    }


def report_structure(procurement_count: int) -> list[dict[str, Any]]:
    values = [
        ("CH-01", "目的・対象・方法と情報境界", "Purpose, scope, method, and information boundary", "公開情報だけを用いる調査範囲、更新方法、セキュリティ、Consensus状態を示します。", "Define the public-only scope, update method, security boundary, and Consensus status.", ["config/research-web-security-policy.json", "knowledge/public/audits/roadmap-source-triage.json"]),
        ("CH-02", "HPCIシステムの現況と更新制約", "Current HPCI systems and refresh constraints", "27システムの構成、将来時期、運用実績、施設根拠の有無を比較します。", "Compare architecture, future timing, operating evidence, and facility evidence for 27 systems.", ["knowledge/public/hpci-system-inventory.json", "RM-X-BLUEPRINT"]),
        ("CH-03", "技術・供給・施設ロードマップ", "Technology, supply, and facility roadmaps", "計算、メモリ、接続、ストレージ、施設、供給網を四半期単位で比較します。", "Compare compute, memory, interconnect, storage, facilities, and supply at quarterly granularity.", ["knowledge/public/roadmaps", "knowledge/public/dependencies/p0-roadmap-dependencies.json"]),
        ("CH-04", "システムソフトウェアと運用準備", "System software and operational readiness", "移植性、ランタイム、ワークフロー、セキュリティ、可観測性の依存関係を示します。", "Describe dependencies across portability, runtimes, workflows, security, and observability.", ["RM-SSW-PORTABILITY", "RM-SSW-RUNTIME", "RM-SSW-WORKFLOW", "RM-SSW-SECURITY", "RM-SSW-PERFORMANCE"]),
        ("CH-05", "アプリケーション需要と性能評価", "Application demand and performance evaluation", "EEA1の再現可能性、測定範囲、定量要件、未承認の合否条件を分離します。", "Separate EEA1 reproducibility, measured ranges, quantitative requirements, and unapproved thresholds.", ["knowledge/public/application-performance-forecasts.json", "RM-APP-WORKLOADS"]),
        ("CH-06", "調達実績とライフサイクル費用", "Procurement evidence and lifecycle cost", f"{procurement_count}案件の公表総額、仕様書、費目範囲、5年費用の計算可否を示します。", f"Show public totals, specifications, scope coverage, and five-year cost computability for {procurement_count} cases.", ["knowledge/public/procurement-cost-register.json", "RM-X-PROCUREMENT"]),
        ("CH-07", "複数のシステム整備計画案", "Multiple system planning options", "同じ11評価軸と依存関係で3案を比較し、予算・数量・採否は人の判断として残します。", "Compare three options using the same eleven criteria and dependencies while leaving budget, quantity, and adoption to accountable humans.", ["knowledge/public/planning-evidence-readiness.json", "roadmaps/scenarios/accepted"]),
        ("CH-08", "未確認事項、検証計画、来歴", "Coverage gaps, validation plan, and provenance", "不足根拠、責任者、次の測定・調査、Consensus Gate、更新履歴を示します。", "Record missing evidence, owners, next measurements and research, the Consensus Gate, and change history.", ["knowledge/public/audits/roadmap-gap-queue.json", "reviews/consensus-packages", "reviews/directives/DIR-900105.json"]),
    ]
    return [
        {"chapter_id": item[0], "title_ja": item[1], "title_en": item[2], "purpose_ja": item[3], "purpose_en": item[4], "evidence_refs": item[5]}
        for item in values
    ]


def build_artifact() -> dict[str, Any]:
    roadmaps = [read_json(str(path.relative_to(ROOT))) for path in sorted((ROOT / "knowledge/public/roadmaps").glob("*.json"))]
    dependency_register = read_json("knowledge/public/dependencies/p0-roadmap-dependencies.json")
    eea1, requirements = build_eea1()
    systems = build_systems(roadmaps)
    procurements = build_procurements()
    roadmap_section = build_roadmaps(roadmaps, dependency_register)
    system_count = systems["summary"]["system_count"]
    procurement_count = procurements["summary"]["case_count"]
    application_count = eea1["summary"]["application_count"]
    roadmap_count = roadmap_section["summary"]["roadmap_count"]
    return {
        "schema_version": "0.1.0", "artifact_id": "FS3-DECISION-EVIDENCE-001",
        "status": "published", "as_of": AS_OF, "research_status": "provisional",
        "consensus_status": "incomplete",
        "title_ja": "FS3.0システム整備計画の判断根拠パッケージ",
        "title_en": "FS3.0 system-planning decision-evidence package",
        "summary_ja": f"HPCI {system_count}システム、公開調達{procurement_count}案件、EEA1 {application_count}アプリ、{roadmap_count}ロードマップを、報告書の章構成と追跡可能な形で接続した暫定資料です。未公表値、未校正予測、未承認の閾値は埋めていません。",
        "summary_en": f"A provisional package connecting {system_count} HPCI systems, {procurement_count} public procurement cases, {application_count} EEA1 applications, and {roadmap_count} roadmaps to a report structure with traceable evidence. Undisclosed values, uncalibrated forecasts, and unapproved thresholds remain unset.",
        "security_readiness": build_security(),
        "hpci_systems": systems,
        "procurements": procurements,
        "eea1": eea1,
        "application_requirements": requirements,
        "roadmaps": roadmap_section,
        "report_structure": report_structure(procurement_count),
        "caveat_ja": "単一のAIモデル・単一エージェントによる公開情報ベースの暫定整理です。独立したAIモデルによるConsensus Gate、各責任者による要件・閾値・予算・調達判断は未完了です。充足数は調査範囲であり、案の点数や推奨順位を示すものではありません。",
        "caveat_en": "A provisional public-information synthesis by one model and one agent. The Consensus Gate using independent models and accountable approval of requirements, thresholds, budgets, and procurement decisions are incomplete. Coverage counts are research scope, not scores or rankings.",
        "publication": {"information_classification": "public", "publication_approved": True, "publication_decision_id": DECISION_ID, "human_approval_directive_id": DIRECTIVE_ID},
    }


def esc(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def money(value: Any) -> str:
    return "未確認" if value is None else f"{value:,.0f}円"


def status_ja(value: str) -> str:
    return {
        "history-only": "過去・現況のみ",
        "future-public-timing": "将来時期の公開根拠あり",
        "registered": "根拠登録済み",
        "coverage-gap": "公開根拠未確認",
        "power-evidence-registered": "電力根拠登録済み",
        "public-read": "公開仕様書を確認済み",
        "not-obtained": "公開仕様書を未取得",
        "restricted": "アクセス制限あり",
        "none": "仕様書なし",
    }.get(value, value)


def render_report(data: dict[str, Any]) -> str:
    security = data["security_readiness"]
    systems = data["hpci_systems"]
    procurements = data["procurements"]
    eea = data["eea1"]
    roadmaps = data["roadmaps"]
    lines = [
        "# FS3.0システム整備計画の判断根拠パッケージ",
        "", f"基準日: {data['as_of']} / Status: provisional / Consensus: incomplete", "",
        data["summary_ja"], "", f"> {data['caveat_ja']}", "",
        "## 1. 判断準備度の要約", "",
        "| 対象 | 登録数 | 現在確認できる範囲 | 判断上の境界 |", "|---|---:|---|---|",
        f"| HPCIシステム | {systems['summary']['system_count']} | 将来時期 {systems['summary']['future_lifecycle_count']}、運用根拠 {systems['summary']['operations_evidence_count']}、電力根拠 {systems['summary']['facility_power_evidence_count']} | 未確認を更新予定・ゼロ値として扱わない |",
        f"| 公開調達 | {procurements['summary']['case_count']} | 総額 {procurements['summary']['public_amount_count']}、公開仕様 {procurements['summary']['public_specification_count']}、60か月費用下限 {procurements['summary']['known_five_year_floor_count']} | 費目別の価格内訳 0件、完全なTCO 0件 |",
        f"| EEA1 | {eea['summary']['application_count']} | コード版固定 {eea['summary']['code_version_pinned_count']}、入力版固定 {eea['summary']['input_version_pinned_count']} | 完全な再現パッケージ 0件、承認済み閾値 0件、検証済み予測 0件 |",
        f"| ロードマップ | {roadmaps['summary']['roadmap_count']} | {roadmaps['summary']['milestone_count']}マイルストーン、{roadmaps['summary']['dependency_count']}依存関係 | Consensus Gate未完了 |",
        "", "```mermaid", "flowchart LR",
        "  S[公開情報] --> E[根拠] --> K[技術整理] --> R[ロードマップ]",
        "  R --> Q[アプリケーション要件] --> P[システム整備計画案] --> D[報告書]",
        "  E --> G[未確認事項] --> S",
        "```", "", "## 2. Web調査自動化のセキュリティ境界", "",
        f"状態: **{security['status']}**。本番利用可能なセキュリティプロファイルは{len(security['production_eligible_profile_ids'])}件、確認待ちの情報源は{security['source_triage']['unresolved']}件です。安全性を自己証明せず、プロファイルを実環境で検証するまでは全URLの再確認を実行しません。", "",
    ]
    for action in security["owner_actions"]:
        lines.append(f"- `{action['action_id']}`: {action['summary_ja']}")
    lines += ["", "## 3. HPCI 27システムの計画根拠", "", "| システム | センター | 将来時期 | 運用根拠 | 電力・施設根拠 | 次の確認 |", "|---|---|---|---|---|---|"]
    for item in systems["systems"]:
        lines.append(f"| {esc(item['name_ja'])} | `{item['center_id']}` | {status_ja(item['lifecycle_status'])} | {status_ja(item['operations_status'])} ({len(item['operational_evidence_refs'])}) | {status_ja(item['facility_status'])} ({len(item['facility_evidence_refs'])}) | {esc(item['next_action_ja'])} |")
    lines += ["", f"## 4. 公開調達{procurements['summary']['case_count']}案件と5年間費用", "", "| 調達案件 | 公表額 | 仕様書 | 費目根拠 | 60か月費用 | 未確認費目 | 判断への利用 |", "|---|---:|---|---:|---:|---:|---|"]
    for item in procurements["cases"]:
        lines.append(f"| {esc(item['title_ja'])} | {money(item['amount_jpy'])} | {status_ja(item['specification_access'])} | {item['component_scope_evidence_count']}/12 | {money(item['known_five_year_floor_jpy'])} | {item['unknown_scope_count']}/12 | {esc(item['decision_use_ja'])} |")
    lines += ["", "## 5. EEA1再現性と性能評価", "", "`1 / 4 / 32 / 128 / 1024 / 10000`ノードを共通表示軸とします。異なる入力の実測は、同一入力の性能予測の校正点として扱いません。", "", "| アプリケーション | コード版 | 入力版 | 確認済み成果物 | 不足成果物 | 公開実測ノード | 閾値・予測 |", "|---|---|---|---|---|---|---|"]
    for item in eea["applications"]:
        lines.append(f"| {item['name']} | {esc(item['code_version'] or '未確認')} | {esc(item['input_version'] or '未確認')} | {esc(', '.join(item['verified_artifacts']) or 'なし')} | {esc(', '.join(item['missing_artifacts']) or 'なし')} | {esc(', '.join(map(str, item['observed_node_scales'])) or 'なし')} | 閾値未承認 / 検証済み予測なし |")
    lines += ["", "## 6. アプリケーション需要からシステム要件へ", "", "定性的な`high / medium / low / unknown`は設計上の注意点であり、採用閾値や点数ではありません。数値がある場合も、公開実測範囲または公開目標として保持します。", "", "| アプリケーション | 高い要求が想定される軸 | 定量要件・実測範囲 | 測定不足セル |", "|---|---|---|---:|"]
    names = {item["application_id"]: item["name"] for item in eea["applications"]}
    for item in data["application_requirements"]["applications"]:
        lines.append(f"| {names[item['application_id']]} | {esc(', '.join(item['high_dimension_ids']) or 'none')} | {esc(', '.join(item['quantitative_requirement_ids']) or 'none')} | {item['measurement_gap_count']} |")
    lines += ["", "## 7. 公開ロードマップと依存関係", "", "| ロードマップ | マイルストーン | 四半期未特定 | 未確認事項 (P0/P1/P2) |", "|---|---:|---:|---:|"]
    for item in roadmaps["roadmaps"]:
        counts = item["coverage_gap_counts"]
        lines.append(f"| [{esc(item['title_ja'])}](https://hpci-cfsp.github.io/OpenFS/roadmaps/{item['slug']}/?lang=ja) | {item['milestone_count']} | {item['undated_milestone_count']} | {counts['P0']}/{counts['P1']}/{counts['P2']} |")
    lines += ["", "## 8. 報告書の章構成と根拠", ""]
    for chapter in data["report_structure"]:
        lines.append(
            f"- **{chapter['chapter_id']} {chapter['title_ja']}**: "
            f"{chapter['purpose_ja']} 根拠: `{ '`, `'.join(chapter['evidence_refs']) }`"
        )
    lines += [
        "", "## English summary", "", data["summary_en"], "", f"> {data['caveat_en']}", "",
        f"- Secure unattended Web research: **{security['status']}**; {security['source_triage']['unresolved']} source-triage entries remain unresolved.",
        f"- HPCI inventory: {systems['summary']['system_count']} systems; {systems['summary']['future_lifecycle_count']} have public future lifecycle timing, {systems['summary']['operations_evidence_count']} have registered operational evidence, and power evidence is registered for {systems['summary']['facility_power_evidence_count']} systems.",
        f"- Procurement: {procurements['summary']['case_count']} cases; {procurements['summary']['public_amount_count']} public totals, {procurements['summary']['component_itemized_count']} itemized cases, and {procurements['summary']['complete_tco_count']} complete five-year TCO cases.",
        f"- EEA1: {eea['summary']['application_count']} applications; {eea['summary']['complete_baseline_package_count']} complete reproducibility packages, {eea['summary']['approved_threshold_count']} approved thresholds, and {eea['summary']['validated_forecast_count']} validated forecasts.",
        f"- Roadmaps: {roadmaps['summary']['roadmap_count']} provisional public roadmaps and {roadmaps['summary']['dependency_count']} registered cross-roadmap dependencies.",
        "", "Machine-readable source: `knowledge/public/fs3-decision-evidence.json`", "",
    ]
    return "\n".join(lines)


def write_outputs() -> None:
    artifact = build_artifact()
    ARTIFACT_PATH.parent.mkdir(parents=True, exist_ok=True)
    ARTIFACT_PATH.write_text(json.dumps(artifact, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(render_report(artifact), encoding="utf-8")
    report_index = {
        "schema_version": "0.1.0",
        "reports": [{
            "report_id": "REPORT-FS3-DECISION-EVIDENCE-20260906",
            "title": "FS3.0システム整備計画の判断根拠パッケージ",
            "title_en": "FS3.0 system-planning decision-evidence package",
            "as_of": AS_OF, "status": "published", "version": "0.1.0", "supersedes": None,
            "summary": artifact["summary_ja"],
            "summary_en": artifact["summary_en"],
            "evidence_refs": ["FS3-DECISION-EVIDENCE-001", "PLANNING-EVIDENCE-READINESS-001", "ROADMAP-DEPENDENCY-REGISTER-001"],
            "download_url": "https://github.com/HPCI-CFSP/OpenFS/blob/main/reports/exports/20260906_001_fs3-system-planning-evidence.md",
            "publication": {"information_classification": "public", "publication_approved": True, "publication_decision_id": DECISION_ID, "human_approval_directive_id": DIRECTIVE_ID, "approved_at": "2026-09-06T00:10:00+09:00"},
        }],
    }
    REPORT_INDEX_PATH.write_text(json.dumps(report_index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    write_outputs()
    print(ARTIFACT_PATH.relative_to(ROOT))
    print(REPORT_PATH.relative_to(ROOT))
    print(REPORT_INDEX_PATH.relative_to(ROOT))


if __name__ == "__main__":
    main()
