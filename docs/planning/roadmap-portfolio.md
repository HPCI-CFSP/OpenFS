# Roadmap portfolio derived from the research catalog

## 1. Purpose

OpenFS separates two structures that answer different questions.

- A research Topic defines what evidence must be collected and evaluated.
- A roadmap integrates evidence from multiple Topics into a time-ordered decision artifact for HPCI planning.

Creating one roadmap for every Topic would produce 58 fragmented timelines with repeated dependencies. The initial portfolio therefore groups the current 58 Topics into 19 integrated roadmap families. Every Topic must be referenced by at least one family, and a Topic may support more than one family when it is genuinely cross-cutting.

The machine-readable source of truth is [`config/roadmap-portfolio.json`](../../config/roadmap-portfolio.json). Schema validation checks its shape, while repository tests check complete and valid Topic coverage.

## 2. Common roadmap contents

Each published roadmap should contain the following elements.

1. A quarterly timeline from 2026 through approximately 2032. A milestone is assigned to Q1-Q4 only when an official source supports that timing; otherwise it remains in the applicable year's “quarter not specified” column.
2. Separate vendor, standards-body, research, and deployment lanes where their timing differs.
3. The distinction among observed availability, standard release, vendor target, research concept, and timing not publicly available.
4. Dependencies on other roadmaps, HPCI center constraints, uncertainties, and decision gates.
5. Source links, an as-of date, an artifact commit, research coverage status, and Consensus Gate status.
6. Multiple HPCI adoption options rather than a single prediction.

## 3. Portfolio by research catalog

| Domain | Integrated roadmap | Principal catalog Topics | Decision output |
|---|---|---|---|
| Hardware | Compute nodes, processors, and accelerators | ARCH-01, 02, 09-13 | Node candidates and performance, power, portability gates |
| Hardware | Memory hierarchy and data movement | ARCH-03, 08, 10 | Memory hierarchy candidates and bandwidth, latency, capacity gates |
| Hardware | Interconnect, optics, and disaggregation | ARCH-04, 05, 08, 09 | Fabric topology and latency, bandwidth, failure-domain gates |
| Hardware | Storage and data platforms | SSW-05, 13; CROSS-03, 14 | Tier placement, retention, transfer, and migration gates |
| Hardware | Facility, power, and cooling | ARCH-06; SSW-15; CROSS-16 | Site limits and construction, commissioning gates |
| Hardware | Supply chain, technology sovereignty, and lifecycle | ARCH-07, 10, 11; CROSS-09, 11, 15 | Procurement risks, maintenance horizon, and alternatives |
| System software | Performance portability, compilers, and automated optimization | SSW-01, 02, 04, 08, 10; APP-05; ARCH-13 | Porting paths and performance, reproducibility criteria |
| System software | Communication, runtimes, scheduling, and operating systems | SSW-03, 06, 11; CROSS-03 | Federated execution model and compatibility gates |
| System software | Data, AI, and experimental workflow platform | SSW-05, 09, 13, 16; APP-03, 06 | Reference workflows and interoperability gates |
| System software | Observability, performance engineering, and power-aware operations | SSW-07, 15; CROSS-02; ARCH-08, 09 | Observability standards and performance, power SLOs |
| System software | Identity, security, and federated operations | SSW-12, 14; CROSS-04 | Trust boundaries and security acceptance criteria |
| Applications | Scientific workloads, benchmarks, and performance models | APP-01, 02, 08; ARCH-08, 09; CROSS-02 | Representative suite and prediction-quality gates |
| Applications | AI for Science and scientific AI agents | APP-03-06, 10; SSW-09, 16 | Reference uses and compute, data, safety requirements |
| Applications | Urgent, real-time, experimental, and quantum applications | APP-09, 11; CROSS-05; SSW-16 | Service levels and pilot-to-production gates |
| Applications | Workforce, adoption, and software sustainability | APP-07; SSW-08; CROSS-10 | Skills, support, maintenance, and readiness plan |
| Cross-cutting | HPCI reference blueprint and center adoption | CROSS-01, 08, 12; ARCH-01, 05, 06, 10 | Center profiles and standardization, exception gates |
| Cross-cutting | Procurement, joint investment, and deployment scenarios | CROSS-06, 09, 13, 15 | Alternative investment and phased deployment scenarios |
| Cross-cutting | Integrated operations, governance, and service continuity | CROSS-03, 04, 07, 10, 14 | Operational transition, accountability, and continuity gates |
| Cross-cutting | Technology horizon scanning and new Topic discovery | CROSS-17, 18; ARCH-07, 11 | Signals, new Topic proposals, and Consensus Gate decisions |

## 4. Recommended sequence

### P0: establish the planning backbone

Continue the published memory roadmap and next create compute nodes, interconnect, scientific workload, performance portability, storage/data, center blueprint, facilities, runtime, workflow, security, procurement scenarios, integrated operations, and horizon-scanning roadmaps. These determine the core architectural choices and expose dependencies early.

### P1: deepen feasibility and adoption

Add supply-chain and lifecycle analysis, observability and power-aware operations, real-time and quantum-linked applications, and workforce and sustainability. These turn technically plausible configurations into deployable and operable plans.

### Continuous maintenance

The horizon-scanning roadmap runs weekly. Product-intensive roadmaps should normally be reviewed monthly, and integrative or institutional roadmaps quarterly or semiannually. New Topics proposed by agents do not enter this portfolio until the Topic Consensus Gate and promotion workflow complete.

## 5. Publication boundary

The portfolio is a harness planning artifact, not a publication approval. A roadmap appears on GitHub Pages only after its evidence, bilingual public export, declared coverage, Consensus status, and human publication Directive satisfy the publication policy. Planned roadmap rows must never be presented as completed research results.
