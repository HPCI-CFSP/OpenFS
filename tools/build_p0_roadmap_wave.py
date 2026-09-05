#!/usr/bin/env python3
"""Build the second wave of provisional P0 roadmaps from registered public sources."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "knowledge/public/roadmaps"
AS_OF = "2026-09-05"
DECISION_ID = "PUBDEC-P0-ROADMAP-PLANNING-20260905-001"
DIRECTIVE_ID = "DIR-900103"
OPENFS_SOURCE = {
    "source_id": "SRC-OPENFS-P0-PLAN",
    "title": "OpenFS roadmap portfolio and evidence rules",
    "publisher": "OpenFS",
    "url": "https://github.com/HPCI-CFSP/OpenFS/blob/main/docs/research-baseline/roadmap-portfolio.md",
    "source_class": "openfs-governance",
}
SOURCE_CLASS_MAP = {
    "official-project": "project-official",
    "official-vendor": "vendor-official",
    "official-standard": "standards-body",
    "peer-reviewed": "academic-primary",
    "research-artifact": "academic-primary",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def source_registry() -> dict[str, dict[str, Any]]:
    topic_surface = load_json(ROOT / "knowledge/public/topic-decision-support.json")
    registry = {item["source_id"]: item for item in topic_surface["sources"]}
    return registry


def roadmap_source(source: dict[str, Any]) -> dict[str, Any]:
    value = {
        "source_id": source["source_id"],
        "title": source["title"],
        "publisher": source["publisher"],
        "url": source["url"],
        "source_class": SOURCE_CLASS_MAP[source["source_class"]],
    }
    if source.get("published_at"):
        value["published_at"] = source["published_at"]
    return value


def milestone(mid, year, quarter, precision, maturity, event_type, basis, ja, en,
              detail_ja, detail_en, source_ids, dependencies=None):
    return {
        "milestone_id": mid,
        "year": year,
        "quarter": quarter,
        "timing_precision": precision,
        "maturity": maturity,
        "event_type": event_type,
        "timing_basis": basis,
        "comparison_priority": "key",
        "label_ja": ja,
        "label_en": en,
        "detail_ja": detail_ja,
        "detail_en": detail_en,
        "source_ids": source_ids,
        "dependency_refs": dependencies or [],
    }


def undated(mid, maturity, event_type, ja, en, detail_ja, detail_en, source_ids, dependencies=None):
    return milestone(
        mid, None, None, "undated", maturity, event_type, "no-public-date",
        ja, en, detail_ja, detail_en, source_ids, dependencies,
    )


def track(tid, group, ja, en, summary_ja, summary_en, state_ja, state_en,
          implication_ja, implication_en, source_ids):
    return {
        "track_id": tid,
        "group": group,
        "name_ja": ja,
        "name_en": en,
        "summary_ja": summary_ja,
        "summary_en": summary_en,
        "current_state_ja": state_ja,
        "current_state_en": state_en,
        "hpci_implications_ja": implication_ja,
        "hpci_implications_en": implication_en,
        "source_ids": source_ids,
    }


def lane(lid, tid, owner, ja, en, milestones):
    return {
        "lane_id": lid,
        "track_id": tid,
        "owner": owner,
        "scope_ja": ja,
        "scope_en": en,
        "milestones": milestones,
    }


def gap(gid, priority, scope_ja, scope_en, impact_ja, impact_en, action_ja, action_en):
    return {
        "gap_id": gid,
        "priority": priority,
        "scope_ja": scope_ja,
        "scope_en": scope_en,
        "impact_ja": impact_ja,
        "impact_en": impact_en,
        "next_action_ja": action_ja,
        "next_action_en": action_en,
        "status": "open",
    }


def dependency(did, relationship, upstream, downstream, ja, en, source_ids):
    return {
        "dependency_id": did,
        "relationship": relationship,
        "upstream_roadmap_id": upstream,
        "downstream_roadmap_id": downstream,
        "statement_ja": ja,
        "statement_en": en,
        "basis": "openfs-assessment",
        "source_ids": source_ids,
    }


def common(spec, sources):
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
        "horizon": {"start_year": 2026, "end_year": 2032,
                    "extension_policy": "extend-to-latest-dated-evidence"},
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
        "caveat_ja": "単一のAIモデル・単一エージェントによる暫定調査です。独立したAIモデルによるConsensus Gateは未完了です。公表資料の確認時点、公開目標、OpenFSの暫定計画を区別し、未公表の時期・費用・性能は推測していません。",
        "caveat_en": "Provisional research by one model and one agent; Consensus review by independent models is incomplete. Documentation checks, published targets, and provisional OpenFS plans are separated, and unpublished timing, cost, and performance are not inferred.",
        "publication": {
            "information_classification": "public",
            "publication_approved": True,
            "publication_decision_id": DECISION_ID,
            "human_approval_directive_id": DIRECTIVE_ID,
        },
    }


def specifications():
    p = "SRC-OPENFS-P0-PLAN"
    return [
        {
            "filename": "facility-power-cooling.json", "export_id": "FACILITY-ROADMAP-EXPORT-001",
            "roadmap_id": "RM-HW-FACILITY", "domain": "hardware", "slug": "hardware/facility-power-cooling",
            "title_ja": "施設・電力・冷却", "title_en": "Facility, power, and cooling",
            "summary_ja": "受電、液冷、熱設計、施設工期をシステム導入判断へ接続する暫定ロードマップです。富岳NEXTの公開施設要件は個別計画の根拠であり、他センターへ一律には適用しません。",
            "summary_en": "A provisional roadmap connecting power delivery, liquid cooling, thermal design, and facility schedules to deployment decisions. Public FugakuNEXT requirements support that project and are not assumed to apply uniformly to other centers.",
            "source_keys": ["SRC-BLUE009", "SRC-CDO001", "SRC-CDO003", "SRC-CDO009"],
            "groups": [{"group_id": "facility", "name_ja": "施設要件", "name_en": "Facility requirements"}, {"group_id": "acceptance", "name_ja": "受入・運用", "name_en": "Acceptance and operations"}],
            "tracks": [
                track("FACILITY-DESIGN", "facility", "建屋・受電・冷却設計", "Building, power, and cooling design", "計算機側の熱・電力条件と施設工程を同期します。", "Synchronize compute thermal and power requirements with facility delivery.", "富岳NEXTでは水冷、CDU、温水条件、負荷変動追従が要求されています。", "FugakuNEXT requirements specify water cooling, CDUs, warm-water conditions, and load following.", "センターごとの受電容量、冷却温度、増設余地を別々に確認します。", "Verify power capacity, cooling temperatures, and expansion headroom per center.", ["SRC-BLUE009", "SRC-CDO001"]),
                track("FACILITY-METRICS", "acceptance", "効率・水・レジリエンス", "Efficiency, water, and resilience", "PUEだけでなく水使用、復旧、計測境界を扱います。", "Cover water use, recovery, and measurement boundaries in addition to PUE.", "DOEの公開ガイドは評価項目を示しますが、各HPCIセンターの実測値ではありません。", "DOE public guidance defines evaluation considerations but is not measured data for each HPCI center.", "共通の計測期間と境界で受入・運用データを比較します。", "Compare acceptance and operating data using common periods and boundaries.", ["SRC-CDO003", "SRC-CDO009"]),
            ],
            "lanes": [
                lane("LANE-FACILITY-RIKEN", "FACILITY-DESIGN", "RIKEN R-CCS", "富岳NEXT新建屋", "FugakuNEXT building", [
                    milestone("MS-FACILITY-REQ-BASELINE", 2026, "Q3", "quarter", "published", "policy", "as-of-baseline", "施設要求の公開版を確認", "Public facility requirements checked", "2026年7月31日修正版と募集ページを基準資料としました。確認時点は施設完成を意味しません。", "The July 31, 2026 revision and solicitation page form the baseline; the check date is not facility completion.", ["SRC-BLUE009", "SRC-CDO001"]),
                    milestone("MS-FACILITY-COOLING-2028", 2028, None, "year", "target", "hpci-evaluation", "project-target", "冷却水条件の調整予定", "Cooling-water conditions scheduled for coordination", "流量・圧力等は2028年頃に計算機側の要求に合わせて決定予定です。四半期は公表されていません。", "Flow, pressure, and related conditions are scheduled for determination around 2028 against compute requirements; no quarter is published.", ["SRC-CDO001"], ["DEP-FACILITY-BLUEPRINT"]),
                    milestone("MS-FACILITY-OPERATION-2030", 2030, None, "year", "target", "hpci-adoption", "project-target", "2030年頃の運転開始目標", "Target operation around 2030", "募集ページに示されたプロジェクト目標であり、確定した稼働四半期ではありません。", "This is the project target on the solicitation page, not a confirmed operating quarter.", ["SRC-BLUE009"], ["DEP-FACILITY-BLUEPRINT"]),
                ]),
                lane("LANE-FACILITY-OPENFS", "FACILITY-METRICS", "OpenFS", "センター共通の施設証拠", "Common center facility evidence", [
                    milestone("MS-FACILITY-CENTER-EVIDENCE", 2027, "Q2", "quarter", "decision-gate", "hpci-evaluation", "openfs-provisional-plan", "センター別計測表の暫定判断点", "Provisional gate for center measurement sheets", "受電、冷却、増設余地、計測境界が揃ったセンターだけを比較対象とするOpenFS上の暫定計画です。", "A provisional OpenFS plan to compare only centers with documented power, cooling, expansion headroom, and measurement boundaries.", [p, "SRC-CDO003", "SRC-CDO009"], ["DEP-FACILITY-BLUEPRINT"]),
                    undated("MS-FACILITY-ALL-CENTERS", "undated", "hpci-evaluation", "全センターの同条件実測は未完了", "Matched measurements across all centers are incomplete", "公開資料だけでは同じ期間・境界の電力、冷却、水使用、可用性を揃えられていません。", "Public sources do not yet provide power, cooling, water, and availability under matched periods and boundaries.", [p]),
                ]),
            ],
            "dependencies": [dependency("DEP-FACILITY-BLUEPRINT", "constrains", "RM-HW-FACILITY", "RM-X-BLUEPRINT", "施設工程と電力・冷却上限が導入可能な構成と時期を制約します。", "Facility schedules and power/cooling limits constrain feasible architecture and timing.", [p, "SRC-CDO001"])],
            "coverage_gaps": [
                gap("GAP-FACILITY-001", "P1", "センター別の同条件電力・冷却データ", "Matched center power and cooling data", "施設適合性を横断比較できません。", "Facility fit cannot be compared across centers.", "各センターの公開値、測定境界、期間、増設余地を収集します。", "Collect public values, boundaries, periods, and expansion headroom per center."),
                gap("GAP-FACILITY-002", "P2", "建設費・運転費と復旧試験", "Construction, operating cost, and recovery testing", "5年費用とサービス継続性を定量化できません。", "Five-year cost and continuity cannot be quantified.", "公開契約、エネルギー・水費、保守範囲、復旧実績を照合します。", "Match public contracts, energy/water cost, support scope, and recovery evidence."),
            ],
        },
        {
            "filename": "runtime-scheduling-os.json", "export_id": "RUNTIME-ROADMAP-EXPORT-001",
            "roadmap_id": "RM-SSW-RUNTIME", "domain": "system-software", "slug": "system-software/runtime-scheduling-os",
            "title_ja": "通信・ランタイム・スケジューリング・OS", "title_en": "Communication, runtimes, scheduling, and operating systems",
            "summary_ja": "通信標準、GPU通信、実行時系、ジョブ管理を連合資源へ接続する暫定ロードマップです。仕様公開と各システムでの相互運用確認を区別します。",
            "summary_en": "A provisional roadmap connecting communication standards, GPU collectives, runtimes, and workload management to federated resources. It separates specification publication from system-level interoperability.",
            "source_keys": ["SRC-PORT014", "SRC-PORT026", "SRC-CDS015", "SRC-CDS016", "SRC-CDO055"],
            "groups": [{"group_id": "communication", "name_ja": "通信・ランタイム", "name_en": "Communication and runtimes"}, {"group_id": "scheduling", "name_ja": "OS・ジョブ管理", "name_en": "Operating systems and workload management"}],
            "tracks": [
                track("RUNTIME-COMM", "communication", "MPI・UCX・集合通信", "MPI, UCX, and collectives", "仕様、実装、GPU・NIC対応を分離して追跡します。", "Track specifications, implementations, and GPU/NIC support separately.", "MPI 5.0資料、MPICH 5.0、UCX/UCCの公開資料を基準にします。", "MPI 5.0 documents, MPICH 5.0, and UCX/UCC public materials form the baseline.", "候補ノードとファブリックの組合せごとに適合試験が必要です。", "Each candidate node/fabric combination needs conformance testing.", ["SRC-PORT014", "SRC-PORT026", "SRC-CDS015", "SRC-CDS016"]),
                track("RUNTIME-SCHED", "scheduling", "スケジューラ・電力連携", "Scheduling and power integration", "ジョブ配置、会計、電力制約の連携を扱います。", "Cover workload placement, accounting, and power constraints.", "Slurmはエネルギー会計設定を公開していますが、HPCI横断の共通実装を意味しません。", "Slurm documents energy accounting, but this does not establish a common HPCI-wide implementation.", "資源記述、会計、優先度、緊急実行の意味をそろえる必要があります。", "Resource descriptions, accounting, priority, and urgent execution semantics need alignment.", ["SRC-CDO055"]),
            ],
            "lanes": [
                lane("LANE-RUNTIME-COMM", "RUNTIME-COMM", "Standards and projects", "通信仕様・実装", "Communication specifications and implementations", [
                    milestone("MS-RUNTIME-2026-BASELINE", 2026, "Q3", "quarter", "published", "standard", "as-of-baseline", "MPI・UCX・UCCの公開状態を確認", "MPI, UCX, and UCC status checked", "仕様ページと実装資料の確認であり、特定システムの性能保証ではありません。", "This checks specifications and implementation documentation; it does not guarantee performance on a specific system.", ["SRC-PORT014", "SRC-PORT026", "SRC-CDS015", "SRC-CDS016"]),
                    undated("MS-RUNTIME-INTEROP", "undated", "hpci-evaluation", "候補構成の相互運用時期は未確定", "Candidate-stack interoperability timing is unknown", "CPU、GPU、NIC、MPI、集合通信を固定した試験日程は未公表です。", "No public schedule fixes CPU, GPU, NIC, MPI, and collective versions for testing.", [p], ["DEP-RUNTIME-BLUEPRINT"]),
                ]),
                lane("LANE-RUNTIME-OPENFS", "RUNTIME-SCHED", "OpenFS", "連合実行の受入条件", "Federated execution acceptance", [
                    milestone("MS-RUNTIME-MATRIX-2027", 2027, "Q1", "quarter", "decision-gate", "hpci-evaluation", "openfs-provisional-plan", "互換性マトリクスの暫定判断点", "Provisional compatibility-matrix gate", "API、版、失敗処理、会計、電力制御を候補構成別に記録する暫定計画です。", "A provisional plan to record APIs, versions, failure handling, accounting, and power controls per candidate stack.", [p, "SRC-CDO055"], ["DEP-RUNTIME-BLUEPRINT"]),
                    undated("MS-RUNTIME-FEDERATED-GA", "undated", "hpci-adoption", "連合実行の提供時期は未確定", "Federated execution availability is undated", "共通SLAと運用責任を含む提供時期は公表資料から確定できません。", "Public sources do not establish availability with common SLAs and operational ownership.", [p]),
                ]),
            ],
            "dependencies": [dependency("DEP-RUNTIME-BLUEPRINT", "enables", "RM-SSW-RUNTIME", "RM-X-BLUEPRINT", "通信と実行時系の相互運用が候補構成の実運用を可能にします。", "Communication and runtime interoperability enables candidate architectures to operate in practice.", [p, "SRC-PORT014"])],
            "coverage_gaps": [
                gap("GAP-RUNTIME-001", "P1", "候補ハードウェア別の通信互換性", "Communication compatibility by candidate hardware", "仕様対応だけでは性能・障害処理を判断できません。", "Specification support alone cannot establish performance or failure behavior.", "固定版のCPU・GPU・NIC・MPI・集合通信で回帰試験します。", "Run regression tests with pinned CPU, GPU, NIC, MPI, and collective versions."),
                gap("GAP-RUNTIME-002", "P2", "連合ジョブ管理のSLA・会計意味", "Federated scheduling SLA and accounting semantics", "センター間で待ち時間や費用を比較できません。", "Queue time and cost cannot be compared across centers.", "資源記述、優先度、課金、緊急実行、失敗時責任を定義します。", "Define resource descriptions, priority, charging, urgent use, and failure ownership."),
            ],
        },
        {
            "filename": "data-workflow-platform.json", "export_id": "WORKFLOW-ROADMAP-EXPORT-001",
            "roadmap_id": "RM-SSW-WORKFLOW", "domain": "system-software", "slug": "system-software/data-workflow-platform",
            "title_ja": "データ・AI・実験ワークフロー基盤", "title_en": "Data, AI, and experimental workflow platform",
            "summary_ja": "HPC、AI、データ転送、実験施設をまたぐ実行と再開可能性を扱う暫定ロードマップです。個別ツールの機能とHPCI横断サービスを区別します。",
            "summary_en": "A provisional roadmap for execution and restartability across HPC, AI, data transfer, and experimental facilities. It separates individual tool capabilities from HPCI-wide services.",
            "source_keys": ["SRC-CDS066", "SRC-CDS067", "SRC-CDS071", "SRC-CDS075", "SRC-CDO075", "SRC-STP010"],
            "groups": [{"group_id": "execution", "name_ja": "ワークフロー実行", "name_en": "Workflow execution"}, {"group_id": "data", "name_ja": "データ連携", "name_en": "Data integration"}],
            "tracks": [
                track("WORKFLOW-EXEC", "execution", "再開可能なワークフロー", "Restartable workflows", "依存関係、再実行、監視、実行先を追跡します。", "Track dependencies, restart, monitoring, and execution backends.", "Parsl、Nextflow、WHEEL等に個別機能がありますが、共通運用は未確認です。", "Parsl, Nextflow, WHEEL, and others provide individual capabilities; common operations remain unverified.", "代表ワークフローを複数センターで同じ来歴付きで再実行する必要があります。", "Representative workflows need reproducible execution with provenance across centers.", ["SRC-CDS066", "SRC-CDS067", "SRC-CDS075"]),
                track("WORKFLOW-DATA", "data", "転送・ストリーミング・来歴", "Transfer, streaming, and provenance", "大容量転送と実験データの連続処理を扱います。", "Cover bulk transfer and continuous experimental-data processing.", "ADIOS2、Globus、EuroHPC workflow資料を確認しました。", "ADIOS2, Globus, and EuroHPC workflow documentation were checked.", "認証、データ所在、再送、メタデータ、保存期間を一体で試験します。", "Test identity, location, retransmission, metadata, and retention together.", ["SRC-CDS071", "SRC-CDO075", "SRC-STP010"]),
            ],
            "lanes": [
                lane("LANE-WORKFLOW-PROJECTS", "WORKFLOW-EXEC", "Workflow projects", "公開ツールの機能基準", "Public-tool capability baseline", [
                    milestone("MS-WORKFLOW-2026-BASELINE", 2026, "Q3", "quarter", "published", "product", "as-of-baseline", "再開・実行先・監視機能を確認", "Restart, executor, and monitoring features checked", "各プロジェクトの公開資料を確認した時点であり、HPCI共通サービスの提供日ではありません。", "This is a documentation baseline, not an HPCI-wide service availability date.", ["SRC-CDS066", "SRC-CDS067", "SRC-CDS075"]),
                    undated("MS-WORKFLOW-CROSS-SITE", "undated", "hpci-adoption", "複数拠点サービスの時期は未確定", "Multi-site service timing is undated", "共通認証、データ転送、再開、SLAを含む提供時期は確認できません。", "No public date establishes a service combining common identity, transfer, restart, and SLA.", [p], ["DEP-WORKFLOW-BLUEPRINT"]),
                ]),
                lane("LANE-WORKFLOW-OPENFS", "WORKFLOW-DATA", "OpenFS", "代表ワークフロー実証", "Reference workflow demonstration", [
                    milestone("MS-WORKFLOW-PILOT-2027", 2027, "Q2", "quarter", "pilot", "hpci-evaluation", "openfs-provisional-plan", "代表ワークフロー実証の暫定判断点", "Provisional reference-workflow pilot gate", "シミュレーション、AI、実験データの少なくとも各1件で再実行性を確認する暫定計画です。", "A provisional plan to test reproducibility for at least one simulation, AI, and experimental-data workflow.", [p, "SRC-CDO075", "SRC-STP010"], ["DEP-WORKFLOW-BLUEPRINT"]),
                    undated("MS-WORKFLOW-SLA", "undated", "hpci-evaluation", "公開SLAと責任分担は未確定", "Public SLA and ownership are undated", "拠点をまたぐ失敗時の責任、再送、復旧時間が未定です。", "Ownership, retransmission, and recovery time for cross-site failures remain undefined.", [p]),
                ]),
            ],
            "dependencies": [dependency("DEP-WORKFLOW-BLUEPRINT", "enables", "RM-SSW-WORKFLOW", "RM-X-BLUEPRINT", "再開可能なデータ・実行経路が複合ワークロードの構成案を実現可能にします。", "Restartable data and execution paths make mixed-workload architecture options deployable.", [p, "SRC-CDO075"])],
            "coverage_gaps": [
                gap("GAP-WORKFLOW-001", "P1", "複数拠点での再現可能な実証", "Reproducible multi-site demonstration", "機能一覧だけでは実運用時の成功率と復旧時間が分かりません。", "Feature lists do not establish operational success or recovery time.", "代表ワークフロー、版、入力、来歴、障害注入結果を公開します。", "Publish representative workflows, versions, inputs, provenance, and fault-injection results."),
                gap("GAP-WORKFLOW-002", "P2", "実験データの継続転送と保存方針", "Continuous experimental transfer and retention", "帯域、再送、所在、保存費を構成へ反映できません。", "Bandwidth, retry, location, and retention cost cannot be translated into architecture.", "実験施設別にデータ量、到着率、保持期間、公開範囲を測定します。", "Measure volume, arrival rate, retention, and disclosure boundaries per facility."),
            ],
        },
        {
            "filename": "identity-security-federation.json", "export_id": "SECURITY-ROADMAP-EXPORT-001",
            "roadmap_id": "RM-SSW-SECURITY", "domain": "system-software", "slug": "system-software/identity-security-federation",
            "title_ja": "認証・セキュリティ・連合運用", "title_en": "Identity, security, and federated operations",
            "summary_ja": "統合認証、保証レベル、HPCセキュリティ、機密計算を段階的に検証する暫定ロードマップです。標準準拠と運用受入を分けます。",
            "summary_en": "A provisional roadmap for staged validation of federated identity, assurance, HPC security, and confidential computing. Standards conformance is separated from operational acceptance.",
            "source_keys": ["SRC-CDO027", "SRC-CDO031", "SRC-CDO032", "SRC-CDO039", "SRC-CDO040", "SRC-CDO053"],
            "groups": [{"group_id": "identity", "name_ja": "認証・認可", "name_en": "Identity and authorization"}, {"group_id": "security", "name_ja": "計算・運用セキュリティ", "name_en": "Compute and operational security"}],
            "tracks": [
                track("SECURITY-IDENTITY", "identity", "連合認証と保証", "Federated identity and assurance", "ログイン、MFA、属性、保証レベルを追跡します。", "Track login, MFA, attributes, and assurance levels.", "HPCI手順、REFEDS MFA、OpenID Federationの公開資料を確認しました。", "HPCI procedures, REFEDS MFA, and OpenID Federation documentation were checked.", "利用者、サービス、ワークロードIDの境界を定義する必要があります。", "User, service, and workload identity boundaries need definition.", ["SRC-CDO027", "SRC-CDO031", "SRC-CDO032"]),
                track("SECURITY-HPC", "security", "HPCゼロトラスト・機密計算", "HPC zero trust and confidential computing", "管理面、計算面、データ面の統制を扱います。", "Cover control-plane, compute-plane, and data-plane controls.", "NISTのHPC向け文書とZero Trust資料は統制設計の基準であり、製品認定ではありません。", "NIST HPC and Zero Trust documents are control-design references, not product certifications.", "性能影響、鍵管理、障害対応、監査証跡を候補構成で試験します。", "Test performance impact, key management, incident handling, and audit trails on candidate stacks.", ["SRC-CDO039", "SRC-CDO040", "SRC-CDO053"]),
            ],
            "lanes": [
                lane("LANE-SECURITY-IDENTITY", "SECURITY-IDENTITY", "HPCI and standards bodies", "現行認証と標準", "Current identity and standards", [
                    milestone("MS-SECURITY-2026-BASELINE", 2026, "Q3", "quarter", "published", "standard", "as-of-baseline", "認証・保証標準の公開状態を確認", "Identity and assurance standards checked", "公開資料の確認であり、全サービスの移行完了を意味しません。", "This is a documentation check and does not mean all services have migrated.", ["SRC-CDO027", "SRC-CDO031", "SRC-CDO032"]),
                    undated("MS-SECURITY-FEDERATION", "undated", "hpci-adoption", "共通保証プロファイルの提供時期は未確定", "Common assurance-profile availability is undated", "センター横断の属性、MFA、復旧、監査要件は確定していません。", "Cross-center attribute, MFA, recovery, and audit requirements are not fixed.", [p], ["DEP-SECURITY-BLUEPRINT"]),
                ]),
                lane("LANE-SECURITY-OPENFS", "SECURITY-HPC", "OpenFS", "候補構成のセキュリティ受入", "Security acceptance for candidate stacks", [
                    milestone("MS-SECURITY-PROFILE-2027", 2027, "Q2", "quarter", "decision-gate", "hpci-evaluation", "openfs-provisional-plan", "信頼境界・受入項目の暫定判断点", "Provisional trust-boundary and acceptance gate", "統制、責任、性能影響、復旧を候補構成ごとに記録する暫定計画です。", "A provisional plan to record controls, ownership, performance impact, and recovery per candidate stack.", [p, "SRC-CDO039", "SRC-CDO040"], ["DEP-SECURITY-BLUEPRINT"]),
                    undated("MS-SECURITY-CONFIDENTIAL", "undated", "hpci-evaluation", "機密計算の相互運用は未確認", "Confidential-computing interoperability is unverified", "CPU、GPU、ネットワーク、ストレージをまたぐ証明・鍵管理・復旧は未検証です。", "Attestation, key management, and recovery across CPU, GPU, network, and storage remain unverified.", [p]),
                ]),
            ],
            "dependencies": [dependency("DEP-SECURITY-BLUEPRINT", "constrains", "RM-SSW-SECURITY", "RM-X-BLUEPRINT", "信頼境界と受入基準が利用可能な構成・データ区分を制約します。", "Trust boundaries and acceptance criteria constrain deployable architectures and data classes.", [p, "SRC-CDO039"])],
            "coverage_gaps": [
                gap("GAP-SECURITY-001", "P1", "センター共通の保証・監査プロファイル", "Common center assurance and audit profile", "利用者体験と統制強度を横断比較できません。", "User experience and control strength cannot be compared across centers.", "属性、MFA、復旧、ログ、インシデント連携を共通試験します。", "Test attributes, MFA, recovery, logging, and incident coordination consistently."),
                gap("GAP-SECURITY-002", "P2", "機密計算の性能・運用実証", "Confidential-computing performance and operations", "保護機能の採用による性能・障害対応コストを評価できません。", "Performance and operational costs of protection cannot be assessed.", "候補ハードウェアで証明、鍵更新、障害復旧、性能を測定します。", "Measure attestation, key rotation, recovery, and performance on candidate hardware."),
            ],
        },
        {
            "filename": "ai-for-science-agents.json", "export_id": "AI-SCIENCE-ROADMAP-EXPORT-001",
            "roadmap_id": "RM-APP-AI", "domain": "applications", "slug": "applications/ai-for-science-agents",
            "title_ja": "AI for Science・科学AIエージェント", "title_en": "AI for Science and scientific AI agents",
            "summary_ja": "大規模学習・推論、科学AIエージェント、評価基盤をシステム要件へ接続する暫定ロードマップです。製品機能、ベンチマーク、公的な科学成果を分けて扱います。",
            "summary_en": "A provisional roadmap connecting large-scale training and inference, scientific AI agents, and evaluation infrastructure to system requirements. Product features, benchmarks, and scientific outcomes are treated separately.",
            "source_keys": ["SRC-CDS048", "SRC-CDS050", "SRC-CDS053", "SRC-AIP001", "SRC-AIP002", "SRC-CDA053", "SRC-HC26-JALAPENO-RESULTS"],
            "groups": [{"group_id": "training-serving", "name_ja": "学習・推論", "name_en": "Training and inference"}, {"group_id": "agents", "name_ja": "科学AIエージェント", "name_en": "Scientific AI agents"}],
            "tracks": [
                track("AI-TRAIN-SERVE", "training-serving", "分散学習・推論サービング", "Distributed training and inference serving", "並列化、メモリ、チェックポイント、待ち時間を扱います。", "Cover parallelism, memory, checkpoints, and latency.", "Megatron、DeepSpeed、vLLM、MLPerfの公開資料を基準にします。", "Public Megatron, DeepSpeed, vLLM, and MLPerf materials form the baseline.", "学習と推論を同じピーク演算値だけで評価せず、通信、KV cache、データ経路を測定します。", "Do not evaluate training and inference by peak arithmetic alone; measure communication, KV cache, and data paths.", ["SRC-CDS048", "SRC-CDS050", "SRC-CDS053", "SRC-AIP001", "SRC-AIP002"]),
                track("AI-SCIENTIFIC-AGENTS", "agents", "科学タスクとエージェント評価", "Scientific tasks and agent evaluation", "正答、再現性、費用、時間、ツール利用を扱います。", "Cover correctness, reproducibility, cost, time, and tool use.", "ScienceAgentBenchとJalapenoの公開成果は異なる評価範囲を持ちます。", "ScienceAgentBench and Jalapeno public results cover different evaluation scopes.", "HPCIで実行可能な科学タスク群と監査可能な実行記録が必要です。", "HPCI needs executable scientific task suites and auditable run records.", ["SRC-CDA053", "SRC-HC26-JALAPENO-RESULTS"]),
            ],
            "lanes": [
                lane("LANE-AI-STACK", "AI-TRAIN-SERVE", "AI software projects", "学習・推論スタック", "Training and serving stack", [
                    milestone("MS-AI-STACK-2026", 2026, "Q3", "quarter", "published", "product", "as-of-baseline", "分散学習・推論機能を確認", "Training and serving capabilities checked", "公開機能の確認であり、候補HPCI構成上の性能測定ではありません。", "This checks public capabilities and is not a performance measurement on candidate HPCI systems.", ["SRC-CDS048", "SRC-CDS050", "SRC-CDS053"]),
                    undated("MS-AI-STACK-ACCEPTANCE", "undated", "hpci-evaluation", "共通受入試験の時期は未確定", "Common acceptance testing is undated", "固定モデル、入力、同時実行数、精度、電力での比較日程はありません。", "No schedule exists for comparison with pinned models, inputs, concurrency, accuracy, and power.", [p], ["DEP-AI-BLUEPRINT"]),
                ]),
                lane("LANE-AI-AGENTS", "AI-SCIENTIFIC-AGENTS", "OpenFS", "科学AIエージェント評価", "Scientific-agent evaluation", [
                    milestone("MS-AI-AGENT-SUITE-2027", 2027, "Q2", "quarter", "pilot", "hpci-evaluation", "openfs-provisional-plan", "科学タスク群の暫定実証点", "Provisional scientific task-suite pilot", "正答、再実行性、時間、費用、ツール権限を測る公開タスク群を試す暫定計画です。", "A provisional plan to pilot public tasks measuring correctness, reproducibility, time, cost, and tool permissions.", [p, "SRC-CDA053", "SRC-HC26-JALAPENO-RESULTS"], ["DEP-AI-BLUEPRINT"]),
                    undated("MS-AI-CONSENSUS", "undated", "research", "独立したAIモデルによる評価の完了時期は未確定", "Evaluation by independent models is undated", "現在の調査は単一のAIモデルによるものであり、Consensus Gateの完了時期を推測しません。", "Current research uses one model; the Consensus Gate completion date is not inferred.", [p]),
                ]),
            ],
            "dependencies": [dependency("DEP-AI-BLUEPRINT", "informs", "RM-APP-AI", "RM-X-BLUEPRINT", "AI負荷の実測と正答条件が計算・メモリ・ネットワーク・ストレージ構成を知らせます。", "Measured AI workloads and correctness requirements inform compute, memory, network, and storage architecture.", [p, "SRC-AIP001", "SRC-AIP002"])],
            "coverage_gaps": [
                gap("GAP-AI-001", "P1", "HPCI候補構成での共通AI負荷測定", "Common AI workload measurements on candidate HPCI systems", "学習・推論の必要資源を比較できません。", "Training and inference resource needs cannot be compared.", "モデル、入力、精度、同時実行、電力、データ移動を固定して測定します。", "Measure with pinned models, inputs, accuracy, concurrency, power, and data movement."),
                gap("GAP-AI-002", "P2", "科学AIエージェントの再現性と監査", "Scientific-agent reproducibility and audit", "出力の正しさと科学的利用可能性を判断できません。", "Output correctness and scientific usability cannot be established.", "公開タスク、期待結果、ツール権限、実行ログ、再試行方針を定義します。", "Define public tasks, expected results, tool permissions, run records, and retry policy."),
            ],
        },
        {
            "filename": "procurement-investment-scenarios.json", "export_id": "PROCUREMENT-ROADMAP-EXPORT-001",
            "roadmap_id": "RM-X-PROCUREMENT", "domain": "cross-cutting", "slug": "cross-cutting/procurement-investment-scenarios",
            "title_ja": "調達・共同投資・システム整備計画案", "title_en": "Procurement, joint investment, and deployment scenarios",
            "summary_ja": "公示、仕様、契約総額、保守、段階導入をシステム整備計画案へ変換する暫定ロードマップです。落札総額から非公開の部品単価を逆算しません。",
            "summary_en": "A provisional roadmap translating notices, specifications, total awards, support, and staged deployment into system plans. It does not reverse-engineer undisclosed component prices from total awards.",
            "source_keys": ["SRC-PRP001", "SRC-PRP003", "SRC-PRP005", "SRC-PCD001", "SRC-CDO085"],
            "groups": [{"group_id": "evidence", "name_ja": "公開調達証拠", "name_en": "Public procurement evidence"}, {"group_id": "planning", "name_ja": "投資・段階整備", "name_en": "Investment and staged deployment"}],
            "tracks": [
                track("PROCUREMENT-EVIDENCE", "evidence", "公示・仕様・契約範囲", "Notices, specifications, and contract scope", "金額、対象、期間、保守、仕様の対応を追跡します。", "Track amount, scope, term, support, and specification correspondence.", "国内公示と欧州の契約資料には総額例がありますが、同じ費目内訳ではありません。", "Japanese notices and European contract records provide total examples but not matched cost breakdowns.", "購入と賃貸、保守、電力・施設、税、移行を分けて比較します。", "Separate purchase and lease, support, power/facility, tax, and migration.", ["SRC-PRP001", "SRC-PRP003", "SRC-PRP005", "SRC-PCD001", "SRC-CDO085"]),
                track("PROCUREMENT-SCENARIOS", "planning", "価格帯別・段階導入案", "Budget-band and staged-deployment options", "複数予算帯で機能と規模の下限・上限を示します。", "Show capability and scale bounds across multiple budget bands.", "現在の公開データでは5年TCOと部品内訳が揃わず、価格帯案は正式評価できません。", "Current public data lacks complete five-year TCO and itemization, so budget-band options cannot be formally scored.", "同じ費用境界と期間で少なくとも5価格帯を比較します。", "Compare at least five budget bands using matched cost boundaries and periods.", [p, "SRC-PRP001", "SRC-PRP003"]),
            ],
            "lanes": [
                lane("LANE-PROCUREMENT-PUBLIC", "PROCUREMENT-EVIDENCE", "Public procuring entities", "公開契約の証拠", "Public award evidence", [
                    milestone("MS-PROCUREMENT-2026-BASELINE", 2026, "Q3", "quarter", "published", "policy", "as-of-baseline", "公示・契約総額の対応を確認", "Notice and total-award correspondence checked", "複数案件の公開総額・対象を確認しましたが、部品別価格や同一の5年費用境界はありません。", "Public totals and scopes were checked for multiple cases, but component prices and matched five-year boundaries are unavailable.", ["SRC-PRP001", "SRC-PRP003", "SRC-PRP005", "SRC-PCD001", "SRC-CDO085"]),
                    undated("MS-PROCUREMENT-ITEMIZED-TCO", "undated", "hpci-evaluation", "部品別5年TCOの比較時期は未確定", "Itemized five-year TCO comparison is undated", "購入、賃貸、保守、電力、冷却、施設、移行、撤去を揃えた公開案件は未確認です。", "No public case yet aligns purchase/lease, support, power, cooling, facility, migration, and decommissioning.", [p], ["DEP-PROCUREMENT-BLUEPRINT"]),
                ]),
                lane("LANE-PROCUREMENT-OPENFS", "PROCUREMENT-SCENARIOS", "OpenFS", "比較可能な計画案", "Comparable deployment options", [
                    milestone("MS-PROCUREMENT-TEMPLATE-2027", 2027, "Q1", "quarter", "decision-gate", "hpci-evaluation", "openfs-provisional-plan", "5年費用テンプレートの暫定判断点", "Provisional five-year cost-template gate", "価格帯を算出する前に費用境界、税、期間、割引、保守範囲を固定する暫定計画です。", "A provisional plan to fix cost boundary, tax, term, discounts, and support scope before computing budget bands.", [p, "SRC-PRP001", "SRC-PRP003"], ["DEP-PROCUREMENT-BLUEPRINT"]),
                    undated("MS-PROCUREMENT-FIVE-BANDS", "undated", "hpci-evaluation", "5価格帯の正式提示は未確定", "Formal five-band options are undated", "5年TCOと性能・施設制約が揃うまで数値案を推測しません。", "Numeric options will not be inferred until five-year TCO, performance, and facility constraints align.", [p]),
                ]),
            ],
            "dependencies": [dependency("DEP-PROCUREMENT-BLUEPRINT", "constrains", "RM-X-PROCUREMENT", "RM-X-BLUEPRINT", "予算境界、契約期間、保守、施設費が実現可能なシステム規模を制約します。", "Budget boundaries, contract terms, support, and facility costs constrain feasible system scale.", [p, "SRC-PRP001", "SRC-PRP003"])],
            "coverage_gaps": [
                gap("GAP-PROCUREMENT-001", "P1", "同一境界の5年TCO", "Five-year TCO with matched boundaries", "価格帯別のシステム規模を比較できません。", "System scale cannot be compared across budget bands.", "購入・賃貸、保守、電力、冷却、施設、移行、撤去、税を案件別に記録します。", "Record purchase/lease, support, power, cooling, facility, migration, decommissioning, and tax per case."),
                gap("GAP-PROCUREMENT-002", "P2", "仕様書と落札額の部品対応", "Specification-to-award component mapping", "総額から各コンポーネント価格を信頼できる形で分離できません。", "Component prices cannot be reliably separated from total awards.", "公開仕様書、数量、契約範囲、保守年数を対応付け、非公開値は未知のまま残します。", "Map public specifications, quantities, scope, and support term; leave undisclosed values unknown."),
            ],
        },
        {
            "filename": "operations-governance-continuity.json", "export_id": "OPERATIONS-ROADMAP-EXPORT-001",
            "roadmap_id": "RM-X-OPERATIONS", "domain": "cross-cutting", "slug": "cross-cutting/operations-governance-continuity",
            "title_ja": "統合運用・ガバナンス・サービス継続", "title_en": "Integrated operations, governance, and service continuity",
            "summary_ja": "連合アクセス、配分、支援、データ移行、責任分担を継続サービスとして設計する暫定ロードマップです。ポータル公開と共通SLAの成立を区別します。",
            "summary_en": "A provisional roadmap for federated access, allocations, support, data migration, and accountability as continuous services. Portal release is separated from establishment of common SLAs.",
            "source_keys": ["SRC-CDO065", "SRC-CDO066", "SRC-CDO067", "SRC-CDO069", "SRC-CDO070", "SRC-CDG005"],
            "groups": [{"group_id": "federation", "name_ja": "連合アクセス・配分", "name_en": "Federated access and allocation"}, {"group_id": "continuity", "name_ja": "継続性・責任", "name_en": "Continuity and accountability"}],
            "tracks": [
                track("OPERATIONS-FEDERATION", "federation", "資源発見・申請・配分", "Discovery, requests, and allocation", "利用者が複数資源へ到達する共通経路を扱います。", "Cover common user paths to multiple resources.", "HPCIの現行制度とEuroHPC Federation Platformの公開機能を確認しました。", "Current HPCI arrangements and public EuroHPC Federation Platform capabilities were checked.", "UIだけでなく属性、資源記述、配分単位、会計を比較します。", "Compare attributes, resource descriptions, allocation units, and accounting in addition to UI.", ["SRC-CDO065", "SRC-CDO067", "SRC-CDO069", "SRC-CDO070"]),
                track("OPERATIONS-CONTINUITY", "continuity", "支援・移行・SLA", "Support, migration, and SLA", "世代交代や障害時のサービス継続を扱います。", "Cover service continuity during system transitions and incidents.", "HPCI Helpdeskと共通化方針の公開資料はありますが、全サービスの共通SLAは未確認です。", "Public HPCI Helpdesk and commonization-policy materials exist, but a common SLA across services is unverified.", "責任分担、通知、データ移行、復旧時間を明文化します。", "Document ownership, notifications, data migration, and recovery time.", ["SRC-CDO066", "SRC-CDG005"]),
            ],
            "lanes": [
                lane("LANE-OPERATIONS-FEDERATION", "OPERATIONS-FEDERATION", "HPCI and EuroHPC", "公開された連合サービス", "Published federation services", [
                    milestone("MS-OPERATIONS-2026-BASELINE", 2026, "Q3", "quarter", "published", "policy", "as-of-baseline", "連合アクセス・配分機能を確認", "Federated access and allocation checked", "制度・ポータル資料の確認であり、相互の機能同等性を意味しません。", "This checks policy and portal documentation and does not imply functional equivalence.", ["SRC-CDO065", "SRC-CDO067", "SRC-CDO069", "SRC-CDO070"]),
                    undated("MS-OPERATIONS-COMMON-SERVICE", "undated", "hpci-adoption", "共通サービス水準の時期は未確定", "Common service-level timing is undated", "資源記述、申請、会計、支援、障害通知の共通化完了時期は確認できません。", "No public date establishes common resource description, request, accounting, support, and incident notification.", [p], ["DEP-OPERATIONS-BLUEPRINT"]),
                ]),
                lane("LANE-OPERATIONS-OPENFS", "OPERATIONS-CONTINUITY", "OpenFS", "継続性の受入条件", "Continuity acceptance", [
                    milestone("MS-OPERATIONS-CONTINUITY-2027", 2027, "Q2", "quarter", "decision-gate", "hpci-evaluation", "openfs-provisional-plan", "サービス継続表の暫定判断点", "Provisional service-continuity matrix gate", "計画停止、障害、世代移行について責任、通知、復旧、データ移行を記録する暫定計画です。", "A provisional plan to record ownership, notification, recovery, and data migration for maintenance, incidents, and generation changes.", [p, "SRC-CDO066", "SRC-CDG005"], ["DEP-OPERATIONS-BLUEPRINT"]),
                    undated("MS-OPERATIONS-SLA", "undated", "hpci-evaluation", "比較可能なSLAは未整備", "Comparable SLAs are unavailable", "公開情報ではセンターごとの可用性・復旧・支援時間を同じ定義で比較できません。", "Public information does not provide center availability, recovery, and support times under common definitions.", [p]),
                ]),
            ],
            "dependencies": [dependency("DEP-OPERATIONS-BLUEPRINT", "enables", "RM-X-OPERATIONS", "RM-X-BLUEPRINT", "連合アクセスと継続運用の責任分担がシステム整備計画案を実サービスにします。", "Federated access and continuity ownership turn deployment options into operable services.", [p, "SRC-CDO065", "SRC-CDG005"])],
            "coverage_gaps": [
                gap("GAP-OPERATIONS-001", "P1", "センター横断の可用性・復旧・支援指標", "Cross-center availability, recovery, and support metrics", "継続性を同じ定義で評価できません。", "Continuity cannot be assessed using common definitions.", "計画停止、障害停止、復旧時間、問合せ応答を同じ期間・境界で収集します。", "Collect maintenance, incidents, recovery time, and support response under matched periods and boundaries."),
                gap("GAP-OPERATIONS-002", "P2", "世代移行時のデータ・アカウント・ソフトウェア継続", "Data, account, and software continuity across generations", "移行費用と利用停止期間を見積もれません。", "Migration cost and interruption cannot be estimated.", "センター別の移行計画、互換期間、責任、成功判定を記録します。", "Record migration plans, compatibility windows, ownership, and success criteria per center."),
            ],
        },
        {
            "filename": "horizon-scanning-topic-discovery.json", "export_id": "HORIZON-ROADMAP-EXPORT-001",
            "roadmap_id": "RM-X-HORIZON", "domain": "cross-cutting", "slug": "cross-cutting/horizon-scanning-topic-discovery",
            "title_ja": "技術動向監視・新規調査項目発見", "title_en": "Technology horizon scanning and new research-topic discovery",
            "summary_ja": "世界の技術・供給・政策の変化を継続監視し、新規調査項目候補を証拠付きで提案するOpenFS運用の暫定ロードマップです。単一のAIモデルによる提案は自動採用しません。",
            "summary_en": "A provisional OpenFS operating roadmap for continuous monitoring of global technology, supply, and policy changes and evidence-backed proposals for new research topics. Single-model proposals are not adopted automatically.",
            "source_keys": ["SRC-CDX001", "SRC-CDX007", "SRC-CDX008", "SRC-CDX022", "SRC-CDX023", "SRC-CDX026"],
            "groups": [{"group_id": "signals", "name_ja": "兆候監視", "name_en": "Signal monitoring"}, {"group_id": "governance", "name_ja": "提案・検証", "name_en": "Proposal and validation"}],
            "tracks": [
                track("HORIZON-SIGNALS", "signals", "技術・供給・政策シグナル", "Technology, supply, and policy signals", "標準、製品、研究、供給網、政策を別々に追跡します。", "Track standards, products, research, supply chains, and policy separately.", "OECD、NIST、NEDO、企業・OSSプロジェクトの公開資料が登録されています。", "Public OECD, NIST, NEDO, company, and OSS-project sources are registered.", "報道だけで正式結果を変更せず、一次情報と影響範囲を確認します。", "Do not change formal findings from news alone; verify primary evidence and scope.", ["SRC-CDX001", "SRC-CDX007", "SRC-CDX008", "SRC-CDX022", "SRC-CDX023", "SRC-CDX026"]),
                track("HORIZON-TOPICS", "governance", "新規項目の提案とConsensus Gate", "New-topic proposals and Consensus Gate", "重複、関連性、証拠、反証可能性を確認します。", "Check duplication, relevance, evidence, and falsifiability.", "ハーネスには提案経路がありますが、独立したAIモデルによるConsensusは未完了です。", "The harness has a proposal path, but Consensus review by independent models remains incomplete.", "候補は正式カタログへ直接書かず、提案・評価・採否記録を残します。", "Keep candidates out of the canonical catalog until proposal, assessment, and decision records exist.", [p]),
            ],
            "lanes": [
                lane("LANE-HORIZON-SOURCES", "HORIZON-SIGNALS", "OpenFS monitors", "公開情報の監視", "Public-information monitoring", [
                    milestone("MS-HORIZON-2026-BASELINE", 2026, "Q3", "quarter", "published", "research", "as-of-baseline", "監視対象と情報源を確認", "Monitoring scope and sources checked", "世界の技術・供給・政策を対象とする基準を確認しました。網羅性や即時反映を保証しません。", "The baseline covers global technology, supply, and policy; it does not guarantee completeness or immediate updates.", ["SRC-CDX001", "SRC-CDX007", "SRC-CDX008", "SRC-CDX022", "SRC-CDX023", "SRC-CDX026"]),
                    milestone("MS-HORIZON-WEEKLY-2026", 2026, "Q4", "quarter", "pilot", "hpci-evaluation", "openfs-provisional-plan", "定期監視の暫定運用点", "Provisional recurring-monitoring gate", "更新候補を提案キューへ入れ、一次情報確認と重複検査を行う暫定計画です。", "A provisional plan to queue update candidates for primary-source and duplication checks.", [p], ["DEP-HORIZON-BLUEPRINT"]),
                ]),
                lane("LANE-HORIZON-GATE", "HORIZON-TOPICS", "OpenFS governance", "新規Topicの統制", "New-topic governance", [
                    milestone("MS-HORIZON-PACKAGE-2027", 2027, "Q1", "quarter", "decision-gate", "hpci-evaluation", "openfs-provisional-plan", "候補Topic審査パッケージの暫定判断点", "Provisional candidate-topic review-package gate", "根拠、関連項目、反対意見、追加調査、権限をまとめる暫定計画です。", "A provisional plan to package evidence, related topics, dissent, follow-up research, and permissions.", [p, "SRC-CDX007"], ["DEP-HORIZON-BLUEPRINT"]),
                    undated("MS-HORIZON-INDEPENDENT-CONSENSUS", "undated", "research", "独立したAIモデルによるConsensusの時期は未確定", "Consensus review by independent models is undated", "利用可能な独立したAIモデルと実行主体が確保されていないため、完了時期を示しません。", "No completion date is stated because independent models and execution parties are not yet secured.", [p]),
                ]),
            ],
            "dependencies": [dependency("DEP-HORIZON-BLUEPRINT", "informs", "RM-X-HORIZON", "RM-X-BLUEPRINT", "新しい技術・供給・政策シグナルが計画案の前提と再検討時期を知らせます。", "New technology, supply, and policy signals inform assumptions and reconsideration dates for deployment options.", [p, "SRC-CDX001", "SRC-CDX007"])],
            "coverage_gaps": [
                gap("GAP-HORIZON-001", "P1", "監視網羅性と更新遅延の測定", "Monitoring coverage and update-latency measurement", "最新情報の未検知や反映遅れを定量化できません。", "Missed updates and publication lag cannot be quantified.", "情報源別の最終確認、変更検知、候補化、公開までの時間を記録します。", "Record source check, change detection, proposal, and publication timestamps."),
                gap("GAP-HORIZON-002", "P2", "独立したAIモデルによる新規Topic評価", "Evaluation of new topics by independent models", "単一のAIモデルによる偏りを除去できません。", "Bias from a single model cannot be removed.", "異なる提供者・モデル・プロンプトの評価者を確保し、不一致を保存します。", "Secure reviewers using different providers, models, and prompts, and preserve disagreement."),
            ],
        },
    ]


def build():
    registry = source_registry()
    existing_by_url = {}
    for path in OUTPUT_DIR.glob("*.json"):
        if path.name in {item["filename"] for item in specifications()}:
            continue
        for item in load_json(path)["sources"]:
            existing_by_url[item["url"]] = item

    outputs = []
    for spec in specifications():
        source_map = {OPENFS_SOURCE["source_id"]: OPENFS_SOURCE}
        for key in spec.pop("source_keys"):
            source = roadmap_source(registry[key])
            source = existing_by_url.get(source["url"], source)
            source_map[key] = source

        def resolve(value):
            return source_map[value]["source_id"] if value in source_map else value

        for collection in (spec["tracks"], spec["dependencies"]):
            for item in collection:
                item["source_ids"] = [resolve(value) for value in item["source_ids"]]
        for lane_item in spec["lanes"]:
            for item in lane_item["milestones"]:
                item["source_ids"] = [resolve(value) for value in item["source_ids"]]
        sources = []
        for source in source_map.values():
            if source["source_id"] not in {item["source_id"] for item in sources}:
                sources.append(source)
        roadmap = common(spec, sources)
        path = OUTPUT_DIR / spec["filename"]
        path.write_text(json.dumps(roadmap, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        outputs.append(path)
    return outputs


def main():
    for path in build():
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
