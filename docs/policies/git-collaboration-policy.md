# Git Collaboration Policy

- The default branch is protected; agents do not push directly to it.
- Proposal branches use `agent/<agent-id>/<run-id>/<work-item-id>`.
- A distributed Agent branch is an assignment envelope: exactly the Work Item's
  declared outputs plus one digest-bound Handoff. Queue and Manifest updates are
  excluded to avoid shared-file conflicts between Agent branches.
- Automated identities must use the `agent/` namespace; using a human branch name to bypass role checks is prohibited.
- One Proposal ID owns one primary artifact path. Shared indexes are generated after merge.
- Discovery, extraction, validation, and synthesis jobs cannot edit canonical paths.
- Consensus decisions are generated from immutable proposal and assessment revisions.
- Promotion pull requests list Decision IDs, source commit, generated paths, validation results, and rollback instructions.
- API-key-bearing model jobs have read-only repository permissions. A separate credential boundary creates branches or pull requests.
- After an output pull request merges, a trusted orchestrator accepts its Handoff
  and batches control-state changes on a separate coordination branch.
- Merge conflicts are resolved from artifact identity and provenance, not by choosing the newest free-form document.

The `Enforce Agent Permissions` check runs trusted base-branch policy code and must be a required branch-protection check. Branch protection, CODEOWNERS, merge queue policy, separate bot identities, and permitted automation identities must be configured before automatic promotion is enabled.
