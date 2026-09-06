# HPCI power and cooling evidence, round 1

## Scope and status

This provisional, single-model pass adds public primary evidence for power and
cooling constraints without converting unlike measurements into a common rank.
Power evidence now covers 5 of the 27 systems in the FY2026 HPCI inventory;
quantitative operational evidence of any kind covers 16 systems. Independent
validation and Consensus remain incomplete.

## Evidence boundaries

| Systems | Recorded value | Boundary and limitation |
| --- | --- | --- |
| Fugaku | approximately 19,000 kW | The FY2022 annual report says average power for the Fugaku machine rose above 19 MW during FY2021. The recorded value is an approximate anchor, not an upper bound or facility-wide value. |
| Miyabi-G | 1,250 W/node | Rated node power; not measured average or system, network, storage, and cooling power. |
| Miyabi-C | 920 W/node | Rated node power; not measured average or system, network, storage, and cooling power. |
| ABCI 3.0 | 5,200 kW | Electrical capacity of the AI datacenter building, not measured machine power. The same source reports at least 5.2 MW cooling, 32 C water at up to 9,000 L/min, 70 kW/rack cooling, and annual average PUE at or below 1.1. |
| TSUBAME4.0 | existing 1,820 kW design and 600-800 kW normal-operation records | Values include cooling, and remain separate from the other boundaries above. |

No total Miyabi power was estimated by multiplying rated node power by node
count. No ABCI machine power was inferred from building capacity. These
distinctions must be preserved in procurement requirements and five-year TCO.

Primary sources:

- RIKEN R-CCS, [Fugaku Annual Report 2022: facility management](https://www.r-ccs.riken.jp/fugaku/fugaku-annual-reports/2022/2/2/)
- The University of Tokyo, [Miyabi early-use briefing](https://www.cc.u-tokyo.ac.jp/events/seminar/files/JCAHPC_20241213_Miyabi.pdf)
- AIST, [ABCI datacenter](https://abci.ai/ja/about_abci/datacenter_facility.html)

## 日本語要約

電力値の公開一次情報を5システムまで拡充しました。ただし、富岳は本体の運用時平均電力の
概算基準、Miyabi-C・Gはノード定格、ABCI 3.0は建屋の電力容量、TSUBAME4.0は冷却込みの
設計値・通常運用範囲であり、境界が異なります。これらを単純比較したり、ノード数を乗じて
未公表のシステム電力を推定したりしていません。ABCIについては、5.2 MW以上の冷却能力、
32℃の冷却水を最大9,000 L/分、ラック当たり70 kW、年間平均PUE 1.1以下という施設条件も
記録しました。単一モデルによる調査のためConsensusは未完了です。
