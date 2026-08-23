# Canonical Claim status events

This directory is an append-only audit log for terminal canonical Claim status.
Do not delete or edit a canonical Claim to correct a published knowledge view.

Create a human Directive under `reviews/directives/` with:

- `directive_type: canonical-status`;
- status `approved` or `completed`;
- exactly one Claim ID in `claim_targets`;
- `canonical_status_action: withdrawn` or `superseded`;
- a public, reviewable `canonical_status_reason`;
- `replacement_claim_id` for `superseded` only; and
- `public_information_confirmed: true`.

Then run:

```console
python3 tools/record_claim_status.py \
  --claim-id CLM-000001 \
  --directive-ref reviews/directives/DIR-000001.json \
  --recorded-by promotion-agent
```

The command pins the canonical Claim and Directive digests, writes one immutable
event, and regenerates `knowledge/claims/index.json` and `TBD.md`. It never
publishes to GitHub Pages and never deletes the original record.
