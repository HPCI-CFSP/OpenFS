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

Run `python3 tools/check_performance_model_card.py <card.json>` before review. The
tool recomputes absolute and relative errors, checks units and thresholds, detects
calibration leakage, and checks declared diversity minima. A zero exit status means
only `candidate_ready_for_consensus`; the tool deliberately returns
`gap_remains_open: true`. Gap closure still requires the explicit closure plan,
independent Consensus, and the applicable human decision.
