# Claim Acceptance Policy

## Unit of review

A Claim is the smallest statement that can be supported or refuted independently. It must include a stable ID, statement, claim kind, temporal scope, evidence IDs, and source-lineage IDs.

## Claim kinds

- `observed_fact`: an event, measurement, publication, product, or status observed by a stated date.
- `reported_claim`: a statement attributed to a named organization or person but not independently verified.
- `forecast`: a future expectation with a source and forecast horizon.
- `interpretation`: an inference from accepted claims.
- `recommendation`: a proposed HPCI action evaluated under Recommendation Governance.

## Acceptance requirements

- Every factual element is supported by a cited evidence excerpt.
- Time, geography, configuration, units, and comparison baseline are present when material.
- Source lineage is known well enough to avoid duplicate-origin counting.
- Derivative Sources declare a canonical origin URL different from their own URL; reprints, summaries, translations, derived analyses, and shared-dataset views from that origin count once.
- Identical retrieved-content hashes cannot be assigned to separate Origin Groups within one Run.
- Publisher authority is known well enough to prevent one organization or Web authority from masquerading as independent corroboration through multiple pages.
- At least one accepted assessment verifies citation entailment and temporal validity.
- The configured quorum is met and no unresolved critical objection remains.

An authoritative source can support a fact about its own action, publication, or specification. It does not by itself independently validate comparative performance, market impact, or future success.

## Change and withdrawal

Claims are append-only records. Corrections create a separately reviewed and
promoted Claim. An approved human `canonical-status` Directive then records a
terminal `superseded` event linking the old Claim to the replacement. A
`withdrawn` event is used when no accepted replacement exists. Both actions
require an explicit public reason and preserve the original Claim, Proposal,
Decision, and Evidence digests. They remove the old Claim from active generated
views but do not grant GitHub Pages publication authority. Withdrawn or
superseded Claims remain addressable and trigger review of dependent Findings,
Roadmap Items, and report statements.
