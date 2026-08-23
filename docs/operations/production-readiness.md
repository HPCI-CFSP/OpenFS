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
- the provider Worker workflow and adapter actually exist;
- at least one recurring research Monitor is enabled and every enabled Monitor
  passes its budget, Consensus-capacity, calibrated-policy, and reviewed-Pilot gate;
- every required external control has a complete, unexpired owner attestation.

`config/activation-policy.json` defines these requirements.
`config/owner-controls.json` starts entirely `unverified`. After checking the real
GitHub or provider setting, a human owner may change one control to `verified` and
record `verified_by`, `verified_at`, `expires_at`, and a non-secret evidence
summary. Use a reviewed pull request. Do not record tokens, credentials, private
URLs, secret values, customer identifiers, or screenshots containing them.

Verification is not permanent. Every attestation expires so configuration drift
must be checked periodically. Repository agents may report an expired or failed
control but must not self-attest it as verified.

As of the initial preflight implementation, production is intentionally blocked:
the provider-backed Worker workflow and adapter are absent, recurring research
Monitors are disabled, owner controls are unverified, the Consensus policy is
uncalibrated, the budget lacks an approved cost ceiling, and no Monitor has its
required reviewed manual Runs. This is a truthful activation boundary, not an
error in Pilot artifacts.
