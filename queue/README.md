# Work Item Queue

The Run Controller writes one immutable-identity JSON Work Item per file under
`queue/<run-id>/`. Runtime status and leases change in place until a promotion
pull request records the reviewed Run. A repeated Run creation with identical
inputs is idempotent; a reused Run ID with different inputs is rejected.

Queue files are untrusted inputs to role workers. A lease grants temporary
ownership of one Work Item, not broader repository permissions.

Shared-storage Workers use advisory locks and update Queue state locally.
Distributed Git Workers do not commit Queue changes. They submit declared outputs
with a digest-bound Handoff; a trusted orchestrator updates Queue state after merge.
