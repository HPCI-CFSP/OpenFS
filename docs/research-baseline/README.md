# OpenFS Research Baseline

## Purpose

This directory defines the initial research inventory that OpenFS agents use when creating Tasks and Monitors. It is a starting scope derived from the currently supplied FS3.0 and FugakuNEXT-era public materials, not a claim that the research scope is complete or authoritative.

An agent may add candidate topics when new evidence appears. It must not silently remove, merge, or narrow an existing topic. Such changes require a reviewed Directive and a recorded rationale showing whether the topic is inherited, revised, split, merged, or retired.

The machine-readable source of truth is `config/research-baseline.json`. This document is the human-readable view.

## How agents use the baseline

1. Select one or more `topic_id` values when creating a Task or Monitor.
2. Convert the listed research questions into source-class and query families.
3. Preserve the expected evidence and output fields in the work item.
4. Record uncovered topics and failed source classes in coverage results.
5. Propose additions or changes through `OFS-002`; do not edit the baseline as incidental research output.
6. Keep vendor claims, measured results, forecasts, interpretations, and HPCI recommendations separate.

If no baseline topic fits, use `OFS-002` to propose a new topic before starting recurring collection. A one-off exploratory Task may proceed only with an explicit human Directive.

## Initial topic catalog

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

## Coverage rule

A roadmap research cycle is not coverage-complete merely because every row has search results. Each active topic must declare monitored source classes, languages, time window, last successful query, failed retrievals, and known gaps. Topics may be marked `not-started`, `partial`, `reviewed`, or `retired`; only a human-approved baseline change may use `retired`.

## Known limitation

The initial public catalog was derived from the four documents listed in `source-corpus.md`. The FS1.0 and FS2.0 final reports and deliverables were not present in the supplied corpus, and one supplied FS3 proposal awaits a public-classification decision. Therefore, inherited, revised, and retired topics from those studies have not yet been verified. See `gap-register.md` and `OFS-002`.
