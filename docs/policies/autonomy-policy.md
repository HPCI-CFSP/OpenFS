# Autonomy Policy

## Level A: automatic

Schema checks, deduplication, content hashing, retrieval-state updates, non-semantic index generation, and validated low-risk bookkeeping may complete automatically.

## Level B: automatic with notification

New public-source proposals, provisional findings, changed-source impact analysis, and ordinary promotion pull requests may proceed automatically when all configured controls pass. They appear in the Weekly Digest.

## Level C: human decision required

Human review is required for NDA export, information-boundary changes, high-impact HPCI recommendations, policy or quorum changes, unresolved critical objections, legal uncertainty, security incidents, and destructive or externally publishing actions.

Every automated operation has a budget, retry limit, idempotency key, and cancellation path. An expired human response must not silently become approval unless a specific low-risk policy defines that behavior.
