---
name: structured-synthesis
description: Synthesize assigned Evidence bundles into an atomic Claim or field-level Center Profile proposal while preserving uncertainty and lineage.
---

# Structured Synthesis

Use only the Evidence bundles and predecessor inputs pinned in the leased Work Item.
Every factual field or Claim must cite supporting Evidence IDs and retain its time
scope. Distinguish observed fact, vendor claim, forecast, interpretation, and
recommendation. Conflicting Evidence stays visible; missing Evidence yields
`unknown`, not a guessed value.

For a Claim, use `tools/propose_claim.py` and keep the statement atomic. For a Center
Profile, use `tools/propose_center_profile.py`; inherited fields must retain the
predecessor digest and original Evidence and remain provisional. Write only the
declared proposal path. A synthesis agent never accepts its own proposal, changes
evaluation weights, or publishes a recommendation.
