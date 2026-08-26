# HPCI University-Center Baseline

## Planning rule

An HPCI-wide plan is evaluated against each participating center, not an abstract average center. FS2.0 interviews showed different priorities for current users, growth, strategic fields, performance, cost, power, heterogeneity, software support, and refresh timing. Those historical statements are discovery evidence; current center profiles require current primary sources and review.

## Minimum profile

Each `center-profile` must record:

| Field | Examples of evidence | Planning use |
|---|---|---|
| Users | allocation statistics, project mix, interviews | capacity, capability, interaction, and support demand |
| Priority domains | center strategy, adopted projects | application and benchmark portfolio |
| Current system | official specifications and topology | migration baseline and coexistence |
| Refresh window | procurement notices and support dates | phasing and joint procurement |
| Power | contracted power, measured system power | feasible node count and scheduling |
| Facility | floor, cooling, electrical, construction limits | deployment feasibility and cost |
| Budget | public budgets, business plans, and budget requests | affordability, phasing, and lifecycle-cost bounds |
| Procurement | tender notices, specifications, awards, and contract periods | executable acquisition timing and supply assumptions |
| Software | compiler, scheduler, library, portal, license inventory | continuity, support, and lock-in |
| Operations | staffing, service levels, incident model | operational feasibility |
| Migration | code, data, user, and workflow dependencies | time, cost, and transition risk |
| Data connectivity | SINET, DTN, storage, instruments, external access | federation and workflow feasibility |

## Initial center scope

The historical FS2.0 RIKEN reports are discovery evidence, but the operational scope is anchored to `config/hpci-center-registry.json`. That registry is dated, cites the current official HPCI provider page, and includes every organization currently listed there as a compute-resource provider. A Run snapshots the registry so later organizational changes cannot silently alter its declared scope.

`MON-HPCI-CENTERS-001` expands separate discovery Work Items for every registered provider. Query execution coverage and profile evidence completeness are different measurements: finding a provider page proves that a search was attempted, not that power, facility, users, software, or refresh constraints are known. OpenFS must not assume that every center wants the same hardware mix or software policy.

The published FY2026 comparison baseline is
`knowledge/public/hpci-system-inventory.json`. It records the systems and nominal
specifications shown in the official HPCI architecture map and annual resource
list. Its `annual-call-availability` windows indicate the period addressed by the
FY2026 project call only. They are not evidence of procurement, formal service
start, guaranteed uptime, migration, retirement, or refresh timing. Those facts
remain separate Center Profile fields and require current provider primary
evidence.

Center Profile proposal contract `0.3.0` adds `budget` and `procurement` because
`GAP-BLUE-003` cannot be evaluated from power and facility fields alone. Historical
`0.2.0` proposals remain valid records; the public assurance projection marks the
two absent fields as `not-collected` instead of treating them as complete or
retroactively rewriting the old Run.

## Freshness and unknowns

- System, procurement, power, and refresh fields are stale after 90 days unless a reviewed monitor rule sets a shorter period.
- A recurring Run may retain a stronger preceding field only while its cited Evidence is still within that freshness limit. It must record the predecessor profile hash, inherited field names, and the original Evidence bundles.
- A same-cycle observation of equal or greater evidentiary strength replaces the inherited field. Search omission alone does not erase still-current Evidence, and inheritance never changes provisional content into accepted content.
- Strategy and organization fields are checked at least annually and upon a public change.
- Every profile carries an `evidence_as_of` date, evidence references, unknowns, and status.
- A scenario cannot claim nationwide coverage while a required center profile is missing or stale; it must list the uncovered centers.
