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
- At least one accepted assessment verifies citation entailment and temporal validity.
- The configured quorum is met and no unresolved critical objection remains.

An authoritative source can support a fact about its own action, publication, or specification. It does not by itself independently validate comparative performance, market impact, or future success.

## Change and withdrawal

Claims are append-only records. Corrections create a revision linked to the prior Claim. Withdrawn or superseded Claims remain addressable and trigger review of dependent Findings, Roadmap Items, and report statements.
