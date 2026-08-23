# Git Collaboration Policy

- The default branch is protected; agents do not push directly to it.
- Proposal branches use `agent/<agent-id>/<run-id>/<work-item-id>`.
- One Proposal ID owns one primary artifact path. Shared indexes are generated after merge.
- Discovery, extraction, validation, and synthesis jobs cannot edit canonical paths.
- Consensus decisions are generated from immutable proposal and assessment revisions.
- Promotion pull requests list Decision IDs, source commit, generated paths, validation results, and rollback instructions.
- API-key-bearing model jobs have read-only repository permissions. A separate credential boundary creates branches or pull requests.
- Merge conflicts are resolved from artifact identity and provenance, not by choosing the newest free-form document.

Branch protection, required checks, CODEOWNERS, merge queue policy, and permitted automation identities must be configured before automatic promotion is enabled.
