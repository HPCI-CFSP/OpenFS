# EEA1 common benchmark and planning-option integration, round 1

## English

### Purpose

This round turns the six draft EEA1 acceptance criteria into one executable,
machine-checkable campaign plan and connects the expected outputs to all three
published system planning options. It defines what evidence is required before
an option may be scored; it does not supply benchmark results or rank options.

### Single source of truth

- `knowledge/public/application-performance-forecasts.json` owns the common
  protocol, application-specific criteria, campaign stages, and scenario bindings.
- `schemas/benchmark-result-bundle.schema.json` owns the result-bundle format.
- `tools/check_benchmark_result_bundle.py` owns result-level consistency checks.
- `roadmaps/scenarios/accepted/hpci-p0-scenarios.json` owns the three planning
  options and their decision-evidence contracts.

The campaign references the existing protocol instead of copying its measurement
rules. The EEA1 profile requires one warm-up and five valid runs per configuration,
although the generic result-bundle schema retains its reusable minimum of three.

### Five-stage gate

1. Application owners approve versioned inputs, scientific-correctness checks,
   applicable scales, and pass/fail values.
2. Reproducible Fugaku baseline packages pin code, inputs, dependencies, commands,
   logs, outputs, and digests.
3. At least two candidate configurations run the identical workload five valid
   times each and report performance, power, memory, communication, I/O, and failures.
4. At least two institutions and two Origin Groups repeat measurements; forecast
   validation uses data separate from calibration.
5. Independent Consensus review attempts falsification before an accountable human
   makes a planning decision.

All five stages currently cover zero of six applications. This is deliberate: public
measurements for similar or partially matching inputs do not count as matched-input
campaign completion.

### Planning-option bindings

- The balanced option emphasizes comparable scientific correctness, elapsed time,
  power, data movement, and porting effort across CPU-, GPU-, and memory-centric nodes.
- The AI- and data-intensive option requires a separate AI training, inference, and
  data-processing suite because EEA1 alone cannot establish AI-workload representativeness.
- The staged option uses the same evidence to govern pilot promotion, rollback,
  migration effort, and failure-recovery checks.

For every option, common benchmark evidence is necessary but insufficient. Complete
TCO, center-specific facility constraints, lifecycle evidence, Consensus review, and
an accountable human decision remain separate gates. No score, quantity, procurement
recommendation, or ranking is published in this round.

## 日本語

### 目的

EEA1の6アプリケーションに対する受入基準案を、実行可能かつ機械検証可能な
単一の共通ベンチマーク計画へまとめ、得るべき測定結果を3つのシステム整備
計画案へ接続しました。これは計画案を採点する前に必要な根拠を定めるもので、
測定結果や計画案の順位を示すものではありません。

### 情報の一元管理

- `knowledge/public/application-performance-forecasts.json` で共通プロトコル、
  アプリケーション別基準、実施段階、計画案との対応を管理します。
- `schemas/benchmark-result-bundle.schema.json` で測定結果の形式を管理します。
- `tools/check_benchmark_result_bundle.py` で測定結果の整合性を検証します。
- `roadmaps/scenarios/accepted/hpci-p0-scenarios.json` で3つの計画案と判断に
  必要な証拠契約を管理します。

測定規則は重複記載せず、既存の受入プロトコルを参照します。汎用的な測定結果
スキーマは3回を最低条件としますが、EEA1用プロファイルでは、事前実行1回と
各構成5回の有効測定を要求します。

### 5段階の確認

1. アプリケーション責任者が、版を固定した入力、科学的妥当性、適用規模、
   合否値を承認します。
2. 富岳基準測定について、コード、入力、依存関係、実行手順、ログ、出力、
   ダイジェストを固定します。
3. 少なくとも2構成で同一入力を各5回有効測定し、性能、電力、メモリ、通信、
   I/O、失敗を記録します。
4. 少なくとも2機関・2出所グループで再測定し、校正とは別のデータで予測を
   検証します。
5. 独立したConsensusレビューによる反証を経て、責任を持つ人が判断します。

現在は全段階とも6件中0件です。類似入力や条件の一部だけが一致する公開実測を、
同一入力によるキャンペーン完了とは数えないためです。

### 計画案への接続

- バランス型では、CPU中心、GPU中心、大容量メモリ構成を科学的妥当性、
  実行時間、電力、データ移動、移植工数で比較します。
- AI・データ集約型では、EEA1だけでは代表性が不足するため、AI学習・推論・
  データ処理の評価スイートを別途要求します。
- 段階導入型では、実証から次段階へ進む条件、撤退可能性、移植工数、障害復旧を
  同じ測定結果で確認します。

共通ベンチマークは、いずれの案にも必要ですが、それだけでは十分ではありません。
完全TCO、センター別施設条件、ライフサイクル情報、Consensusレビュー、人による
正式判断は別の確認事項です。今回は採点、数量、調達提案、推奨順位を公開しません。
