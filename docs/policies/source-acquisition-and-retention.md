# Source Acquisition and Retention Policy

## Acquisition order

Prefer official APIs, RSS/Atom feeds, sitemaps, DOI or publisher metadata, and stable public pages before general-purpose scraping. Respect access controls, terms of use, robots directives where applicable, and rate limits.

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

## Failure and deletion

Record blocked, unavailable, paywalled, malformed, and stale sources in coverage metrics. Support deletion or quarantine requests without erasing the provenance of decisions that previously depended on the material.
