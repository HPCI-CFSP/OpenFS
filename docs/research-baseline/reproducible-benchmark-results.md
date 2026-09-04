# Reproducible benchmark-result contract

`GAP-COMP-004`, `GAP-MEM003`, `GAP-PORT-004`, `GAP-PORT-006`, and the
measurement side of `GAP-WORK-003` require comparable experimental evidence.
A benchmark name, peak number, vendor chart, or one successful run is not enough.

Candidate campaigns use `schemas/benchmark-result-bundle.schema.json`. One bundle
pins a workload version, input digest, scale, numerical precision, correctness
tolerance, protocol digest, raw-data digest, and every compared hardware/software
environment. It records individual runs before aggregates so the validator can
recompute medians. At least two configurations, two institutions, two independent
Origin Groups, and three valid repetitions per configuration are required.

The generic three-run minimum is a reusable floor, not a sufficient EEA1 campaign.
The EEA1 profile is defined once in
`knowledge/public/application-performance-forecasts.json` under
`common_benchmark_campaign`: it references `ACCPROTO-EEA1-001`, requires five valid
runs per configuration, and binds all six application criteria to all three system
planning options. A result meeting only the generic floor does not complete an EEA1
campaign stage.

`tools/check_benchmark_result_bundle.py` applies Gap-specific checks. Compute and
memory comparisons require energy and failure/recovery trials. Portability
comparisons require code and effort records. MPI comparisons require at least two
implementations, two fabric providers, and failure trials. The tool also checks
timestamps, correctness thresholds, reference integrity, and aggregate arithmetic.

A successful check means only `candidate_ready_for_consensus`. It does not prove
national workload representativeness, procurement availability, or independent
reproduction, and it never closes a Coverage Gap. Raw results remain provisional
until independent reviewers reproduce them and the applicable Consensus and human
decision gates pass.
