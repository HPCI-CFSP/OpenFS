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

Prepare a default-deny draft with:

```bash
python3 tools/prepare_run_approval.py --run-id RUN-EXAMPLE-PILOT-001
```

The command pins the final manifest and Brief digests but sets every check to
`false`, leaves the reviewer fields empty, and uses status `draft`. A human reviewer
must inspect the cited artifacts and explicitly complete the record. Agents must not
turn their own draft into `reviewed-pass`.
