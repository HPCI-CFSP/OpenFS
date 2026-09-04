(function () {
  "use strict";

  const data = window.OPENFS_PUBLIC_DATA;
  if (!data) {
    document.body.textContent = "OpenFS public data is unavailable.";
    return;
  }

  const copy = {
    ja: {
      languageControl: "表示言語", siteNavigation: "サイト内ナビゲーション", breadcrumbs: "パンくずリスト", tagline: "公開調査カタログとシステム整備計画案", publicOnly: "公開情報のみ", siteUpdated: "サイト更新日時", licenseLabel: "ライセンス",
      navOverview: "概要", navCatalog: "調査カタログ", navSearch: "検索", navRoadmaps: "ロードマップ", navScenarios: "システム整備計画案", navReports: "報告書", footerDescription: "HPCI-CFSP 公開調査ビュー",
      evidenceKicker: "根拠の検証状況", evidenceTitle: "根拠情報の監査", evidenceLead: "URLの到達性、マイルストーンの主張種別、時期の精度、未確認事項を分けて表示します。",
      consensusCaveatTitle: "検証状況", evidenceCaveat: "すべての項目について、参照ID、主張種別、時期表現を構造的に検査し、主要な更新項目を単一のAIモデルで一次情報と照合しました。ただし、全項目を独立したAIモデルが意味内容まで検証したものではなく、合意判定（Consensus Gate）は完了していません。到達性監査も主張の正しさを判定するものではありません。",
      claimAuditTitle: "主張と根拠の対応監査", sourceAuditTitle: "情報源の到達性", sourceAuditNote: "到達性は主張の正しさを示しません。ブラウザで閲覧できる資料でも、機械的な取得ではアクセス制限やタイムアウトが発生する場合があります。重複を除いたURL数は独立した情報源の数とは限らず、本文確認も単一のAIモデルによる暫定結果です。", sourceClassTitle: "情報源区分の内訳", sourceClassNote: "区分別の件数は、ロードマップへの登録件数です。重複を除いたURL数は上部に分けて表示します。一次情報または公式情報であっても、個々の主張が独立に検証済みとは限りません。", sourceClass: "情報源区分", sourceClassMeaning: "この区分が示す範囲", retrievalAttentionTitle: "到達性の確認が必要な情報源", "vendor-official": "ベンダー公式", "standards-body": "標準化団体", "government-official": "政府・公的機関", "research-organization": "研究機関", "project-official": "公式プロジェクト", "academic-primary": "原著学術論文", "openfs-governance": "OpenFSの運用記録", "vendor-officialMeaning": "自社製品、出荷、企業ロードマップについて発表した主体", "standards-bodyMeaning": "仕様、標準化段階、公開版について発表した主体", "government-officialMeaning": "政策、調達、施設、事業計画について発表した公的機関", "research-organizationMeaning": "研究開発計画、実証、システム運用について発表した機関", "project-officialMeaning": "OSS、ベンチマーク、共同開発計画の公式発表主体", "academic-primaryMeaning": "著者が方法と結果を報告した原著論文", "openfs-governanceMeaning": "外部技術の根拠ではなく、OpenFS自身の暫定判断または手続き", retrievalTriage: "本文確認の要否", exactUrlConfirmed: "登録URLの本文を確認済み", unresolvedRetrieval: "未解決",
      freshnessAuditTitle: "情報源の更新状況と再調査キュー", freshnessAuditLead: "公開日や更新日が古いという理由だけで誤りとはみなしません。時期が未確定の項目、公表された目標時期を過ぎた項目、到達性に注意が必要な情報源、日付情報が不足する項目を次回の調査対象にします。", freshnessAttentionTitle: "更新確認が必要な項目", freshnessAttention: "高優先度の更新確認", critical: "重大", object: "対象", reason: "理由",
      gapRegisterTitle: "優先度付きの未確認事項", gapRegisterLead: "公開情報で確認できない条件を推測で補わず、判断への影響と次の調査行動を記録します。",
      centerProfileTitle: "HPCIセンタープロファイルの監査", centerProfileLead: "検索の実行状況、項目ごとの根拠、合意判定による受理を分け、GAP-BLUE-001/003を推測で解消しないための監査です。", profileFieldCoverage: "12項目の根拠確認状況", centerProfileStatus: "センター別の暫定状況", acceptedProfiles: "合意判定で受理済み", evidenceCompleteProfiles: "全項目に根拠あり", effectiveQueries: "有効な追跡クエリ", verifiedFields: "確認済み項目", partialFields: "一部確認", unknownFields: "未確認", notCollectedFields: "旧形式では未収集", profileField: "プロファイル項目", centerName: "センター", profileDecision: "合意判定", fieldSummary: "項目別の状況", officialPage: "公式サイト", verified: "確認済み", partial: "一部確認", unknown: "未確認", "not-collected": "未収集", unaccepted: "未受理", acceptedCurrent: "受理済み・現行", profile_users: "利用者", profile_priority_domains: "重点分野", profile_current_system: "現行システム", profile_refresh_window: "更新時期", profile_power: "電力", profile_facility: "施設", profile_budget: "予算", profile_procurement: "調達", profile_software: "ソフトウェア", profile_operations: "運用", profile_migration: "移行", profile_data_connectivity: "データ接続性",
      gapQueueTitle: "優先度P0の調査割当キュー", gapQueueLead: "優先度P0の未確認事項を調査モニターまたは独立レビューへ割り当て、検索計画と解消条件を分けて示します。すべての解消条件と、必要な独立情報源数および合意判定要件を満たすまで、未解決として扱います。", assignment: "割当先", cadence: "再確認間隔", executionState: "実行状況", queryPlan: "検索計画", closurePlan: "解消条件", closureCriteria: "条件", independentOrigins: "独立した情報源", consensusRequired: "合意判定が必要", criteriaUnverified: "条件未検証", weekly: "毎週", monthly: "毎月", quarterly: "四半期ごと", "continuous-until-quorum": "定足数を満たすまで継続", "staged-monitor-disabled": "モニター無効・準備待ち", "ready-for-scheduled-discovery": "定期調査を実行可能", "awaiting-independent-review": "独立レビュー待ち", "explicit-override": "明示した検索クエリ", "generated-fallback": "自動生成した代替クエリ", "not-applicable": "対象外", assignedDiscovery: "情報探索への割当", assignedConsensus: "独立レビューへの割当", productionReady: "定期実行可能", p0ExplicitQueries: "P0の明示クエリ", p0FallbackQueries: "P0の代替クエリ",
      normalizedDependenciesTitle: "整理した相互依存関係", externalConstraintsTitle: "外部制約と未確認事項", portfolioGateTitle: "計画全体の判断ゲート", portfolioGateNote: "ここに示す項目は、個別ロードマップ間の因果関係ではありません。公開ロードマップを統合して正式判断する前に、計画全体で解消すべき未確認事項です。", sourceCount: "情報源", sourceRegistrations: "情報源の登録数", uniqueSourceUrls: "重複を除いたURL数", duplicateRegistrations: "重複登録数", externalUrls: "外部URL数", httpFetches: "HTTP取得", uniqueUrlsUnit: "重複を除いたURL", accessRestrictionBasis: "HTTP応答または取得ポリシーによる制限", externalFirstParty: "外部の一次・公式情報", standardsUnit: "標準化団体", vendorsUnit: "ベンダー", openfsGovernance: "OpenFSの運用記録", internalGovernanceEvent: "内部の運用記録", internalGovernanceNote: "外部技術の根拠には含めない", reachable: "到達可能", accessRestricted: "アクセス制限", timeoutError: "タイムアウト／エラー", milestoneCount: "マイルストーン", primaryEvent: "出来事・標準", forwardTarget: "将来目標", baseline: "情報確認日時点", coverageGap: "時期未公表", provisionalGate: "OpenFS暫定判断ゲート", sourceQuarterPrecision: "外部根拠のある四半期", provisionalQuarterPrecision: "暫定的な四半期", lowerPrecision: "半期・年単位",
      roadmap: "ロードマップ", total: "合計", status: "状況", source: "情報源", url: "公開URL", relationship: "関係", criticality: "重要度", decisionImpact: "判断への影響", delayRisk: "遅延リスク", gates: "判断ゲート", high: "高", medium: "中", low: "低", commit: "コミット", priority: "優先度", scope: "確認対象", impact: "判断への影響", nextAction: "次の調査行動", open: "未解決", gapId: "未確認事項ID", pastTargetRechecks: "期限経過後の再確認", profileContract: "プロファイル必須項目", coverageGapsUnit: "未確認事項", roadmapsUnit: "ロードマップ", relationshipRequires: "必要とする", relationshipInforms: "判断材料となる", relationshipConstrains: "制約する", relationshipEnables: "可能にする", relationshipCoEvolves: "相互に発展する", basisEvidenceBacked: "公開根拠に基づく", basisOpenfsAssessment: "OpenFSによる暫定評価",
      scenarioKicker: "システム整備計画案", scenarioIndexTitle: "3つのシステム整備計画案", scenarioIndexLead: "同じ11項目の評価軸、判断ゲート、時間軸で比較し、未確認条件を推測で埋めずに残します。",
      notRanking: "推奨順位を示すものではありません", scenarioNotice: "3つの案はいずれも、単一のAIモデルが作成した暫定案です。センタープロファイル、価格、供給、施設条件の確認と、独立したAIモデルによる合意判定は完了していません。",
      scenarioComparisonTitle: "共通形式で比較", commonDecisionGates: "共通判断ゲート", objective: "目的", architecture: "アーキテクチャ", systemSoftware: "システムソフトウェア", applications: "アプリケーション", unknownCount: "未確認条件", reversibility: "可逆性", openDetail: "詳細を見る", budgetArchitectureTitle: "予算規模別のシステムアーキテクチャ案", budgetArchitectureLead: "五つの予算水準で設計方針ごとの仮配分を比較します。数量・費用・実現可能性の未確認部分を区別して示します。", budgetArchitectureControl: "予算規模", budgetRange: "概算事業規模", analyticalEstimate: "OpenFSによる概算", lowConfidence: "確度：低", cpuNodes: "CPUノード", acceleratorNodes: "アクセラレータノード", accelerators: "アクセラレータ", storageCapacity: "共有ストレージ", facilityClass: "施設規模", component: "構成要素", quantity: "概算規模", role: "役割", budgetReferenceCases: "公開調達実績と仕様書", referenceBudget: "公表規模", notPublished: "非公表", comparabilityNote: "比較上の注意", estimateMethod: "推定方法",
      planningHorizon: "計画期間", researchStatus: "調査状況", consensusStatus: "合意判定状況", updatedColumn: "更新日時", provisional: "暫定", incomplete: "未完了", implementationTimelineTitle: "計画案の時間的な展開", implementationTimelineLead: "各案が調査・実証から導入・展開へ進む想定を四半期単位で示します。すべてOpenFSの暫定計画であり、外部製品の確定日程ではありません。", implementationTimelineDetailLead: "分野別の調査、実証、判断、導入、展開を四半期単位で示します。各帯の期間はOpenFSの暫定計画です。", contextNotesTitle: "適用範囲に関する注記", hpciSpecific: "HPCI固有", reusable: "一般化可能", planVersion: "計画案の版", effectiveFrom: "適用開始日", reviewDue: "次回見直し期限", supersedes: "置換前の版", noSupersededVersion: "初版", timelineDomain: "分野", timelineQuarter: "四半期", stageResearch: "調査", stageEvaluation: "評価", stagePilot: "実証", stageDecision: "判断", stageDeployment: "導入", stageExpansion: "展開", stageOperation: "運用", stageRetirement: "更新・終了", portfolio: "計画全体", "storage-data": "ストレージ・データ", "facility-operations": "施設・運用", "procurement-governance": "調達・ガバナンス",
      centerImpacts: "センターへの影響", technologyOptions: "技術候補と代替策", decisionEvidenceContracts: "判断に必要な検証条件", decisionEvidenceContractsNote: "各検証条件を満たしても、合意判定の候補になるだけで、自動的には採用されません。", coveredGaps: "対象となるP0未確認事項", schemas: "スキーマ", validators: "検証プログラム", acceptanceEffect: "判定上の効力", candidateOnly: "合意判定の候補段階", evaluationAxes: "11項目の評価軸", unscoredNote: "評価軸の重みが人によって承認されていないため、総合点は算出しません。", decisionBlockingGaps: "正式判断を保留させるP0未確認事項", decisionBlockingGapsNote: "候補の比較は継続できますが、正式な推奨または採用には、未確認事項の解消か、その取扱いと根拠を記録した判断が必要です。", uncertainties: "未確認条件", decisionGates: "判断ゲート", provenance: "来歴", traceability: "来歴と参照ID", sourceCommit: "生成元コミット",
      fit: "適合性", migration: "移行", unverified: "未確認", candidate: "候補", role: "役割", maturityGate: "成熟度ゲート", fallback: "代替策", criterion: "評価軸", assessment: "暫定評価", evidence: "参照ID", optionDomain: "分野", compute: "計算ノード", memory: "メモリ", interconnect: "インターコネクト", "system-software": "システムソフトウェア", applicationsDomain: "アプリケーション",
      "application-coverage": "アプリケーション・利用者適合性", "time-to-solution": "性能・応答・スループット", "power-facility-fit": "電力・冷却・建屋適合性", "lifecycle-cost": "ライフサイクル費用", "maturity-schedule": "技術成熟度・供給・導入時期", "software-migration": "ソフトウェア継続性・移行", "operations-security": "運用性・人材・セキュリティ", "hpci-interoperability": "HPCI相互運用性", "technology-origin-and-ecosystem": "技術・供給網・産業波及", "center-fit": "センター別適合", reversibilityCriterion: "可逆性・段階導入性",
      consensusReview: "合意判定レビュー", consensusIndexTitle: "合意判定レビュー", consensusIndexLead: "対象を固定したコミット、独立性要件、決定論的な判定ゲート、要件を満たすレビュー担当者の属性と来歴を表示します。", consensusNotAcceptance: "レビュー完了は自動採用を意味しません", consensusIndexNotice: "HPCIに大きな影響を与える判断には、独立レビューの基準を満たした後も、人による正式な指示が必要です。", openConsensus: "レビューの来歴を見る", consensusRequirements: "独立レビューの要件", consensusReviewUnits: "レビュー単位", eligibleReviewers: "要件を満たすレビュアー", unmetRequirements: "未達の要件", knownLimitations: "既知の制約", noEligibleReviewers: "現在、要件を満たす独立レビューはありません。", assessmentCount: "有効なレビュー", supportCount: "支持", modelFamilies: "モデル系統", providers: "AIサービス提供者", harnesses: "ハーネス構成", criticReviews: "反証レビュー", pinnedArtifacts: "固定した成果物", baseCommit: "基準コミット", manifestDigest: "マニフェストのSHA-256", requirement: "要件", threshold: "閾値", reviewChecks: "検査項目", reviewer: "レビュアー", model: "モデル", harness: "ハーネス", verdict: "判定", reviewedAt: "レビュー日時", package: "レビュー一式", manifest: "マニフェスト", artifactId: "成果物ID", "ready-for-human-decision": "人による判断待ち", awaiting: "独立レビュー待ち", gateEffectIncomplete: "独立レビューの要件を満たしていません。ロードマップとシステム整備計画案は暫定のままです。", gateEffectReady: "独立レビューの基準を満たしていますが、採用には人による判断が必要です。"
    },
    en: {
      languageControl: "Display language", siteNavigation: "Site navigation", breadcrumbs: "Breadcrumbs", tagline: "Public research catalog and system planning options", publicOnly: "Public information only", siteUpdated: "Site updated", licenseLabel: "License",
      navOverview: "Overview", navCatalog: "Research catalog", navSearch: "Search", navRoadmaps: "Roadmaps", navScenarios: "System planning options", navReports: "Reports", footerDescription: "HPCI-CFSP public research view",
      evidenceKicker: "EVIDENCE ASSURANCE", evidenceTitle: "Evidence assurance", evidenceLead: "This audit separates URL reachability, milestone claim types, timing precision, and coverage gaps.",
      consensusCaveatTitle: "Validation status", evidenceCaveat: "All items were structurally checked for source references, claim type, and timing semantics. One model also checked major updates against primary sources. These checks do not constitute independent semantic verification of every item: Consensus review by independent models is incomplete, and source reachability does not establish that a claim is correct.",
      claimAuditTitle: "Claim-evidence audit", sourceAuditTitle: "Source reachability", sourceAuditNote: "Reachability does not validate claims. A source that is accessible in a browser may still return an access restriction or timeout to the automated client. A unique URL count is not a count of independent origins, and the content checks remain provisional work by one model.", sourceClassTitle: "Source-class breakdown", sourceClassNote: "Class counts are roadmap registrations. The deduplicated URL count is shown separately above. First-party or official provenance does not mean that each claim has been independently verified.", sourceClass: "Source class", sourceClassMeaning: "What this classification represents", retrievalAttentionTitle: "Sources requiring reachability attention", "vendor-official": "Vendor official", "standards-body": "Standards body", "government-official": "Government / public body", "research-organization": "Research organization", "project-official": "Official project", "academic-primary": "Primary academic paper", "openfs-governance": "OpenFS governance", "vendor-officialMeaning": "Publisher responsible for product, shipment, or corporate-roadmap statements", "standards-bodyMeaning": "Publisher responsible for specifications, standards stages, or releases", "government-officialMeaning": "Public authority responsible for policy, procurement, facilities, or programs", "research-organizationMeaning": "Organization responsible for R&D plans, demonstrations, or system operation", "project-officialMeaning": "Official publisher for an OSS, benchmark, or collaborative project", "academic-primaryMeaning": "Original paper whose authors report methods and results", "openfs-governanceMeaning": "OpenFS procedure or provisional judgment, not external technology evidence", retrievalTriage: "Content-review status", exactUrlConfirmed: "exact-URL content reviewed", unresolvedRetrieval: "unresolved",
      freshnessAuditTitle: "Source update status and follow-up queue", freshnessAuditLead: "Queues undated items, target dates that have passed, reachability warnings, and missing date metadata without treating age alone as an error.", freshnessAttentionTitle: "Items requiring follow-up", freshnessAttention: "High-priority source review", critical: "critical", object: "Object", reason: "Reason",
      gapRegisterTitle: "Prioritized Coverage Gaps", gapRegisterLead: "Unknown public conditions remain explicit rather than being filled by inference, with decision impact and the next research action recorded.",
      centerProfileTitle: "HPCI center profile assurance", centerProfileLead: "This audit separates search execution, field-level evidence, and acceptance through the Consensus Gate so that GAP-BLUE-001/003 cannot be closed by inference.", profileFieldCoverage: "Evidence status across twelve fields", centerProfileStatus: "Provisional status by center", acceptedProfiles: "Accepted profiles", evidenceCompleteProfiles: "Profiles with evidence for every field", effectiveQueries: "Effective follow-up queries", verifiedFields: "Verified fields", partialFields: "Partially verified fields", unknownFields: "Unknown fields", notCollectedFields: "Not collected under the earlier specification", profileField: "Profile field", centerName: "Center", profileDecision: "Acceptance", fieldSummary: "Field status", officialPage: "Official site", verified: "verified", partial: "partial", unknown: "unknown", "not-collected": "not collected", unaccepted: "unaccepted", acceptedCurrent: "accepted and current", profile_users: "Users", profile_priority_domains: "Priority domains", profile_current_system: "Current system", profile_refresh_window: "Refresh window", profile_power: "Power", profile_facility: "Facility", profile_budget: "Budget", profile_procurement: "Procurement", profile_software: "Software", profile_operations: "Operations", profile_migration: "Migration", profile_data_connectivity: "Data connectivity",
      gapQueueTitle: "P0 research assignment queue", gapQueueLead: "This queue assigns each P0 coverage gap to a research monitor or an independent Consensus review. Search plans and closure criteria are shown separately. An item remains open until all criteria, the required number of independent sources, and the Consensus requirements are met.", assignment: "Assignment", cadence: "Review cadence", executionState: "Execution status", queryPlan: "Search plan", closurePlan: "Closure criteria", closureCriteria: "criteria", independentOrigins: "independent sources", consensusRequired: "Consensus required", criteriaUnverified: "criteria unverified", weekly: "weekly", monthly: "monthly", quarterly: "quarterly", "continuous-until-quorum": "until quorum is reached", "staged-monitor-disabled": "Monitor disabled; awaiting activation", "ready-for-scheduled-discovery": "ready for scheduled research", "awaiting-independent-review": "awaiting independent review", "explicit-override": "curated search queries", "generated-fallback": "automatically generated fallback query", "not-applicable": "not applicable", assignedDiscovery: "Research assignments", assignedConsensus: "Independent-review assignments", productionReady: "Ready for scheduled runs", p0ExplicitQueries: "P0 curated queries", p0FallbackQueries: "P0 fallback queries",
      normalizedDependenciesTitle: "Consolidated dependencies", externalConstraintsTitle: "External constraints and coverage gaps", portfolioGateTitle: "Portfolio-wide decision gate", portfolioGateNote: "This is not a causal dependency edge. It is an unresolved condition that applies to the whole portfolio before the published roadmaps can support a formal decision.", sourceCount: "Sources", sourceRegistrations: "Source registrations", uniqueSourceUrls: "Unique source URLs", duplicateRegistrations: "duplicate registrations", externalUrls: "external URLs", httpFetches: "HTTP fetches", uniqueUrlsUnit: "unique URLs", accessRestrictionBasis: "restricted by an HTTP response or fetch policy", externalFirstParty: "External primary and official registrations", standardsUnit: "standards bodies", vendorsUnit: "vendors", openfsGovernance: "OpenFS governance", internalGovernanceEvent: "Internal governance record", internalGovernanceNote: "Excluded from external technology evidence", reachable: "Reachable", accessRestricted: "Access restricted", timeoutError: "Timeout / error", milestoneCount: "Milestones", primaryEvent: "Events / standards", forwardTarget: "Forward targets", baseline: "Status as of the research date", coverageGap: "Undated", provisionalGate: "OpenFS provisional gates", sourceQuarterPrecision: "Externally supported quarters", provisionalQuarterPrecision: "Provisional quarters", lowerPrecision: "Half-year / year",
      roadmap: "Roadmap", total: "Total", status: "Status", source: "Source", url: "Public URL", relationship: "Relationship", criticality: "Criticality", decisionImpact: "Decision impact", delayRisk: "Delay risk", gates: "Decision gates", high: "high", medium: "medium", low: "low", commit: "Commit", priority: "Priority", scope: "Scope", impact: "Decision impact", nextAction: "Next research action", open: "open", gapId: "Coverage Gap ID", pastTargetRechecks: "past-target rechecks", profileContract: "required profile fields", coverageGapsUnit: "Coverage Gaps", roadmapsUnit: "roadmaps", relationshipRequires: "requires", relationshipInforms: "informs", relationshipConstrains: "constrains", relationshipEnables: "enables", relationshipCoEvolves: "co-evolves", basisEvidenceBacked: "evidence-backed", basisOpenfsAssessment: "OpenFS provisional assessment",
      scenarioKicker: "SYSTEM PLANNING OPTIONS", scenarioIndexTitle: "Three system planning options", scenarioIndexLead: "Compare all three on the same eleven criteria, decision gates, and time axis without filling unknowns by inference.",
      notRanking: "The options are not ranked", scenarioNotice: "All three options are provisional analyses prepared by one model. Center profiles, prices, supply conditions, facility constraints, and Consensus review by independent models remain incomplete.",
      scenarioComparisonTitle: "Common-format comparison", commonDecisionGates: "Common decision gates", objective: "Objective", architecture: "Architecture", systemSoftware: "System software", applications: "Applications", unknownCount: "Unknown conditions", reversibility: "Reversibility", openDetail: "Open details", budgetArchitectureTitle: "Budget-scaled system architecture options", budgetArchitectureLead: "Compare allocation assumptions across five numeric budget levels. Quantities, costs, and feasibility remain explicitly unverified where evidence is missing.", budgetArchitectureControl: "Budget class", budgetRange: "Estimated program scale", analyticalEstimate: "OpenFS estimate", lowConfidence: "Confidence: low", cpuNodes: "CPU nodes", acceleratorNodes: "Accelerator nodes", accelerators: "Accelerators", storageCapacity: "Shared storage", facilityClass: "Facility class", component: "Component", quantity: "Estimated scale", role: "Role", budgetReferenceCases: "Public procurement costs and specifications", referenceBudget: "Published scale", notPublished: "not published", comparabilityNote: "Comparability note", estimateMethod: "Estimation method",
      planningHorizon: "Planning horizon", researchStatus: "Research status", consensusStatus: "Consensus status", updatedColumn: "Updated", provisional: "provisional", incomplete: "incomplete", implementationTimelineTitle: "Time-phased implementation path", implementationTimelineLead: "Shows how each option could progress from research and pilots to deployment and expansion by quarter. All bands are provisional OpenFS plans, not confirmed external product schedules.", implementationTimelineDetailLead: "Shows research, evaluation, decisions, deployment, and expansion by domain and quarter. Each band is a provisional OpenFS plan.", contextNotesTitle: "Scope notes", hpciSpecific: "HPCI-specific", reusable: "Generally applicable", planVersion: "Plan version", effectiveFrom: "Effective from", reviewDue: "Review due", supersedes: "Supersedes", noSupersededVersion: "Initial version", timelineDomain: "Domain", timelineQuarter: "Quarter", stageResearch: "research", stageEvaluation: "evaluation", stagePilot: "pilot", stageDecision: "decision", stageDeployment: "deployment", stageExpansion: "expansion", stageOperation: "operation", stageRetirement: "renewal / retirement", portfolio: "Overall plan", "storage-data": "Storage and data", "facility-operations": "Facilities and operations", "procurement-governance": "Procurement and governance",
      centerImpacts: "Center impacts", technologyOptions: "Technology options and fallbacks", decisionEvidenceContracts: "Evidence requirements for decisions", decisionEvidenceContractsNote: "Meeting an evidence requirement only makes the result a Consensus candidate; it does not trigger automatic adoption.", coveredGaps: "P0 Gaps addressed", schemas: "Schemas", validators: "Validators", acceptanceEffect: "Effect", candidateOnly: "Consensus candidate only", evaluationAxes: "Eleven evaluation criteria", unscoredNote: "No total score is calculated before human approval of weights.", decisionBlockingGaps: "P0 Gaps blocking a formal decision", decisionBlockingGapsNote: "Candidate comparison can continue, but a formal recommendation or adoption requires either resolution of each Gap or a documented decision on how to handle it.", uncertainties: "Uncertainties", decisionGates: "Decision gates", provenance: "PROVENANCE", traceability: "Traceability and references", sourceCommit: "Source commit",
      fit: "Fit", migration: "Migration", unverified: "Unverified", candidate: "Candidate", role: "Role", maturityGate: "Maturity gate", fallback: "Fallback", criterion: "Criterion", assessment: "Provisional assessment", evidence: "Evidence refs", optionDomain: "Domain", compute: "Compute", memory: "Memory", interconnect: "Interconnect", "system-software": "System software", applicationsDomain: "Applications",
      "application-coverage": "Application and user fit", "time-to-solution": "Performance, response, and throughput", "power-facility-fit": "Power, cooling, and facility fit", "lifecycle-cost": "Lifecycle cost", "maturity-schedule": "Maturity, supply, and schedule", "software-migration": "Software continuity and migration", "operations-security": "Operations, staffing, and security", "hpci-interoperability": "HPCI interoperability", "technology-origin-and-ecosystem": "Technology, supply chain, and ecosystem", "center-fit": "Center-specific fit", reversibilityCriterion: "Reversibility and staged deployment",
      consensusReview: "Consensus review", consensusIndexTitle: "Consensus review", consensusIndexLead: "Shows the pinned commit, independence requirements, deterministic gate, and provenance of eligible reviewers.", consensusNotAcceptance: "Review completion does not imply automatic adoption", consensusIndexNotice: "A high-impact HPCI decision still requires a human Directive after the independent-review thresholds are met.", openConsensus: "Open review provenance", consensusRequirements: "Independent-review requirements", consensusReviewUnits: "Review units", eligibleReviewers: "Eligible reviewers", unmetRequirements: "Unmet requirements", knownLimitations: "Known limitations", noEligibleReviewers: "There are currently no eligible independent reviews.", assessmentCount: "Eligible reviews", supportCount: "Support", modelFamilies: "Model families", providers: "Providers", harnesses: "Harness configurations", criticReviews: "Falsification reviews", pinnedArtifacts: "Pinned artifacts", baseCommit: "Pinned commit", manifestDigest: "Manifest SHA-256", requirement: "Requirement", threshold: "Threshold", reviewChecks: "Checks", reviewer: "Reviewer", model: "Model", harness: "Harness", verdict: "Verdict", reviewedAt: "Reviewed", package: "Review package", manifest: "Manifest", artifactId: "Artifact ID", "ready-for-human-decision": "ready for human decision", awaiting: "awaiting independent review", gateEffectIncomplete: "Independent-review requirements are unmet. Roadmaps and system planning options remain provisional.", gateEffectReady: "Independent-review thresholds are met, but adoption still requires a human decision."
    }
  };

  let language = readLanguage();
  const page = document.body.dataset.page;
  const rootPrefix = document.body.dataset.rootPrefix || "";

  function readLanguage() {
    const requested = new URLSearchParams(window.location.search).get("lang");
    if (requested === "ja" || requested === "en") return requested;
    try { const value = window.localStorage.getItem("openfs-language"); if (value === "ja" || value === "en") return value; } catch (_error) {}
    return "ja";
  }
  function rememberLanguage(value) {
    try { window.localStorage.setItem("openfs-language", value); } catch (_error) {}
    const url = new URL(window.location.href); url.searchParams.set("lang", value);
    window.history.replaceState(null, "", url);
  }
  function tr(key) { return copy[language][key] || key; }
  function localized(item, field) { return item?.[`${field}_${language}`] || item?.[field] || ""; }
  function localizedArray(item, field) { const value = item?.[`${field}_${language}`] || item?.[field] || []; return Array.isArray(value) ? value : []; }
  function setText(id, value) { const element = document.getElementById(id); if (element) element.textContent = value; }
  function formatJst(value) {
    const parts = Object.fromEntries(new Intl.DateTimeFormat("en-CA", {timeZone: "Asia/Tokyo", year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit", hour12: false}).formatToParts(new Date(value)).filter((part) => part.type !== "literal").map((part) => [part.type, part.value]));
    return `${parts.year}-${parts.month}-${parts.day}-${parts.hour}:${parts.minute}:${parts.second} JST`;
  }
  function makeCell(tag, text) { const cell = document.createElement(tag); cell.textContent = text; return cell; }
  function repositoryPathLinks(paths, commit) { const root = document.createElement("span"); paths.forEach((path, index) => { if (index) root.append(" · "); const link = document.createElement("a"); link.href = `https://github.com/HPCI-CFSP/OpenFS/blob/${encodeURIComponent(commit)}/${path.split("/").map(encodeURIComponent).join("/")}`; link.target = "_blank"; link.rel = "noopener noreferrer"; link.textContent = path; root.append(link); }); return root; }
  function scenarioLink(scenario) {
    const params = new URLSearchParams({v: data.site.commit_sha, lang: language});
    const selected = new URLSearchParams(window.location.search);
    for (const key of ["budget", "year"]) if (selected.has(key)) params.set(key, selected.get(key));
    return `${rootPrefix}${scenario.path}?${params}`;
  }
  function refreshScenarioLinks() {
    const targets = new Map(data.scenarios.map((scenario) => [new URL(rootPrefix + scenario.path, window.location.href).pathname, scenario]));
    document.querySelectorAll("a[href]").forEach((link) => {
      const url = new URL(link.href, window.location.href);
      const scenario = targets.get(url.pathname);
      if (scenario && url.origin === window.location.origin) link.href = scenarioLink(scenario);
    });
  }
  function consensusLink(item) { return `${rootPrefix}${item.path}?v=${encodeURIComponent(data.site.commit_sha)}`; }
  function roadmapTitle(roadmapId) { const roadmap = data.roadmaps.find((item) => item.roadmap_id === roadmapId); return roadmap ? (language === "ja" ? roadmap.title_ja : roadmap.title_en) : roadmapId; }
  function profileFieldLabel(field) { return tr(`profile_${field}`); }
  function sourceStatusLabel(status) { return ({reachable: tr("reachable"), "access-restricted": tr("accessRestricted"), timeout: tr("timeoutError"), error: tr("timeoutError")})[status] || status; }
  function relationshipLabel(value) { return ({requires: tr("relationshipRequires"), informs: tr("relationshipInforms"), constrains: tr("relationshipConstrains"), enables: tr("relationshipEnables"), "co-evolves": tr("relationshipCoEvolves")})[value] || value; }
  function dependencyBasisLabel(value) { return ({"evidence-backed": tr("basisEvidenceBacked"), "openfs-assessment": tr("basisOpenfsAssessment")})[value] || value; }

  function applyStaticCopy() {
    document.documentElement.lang = language;
    document.querySelectorAll("[data-i18n]").forEach((element) => { element.textContent = tr(element.dataset.i18n); });
    document.querySelectorAll("[data-i18n-aria-label]").forEach((element) => { element.setAttribute("aria-label", tr(element.dataset.i18nAriaLabel)); });
    document.querySelectorAll("[data-language]").forEach((button) => { const selected = button.dataset.language === language; button.classList.toggle("active", selected); button.setAttribute("aria-pressed", String(selected)); });
    const updated = document.getElementById("site-updated"); if (updated) { updated.href = data.site.commit_url; updated.textContent = `${tr("siteUpdated")} ${formatJst(data.site.updated_at)} · ${data.site.commit_sha.slice(0, 7)}`; }
    setText("license-status", `${tr("licenseLabel")}: ${data.publication.license}`);
    const pageTitleKey = {"roadmap-evidence": "evidenceTitle", "scenario-index": "scenarioIndexTitle", "consensus-index": "consensusIndexTitle"}[page];
    if (pageTitleKey) document.title = `${tr(pageTitleKey)} | OpenFS`;
  }

  function renderMetric(root, label, value, note) {
    const item = document.createElement("div"); const term = document.createElement("span"); term.textContent = label; const count = document.createElement("strong"); count.textContent = value; item.append(term, count); if (note) { const small = document.createElement("small"); small.textContent = note; item.append(small); } root.append(item);
  }

  function makeQueryPlanCell(item) {
    const cell = document.createElement("td");
    cell.className = "gap-query-plan-cell";
    if (!item.query_seeds.length) {
      cell.textContent = tr(item.query_plan_origin);
      return cell;
    }
    const details = document.createElement("details");
    const summary = document.createElement("summary");
    summary.textContent = `${tr(item.query_plan_origin)} (${item.query_seeds.length})`;
    const list = document.createElement("ol");
    item.query_seeds.forEach((seed) => {
      const entry = document.createElement("li");
      const languageLabel = document.createElement("strong");
      languageLabel.textContent = seed.language.toUpperCase();
      const query = document.createElement("code");
      query.textContent = seed.query;
      entry.append(languageLabel, query);
      list.append(entry);
    });
    details.append(summary, list);
    cell.append(details);
    return cell;
  }

  function makeClosurePlanCell(item) {
    const cell = document.createElement("td");
    cell.className = "gap-closure-plan-cell";
    const plan = item.closure_plan;
    const details = document.createElement("details");
    const summary = document.createElement("summary");
    summary.textContent = `${plan.criteria.length} ${tr("closureCriteria")} · ${plan.minimum_independent_origin_groups} ${tr("independentOrigins")}`;
    const meta = document.createElement("p");
    meta.textContent = `${tr("consensusRequired")} · ${tr("criteriaUnverified")}`;
    const list = document.createElement("ol");
    plan.criteria.forEach((criterion) => {
      const entry = document.createElement("li");
      const method = document.createElement("strong");
      method.textContent = criterion.verification_method;
      const requirement = document.createElement("span");
      requirement.textContent = localized(criterion, "requirement");
      entry.append(method, requirement);
      list.append(entry);
    });
    details.append(summary, meta, list);
    cell.append(details);
    return cell;
  }

  function renderEvidencePage() {
    const assurance = data.roadmap_assurance; const source = assurance.source_audit; const sourceTriage = assurance.source_triage; const evidence = assurance.evidence_audit; const freshness = assurance.freshness_audit; const gapQueue = assurance.gap_queue; const centerProfile = assurance.center_profile_assurance; const dependencies = assurance.dependency_register;
    const metrics = document.getElementById("assurance-metrics"); metrics.replaceChildren();
    renderMetric(metrics, tr("sourceRegistrations"), source.summary.source_count, `${source.summary.duplicate_registration_count} ${tr("duplicateRegistrations")}`);
    renderMetric(metrics, tr("uniqueSourceUrls"), source.summary.unique_url_count, `${source.summary.fetch_count} ${tr("httpFetches")} · ${source.summary.unique_external_url_count} ${tr("externalUrls")} · ${source.audit_id}`);
    renderMetric(metrics, tr("externalFirstParty"), source.summary.external_first_party_source_count, `${source.summary.source_class_counts["standards-body"]} ${tr("standardsUnit")} · ${source.summary.source_class_counts["vendor-official"]} ${tr("vendorsUnit")}`);
    renderMetric(metrics, tr("reachable"), source.summary.reachable, `${source.summary.unique_url_status_counts.reachable} ${tr("uniqueUrlsUnit")} · ${Math.round(source.summary.reachable / source.summary.source_count * 100)}%`);
    renderMetric(metrics, tr("accessRestricted"), source.summary["access-restricted"], `${source.summary.unique_url_status_counts["access-restricted"]} ${tr("uniqueUrlsUnit")} · ${tr("accessRestrictionBasis")}`);
    const unaudited = source.results.filter((entry) => entry.error_kind === "not-audited");
    const unauditedUrls = new Set(unaudited.map((entry) => entry.url)).size;
    renderMetric(metrics, tr("timeoutError"), source.summary.timeout + source.summary.error - unaudited.length, `${source.summary.unique_url_status_counts.timeout + source.summary.unique_url_status_counts.error - unauditedUrls} ${tr("uniqueUrlsUnit")}`);
    if (unaudited.length) renderMetric(metrics, language === "ja" ? "HTTP未監査" : "HTTP not audited", unaudited.length, `${unauditedUrls} ${tr("uniqueUrlsUnit")}`);
    renderMetric(metrics, tr("milestoneCount"), evidence.summary.milestone_count, evidence.as_of);
    renderMetric(metrics, tr("sourceQuarterPrecision"), evidence.summary.source_supported_quarter, `${evidence.summary.source_supported_half_year + evidence.summary.source_supported_year + (evidence.summary.source_supported_quarter_range || 0)} ${tr("lowerPrecision")}`);
    renderMetric(metrics, tr("provisionalQuarterPrecision"), evidence.summary.openfs_provisional_quarter, `${evidence.summary.openfs_provisional_year + (evidence.summary.openfs_provisional_half_year || 0) + (evidence.summary.openfs_provisional_quarter_range || 0)} ${tr("lowerPrecision")}`);
    renderMetric(metrics, tr("internalGovernanceEvent"), evidence.summary.openfs_governance_event, tr("internalGovernanceNote"));
    renderMetric(metrics, tr("coverageGap"), evidence.summary.coverage_gap, `${evidence.summary.openfs_provisional} ${tr("provisionalGate")}`);
    renderMetric(metrics, tr("freshnessAttention"), freshness.summary.high + freshness.summary.critical, `${freshness.summary.critical} ${tr("critical")} · ${freshness.summary.past_target_rechecks} ${tr("pastTargetRechecks")}`);
    setText("assurance-caveat-text", tr("evidenceCaveat"));
    [["evidence-audit-commit", evidence], ["freshness-audit-commit", freshness], ["gap-queue-commit", gapQueue], ["center-profile-commit", centerProfile], ["source-audit-commit", source], ["source-triage-commit", sourceTriage], ["dependency-register-commit", dependencies]].forEach(([id, artifact]) => { const link = document.getElementById(id); link.href = artifact.source_commit_url; link.textContent = `${id === "source-triage-commit" ? tr("retrievalTriage") : tr("commit")} ${artifact.source_commit.slice(0, 7)}`; });

    const byRoadmap = new Map(data.roadmaps.map((item) => [item.roadmap_id, {total: 0, primary: 0, target: 0, baseline: 0, gap: 0, provisional: 0, governance: 0}]));
    evidence.entries.forEach((entry) => { const item = byRoadmap.get(entry.roadmap_id); item.total += 1; if (entry.review_status === "classified-primary-event") item.primary += 1; if (entry.review_status === "classified-forward-looking") item.target += 1; if (entry.review_status === "as-of-baseline") item.baseline += 1; if (entry.review_status === "coverage-gap") item.gap += 1; if (entry.review_status === "openfs-provisional") item.provisional += 1; if (entry.review_status === "openfs-governance-event") item.governance += 1; });
    const claimTable = document.createElement("table"); claimTable.className = "assurance-table"; const claimHead = document.createElement("thead"); const claimHeadRow = document.createElement("tr"); [tr("roadmap"), tr("total"), tr("primaryEvent"), tr("forwardTarget"), tr("baseline"), tr("coverageGap"), tr("provisionalGate"), tr("internalGovernanceEvent")].forEach((label) => claimHeadRow.append(makeCell("th", label))); claimHead.append(claimHeadRow); const claimBody = document.createElement("tbody"); byRoadmap.forEach((counts, roadmapId) => { const row = document.createElement("tr"); row.append(makeCell("th", roadmapTitle(roadmapId)), makeCell("td", counts.total), makeCell("td", counts.primary), makeCell("td", counts.target), makeCell("td", counts.baseline), makeCell("td", counts.gap), makeCell("td", counts.provisional), makeCell("td", counts.governance)); claimBody.append(row); }); claimTable.append(claimHead, claimBody); const claimRoot = document.getElementById("claim-audit-by-roadmap"); claimRoot.replaceChildren(claimTable);

    const freshnessTable = document.createElement("table"); freshnessTable.className = "assurance-table"; const freshnessHead = document.createElement("thead"); const freshnessHeadRow = document.createElement("tr"); [tr("roadmap"), tr("milestoneCount"), tr("sourceCount"), tr("critical"), tr("high"), tr("medium"), tr("low")].forEach((label) => freshnessHeadRow.append(makeCell("th", label))); freshnessHead.append(freshnessHeadRow); const freshnessBody = document.createElement("tbody"); freshness.roadmap_summaries.forEach((summary) => { const row = document.createElement("tr"); row.append(makeCell("th", roadmapTitle(summary.roadmap_id)), makeCell("td", summary.milestone_count), makeCell("td", summary.source_count), makeCell("td", summary.critical), makeCell("td", summary.high), makeCell("td", summary.medium), makeCell("td", summary.low)); freshnessBody.append(row); }); freshnessTable.append(freshnessHead, freshnessBody); document.getElementById("freshness-summary").replaceChildren(freshnessTable);
    const followups = freshness.attention_items.filter((item) => item.severity !== "low"); const followupTable = document.createElement("table"); followupTable.className = "assurance-table freshness-attention-table"; const followupHead = document.createElement("thead"); const followupHeadRow = document.createElement("tr"); [tr("priority"), tr("roadmap"), tr("object"), tr("reason"), tr("nextAction")].forEach((label) => followupHeadRow.append(makeCell("th", label))); followupHead.append(followupHeadRow); const followupBody = document.createElement("tbody"); followups.forEach((item) => { const row = document.createElement("tr"); const severityCell = document.createElement("td"); const badge = document.createElement("span"); badge.className = `freshness-severity severity-${item.severity}`; badge.textContent = tr(item.severity); severityCell.append(badge); row.append(severityCell, makeCell("th", roadmapTitle(item.roadmap_id)), makeCell("td", item.object_id), makeCell("td", localized(item, "reason")), makeCell("td", localized(item, "next_action"))); followupBody.append(row); }); followupTable.append(followupHead, followupBody); document.getElementById("freshness-attention").replaceChildren(followupTable);

    const sourceClassOrder = ["vendor-official", "standards-body", "government-official", "research-organization", "project-official", "academic-primary", "openfs-governance"]; const sourceClassTable = document.createElement("table"); sourceClassTable.className = "assurance-table source-class-table"; const sourceClassHead = document.createElement("thead"); const sourceClassHeadRow = document.createElement("tr"); [tr("sourceClass"), tr("total"), tr("sourceClassMeaning")].forEach((label) => sourceClassHeadRow.append(makeCell("th", label))); sourceClassHead.append(sourceClassHeadRow); const sourceClassBody = document.createElement("tbody"); sourceClassOrder.forEach((sourceClass) => { const row = document.createElement("tr"); row.append(makeCell("th", tr(sourceClass)), makeCell("td", source.summary.source_class_counts[sourceClass] || 0), makeCell("td", tr(`${sourceClass}Meaning`))); sourceClassBody.append(row); }); sourceClassTable.append(sourceClassHead, sourceClassBody); document.getElementById("source-class-summary").replaceChildren(sourceClassTable);
    const triageBySource = new Map(sourceTriage.entries.map((item) => [`${item.roadmap_id}:${item.source_id}`, item])); const attention = source.results.filter((item) => item.status !== "reachable"); const sourceTable = document.createElement("table"); sourceTable.className = "assurance-table source-attention-table"; const sourceHead = document.createElement("thead"); const sourceHeadRow = document.createElement("tr"); [tr("roadmap"), tr("source"), tr("status"), tr("retrievalTriage"), tr("url")].forEach((label) => sourceHeadRow.append(makeCell("th", label))); sourceHead.append(sourceHeadRow); const sourceBody = document.createElement("tbody"); attention.forEach((item) => { const row = document.createElement("tr"); const triage = triageBySource.get(`${item.roadmap_id}:${item.source_id}`); const triageCell = document.createElement("td"); const triageLabel = triage && triage.review_outcome === "exact-url-content-confirmed" ? tr("exactUrlConfirmed") : tr("unresolvedRetrieval"); triageCell.textContent = triageLabel; if (triage) triageCell.title = localized(triage, "note"); row.append(makeCell("th", roadmapTitle(item.roadmap_id)), makeCell("td", item.source_id), makeCell("td", sourceStatusLabel(item.status)), triageCell); const url = document.createElement("td"); const link = document.createElement("a"); link.href = item.url; link.target = "_blank"; link.rel = "noopener noreferrer"; link.textContent = item.url; url.append(link); row.append(url); sourceBody.append(row); }); sourceTable.append(sourceHead, sourceBody); document.getElementById("source-audit-results").replaceChildren(sourceTable);

    const gaps = data.roadmap_artifacts.flatMap((roadmap) => roadmap.coverage_gaps.map((gap) => ({...gap, roadmap_id: roadmap.roadmap_id}))).sort((left, right) => left.priority.localeCompare(right.priority) || left.roadmap_id.localeCompare(right.roadmap_id) || left.gap_id.localeCompare(right.gap_id));
    const priorityRoot = document.getElementById("gap-priority-summary"); priorityRoot.replaceChildren(); ["P0", "P1", "P2"].forEach((priority) => { const item = document.createElement("div"); const label = document.createElement("span"); label.className = `gap-priority priority-${priority.toLowerCase()}`; label.textContent = priority; const count = document.createElement("strong"); count.textContent = String(gaps.filter((gap) => gap.priority === priority).length); item.append(label, count); priorityRoot.append(item); });
    const gapTable = document.createElement("table"); gapTable.className = "assurance-table coverage-gap-table"; const gapHead = document.createElement("thead"); const gapHeadRow = document.createElement("tr"); [tr("priority"), tr("roadmap"), tr("scope"), tr("impact"), tr("nextAction")].forEach((label) => gapHeadRow.append(makeCell("th", label))); gapHead.append(gapHeadRow); const gapBody = document.createElement("tbody"); gaps.forEach((gap) => { const row = document.createElement("tr"); const priorityCell = document.createElement("td"); const priority = document.createElement("span"); priority.className = `gap-priority priority-${gap.priority.toLowerCase()}`; priority.textContent = gap.priority; priorityCell.append(priority); row.append(priorityCell, makeCell("th", roadmapTitle(gap.roadmap_id)), makeCell("td", localized(gap, "scope")), makeCell("td", localized(gap, "impact")), makeCell("td", localized(gap, "next_action"))); gapBody.append(row); }); gapTable.append(gapHead, gapBody); document.getElementById("coverage-gap-register").replaceChildren(gapTable);

    const profileSummary = document.getElementById("center-profile-summary"); profileSummary.replaceChildren(); renderMetric(profileSummary, tr("acceptedProfiles"), `${centerProfile.summary.accepted_current_count}/${centerProfile.summary.center_count}`, tr(centerProfile.consensus_status)); renderMetric(profileSummary, tr("evidenceCompleteProfiles"), `${centerProfile.summary.field_evidence_complete_count}/${centerProfile.summary.center_count}`, `${tr("profileContract")} ${centerProfile.profile_contract_target}`); renderMetric(profileSummary, tr("effectiveQueries"), `${centerProfile.summary.effective_followup_query_count}/${centerProfile.summary.followup_query_count}`, centerProfile.source_run_id); renderMetric(profileSummary, tr("verifiedFields"), centerProfile.summary.verified, `${centerProfile.summary.field_slot_count} ${tr("total")}`); renderMetric(profileSummary, tr("notCollectedFields"), centerProfile.summary.not_collected, `${profileFieldLabel("budget")} · ${profileFieldLabel("procurement")}`); setText("center-profile-caveat", localized(centerProfile, "caveat"));
    const profileFieldTable = document.createElement("table"); profileFieldTable.className = "assurance-table center-profile-field-table"; const profileFieldHead = document.createElement("thead"); const profileFieldHeadRow = document.createElement("tr"); [tr("profileField"), tr("verified"), tr("partial"), tr("unknown"), tr("not-collected"), tr("not-applicable")].forEach((label) => profileFieldHeadRow.append(makeCell("th", label))); profileFieldHead.append(profileFieldHeadRow); const profileFieldBody = document.createElement("tbody"); centerProfile.field_summary.forEach((item) => { const row = document.createElement("tr"); row.append(makeCell("th", profileFieldLabel(item.field)), makeCell("td", item.verified), makeCell("td", item.partial), makeCell("td", item.unknown), makeCell("td", item.not_collected), makeCell("td", item.not_applicable)); profileFieldBody.append(row); }); profileFieldTable.append(profileFieldHead, profileFieldBody); document.getElementById("center-profile-fields").replaceChildren(profileFieldTable);
    const centerTable = document.createElement("table"); centerTable.className = "assurance-table center-profile-center-table"; const centerHead = document.createElement("thead"); const centerHeadRow = document.createElement("tr"); [tr("centerName"), tr("profileDecision"), tr("fieldSummary"), tr("officialPage")].forEach((label) => centerHeadRow.append(makeCell("th", label))); centerHead.append(centerHeadRow); const centerBody = document.createElement("tbody"); centerProfile.centers.forEach((center) => { const counts = center.field_states.reduce((result, item) => { result[item.status] = (result[item.status] || 0) + 1; return result; }, {}); const row = document.createElement("tr"); row.append(makeCell("th", language === "ja" ? center.name_ja : center.name_en), makeCell("td", center.accepted_current ? tr("acceptedCurrent") : tr("unaccepted")), makeCell("td", `${tr("verified")} ${counts.verified || 0} · ${tr("partial")} ${counts.partial || 0} · ${tr("unknown")} ${counts.unknown || 0} · ${tr("not-collected")} ${counts["not-collected"] || 0}`)); const official = document.createElement("td"); const officialLink = document.createElement("a"); officialLink.href = center.official_url; officialLink.target = "_blank"; officialLink.rel = "noopener noreferrer"; officialLink.textContent = tr("officialPage"); official.append(officialLink); row.append(official); centerBody.append(row); }); centerTable.append(centerHead, centerBody); document.getElementById("center-profile-centers").replaceChildren(centerTable);

    const queueSummary = document.getElementById("gap-queue-summary"); queueSummary.replaceChildren(); [[tr("p0ExplicitQueries"), gapQueue.summary.p0_explicit_query_overrides], [tr("p0FallbackQueries"), gapQueue.summary.p0_generated_query_fallbacks], [tr("assignedConsensus"), gapQueue.summary.consensus_review], [tr("productionReady"), gapQueue.summary.ready_for_scheduled_discovery]].forEach(([labelText, value]) => { const item = document.createElement("div"); item.append(makeCell("span", labelText), makeCell("strong", value)); queueSummary.append(item); });
    const p0Assignments = gapQueue.assignments.filter((item) => item.priority === "P0"); const queueTable = document.createElement("table"); queueTable.className = "assurance-table gap-assignment-table"; const queueHead = document.createElement("thead"); const queueHeadRow = document.createElement("tr"); [tr("gapId"), tr("roadmap"), tr("assignment"), tr("cadence"), tr("queryPlan"), tr("closurePlan"), tr("executionState"), tr("nextAction")].forEach((label) => queueHeadRow.append(makeCell("th", label))); queueHead.append(queueHeadRow); const queueBody = document.createElement("tbody"); p0Assignments.forEach((item) => { const row = document.createElement("tr"); row.append(makeCell("th", item.gap_id), makeCell("td", roadmapTitle(item.roadmap_id)), makeCell("td", item.assignment_ref), makeCell("td", tr(item.cadence)), makeQueryPlanCell(item), makeClosurePlanCell(item), makeCell("td", tr(item.execution_state)), makeCell("td", localized(item, "next_action"))); queueBody.append(row); }); queueTable.append(queueHead, queueBody); document.getElementById("gap-assignment-queue").replaceChildren(queueTable);

    const dependencyRoot = document.getElementById("dependency-register"); dependencyRoot.replaceChildren(); const portfolioGate = document.createElement("article"); portfolioGate.className = "portfolio-gate"; const portfolioGateTitle = document.createElement("h4"); portfolioGateTitle.textContent = tr("portfolioGateTitle"); const portfolioGateNote = document.createElement("p"); portfolioGateNote.textContent = tr("portfolioGateNote"); const portfolioGateRefs = document.createElement("p"); portfolioGateRefs.className = "mono-list"; portfolioGateRefs.textContent = dependencies.portfolio_gate_gap_refs.join(" · "); portfolioGate.append(portfolioGateTitle, portfolioGateNote, portfolioGateRefs); dependencyRoot.append(portfolioGate); dependencies.dependencies.forEach((dependency) => { const item = document.createElement("article"); const route = document.createElement("h4"); route.textContent = `${roadmapTitle(dependency.upstream_roadmap_id)} → ${roadmapTitle(dependency.downstream_roadmap_id)}`; const meta = document.createElement("p"); meta.className = "dependency-meta"; meta.textContent = `${tr("relationship")}: ${relationshipLabel(dependency.relationship)} · ${tr("criticality")}: ${tr(dependency.criticality)} · ${dependencyBasisLabel(dependency.basis)}`; const statement = document.createElement("p"); statement.textContent = localized(dependency, "statement"); const detail = document.createElement("dl"); [[tr("decisionImpact"), localized(dependency, "decision_impact")], [tr("delayRisk"), localized(dependency, "risk_if_late")], [tr("gates"), dependency.gate_refs.join(", ")]].forEach(([term, value]) => { const group = document.createElement("div"); group.append(makeCell("dt", term), makeCell("dd", value)); detail.append(group); }); item.append(route, meta, statement, detail); dependencyRoot.append(item); });
    const externalRoot = document.getElementById("external-constraints"); externalRoot.replaceChildren(); dependencies.external_constraints.forEach((constraint) => { const item = document.createElement("article"); const title = document.createElement("h4"); title.textContent = localized(constraint, "name"); const body = document.createElement("p"); body.textContent = localized(constraint, "impact"); item.append(title, body); externalRoot.append(item); });
  }

  function renderScenarioCards(root) {
    root.replaceChildren(); data.scenarios.forEach((scenario) => { const item = document.createElement("article"); const id = document.createElement("span"); id.className = "eyebrow"; id.textContent = scenario.scenario_id; const title = document.createElement("h3"); const link = document.createElement("a"); link.href = scenarioLink(scenario); link.textContent = localized(scenario, "title"); title.append(link); const objective = document.createElement("p"); objective.textContent = localized(scenario, "objective"); const meta = document.createElement("p"); meta.className = "scenario-card-meta"; meta.textContent = `${scenario.planning_horizon} · ${tr("provisional")} · ${tr("consensusStatus")}: ${tr("incomplete")}`; item.append(id, title, objective, meta); root.append(item); });
  }

  function quarterOrdinal(point) {
    return point.year * 4 + Number(point.quarter.slice(1)) - 1;
  }

  function timelineGridColumns(quarterCount) {
    return `minmax(180px, 240px) repeat(${quarterCount}, 34px)`;
  }

  function renderScenarioTimeline(root, rows, startYear, endYear) {
    root.replaceChildren();
    const quarterCount = (endYear - startYear + 1) * 4;
    const startOrdinal = startYear * 4;
    const timeline = document.createElement("div");
    timeline.className = "scenario-timeline";

    const years = document.createElement("div");
    years.className = "scenario-timeline-grid scenario-timeline-years";
    years.style.gridTemplateColumns = timelineGridColumns(quarterCount);
    years.append(makeCell("div", tr("timelineDomain")));
    for (let year = startYear; year <= endYear; year += 1) {
      const label = makeCell("div", String(year));
      label.style.gridColumn = `${2 + (year - startYear) * 4} / span 4`;
      years.append(label);
    }
    timeline.append(years);

    const quarters = document.createElement("div");
    quarters.className = "scenario-timeline-grid scenario-timeline-quarters";
    quarters.style.gridTemplateColumns = timelineGridColumns(quarterCount);
    quarters.append(makeCell("div", tr("timelineQuarter")));
    for (let index = 0; index < quarterCount; index += 1) {
      quarters.append(makeCell("div", `Q${index % 4 + 1}`));
    }
    timeline.append(quarters);

    rows.forEach((row) => {
      const line = document.createElement("div");
      line.className = "scenario-timeline-grid scenario-timeline-row";
      line.style.gridTemplateColumns = timelineGridColumns(quarterCount);
      const label = document.createElement("div");
      label.className = "scenario-timeline-label";
      if (row.href) {
        const link = document.createElement("a");
        link.href = row.href;
        link.textContent = row.label;
        label.append(link);
      } else {
        label.textContent = row.label;
      }
      line.append(label);
      row.phases.forEach((phase) => {
        const start = quarterOrdinal(phase.start) - startOrdinal;
        const end = quarterOrdinal(phase.end) - startOrdinal;
        const bar = document.createElement("div");
        bar.className = `scenario-phase scenario-stage-${phase.stage}${phase.context_scope === "hpci-specific" ? " scenario-phase-hpci" : ""}`;
        bar.style.gridColumn = `${2 + start} / span ${end - start + 1}`;
        const contextLabel = phase.context_scope === "hpci-specific" ? `${tr("hpciSpecific")} · ` : "";
        bar.textContent = `${contextLabel}${localized(phase, "title")}`;
        bar.title = `${contextLabel}${tr(`stage${phase.stage.charAt(0).toUpperCase()}${phase.stage.slice(1)}`)}: ${localized(phase, "title")}\n${localized(phase, "condition")}`;
        line.append(bar);
      });
      timeline.append(line);
    });
    root.append(timeline);
  }

  function comparisonValue(scenario, row) {
    if (row === "objective") return localized(scenario, "objective");
    if (row.startsWith("option:")) {
      const domain = row.slice("option:".length);
      const option = scenario.technology_options.find((item) => item.domain === domain);
      return option ? `${localized(option, "candidate")}: ${localized(option, "role")}` : "";
    }
    if (row === "unknownCount") return String(localizedArray(scenario, "uncertainties").length);
    return localized(scenario.evaluation.reversibility, "rationale");
  }

  function planningEvidenceLabel(key) {
    const labels = {
      ja: {
        title: "計画判断に必要な根拠の充足状況",
        lead: "更新時期、運用実績、費用、性能、アプリケーション要件を同じ形式で監査します。数値が登録されていても、比較条件や合意が未確認の項目は正式判断に使いません。",
        dimension: "判断項目", coverage: "充足範囲", finding: "現時点の把握", planningUse: "計画への使い方", blockers: "未確認事項",
        partial: "一部確認", blocked: "判断保留",
        scenarioTitle: "公開根拠から見たこの案の位置付け",
        commitmentBoundary: "確定しない範囲", blockingDimensions: "判断を止める項目",
      },
      en: {
        title: "Evidence readiness for planning decisions",
        lead: "Lifecycle, operations, cost, performance and application requirements are audited in one format. A registered number is not used for a formal decision when comparability or consensus remains unverified.",
        dimension: "Decision dimension", coverage: "Coverage", finding: "Current finding", planningUse: "Planning use", blockers: "Unresolved conditions",
        partial: "Partial", blocked: "Decision blocked",
        scenarioTitle: "Position of this option against public evidence",
        commitmentBoundary: "Commitment boundary", blockingDimensions: "Blocking dimensions",
      },
    };
    return labels[language][key] || key;
  }

  function renderPlanningEvidenceSummary() {
    const readiness = data.planning_evidence_readiness;
    if (!readiness) return;
    setText("planning-evidence-title", planningEvidenceLabel("title"));
    setText("planning-evidence-lead", planningEvidenceLabel("lead"));
    setText("planning-evidence-caveat", localized(readiness, "caveat"));
    const table = document.createElement("table");
    table.className = "scenario-comparison-table planning-evidence-table";
    const head = document.createElement("thead");
    const headRow = document.createElement("tr");
    ["dimension", "coverage", "finding", "planningUse", "blockers"].forEach((key) => headRow.append(makeCell("th", planningEvidenceLabel(key))));
    head.append(headRow);
    const body = document.createElement("tbody");
    readiness.dimensions.forEach((dimension) => {
      const row = document.createElement("tr");
      const status = document.createElement("span");
      status.className = `status-badge status-${dimension.status}`;
      status.textContent = planningEvidenceLabel(dimension.status);
      const dimensionCell = document.createElement("th");
      dimensionCell.append(makeCell("span", localized(dimension, "label")), status);
      const coverage = document.createElement("div");
      const primaryCoverage = document.createElement("strong");
      primaryCoverage.textContent = `${dimension.coverage.numerator}/${dimension.coverage.denominator} ${localized(dimension.coverage, "unit")}`;
      coverage.append(primaryCoverage);
      if (dimension.supporting_coverages.length) {
        const supporting = document.createElement("ul");
        supporting.className = "supporting-coverage-list";
        dimension.supporting_coverages.forEach((item) => {
          const line = document.createElement("li");
          line.textContent = `${item.numerator}/${item.denominator} ${localized(item, "unit")}`;
          supporting.append(line);
        });
        coverage.append(supporting);
      }
      const coverageCell = document.createElement("td");
      coverageCell.append(coverage);
      row.append(
        dimensionCell,
        coverageCell,
        makeCell("td", localized(dimension, "finding")),
        makeCell("td", localized(dimension, "planning_use")),
        makeCell("td", localizedArray(dimension, "blockers").join("; ")),
      );
      body.append(row);
    });
    table.append(head, body);
    document.getElementById("planning-evidence-dimensions").replaceChildren(table);
  }

  function renderScenarioPlanningEvidence(scenario) {
    const readiness = data.planning_evidence_readiness;
    if (!readiness) return;
    const assessment = readiness.scenario_assessments.find((item) => item.scenario_id === scenario.scenario_id);
    if (!assessment) return;
    setText("scenario-planning-evidence-title", planningEvidenceLabel("scenarioTitle"));
    setText("scenario-planning-evidence-implication", localized(assessment, "implication"));
    setText("scenario-commitment-boundary-label", planningEvidenceLabel("commitmentBoundary"));
    setText("scenario-commitment-boundary", localized(assessment, "commitment_boundary"));
    setText("scenario-blocking-dimensions-label", planningEvidenceLabel("blockingDimensions"));
    const labels = assessment.blocking_dimension_ids.map((id) => {
      const dimension = readiness.dimensions.find((item) => item.dimension_id === id);
      return dimension ? localized(dimension, "label") : id;
    });
    setText("scenario-blocking-dimensions", labels.join(" · "));
    setText("scenario-planning-evidence-caveat", localized(readiness, "caveat"));
  }

  function renderScenarioIndex() {
    renderScenarioCards(document.getElementById("scenario-index-list"));
    window.OpenFSBudget.controls(document.getElementById("portfolio-budget-controls"), language, (state) => {
      window.OpenFSBudget.renderAllocations(document.getElementById("portfolio-budget-comparison"), data.scenarios, state, language, rootPrefix);
      refreshScenarioLinks();
    });
    window.OpenFSBudget.renderRegister(document.getElementById("portfolio-procurement-register"), language, rootPrefix);
    renderPlanningEvidenceSummary();
    renderScenarioTimeline(
      document.getElementById("scenario-portfolio-timeline"),
      data.scenarios.map((scenario) => ({
        label: localized(scenario, "title"),
        href: scenarioLink(scenario),
        phases: scenario.implementation_path.phases.filter((phase) => phase.domain === "portfolio"),
      })),
      Math.min(...data.scenarios.map((scenario) => scenario.implementation_path.start_year)),
      Math.max(...data.scenarios.map((scenario) => scenario.implementation_path.end_year)),
    );
    const rows = [
      ["objective", "objective"],
      ["compute", "option:compute"],
      ["memory", "option:memory"],
      ["interconnect", "option:interconnect"],
      ["systemSoftware", "option:system-software"],
      ["applications", "option:applications"],
      ["unknownCount", "unknownCount"],
      ["reversibility", "reversibility"],
    ];
    const table = document.createElement("table"); table.className = "scenario-comparison-table"; const head = document.createElement("thead"); const headRow = document.createElement("tr"); headRow.append(makeCell("th", tr("criterion"))); data.scenarios.forEach((scenario) => { const cell = document.createElement("th"); const link = document.createElement("a"); link.href = scenarioLink(scenario); link.textContent = localized(scenario, "title"); cell.append(link); headRow.append(cell); }); head.append(headRow); const body = document.createElement("tbody"); rows.forEach(([label, value]) => { const row = document.createElement("tr"); row.append(makeCell("th", tr(label))); data.scenarios.forEach((scenario) => row.append(makeCell("td", comparisonValue(scenario, value)))); body.append(row); }); table.append(head, body); document.getElementById("scenario-comparison").replaceChildren(table);
    const gates = document.getElementById("scenario-gates"); gates.replaceChildren(); data.scenarios.forEach((scenario) => { const item = document.createElement("section"); const title = document.createElement("h4"); title.textContent = localized(scenario, "title"); const list = document.createElement("ol"); localizedArray(scenario, "decision_gates").forEach((gate) => list.append(makeCell("li", gate))); item.append(title, list); gates.append(item); });
  }

  function renderPlanSection(root, key, value) {
    const section = document.createElement("section"); section.className = "scenario-plan-section"; const title = document.createElement("h3"); title.textContent = tr(key); const summary = document.createElement("p"); summary.textContent = localized(value, "summary"); const list = document.createElement("ul"); localizedArray(value, "priorities").forEach((priority) => list.append(makeCell("li", priority))); const refs = document.createElement("p"); refs.className = "mono-list"; refs.textContent = (value.roadmap_refs || []).join(" · "); section.append(title, summary, list, refs); root.append(section);
  }

  function architectureQuantity(component) {
    return component.quantity === null
      ? (language === "ja" ? "数量・容量は未算出" : "Quantity / capacity not calculated")
      : `${component.quantity.toLocaleString(language === "ja" ? "ja-JP" : "en-US")} ${localized(component, "unit")}`;
  }

  function architectureComponent(component, allocation) {
    const item = document.createElement("article");
    item.className = `architecture-node architecture-${component.component_type}`;
    const type = document.createElement("span"); type.className = "architecture-node-type"; type.textContent = `${language === "ja" ? "仮配分" : "Allocation"}: ${window.OpenFSBudget.money(allocation.amount, language)}`;
    const title = document.createElement("h4"); title.textContent = localized(component, "label");
    const quantity = document.createElement("strong"); quantity.textContent = architectureQuantity(component);
    const role = document.createElement("p"); role.textContent = localized(component, "role");
    item.append(type, title, quantity, role);
    return item;
  }

  function renderArchitectureDiagram(option, allocations) {
    const figure = document.getElementById("scenario-architecture-diagram");
    figure.replaceChildren();
    const groups = [
      ["architecture-service-row", ["management"]],
      ["architecture-compute-row", ["compute-cpu", "compute-accelerator", "large-memory", "pilot"]],
      ["architecture-network-row", ["interconnect"]],
      ["architecture-data-row", ["storage", "facility"]],
    ];
    groups.forEach(([className, types], index) => {
      const row = document.createElement("div"); row.className = className;
      option.components.filter((item) => types.includes(item.component_type)).forEach((item) => row.append(architectureComponent(item, allocations.find((a) => a.id === item.component_type))));
      if (row.childElementCount) figure.append(row);
      if (row.childElementCount && index < groups.length - 1) {
        const connector = document.createElement("div"); connector.className = "architecture-connector"; connector.setAttribute("aria-hidden", "true"); figure.append(connector);
      }
    });
    const caption = document.createElement("figcaption"); caption.textContent = localized(option, "caveat"); figure.append(caption);
  }

  function renderArchitectureSpecs(option) {
    const root = document.getElementById("scenario-architecture-specs");
    const table = document.createElement("table"); table.className = "architecture-spec-table";
    const head = document.createElement("thead"); const headRow = document.createElement("tr");
    [tr("component"), tr("quantity"), tr("role")].forEach((label) => headRow.append(makeCell("th", label))); head.append(headRow);
    const body = document.createElement("tbody");
    option.components.forEach((item) => { const row = document.createElement("tr"); row.append(makeCell("th", localized(item, "label")), makeCell("td", architectureQuantity(item)), makeCell("td", localized(item, "role"))); body.append(row); });
    table.append(head, body); root.replaceChildren(table);
  }

  function renderBudgetOptions(scenario) {
    window.OpenFSBudget.controls(document.getElementById("scenario-budget-options"), language, (state) => {
      window.OpenFSBudget.renderAllocations(document.getElementById("scenario-budget-summary"), [scenario], state, language, rootPrefix);
      renderArchitectureDiagram(scenario.budget_options[0], window.OpenFSBudget.allocation(data.budget_planning, scenario.scenario_id, state.budget));
      renderArchitectureSpecs(scenario.budget_options[0]);
    });
    window.OpenFSBudget.renderRegister(document.getElementById("scenario-budget-references"), language, rootPrefix);
  }

  function renderScenarioDetail() {
    const scenario = data.scenarios.find((item) => item.scenario_id === document.body.dataset.scenarioId); if (!scenario) { document.querySelector("main").textContent = "Scenario unavailable."; return; }
    document.title = `${localized(scenario, "title")} | OpenFS`; setText("scenario-breadcrumb-title", localized(scenario, "title")); setText("scenario-id", scenario.scenario_id); setText("scenario-title", localized(scenario, "title")); setText("scenario-objective", localized(scenario, "objective")); setText("scenario-horizon", scenario.planning_horizon); setText("scenario-research-status", tr(scenario.research_status)); setText("scenario-consensus-status", tr(scenario.consensus_status)); setText("scenario-caveat", localized(scenario, "caveat")); setText("scenario-artifact-id", scenario.scenario_id); setText("scenario-plan-version", scenario.plan_version); setText("scenario-effective-from", scenario.effective_from); setText("scenario-review-due", scenario.review_due); setText("scenario-supersedes", scenario.supersedes.length ? scenario.supersedes.join(" · ") : tr("noSupersededVersion")); setText("scenario-evidence-refs", scenario.evidence_refs.join(" · ")); setText("scenario-revision-updated", formatJst(scenario.updated_at)); const updated = document.getElementById("scenario-updated"); updated.href = scenario.source_commit_url; updated.textContent = formatJst(scenario.updated_at); const commit = document.getElementById("scenario-source-commit"); commit.href = scenario.source_commit_url; commit.textContent = scenario.source_commit;
    window.OpenFSFeedback.mount("scenario-feedback", {kind: "scenario", id: scenario.scenario_id, title: localized(scenario, "title"), path: scenario.path});
    renderBudgetOptions(scenario);
    renderScenarioPlanningEvidence(scenario);
    const timelineDomains = ["compute", "memory", "interconnect", "storage-data", "system-software", "applications", "facility-operations", "procurement-governance"];
    renderScenarioTimeline(
      document.getElementById("scenario-detail-timeline"),
      timelineDomains.map((domain) => ({label: domain === "applications" ? tr("applicationsDomain") : tr(domain), phases: scenario.implementation_path.phases.filter((phase) => phase.domain === domain)})).filter((row) => row.phases.length),
      scenario.implementation_path.start_year,
      scenario.implementation_path.end_year,
    );
    const contextNotes = document.getElementById("scenario-context-notes"); contextNotes.replaceChildren(); scenario.context_notes.forEach((note) => { const item = document.createElement("article"); const badge = document.createElement("span"); badge.className = `context-note-badge context-${note.scope}`; badge.textContent = note.scope === "hpci-specific" ? tr("hpciSpecific") : tr("reusable"); const body = document.createElement("p"); body.textContent = localized(note, "note"); const refs = document.createElement("p"); refs.className = "mono-list"; refs.textContent = note.evidence_refs.join(" · "); item.append(badge, body, refs); contextNotes.append(item); });
    const sections = document.getElementById("scenario-plan-sections"); sections.replaceChildren(); renderPlanSection(sections, "architecture", scenario.architecture); renderPlanSection(sections, "systemSoftware", scenario.system_software); renderPlanSection(sections, "applications", scenario.applications);
    const centers = document.getElementById("scenario-center-impacts"); centers.replaceChildren(); scenario.center_impacts.forEach((impact) => { const item = document.createElement("article"); const title = document.createElement("h4"); title.textContent = localized(impact, "center_group"); const details = document.createElement("dl"); [[tr("fit"), localized(impact, "fit")], [tr("migration"), localized(impact, "migration")], [tr("unverified"), localizedArray(impact, "unverified_conditions").join("; ")]].forEach(([term, value]) => { const group = document.createElement("div"); group.append(makeCell("dt", term), makeCell("dd", value)); details.append(group); }); item.append(title, details); centers.append(item); });
    const options = document.getElementById("scenario-technology-options"); options.replaceChildren(); scenario.technology_options.forEach((option) => { const item = document.createElement("article"); const domain = document.createElement("span"); domain.className = "technology-option-domain"; domain.textContent = option.domain === "applications" ? tr("applicationsDomain") : tr(option.domain); const title = document.createElement("h4"); title.textContent = localized(option, "candidate"); const details = document.createElement("dl"); [[tr("role"), localized(option, "role")], [tr("maturityGate"), localized(option, "maturity_gate")], [tr("fallback"), localized(option, "fallback")], [tr("evidence"), option.evidence_refs.join(" · ")]].forEach(([term, value]) => { const group = document.createElement("div"); group.append(makeCell("dt", term), makeCell("dd", value)); details.append(group); }); item.append(domain, title, details); options.append(item); });
    const contracts = document.getElementById("scenario-evidence-contracts"); contracts.replaceChildren(); (scenario.decision_evidence_contracts || []).forEach((contract) => { const item = document.createElement("article"); const id = document.createElement("span"); id.className = "technology-option-domain"; id.textContent = contract.contract_id; const title = document.createElement("h4"); title.textContent = localized(contract, "title"); const effect = document.createElement("p"); effect.textContent = localized(contract, "effect"); const details = document.createElement("dl"); [[tr("coveredGaps"), contract.gap_refs.join(" · ")], [tr("schemas"), repositoryPathLinks(contract.schema_paths, scenario.source_commit)], [tr("validators"), repositoryPathLinks(contract.validator_paths, scenario.source_commit)], [tr("acceptanceEffect"), tr("candidateOnly")]].forEach(([term, value]) => { const group = document.createElement("div"); const definition = document.createElement("dd"); if (typeof value === "string") definition.textContent = value; else definition.append(value); group.append(makeCell("dt", term), definition); details.append(group); }); item.append(id, title, effect, details); contracts.append(item); });
    const evalTable = document.createElement("table"); evalTable.className = "scenario-evaluation-table"; const head = document.createElement("thead"); const headRow = document.createElement("tr"); [tr("criterion"), tr("assessment"), tr("evidence")].forEach((label) => headRow.append(makeCell("th", label))); head.append(headRow); const body = document.createElement("tbody"); Object.entries(scenario.evaluation).forEach(([criterion, evaluation]) => { const row = document.createElement("tr"); const label = criterion === "reversibility" ? tr("reversibilityCriterion") : tr(criterion); row.append(makeCell("th", label), makeCell("td", localized(evaluation, "rationale")), makeCell("td", evaluation.evidence_refs.join(", "))); body.append(row); }); evalTable.append(head, body); document.getElementById("scenario-evaluation").replaceChildren(evalTable);
    setText("scenario-blocking-gaps", scenario.decision_blocking_gap_refs.join(" · ")); const uncertaintyList = document.getElementById("scenario-uncertainties"); uncertaintyList.replaceChildren(); localizedArray(scenario, "uncertainties").forEach((item) => uncertaintyList.append(makeCell("li", item))); const gateList = document.getElementById("scenario-decision-gates"); gateList.replaceChildren(); localizedArray(scenario, "decision_gates").forEach((item) => gateList.append(makeCell("li", item)));
  }

  function renderConsensusCards(root) {
    root.replaceChildren();
    data.consensus_packages.forEach((item) => {
      const card = document.createElement("article");
      const id = document.createElement("span"); id.className = "eyebrow"; id.textContent = item.package_id;
      const packageVersion = item.package_id.split("-").at(-1);
      const title = document.createElement("h3"); const link = document.createElement("a"); link.href = consensusLink(item); link.textContent = `${item.portfolio_summary.roadmap_count} P0 ${tr("roadmapsUnit")} · ${packageVersion}`; title.append(link);
      const status = document.createElement("span"); status.className = `status-badge status-${item.gate.status}`; status.textContent = tr(item.gate.status);
      const summary = document.createElement("p"); summary.textContent = `${item.portfolio_summary.milestone_count} ${tr("milestoneCount")} · ${item.portfolio_summary.source_count} ${tr("sourceCount")} · ${item.portfolio_summary.coverage_gap_count} ${tr("coverageGapsUnit")}`;
      const meta = document.createElement("p"); meta.className = "scenario-card-meta"; meta.textContent = `${tr("assessmentCount")}: ${item.gate.counts.assessments} · ${tr("supportCount")}: ${item.gate.counts.support}`;
      card.append(id, title, status, summary, meta); root.append(card);
    });
  }

  function renderConsensusIndex() {
    renderConsensusCards(document.getElementById("consensus-package-list"));
  }

  function renderConsensusDetail() {
    const item = data.consensus_packages.find((candidate) => candidate.package_id === document.body.dataset.packageId);
    if (!item) { document.querySelector("main").textContent = "Consensus package unavailable."; return; }
    document.title = `${item.package_id} | OpenFS`;
    setText("consensus-breadcrumb-title", item.package_id); setText("consensus-package-id", item.package_id); setText("consensus-effect", tr(item.gate.status === "ready-for-human-decision" ? "gateEffectReady" : "gateEffectIncomplete"));
    const status = document.getElementById("consensus-gate-status"); status.textContent = tr(item.gate.status); status.className = `status-badge status-${item.gate.status}`;
    const base = document.getElementById("consensus-base-commit"); base.href = item.base_commit_url; base.textContent = `${tr("baseCommit")} ${item.base_commit.slice(0, 12)}`;
    const metrics = document.getElementById("consensus-metrics"); metrics.replaceChildren();
    renderMetric(metrics, tr("assessmentCount"), item.gate.counts.assessments, `${item.consensus_policy.minimum_assessments} ${tr("threshold")}`);
    renderMetric(metrics, tr("supportCount"), item.gate.counts.support, `${item.consensus_policy.minimum_support} ${tr("threshold")}`);
    renderMetric(metrics, tr("modelFamilies"), item.gate.counts.support_model_families, `${item.consensus_policy.minimum_model_families} ${tr("threshold")}`);
    renderMetric(metrics, tr("providers"), item.gate.counts.support_providers, `${item.consensus_policy.minimum_providers} ${tr("threshold")}`);
    renderMetric(metrics, tr("harnesses"), item.gate.counts.support_harnesses, `${item.consensus_policy.minimum_harnesses} ${tr("threshold")}`);
    renderMetric(metrics, tr("criticReviews"), item.gate.counts.critic_reviews, item.consensus_policy.require_falsification_review ? ">= 1" : "0");
    renderMetric(metrics, tr("pinnedArtifacts"), item.artifact_count || 0, item.base_commit.slice(0, 12));

    const requirements = document.createElement("table"); requirements.className = "assurance-table"; const head = document.createElement("thead"); const headRow = document.createElement("tr"); [tr("requirement"), tr("threshold")].forEach((label) => headRow.append(makeCell("th", label))); head.append(headRow); const body = document.createElement("tbody");
    [["minimum_assessments", item.consensus_policy.minimum_assessments], ["minimum_support", item.consensus_policy.minimum_support], ["minimum_support_independence_groups", item.consensus_policy.minimum_support_independence_groups], ["minimum_origin_groups", item.consensus_policy.minimum_origin_groups], ["minimum_model_families", item.consensus_policy.minimum_model_families], ["minimum_providers", item.consensus_policy.minimum_providers], ["minimum_harnesses", item.consensus_policy.minimum_harnesses], ["require_falsification_review", item.consensus_policy.require_falsification_review], ["require_human_decision", item.consensus_policy.require_human_decision]].forEach(([name, value]) => { const row = document.createElement("tr"); row.append(makeCell("th", name), makeCell("td", String(value))); body.append(row); }); requirements.append(head, body); document.getElementById("consensus-requirements").replaceChildren(requirements);

    const units = document.getElementById("consensus-review-units"); units.replaceChildren(); item.review_units.forEach((unit) => { const card = document.createElement("article"); const title = document.createElement("h4"); title.textContent = localized(unit, "title"); const id = document.createElement("p"); id.className = "mono-list"; id.textContent = `${unit.unit_id} · ${unit.kind}`; const checks = document.createElement("p"); checks.textContent = `${tr("reviewChecks")}: ${unit.required_checks.join(", ")}`; card.append(title, id, checks); units.append(card); });

    const reviewers = document.getElementById("consensus-reviewers"); reviewers.replaceChildren(); setText("consensus-reviewer-note", item.eligible_reviewers.length ? "" : tr("noEligibleReviewers")); item.eligible_reviewers.forEach((reviewer) => { const card = document.createElement("article"); const title = document.createElement("h4"); title.textContent = `${reviewer.provider} · ${reviewer.model_family}`; const meta = document.createElement("p"); meta.className = "mono-list"; meta.textContent = `${reviewer.review_id} · ${reviewer.role} · ${reviewer.overall_verdict}`; const profile = document.createElement("p"); profile.textContent = `${reviewer.prompt_profile} · ${reviewer.independence_group} · ${reviewer.origin_group}`; const harness = document.createElement("a"); harness.href = reviewer.harness_commit_url || reviewer.harness_repository_url; harness.target = "_blank"; harness.rel = "noopener noreferrer"; harness.textContent = `${reviewer.harness_id} @ ${reviewer.harness_commit.slice(0, 12)}`; card.append(title, meta, profile, harness); reviewers.append(card); });

    const unmet = document.getElementById("consensus-unmet"); unmet.replaceChildren(); item.gate.unmet_requirements.forEach((value) => unmet.append(makeCell("li", value)));
    const limitations = document.getElementById("consensus-limitations"); limitations.replaceChildren(); item.known_limitations.forEach((limitation) => { const card = document.createElement("article"); const title = document.createElement("h4"); title.textContent = limitation.limitation_id; const body = document.createElement("p"); body.textContent = localized(limitation, "description"); const effect = document.createElement("span"); effect.className = "status-badge"; effect.textContent = limitation.effect; card.append(title, body, effect); limitations.append(card); });
    setText("consensus-provenance-id", item.package_id); setText("consensus-manifest-digest", item.manifest_sha256); const source = document.getElementById("consensus-source-commit"); source.href = item.source_commit_url; source.textContent = item.source_commit; const manifest = document.getElementById("consensus-manifest"); manifest.href = item.manifest_url;
  }

  function render() { applyStaticCopy(); if (page === "roadmap-evidence") renderEvidencePage(); if (page === "scenario-index") renderScenarioIndex(); if (page === "scenario-detail") renderScenarioDetail(); if (page === "consensus-index") renderConsensusIndex(); if (page === "consensus-detail") renderConsensusDetail(); }
  document.querySelectorAll("[data-language]").forEach((button) => button.addEventListener("click", () => { language = button.dataset.language; rememberLanguage(language); render(); }));
  render();
})();
