# FS2.0/FS3.0 Topic Inheritance

## Retention rule

`FSBASE-001` is the protected initial catalog. Its 30 IDs remain present even when a later report refines, splits, or overlaps a topic. A future retirement requires a reviewed Directive and Decision; ordinary collection or synthesis agents may only propose the change.

## Source-stream mapping

| Official source stream | Existing Topics retained | Added or separated Topics | Reason for separation |
|---|---|---|---|
| RIKEN FS2.0 architecture and application analysis | `ARCH-01` to `ARCH-07`, `APP-01` to `APP-03`, `CROSS-01`, `CROSS-02`, `CROSS-06` | `ARCH-08` to `ARCH-10`, `ARCH-13`, `APP-08`, `APP-10` | Data-movement limits, scaling modes, RAS, numerical integrity, domain coverage, and AI workloads need distinct evidence and outputs. |
| RIKEN FS2.0 system-software analysis | `SSW-01` to `SSW-09`, `APP-05`, `APP-07` | `SSW-10`, `SSW-13` | Autotuning and cross-generation data lifecycle are recurring decisions beyond generic compiler/storage topics. |
| Kobe FS2.0 domestic system study | `ARCH-01`, `ARCH-07`, `SSW-01`, `SSW-02`, `APP-01` | `ARCH-11`, `ARCH-12`, `CROSS-11` | Domestic processors, dataflow/RISC-V/accelerator paths, and deployment impact require explicit mandatory tracking. |
| Keio FS2.0 new computing-principles study | `CROSS-05` | `APP-11` | Infrastructure integration and application-level advantage against classical baselines are separate questions. |
| University of Tokyo FS2.0 operations study | `SSW-05` to `SSW-07`, `CROSS-03`, `CROSS-04` | `SSW-11` to `SSW-16`, `CROSS-09`, `CROSS-10`, `CROSS-14` to `CROSS-16` | Federation, identity, data lifecycle, security, telemetry, workflow, organization, funding, and placement each have different owners and acceptance evidence. |
| RIKEN FY2025 FS3.0 compute-system plan | `CROSS-01`, `CROSS-02`, `CROSS-06`, `CROSS-07` | `CROSS-08`, `CROSS-12`, `CROSS-13`, `CROSS-17` | HPCI-CFSP requires continuing center evidence, multiple feasible plans, a presentation mechanism, and discovery beyond inherited topics. |
| FY2025 operation organization and security teams | `CROSS-03`, `CROSS-04` | `SSW-11` to `SSW-16`, `CROSS-09`, `CROSS-10`, `CROSS-15`, `CROSS-16` | These reports turn broad integration needs into separable technical, organizational, and financial work. |
| FY2025 Tohoku quantum-hybrid team | `CROSS-05` | `APP-11`, `CROSS-11`, `CROSS-16` | The report adds domestic-stack tracking, application benchmarks, operating constraints, and placement/connectivity questions. |

## Change classes

- **Inherited:** all 30 protected initial Topics remain valid research entry points.
- **Split for actionability:** 26 report-derived Topics separate recurring questions that need their own evidence, cadence, owner, or output.
- **Harness process:** retired Topic `CROSS-17` preserves the origin of the independently reviewed AI-proposal path now implemented by `OFS-004` and `MON-EMERGING-TOPICS-001`.
- **No retirements:** this review does not retire or narrow any initial Topic.

The exact source references for every added Topic are machine-readable in `config/research-baseline.json`.
