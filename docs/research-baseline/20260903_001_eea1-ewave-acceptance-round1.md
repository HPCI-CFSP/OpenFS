# EEA1 evidence and draft acceptance criteria, round 1

## English

### Purpose

This round turns the six EEA1 applications from a list of performance examples
into a testable, but still provisional, acceptance framework. It does not assign
procurement targets. The application owners must approve inputs, applicable
scales, correctness tolerances, and pass/fail values before the criteria can be
used in a system acquisition.

### E-Wave evidence added

The FY2021 JAMSTEC project report supplies a public E-wave FEM measurement that
was missing from the structured performance surface:

- Ground-motion domain: 238 km x 188 km x 108 km.
- Approximately 1.77 billion finite elements and 2.38 billion finite-element
  mesh nodes.
- 20,000 time steps at 0.01 seconds per step.
- Fugaku main calculation: 385 nodes, 1,540 MPI processes, 7.6 hours.
- Preprocessing on Jasper: 33.2 hours; postprocessing on Fugaku: 2.8 hours.
  These stages are kept separate from the 7.6-hour main Fugaku calculation.

This is a useful public scale and workflow observation, but it is not the same
input as the FugakuNEXT EEA1 case. It is therefore not added to a calibration
candidate and does not make an EEA1 forecast available.

The same official report describes accuracy checks against analytical and FDM
results, including waveform comparison. The draft E-Wave correctness contract
therefore requires waveform correlation, amplitude, phase, frequency-band, and
engineering-output checks, while leaving numerical tolerances to the application
owner.

### Common measurement contract

`ACCPROTO-EEA1-001` proposes one warm-up run and five valid measured runs. It
reports the median, minimum, maximum, and coefficient of variation, and records
failed or excluded runs. Code revision, input, precision, convergence, output,
and timing boundaries must be pinned. The comparison basis must state whether
node count, accelerators, memory, power, or cost is held equal.

All six application drafts require scientific correctness, time to solution,
domain throughput, parallel efficiency, energy to solution, peak memory,
communication share, I/O volume, and run variability. I/O throughput is
conditional but must be collected when I/O affects the measured interval.

### Decision boundary

- Six of six applications now have a draft measurement contract.
- Six of six applications have some public Fugaku measurement evidence.
- Five of six applications have public candidate-platform measurements.
- Two interpolation candidates exist; both remain limited to one system, one
  workload, and one origin.
- Zero applications have human-approved pass/fail thresholds.
- Zero future-performance forecasts are validated.
- Consensus is incomplete and procurement use is prohibited.

### Sources

- [JAMSTEC FY2021 project report](https://www.jamstec.go.jp/fugaku-earthq/ja/docs/r3fugakujishin_seikahokoku.pdf)
- [RIKEN R-CCS FugakuNEXT application development and evaluation environment](https://www.r-ccs.riken.jp/events/20260306-1/fugakunext-5.pdf)
- [JAMSTEC numerical-analysis project overview](https://www.jamstec.go.jp/namr/project03.html)

## 日本語

### 目的

本更新では、EEA1の6アプリケーションについて、性能事例の列挙から、検証可能な
受入試験の枠組みへ進めます。ただし、現段階は暫定案であり、調達目標値ではありません。
システム調達へ用いる前に、アプリケーション責任者が入力、適用規模、科学的妥当性の
許容差、合否値を承認する必要があります。

### 追加したE-Waveの根拠

JAMSTECの令和3年度成果報告書から、これまで構造化データに不足していたE-wave FEMの
公開実測を追加しました。

- 地震動計算の領域: 238 km x 188 km x 108 km
- 約17.7億有限要素、約23.8億節点
- 時間刻み0.01秒、20,000ステップ
- 富岳の本計算: 385ノード、1,540 MPIプロセス、7.6時間
- Jasperでのプリプロセス: 33.2時間、富岳でのポストプロセス: 2.8時間。
  富岳の本計算7.6時間とは別工程として分離して登録しています。

これは公開された規模・ワークフローの観測として有用ですが、FugakuNEXTのEEA1と
同一入力ではありません。そのため校正候補には加えず、EEA1性能予測が可能になったとは
扱いません。

同報告書は、解析解やFDMとの比較を含む精度検証も記載しています。E-Waveの受入基準案
では、波形の相互相関、振幅、位相、対象周波数帯、工学的出力を確認対象とし、数値的な
許容値はアプリケーション責任者の判断事項として残しました。

### 共通測定契約

`ACCPROTO-EEA1-001`では、ウォームアップ1回、有効測定5回を暫定的に提案し、中央値、
最小値、最大値、変動係数を報告します。失敗実行や除外した実行も記録します。コード版、
入力、精度、収束条件、出力、計測区間を固定し、同一ノード数、同一アクセラレータ数、
同一メモリ容量、同一消費電力、同一費用のどの条件で比較したかを明示します。

6アプリケーションすべてについて、科学的妥当性、実行時間、分野指標による処理速度、
並列効率、解取得までのエネルギー、最大メモリ使用量、通信時間比率、I/O量、実行時間の
ばらつきを必須測定項目としました。I/O実効帯域は、I/Oが計測区間へ影響する場合の
条件付き項目です。

### 判断の境界

- 6アプリケーションすべてに測定契約案があります。
- 6アプリケーションすべてに何らかの富岳公開実測があります。
- 候補機での公開実測があるのは5アプリケーションです。
- 補間候補は2件ありますが、いずれも1システム、1入力、1出所に限られます。
- 人が合否値を承認したアプリケーションは0件です。
- 検証済みの将来性能予測は0件です。
- Consensusは未完了であり、調達判断への利用は禁止します。

### 情報源

- [JAMSTEC 令和3年度成果報告書](https://www.jamstec.go.jp/fugaku-earthq/ja/docs/r3fugakujishin_seikahokoku.pdf)
- [理研R-CCS FugakuNEXTアプリケーション開発・評価環境](https://www.r-ccs.riken.jp/events/20260306-1/fugakunext-5.pdf)
- [JAMSTEC 大規模数値解析プロジェクト概要](https://www.jamstec.go.jp/namr/project03.html)
