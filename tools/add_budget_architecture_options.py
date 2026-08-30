#!/usr/bin/env python3
"""Add reproducible budget-scaled architecture estimates to planning options."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from estimate_system_cost import allocate_budget


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "roadmaps/scenarios/accepted/hpci-p0-scenarios.json"

REFERENCE_CASES = [
    {
        "case_id": "BREF-HPCI-AI-2025",
        "name_ja": "HPCI戦略プログラム向けAI計算資源増強",
        "name_en": "AI compute enhancement for the HPCI strategic program",
        "budget_oku_jpy": 50,
        "scope_ja": "1課題当たりの支援上限。装置費だけとは限らない。",
        "scope_en": "Maximum support per project; not necessarily hardware-only cost.",
        "configuration_ja": "1課題当たり約500基のGPUと、4～5 EFLOPSのAI向け演算性能を想定。",
        "configuration_en": "Assumes roughly 500 GPUs and 4-5 EFLOPS of AI compute per project.",
        "source_title": "AI for Science推進戦略の方向性（案）参考資料",
        "source_publisher": "文部科学省",
        "source_url": "https://www.mext.go.jp/content/20260114-mxt_jyohoka01-000046711_5.pdf",
        "public_date": "2026-01-14",
        "comparability_note_ja": "GPU世代、ネットワーク、ストレージ、施設、運用期間が将来案と同一ではない。",
        "comparability_note_en": "GPU generation, network, storage, facilities, and operating period are not identical to future options.",
    },
    {
        "case_id": "BREF-ABCI30-2023",
        "name_ja": "ABCI 3.0整備",
        "name_en": "ABCI 3.0 expansion",
        "budget_oku_jpy": 400,
        "scope_ja": "令和5年度補正予算の整備事業規模。",
        "scope_en": "FY2023 supplementary-budget program scale.",
        "configuration_ja": "公開資料は、6.22 EFLOPSのAI向け演算性能を持つシステムの整備を示す。",
        "configuration_en": "The public strategy material reports 6.22 EFLOPS of AI compute.",
        "source_title": "半導体・デジタル産業戦略関連資料",
        "source_publisher": "経済産業省",
        "source_url": "https://www.meti.go.jp/policy/mono_info_service/joho/conference/semicon_digital/0012/handeji3.pdf",
        "public_date": "2024-06-04",
        "comparability_note_ja": "事業範囲と価格時点が異なるため、単純なノード単価には換算しない。",
        "comparability_note_en": "Program scope and price date differ, so this is not converted into a simple node unit cost.",
    },
    {
        "case_id": "BREF-FUGAKU-2022",
        "name_ja": "スーパーコンピュータ「富岳」整備",
        "name_en": "Fugaku supercomputer program",
        "budget_oku_jpy": 1300,
        "scope_ja": "開発・製造などを含む総事業費の公表規模。",
        "scope_en": "Published total program scale including development and manufacture.",
        "configuration_ja": "フラッグシップ級システムと開発を含む。",
        "configuration_en": "Includes a flagship-scale system and development program.",
        "source_title": "スーパーコンピュータ「富岳」成果と今後の展開",
        "source_publisher": "文部科学省",
        "source_url": "https://www.mext.go.jp/content/20220120-mxt_jyohoka01-000019552_05.pdf",
        "public_date": "2022-01-20",
        "comparability_note_ja": "独自CPU開発を含む国家プロジェクトであり、市販GPUシステムの調達費とは比較できない。",
        "comparability_note_en": "This national program includes custom CPU development and is not directly comparable with the procurement of commercial GPU systems.",
    },
    {
        "case_id": "BREF-RIKEN-AIFS-2026",
        "name_ja": "理研AI for Science Supercomputer",
        "name_en": "RIKEN AI for Science Supercomputer",
        "budget_oku_jpy": None,
        "scope_ja": "公開構成の参照例。契約金額の根拠には用いない。",
        "scope_en": "Public topology reference; not used as a contract-price basis.",
        "configuration_ja": "400計算ノード、計1,600基のGPU、XDR 800 Gbit/sのFat-tree（ファットツリー）、実効容量1.08 PBの全NVMe構成Lustre。",
        "configuration_en": "400 compute nodes, 1,600 GPUs, an XDR 800 Gbit/s fat-tree network, and 1.08 PB of effective all-NVMe Lustre capacity.",
        "source_title": "AI-for-Science-Supercomputer README",
        "source_publisher": "RIKEN R-CCS",
        "source_url": "https://github.com/RIKEN-RCCS/AI-for-Science-Supercomputer",
        "public_date": "2026-08-27",
        "comparability_note_ja": "構成図の表現とノード内GPU数の参照に限り、将来価格や性能を外挿しない。",
        "comparability_note_en": "Used only for topology presentation and GPUs per node, not to extrapolate future price or performance.",
    },
]

def build_option(scenario: dict[str, Any], ceiling: int, config: dict[str, Any]) -> dict[str, Any]:
    scenario_id = scenario["scenario_id"]
    allocation = allocate_budget(config, scenario_id, ceiling, config["default_deployment_year"])
    key = scenario_id.removeprefix("SCN-HPCI-").removesuffix("-001")
    tier = f"jpy-{ceiling}"
    ids = {c["id"]: f"BCMP-{key}-{ceiling}-{c['id'].upper()}" for c in config["components"]}
    components = []
    options = {item["domain"]: item for item in scenario["technology_options"]}
    for item in config["components"]:
        kind = item["id"]
        if kind in {"integration", "contingency"}:
            continue
        connections = [ids["interconnect"]] if kind != "interconnect" else [
            ids[c["id"]] for c in config["components"]
            if c["id"] not in {"interconnect", "facility", "integration", "contingency"}]
        if kind == "facility":
            connections = [ids[key] for key in ("compute-cpu", "compute-accelerator", "pilot", "storage")]
        domain = {"compute-cpu": "compute", "compute-accelerator": "compute", "pilot": "memory", "management": "system-software"}.get(kind, kind)
        candidate = options.get(domain)
        role_ja = candidate["role"] if candidate else {
            "storage": "データ取り込み、一時保存、長期保存の要件から容量・帯域と階層構成を検討します。",
            "facility": "受電、電力密度、液冷、既存設備との共用範囲と改修費を確認します。",
        }[kind]
        role_en = candidate["role_en"] if candidate else {
            "storage": "Plan capacity, bandwidth, and tiers from ingestion, scratch, and retention requirements.",
            "facility": "Verify power supply, density, liquid cooling, shared infrastructure, and retrofit costs.",
        }[kind]
        components.append({
            "component_id": ids[kind], "component_type": kind,
            "label_ja": item["label_ja"], "label_en": item["label_en"],
            "quantity": None, "unit_ja": item["unit_ja"], "unit_en": item["unit_en"],
            "role_ja": role_ja, "role_en": role_en,
            "connection_ids": connections,
        })
    return {
        "option_id": f"BUD-{key}-{ceiling}", "tier": tier,
        "label_ja": f"{ceiling:,}億円", "label_en": f"JPY {ceiling / 10:g}B",
        "budget_range_oku_jpy": {"lower": ceiling, "reference": ceiling, "upper": ceiling},
        "estimate_method_ja": "設計方針ごとに仮配分した初期整備予算です。契約価格の推定ではなく、機器単価と施設条件の検証が済むまで数量・TCOは未算出とします。",
        "estimate_method_en": "An initial budget allocation for this design strategy, not an estimated contract price. Quantities and TCO remain unknown until component pricing and facility constraints are validated.",
        "confidence": "low",
        "reference_case_ids": [r["case_id"] for r in REFERENCE_CASES],
        "budget_allocation": allocation, "components": components,
        "aggregate": {"cpu_nodes": None, "accelerator_nodes": None, "accelerators": None,
                      "storage_pb": None, "facility_class_ja": "既存設備・改修範囲を要確認",
                      "facility_class_en": "Existing facilities and required work need verification"},
        "caveat_ja": "概念構成図です。数量・容量・実現可能性は未確認で、予算配分額は推定費用やベンダー見積りではありません。施設・電力・冷却条件と独立検証を確認してから構成規模を算出します。",
        "caveat_en": "Conceptual topology. Quantities, capacity, and feasibility are unverified; allocations are neither cost estimates nor vendor quotes. Sizing requires facility, power, cooling, and independent validation evidence.",
    }


def main() -> int:
    payload = json.loads(PATH.read_text(encoding="utf-8"))
    config = json.loads((ROOT / "config/budget-planning.json").read_text(encoding="utf-8"))
    payload["budget_reference_cases"] = REFERENCE_CASES
    for scenario in payload["scenarios"]:
        scenario_id = scenario["scenario_id"]
        predecessor = f"{scenario_id}@{scenario['plan_version']}"
        if scenario["plan_version"] != "0.5" and predecessor not in scenario["supersedes"]:
            scenario["supersedes"].append(predecessor)
        scenario["plan_version"] = "0.5"
        scenario["effective_from"] = "2026-08-30"
        scenario["budget_options"] = [
            build_option(scenario, ceiling, config)
            for ceiling in config["budget_ceilings_oku_jpy"]
        ]
        scenario["publication"] = {
            "information_classification": "public", "publication_approved": True,
            "publication_decision_id": "PUBDEC-20260830-001",
            "human_approval_directive_id": "DIR-900013",
            "approved_at": "2026-08-30T16:56:26+09:00",
        }
    PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
