# AI agent and harness evaluation proposals

This directory stores provisional `AEVAL-*.json` bundles produced by an assigned
`synthesis` Work Item. Each bundle must validate against
`schemas/agent-evaluation-bundle.schema.json` and pass
`tools/check_agent_evaluation_bundle.py` before independent review.

The contract records the model and harness as separate versioned components. It
also pins the prompt, tools, skills, evaluator, task set, budgets, execution
boundary, network path, write roots, credential policy, holdout visibility, run
traces, artifacts, token use, elapsed time, and cost. A container or a benchmark
security score is not accepted as proof of network or permission isolation.

Bundles are proposals, not published findings. Do not commit credentials, raw
private traces, NDA material, personal data, or hidden benchmark answers. Store
raw artifacts at the declared immutable URI and commit only their digest. Passing
the deterministic checker only makes a bundle eligible for independent Consensus
review; publication still requires the applicable human decision.
