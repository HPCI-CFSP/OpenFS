# Privacy-preserving workload-observation contract

`GAP-WORK-001` cannot be resolved from machine peak specifications or project
application limits. HPCI planning needs observed distributions of workload type,
job scale, wall time, queue wait, memory, accelerator use, data movement, and job
outcome across centers. Those observations can expose users and research activity
if job rows or small cells leave the operating institution.

Candidate public aggregates use
`schemas/workload-observation-summary.schema.json`. Aggregation occurs inside an
approved boundary. The public proposal contains only coded institution, system,
and Origin Group IDs plus digest receipts. It excludes direct identifiers,
job-level rows, free text, raw paths, and raw-data locations. Counts use a declared
rounding base, cells below ten are suppressed, and at least one complementary cell
is suppressed whenever small-cell suppression occurs so totals cannot reveal the
hidden value by subtraction.

`tools/check_workload_observation_summary.py` verifies the minimum 28-day window,
institution and Origin Group diversity, required dimensions, ID uniqueness,
rounding, cell-size thresholds, complementary suppression, interval bounds, and
publication-state consistency. Schema validation also prevents undeclared fields
from carrying sensitive content.

A successful check is only `candidate_ready_for_consensus`. It does not show that
all 15 HPCI providers are covered, that bins are scientifically representative,
or that data may be published. Every summary remains provisional until independent
review and Consensus pass and a human publication Directive names the artifact.
