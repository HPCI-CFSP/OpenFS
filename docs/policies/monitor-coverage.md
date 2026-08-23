# Monitor Coverage Policy

OpenFS does not claim complete coverage of the Web. Each Monitor declares a measurable search scope and reports what was not observed.

## Required monitor contract

- research task and supported languages;
- required organizations, standards bodies, conferences, journals, and domains;
- source classes and named high-priority sources;
- query families and query-expansion rules;
- cadence and maximum unchecked age;
- retrieval methods and fallback order;
- per-run source, time, and cost limits;
- retry and stopping conditions;
- conditions that produce `coverage_status: incomplete` or an exception.

## Run receipts

Store each query, execution time, retrieval method, result URLs or stable identifiers, rank where available, and failures. The Weekly Digest reports domain coverage, stale sources, failed queries, newly added sources, and scope changes.

Each new failure should declare `coverage_impact` as `blocking` or `warning`.
An unclassified failure is blocking by default. `rights-excluded` is retained as a
non-blocking warning when an evidence-eligible replacement is selected; the Rights
Gate record must still remain in the Run.

Coverage changes are policy-relevant changes. Agents may propose them, but a reviewed Directive or owner approval is required before removing a required source class or monitored organization.
