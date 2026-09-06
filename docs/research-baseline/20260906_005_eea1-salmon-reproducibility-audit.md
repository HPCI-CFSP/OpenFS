# EEA1 SALMON reproducibility audit

## Finding

The public assets are useful but do not yet form an EEA1-reproducible baseline.
OpenFS has pinned the following candidates:

- SALMON2 v.2.3.0 source commit `30ba64694ec761cdb6288f01a75b8bcabf05721f`;
- SALMON public-input snapshot `e5cf45d7378cc1aec6bb4dd4c3b534cbee8a81b9`;
- Fugaku evaluation-script snapshot `89ef39246bc903712b3b22260a050647953e117b`.

The official install and run guide establishes the generic execution contract:
SALMON reads a Fortran-namelist input from standard input and requires
element-specific norm-conserving pseudopotentials. An MPI-capable Fortran/C
toolchain and BLAS/LAPACK are required; ScaLAPACK, EigenExa and Libxc are
configuration-dependent. These generic instructions improve the audit but do
not identify the EEA1 experiment.

## Blocking evidence

The following must be pinned as one owner-approved package before reproducible
measurement or formal performance prediction:

1. the exact EEA1 supercell input and every referenced pseudopotential;
2. confirmation that the public input is identical to EEA1, or an explicit
   declaration that it is only a proxy;
3. compiler, MPI, numerical-library and CMake versions, build options and flags;
4. node resources, MPI-process and thread mapping, affinity, power mode and job
   launcher options;
5. restart or initialization state and the exact timed stages;
6. reference outputs, comparison fields, numerical tolerances and failure rules;
7. a content digest for all inputs and an approved redistribution statement; and
8. an independent rerun on the reference system before candidate-system use.

The public input repository accepts publication metadata and optionally output
files, but that policy does not prove that the EEA1 input or reference output is
present. No missing item is inferred from a similarly named example. The
baseline remains blocked and is not procurement-eligible.

Primary sources:

- SALMON developers, [official install and run guide](https://salmon-tddft.jp/webmanual/v_2_2_2/html/install_and_run.html)
- SALMON developers, [public input collection](https://github.com/SALMON-TDDFT/SALMON-inputs)
- SALMON developers, [SALMON2 source](https://github.com/SALMON-TDDFT/SALMON2)
- SALMON developers, [Fugaku evaluation scripts](https://github.com/SALMON-TDDFT/SALMON2-evaluation-scripts)

## 日本語要約

SALMON2 v.2.3.0、公開入力集、富岳向け評価スクリプトはコミット単位で固定されていますが、
EEA1を再現できる一体の基準測定パッケージにはなっていません。公式手順から、入力ファイルに
加えて元素ごとの擬ポテンシャル、MPI対応コンパイラ、BLAS/LAPACKなどが必要と確認しました。
一方、EEA1スーパーセル入力との一致、擬ポテンシャル、ビルド条件、プロセス・スレッド配置、
測定区間、参照出力、数値一致条件、再配布条件は未確認です。類似する公開入力から補完せず、
アプリケーション責任者が一体のパッケージとして承認し、独立再実行が完了するまで、調達評価に
使用しません。単一モデルによる調査のためConsensusは未完了です。
