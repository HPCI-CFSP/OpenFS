# OpenFS Research Baseline

## Purpose

This directory defines the research inventory that OpenFS agents use when creating Tasks and Monitors. `FSBASE-002` preserves the original 30-topic `FSBASE-001` catalog, adds topics identified through a review of all 26 reports linked from the official FY2022-FY2025 MEXT FS pages, and includes a human-directed broad domestic-technology scope.

An agent may and should propose candidate topics when new evidence appears. AI-originated proposals follow the same evidence, independent-review, and consensus process as human-originated proposals. An agent must not silently remove, merge, or narrow an existing topic. The original 30 IDs are explicitly protected in `config/research-baseline.json`.

The machine-readable source of truth is `config/research-baseline.json`. This document is the human-readable view.

## How agents use the baseline

1. Select one or more `topic_id` values when creating a Task or Monitor.
2. Convert the listed research questions into source-class and query families.
3. Preserve the expected evidence and output fields in the work item.
4. Record uncovered topics and failed source classes in coverage results.
5. Propose additions or changes through `OFS-002`; do not edit the baseline as incidental research output.
6. Keep vendor claims, measured results, forecasts, interpretations, and HPCI recommendations separate.

If no baseline topic fits, use `OFS-002` to propose a new topic before starting recurring collection. A one-off exploratory Task may proceed only with an explicit human Directive.

## Protected initial topic catalog

The following 30 topics are the unchanged starting catalog from `FSBASE-001`. Additions extend this catalog; they do not replace it.

### Architecture

| ID | Topic | Questions to carry into research |
|---|---|---|
| `ARCH-01` | Heterogeneous compute and node architecture | What mix of CPU, GPU, vector, FPGA, and AI accelerators serves the HPCI workload portfolio? Which resources should be tightly or loosely coupled? |
| `ARCH-02` | Semiconductor, chiplet, and advanced packaging | How do process nodes, 2.5D/3D/3.5D integration, UCIe-class chiplets, and yield constrain cost, power, and deployment time? |
| `ARCH-03` | Memory hierarchy and data movement | Which HBM, DDR, CXL, pooled, tiered, or emerging-memory combinations suit bandwidth-, latency-, and capacity-sensitive workloads? |
| `ARCH-04` | Interconnect and optical networking | How should scale-up and scale-out networks combine electrical and optical links, and what topology and congestion behavior results? |
| `ARCH-05` | System composition and resource disaggregation | Which functions belong in large homogeneous systems versus smaller heterogeneous or disaggregated systems, and how are they composed across HPCI? |
| `ARCH-06` | Power, cooling, and facilities | What power envelope, cooling technology, facility capacity, and carbon or energy constraints govern feasible systems? |
| `ARCH-07` | Supply chain and economic security | How do manufacturing capacity, domestic technology, vendor concentration, export controls, and lifecycle supply affect options? |

### System software

| ID | Topic | Questions to carry into research |
|---|---|---|
| `SSW-01` | Programming models and performance portability | What roles should CUDA, OpenMP target, SYCL, Kokkos, oneAPI, ROCm, Julia, and future models play across heterogeneous HPCI? |
| `SSW-02` | Compilers, languages, and application continuity | How are Fortran, C/C++, Python, binaries, and long-lived scientific codes migrated and sustained? |
| `SSW-03` | Communication and runtime systems | How should MPI, UCX/UCC, collective libraries, and accelerator fabrics map to hierarchical HPCI networks? |
| `SSW-04` | Numerical libraries and algorithms | Which dense, sparse, FFT, mixed-precision, randomized, and accelerator libraries require shared investment? |
| `SSW-05` | Storage, filesystems, and data management | How should data move and persist across sites, tiers, AI pipelines, archives, and workflow boundaries? |
| `SSW-06` | Scheduler, OS, containers, packages, and cloud | What resource management and execution environment supports composable HPC and AI resources without fragmenting operations? |
| `SSW-07` | Observability and performance engineering | Which usage telemetry, profilers, debuggers, traces, and performance models are needed for evidence-based planning? |
| `SSW-08` | Software sustainability and OSS governance | What should be developed domestically, maintained upstream, adopted internationally, or retired, and by whom? |
| `SSW-09` | AI for Science platform services | Which model, data, workflow, inference, and experiment services should be common HPCI capabilities? |

### Applications and users

| ID | Topic | Questions to carry into research |
|---|---|---|
| `APP-01` | Future application and user needs | Which scientific domains, algorithm classes, data scales, interaction patterns, and service levels will matter in the target period? |
| `APP-02` | Benchmarks, proxies, and performance models | Which representative applications and motifs can evaluate architecture candidates continuously and reproducibly? |
| `APP-03` | AI for Science workflows | How will simulation, learning, experimental data, foundation models, and inference be coupled? |
| `APP-04` | Scientific AI agents | What workload shape, scalability, reliability, provenance, and security arise from multi-agent science workflows? |
| `APP-05` | Code generation and automatic porting | Where can AI-assisted generation, tuning, and accelerator migration improve productivity without compromising correctness? |
| `APP-06` | Experiment and workflow automation | Which orchestration, closed-loop experiment, digital-twin, and human-approval capabilities are required? |
| `APP-07` | Skills, training, and adoption | What user support, education, interfaces, and migration paths keep HPCI broadly usable? |

### Cross-cutting planning

| ID | Topic | Questions to carry into research |
|---|---|---|
| `CROSS-01` | HPCI reference blueprint | What reusable technical specifications and evaluation methods allow sites to plan interoperable systems? |
| `CROSS-02` | Continuous benchmarking | How should performance, cost, power, and application coverage be measured repeatedly as technologies change? |
| `CROSS-03` | Integrated HPCI operation and data movement | Which identity, allocation, network, data-transfer, catalog, and federation functions make separate systems operate as one infrastructure? |
| `CROSS-04` | Operations and security | What reliability, resilience, incident response, supply-chain security, and zero-trust controls are needed? |
| `CROSS-05` | Quantum-HPC hybrid operation | Which workloads, interfaces, scheduling, data paths, and maturity gates justify integration with quantum resources? |
| `CROSS-06` | Procurement, scenarios, and roadmap | How do technology maturity, cost, deployment timing, reversibility, and uncertainty produce multiple actionable scenarios? |
| `CROSS-07` | Continuous FS governance and provenance | How are recurring evidence, dissent, decisions, human Directives, and report lineage maintained across FS cycles? |

## FS2.0/FS3.0 additions

### Architecture additions

| ID | Topic |
|---|---|
| `ARCH-08` | Data-movement and performance-bottleneck quantification |
| `ARCH-09` | Strong/weak scaling and service characteristics |
| `ARCH-10` | RAS, maintainability, and long lifecycle |
| `ARCH-11` | Domestic processors, accelerators, and packaging technologies |
| `ARCH-12` | Reconfigurable, dataflow, and domain-specific computing |
| `ARCH-13` | Mixed precision, approximate computing, and numerical integrity |

### System-software additions

| ID | Topic |
|---|---|
| `SSW-10` | Autotuning and compiler-assisted optimization |
| `SSW-11` | Federated resource abstraction, meta-scheduling, and urgent computing |
| `SSW-12` | Federated identity, authorization, and portals |
| `SSW-13` | Cross-generation data lifecycle and high-speed transfer |
| `SSW-14` | Confidential computing, privacy, and federated security |
| `SSW-15` | Power/cooling telemetry and power-adaptive operation |
| `SSW-16` | Unified HPC, AI, and experimental-facility workflow execution |

### Application additions

| ID | Topic |
|---|---|
| `APP-08` | Priority-domain portfolio and workload representativeness |
| `APP-09` | Urgent, real-time, and experiment-coupled workloads |
| `APP-10` | Large-scale AI and LLM training/inference workload models |
| `APP-11` | Quantum/Ising applications and classical baselines |

### Cross-cutting additions

| ID | Topic |
|---|---|
| `CROSS-08` | University infrastructure-center status, refresh plans, and constraints |
| `CROSS-09` | Joint procurement, joint investment, and staged deployment |
| `CROSS-10` | HPCI operating organization, responsibility, and workforce |
| `CROSS-11` | Domestic technology sovereignty, deployment, and industrial impact |
| `CROSS-12` | Center-specific adoption profiles and migration feasibility |
| `CROSS-13` | Multi-scenario system-plan generation, comparison, and presentation |
| `CROSS-14` | Data and service continuity across compute generations |
| `CROSS-15` | Resource ownership, funding, and charging models |
| `CROSS-16` | Geographic placement, electricity, and facility proximity |
| `CROSS-17` | AI-proposed emerging research topics |
| `CROSS-18` | Broad and continuing research of the technology ecosystem developed in Japan |

Detailed Japanese questions, expected evidence, outputs, source references, and cadence are in `config/research-baseline.json`. The review method and inheritance map are in `fs2-fs3-corpus-review.md` and `topic-inheritance.md`.

## Coverage rule

A roadmap research cycle is not coverage-complete merely because every row has search results. Each active topic must declare monitored source classes, languages, time window, last successful query, failed retrievals, and known gaps. Topics may be marked `not-started`, `partial`, `reviewed`, or `retired`; only a human-approved baseline change may use `retired`.

## AI proposal lane

`CROSS-17`, `OFS-004`, and `MON-EMERGING-TOPICS-001` keep discovery open beyond historical FS scope. A candidate must state its novelty relative to all current Topic IDs, cite at least two Origin Groups, include a falsification query, and pass the `research_topic` Consensus Gate before additive promotion. The accepted Topic and Query Plan are registered in `MON-AUTO-TOPICS-001` so other agents can research it in later Runs. See `ai-topic-promotion.md`.

`CROSS-18`, `OFS-005`, `MON-JP-TECH-001`, and `config/domestic-technology-scope.json` require broad discovery of technologies developed in Japan. Named organizations and current products are only seeds; agents must also search pre-commercial research, startups, standards, software, facilities, supply chains, negative results, and previously unknown categories.

## Known limitations

The official FY2022-FY2025 corpus has now been reviewed, but the FS1.0 final report remains unavailable in the registered corpus. Center profiles, current procurement plans, workload telemetry, scenario weights, and one separately supplied FS3 proposal still require additional handling or approval. See `gap-register.md` and `OFS-002`.
