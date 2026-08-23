# Pilot Run approvals

This directory stores human review records used only to decide whether a Monitor
has completed its required manual calibration Runs. A passing record does not
accept a Claim, Finding, Recommendation, scenario, or report.

Create one `RUN-<ID>.json` record through a reviewed pull request after inspecting
the final Run manifest and generated review Brief. Record their stable digests and
all six checks defined by `schemas/run-approval.schema.json`. The readiness gate
counts only completed Pilot Runs whose coverage, temporal integrity, research
Consensus, digests, and human checks all pass. Editing a Run or Brief after review
invalidates the record automatically.
