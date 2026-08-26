#!/usr/bin/env python3
"""Add reproducible budget-scaled architecture estimates to planning options."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "roadmaps/scenarios/accepted/hpci-p0-scenarios.json"

BUDGETS = {
    "ume": (40, 50, 70, "最小構成（梅）", "Minimum option (Ume)"),
    "take": (300, 400, 500, "基準構成（竹）", "Reference option (Take)"),
    "matsu": (1000, 1300, 1500, "拡張構成（松）", "Expanded option (Matsu)"),
}

REFERENCE_CASES = [
    {
        "case_id": "BREF-HPCI-AI-2025",
        "name_ja": "HPCI戦略プログラム向けAI計算資源増強",
        "name_en": "AI compute enhancement for the HPCI strategic program",
        "budget_oku_jpy": 50,
        "scope_ja": "1課題あたりの支援上限。装置費だけとは限らない。",
        "scope_en": "Maximum support per project; not necessarily hardware-only cost.",
        "configuration_ja": "1課題あたり約500 GPU、AI計算性能4〜5 EFLOPSを想定。",
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
        "configuration_ja": "公開資料はAI計算性能6.22 EFLOPSの整備を示す。",
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
        "scope_ja": "開発・製造等を含む総事業費の公表規模。",
        "scope_en": "Published total program scale including development and manufacture.",
        "configuration_ja": "フラッグシップ級システムと開発を含む。",
        "configuration_en": "Includes a flagship-scale system and development program.",
        "source_title": "スーパーコンピュータ「富岳」成果と今後の展開",
        "source_publisher": "文部科学省",
        "source_url": "https://www.mext.go.jp/content/20220120-mxt_jyohoka01-000019552_05.pdf",
        "public_date": "2022-01-20",
        "comparability_note_ja": "独自CPU開発を含む国家プロジェクトであり、市販GPUシステムの調達費とは比較できない。",
        "comparability_note_en": "This national program includes custom CPU development and is not directly comparable with commercial-GPU procurement.",
    },
    {
        "case_id": "BREF-RIKEN-AIFS-2026",
        "name_ja": "理研AI for Science Supercomputer",
        "name_en": "RIKEN AI for Science Supercomputer",
        "budget_oku_jpy": None,
        "scope_ja": "公開構成の参照例。契約金額の根拠には用いない。",
        "scope_en": "Public topology reference; not used as a contract-price basis.",
        "configuration_ja": "400計算ノード、計1,600 GPU、XDR 800Gbps fat-tree、1.08PB実効NVMe Lustre。",
        "configuration_en": "400 compute nodes, 1,600 GPUs, XDR 800Gbps fat-tree, and 1.08PB effective all-NVMe Lustre.",
        "source_title": "AI-for-Science-Supercomputer README",
        "source_publisher": "RIKEN R-CCS",
        "source_url": "https://github.com/RIKEN-RCCS/AI-for-Science-Supercomputer",
        "public_date": "2026-08-27",
        "comparability_note_ja": "構成図の表現とノード内GPU数の参照に限り、将来価格や性能を外挿しない。",
        "comparability_note_en": "Used only for topology presentation and GPUs per node, not to extrapolate future price or performance.",
    },
]

SIZES = {
    "SCN-HPCI-BALANCED-001": {
        "ume": (96, 96, 384, 8, 10),
        "take": (1024, 512, 2048, 32, 50),
        "matsu": (8192, 2048, 8192, 128, 200),
    },
    "SCN-HPCI-AI-DATA-001": {
        "ume": (32, 112, 448, 8, 15),
        "take": (256, 768, 3072, 32, 80),
        "matsu": (1024, 2560, 10240, 96, 300),
    },
    "SCN-HPCI-STAGED-001": {
        "ume": (64, 64, 256, 16, 10),
        "take": (512, 320, 1280, 64, 50),
        "matsu": (4096, 1536, 6144, 256, 200),
    },
}


def component(
    component_id: str,
    component_type: str,
    label_ja: str,
    label_en: str,
    quantity: float,
    unit_ja: str,
    unit_en: str,
    role_ja: str,
    role_en: str,
    connections: list[str],
) -> dict[str, Any]:
    return {
        "component_id": component_id,
        "component_type": component_type,
        "label_ja": label_ja,
        "label_en": label_en,
        "quantity": quantity,
        "unit_ja": unit_ja,
        "unit_en": unit_en,
        "role_ja": role_ja,
        "role_en": role_en,
        "connection_ids": connections,
    }


def build_option(scenario_id: str, tier: str, values: tuple[int, int, int, int, int]) -> dict[str, Any]:
    cpu_nodes, accelerator_nodes, accelerators, pilot_nodes, storage_pb = values
    key = scenario_id.removeprefix("SCN-HPCI-").removesuffix("-001").replace("-", "")
    prefix = f"{key}-{tier}".upper()
    lower, reference, upper, label_ja, label_en = BUDGETS[tier]
    facility_ja = {"ume": "既存の液冷対応センター増強", "take": "大規模センター増築・電力増強", "matsu": "専用施設を含むフラッグシップ級"}[tier]
    facility_en = {"ume": "Existing liquid-cooled center expansion", "take": "Major center and power expansion", "matsu": "Flagship class including dedicated facilities"}[tier]
    fabric_label_ja = "二面化した標準fabric"
    fabric_label_en = "Dual-plane standards-based fabric"
    if "AI-DATA" in scenario_id:
        fabric_label_ja = "高帯域scale-up＋scale-out fabric"
        fabric_label_en = "High-bandwidth scale-up and scale-out fabrics"
    if "STAGED" in scenario_id:
        fabric_label_ja = "本番fabric＋分離された実証fabric"
        fabric_label_en = "Production fabric plus isolated pilot fabric"
    ids = {name: f"BCMP-{prefix}-{name}" for name in ("CPU", "ACC", "PILOT", "NET", "STORAGE", "MGMT", "FACILITY")}
    components = [
        component(ids["CPU"], "compute-cpu", "汎用・HPC CPU区画", "General-purpose and HPC CPU partition", cpu_nodes, "ノード", "nodes", "CPU・大容量メモリ・既存HPCアプリ", "CPU, capacity-memory, and existing HPC applications", [ids["NET"]]),
        component(ids["ACC"], "compute-accelerator", "GPU・アクセラレータ区画", "GPU and accelerator partition", accelerator_nodes, "ノード", "nodes", f"計{accelerators:,}基を想定するAI/HPC演算", f"AI/HPC compute assuming {accelerators:,} accelerators", [ids["NET"]]),
        component(ids["PILOT"], "pilot", "大容量メモリ・新技術評価区画", "Large-memory and emerging-technology pilot", pilot_nodes, "ノード", "nodes", "CXL、PIM、wafer-scale等を本番と分離して評価", "Evaluate CXL, PIM, wafer-scale, and other options outside production", [ids["NET"]]),
        component(ids["NET"], "interconnect", fabric_label_ja, fabric_label_en, 2, "面", "planes", "計算、データ、管理を故障領域と用途に応じて接続", "Connect compute, data, and management by fault domain and use", [ids["CPU"], ids["ACC"], ids["PILOT"], ids["STORAGE"], ids["MGMT"]]),
        component(ids["STORAGE"], "storage", "階層型共有ストレージ", "Tiered shared storage", storage_pb, "PB（概算）", "PB (estimate)", "NVMe層、容量層、アーカイブ連携", "NVMe tier, capacity tier, and archive integration", [ids["NET"]]),
        component(ids["MGMT"], "management", "ログイン・管理・可観測性", "Login, management, and observability", max(4, accelerator_nodes // 32), "ノード相当", "node equivalents", "認証、scheduler、監視、CI、データ転送", "Identity, scheduler, monitoring, CI, and data transfer", [ids["NET"]]),
        component(ids["FACILITY"], "facility", "施設・電力・冷却", "Facilities, power, and cooling", 1, "式", "facility", facility_ja, facility_en, [ids["CPU"], ids["ACC"], ids["PILOT"], ids["STORAGE"]]),
    ]
    return {
        "option_id": f"BUD-{prefix}",
        "tier": tier,
        "label_ja": label_ja,
        "label_en": label_en,
        "budget_range_oku_jpy": {"lower": lower, "reference": reference, "upper": upper},
        "estimate_method_ja": "公開された50億円・400億円・1,300億円級案件を予算規模の参照点とし、400ノード・4 GPU/ノードの公開構成を補助線に、戦略別の演算・network・storage・施設配分を置いたOpenFS分析値。",
        "estimate_method_en": "An OpenFS analytical estimate using published JPY 5B, 40B, and 130B program classes as budget anchors and the public 400-node, four-GPU-per-node topology as a structural reference, then allocating capacity by strategy across compute, network, storage, and facilities.",
        "confidence": "low",
        "reference_case_ids": ["BREF-HPCI-AI-2025", "BREF-ABCI30-2023", "BREF-FUGAKU-2022", "BREF-RIKEN-AIFS-2026"],
        "components": components,
        "aggregate": {
            "cpu_nodes": cpu_nodes,
            "accelerator_nodes": accelerator_nodes,
            "accelerators": accelerators,
            "storage_pb": storage_pb,
            "facility_class_ja": facility_ja,
            "facility_class_en": facility_en,
        },
        "caveat_ja": "ノード数と容量はベンダー見積り、調達仕様、性能保証ではない。物価、為替、装置世代、建屋、受電、保守、ソフトウェア、人件費で大きく変わるため、RFIとセンターProfileで置き換える。",
        "caveat_en": "Node counts and capacity are not vendor quotations, procurement specifications, or performance guarantees. Inflation, exchange rates, generation, buildings, power delivery, service, software, and staffing can materially change them; replace these estimates with RFI and center-profile evidence.",
    }


def main() -> int:
    payload = json.loads(PATH.read_text(encoding="utf-8"))
    payload["schema_version"] = "0.3.0"
    payload["budget_reference_cases"] = REFERENCE_CASES
    for scenario in payload["scenarios"]:
        scenario_id = scenario["scenario_id"]
        scenario["plan_version"] = "0.4"
        if f"{scenario_id}@0.3" not in scenario["supersedes"]:
            scenario["supersedes"].append(f"{scenario_id}@0.3")
        scenario["budget_options"] = [
            build_option(scenario_id, tier, SIZES[scenario_id][tier])
            for tier in ("ume", "take", "matsu")
        ]
        scenario["publication"] = {
            "information_classification": "public",
            "publication_approved": True,
            "publication_decision_id": "PUBDEC-20260827-003",
            "human_approval_directive_id": "DIR-900012",
            "approved_at": "2026-08-27T00:48:00+09:00",
        }
    PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
