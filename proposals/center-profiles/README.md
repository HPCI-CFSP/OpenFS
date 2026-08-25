# Center Profile Proposals

`RUN-*/CENTER-*.json` files are provisional, field-level profiles created from Evidence bundles. They do not become accepted planning inputs merely because every field is present. Each non-unknown field names its Evidence, and independent review plus Consensus remains required before promotion.

When a recurring Run inherits a stronger still-current field, `predecessor` pins the
prior profile and lists the inherited fields. `evidence_bundle_refs` and
`evidence_run_ids` keep the original Evidence traceable across Runs. Repository
validation fails if the predecessor digest changes or an inherited field no longer
matches its declared source profile.

New proposals use contract `0.3.0` and include `budget` and `procurement` alongside
the original ten fields. Older `0.2.0` proposals are immutable historical records;
their missing fields must be queued as unknown work, never inferred or backfilled
without a new Run and Evidence.
