# Issue payloads

Open Exceptions can be converted into sanitized GitHub Issue payloads with
`tools/prepare_exception_issues.py`. Payloads exclude raw Web content and raw
error messages, carry a stable deduplication marker, and remain `prepared` until
an authorized publisher records the resulting GitHub Issue number and URL.
