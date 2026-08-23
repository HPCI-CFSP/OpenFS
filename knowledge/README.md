# Canonical knowledge

This directory contains only promoted, traceable knowledge records. Research
agents write Proposals under `proposals/`; they cannot write here.

`claims/` is populated by `tools/promote_claim.py` only after an accepted Decision
under a calibrated Run-pinned Consensus Policy. Each canonical Claim pins the
digests of its Proposal, Decision, Evidence bundles, and checked dependency-impact
reports. Recommendation Claims are excluded from this automatic path.

Do not edit a promoted record in place. A correction creates a new reviewed
Proposal and a superseding append-only record.
