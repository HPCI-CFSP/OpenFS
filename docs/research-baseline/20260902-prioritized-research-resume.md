# September 2 Prioritized Research Resume

## English

This continuation is human-authorized under `DIR-900021` and uses public
information only. Results are provisional work by one AI agent and one model;
independent Consensus remains incomplete. No result in this batch authorizes a
procurement decision, production merge, or Pages deployment.

### New Evidence Added Near the Checkpoint

`RUP-000355` through `RUP-000364` add public evidence on Japanese system costs,
service components and policy. They keep package scope intact rather than
deriving unsupported component prices. The additions include RIKEN's staged
AI-for-Science storage and GPU procurements, Fugaku annual maintenance and major
overhaul contracts, FugakuNEXT design work packages, performance-model and
communication-analysis services, facility energy and operations contracts,
shared-storage service components, the revised Fugaku strategic allocation
framework, an explicitly assumption-sensitive 2030 AI-for-Science stress case,
and package values for the systems corresponding to RIKYU and ROQUO.

`RUP-000365` adds a cross-domain demand distinction. Life-science foundation
models emphasize long sequences and multimodal biological data; materials
workflows combine equivariant graph models with simulation, active learning and
experiments; weather and environmental workflows combine multivariate grids or
graphs, ensembles, physical models and deadline-bound dissemination. Accelerator
counts alone cannot compare these demands. Model-specific figures reproduced in
the commissioned study remain pending reconciliation with original papers,
repositories and datasets.

`RUP-000366` adds an operational reference case from ECMWF. AIFS Single entered
operations in February 2025 and the 51-member AIFS ENS in July 2025; both moved to
version 2 in May 2026. Official material describes four runs per day, six-hourly
steps to 15 days and about 6 TB/day from Single and ENS together. The lower-
resolution AI ensemble operates alongside the physics-based IFS, so fast model
inference is not treated as a replacement for data assimilation, high-resolution
and coupled modelling, archives, dissemination, or fallback.

### Resume Priorities

1. Reconcile the life-science, materials and weather model records against each
   original paper, official repository, dataset, licence and measured setup.
2. Obtain final specifications and support scopes before comparing Japanese
   procurement packages or calculating any unit price.
3. Measure representative domain workflows end to end, including memory, I/O,
   communication, queue delay, checkpointing, data governance and deadlines.
4. Preserve every result as provisional and Consensus-incomplete until
   independent agents or models perform source-blind assessments.

### Checkpoint Validation

The immutable-update audit completed with zero errors through `RUP-000366`.
JSON Schema validation passed for 2,394 artifacts, repository validation passed,
and Pages built 40 topics, seven roadmaps and three scenarios. Fifteen focused
offline catalog and roadmap DOM tests passed after replacing a stale fixed
hardware-item count with a comparison against the canonical non-archived count.
The full Python suite was not started because its latest measured runtime would
extend substantially beyond the requested 07:30 JST checkpoint; it remains the
first validation step on resume.

## 日本語

本作業は`DIR-900021`に基づく人間の明示的な承認の下、公開情報だけを用いて
継続した調査です。単一のAIエージェントと単一のモデルによる暫定結果であり、
独立Consensusは未完了です。今回の結果は、調達判断、本番へのマージ、Pagesへの
公開を承認するものではありません。

### チェックポイント直前に追加した新規根拠

`RUP-000355`から`RUP-000364`では、国内システムの費用、サービス構成、制度に
関する公開根拠を追加しました。一括契約の範囲を保持し、根拠のない部品単価へ
分解していません。理研のAI for Science向けストレージ・GPUの段階的調達、富岳の
年次保守と大型更新、富岳NEXTの設計業務、性能モデル・通信解析役務、施設の
エネルギー・運転契約、共用ストレージのサービス構成、富岳の戦略枠変更、仮定に
敏感な2030年AI for Science需要のストレスケース、理究・ROQUOに対応するシステムの
一括契約額を含みます。

`RUP-000365`では、科学分野による需要の違いを追加しました。生命科学の基盤モデルは
長い配列と複数種類の生物データ、材料系は等変グラフモデルとシミュレーション・
能動学習・実験の反復、気象・環境系は多変量の格子・グラフ、アンサンブル、物理モデル、
期限付きの配信を重視します。アクセラレータの台数だけでは需要を比較できません。
委託調査に掲載された個別モデルの数値は、原論文、公式リポジトリ、データセットとの
照合前であり、確定値として扱いません。

`RUP-000366`では、ECMWFの運用事例を追加しました。AIFS Singleは2025年2月、
51メンバーのAIFS ENSは同年7月に運用を開始し、2026年5月に双方がv2へ更新されました。
公式資料では、1日4回、6時間刻みで15日先まで予報し、SingleとENSで約6 TB/日の
データを生成します。低解像度のAIアンサンブルは物理ベースのIFSと並行運用されるため、
高速な推論を、データ同化、高解像度・結合モデル、保存、配信、障害時の代替手段の
置換とは扱いません。

### 再開時の優先事項

1. 生命科学、材料、気象の各モデルを、原論文、公式リポジトリ、データセット、
   ライセンス、測定条件と照合する。
2. 国内の一括調達を比較し、単価を計算する前に、最終仕様書と保守範囲を取得する。
3. メモリ、I/O、通信、待ち時間、チェックポイント、データ管理、期限を含む代表的な
   分野別ワークフローを、開始から終了まで測定する。
4. 独立したエージェントまたはモデルが情報源を伏せた評価を行うまで、全結果を
   暫定・Consensus未完了として維持する。

### チェックポイント時の検証

`RUP-000366`までの更新bundle監査はエラー0で完了しました。JSON Schemaは2,394件、
repository検証、40カタログ・7ロードマップ・3計画案のPages生成に成功しました。
カタログとロードマップの重点オフラインDOM試験15件も成功しました。途中で、hardware
項目数を87件に固定した古い試験が失敗したため、正本の非アーカイブ項目数と公開データを
照合する試験へ修正しています。全Python suiteは直近の実測時間では07:30 JSTを大幅に
越えるため開始しておらず、再開時の最初の検証項目です。
