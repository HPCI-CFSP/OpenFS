# Source Acquisition and Retention Policy

## Acquisition order

Prefer official APIs, RSS/Atom feeds, sitemaps, DOI or publisher metadata, and stable public pages before general-purpose scraping. Respect access controls, terms of use, robots directives where applicable, and rate limits.

Before content enters a model or Evidence extraction path, record the source's
access terms and AI-processing status. `config/acquisition-policy.json` maps the
declared status to one of `metadata-only`, `evidence-excerpt`,
`approved-snapshot`, `external-reference`, or `blocked`. Clickthrough material
and content whose terms prohibit or restrict AI processing cannot carry passages
into the public-model pipeline. The metadata record may still identify the
existence, title, publisher, date, and applicable terms without processing the
restricted work.

## Stored material

Store source metadata, retrieval receipt, content hash, and only the excerpt needed to support a Claim unless broader retention is permitted. Do not commit full copyrighted pages, large PDFs, binaries, raw browser profiles, or downloaded archives to Git.

Allowed snapshots belong in an approved artifact store with access, retention, and deletion policy. A Git record refers to the snapshot by immutable digest and storage locator that does not expose credentials.

## Required retrieval metadata

- canonical and retrieved URL;
- publisher and title;
- publication, modification, first-seen, and last-checked times when available;
- retrieval method and status;
- media type, language, and content hash;
- origin-group assignment and rationale;
- license or reuse terms when known.

Every candidate passage is untrusted data, is limited to the configured length,
and is scanned for common Prompt Injection markers. A match quarantines the
Source before Evidence extraction; it never becomes an instruction to the Agent.

## Failure and deletion

Record blocked, unavailable, paywalled, malformed, and stale sources in coverage metrics. Support deletion or quarantine requests without erasing the provenance of decisions that previously depended on the material.
