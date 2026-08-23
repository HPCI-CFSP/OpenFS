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

This repository currently contains the Phase 0 design baseline, the first deterministic consensus-gate prototype, the official FY2022-FY2025 FS report inventory, and a deterministic multi-scenario view generator. Web collection, scheduled agent dispatch, canonical promotion, and production report generation are not enabled yet.

The first vertical slice is `OFS-001`, a recurring investigation of memory hierarchy candidates for HPCI in the 2030s. `OFS-002` maintains the research-scope baseline inherited from FS materials, `OFS-003` builds center-aware multi-scenario plans, and `OFS-004` preserves a reviewed lane for AI-proposed emerging topics.

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
| `docs/agent-onboarding.md` | First-run checklist, stop conditions, and role routing |
| `docs/architecture.md` | End-to-end architecture, states, and trust boundaries |
| `docs/policies/` | Human-owned decision and governance rules |
| `docs/tasks/` | Research tasks and their expected outputs |
| `docs/research-baseline/` | Human-readable FS-derived topic catalog, source corpus, and known gaps |
| `docs/planning/` | University-center inputs, multi-scenario generation, and presentation rules |
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

## Research baseline

New research Tasks and Monitors should select topics from `config/research-baseline.json`. `FSBASE-002` contains 57 topics: the protected 30-topic initial catalog plus 27 additions from all 26 PDFs linked by MEXT for FY2022-FY2025. The additions cover performance limits, RAS, domestic technologies, federated software and data services, center conditions, governance, funding, and scenario presentation.

The FS1.0 record and current primary evidence for every HPCI center remain incomplete. The baseline must not be represented as a complete historical or current HPCI review. AI agents may propose further topics through `OFS-004`, but may not remove the protected initial catalog.

## Local validation

The current validator and tests use the Python standard library only.

```bash
python3 tools/validate_repository.py
python3 -m unittest discover -s tests -v
```

Check whether a research role may write planned paths:

```bash
python3 tools/check_agent_permissions.py \
  --role validator \
  assessments/PRP-CLM-000001/ASM-000001.json \
  runs/RUN-TEST-001/validator-summary.json
```

Run the consensus-gate example:

```bash
python3 tools/consensus_gate.py \
  --proposal evals/golden/accepted-proposal.json \
  --assessments evals/golden/accepted-assessments.json \
  --policy config/consensus-policy.json
```

Render the illustrative multi-scenario example without ranking:

```bash
python3 tools/generate_scenario_views.py \
  --input evals/scenarios/candidate-scenarios.json \
  --policy config/scenario-policy.json \
  --output-markdown /tmp/openfs-scenarios.md \
  --output-json /tmp/openfs-scenarios.json
```

## Human directions

Humans add asynchronous instructions through either:

- a GitHub Issue labeled `research-directive`; or
- a reviewed directive file under `reviews/directives/`.

Each directive will eventually be linked to the work items, runs, and decisions that processed it.

## License

The project license is not yet selected. Until a license is added, the repository is publicly visible but no open-source reuse rights are granted by default.
