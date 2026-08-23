# Model and Prompt Change Policy

A change to model family, model version, reasoning configuration, prompt profile, Skill, tool, retrieval connector, or consensus threshold can change research outcomes and is therefore versioned.

Before promotion to the recurring workflow:

1. run the Golden evaluation set;
2. run the Adversarial set, including shared-error and prompt-injection cases;
3. replay representative prior Runs;
4. compare correctness, abstention, disagreement, citation fidelity, latency, and cost;
5. document regressions and the approval decision.

Aliases that can move between model versions must be recorded with the resolved model identity available at execution time. A change can be rolled back without rewriting prior Run records.
