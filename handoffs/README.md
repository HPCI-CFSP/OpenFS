# Agent handoffs

A distributed Worker branch contains exactly the Work Item's declared outputs and
`handoffs/<run-id>/<work-item-id>.json`. The Handoff binds those outputs to their
digests, the pinned Run base, the registered Agent identity, and reported usage.

Agents do not commit Queue or Run manifest mutations. After the output pull
request is merged, a trusted orchestrator validates and accepts the Handoff with
`tools/accept_handoff.py`, then commits the resulting control-state update on a
separate maintainer-authorized coordination branch.
