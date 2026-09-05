# Production readiness preflight

OpenFS separates repository-verifiable controls from settings that exist only in
GitHub or provider accounts. Unattended provider-backed research is default-deny.

Run the aggregate preflight with:

```console
python3 tools/evaluate_operational_readiness.py \
  --output _automation/operational-readiness.json
```

Add `--require-ready` in any future production Worker workflow so a blocked report
stops dispatch. The weekly Coordinator generates the report without that flag and
uploads it for diagnosis; a blocked report must not prevent a manual Pilot plan
from being inspected.

The report checks:

- every scheduled workflow still contains its declared activation variable;
- the Provider Worker workflow and adapter exist and contain the required protocol markers;
- a web-research execution profile has independently verified managed search,
  safe anonymous fetch, SSRF controls, shell socket isolation, separate dependency
  egress, and restricted Git publication;
- at least one recurring research Monitor is enabled and every enabled Monitor
  passes its budget, Consensus-capacity, calibrated-policy, and reviewed-Pilot gate;
- every required external control has a complete, unexpired owner attestation.

For every failed check, the report also emits a deterministic `owner_actions`
entry with a non-secret summary and repository references. The weekly coordination
Issue shows these summaries, while the complete readiness report remains the
workflow artifact. Actions are guidance only: they do not bypass approval or
self-attest an external control.

Component existence is not a filename-only check. The activation policy also
declares a minimum size and required protocol markers. An empty workflow or adapter
stub therefore remains blocked.

`config/activation-policy.json` defines these requirements.
The capability contract and platform profiles are in
`config/research-web-security-policy.json` and
`config/execution-security-profiles.json`; repository validation alone does not
make a profile production-eligible.
`config/owner-controls.json` starts entirely `unverified`. After checking the real
GitHub or provider setting, a human owner may change one control to `verified` and
record `verified_by`, `verified_at`, `expires_at`, and a non-secret evidence
summary. Use a reviewed pull request. Do not record tokens, credentials, private
URLs, secret values, customer identifiers, or screenshots containing them.

Verification is not permanent. Every attestation expires so configuration drift
must be checked periodically. Repository agents may report an expired or failed
control but must not self-attest it as verified.

As of 2026-09-06, production remains intentionally blocked. The review-only
Provider Worker and Safe Web Fetch Broker are present, so the component-existence
checks can pass. However, no execution profile has reviewed evidence for all
required platform controls, recurring research Monitors remain disabled, owner
controls are unverified, the Consensus policy is uncalibrated, the budget lacks
an approved cost ceiling, and no Monitor has completed the required manually
initiated Runs with review approval.
This accurately reflects the current activation boundary; it is not an error in the pilot artifacts.

The roadmap source triage currently records 108 reviewed and exact-URL-confirmed
entries and 84 unresolved entries. Twenty unresolved entries were added with the
four roadmap families published on 2026-09-06; they have not yet been retrieved
through a production-eligible Safe Web Fetch profile. These counts describe the current audit
artifact; they are not evidence that a fresh full scan has run. Do not copy the
84 unresolved entries into confirmed evidence, and do not change their state
without a retrieval receipt plus semantic review.

## Owner activation sequence

Perform the following steps in order. Stop when any check fails.

1. Deploy the network and capability controls described by
   `config/research-web-security-policy.json` in the actual execution environment.
2. Independently verify those controls and update one profile in
   `config/execution-security-profiles.json` with non-secret evidence. A repository
   edit alone does not establish that the controls exist.
3. Verify the six external controls in `config/owner-controls.json` and record
   accountable, expiring attestations without secrets or private screenshots.
4. Confirm the aggregate gate:

   ```console
   python3 tools/check_research_web_security.py --require-production-profile
   python3 tools/evaluate_operational_readiness.py \
     --output _automation/operational-readiness.json --require-ready
   ```

5. Only after both commands pass, set `OPENFS_SECURITY_PROFILE_ID` to that
   production-eligible profile ID in the GitHub Actions environment used by the
   research Worker.
6. Run the full source audit through the Safe Web Fetch Broker, then rebuild the
   triage and review every unresolved or changed entry:

   ```console
   python3 tools/audit_roadmap_sources_via_fetch_broker.py \
     --profile-id "$OPENFS_SECURITY_PROFILE_ID"
   python3 tools/build_roadmap_source_triage.py
   ```

`--offline-reconcile` may be used during repository development to register new
roadmap URLs against earlier exact-URL results. It performs no network request
and must not be reported as a current full refresh.
