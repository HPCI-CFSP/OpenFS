# Runs

Each Run has `runs/<run-id>/manifest.json`. The manifest pins the base commit,
Policy and Monitor hashes, budget, Directives, Work Item IDs, execution records,
query receipts, and terminal metrics needed for replay and audit.

Large retrieval artifacts are not stored here. Run records refer to approved
external artifacts by digest.
