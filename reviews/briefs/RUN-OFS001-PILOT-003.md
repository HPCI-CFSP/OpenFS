# OpenFS Run Brief: RUN-OFS001-PILOT-003

Generated: `2026-08-23T17:53:30Z`

- Run: **completed**
- Research: **provisional**
- Coverage: **met-declared-scope**
- Consensus capacity: **incomplete**
- Review: **human-review-required**

## Claims for review

### 1. `CLM-148702` (provisional)

Public 2025 sources indicate that heterogeneous-memory benefit depends jointly on application or object access behavior and placement policy. HPCI candidate evaluation therefore needs real-application sensitivity studies and migration overhead in addition to device bandwidth and capacity.

Conditions:
- The result is limited to the cited FS3 scope and DOE summary; reported speedups are configuration-specific.

Sources:
- [HPCI整備計画調査研究 運用システム整備計画調査研究](https://www.r-ccs.riken.jp/assets/uploads/2025/12/fs3-overview_jp.pdf) (理化学研究所 計算科学研究センター, `official-primary`)
- [Improving Computing Memory Performance for Scientific Discovery](https://stage.energy.gov/science/ascr/articles/improving-computing-memory-performance-scientific-discovery) (U.S. Department of Energy Office of Science, `official-primary`)

Unmet checks: `minimum_assessments`, `minimum_support`, `minimum_support_independence_groups`

Reviewer objections:
- **major**: The reviewer and Proposal author are in the same OpenAI GPT-5 Codex independence group; this review cannot supply independent support.
- **minor**: The DOE page summarizes selected real-system evaluations but does not expose enough configuration detail to generalize a migration policy across HPCI applications.

### 2. `CLM-382908` (provisional)

Research published in 2023 and 2026 indicates that switched CXL pooling needs a total-cost and scheduler-only baseline plus explicit interference, fairness, congestion, and admission-control evaluation. Capacity pooling alone does not establish net system benefit.

Conditions:
- Datacenter and switched-appliance evidence may not transfer directly to every HPCI workload or topology.

Sources:
- [Building A CSFQ-Inspired Transport for Switched CXL Memory Pooling](https://www.usenix.org/conference/nsdi26/presentation/guo-zerui) (USENIX Association, `peer-reviewed-research`)
- [A Case Against CXL Memory Pooling](https://research.google/pubs/a-case-against-cxl-memory-pooling/) (Google Research / ACM HotNets, `peer-reviewed-research`)

Unmet checks: `minimum_assessments`, `minimum_support`, `minimum_support_independence_groups`

Reviewer objections:
- **major**: The reviewer and Proposal author are in the same OpenAI GPT-5 Codex independence group; this review cannot supply independent support.
- **major**: The cited HotNets argument and NSDI appliance study cover datacenter assumptions and one switched platform; HPCI scheduler, fabric, workload, and acquisition-cost baselines still require direct evaluation.

### 3. `CLM-726174` (provisional)

CXL link capabilities and observed pooled-system behavior are different evaluation layers. A standard's link rate and RAS features do not predict workload latency, transfer-direction behavior, contention, or balance across pooled devices.

Conditions:
- The reported 214 ns and 658 ns measurements belong to one published setup and are not universal constants.

Sources:
- [CXL-CCL: Inter-Node Collective GPU-Communication Using a CXL Shared Memory Pool](https://doi.org/10.1145/3797905.3807846) (ACM International Conference on Supercomputing, `peer-reviewed-research`)
- [CXL Consortium Releases the Compute Express Link 4.0 Specification Increasing Speed and Bandwidth](https://computeexpresslink.org/wp-content/uploads/2025/11/CXL_4.0-Specification-Release_FINAL_Website-Copy.pdf) (Compute Express Link Consortium, `standards-body`)

Unmet checks: `minimum_assessments`, `minimum_support`, `minimum_support_independence_groups`

Reviewer objections:
- **major**: The reviewer and Proposal author are in the same OpenAI GPT-5 Codex independence group; this review cannot supply independent support.
- **minor**: The 214 ns and 658 ns values are tied to one published setup, while the CXL 4.0 item is a standards announcement rather than an application benchmark.

### 4. `CLM-485678` (provisional)

Independent packaging analyses identify signal integrity, power delivery, warpage, heat dissipation, interconnect density, and attainable stack configuration as coupled HBM4 constraints. Architecture exploration should use thermally attainable bandwidth rather than peak interface bandwidth alone.

Conditions:
- The cited materials characterize integration constraints; they do not provide a complete HPCI application benchmark.

Sources:
- [AI Technology and the Markets](https://eps.ieee.org/wp-content/uploads/2025/11/Oct_8_Vardaman_.pdf) (TechSearch International, `independent-analysis`)
- [Packaging Integration: AI/HPC Memory and Data-Movement Scaling](https://www.ieee.org/ns/periodicals/EDS/EDS-OCTOBER-2025-HTML/InnerFiles/LandPage.html) (IEEE Electron Devices Society Newsletter, `independent-analysis`)

Unmet checks: `minimum_assessments`, `minimum_support`, `minimum_support_independence_groups`, `primary_source`

Reviewer objections:
- **major**: The reviewer and Proposal author are in the same OpenAI GPT-5 Codex independence group; this review cannot supply independent support.
- **major**: Both cited sources are independent packaging analyses rather than primary HBM4 HPCI application measurements; thermally attainable bandwidth still needs platform-specific validation.

### 5. `CLM-132983` (provisional)

Public Japanese and European roadmap sources support an updateable, multi-objective HPCI memory evaluation spanning performance, capacity, cost, power, coherence, data movement, and replacement flexibility; they do not establish one memory medium as universally optimal.

Conditions:
- The statement is a synthesis of roadmap priorities, not a procurement recommendation.

Sources:
- [ETP4HPC SRA6 White Paper - Hardware Components](https://zenodo.org/records/15185032) (ETP4HPC, `research-primary`)
- [次世代計算基盤に関する報告書 最終取りまとめ ポイント](https://www.mext.go.jp/content/20240614-mxt-jyohoka01-000036490_04.pdf) (文部科学省 HPCI計画推進委員会, `official-primary`)

Unmet checks: `minimum_assessments`, `minimum_support`, `minimum_support_independence_groups`

Reviewer objections:
- **major**: The reviewer and Proposal author are in the same OpenAI GPT-5 Codex independence group; this review cannot supply independent support.
- **minor**: Roadmap priorities support an evaluation framework but do not supply calibrated weights, thresholds, or a procurement ranking.

### 6. `CLM-775072` (provisional)

Japan's public next-generation memory portfolio includes HBM4E, CXL 3D memory, low-power DRAM, and ZAM at different maturity levels. ZAM has stated FY2027 prototype and FY2029 commercialization targets, but the cited sources do not yet provide measured HPCI application suitability.

Conditions:
- Vendor and program targets are not treated as achieved product performance or adoption evidence.

Sources:
- [SoftBank Corp. Subsidiary SAIMEMORY and Intel Collaborate to Commercialize Next-generation Memory Technology](https://www.saimemory.co.jp/assets/news/pdf/SAIMEMORY_PR_20260203_01_ENG.pdf) (SoftBank Corp. and SAIMEMORY Corp., `vendor-primary`)
- [次世代メモリ技術開発](https://www.nedo.go.jp/content/800036414.pdf) (NEDO, `official-primary`)

Unmet checks: `minimum_assessments`, `minimum_support`, `minimum_support_independence_groups`

Reviewer objections:
- **major**: The reviewer and Proposal author are in the same OpenAI GPT-5 Codex independence group; this review cannot supply independent support.
- **major**: NEDO and SAIMEMORY describe related program and vendor plans, not independent achieved-performance evidence; HPCI workload, yield, reliability, cost, and software integration remain unmeasured in the cited public sources.

## Caveats

- This brief is a generated review view, not primary evidence.
- Only accepted artifacts may enter the publication workflow.
- Source links and repository evidence records must be checked before use.
