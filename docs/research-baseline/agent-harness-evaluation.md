# AI agent and harness evaluation contract

AI-agent results are properties of a complete configuration, not a model name.
OpenFS therefore records the exact model release, harness repository and commit,
prompt, tool set, skill set, evaluator, task set, budget, and execution policy for
every evaluation. Each component is versioned or represented by a SHA-256 digest.

Candidate evaluations use `schemas/agent-evaluation-bundle.schema.json`. The
contract requires at least three runs with unique identifiers and repetitions. It
records outcome scores and policy compliance together with trace, artifact,
token, time, and cost evidence. Dynamic-web evaluations must pin a retrieval time
and receipt bundle so that web drift is not mistaken for agent improvement.

Security claims are fail-closed. Review-candidate evaluations must be
unprivileged and cannot use direct outbound network access. Network-disabled,
brokered public-web, and managed-browser runs are distinct modes. Write roots,
credential policy, enforcement evidence, and secret-scan success are explicit;
container use by itself is not treated as proof of isolation.

Holdout and contamination controls depend on the benchmark. A formal protocol
may require a hidden test partition and an evaluator from an Origin Group
independent of the author. Public benchmarks should be paired with private
OpenFS-specific tasks to detect overfitting, but hidden task contents and answers
must never be committed to the public repository.

`tools/check_agent_evaluation_bundle.py` recomputes mean outcome, policy pass
rate, total token use, and cost, then checks budgets, timestamps, boundary rules,
holdout requirements, evaluator independence, and Consensus state. A passing
bundle is only a candidate for independent review. It does not prove safety,
generalization, or suitability for publication.

Every run must pass the declared policy checks. Outcome quality cannot compensate
for a permission, information-boundary, or network-policy failure.
