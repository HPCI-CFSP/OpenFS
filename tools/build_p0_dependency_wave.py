#!/usr/bin/env python3
"""Maintain post-baseline roadmap edges in the public dependency register."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "knowledge/public/dependencies/p0-roadmap-dependencies.json"
EDGE_IDS = {
    "XDEP-FACILITY-BLUE",
    "XDEP-RUNTIME-BLUE",
    "XDEP-WORKFLOW-BLUE",
    "XDEP-SECURITY-BLUE",
    "XDEP-AI-BLUE",
    "XDEP-PROCUREMENT-BLUE",
    "XDEP-OPERATIONS-BLUE",
    "XDEP-HORIZON-BLUE",
    "XDEP-SOVEREIGNTY-BLUE",
    "XDEP-PERFORMANCE-BLUE",
    "XDEP-REALTIME-BLUE",
    "XDEP-ADOPTION-BLUE",
}


def edge(eid, upstream, relationship, criticality, ja, en, impact_ja, impact_en,
         risk_ja, risk_en, source_ids, source_dependency_id, gate_ref):
    return {
        "dependency_id": eid,
        "upstream_roadmap_id": upstream,
        "downstream_roadmap_id": "RM-X-BLUEPRINT",
        "relationship": relationship,
        "criticality": criticality,
        "basis": "openfs-assessment",
        "statement_ja": ja,
        "statement_en": en,
        "decision_impact_ja": impact_ja,
        "decision_impact_en": impact_en,
        "risk_if_late_ja": risk_ja,
        "risk_if_late_en": risk_en,
        "source_ids": source_ids,
        "source_dependency_ids": [source_dependency_id],
        "gate_refs": [gate_ref],
        "coverage_gap_refs": [],
    }


EDGES = [
    edge("XDEP-FACILITY-BLUE", "RM-HW-FACILITY", "constrains", "high",
         "施設工程と電力・冷却上限が導入可能な構成と時期を制約する。",
         "Facility schedules and power/cooling limits constrain feasible architecture and timing.",
         "ラック密度、段階導入、試運転の前提としてセンター別条件を明示する。",
         "Make center conditions explicit for rack density, staged deployment, and commissioning.",
         "条件確定が遅れると、計算機と施設の再設計が必要になる。",
         "Late constraints can force compute and facility redesign.",
         ["SRC-OPENFS-P0-PLAN", "SRC-BLUE043"], "DEP-FACILITY-BLUEPRINT", "MS-FACILITY-REQ-BASELINE"),
    edge("XDEP-RUNTIME-BLUE", "RM-SSW-RUNTIME", "enables", "high",
         "通信・ランタイムの相互運用が候補ハードウェアの実利用を可能にする。",
         "Communication and runtime interoperability enables practical use of candidate hardware.",
         "CPU、GPU、NIC、MPI、集合通信、スケジューラを一体で受入評価する。",
         "Accept CPU, GPU, NIC, MPI, collectives, and scheduling as a stack.",
         "ソフトウェア対応が遅れると、利用可能な性能と移行期間を過大評価する。",
         "Late software support can overstate usable performance and understate migration time.",
         ["SRC-OPENFS-P0-PLAN", "SRC-PORT014"], "DEP-RUNTIME-BLUEPRINT", "MS-RUNTIME-2026-BASELINE"),
    edge("XDEP-WORKFLOW-BLUE", "RM-SSW-WORKFLOW", "enables", "high",
         "再開可能な実行経路とデータ経路が複合ワークロードの運用を可能にする。",
         "Restartable execution and data paths enable operation of mixed workloads.",
         "シミュレーション、AI、実験連携を個別機能ではなく一連のサービスとして評価する。",
         "Evaluate simulation, AI, and experimental integration as an end-to-end service.",
         "実証が遅れると、データ転送と再実行の費用・停止時間が計画から漏れる。",
         "Late demonstrations can omit transfer, rerun cost, and interruption from planning.",
         ["SRC-OPENFS-P0-PLAN", "SRC-CDO075"], "DEP-WORKFLOW-BLUEPRINT", "MS-WORKFLOW-2026-BASELINE"),
    edge("XDEP-SECURITY-BLUE", "RM-SSW-SECURITY", "constrains", "high",
         "信頼境界と受入基準が扱えるデータ区分と構成を制約する。",
         "Trust boundaries and acceptance criteria constrain data classes and deployable architectures.",
         "認証、認可、監査、機密計算の責任と性能影響を構成案へ反映する。",
         "Reflect identity, authorization, audit, confidential-computing ownership, and performance impact.",
         "後付けすると互換性、鍵管理、運用責任の再設計が必要になる。",
         "Retrofitting can require redesign of interoperability, key management, and ownership.",
         ["SRC-OPENFS-P0-PLAN", "SRC-CDO039"], "DEP-SECURITY-BLUEPRINT", "MS-SECURITY-2026-BASELINE"),
    edge("XDEP-AI-BLUE", "RM-APP-AI", "informs", "high",
         "AI負荷の実測と正答条件が計算・メモリ・ネットワーク・ストレージ要件を知らせる。",
         "Measured AI workloads and correctness requirements inform compute, memory, network, and storage needs.",
         "学習、推論、エージェント処理を異なる負荷として構成案へ割り当てる。",
         "Assign training, inference, and agent execution as distinct workloads in planning options.",
         "測定が遅れると、ピーク演算値だけでAI適性を誤判定する。",
         "Late measurement can misjudge AI fitness from peak arithmetic alone.",
         ["SRC-OPENFS-P0-PLAN", "SRC-AIP001", "SRC-AIP002"], "DEP-AI-BLUEPRINT", "MS-AI-STACK-2026"),
    edge("XDEP-PROCUREMENT-BLUE", "RM-X-PROCUREMENT", "constrains", "high",
         "予算境界、契約期間、保守、施設費が実現可能なシステム規模を制約する。",
         "Budget boundaries, contract terms, support, and facility cost constrain feasible system scale.",
         "総額ではなく同じ5年費用境界で複数案を比較する。",
         "Compare options using matched five-year cost boundaries rather than total award alone.",
         "費用内訳が遅れると、計算資源規模を過大評価する。",
         "Late itemization can overstate feasible compute capacity.",
         ["SRC-OPENFS-P0-PLAN", "SRC-PRP001", "SRC-PRP003"], "DEP-PROCUREMENT-BLUEPRINT", "MS-PROCUREMENT-2026-BASELINE"),
    edge("XDEP-OPERATIONS-BLUE", "RM-X-OPERATIONS", "enables", "high",
         "連合アクセスと継続運用の責任分担が計画案を実サービスにする。",
         "Federated access and continuity ownership turn architecture options into operable services.",
         "申請、配分、支援、障害、移行、データ継続を構成案ごとに確認する。",
         "Check requests, allocation, support, incidents, migration, and data continuity per option.",
         "責任分担が遅れると、技術的に稼働しても共通サービスとして提供できない。",
         "Late ownership decisions can prevent a technically working system from becoming a common service.",
         ["SRC-OPENFS-P0-PLAN", "SRC-CDO065", "SRC-BLUE042"], "DEP-OPERATIONS-BLUEPRINT", "MS-OPERATIONS-2026-BASELINE"),
    edge("XDEP-HORIZON-BLUE", "RM-X-HORIZON", "informs", "medium",
         "技術・供給・政策シグナルが計画案の前提と再検討時期を知らせる。",
         "Technology, supply, and policy signals inform assumptions and reconsideration dates.",
         "採用済み前提と新規候補を区別し、変更履歴と反対意見を残す。",
         "Separate adopted assumptions from candidates and retain change history and dissent.",
         "監視が遅れると、陳腐化した前提のまま判断時点を迎える。",
         "Late monitoring can leave obsolete assumptions in place at decision time.",
         ["SRC-OPENFS-P0-PLAN", "SRC-CDX001", "SRC-CDX007"], "DEP-HORIZON-BLUEPRINT", "MS-HORIZON-2026-BASELINE"),
]


REMAINING_EDGES = [
    edge("XDEP-SOVEREIGNTY-BLUE", "RM-HW-SOVEREIGNTY", "constrains", "high",
         "供給能力、認定、保守、代替経路が導入時期と構成の可逆性を制約する。",
         "Capacity, qualification, support, and alternatives constrain deployment timing and architectural reversibility.",
         "候補部品を出自だけで評価せず、供給量、認定、保守、代替時の再設計を計画案へ反映する。",
         "Reflect volume, qualification, support, and redesign under substitution rather than judging components by origin alone.",
         "供給証拠が遅れると、量産目標を調達可能な数量・時期と誤認する。",
         "Late supply evidence can cause production targets to be mistaken for procurable volume and dates.",
         ["SRC-OPENFS-REMAINING-PLAN", "SRC-CDX001", "SRC-CDX007"],
         "DEP-SOVEREIGNTY-BLUEPRINT", "MS-SOVEREIGNTY-GATE-2027Q2"),
    edge("XDEP-PERFORMANCE-BLUE", "RM-SSW-PERFORMANCE", "informs", "high",
         "実効性能、電力、待ち時間、失敗の観測が候補構成の比較と運用条件を知らせる。",
         "Observed performance, power, queueing, and failures inform candidate comparison and operating conditions.",
         "ピーク値だけでなく、同一入力・計測境界による性能と電力を計画案へ反映する。",
         "Use performance and power from matched inputs and measurement boundaries, not peak values alone.",
         "観測契約が遅れると、個別研究結果を本番SLOへ誤って一般化する。",
         "Late observability contracts can cause isolated research results to be generalized into production SLOs.",
         ["SRC-OPENFS-REMAINING-PLAN", "SRC-CDS376"],
         "DEP-PERFORMANCE-BLUEPRINT", "MS-PERFORMANCE-CONTRACT-2027Q2"),
    edge("XDEP-REALTIME-BLUE", "RM-APP-REALTIME", "informs", "high",
         "実験・緊急・量子ユースケースの期限、データ率、正答条件がサービス構成を知らせる。",
         "Deadlines, data rates, and correctness conditions for experimental, urgent, and quantum use cases inform service architecture.",
         "取得、転送、計算、判断、復旧を一つのエンドツーエンド経路として評価する。",
         "Evaluate acquisition, transfer, computation, decision, and recovery as one end-to-end path.",
         "ユースケース契約が遅れると、個別要素の速度からサービス能力を過大評価する。",
         "Late use-case contracts can overstate service capability from component speed.",
         ["SRC-OPENFS-REMAINING-PLAN", "SRC-CDS397", "SRC-CDS455"],
         "DEP-REALTIME-BLUEPRINT", "MS-REALTIME-GATE-2027Q2"),
    edge("XDEP-ADOPTION-BLUE", "RM-APP-ADOPTION", "enables", "high",
         "移行支援、技能、保守責任、終了条件が候補構成を継続利用可能なサービスにする。",
         "Migration support, skills, stewardship, and exit conditions make candidate architectures sustainable services.",
         "主要ソフトウェアの移植・検証・支援工数と責任者を導入工程へ反映する。",
         "Reflect porting, validation, support effort, and ownership for critical software in deployment schedules.",
         "準備が遅れると、機器稼働後も利用者が移行できず、保守不能な構成が残る。",
         "Late readiness can leave users unable to migrate and software unsupported after hardware starts operating.",
         ["SRC-OPENFS-REMAINING-PLAN", "SRC-PORT052", "SRC-CDO066"],
         "DEP-ADOPTION-BLUEPRINT", "MS-ADOPTION-GATE-2027Q2"),
]


def main():
    payload = json.loads(PATH.read_text(encoding="utf-8"))
    payload["as_of"] = "2026-09-06"
    payload["title_ja"] = "公開ロードマップ間の依存関係一覧"
    payload["title_en"] = "Public cross-roadmap dependency register"
    payload["summary_ja"] = "19本の公開ロードマップ間の依存関係を整理した暫定版です。技術、供給網、施設、ソフトウェア、アプリケーション、調達、運用、利用支援、継続監視から参照構成までの判断経路を示します。独立レビューは未完了です。"
    payload["summary_en"] = "A provisional register connecting 19 published roadmaps across technology, supply chain, facilities, software, applications, procurement, operations, adoption, and horizon scanning to the reference blueprint. Independent review remains incomplete."
    payload["dependencies"] = [
        item for item in payload["dependencies"]
        if item["dependency_id"] not in EDGE_IDS
    ] + EDGES + REMAINING_EDGES
    for constraint in payload["external_constraints"]:
        if constraint["constraint_id"] == "EXT-FACILITY":
            constraint["impact_ja"] = "計算・ネットワーク・メモリ密度と段階導入を制約する。専用施設ロードマップに富岳NEXTの公開工程を取り込んだが、全センターを同じ境界で比較できる電力・冷却・水使用・増設余地のデータは未完了である。"
            constraint["impact_en"] = "These factors constrain compute, network, and memory density as well as staged deployment. The facility roadmap includes the public FugakuNEXT schedule, but matched power, cooling, water, and expansion-headroom data for all centers remain incomplete."
    payload["publication"] = {
        "information_classification": "public",
        "publication_approved": True,
        "publication_decision_id": "PUBDEC-RESEARCH-READINESS-20260906-001",
        "human_approval_directive_id": "DIR-900104",
    }
    PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
