# Runs

Each Run has `runs/<run-id>/manifest.json`. The manifest pins the base commit,
Policy and Monitor hashes, budget, Directives, Work Item IDs, execution records,
query receipts, and terminal metrics needed for replay and audit.

`changes.json` compares Sources with the prior completed Run for the same Task and
Monitor. A prior URL omitted from the current search is recorded as `not-observed`,
not as withdrawn or unavailable; only an explicit retrieval result can establish
an availability change.

Large retrieval artifacts are not stored here. Run records refer to approved
external artifacts by digest.
