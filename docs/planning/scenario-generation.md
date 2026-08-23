# HPCI System Scenario Generation

## Purpose

OpenFS must produce several feasible HPCI development plans, not one model-authored answer. Each scenario binds architecture, system software, applications, center impacts, domestic technology, evidence, uncertainty, and decision gates into one reviewable object.

## Inputs and trust

1. Use accepted Sources, Claims, Findings, and Roadmap Items. Provisional inputs must be labeled and cannot silently support an accepted recommendation.
2. Load a current `center-profile` for every center in scope. Missing fields remain visible and reduce the scenario's readiness; they are not filled by inference from another center.
3. Load the human-owned criteria and weights in `config/scenario-policy.json`. When any weight is `null`, the tool displays an unranked comparison.
4. Include domestic technology candidates found by RIKEN, Kobe, Keio, Tohoku, and later primary sources. Evaluate maturity, software, production, maintenance, and fallback.

## Generation loop

1. Build constraint envelopes for each center and the HPCI-wide workload portfolio.
2. Generate at least three meaningfully different options. Vary investment objective, resource composition, service model, timing, and risk posture rather than only changing labels.
3. Reject an option that omits architecture, system software, applications, center impacts, domestic technology, uncertainties, or decision gates.
4. Have independent agents challenge workload coverage, center feasibility, vendor or model bias, missing domestic technology, migration cost, and correlated evidence.
5. Run sensitivity analysis only after a human-approved weight set exists. Preserve conditions under which an option becomes preferable or infeasible.
6. Promote candidate scenarios only through the Recommendation Gate and a human-approved Directive.

## Deterministic view generation

The generator validates scenario count and required sections, normalizes the evaluation matrix, and emits the same scenario set as reviewable Markdown and structured JSON.

```bash
python3 tools/generate_scenario_views.py \
  --input evals/scenarios/candidate-scenarios.json \
  --policy config/scenario-policy.json \
  --output-markdown /tmp/openfs-scenarios.md \
  --output-json /tmp/openfs-scenarios.json
```

The committed example set is illustrative test data, not an HPCI recommendation. Production inputs belong in the proposal/review/promotion flow, and only the promotion role writes `roadmaps/` or `reports/`.
