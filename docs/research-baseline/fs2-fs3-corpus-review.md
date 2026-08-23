# FS2.0/FS3.0 Official Corpus Review

## Scope and method

This review covers every PDF linked from the official MEXT FY2022, FY2023, FY2024, and FY2025 report pages as of 2026-08-23: 26 files and 1,554 pages in total.

1. Download each PDF from its official MEXT URL and record SHA-256, page count, fiscal year, team, part, and origin group.
2. Extract layout-preserving text, inspect each table of contents and report structure, and review conclusions and sections matching architecture, software, applications, operation, security, centers, domestic technology, and quantum-HPC terms.
3. Visually inspect representative tables and system diagrams where layout carries meaning, including center interview tables, HPCI-CFSP/HPCI-RB/HPCI-CB, and operation/funding proposals.
4. Map findings to the protected initial 30-topic catalog. Add a topic only when the material creates a separately actionable research question, evidence need, and output.
5. Treat annual parts from the same team as correlated sources and keep report statements as proposed evidence until normal OpenFS review and promotion.

This is a bounded review of the registered corpus, not a claim of exhaustive web research or current validation of every report statement.

## Complete file inventory

| Source | FY | Team / document | Part | Pages | Primary use in this review |
|---|---:|---|---|---:|---|
| `FSBASE-SRC-006` | 2022 | RIKEN system study | Cover / contents | 5 | Scope and part lineage |
| `FSBASE-SRC-007` | 2022 | RIKEN system study | 2 | 122 | Architecture, performance model, HPCI requirements |
| `FSBASE-SRC-008` | 2022 | RIKEN system study | 3 | 46 | System software and applications |
| `FSBASE-SRC-009` | 2022 | Kobe system study | Full report | 36 | Domestic accelerators, RISC-V, DSLs, applications |
| `FSBASE-SRC-010` | 2022 | Keio new computing principles | Full report | 61 | Quantum, annealing, simulators, hybrid use |
| `FSBASE-SRC-011` | 2022 | University of Tokyo operations study | Full report | 37 | Federated operation, storage, identity, workflow |
| `FSBASE-SRC-012` | 2023 | RIKEN system study | Cover / contents | 5 | Scope and part lineage |
| `FSBASE-SRC-013` | 2023 | RIKEN system study | 2 | 56 | HPCI center interviews and architecture needs |
| `FSBASE-SRC-014` | 2023 | RIKEN system study | 3 | 171 | Architecture, software, applications, evaluation |
| `FSBASE-SRC-015` | 2023 | RIKEN system study | 4 | 64 | Roadmap and detailed supporting analyses |
| `FSBASE-SRC-016` | 2023 | RIKEN system study | Appendix | 2 | Appendix lineage |
| `FSBASE-SRC-017` | 2023 | Kobe system study | Full report | 52 | Domestic technology reference architecture |
| `FSBASE-SRC-018` | 2023 | Keio new computing principles | Full report | 103 | Quantum/Ising stack and applications |
| `FSBASE-SRC-019` | 2023 | University of Tokyo operations study | Full report | 56 | Storage, data movement, unified operation |
| `FSBASE-SRC-020` | 2024 | RIKEN system study | Cover / contents | 5 | Scope and part lineage |
| `FSBASE-SRC-021` | 2024 | RIKEN system study | 2 | 270 | Final architecture/software analysis and center survey |
| `FSBASE-SRC-022` | 2024 | RIKEN system study | 3 | 71 | Applications, benchmarks, performance prediction |
| `FSBASE-SRC-023` | 2024 | Kobe system study | Full report | 60 | Final domestic accelerator/CPU/software study |
| `FSBASE-SRC-024` | 2024 | Keio new computing principles | Full report | 40 | Final quantum and annealing study |
| `FSBASE-SRC-025` | 2024 | University of Tokyo operations study | Full report | 72 | Final HPCI operation/data/organization proposals |
| `FSBASE-SRC-026` | 2025 | HPCI planning study | Program structure | 1 | Team boundaries and coordination |
| `FSBASE-SRC-027` | 2025 | University of Tokyo operation organization | Full report | 12 | Coordinating body, ownership, funding, workforce |
| `FSBASE-SRC-028` | 2025 | University of Tokyo operations/security | Full report | 22 | Identity, portals, telemetry, security, workflows |
| `FSBASE-SRC-029` | 2025 | RIKEN compute-system planning | 1 | 70 | Architecture, vendors, HPCI-CFSP/RB/CB |
| `FSBASE-SRC-030` | 2025 | RIKEN compute-system planning | 2 | 30 | System software and application work |
| `FSBASE-SRC-031` | 2025 | Tohoku quantum-hybrid environment | Full report | 85 | Quantum/Ising operation, stack, and applications |

## Cross-report synthesis

### Architecture and evaluation

- Sustained application performance is frequently limited by data movement rather than peak FLOPS. OpenFS must therefore model bandwidth, latency, capacity, communication, storage, scaling mode, and power jointly.
- The plan must cover CPU, GPU, vector, FPGA/dataflow and other accelerators, memory hierarchy, network, storage, packaging, facilities, and RAS as one system. Large-memory AI nodes and high-throughput inference are distinct service needs.
- Application benchmarks, workload logs, performance models, simulators, and what-if exploration are a continuous decision service, not a one-time procurement benchmark.

### System software and operation

- Migration and sustainability span compilers and languages, programming models, communication, numerical libraries, schedulers, containers, cloud/Kubernetes, AI frameworks, autotuning, observability, and support ownership.
- Cross-generation storage and data services require local scratch, shared and archival tiers, DTNs, high-speed transfer, metadata, authorization, and a lifecycle independent of each compute refresh.
- HPCI-wide functions include federated identity and authorization, portals, resource abstraction, meta-scheduling, urgent computing, telemetry, security/privacy, and experiment/instrument workflows.

### Applications and users

- The representative portfolio must include life science, materials, climate and disaster prevention, manufacturing, fundamental science, data assimilation/digital twins, AI for Science, and emerging interactive or streaming work.
- AI/LLM training and inference require explicit memory, topology, I/O, and power models. Quantum/Ising candidates require comparison with improving classical methods and maturity gates.
- Application continuity, porting effort, user support, and scientific productivity are planning criteria alongside raw performance.

### HPCI centers, governance, and domestic technology

- University centers differ in user communities, strategic fields, buildings, power, procurement timing, software policy, operating staff, and appetite for heterogeneity. A single identical configuration is not a sufficient planning model.
- Candidate plans must model joint procurement and investment, HPCI-owned versus center-contributed resources, charging and funding, a coordinating organization, and sustainable technical careers while preserving center autonomy.
- Domestic technologies described by the RIKEN, Kobe, Keio, and Tohoku teams are mandatory research targets. They must be assessed for application value, maturity, software, production, maintenance, supply chain, and fallback options rather than included symbolically.

## Baseline decision

- Retain all 30 `FSBASE-001` Topic IDs unchanged and protect them from silent removal.
- Add 27 separately actionable topics in `FSBASE-002`, including center profiles, domestic technology, data/service continuity, HPCI governance, and scenario presentation.
- Close the registered FS2.0 and related-team-report gaps because the official FY2022-FY2025 corpus is now registered. Keep FS1.0, current center evidence, evaluation ownership, NDA reconciliation, and the unclassified supplied proposal as explicit gaps.
- Keep an AI-originated emerging-topic lane so the historical catalog cannot become a ceiling on future investigation.
