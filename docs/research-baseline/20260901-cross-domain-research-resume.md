# September 1 Cross-Domain Research Resume

## English

This human-authorized continuation under `DIR-900020` resumes the saved
September 1 research-unit index. It uses public information only. Results remain
provisional work by one AI agent and one AI model; independent Consensus,
hardware reproduction, production merge and deployment are outside this update.

### Portability Evaluation

`RUP-000123` adds official SPEChpc 2021 and RAJA Performance Suite evidence to
`SSW-01-U04`. `RUP-000124` is its wording successor and preserves the same
technical claims. The resulting comparison separates three complementary layers:

1. OpenMP V&V checks compiler-feature conformance.
2. RAJAPerf compares representative kernels and implementation variants.
3. SPEChpc compares applications and mini-applications across programming models.

These layers must not be collapsed into one completion score. Suite versions,
inputs, precision, correctness criteria, compilers, dependencies, resource
boundaries and timed regions must be pinned. Public results do not establish
porting effort, source changes, long-term maintenance or retained performance for
the full HPCI application portfolio. `GAP-TDS-005` therefore remains open.

`RUP-000125` separately records the readable public NICAM-DC reference kernel
and the Kokkos implementation URL cited by the porting paper. Managed Web could
not retrieve the Kokkos repository. The public reference repository therefore
does not establish the exact code, input or build used in the reported results.

### Performance Evidence and Reference Calculations

The 36 existing EEA1 what-if records are now stored under `illustrations`, while
the formal `forecasts` collection is empty. Every numerical value, evidence
reference and former `FORECAST-*` identifier is preserved. The change prevents an
uncalibrated calculation from satisfying the formal forecast contract merely by
retaining its historical name.

Reference calculations remain low-confidence, Consensus-incomplete and ineligible
for procurement use. A formal forecast must use a declared model, separate
calibration and independent-validation datasets, at least medium confidence and
accepted Consensus. Its model card must also pass the existing deterministic
performance-model check and be registered in `validated_model_cards` with
accepted independent Consensus. The registered calibration and validation
dataset IDs must cover those used by the forecast. The list is currently empty.
Formal forecasts may be added incrementally; unlike the legacy 6-by-6
illustration grid, they are not required to fill every application and scale
before publication.

The model inputs, including the GENESIS accelerator-eligible fraction and
scale-retention coefficients, remain uncalibrated assumptions. The displayed
lower/base/upper values are an illustrative range, not a statistical confidence
interval, error bound or performance guarantee. `GAP-PERF-001` through
`GAP-PERF-005` remain open.

### Validation Boundary

The repository checker recomputes all 36 legacy cells from the declared equation
and rejects altered IDs, duplicate cells, unknown evidence, unknown assumptions
or procurement eligibility. It also rejects a formal forecast whose model card
is absent, fails deterministic validation, lacks accepted Consensus, or does not
cover the forecast's calibration and validation datasets. Schema validation
separately enforces the formal forecast contract. These checks establish
structural consistency and reproducibility of the arithmetic, not scientific
validity or independent agreement.

## 日本語

本作業は、`DIR-900020`に基づき、9月1日に保存した調査小項目インデックスから
再開したものです。公開情報のみを使用しています。単一のAIエージェントと単一の
AIモデルによる暫定結果であり、独立Consensus、実機での再現、本番へのマージ、
公開環境への反映は本更新の対象外です。

### 可搬性評価

`RUP-000123`では、`SSW-01-U04`にSPEChpc 2021とRAJA Performance Suiteの
公式情報を追加しました。`RUP-000124`は日本語表現を修正した後続記録であり、
技術的な主張は維持しています。比較では、次の三つの層を区別します。

1. OpenMP V&Vによるコンパイラ機能の適合性確認
2. RAJAPerfによる代表カーネルと実装方式の比較
3. SPEChpcによる複数のプログラミングモデルを用いたアプリケーションとミニアプリケーションの比較

三つの層を一つの完了指標へ統合してはいけません。スイートの版、入力、精度、
正解条件、コンパイラ、依存関係、使用資源、計測区間を固定する必要があります。
公開結果だけでは、移植工数、ソースコードの変更量、長期保守性、HPCI向け
アプリケーション群全体の性能維持を判断できません。このため、`GAP-TDS-005`は
未解決のままです。

`RUP-000125`では、取得できたNICAM-DCの公開元カーネルと、移植論文が示す
Kokkos実装のURLを別々に記録しました。管理WebではKokkos実装を取得できなかった
ため、公開元カーネルの存在だけで、論文のコード、入力、ビルド条件を再現できるとは
判断しません。

### 性能根拠と参考試算

既存のEEA1 what-if記録36件を`illustrations`へ移し、正式な`forecasts`は
空にしました。すべての数値、根拠参照、旧`FORECAST-*` IDを保持しています。
未校正の計算が、従来の名前を保持しているという理由だけで正式予測の要件を
満たしたように見えることを防ぐための変更です。

参考試算は、信頼度が低く、Consensus未完了であり、調達判断には利用できません。
正式予測には、明示したモデル、分離した校正用データと独立検証用データ、
中以上の信頼度、受理済みConsensusが必要です。さらに、モデルカードが既存の
決定論的な性能モデル検証に合格し、独立Consensusで受理された状態で
`validated_model_cards`へ登録されていなければなりません。モデルカードに登録した
校正用・検証用データIDは、正式予測で使用するデータを包含する必要があります。
現在、この登録欄は空です。正式予測は条件を満たした範囲から段階的に追加でき、
従来の6アプリケーション×6規模の参考試算のように、全セルを埋めることを公開条件
にはしません。

GENESISの高速化可能と仮定した実行時間比率や規模別の保持係数を含め、モデルの
入力値は未校正の仮定です。表示する下側・基準・上側の値は参考範囲であり、
統計的信頼区間、誤差限界、性能保証ではありません。`GAP-PERF-001`から
`GAP-PERF-005`は未解決のままです。

### 検証範囲

リポジトリの検証器は、宣言した式から36件の参考試算を再計算し、IDの変更、
セルの重複、未登録の根拠・仮定、調達利用の許可を検出します。別のSchema検証では
正式予測の要件を確認します。また、正式予測が、決定論的検証とConsensusを通過した
モデルカードを参照し、そのカードに登録された校正用・検証用データを使用しているか
確認します。これらは構造の整合性と計算の再現可能性を確認するものであり、科学的
妥当性や独立した合意を証明するものではありません。
