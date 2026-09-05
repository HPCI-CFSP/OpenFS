#!/usr/bin/env python3
"""Build the four remaining provisional roadmap families from public evidence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

try:
    from .build_p0_roadmap_wave import (
        SOURCE_CLASS_MAP,
        dependency,
        gap,
        lane,
        milestone,
        track,
        undated,
    )
except ImportError:  # Direct script execution.
    from build_p0_roadmap_wave import (
        SOURCE_CLASS_MAP,
        dependency,
        gap,
        lane,
        milestone,
        track,
        undated,
    )


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "knowledge/public/roadmaps"
AS_OF = "2026-09-06"
DECISION_ID = "PUBDEC-RESEARCH-READINESS-20260906-001"
DIRECTIVE_ID = "DIR-900105"
OPENFS_SOURCE = {
    "source_id": "SRC-OPENFS-REMAINING-PLAN",
    "title": "OpenFS Roadmap Portfolio",
    "publisher": "OpenFS",
    "url": "https://github.com/HPCI-CFSP/OpenFS/blob/main/docs/planning/roadmap-portfolio.md",
    "source_class": "openfs-governance",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def source_registry() -> dict[str, dict[str, Any]]:
    payload = load_json(ROOT / "knowledge/public/topic-decision-support.json")
    return {item["source_id"]: item for item in payload["sources"]}


def roadmap_source(source: dict[str, Any]) -> dict[str, Any]:
    value = {
        "source_id": source["source_id"],
        "title": source["title"],
        "publisher": source["publisher"],
        "url": source["url"],
        "source_class": SOURCE_CLASS_MAP[source["source_class"]],
    }
    published = source.get("published_at")
    if published:
        value["published_at"] = published
    return value


def common(spec: dict[str, Any], sources: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema_version": "0.2.0",
        "export_id": spec["export_id"],
        "roadmap_id": spec["roadmap_id"],
        "status": "published",
        "domain": spec["domain"],
        "slug": spec["slug"],
        "as_of": AS_OF,
        "title_ja": spec["title_ja"],
        "title_en": spec["title_en"],
        "summary_ja": spec["summary_ja"],
        "summary_en": spec["summary_en"],
        "horizon": {
            "start_year": 2024,
            "end_year": 2032,
            "extension_policy": "extend-to-latest-dated-evidence",
        },
        "timeline_granularity": "quarter",
        "research_status": "provisional",
        "coverage_status": "official-source-scan-incomplete",
        "consensus_status": "incomplete",
        "groups": spec["groups"],
        "tracks": spec["tracks"],
        "lanes": spec["lanes"],
        "dependencies": spec["dependencies"],
        "sources": sources,
        "coverage_gaps": spec["coverage_gaps"],
        "caveat_ja": "単一のAIモデル・単一エージェントによる暫定調査です。独立したAIモデルによるConsensus Gateは未完了です。公表された実績、組織・企業の目標、OpenFSの暫定判断点を区別し、未公表の時期、性能、費用は推測していません。",
        "caveat_en": "Provisional research by one model and one agent; the Consensus Gate using independent models is incomplete. Observed events, organization or vendor targets, and provisional OpenFS gates are separated, and unpublished timing, performance, and cost are not inferred.",
        "publication": {
            "information_classification": "public",
            "publication_approved": True,
            "publication_decision_id": DECISION_ID,
            "human_approval_directive_id": DIRECTIVE_ID,
        },
    }


def specifications() -> list[dict[str, Any]]:
    p = OPENFS_SOURCE["source_id"]
    return [
        {
            "filename": "supply-sovereignty-lifecycle.json",
            "export_id": "SOVEREIGNTY-ROADMAP-EXPORT-001",
            "roadmap_id": "RM-HW-SOVEREIGNTY",
            "domain": "hardware",
            "slug": "hardware/supply-sovereignty-lifecycle",
            "title_ja": "供給網・技術主権・ライフサイクル",
            "title_en": "Supply chain, technology sovereignty, and lifecycle",
            "summary_ja": "半導体・実装技術の供給集中、国内の研究開発、量産目標、保守・代替経路を調達判断へ接続する暫定ロードマップです。国内技術を優先して確認しますが、国名だけで採否を判断せず、供給能力、認定、保守、国際的な相互依存を分けて扱います。",
            "summary_en": "A provisional roadmap connecting semiconductor and packaging concentration, Japanese R&D, production targets, support, and alternatives to procurement decisions. Japanese technologies receive priority attention, while origin alone is not an adoption criterion; capacity, qualification, support, and global interdependence remain separate.",
            "source_keys": ["SRC-CDX001", "SRC-CDX007", "SRC-CDX008", "SRC-HW1-RAPIDUS-FY26", "SRC-CDX023"],
            "groups": [
                {"group_id": "supply", "name_ja": "供給網・リスク", "name_en": "Supply chain and risk"},
                {"group_id": "domestic", "name_ja": "国内開発・実用化", "name_en": "Japanese development and adoption"},
            ],
            "tracks": [
                track("SOVEREIGNTY-SUPPLY", "supply", "供給集中・代替・保守", "Concentration, alternatives, and support", "工程別・製品別の依存関係と代替可能性を追跡します。", "Track dependencies and substitutability by value-chain stage and product.", "OECDとNISTの資料は、半導体の相互依存と供給網リスク管理を示しますが、個別製品の供給確約ではありません。", "OECD and NIST materials describe semiconductor interdependence and supply-chain risk management, but do not constitute supply commitments for specific products.", "採用候補ごとに供給者、製造拠点、認定、保守期間、代替時の再設計を確認します。", "For each candidate, verify suppliers, production locations, qualification, support horizon, and redesign required by substitution.", ["SRC-CDX001", "SRC-CDX007"]),
                track("SOVEREIGNTY-DOMESTIC", "domestic", "国内技術の試作から供給へ", "From Japanese prototypes to supply", "研究、試作、パイロット、量産、システム認定を別の段階として扱います。", "Treat research, prototypes, pilots, production, and system qualification as distinct stages.", "Rapidusは2nmパイロットラインと2027年量産目標を公表し、NEDOはPost-5G事業を2029年まで実施しています。目標は認定済みHPCI部品の納期ではありません。", "Rapidus reports a 2 nm pilot line and a 2027 mass-production target, while NEDO runs the Post-5G program through 2029. These targets are not delivery dates for HPCI-qualified parts.", "国内技術を候補に含める場合も、実測、量産能力、歩留まり、ソフトウェア、保守、代替策を同じゲートで評価します。", "When Japanese technology is included, evaluate measurements, production capacity, yield, software, support, and alternatives under the same gates.", ["SRC-CDX008", "SRC-HW1-RAPIDUS-FY26", "SRC-CDX023"]),
            ],
            "lanes": [
                lane("LANE-SOVEREIGNTY-GLOBAL", "SOVEREIGNTY-SUPPLY", "OECD and NIST", "国際供給網の基準資料", "Global supply-chain baseline", [
                    milestone("MS-SOVEREIGNTY-NIST-2024Q4", 2024, "Q4", "quarter", "published", "standard", "as-of-baseline", "NIST供給網リスク管理文書", "NIST supply-chain risk guidance", "組織の供給網リスク管理を扱う基準資料です。特定地域・企業の優劣を示すものではありません。", "A baseline for organizational supply-chain risk management; it does not rank specific regions or suppliers.", ["SRC-CDX007"]),
                    milestone("MS-SOVEREIGNTY-OECD-2025", 2025, None, "year", "published", "policy", "as-of-baseline", "OECD半導体バリューチェーン分析", "OECD semiconductor value-chain analysis", "工程・製品によって依存関係が異なることを示す分析です。個別部品の現在在庫や納期ではありません。", "An analysis showing that dependencies vary by stage and product; it is not current inventory or lead-time evidence for individual parts.", ["SRC-CDX001"]),
                ]),
                lane("LANE-SOVEREIGNTY-JAPAN", "SOVEREIGNTY-DOMESTIC", "Rapidus and NEDO projects", "国内研究開発・供給目標", "Japanese R&D and supply targets", [
                    milestone("MS-SOVEREIGNTY-RAPIDUS-PILOT-2025Q2", 2025, "Q2", "quarter", "pilot", "product", "observed", "2nmパイロットライン開始", "2 nm pilot-line start", "Rapidusの公表では2025年4月にパイロットラインが開始しました。量産能力や顧客認定とは区別します。", "Rapidus states that its pilot line began in April 2025; this is distinct from production capacity and customer qualification.", ["SRC-HW1-RAPIDUS-FY26"]),
                    milestone("MS-SOVEREIGNTY-RAPIDUS-FY26-2026Q2", 2026, "Q2", "quarter", "published", "policy", "observed", "FY2026計画・予算承認", "FY2026 plan and budget approval", "一般向けPDK、RCSパイロットライン、2.xD/3D実装検証が計画されています。各成果の完了時期はこの承認日から推測しません。", "The plan covers a general PDK, RCS pilot line, and 2.xD/3D packaging verification. Completion dates are not inferred from the approval date.", ["SRC-HW1-RAPIDUS-FY26"]),
                    milestone("MS-SOVEREIGNTY-RAPIDUS-2027", 2027, None, "year", "target", "product", "vendor-target", "2nm量産目標", "2 nm mass-production target", "企業が公表した年単位の目標です。四半期、歩留まり、供給量、HPCI向け認定は未公表です。", "A vendor-published year-level target; quarter, yield, volume, and HPCI qualification are not public.", ["SRC-HW1-RAPIDUS-FY26"]),
                    milestone("MS-SOVEREIGNTY-NEDO-2029", 2029, None, "year", "target", "policy", "policy-target", "Post-5G事業期間の終点", "End of the Post-5G program period", "NEDOが示す事業期間の終点です。すべての研究成果が同年に製品化されることを意味しません。", "The program-period endpoint stated by NEDO; it does not mean every R&D output becomes a product in that year.", ["SRC-CDX008"]),
                    milestone("MS-SOVEREIGNTY-GATE-2027Q2", 2027, "Q2", "quarter", "decision-gate", "hpci-evaluation", "openfs-provisional-plan", "候補別の供給・保守証拠ゲート", "Candidate supply and support evidence gate", "供給能力、認定状況、保守期間、代替経路を確認できた候補だけを計画案の数量検討へ進めるOpenFS上の暫定判断点です。", "A provisional OpenFS gate that advances only candidates with evidenced capacity, qualification, support horizon, and alternatives to sizing analysis.", [p, "SRC-CDX001", "SRC-CDX007"]),
                ]),
            ],
            "dependencies": [dependency("DEP-SOVEREIGNTY-BLUEPRINT", "constrains", "RM-HW-SOVEREIGNTY", "RM-X-BLUEPRINT", "供給能力、認定、保守、代替経路が導入時期と構成の可逆性を制約します。", "Capacity, qualification, support, and alternatives constrain deployment timing and architectural reversibility.", [p, "SRC-CDX001", "SRC-CDX007"])],
            "coverage_gaps": [
                gap("GAP-SOVEREIGNTY-001", "P1", "候補部品ごとの供給量・認定・リードタイム", "Candidate component capacity, qualification, and lead time", "量産目標を調達可能な数量と時期へ変換できません。", "Production targets cannot be translated into procurable volume and timing.", "供給者の認定資料、供給確約、保守契約、代替時の再設計を候補別に収集します。", "Collect qualification, supply commitments, support contracts, and substitution redesign by candidate."),
                gap("GAP-SOVEREIGNTY-002", "P1", "国内外候補を同じ条件で比較する実測", "Matched measurements for Japanese and international candidates", "出自と実用性を混同する恐れがあります。", "Origin may be conflated with practical readiness.", "同一アプリケーション、電力境界、ソフトウェア版、保守期間で比較します。", "Compare identical applications, power boundaries, software versions, and support periods."),
            ],
        },
        {
            "filename": "observability-performance-power.json",
            "export_id": "PERFORMANCE-ROADMAP-EXPORT-001",
            "roadmap_id": "RM-SSW-PERFORMANCE",
            "domain": "system-software",
            "slug": "system-software/observability-performance-power",
            "title_ja": "可観測性・性能工学・電力適応運用",
            "title_en": "Observability, performance engineering, and power-aware operations",
            "summary_ja": "ジョブ、通信、I/O、電力・冷却の観測を性能モデルと運用制御へ接続する暫定ロードマップです。研究上の電力制御結果と、センター全体で安全に運用できる制御を区別します。",
            "summary_en": "A provisional roadmap connecting job, communication, I/O, power, and cooling telemetry to performance models and operational controls. Research power-capping results are separated from controls proven safe for center-wide operation.",
            "source_keys": ["SRC-CDS376", "SRC-CDS426", "SRC-CDO055"],
            "groups": [
                {"group_id": "measurement", "name_ja": "計測・性能モデル", "name_en": "Measurement and performance models"},
                {"group_id": "control", "name_ja": "電力適応運用", "name_en": "Power-aware operations"},
            ],
            "tracks": [
                track("PERFORMANCE-OBSERVABILITY", "measurement", "共通テレメトリと再現測定", "Common telemetry and reproducible measurement", "性能、電力、待ち時間、失敗を同じ実行単位で記録します。", "Record performance, power, queueing, and failures for the same execution unit.", "既存資料は個別ツールやシステムの計測機能を示しますが、HPCI全体で共通の意味・粒度・保持期間は未確定です。", "Existing material documents measurement capabilities for individual tools and systems, but common HPCI-wide semantics, granularity, and retention are unresolved.", "候補構成を同じ入力、版、精度、計測境界で比較できる観測契約が必要です。", "Candidate systems need an observability contract with identical inputs, versions, correctness, and measurement boundaries.", [p, "SRC-CDO055"]),
                track("PERFORMANCE-POWER", "control", "ジョブ別電力制御と施設連携", "Per-job power control and facility coordination", "性能・エネルギー・期限の関係を負荷別に扱います。", "Treat performance, energy, and deadlines by workload.", "ORNLのGH200研究はタスク別の電力上限の有効性を示しますが、全負荷・全候補機・本番運用への一般化はできません。OCPの800 VDC資料は施設側の標準化活動です。", "ORNL's GH200 study shows task-specific power-cap effects, but cannot be generalized to every workload, platform, or production service. OCP's 800 VDC material concerns facility-side standardization.", "電力上限の安全性、性能劣化、復旧、施設負荷追従をアプリケーション別に検証します。", "Validate power-cap safety, performance impact, recovery, and facility-load following per application.", ["SRC-CDS376", "SRC-CDS426"]),
            ],
            "lanes": [
                lane("LANE-PERFORMANCE-RESEARCH", "PERFORMANCE-POWER", "ORNL and OCP", "公開された研究・標準化活動", "Published research and standardization", [
                    milestone("MS-PERFORMANCE-POWERCAP-2025Q2", 2025, "Q2", "quarter", "published", "research", "observed", "GH200電力上限制御の研究発表", "GH200 power-capping study", "200Wから1000Wの範囲を調べたタスク固有の研究結果です。センター共通の推奨値ではありません。", "A task-specific study spanning 200 W to 1000 W; it is not a center-wide recommended setting.", ["SRC-CDS376"]),
                    milestone("MS-PERFORMANCE-ORNL-PAGE-2026Q1", 2026, "Q1", "quarter", "published", "research", "as-of-baseline", "ORNL研究紹介の公開", "ORNL research highlight published", "研究紹介ページの公開時点であり、運用展開日ではありません。", "The publication date of the research highlight, not a production-deployment date.", ["SRC-CDS376"]),
                    milestone("MS-PERFORMANCE-OCP-2026Q3", 2026, "Q3", "quarter", "published", "standard", "as-of-baseline", "800 VDC標準化活動を確認", "800 VDC standardization activity checked", "OCPが業界活動を公表した時点です。仕様完成やHPCI施設への導入日ではありません。", "The date OCP described the industry effort; it is not specification completion or HPCI deployment.", ["SRC-CDS426"]),
                ]),
                lane("LANE-PERFORMANCE-OPENFS", "PERFORMANCE-OBSERVABILITY", "OpenFS", "共通観測・受入条件", "Common observability and acceptance", [
                    milestone("MS-PERFORMANCE-CONTRACT-2027Q2", 2027, "Q2", "quarter", "decision-gate", "hpci-evaluation", "openfs-provisional-plan", "性能・電力観測契約の暫定判断点", "Provisional performance and power observability gate", "入力、版、精度、計測区間、IT/施設電力境界、失敗を固定した比較形式を審査する暫定計画です。", "A provisional plan to review a comparison contract pinning input, version, correctness, timing interval, IT/facility power boundary, and failures.", [p, "SRC-CDS376", "SRC-CDO055"]),
                    undated("MS-PERFORMANCE-SLO-UNDATED", "undated", "hpci-evaluation", "共通SLOの採用時期は未確定", "Common SLO adoption is undated", "性能、期限、電力、失敗率の合否値は、人による承認と実測がないため設定していません。", "Pass/fail values for performance, deadlines, power, and failure rate remain unset pending measurements and human approval.", [p]),
                ]),
            ],
            "dependencies": [dependency("DEP-PERFORMANCE-BLUEPRINT", "informs", "RM-SSW-PERFORMANCE", "RM-X-BLUEPRINT", "実効性能、電力、待ち時間、失敗の観測が候補構成の比較と運用条件を知らせます。", "Observed performance, power, queueing, and failures inform candidate comparison and operating conditions.", [p, "SRC-CDS376"])],
            "coverage_gaps": [
                gap("GAP-PERFORMANCE-001", "P1", "候補機・センター間で共通の観測契約", "Common observability contract across candidates and centers", "個別資料の数値を同じ指標として比較できません。", "Values from separate sources cannot be compared as the same metric.", "入力、版、期間、計測境界、欠測、失敗を共通Schemaで記録します。", "Record input, version, period, measurement boundary, missing data, and failures in one schema."),
                gap("GAP-PERFORMANCE-002", "P1", "電力適応制御の負荷別安全性と利益", "Workload-specific safety and benefit of power-aware control", "研究結果を本番運用へ一般化できません。", "Research results cannot be generalized to production operation.", "代表負荷ごとに性能、エネルギー、熱、復旧、結果妥当性を測定します。", "Measure performance, energy, thermals, recovery, and correctness for each representative workload."),
            ],
        },
        {
            "filename": "realtime-experiment-quantum.json",
            "export_id": "REALTIME-ROADMAP-EXPORT-001",
            "roadmap_id": "RM-APP-REALTIME",
            "domain": "applications",
            "slug": "applications/realtime-experiment-quantum",
            "title_ja": "緊急・リアルタイム・実験連携・量子応用",
            "title_en": "Urgent, real-time, experimental, and quantum applications",
            "summary_ja": "実験データの即時処理、緊急計算、量子・HPC連携を、個別実証から継続サービスへ移す条件を整理する暫定ロードマップです。特定実験の速度や圧縮率を他用途へ一般化しません。",
            "summary_en": "A provisional roadmap for moving real-time experimental data processing, urgent computing, and quantum-HPC integration from individual demonstrations to sustained services. Speed and compression results from a specific experiment are not generalized to other uses.",
            "source_keys": ["SRC-CDS368", "SRC-CDS397", "SRC-CDS402", "SRC-CDS433", "SRC-CDS422", "SRC-CDS455"],
            "groups": [
                {"group_id": "experiment", "name_ja": "実験・リアルタイム処理", "name_en": "Experimental and real-time processing"},
                {"group_id": "quantum", "name_ja": "量子・HPC連携", "name_en": "Quantum-HPC integration"},
            ],
            "tracks": [
                track("REALTIME-EXPERIMENT", "experiment", "実験データの即時処理", "Real-time experimental data processing", "取得、圧縮、転送、解析、判断までの期限と障害処理を扱います。", "Cover acquisition, compression, transfer, analysis, decision deadlines, and failures.", "理研の圧縮技術、SPring-8とGakuNin RDMの試行、APSのAI画像処理実証が公表されています。対象データと測定条件は異なります。", "RIKEN compression, the SPring-8/GakuNin RDM trial, and an APS AI-imaging demonstration are public, with different data and measurement conditions.", "本番化にはデータ率、期限、再送、来歴、認証、障害時の手動経路をユースケース別に固定する必要があります。", "Production requires use-case-specific data rate, deadline, retry, provenance, identity, and manual fallback contracts.", ["SRC-CDS397", "SRC-CDS402", "SRC-CDS433"]),
                track("REALTIME-QUANTUM", "quantum", "量子アクセラレータとの連携", "Quantum-accelerator integration", "オンプレミス量子機、HPC資源、古典基準計算を一体で評価します。", "Evaluate on-premises quantum systems, HPC resources, and classical baselines together.", "ROQUOとORNL Pathfinderは運用開始が公表され、QuEraは2028年以降の製品目標を示しています。量子優位性やHPCI共通サービスは確立していません。", "ROQUO and ORNL Pathfinder have announced operation, while QuEra states targets from 2028. Quantum advantage and a common HPCI service are not established.", "量子回路だけでなく、前後処理、待ち時間、誤り、古典基準、利用者支援を含めます。", "Include preprocessing, postprocessing, queueing, error, classical baselines, and user support in addition to quantum circuits.", ["SRC-CDS368", "SRC-CDS422", "SRC-CDS455"]),
            ],
            "lanes": [
                lane("LANE-REALTIME-EXPERIMENT", "REALTIME-EXPERIMENT", "RIKEN and Argonne", "実験連携の公開実証", "Public experimental integration", [
                    milestone("MS-REALTIME-APS-2026Q2", 2026, "Q2", "quarter", "pilot", "research", "observed", "APS実時間AI画像処理実証", "APS real-time AI imaging demonstration", "特定データと構成による実証です。広範な本番提供時期は公表されていません。", "A demonstration for a specific dataset and configuration; no date for broad production availability is public.", ["SRC-CDS433"]),
                    milestone("MS-REALTIME-RIKEN-COMPRESS-2026Q2", 2026, "Q2", "quarter", "deployment", "hpci-adoption", "observed", "大容量実験データ圧縮の運用開始", "Operation of high-volume experimental-data compression", "公表された27 GB/s入力、平均約8,600分の1の圧縮、2〜3分転送は特定実験の結果です。", "The published 27 GB/s input, approximately 8,600-fold average compression, and two-to-three-minute transfer are specific to the reported experiment.", ["SRC-CDS402"]),
                    milestone("MS-REALTIME-RDM-2026Q2", 2026, "Q2", "quarter", "pilot", "hpci-adoption", "observed", "SPring-8とGakuNin RDMの試行運用", "SPring-8 and GakuNin RDM trial operation", "試行運用の開始であり、他施設への展開時期や共通SLAは未公表です。", "The start of trial operation; rollout to other facilities and a common SLA are not public.", ["SRC-CDS397"]),
                    undated("MS-REALTIME-BROAD-SERVICE", "undated", "hpci-adoption", "広域リアルタイムサービスの時期は未確定", "Broad real-time service is undated", "複数施設で共通の期限、帯域、再送、認証、責任分担は確認できていません。", "Common deadlines, bandwidth, retry, identity, and ownership across facilities are not established.", [p]),
                ]),
                lane("LANE-REALTIME-QUANTUM", "REALTIME-QUANTUM", "RIKEN, ORNL, and QuEra", "量子・HPC連携の運用と目標", "Quantum-HPC operation and targets", [
                    milestone("MS-REALTIME-ROQUO-2026Q2", 2026, "Q2", "quarter", "deployment", "hpci-adoption", "observed", "ROQUO運用開始", "ROQUO operation started", "GB200 NVL4 135ノード、540 GPUを含む量子HPC連携基盤の運用開始です。量子優位性の実証とは区別します。", "Operation began for a quantum-HPC platform with 135 GB200 NVL4 nodes and 540 GPUs; this is distinct from demonstrating quantum advantage.", ["SRC-CDS368"]),
                    milestone("MS-REALTIME-PATHFINDER-2026Q2", 2026, "Q2", "quarter", "deployment", "hpci-adoption", "observed", "ORNL Pathfinder開始", "ORNL Pathfinder launched", "20量子ビットのオンプレミス機を用いた統合研究の開始です。一般利用の性能保証ではありません。", "The start of integration research using an on-premises 20-qubit system; it is not a general-user performance guarantee.", ["SRC-CDS455"]),
                    milestone("MS-REALTIME-QUERA-2028", 2028, None, "year", "target", "product", "vendor-target", "QuEra Libra提供目標", "QuEra Libra launch target", "企業ロードマップに示された年単位の目標です。納入、性能、利用条件の確約ではありません。", "A year-level vendor roadmap target; it is not a commitment on delivery, performance, or access terms.", ["SRC-CDS422"]),
                    milestone("MS-REALTIME-GATE-2027Q2", 2027, "Q2", "quarter", "decision-gate", "hpci-evaluation", "openfs-provisional-plan", "リアルタイム・量子サービス契約の暫定判断点", "Provisional real-time and quantum service-contract gate", "期限、データ率、古典基準、正答、失敗、責任分担を定義したユースケースだけを整備案へ接続する暫定計画です。", "A provisional plan to connect only use cases with defined deadlines, data rates, classical baselines, correctness, failures, and ownership to deployment options.", [p, "SRC-CDS397", "SRC-CDS455"]),
                ]),
            ],
            "dependencies": [dependency("DEP-REALTIME-BLUEPRINT", "informs", "RM-APP-REALTIME", "RM-X-BLUEPRINT", "実験・緊急・量子ユースケースの期限、データ率、正答条件がサービス構成を知らせます。", "Deadlines, data rates, and correctness conditions for experimental, urgent, and quantum use cases inform service architecture.", [p, "SRC-CDS397", "SRC-CDS455"])],
            "coverage_gaps": [
                gap("GAP-REALTIME-001", "P1", "ユースケース別のエンドツーエンドSLA", "End-to-end SLA by use case", "個別要素の速度から継続サービスを設計できません。", "A sustained service cannot be designed from component speed alone.", "取得から判断までの期限、データ率、再送、復旧、責任を固定します。", "Fix acquisition-to-decision deadlines, data rates, retry, recovery, and ownership."),
                gap("GAP-REALTIME-002", "P1", "量子・HPC連携の古典基準と総費用", "Classical baseline and total cost for quantum-HPC integration", "量子機を使う効果と運用負担を比較できません。", "Benefits and operational burden of quantum use cannot be compared.", "同一問題の古典基準、精度、待ち時間、前後処理、失敗、費用を測定します。", "Measure identical-problem classical baselines, accuracy, queueing, preprocessing/postprocessing, failures, and cost."),
            ],
        },
        {
            "filename": "workforce-adoption-sustainability.json",
            "export_id": "ADOPTION-ROADMAP-EXPORT-001",
            "roadmap_id": "RM-APP-ADOPTION",
            "domain": "applications",
            "slug": "applications/workforce-adoption-sustainability",
            "title_ja": "利用支援・ソフトウェア持続性・運営体制",
            "title_en": "User support, software sustainability, and governance",
            "summary_ja": "利用者支援、移行支援、技能、OSS保守責任を、ハードウェア導入と同期させる暫定ロードマップです。資料やデモの公開と、継続的に提供できる支援体制を区別します。",
            "summary_en": "A provisional roadmap synchronizing user support, migration assistance, skills, and OSS stewardship with hardware deployment. Publication of documentation or demonstrations is separated from a support service that can be sustained.",
            "source_keys": ["SRC-PORT052", "SRC-PORT053", "SRC-CDS447", "SRC-CDS336", "SRC-CDS345", "SRC-WORK013", "SRC-CDO066"],
            "groups": [
                {"group_id": "adoption", "name_ja": "利用・移行支援", "name_en": "Adoption and migration support"},
                {"group_id": "sustainability", "name_ja": "ソフトウェア持続性", "name_en": "Software sustainability"},
            ],
            "tracks": [
                track("ADOPTION-SUPPORT", "adoption", "利用者支援と移行準備", "User support and migration readiness", "問合せ、移植、性能評価、利用制度の支援負荷を扱います。", "Cover support load for questions, porting, performance evaluation, and access rules.", "HPCIの統計、利用者アンケート、自己点検、Helpdeskは需要や現行支援を示しますが、次期構成で必要な要員数と移行工数は未確定です。", "HPCI statistics, surveys, self-assessment, and Helpdesk document demand and current support, but staffing and migration effort for future systems remain unresolved.", "利用件数だけでなく、未評価、未最適化、問合せ時間、解決率、移行完了を追跡します。", "Track unevaluated and unoptimized work, support time, resolution rate, and completed migration in addition to usage counts.", ["SRC-CDS336", "SRC-CDS345", "SRC-WORK013", "SRC-CDO066"]),
                track("ADOPTION-SUSTAINABILITY", "sustainability", "OSS保守・再現可能な配布", "OSS stewardship and reproducible distribution", "版、ビルド、依存関係、保守責任、終了条件を扱います。", "Cover versions, builds, dependencies, maintenance ownership, and exit conditions.", "EESSIは方針とローリングロードマップを公開しています。これはHPCIの採用決定や長期保守契約を意味しません。", "EESSI publishes policies and a rolling roadmap; this does not constitute an HPCI adoption decision or long-term support contract.", "重要ソフトウェアごとに責任者、代替者、検証基盤、更新頻度、撤退・移行手順を定義します。", "For each critical package, define owners, backups, validation platforms, update cadence, and exit or migration procedures.", ["SRC-PORT052", "SRC-PORT053"]),
            ],
            "lanes": [
                lane("LANE-ADOPTION-PUBLIC", "ADOPTION-SUPPORT", "HPCI and ALCF", "公開された支援・需要資料", "Published support and demand evidence", [
                    milestone("MS-ADOPTION-HPCI-SELF-2026Q1", 2026, "Q1", "quarter", "published", "policy", "as-of-baseline", "HPCI運営自己点検", "HPCI operations self-assessment", "公開報告の時点であり、すべての課題が解決したことを意味しません。", "The publication point of the assessment; it does not mean every issue has been resolved.", ["SRC-CDS345"]),
                    milestone("MS-ADOPTION-EESSI-2026Q2", 2026, "Q2", "quarter", "published", "policy", "as-of-baseline", "EESSIローリングロードマップ更新", "EESSI rolling-roadmap update", "6〜12か月の目標を示す更新です。HPCIでの提供時期ではありません。", "An update of six-to-twelve-month goals; it is not an HPCI availability date.", ["SRC-PORT053"]),
                    milestone("MS-ADOPTION-HPCI-SURVEY-2026Q3", 2026, "Q3", "quarter", "published", "policy", "as-of-baseline", "HPCI利用者アンケート公開", "HPCI user survey published", "利用者の自己申告を含む調査であり、共通入力による性能実測とは区別します。", "A survey including self-reports, distinct from matched-input performance measurements.", ["SRC-CDS336"]),
                    milestone("MS-ADOPTION-ASKALCF-2026Q3", 2026, "Q3", "quarter", "pilot", "research", "observed", "AskALCF紹介・実証", "AskALCF presentation and demonstration", "人の確認を含む支援ワークフローの紹介です。広範な本番導入や労力削減率は確認できません。", "A presentation of a human-reviewed support workflow; broad production deployment and labor savings are unverified.", ["SRC-CDS447"]),
                ]),
                lane("LANE-ADOPTION-OPENFS", "ADOPTION-SUSTAINABILITY", "OpenFS", "支援・保守準備度", "Support and stewardship readiness", [
                    milestone("MS-ADOPTION-GATE-2027Q2", 2027, "Q2", "quarter", "decision-gate", "hpci-evaluation", "openfs-provisional-plan", "支援・保守責任表の暫定判断点", "Provisional support and stewardship gate", "主要アプリ、ライブラリ、ツールについて責任者、代替者、対応時間、検証版、撤退条件を審査する暫定計画です。", "A provisional plan to review ownership, backups, response time, validated versions, and exit conditions for key applications, libraries, and tools.", [p, "SRC-PORT052", "SRC-CDO066"]),
                    undated("MS-ADOPTION-STAFFING-UNDATED", "undated", "hpci-evaluation", "次期体制の要員・技能充足時期は未確定", "Future staffing and skills readiness is undated", "候補構成別の移植・支援工数と確保済み人員は公開情報から確定できません。", "Public information does not establish porting and support effort or secured staffing by candidate architecture.", [p]),
                ]),
            ],
            "dependencies": [dependency("DEP-ADOPTION-BLUEPRINT", "enables", "RM-APP-ADOPTION", "RM-X-BLUEPRINT", "移行支援、技能、保守責任、終了条件が候補構成を継続利用可能なサービスにします。", "Migration support, skills, stewardship, and exit conditions make candidate architectures sustainable services.", [p, "SRC-PORT052", "SRC-CDO066"])],
            "coverage_gaps": [
                gap("GAP-ADOPTION-001", "P1", "候補構成別の移植・支援工数", "Porting and support effort by candidate architecture", "導入日までに必要な要員と期間を見積もれません。", "Staffing and lead time required before deployment cannot be estimated.", "主要アプリと利用者群ごとに、移植、検証、最適化、問合せ工数を実測します。", "Measure porting, validation, tuning, and support effort for major applications and user cohorts."),
                gap("GAP-ADOPTION-002", "P1", "重要ソフトウェアの保守責任と撤退計画", "Stewardship and exit plans for critical software", "提供終了や人員交代時の継続性を判断できません。", "Continuity cannot be assessed when support ends or personnel change.", "責任者、代替者、資金、検証環境、保守期間、移行先を登録します。", "Register owners, backups, funding, validation environments, support horizons, and migration targets."),
            ],
        },
    ]


def build() -> list[Path]:
    registry = source_registry()
    existing_by_url: dict[str, dict[str, Any]] = {}
    existing_by_id: dict[str, dict[str, Any]] = {}
    filenames = {item["filename"] for item in specifications()}
    for path in OUTPUT_DIR.glob("*.json"):
        if path.name in filenames:
            continue
        for item in load_json(path)["sources"]:
            existing_by_url[item["url"]] = item
            existing_by_id[item["source_id"]] = item

    outputs = []
    for original in specifications():
        spec = dict(original)
        source_keys = spec.pop("source_keys")
        source_map = {OPENFS_SOURCE["source_id"]: OPENFS_SOURCE}
        for key in source_keys:
            source = (
                roadmap_source(registry[key])
                if key in registry
                else existing_by_id[key]
            )
            source_map[key] = existing_by_url.get(source["url"], source)

        def resolve(value: str) -> str:
            return source_map[value]["source_id"] if value in source_map else value

        for collection in (spec["tracks"], spec["dependencies"]):
            for item in collection:
                item["source_ids"] = [resolve(value) for value in item["source_ids"]]
        for lane_item in spec["lanes"]:
            for item in lane_item["milestones"]:
                item["source_ids"] = [resolve(value) for value in item["source_ids"]]
        sources: list[dict[str, Any]] = []
        for source in source_map.values():
            if source["source_id"] not in {item["source_id"] for item in sources}:
                sources.append(source)
        roadmap = common(spec, sources)
        path = OUTPUT_DIR / spec["filename"]
        path.write_text(json.dumps(roadmap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        outputs.append(path)
    return outputs


def main() -> None:
    for path in build():
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
