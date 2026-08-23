# Canonical knowledge

This directory contains only promoted, traceable knowledge records. Research
agents write Proposals under `proposals/`; they cannot write here.

`claims/` is populated by `tools/promote_claim.py` only after an accepted Decision
under a calibrated Run-pinned Consensus Policy. Each canonical Claim pins the
digests of its Proposal, Decision, Evidence bundles, and checked dependency-impact
reports. Recommendation Claims are excluded from this automatic path.

Do not edit a promoted record in place. A correction creates a new reviewed
Proposal and a superseding append-only record.

`claims/index.json` and the repository-root `TBD.md` are deterministic generated
views. `tools/promote_claim.py` refreshes both in the same operation;
`python3 tools/generate_knowledge_views.py` may be used for deterministic repair.
The generator never reads Proposal or provisional Decision directories as
standalone knowledge.
