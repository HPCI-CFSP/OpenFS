# September 2 Planning-Evidence Priorities

## English

This update implements the human-approved priorities in `DIR-900024` using
public information only. All findings remain provisional work by one AI agent
and one model. Independent Consensus, production merge, and deployment are not
part of this update.

### HPCI System Evidence

The FY2026 HPCI inventory still distinguishes annual call availability from a
system lifecycle. Existing public roadmap evidence is now linked directly from
the three SQUID node groups and HOKUSAI BigWaterfall2, in addition to the links
already recorded for Furo-II and Sirius. Twenty of the 27 inventory entries
still lack a directly linked, institution-confirmed lifecycle milestone, so
`GAP-HPCI-SYS-001` remains P0 and open.

The AIST system guide supplies the previously missing ABCI 3.0 configuration:
766 compute nodes and 6,128 H200 GPUs, with published per-node memory and
InfiniBand connectivity and approximately 75 PB of shared storage. No peak
performance was derived from component specifications. HPCI allocations, queue
conditions, and capacity definitions still need alignment across providers.

### Procurement Evidence

The RIKEN contract-results disclosure records a JPY 5,148,000 tax-inclusive
contract for an AI for Science InfiniBand switch package, separately from the
JPY 6,731,406,000 supercomputer package. The public RIKEN R-CCS system overview
also records a planned 400-node GB200 NVL4 system, an XDR 800 Gb/s fabric, and
1,081.34 TB of effective all-NVMe Lustre storage.

OpenFS does not equate the small switch contract with any of the 25 switches in
the public architecture, subtract it from the computer package, or derive a
unit price. The final specification, quantity, overlap, component prices, and
installation and maintenance scope remain unresolved under `PCG-001` through
`PCG-003`.

### GENESIS Calibration Candidate

The 2021 GENESIS paper publishes 1 Å PME weak-scaling measurements on
Fugaku from 16 through 16,384 nodes. Six alternating points calibrate a
piecewise linear interpolation against log2(node count), while five disjoint
points are held out for validation. The largest relative error on those
holdout points is about 6.2%.

`PMCAL-GENESIS-WEAK-001` is deliberately not a validated model card or a
future-system forecast. It covers one system, one workload, and one measurement
series. Published values are rounded, and no independent remeasurement or
cross-architecture validation is available. It remains Consensus-incomplete
and ineligible for procurement use.

### Application Demand and Infrastructure Requirements

The six EEA1 applications are compared on eight planning dimensions: compute
throughput, memory capacity and bandwidth, scale-up and scale-out interconnect,
storage and I/O, workflow deadlines, software portability, and data governance.
Each cell carries a qualitative demand level, evidence-based rationale, and a
measurement or confirmation gap.

The matrix is a planning index, not a bill of materials. Its levels are not
node counts, bandwidth requirements, or procurement specifications and must
not be aggregated into a score. Quantitative requirements await pinned inputs,
measurements, application-owner review, and independent Consensus.

## 日本語

本更新は、`DIR-900024`で承認された優先課題を、公開情報だけを用いて実施したもの
です。単一のAIエージェントと単一モデルによる暫定結果であり、独立Consensus、
本番へのマージ、公開環境への反映は本更新の対象外です。

### HPCIシステムの根拠

令和8年度HPCI資源台帳では、課題募集上の提供期間と装置のライフサイクルを引き続き
区別します。不老・弐とSiriusに加え、SQUIDの3ノード群とHOKUSAI BigWaterfall2から、
既存の公開ロードマップにある運用終了・更新根拠へ直接接続しました。27システムの
うち20システムは、機関が確認したライフサイクルのマイルストーンへ未接続であり、
`GAP-HPCI-SYS-001`はP0の未解決課題として残します。

産総研のシステムガイドから、ABCI 3.0の766計算ノード、H200 GPU 6,128基、
ノード内メモリ、InfiniBand接続、約75 PBの共有ストレージ構成を補完しました。
部品仕様からピーク性能を算出してはいません。HPCI課題への提供量、キュー条件、
容量定義を提供機関間でそろえる作業は残っています。

### 調達根拠

理研の契約結果には、67億3,140万6千円の計算機一式とは別に、514万8千円の
AI for Science用InfiniBandスイッチ一式が税込契約額として記載されています。
理研R-CCSの公開概要からは、水冷計算ノード400台、GB200 NVL4、XDR 800 Gb/s網、
実効容量1,081.34 TBのオールNVMe Lustreストレージも記録しました。

小額のスイッチ契約を公開構成の25台のいずれかと同一視せず、計算機一式の金額から
控除せず、単価も算出しません。最終仕様、数量、契約間の重複、機器別価格、設置・
保守の範囲は、`PCG-001`から`PCG-003`の未確認事項として残します。

### GENESIS校正候補

2021年のGENESIS論文には、1 ÅのPME格子を用いた、富岳16ノードから
16,384ノードまでの弱スケーリング実測が掲載されています。交互に選んだ6点を
校正に使い、重複しない5点を検証用に保留して、ノード数のlog2に対する区分線形
補間を評価しました。検証点における最大相対誤差は約6.2%です。

`PMCAL-GENESIS-WEAK-001`は、検証済みモデルカードでも将来機予測でもありません。
1システム、1ワークロード、1測定系列に限られ、公表値は丸められています。
独立再測定と別アーキテクチャでの検証もないため、Consensus未完了、調達利用不可
のまま保持します。

### アプリケーション需要と計算基盤要件

EEA1の6アプリケーションを、演算スループット、メモリ容量・帯域、スケールアップ
接続、スケールアウト接続、ストレージ・I/O、ワークフロー期限、ソフトウェア可搬性、
データ管理の8軸で比較します。各セルには、定性的な要求水準、根拠に基づく理由、
追加で必要な測定または確認を記録しました。

この表は整備計画を検討するための索引であり、部品表ではありません。要求水準は
ノード数、帯域要件、調達仕様を示さず、合算した点数にもできません。定量要件の
策定には、入力の固定、測定、アプリケーション責任者の確認、独立Consensusが必要です。
