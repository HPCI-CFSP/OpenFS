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
| Software | compiler, scheduler, library, portal, license inventory | continuity, support, and lock-in |
| Operations | staffing, service levels, incident model | operational feasibility |
| Migration | code, data, user, and workflow dependencies | time, cost, and transition risk |
| Data connectivity | SINET, DTN, storage, instruments, external access | federation and workflow feasibility |

## Initial center scope

The FS2.0 RIKEN reports discuss Hokkaido, Tohoku, Tsukuba, Tokyo, Tokyo Institute of Technology / current successor organization, Nagoya, Kyoto, Osaka, Kyushu, RIKEN, AIST, and JAMSTEC. OpenFS must resolve current names, organizational changes, resource-provider status, and systems from primary sources before accepting profiles. It must not assume that every center wants the same hardware mix or software policy.

## Freshness and unknowns

- System, procurement, power, and refresh fields are stale after 90 days unless a reviewed monitor rule sets a shorter period.
- Strategy and organization fields are checked at least annually and upon a public change.
- Every profile carries an `evidence_as_of` date, evidence references, unknowns, and status.
- A scenario cannot claim nationwide coverage while a required center profile is missing or stale; it must list the uncovered centers.
