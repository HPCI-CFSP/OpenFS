# Research Baseline Gap Register

This register prevents absent material from being mistaken for a completed historical review.

| Gap ID | Missing or unresolved input | Why it matters | Required action | Status |
|---|---|---|---|---|
| `FSBASE-GAP-001` | FS1.0 final report and technical deliverables | The baseline cannot verify which Fugaku-era requirements should be inherited, revised, or retired. | Obtain an authorized copy or official public URL, register its hash and lineage, and map its topics to the catalog. | open |
| `FSBASE-GAP-003` | Authoritative owners and weights for HPCI evaluation criteria | Agents can compare evidence but cannot turn draft criteria into an accountable investment decision. | Record criterion owners, weights or scenario rules, and approval history through a reviewed Directive. | open |
| `FSBASE-GAP-005` | User-needs evidence and workload telemetry coverage | Presentation-level scope does not establish representative demand across all HPCI users. | Define survey, interview, workload-log, and benchmark sampling plans with privacy controls. | open |
| `FSBASE-GAP-006` | Vendor roadmap handling rules and NDA/public reconciliation | Public trend research alone may miss constraints, while NDA content cannot enter public OpenFS. | Use the separate NDA plane and approved export-package protocol for public-safe conclusions. | open |
| `FSBASE-GAP-007` | Public classification of one supplied FS3 proposal document | Its contents and metadata must not enter public OpenFS until redistribution and public handling are confirmed. | Obtain an authorized classification decision; then either register it or retain it only in the approved private plane. | open |

Closing a gap requires source or Directive IDs, a reviewer, date, and resulting baseline version. Agents must not mark gaps closed from inference alone.

## Closed gaps

| Gap ID | Resolution | Evidence | Reviewer / date | Resulting baseline |
|---|---|---|---|---|
| `FSBASE-GAP-002` | Registered and reviewed every PDF on the official FY2022-FY2024 MEXT report pages; created an inheritance map. | `FSBASE-SRC-006` to `FSBASE-SRC-025`; `fs2-fs3-corpus-review.md`; `topic-inheritance.md` | Authorized maintainer execution for user request / 2026-08-23 | `FSBASE-002` |
| `FSBASE-GAP-004` | Registered and reviewed the FY2025 operation-organization, operations/security, RIKEN compute-system, and quantum-hybrid reports. | `FSBASE-SRC-026` to `FSBASE-SRC-031` | Authorized maintainer execution for user request / 2026-08-23 | `FSBASE-002` |
