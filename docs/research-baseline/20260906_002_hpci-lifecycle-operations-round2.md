# HPCI lifecycle and operations evidence, round 2

## Scope and status

This provisional, single-model research pass checks public primary sources for
future lifecycle timing and operational-information paths across the 27 systems
in the FY2026 HPCI inventory. It does not constitute independent validation or
Consensus.

Coverage after this pass is:

- future retirement, refresh, or expansion timing: 16 of 27 systems;
- public operational-information paths: 25 of 27 systems; and
- quantitative operational observations: 16 of 27 systems.

A current status page, maintenance notice, or usage rule is counted only as an
operational-information path. It is not treated as numerical utilization,
availability, queue-time, or power evidence.

## Added evidence

| System | Evidence added | Planning boundary |
| --- | --- | --- |
| Earth Simulator ES4 CPU and VE | JAMSTEC states that FY2026 is the current ES4's final operating fiscal year. | Recorded as 2027 Q1, the Japanese fiscal-year end. This does not establish the successor launch or migration period. |
| TSUBAME4.0 | The public procurement notice gives a lease period ending March 31, 2030. | Recorded as 2030 Q1. A contractual lease end does not establish a successor launch or migration period. |
| OCTOPUS CPU | The public procurement notice gives a lease period ending August 31, 2031. | Recorded as 2031 Q3. The matching service start identifies the contract, but the lease end does not establish a service stop, successor launch, or migration period. |
| Camphor3-A | The public procurement notice gives a lease period ending December 31, 2027. | Recorded as 2027 Q4. The notice does not establish a service stop, successor launch, or migration period. |
| AOBA-S | The public procurement notice gives a lease period ending March 31, 2028. | Recorded as 2028 Q1. The notice does not establish AOBA-A/B retirement or a successor launch. |
| Grand Chariot 2 CPU and GPU | The public procurement notice gives a lease period ending March 31, 2030. | Recorded as 2030 Q1 for both HPCI resources. The notice does not establish a service stop, migration period, or successor launch. |
| University of Tsukuba | A request for information plans an HPC-AI system from March 2027 onward and requires access to the existing Pegasus and Sirius file systems. | Recorded as a provisional 2027 Q1 center update, not a final procurement, operating launch, or HPCI availability date. |
| AOBA-A and AOBA-B | A provider notice records service suspension, maintenance, recovery, and job impact. | One incident record, not an annual availability or utilization aggregate. |
| OCTOPUS CPU | The provider system page reports operation from September 1, 2025 and a current steady-operation state. | Current service status, not availability, downtime, utilization, or queue statistics. |
| ISM large-memory system | Usage rules effective April 1, 2026 define applications, accounts, renewal, and usage-based fees. | Evidence of an active service framework, not current incident or performance statistics. |

Primary sources:

- JAMSTEC, [FY2026 Earth Simulator Challenge Use call](https://www.jamstec.go.jp/es/jp/project/r08ch/R08_Challenge_oubo.pdf)
- JETRO Government Procurement Database, [TSUBAME4.0 procurement notice](https://www.jetro.go.jp/gov_procurement/national/articles/256628/2022121400400001.html)
- JETRO Government Procurement Database, [University of Osaka shared-use supercomputer procurement notice](https://www.jetro.go.jp/gov_procurement/national/articles/329362/2024100700450001.html)
- JETRO Government Procurement Database, [Kyoto University Institute for Chemical Research supercomputer procurement notice](https://www.jetro.go.jp/gov_procurement/national/articles/264303/2023022100240001.html)
- JETRO Government Procurement Database, [Tohoku University supercomputer procurement notice](https://www.jetro.go.jp/gov_procurement/national/articles/233599/2022042100330003.html)
- JETRO Government Procurement Database, [University of Tsukuba HPC-AI supercomputer request for information](https://www.jetro.go.jp/gov_procurement/national/articles/385153/2026031600450001.html)
- JETRO Government Procurement Database, [Hokkaido University interdisciplinary large-scale computing system procurement notice](https://www.jetro.go.jp/gov_procurement/national/articles/302618/2024021400260000.html)
- Tohoku University, [AOBA emergency maintenance notice](https://www.ss.cc.tohoku.ac.jp/n20260709-1/)
- University of Osaka D3 Center, [OCTOPUS system page](https://www.hpc.cmc.osaka-u.ac.jp/octopus2/)
- Institute of Statistical Mathematics, [current usage rules](https://www.ism.ac.jp/computer_system/jpn/hpci/6-11.pdf)

## Coverage gaps

Future timing remains unverified for 11 systems: Fugaku, Genkai A and B,
Miyabi C and G, AOBA A and B, the ISM large-memory system,
Sirius, Pegasus, and ABCI 3.0. The planned 2027 Tsukuba system is a center-level
update and does not establish the retirement dates of Sirius or Pegasus. No date
should be inferred from a typical lease term or another system's lifecycle.

The only systems without a public operational-information path are the two
Furo-II resources, which are still pre-service as of this check. Tracking should
begin after their formal launch. Comparable numerical evidence remains sparse:
periods, denominators, maintenance exclusions, and facility or system power
boundaries are not aligned across providers.

## 日本語要約

令和8年度HPCI資源一覧の27システムを対象に、将来の更新・終了・増強時期と公開運用情報を
追加調査しました。将来時期は16システム、公開運用情報への経路は25システム、数値を伴う
運用実績は16システムです。地球シミュレータES4は令和8年度が現行システムの運用最終年度、
TSUBAME4.0は2030年3月31日が借入期間の終期であることを一次情報で確認しました。ただし、
いずれも後継機の稼働開始日や移行期間を示すものではありません。

さらに、OCTOPUSは2031年8月末、Camphor3は2027年12月末、AOBA-Sは2028年3月末が
公告上の借入期間の終期であることを確認しました。筑波大学では2027年3月以降のHPC-AI
新システム導入計画と、既存Pegasus・Siriusのファイルシステムへ接続する要件が公示されています。
これらは契約または計画上の日付であり、サービス停止、後継機の稼働、HPCI提供の確定日ではありません。

Grand Chariot 2は、CPU・GPUの両資源を含む学際大規模計算機システムの借入期間が
2030年3月31日までであることを確認しました。これも契約境界であり、正式なサービス停止日、
移行期間、後継機の稼働開始日を示すものではありません。

AOBA-A・Bの保守通知、OCTOPUSの運転状態、統計数理研究所の利用細則も登録しましたが、
これらは公開運用情報への経路であり、稼働率、年度可用性、待ち時間、電力の数値実績としては
扱いません。将来時期が未確認の11システムはCoverage Gapとして残し、一般的な借入期間など
から日付を推定していません。単一モデルによる調査のためConsensusは未完了です。
