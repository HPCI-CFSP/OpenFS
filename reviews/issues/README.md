# Issue payloads

Open Exceptions can be converted into sanitized GitHub Issue payloads with
`tools/prepare_exception_issues.py`. Payloads exclude raw Web content and raw
error messages, carry a stable deduplication marker, and remain `prepared` until
an authorized publisher records the resulting GitHub Issue number and URL.

Open Exceptions are grouped by exception kind, unmet requirements, and publication
blocking state. The group marker remains stable when later Runs encounter the same
owner action, while the payload retains every Run, Exception ID, and repository
record reference. This prevents recurring Consensus-capacity or policy failures
from creating one Issue per Run.
When the same marker already exists on GitHub, the publisher updates its title and
sanitized body only when they changed, so later Run references become visible
without opening a duplicate Issue.
