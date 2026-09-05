# HPCI demand and public procurement evidence update

## Scope

This provisional update strengthens two evidence layers used by the system
planning options:

1. demand and operational evidence for the 27-system FY2026 HPCI inventory;
2. public basic requirements and cost boundaries for academic and research
   computing procurements.

The work was performed by one model in an interactive maintainer session. It is
not independent validation or Consensus. No recommendation, score, weight, price
estimate, or EEA1 acceptance threshold is introduced.

## HPCI demand and operations

The HPCI statistics page publishes FY2026 regular-call values for 25 systems in
the current inventory. OpenFS records 26 rows because Genkai node group B has
separate shared and node-fixed allocation modes. Each row preserves:

- resource-level application count;
- requested-resource ratio, defined by HPCI as requested resources divided by
  available resources;
- acceptance rate; and
- the allocation mode when the source separates it.

These values describe demand and allocation at the call stage. They are not
runtime utilization, queue wait, delivered resource volume, or latent demand.
Fugaku and ABCI 3.0 are not present in the same resource-level table and remain a
Coverage Gap.

The operations layer also adds four exact TSUBAME4 monthly node-utilization
values published by the Institute of Science Tokyo: 47.06% in April, 87.22% in
May, 95.31% in June and 93.89% in July 2024. The source counts a node as in use
when any partition is active. A Kyushu University publication covering October
2024 through July 2025 is registered as a chart-only data product for Genkai A
and B; OpenFS does not infer numeric values from the chart.

Primary sources:

- HPCI, [Major statistics](https://www.hpci-office.jp/about_hpci/statistics)
- Institute of Science Tokyo, [FY2025 TSUBAME shared-use briefing](https://www.gsic.titech.ac.jp/sites/default/files/R7kobo3.pdf)
- Kyushu University, [Usage analysis of the Genkai supercomputer](https://www.jstage.jst.go.jp/article/axies/2025/0/2025_676/_pdf/-char/en)

## Public procurement requirements

OpenFS adds public RFI-stage basic requirements to the existing RIKEN AI for
Science, Sirius and Furo NEXT cases, and adds the 2026 JSS4 computing-platform
RFI as a separate fourteenth case. The 2026 JSS4 case is not merged with the
2025 JSS4 tender because the public titles, scopes and procurement stages differ.

The public requirements are also represented as external workload-to-system
translation examples on the EEA1 planning surface:

| Case | Decision-relevant requirement boundary |
| --- | --- |
| RIKEN AI for Science | AI compute, fast storage, internal and adjacent-system connectivity, scheduling, warm-water cooling, density and long-term operating cost |
| Sirius | Coherent CPU/GPU memory, local NVMe, fabric, parallel filesystem, programming environment and a 300 kVA facility limit |
| Furo NEXT | CPU, GPU, large-memory, cloud and four storage tiers within a 3 MVA system and phased-introduction boundary |
| JSS4 computing platform | Compute, data, operations, security, facilities, quantum and software over an approximately six-year operational intent |
| Kyoto genomics and chemistry | Workload-specific CPU, GPU, memory, storage, network, resilience and domain-software requirements |

These are requirement examples, not prices, deployed configurations, measured
performance, or EEA1 pass/fail values. Package totals remain unitemized; complete
five-year TCO remains unavailable for all 14 registered cases.

Primary sources:

- RIKEN, [AI for Science supercomputer RFI](https://www.jetro.go.jp/gov_procurement/national/articles/293346/2023120101230001.html)
- University of Tsukuba, [Unified-memory supercomputer RFI](https://www.jetro.go.jp/gov_procurement/national/articles/308570/2024040800430001.html)
- Nagoya University, [Furo NEXT RFI](https://www.jetro.go.jp/gov_procurement/national/articles/323801/2024080600650001.html)
- JAXA, [JSS4 computing-platform RFI](https://www.jetro.go.jp/gov_procurement/national/articles/400647/2026081700600001.html)
- Kyoto University, [Genomics and computational-chemistry system RFI](https://www.jetro.go.jp/gov_procurement/national/articles/386021/2026032600480001.html)

## Remaining work

- collect post-award use, queue-time and workload-mix evidence under aligned
  definitions;
- obtain publicly usable final specifications and contract boundaries without
  collecting restricted documents;
- find itemized component prices and complete lifecycle-cost evidence;
- pin redistributable EEA1 inputs and reference outputs with application-owner
  confirmation; and
- submit the evidence package to genuinely independent reviewers before any
  Consensus claim.

## 日本語要約

令和8年度定期募集について、現行台帳の25システムを対象に、応募数、要求資源倍率、
採択率を登録しました。玄界Bは共有とノード固定を分けるため26行です。これらは公募時の
需要と配分結果であり、実運用時の利用率や待ち時間ではありません。TSUBAME4の月別
ノード利用率4点を数値として追加し、玄界A・Bの利用状況は公開図から数値を推測せず、
図として確認できるデータ項目として登録しました。

公共調達では、理研AI for Science、Sirius、不老NEXTの公開基本要求を既存案件へ追加し、
2026年のJSS4コンピュータ基盤に関する資料提供招請を別案件として追加しました。これらと
京都大学の要求要件を、用途から演算、メモリ、ストレージ、ネットワーク、施設、
ソフトウェア、運用へ変換した外部事例としてPagesへ表示します。ただし、価格、最終仕様、
実導入構成、実測性能、EEA1の合否値には扱いません。14件すべてで完全な5年間TCOは
未算出であり、単一モデルによる調査のためConsensusは未完了です。
