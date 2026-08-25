# Workload observation proposals

This directory stores provisional `WOS-*.json` summaries produced by an assigned
`synthesis` Work Item. Each summary must validate against
`schemas/workload-observation-summary.schema.json` and pass
`tools/check_workload_observation_summary.py` before independent review.

Only privacy-reviewed aggregates belong here. Aggregate source data inside its
approved security boundary; export no user identifier, project identifier,
job-level row, command line, path, free text, credential, NDA content, or raw-data
location. Small cells require suppression, complementary cells must also be hidden
to prevent subtraction, and published counts are rounded.

Passing the validator means only that the summary is a Consensus candidate. It
does not establish national representativeness, authorize GitHub Pages release,
or close a Coverage Gap. Publication also requires independent Consensus and an
artifact-specific human publication Directive.
