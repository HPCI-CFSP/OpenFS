# Scheduled research production-readiness checkpoint

## Status

- Date: 2026-09-06 JST
- Research status: provisional
- Consensus status: incomplete
- Production status: blocked by design

## Source-review reconciliation

The roadmap source audit contains 420 source registrations. Of these, 194 have an HTTP
reachability warning. The source-triage artifact previously covered 192 because two sources
added to the reference-blueprint roadmap had not been incorporated into the triage build.

The exact content at both URLs was reviewed on 2026-09-06:

| Source | Verified boundary |
|---|---|
| JAMSTEC FY2026 Earth Simulator Challenge Use call | FY2026 is the final operating fiscal year for the current ES4; the document does not establish the successor configuration or commissioning date. |
| JETRO TSUBAME4.0 procurement notice | The advertised lease runs from 2024-04-01 through 2030-03-31; this is not a successor commissioning date or migration window. |

After deterministic regeneration, all 194 warnings are represented in the triage: 110 have
an exact-URL single-model content check and 84 remain unresolved. These checks are not
independent claim validation and do not satisfy the Consensus Gate.

Primary sources:

- https://www.jamstec.go.jp/es/jp/project/r08ch/R08_Challenge_oubo.pdf
- https://www.jetro.go.jp/gov_procurement/national/articles/256628/2022121400400001.html

## Production preflight

Repository-verifiable workflow gates and required components pass. Unattended research
remains blocked by four aggregate checks:

1. No independently verified, production-eligible Research Web security profile exists.
2. Six external owner controls have not been attested.
3. No recurring research Monitor is enabled.
4. No enabled Monitor has passed the budget, Consensus-capacity, calibrated-policy, and
   reviewed-manual-run gates.

This is the correct fail-closed state. Do not enable a Monitor, set
`OPENFS_SECURITY_PROFILE_ID`, or report a full source refresh until the owner activation
sequence in `docs/operations/production-readiness.md` has been completed.

## Resume point

The next production step belongs to the repository owner or platform administrator: deploy
and independently verify the Safe Web Fetch controls, then record non-secret, expiring
attestations for the external owner controls. Once those checks pass, run the full source audit
through the broker and semantically review the 84 unresolved entries.
