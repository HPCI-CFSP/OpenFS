# Application-to-system-requirement traceability audit

## Status

- Date: 2026-09-06 JST
- Scope: public information only
- Research status: provisional
- Consensus status: incomplete
- Procurement eligibility: false

## Outcome

The six EEA1 applications are represented by 48 provisional requirement candidates: one
candidate for each application and each of the eight infrastructure dimensions. Every
candidate now has a stable `SYSREQ-EEA1-*` identifier and links to:

1. the public sources supporting its qualitative demand direction;
2. the acceptance metrics that would test the requirement;
3. related measured envelopes, published targets, or measurement-gap records; and
4. the draft application acceptance criterion and system-planning criteria.

Eight quantitative planning records produce bidirectional links to thirteen matrix cells.
The remaining 35 cells intentionally remain qualitative-evidence-only. No missing value was
estimated or promoted to a threshold.

## Decision boundary

A linked quantitative record is supporting evidence, not an adopted system requirement.
Measured node ranges describe where an application has been observed and do not define a
minimum node count, bandwidth, capacity, or performance threshold. The SALMON published
one-second-per-step target remains an unapproved candidate until its workload and accuracy
conditions are accepted by the application owner.

All 48 candidates retain `provisional-owner-approval-required`. They must not be used as
formal procurement requirements until matched-input measurements, application-owner
approval, independent validation, and the Consensus Gate are complete.

## Validation added

The repository validator now rejects:

- duplicate system-requirement IDs;
- links to unknown quantitative records or acceptance metrics;
- links to a different application's evidence;
- evidence-status labels inconsistent with their links; and
- quantitative records without a matching matrix backlink.

The Pages view exposes the stable IDs, evidence class, linked acceptance metrics, and anchors
from each requirement candidate to the corresponding quantitative record.
