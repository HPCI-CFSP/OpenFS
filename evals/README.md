# OpenFS Evaluations

OpenFS evaluates the harness, not just individual model answers.

- `golden/` contains reviewed cases with expected policy outcomes.
- `adversarial/` contains correlated-source, shared-model-error, prompt-injection, temporal, and citation-mismatch cases.
- `replay/` records representative prior Runs selected for regression testing.

Model, Prompt, Skill, connector, Schema, or Consensus Policy changes must run the relevant sets before joining the recurring workflow. Track at least false acceptance, false rejection, abstention, citation entailment, source-lineage accuracy, latency, and cost.

The current fixtures verify only the deterministic Phase 0 gate. They are examples, not a calibrated scientific benchmark.
