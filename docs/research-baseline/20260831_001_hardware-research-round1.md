# Hardware Research Update, 2026-08-31

## English

### Scope and Status

This update covers all 20 existing research units in seven hardware catalogs,
including the six previously unstarted units. It adds an initial evidence-backed
comparison, not a claim of complete research. Every unit remains `partial` and
the public conclusions remain provisional, with Consensus `incomplete`.

The work was authorized by the user's interactive request, transcribed in
[DIR-900018](../../reviews/directives/DIR-900018.json), against base commit
`60691c3ae26e993ca57d6bb020b1571706ac7b65`. The publication authorization covers
reviewable public data, not approval of scientific conclusions or permission to
merge, deploy production, or enable unattended agents.

### Coverage

The public catalog code and canonical research-unit ID are deliberately distinct.
Descriptions, sources and adoption conditions live in
[topic-decision-support.json](../../knowledge/public/topic-decision-support.json);
this table is a work record, not a second source of technical conclusions.

| Public catalog | Canonical unit | Investigation added |
|---|---|---|
| ARCH-001 | ARCH-01-U01 | CPU/GPU/vector choices; instruction support and precision-specific peaks |
| ARCH-001 | ARCH-01-U02 | DDR/NUMA, discrete versus coherent CPU-GPU memory, shared-HBM capacity/contention |
| ARCH-001 | ARCH-01-U03 | Agent latency versus concurrent throughput, core allocation, frequency/power evidence |
| ARCH-002 | ARCH-02-U01 | TSMC, Intel, Samsung and Rapidus process availability versus product qualification |
| ARCH-002 | ARCH-02-U02 | UCIe, die-to-wafer/wafer-to-wafer bonding, package scaling and yield boundaries |
| ARCH-003 | ARCH-03-U01 | DDR/MRDIMM, LPDDR, HBM generations and manufacturing-stage supply dependencies |
| ARCH-003 | ARCH-03-U02 | SOCAMM2, NVHBM, zHBM and ZAM as distinct module/integration approaches |
| ARCH-003 | ARCH-03-U03 | Bandwidth/latency/capacity, page placement, CXL tiers and near-memory compute |
| ARCH-004 | ARCH-04-U01 | PCIe, CXL, NVLink and UALink semantics, versions and qualification |
| ARCH-004 | ARCH-04-U02 | RoCE, Ultra Ethernet, Cornelis and InfiniBand topology/congestion/driver conditions |
| ARCH-004 | ARCH-04-U03 | CPO power boundaries, replacement scope and PEC-2/PEC-3 delivery stages |
| ARCH-009 | ARCH-12-U01 | Cerebras, MN-Core, SambaNova, Versal and Jalapeno execution/supply scope |
| ARCH-009 | ARCH-12-U02 | PIM host costs, measured versus simulated mechanisms and CXL attachment |
| ARCH-009 | ARCH-12-U03 | SDK/access paths, supported versions and limitations of performance comparisons |
| ARCH-012 | SSW-05-U01 | SSD/HDD/tape endurance, supply, measurement conditions and media compatibility |
| ARCH-012 | SSW-05-U02 | NVMe transports, multipathing, redundancy and correlated failure domains |
| ARCH-012 | SSW-05-U03 | EXAScaler, Infinia, VAST and DAOS API/release/serving boundaries |
| ARCH-012 | SSW-05-U04 | Tier placement, Globus gateways, S3 atomicity and checkpoint recovery |
| ARCH-005 | ARCH-05-U01 | RIKEN AI for Science, JUPITER, LUMI and Helios configuration accounting |
| ARCH-005 | ARCH-05-U02 | Cooling, disaggregated inference, procurement boundaries and conflicting specifications |

Initial updates [RUP-000019](../../proposals/research-unit-updates/RUP-000019.json)
through [RUP-000025](../../proposals/research-unit-updates/RUP-000025.json) add 78
technical items. Optional follow-ups RUP-000026 through RUP-000030 add nine items
covering HBF, Thor Ultra, Croc/HyperCroc, ETHEREAL, MX1 and Rubin delivery stages.
RUP-000031/32 correct wording by superseding six items, retaining the originals;
they do not count as additional investigations. The resulting update contains
87 current technical items and source-check records for 103 distinct exact URLs.
Repeated checks and different reports of one experiment are not independent votes.

### Roadmaps and Interpretation

- Four hardware roadmaps gain 22 dated/undated milestones and five corrections
  to existing milestones. Manufacturing plans, samples, volume production,
  customer shipment and institutional service start remain distinct.
- Fiscal-year targets now use `quarter-range` windows, including FY2026 as
  2026 Q2 through 2027 Q1. These are uncertainty windows, not event durations.
  Year-only and half-year evidence is not narrowed to an invented quarter.
- HBF and ZAM definitions/comparison rows use the central
  [reference dataset](../../knowledge/public/roadmap-reference-data.json).
  HBF is not treated as interchangeable with HBM, and ZAM is not zHBM.
- [Cross-roadmap dependencies](../../knowledge/public/dependencies/p0-roadmap-dependencies.json)
  connect supply/qualification, network interoperability/serviceability and
  storage recovery to node choices. Fallbacks are evaluation options, not
  validated performance or procurement recommendations.
- The Micron DDR/3D-DRAM attribution, the Micron March 16 publication date, and
  NTT's fiscal-year commercialization versus calendar-year sample targets are
  corrected. Previous roadmap versions remain in Git history; old catalog
  evidence remains in archived sections and immutable update bundles.

### Optional Research and Remaining Gaps

The follow-up checked performance denominators and software/access routes,
traced prior targets against subsequent announcements, and reviewed additional
Hot Chips-related primary material. The conference register now has 30 entries
with related primary evidence and 18 with program information only. None is
classified as a complete review of conference presentation materials.

Material caveats include simulated versus physical Cerebras results, off-chip
work in ETHEREAL, vendor-provided Jalapeno measurements, differing GPU identities
in one CPU-agent energy study, SSD bandwidth/latency queue-depth differences,
and unresolved aggregation/version differences in public system specifications.
These prevent unqualified speedup, energy or node-cost extrapolation.

[GAP-TDS-054 through GAP-TDS-060](../../knowledge/public/topic-decision-support.json)
remain open, alongside existing gaps. Missing items include qualified product
dates, matched hardware/software measurements, independent replication,
production yield, academic supply/support and comparable contract boundaries.
No component prices, discounts, achieved application FLOP/s or future system
speedups are inferred from unmatched evidence.

### Verification Boundaries

Research used managed public Web access. Restricted or failed retrievals were
not bypassed with shell commands, alternate browsers or authenticated access.
Examples include JEDEC text, CN6000, an oversized NVIDIA PDF, a redirected UCIe
white paper, MX1's current product page and some SDK/readme locations. Readable
overviews and historical material support only the narrower claims recorded in
the source checks; they do not substitute for unavailable normative documents.

Source-audit regeneration uses `--offline-reconcile`: existing HTTP observation
dates/counts are retained and new URLs remain unaudited by that network checker.
Managed-Web content review is recorded separately and is not independent
verification. No hardware benchmarks, SDK programs or production research agents
were executed. Browser pixel/layout inspection is not claimed; offline DOM
checks cover bilingual rendering, event links, exact quarter spans and collisions.

## 日本語

### 対象と状態

ハードウェア7カタログの既存20小項目を対象に、未着手だった6項目を含めて、
根拠に基づく初回の比較整理を追加しました。網羅的な調査完了を意味するものではなく、
全小項目を「一部完了」、調査結果を暫定、Consensusを未完了のまま維持しています。

ユーザーからの対話による依頼をDIR-900018に記録し、上記のbase commitを起点に
作業しました。これは公開データをレビュー可能な変更として準備する承認であり、
科学的結論の承認、マージ、本番公開、無人エージェントの有効化を認めるものではありません。

### 小項目別の内容

公開カタログ番号と内部の小項目IDは別の識別子です。技術説明・出典・採用条件の
正本は上記の構造化データに置き、この表は作業記録とします。

| 公開カタログ | 内部の小項目ID | 追加した調査内容 |
|---|---|---|
| ARCH-001 | ARCH-01-U01 | CPU・GPU・ベクトル機、命令対応、精度別ピーク性能の違い |
| ARCH-001 | ARCH-01-U02 | DDR・NUMA、CPU/GPU間のメモリ整合性、共有HBMの容量・帯域競合 |
| ARCH-001 | ARCH-01-U03 | エージェントの応答時間と同時処理量、コア割当、周波数・電力の根拠 |
| ARCH-002 | ARCH-02-U01 | TSMC・Intel・Samsung・Rapidusの製造段階と製品認定の違い |
| ARCH-002 | ARCH-02-U02 | UCIe、D2W/W2W接合、パッケージ大型化、歩留まりの評価範囲 |
| ARCH-003 | ARCH-03-U01 | DDR/MRDIMM・LPDDR・HBMの世代と製造工程別の供給条件 |
| ARCH-003 | ARCH-03-U02 | SOCAMM2・NVHBM・zHBM・ZAMのモジュール／実装方式の違い |
| ARCH-003 | ARCH-03-U03 | 帯域・遅延・容量、ページ配置、CXL階層、メモリ近傍演算 |
| ARCH-004 | ARCH-04-U01 | PCIe・CXL・NVLink・UALinkの機能、版、認定条件 |
| ARCH-004 | ARCH-04-U02 | RoCE・Ultra Ethernet・Cornelis・InfiniBandの構成、輻輳、ドライバ |
| ARCH-004 | ARCH-04-U03 | CPOの電力測定範囲、交換単位、PEC-2/PEC-3の提供段階 |
| ARCH-009 | ARCH-12-U01 | Cerebras・MN-Core・SambaNova・Versal・Jalapenoの実行・供給条件 |
| ARCH-009 | ARCH-12-U02 | PIMのホスト処理、実測とシミュレーションの区別、CXL接続 |
| ARCH-009 | ARCH-12-U03 | SDK・実機へのアクセス、対応版、性能比較の制約 |
| ARCH-012 | SSW-05-U01 | SSD・HDD・テープの耐久性、供給、測定条件、媒体互換性 |
| ARCH-012 | SSW-05-U02 | NVMeの通信方式、マルチパス、冗長化、共通原因故障 |
| ARCH-012 | SSW-05-U03 | EXAScaler・Infinia・VAST・DAOSのAPI、提供版、推論処理との分担 |
| ARCH-012 | SSW-05-U04 | 階層配置、Globus、S3の更新単位、チェックポイント復旧 |
| ARCH-005 | ARCH-05-U01 | 理研AI for Science・JUPITER・LUMI・Heliosの構成と集計単位 |
| ARCH-005 | ARCH-05-U02 | 冷却、推論処理の分離、調達費用の範囲、仕様記載の不整合 |

RUP-000019〜025で78件の技術説明を追加し、RUP-000026〜030ではHBF、Thor Ultra、
Croc/HyperCroc、ETHEREAL、MX1、Rubinの提供段階について9件を追加しました。
RUP-000031/32は6件の文章を旧版を残して訂正するもので、新しい調査件数には含めません。
今回の現行説明は合計87件、参照内容と制約を記録したURLは重複を除いて103件です。
同じ資料の再確認や同一実験に由来する複数記事は、独立した合意の票にはなりません。

### ロードマップと判断上の注意

- ハードウェアの4ロードマップに22件の日程・時期未公表の項目を追加し、既存5項目を
  修正しました。製造計画、サンプル、量産、顧客出荷、各機関での供用開始は区別しています。
- 年度の目標を複数四半期の範囲で表示できるようにしました。例えば2026年度は
  2026年Q2〜2027年Q1です。矩形は時期の不確実性を示し、事象の継続期間ではありません。
  年・半期だけが公表された場合も、特定の四半期へ狭めていません。
- HBF・ZAMの説明と比較表は共通用語集に追加しました。HBFをHBMと同一視せず、
  ZAMとzHBMも区別します。
- 供給・認定、通信の相互運用・保守、ストレージ復旧をノード選択へ結び付け、
  遅延時に比較すべき代替構成を依存関係一覧に追記しました。代替案の性能が検証済み、
  または調達上の推奨であるとは扱いません。
- MicronのDDR・3D DRAM項目の帰属、3月16日の資料公開日、NTTの年度別商用化と
  暦年で示されたサンプル提供目標を訂正しました。旧ロードマップはGit履歴、
  カタログの旧根拠はアーカイブされた節と変更不能の更新記録に保持します。

### 追加調査と残件

性能比較の分母とソフトウェア・実機利用経路を確認し、過去の目標とその後の発表を
照合しました。Hot Chips関連の一次資料も追加で確認し、会議台帳は関連一次情報あり30件、
プログラム情報のみ18件となりました。講演資料を全文確認した扱いの項目はありません。

注意点として、Cerebrasの実機とシミュレーション、ETHEREALのチップ外処理、
Jalapenoの開発元による測定、CPUエージェント研究のGPU機種表記の不一致、
SSDの帯域と遅延で異なるキュー深度、公開システム仕様の集計・版の違いを明記しました。
これらを無条件の高速化率、消費電力量、ノード単価へ外挿しません。

GAP-TDS-054〜060と既存の未確認事項は未解決のままです。認定済み製品の提供時期、
同条件の実機・ソフトウェア測定、独立追試、量産歩留まり、学術向け供給・保守、
比較可能な契約範囲などが残ります。比較条件が一致しない資料から、部品価格、割引率、
アプリケーションの達成FLOP/s、将来システムの高速化率を推定していません。

### 検証の範囲

調査には管理されたWebアクセスを使い、取得制限をシェル、別ブラウザ、認証付きアクセスで
迂回していません。JEDEC本文、CN6000、大容量NVIDIA PDF、リダイレクトされたUCIe白書、
MX1の現行製品ページ、一部SDK/READMEなどは取得できませんでした。読めた概要・過去資料は
記録した範囲の根拠に限り、取得できない規格本文などの代わりにはしていません。

URL監査はオフラインで対応付けを再生成し、過去のHTTP確認日時・回数を保持しました。
新しいURLはそのネットワーク監査では未確認です。管理Webによる本文確認は別に記録し、
独立検証と区別しています。実機ベンチマーク、SDKプログラム、本番の調査エージェントは
実行していません。ブラウザの描画・ピクセル検査も実施済みとは扱わず、オフラインの
DOMテストで日英表示、項目リンク、四半期幅、重なる期間の配置を検証します。
