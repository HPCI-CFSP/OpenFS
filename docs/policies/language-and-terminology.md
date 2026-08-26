# Language and Terminology Policy

OpenFS publishes Japanese and English content as two views of the same research
record. Both versions must communicate the same scope, evidence limits,
uncertainties, and publication status. A translation must not add confidence,
remove a caveat, or narrow the meaning of the other language.

## Japanese

- Use established Japanese technical terms when they are clear to the intended
  reader. Retain official product names, standard names, acronyms, API names, and
  titles of external sources.
- Explain OpenFS contract terms in Japanese at first use. Public pages should use
  reader-facing expressions such as `未確認事項`, `調査項目`, `調査モニター`,
  `センタープロファイル`, and `合意判定` instead of unexplained internal
  English labels.
- Distinguish observed facts, published targets, OpenFS interpretations, and
  OpenFS proposals through explicit wording. Avoid sentence fragments when a
  complete sentence is practical.
- Translate ordinary prose rather than mixing English words into a Japanese
  sentence. Do not translate identifiers, code, units, or proper names merely to
  satisfy this rule.

## English

- Use concise, complete sentences with an explicit subject when the actor or
  evidentiary basis matters.
- Prefer established HPC, standards, and procurement terminology. Define an
  OpenFS-specific contract term before relying on it in reader-facing text.
- Preserve the same distinctions among observation, target, interpretation,
  recommendation, and unresolved evidence that appear in Japanese.

## Source of truth

- Store reusable term definitions and technology comparisons only in
  `knowledge/public/roadmap-reference-data.json`.
- Keep paired public fields in the same structured object with `_ja` and `_en`
  suffixes. Do not maintain equivalent paragraphs independently in several page
  templates.
- Treat `README.md` and `README.ja.md` as a synchronized pair and preserve their
  matching `i18n-section` structure.
- Do not rewrite external titles or immutable provenance records. Correct an
  immutable record through a superseding artifact when necessary.

Run `python3 tools/check_public_language.py` before publication. The check rejects
missing language pairs, known wording defects, and selected unexplained internal
terms in Japanese public fields. Human review remains necessary for context,
technical accuracy, and natural prose.
