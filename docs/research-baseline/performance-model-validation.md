# Performance model validation contract

`GAP-WORK-003` remains open until published model definitions, inputs, error
criteria, and independently reproducible prediction-versus-measurement data are
available. A release name, chart, model score, or one laboratory's measurements
do not close the Gap.

Candidate models use `schemas/performance-model-card.schema.json`. The card pins
the equation or implementation digest, input and output units, applicability and
exclusions, calibration dataset IDs, holdout measurements, acceptance thresholds,
and execution provenance. Validation datasets must not overlap calibration data.
At least two systems, two workloads, and two independent Origin Groups are required
for a card to become eligible for Consensus review.

The public comparison surface is
`knowledge/public/application-performance-forecasts.json`. It does not normalize
the entire Fugaku system to one scalar. Each EEA1 application is evaluated at the
applicable subset of 1, 4, 32, 128, 1,024, and about 10,000 Fugaku nodes, with
strong scaling, weak scaling, and throughput/ensemble kept distinct. Comparisons
must identify whether they hold node count, CPU or accelerator count, memory
capacity, power, or procurement cost constant. An unsupported scale is recorded
as `calibration-required` or `not-applicable`, not extrapolated silently.

Numerical entries use
`T_pred = T_compute + T_memory + T_communication + T_IO - T_overlap` and report a
lower, base, and upper estimate. Time-to-solution, parallel efficiency,
throughput, energy-to-solution, and a domain-specific rate are primary. Achieved
FLOP/s is only a secondary metric when operation counts are stable for the pinned
code, algorithm, and input and can be reproduced from time-to-solution. Forecasts
remain prohibited for procurement use until their model cards pass independent
validation and Consensus.

Run `python3 tools/check_performance_model_card.py <card.json>` before review. The
tool recomputes absolute and relative errors, checks units and thresholds, detects
calibration leakage, and checks declared diversity minima. A zero exit status means
only `candidate_ready_for_consensus`; the tool deliberately returns
`gap_remains_open: true`. Gap closure still requires the explicit closure plan,
independent Consensus, and the applicable human decision.

Run `python3 tools/check_public_planning_surfaces.py` after changing the public
scale contract, readiness matrix, or forecasts array.
