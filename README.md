# OpenFS

OpenFS is an evidence-first research harness for continuously investigating the technologies, systems, and operating models needed for future HPCI infrastructure.

The project turns a recurring research question into traceable artifacts:

```text
Research task
  -> Sources
  -> Evidence excerpts
  -> Atomic claims
  -> Findings
  -> Roadmap scenarios
  -> Reports
```

## Status

This repository currently contains the Phase 0 design baseline and the first deterministic consensus-gate prototype. Web collection, scheduled agent dispatch, canonical promotion, and automatic report generation are not enabled yet.

The first vertical slice is `OFS-001`, a recurring investigation of memory hierarchy candidates for HPCI in the 2030s.

## Core principles

- Public OpenFS contains public information only. NDA information remains in RiVault or another approved private environment.
- A model vote is not evidence. Model independence and source-origin independence are evaluated separately.
- Accepted knowledge is traceable from a report sentence back to claims, evidence excerpts, sources, runs, agents, prompts, and policies.
- External web pages, documents, issues, and pull-request text are untrusted data, never instructions.
- Research agents propose. Independent agents assess. Deterministic code decides whether the configured quorum is met. Only the promotion workflow may update canonical data.
- Facts, forecasts, and HPCI recommendations are different object types and pass different review gates.
- Normal processing is automated. Humans receive digests and intervene for exceptions, high-impact recommendations, policy changes, or NDA export.

## Repository map

| Path | Purpose |
|---|---|
| `AGENTS.md` | Common rules for Codex and other repository agents |
| `docs/architecture.md` | End-to-end architecture, states, and trust boundaries |
| `docs/policies/` | Human-owned decision and governance rules |
| `docs/tasks/` | Research tasks and their expected outputs |
| `config/` | Machine-readable agent, monitor, budget, and consensus settings |
| `schemas/` | JSON Schemas for durable research artifacts |
| `skills/` | Reusable agent procedures, added as each workflow is implemented |
| `evals/` | Golden, adversarial, and replay evaluation cases |
| `tools/` | Deterministic validation and consensus commands |
| `tests/` | Tests for deterministic harness behavior |
| `proposals/` | Agent-produced candidates; not canonical |
| `assessments/` | Independent reviews of proposals |
| `decisions/` | Machine-generated consensus decisions |
| `data/` | Accepted canonical source, evidence, and finding records |
| `knowledge/` | Accepted findings organized by HPCI technical domain |
| `roadmaps/` | Scenario-based roadmap drafts and accepted versions |
| `reports/` | Generated report drafts and exports |
| `reviews/` | Human directives, digests, exceptions, and dissent |
| `runs/` | Immutable run manifests and run-scoped outputs |
| `state/` | Watermarks and resumable scheduler state |

Directories that do not yet contain implemented behavior are documented in `docs/architecture.md` and will be added when the corresponding vertical slice is built.

## Local validation

The current validator and tests use the Python standard library only.

```bash
python3 tools/validate_repository.py
python3 -m unittest discover -s tests -v
```

Run the consensus-gate example:

```bash
python3 tools/consensus_gate.py \
  --proposal evals/golden/accepted-proposal.json \
  --assessments evals/golden/accepted-assessments.json \
  --policy config/consensus-policy.json
```

## Human directions

Humans add asynchronous instructions through either:

- a GitHub Issue labeled `research-directive`; or
- a reviewed directive file under `reviews/directives/`.

Each directive will eventually be linked to the work items, runs, and decisions that processed it.

## License

The project license is not yet selected. Until a license is added, the repository is publicly visible but no open-source reuse rights are granted by default.
