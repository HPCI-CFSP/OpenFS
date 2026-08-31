# September 1 Cross-Domain Research

## English

This is an interactive, human-authorized, single-agent/single-model research
continuation under `DIR-900019`, based on commit
`c87edcce5d1203587f5ef484c3c5669fd085565a`.
Its research window ends around September 1, 2026 at 06:30 JST.
It does not authorize a production merge, independent Consensus, hardware
experiments, credentials, restricted material, or a new unattended agent.

The first pass covers 53 existing units in 33 catalogs: 15 system-software,
18 application, 13 operations/procurement, two governance and five cross-cutting
units. `RUP-000033` through `RUP-000065` retain source observations and provisional
results; later RUPs add follow-up evidence or corrections without rewriting an
applied bundle. A first pass is not a completed survey or verification.

### Derived View Revisions

The software and numerical-method matrices in
`knowledge/public/topic-decision-support.json` supersede their views at the base
commit. Their source records remain intact, and the revision is reviewable in
Git. Vendor-specific collective and math-library cells are split by deployment
target; generic portable implementations can still cover multiple targets.
The former `SWC-NCCL-RCCL` becomes `SWC-NCCL` and `SWC-RCCL`;
`SWC-CPU-MATH-EXT` becomes four vendor-specific entries;
`SWC-OPENMPI` becomes CPU and conditional GPU-aware paths;
`SWC-AMD-PROF` becomes separate uProf and ROCm-profiler entries.
Numerical implementations with combined vendor lists use target-specific child
IDs. These are presentation IDs, not new research topics or Consensus decisions.

Compiler, runtime and numerical evidence comes from the original source records
and `RUP-000033`, `RUP-000035`, `RUP-000077` through `RUP-000080`.
Suite, component and independently distributed versions are not interchangeable.
Documented support is not proof of testing by OpenFS. The parent artifact remains
provisional and Consensus incomplete. Compatibility, numerical correctness,
performance, application representativeness and operational integration remain
separate questions.

The new `GAP-BLUE-009` is propagated to the portability-to-blueprint dependency
and the center-profile evidence contract shared by all three candidate plans.
No ranking, procurement choice, budget, quantity or adoption authorization is
changed. Fiscal-year windows preserve the source's uncertainty and do not denote
event duration.

The shared glossary now includes Terminal-Bench and Terminal-Bench-Science in
the benchmark, evaluation-control and research-priority comparisons. The six-row
EEA1 reproducibility table uses `RUP-000081` and its associated roadmap sources to
distinguish algorithm, precision, timed stage, deployment recipe and current
retrieval limits. It does not turn published measurements into OpenFS forecasts.

Follow-up evidence distinguishes vLLM's upstream release from AMD's documented
qualification version, EESSI's aspirational goals from feature delivery, and
EPICURE's funding endpoint from an assured service lifetime. DeePMD v3.2.0 tagged
documentation clarifies backend/model-format contracts that differ from the
retrieved rendered manual. SQUID's application-tuning ratios are comparisons
against previous software modules, not new-GPU forecasts or energy measurements.

Japanese data-continuity examples add AOBA-S S3 synchronization and retention
conditions, the historical AOBA-C cutoff, and the October 2026 RED-ONION trial
plan. A trial endpoint is not an asserted data-deletion date. RED-ONION does not
establish procurement of a successor compute system for SQUID/ONION.

Further follow-ups (`RUP-000092` through `RUP-000104`) cover adopted policy versus
working-group proposals, the scope of a NEDO software/testbed study, MindSpore and
Bisheng version boundaries, QUBO++ solver/licensing conditions, and experimental
facility workflows at SPring-8, European XFEL, ESRF and SSRF. The NEDO study ceiling
is not a computer-procurement budget. Policy fiscal-year windows are not confirmed
service dates. Japanese wording revisions retain the English claims and source
receipts; they do not establish new performance measurements.

`RUP-000105` through `RUP-000113` distinguish AIPerf goodput from attainment
fractions and pre-send skips, GH200 module power budgets from whole-node energy,
and JUPITER transition notices from confirmed migration. Further evidence covers
India's ParaS/CLAP/Torch-ParaS projects, NCI research-cloud boundaries, procurement
workload comparisons, Open MPI API-specific GPU support and the proposed GPU-aware
OpenSHMEM extension. A July 2026 paper publication is recorded as research, not
standards ratification or vendor delivery. Public repositories alone do not
establish deployed service, conformance or performance.

`RUP-000114` through `RUP-000120` add ReFrame/JUBE measurement controls,
NERSC reservation and real-time access boundaries, HOKUSAI access-route tariffs,
HPC agent/MCP interfaces, and Nagoya's software-license/account transition.
The HOKUSAI public fee example remains internally inconsistent; an internal
RIKEN tariff is not substituted to repair it. Local MCP execution does not mean
local model inference, and a client wait timeout does not cancel the remote job.
Planned center briefings and October service dates do not prove completed access
migration, continuing licenses or automatic account transfer.

A later SALMON retrieval finds 2.3.0 download links and a readable manual where
an earlier retrieval showed 2.2.2. Both observations are retained. The new
summary distinguishes SALMON2 from the legacy repository, documents restricted
r2SCAN/OpenACC support, and flags ground-state-density changes in restart files.
The tarball was not downloaded, no code was executed, and artifact/tag/EEA1
correspondence remains unverified. The shared glossary, comparison and code links
are synchronized without changing any performance-model coefficients.

`RUP-000121` adds a NICAM/Kokkos porting case and portability-measurement
conditions. Its GPU ratios use one A64FX CMG with 12 cores, not a Fugaku node
or the whole application. CPU regressions, timing exclusions, unavailable code
retrieval and unperformed reproduction remain visible. Portability metrics need
fixed platform cohorts and reference runtimes; unmeasured does not mean failed.
A research-page update date is not a new benchmark measurement date.
`RUP-000122` only aligns the Japanese summary with the terminology policy,
preserving its predecessor and all measurement claims; it is not new research.

Search now indexes sources cited by active catalog claims and software matrices,
not just roadmap sources. Identical URLs retain all source IDs and classifications
without duplicate result cards. Archived-only, retired-topic-only and unreferenced
catalog metadata do not enter this source index. Corrections take display-title
precedence for matching URLs. Offline DOM tests cover both languages, filters,
links and correction handling; these are not browser-layout tests. Topic search
also excludes archived claim text and provenance-only history, while category
membership tables no longer cause unrelated topics or roadmaps to match a code.

The existing EEA1 table retains all 36 numerical results, equations and numeric
assumptions unchanged. Its Japanese and English prose and cell labels now say
explicitly that these are uncalibrated what-if calculations. GENESIS's 0.75 and
the scale-retention coefficients are not measured fractions; the chosen 0.5-1.5
range is not a confidence interval or a bound on actual performance. The sources
inform workload characteristics but do not calibrate these inputs. Procurement
use remains prohibited. Separating legacy illustrations from formal forecast
records under the stricter contract remains a follow-up, not a completed fix.

### Source Metadata Corrections

`RUP-000096` appends `SRC-CDA101` through `SRC-CDA104` as corrections to catalog
sources `SRC-WORK020`, `SRC-WORK025`, `SRC-WORK026` and `SRC-WORK027`. Explicit arXiv
versions clarify titles and dates, but their inspected metadata does not establish
peer-reviewed publication. The replacement records use `research-artifact`, not
a claim that peer review never occurred. Original metadata and archived claims
remain unchanged. The separately maintained roadmap class `academic-primary`
does not itself claim peer review.

The source schema now permits a bilingual `correction` with `supersedes_source_id`.
Validation rejects missing predecessors, self-reference, cycles, branching
corrections and blank reasons. A new research update must use the replacement
record and cannot leave the superseded metadata in active claims, actors or
comparison matrices. Historical records remain usable for auditing. This is
metadata lineage, not a Consensus or scientific-validity decision.

### Known Limits

- Public documentation does not establish actual center installation or service.
- Source retrieval and schema checks do not count as independent Consensus.
- Prices from unmatched procurement packages are not component unit prices.
- Public GENESIS evidence does not calibrate the older illustrative EEA1
  what-if values. Their presentation is clarified without changing numbers;
  their compatibility with the stricter forecast contract still needs review.
- Failed or restricted retrievals are not evidence that a technology is absent.
- Offline source-audit reconciliation preserves prior HTTP observations and does
  not claim a new network reachability check.
- The disabled legacy whole-profile generator mapped `academic-primary` to
  `peer-reviewed` and inserted a fixed access date for undated sources. Its import
  helper now uses neutral `research-artifact` classification and an explicit
  unknown date. The four identified catalog records are corrected through new
  versions above, not in-place edits. Broader historical metadata review remains
  necessary; this change does not certify every previous record.

## 日本語

本作業は、`DIR-900019`に基づき、人間の明示的な依頼を受けて単一のAIエージェント・
単一のAIモデルが実施する調査の継続です。基準コミットは
`c87edcce5d1203587f5ef484c3c5669fd085565a`、作業期限は2026年9月1日06:30 JST頃です。
本番へのマージ、独立Consensus、実機実験、認証情報・制限資料の利用、
新しい無人エージェントの起動を承認するものではありません。

一次調査の対象は既存33カタログの53小項目で、システムソフトウェア15、
アプリケーション18、運用技術・調達13、利用制度・運営制度2、分野横断5です。
`RUP-000033`から`RUP-000065`に情報源の確認記録と暫定結果を保存し、
後続RUPでは適用済みの記録を書き換えず、追加の根拠や訂正を記録しています。
一次調査の実施は、網羅的な調査や検証の完了を意味しません。

### 派生表示の改訂

`knowledge/public/topic-decision-support.json`のソフトウェア対応表と数値計算手法の
比較表を、基準コミットの表示から改訂しました。情報源の記録は保持し、差分はGitで
確認できます。ベンダー固有の集合通信・数値計算ライブラリは対象機種別に分け、
可搬性のある共通実装は引き続き複数機種を対象にできます。
旧`SWC-NCCL-RCCL`を`SWC-NCCL`と`SWC-RCCL`へ、`SWC-CPU-MATH-EXT`を
4社別の項目へ、`SWC-OPENMPI`をCPU向けと条件付きGPU-aware経路へ、
`SWC-AMD-PROF`をuProfとROCmの解析ツールへ分割しました。
数値計算の複数ベンダーをまとめた実装項目も、対象機種別の子IDへ分割しています。
これらは表示用IDであり、新しい調査カタログやConsensus決定ではありません。

コンパイラ・実行時環境・数値計算の根拠は、従来の情報源と`RUP-000033`、
`RUP-000035`、`RUP-000077`から`RUP-000080`にあります。SDK全体、構成要素、
単独配布物の版を同一視せず、文書上の対応をOpenFSでの実機検証とは扱いません。
成果物は暫定・Consensus未完了のままです。互換性、数値的正しさ、性能、
アプリケーションの代表性、運用への組込みは、それぞれ別に検証する必要があります。

新しい`GAP-BLUE-009`は、可搬性ロードマップからシステム構成への依存関係と、
3つの計画候補が共有するセンタープロファイルの根拠要件へ反映しました。
順位、調達先、予算、台数、採用承認は変更していません。年度の期間は情報源に残る
時期の不確定さを表し、事象の継続期間を意味しません。

共通用語集ではTerminal-BenchとTerminal-Bench-Scienceを、評価対象、検証条件、
調査優先度の3つの比較表から参照できるようにしました。6本のEEA1の再現性比較表は
`RUP-000081`と対応するロードマップ情報源を用い、手法、精度、計測区間、導入手順、
今回の取得制約を区別しています。公表された測定値をOpenFSの予測値へ転用した
ものではありません。

追加調査では、vLLMの公開版とAMD文書上の検証対象版、EESSIの努力目標と機能提供、
EPICUREの事業終期とサービス継続保証を区別しました。DeePMDはv3.2.0のタグ付き
資料を照合し、取得した公開マニュアルと異なるバックエンド・モデル形式の条件を
整理しています。SQUIDのアプリ改善率は旧モジュールとの比較であり、新GPUの予測や
消費電力量の測定ではありません。

国内のデータ継続性については、AOBA-S S3の同期・保存条件、過去のAOBA-C終了条件、
2026年10月予定のRED-ONION試験運用を追記しました。試験期間の終端をデータ削除日と
断定せず、RED-ONIONをSQUID・ONIONの後継計算機の調達決定とも解釈していません。

`RUP-000092`から`RUP-000104`では、策定済み政策とWG設置案の違い、NEDOの
ソフトウェア・テストベッド調査の対象、MindSpore・Bishengの版ごとの条件、
QUBO++のソルバー・ライセンス条件、SPring-8・European XFEL・ESRF・SSRFの
実験連携を追加確認しました。NEDOの調査費上限は計算機の調達予算ではなく、
政策の年度目標も提供開始日ではありません。日本語の表現修正では英語の主張と
情報源の確認記録を維持しており、新しい性能測定を行ったものではありません。

`RUP-000105`から`RUP-000113`では、AIPerfのgoodputと達成割合・送信前の省略、
GH200モジュールの電力枠とノード全体の消費電力量、JUPITERの移行告知と移行完了を
区別しました。インドのParaS・CLAP・Torch-ParaS、NCIの研究クラウド、調達時の
ワークロード比較、Open MPIのAPI別GPU対応、GPU向けOpenSHMEMの仕様提案も
追加調査しています。2026年7月の論文公開は研究発表として記録し、規格の採択や
製品提供とは扱いません。リポジトリの公開だけでサービス運用、適合性、性能を
確認したとは判断していません。

`RUP-000114`から`RUP-000120`では、ReFrame/JUBEの計測条件、NERSCの予約と
リアルタイム利用条件、HOKUSAIの利用経路別料金、HPCエージェント・MCPの境界、
名古屋大学のライセンス・アカウント移行を追加調査しました。HOKUSAIの公開料金例に
残る計算上の不整合は、理研内部向け料金を代入して修正していません。MCPをローカルで
実行してもモデルの推論がローカルとは限らず、待機のタイムアウトも遠隔ジョブの取消し
ではありません。説明会や10月のサービス予定は、移行完了、ライセンス継続、
アカウントの自動引継ぎを確認した根拠とはしません。

SALMONの再取得では、先に2.2.2と表示された配布ページに2.3.0へのリンクと
閲覧可能なマニュアルを確認しました。両時点の取得記録を保持しています。
新しい整理ではSALMON2と旧リポジトリを区別し、r2SCANとOpenACCの併用制約、
再開ファイルの基底状態密度の扱いを明記しました。tarballの取得やコード実行は
しておらず、配布物・タグ・EEA1評価版の対応は未検証です。用語集、比較表、
コードへのリンクを揃えましたが、性能モデルの係数は変更していません。

`RUP-000121`ではNICAMのKokkos移植事例と性能可搬性の測定条件を追加しました。
GPUの比較基準はA64FXの1 CMG・12コアであり、富岳1ノードや全アプリではありません。
CPU側の性能低下、測定からの除外区間、コード取得失敗、再現実行の未実施を明記します。
可搬性指標は対象機種と基準時間を固定する必要があり、未測定を失敗とは扱いません。
研究紹介ページの更新日も、新しいベンチマークの測定日とは区別します。
`RUP-000122`は日本語要約の用語訂正だけを行い、原記録と測定に関する記述を
保持しています。新しい調査としては数えません。

検索にはロードマップの資料に加え、公開中のカタログの主張とソフトウェア比較表が
引用する資料を含めました。同じURLの結果はまとめ、すべての情報源IDと分類を保持します。
アーカイブ済みの主張だけが使う資料、廃止項目だけの資料、未参照のメタデータは
カタログ資料の検索索引に入れません。URLが一致する場合は訂正後の題名を優先します。
日英、フィルター、リンク、訂正の扱いをオフラインDOMテストで確認する構成であり、
ブラウザーでのレイアウト検証とは区別します。調査項目の検索でも過去版の文章や
来歴だけの記録は除外し、カテゴリの所属表に含まれるIDが無関係なカタログや
ロードマップに一致する問題を修正しました。

既存EEA1表の36件の数値、計算式、数値の仮定は変更せず、日英の説明とセルの表示を
「未校正のwhat-if試算」と明確化しました。GENESISの0.75や規模別の保持係数は
実測した割合ではなく、便宜的な0.5〜1.5倍の範囲も信頼区間や実際の性能の上下限では
ありません。情報源は計算特性の参考資料であり、これらの入力値を校正するものでは
ありません。調達への使用禁止は維持します。厳格化された要件に沿って既存の例示と
正式な予測データを分離する作業は、解決済みとはせず今後の課題として残します。

### 情報源メタデータの訂正

`RUP-000096`は、カタログ情報源`SRC-WORK020`、`SRC-WORK025`、`SRC-WORK026`、
`SRC-WORK027`の訂正として、`SRC-CDA101`から`SRC-CDA104`を追加します。
arXivの版を指定して題名・日付を確認しましたが、確認したメタデータだけでは
査読済み出版を確認できません。後継記録は`research-artifact`に分類しますが、
査読が一度も行われていないと断定するものではありません。元のメタデータと
アーカイブ済みの主張は保持します。別管理のロードマップで用いる
`academic-primary`も、それ自体で査読済みを意味する分類ではありません。

情報源のスキーマに、訂正理由を日英で記した`correction`と
`supersedes_source_id`を追加しました。存在しない前版、自己参照、循環、訂正の
分岐、空の理由を検証で拒否します。新しい調査結果は後継記録を使う必要があり、
公開中の主張・組織情報・比較表に古いメタデータを残したまま訂正を適用することも
拒否します。過去の記録は監査のため保持します。これは書誌情報の来歴管理であり、
Consensusや研究内容の正しさを決定するものではありません。

### 残る制約

- 公開文書だけで、センターでの導入・サービス開始を確認したとは扱いません。
- 情報源の取得やスキーマ検証を、独立Consensusとは扱いません。
- 対象範囲が一致しない一括調達の価格から、部品単価を求めません。
- GENESISの公開根拠は、既存のEEA1の例示的なwhat-if値の校正にはなりません。
  数値を変更せず表示を明確化しましたが、厳格化された予測要件との整合は別途確認が
  必要です。
- 取得できない資料やアクセス制限は、技術が存在しない根拠にはなりません。
- 情報源監査のオフライン再整合は過去のHTTP確認結果を保持する処理であり、
  新しいネットワーク接続確認ではありません。
- 無効化済みの旧プロファイル生成処理には、`academic-primary`を`peer-reviewed`へ
  自動変換し、日付不明の資料に固定のアクセス日を付ける問題がありました。
  変換関数は中立的な`research-artifact`と日付不明の表示に修正しました。
  判明した4件は上記の新しい版で訂正し、元の記録は変更していません。
  過去のメタデータ全体の確認は引き続き必要であり、今回の変更だけで全記録の
  正しさを保証するものではありません。
