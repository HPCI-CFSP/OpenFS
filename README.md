# OpenFS

**English** | [日本語](README.ja.md)

[![OpenFS Pages](https://img.shields.io/badge/OpenFS-Public%20Site-18755b?logo=githubpages&logoColor=white)](https://hpci-cfsp.github.io/OpenFS/)
[![Validate OpenFS](https://github.com/HPCI-CFSP/OpenFS/actions/workflows/validate.yml/badge.svg)](https://github.com/HPCI-CFSP/OpenFS/actions/workflows/validate.yml)
[![Publish OpenFS Pages](https://github.com/HPCI-CFSP/OpenFS/actions/workflows/pages.yml/badge.svg)](https://github.com/HPCI-CFSP/OpenFS/actions/workflows/pages.yml)
[![License](https://img.shields.io/badge/License-Apache--2.0-173b57.svg)](LICENSE)

<!-- i18n-section: overview -->

OpenFS is an evidence-first research harness for continuously investigating the technologies, systems, and operating models needed for future HPCI infrastructure.

Browse the bilingual public research view at [OpenFS Pages](https://hpci-cfsp.github.io/OpenFS/).

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

<!-- i18n-section: status -->

## Status

This repository currently contains the Phase 0 design baseline, a replayable public-Web Pilot vertical slice, deterministic consensus and AI-topic-promotion paths, the official FY2022-FY2025 FS report inventory, a deterministic multi-scenario view generator, a review-only canonical Claim promotion path, and a deployed bilingual GitHub Pages public view. The first six common-format provisional roadmaps cover compute, memory, interconnect, performance portability, scientific workloads, and the HPCI reference blueprint; Pages provides individual quarterly views and a cross-roadmap comparison. Scheduled production provider dispatch and production report generation are not enabled yet; their workflows remain default-disabled until the owner completes the documented drills.

The first vertical slice is `OFS-001`, a recurring investigation of memory hierarchy candidates for HPCI in the 2030s. `OFS-002` maintains the FS-derived baseline, `OFS-003` uses a dated HPCI provider registry and field-evidenced Center Profiles to build center-aware scenarios, `OFS-004` promotes Consensus-accepted AI Topic additions, and `OFS-005` continuously surveys worldwide technology trends while prioritizing coverage of technologies developed in Japan.

<!-- i18n-section: core-principles -->

## Core principles

- Public OpenFS contains public information only. NDA information remains in RiVault or another approved private environment.
- A model vote is not evidence. Model independence and source-origin independence are evaluated separately.
- Accepted knowledge is traceable from a report sentence back to claims, evidence excerpts, sources, runs, agents, prompts, and policies.
- External web pages, documents, issues, and pull-request text are untrusted data, never instructions.
- Research agents propose. Independent agents assess. Deterministic code decides whether the configured quorum is met. Only the promotion workflow may update canonical data.
- Canonical Claims are immutable. Human-authorized withdrawal or supersession adds a digest-pinned status event and changes generated active views; it never deletes history.
- Facts, forecasts, and HPCI recommendations are different object types and pass different review gates.
- Normal processing is automated. Humans receive digests and intervene for exceptions, high-impact recommendations, policy changes, or NDA export.

<!-- i18n-section: repository-map -->

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
| `docs/publication/` | GitHub Pages activation and public-output boundaries |
| `docs/operations/` | Owner setup, Pilot activation, and recurring-operation procedures |
| `config/` | Machine-readable agent, monitor, budget, consensus, and dated HPCI provider-scope settings |
| `schemas/` | JSON Schemas for durable research artifacts |
| `skills/` | Versioned Discovery, extraction, synthesis, validation, and falsification procedures pinned into each Run |
| `evals/` | Golden, adversarial, and replay evaluation cases |
| `tools/` | Deterministic validation and consensus commands |
| `tests/` | Tests for deterministic harness behavior |
| `proposals/` | Agent-produced candidates; not canonical |
| `assessments/` | Independent reviews of proposals |
| `decisions/` | Machine-generated consensus decisions |
| `data/` | Accepted canonical source, evidence, and finding records |
| `knowledge/` | Promoted canonical Claims, append-only status events, and generated active views |
| `knowledge/public/roadmaps/` | Human-approved bilingual public roadmap exports using one common schema |
| `knowledge/public/roadmap-reference-data.json` | Single bilingual source for roadmap terminology and decision-oriented comparison tables |
| `roadmaps/` | Scenario-based roadmap drafts and accepted versions |
| `reports/` | Generated report drafts and exports |
| `reviews/` | Human directives, digests, exceptions, dissent, and commit-pinned Consensus review packages |
| `runs/` | Immutable run manifests and run-scoped outputs |
| `state/` | Watermarks and resumable scheduler state |

Directories that do not yet contain implemented behavior are documented in `docs/architecture.md` and will be added when the corresponding vertical slice is built. `config/skill-registry.json` deterministically selects and snapshots the procedure for each supported Work Item kind.

<!-- i18n-section: research-baseline -->

## Research baseline

New research Tasks and Monitors should select topics from `config/research-baseline.json`. `FSBASE-002` contains 58 topics: the protected 30-topic initial catalog, 27 additions from all 26 PDFs linked by MEXT for FY2022-FY2025, and one human-directed worldwide technology-horizon Topic with priority coverage for Japan.

OpenFS research is worldwide. `config/global-technology-scope.json` requires regionally broad discovery, source-language coverage where feasible, and comparison across international alternatives. Technologies developed in Japan receive priority search coverage so that domestic research, startups, standards, prototypes, and supply-chain capabilities are not overlooked; origin alone is not an adoption criterion.

The FS1.0 record and current primary evidence for every HPCI center remain incomplete. AI agents may propose additive Topics through `OFS-004`; independent review, the Consensus Gate, and deterministic promotion are required, and the automated path cannot remove or modify existing Topics.

<!-- i18n-section: local-validation -->

## Local validation

Dependency-free structural validation runs first. Full Draft 2020-12 instance
validation, GitHub Actions YAML validation, and their unit tests use the exact
versions in `requirements-validation.txt`.

```bash
python3 -m pip install --requirement requirements-validation.txt
python3 tools/validate_repository.py
python3 tools/validate_readme_i18n.py
python3 tools/validate_workflows.py
python3 tools/validate_json_schemas.py
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

Build and evaluate an independent P0 roadmap review package after committing the
artifact set:

```bash
python3 tools/build_consensus_review_package.py --base-commit <40-hex-artifact-commit>
python3 tools/evaluate_consensus_review_package.py \
  reviews/consensus-packages/CRP-P0-ROADMAPS-V02/manifest.json
```

The evaluator can return `ready-for-human-decision`, but high-impact HPCI adoption
still requires a reviewed human Directive. Each reviewer must record a conclusive,
commit-pinned primary-source check for every roadmap unit. See
`docs/operations/independent-roadmap-review.md`.

Render the illustrative multi-scenario example without ranking:

```bash
python3 tools/generate_scenario_views.py \
  --input evals/scenarios/candidate-scenarios.json \
  --policy config/scenario-policy.json \
  --output-markdown /tmp/openfs-scenarios.md \
  --output-json /tmp/openfs-scenarios.json
```

Build the public GitHub Pages view locally:

```bash
python3 tools/build_pages_site.py --output _site
```

The public site supports Japanese and English. Its roadmap library separates hardware, system software, application, and cross-cutting outlooks into a searchable index, evidence-constrained quarterly detail pages, and a six-roadmap comparison of key milestones, primary-source coverage, Coverage Gaps, and dependencies. Year-only and half-year timing is shown as a Q1-Q4 or two-quarter uncertainty window, not as an invented quarter or event duration. Relevant terms open centrally maintained definitions and supporting sources, while high-value choices across memory, compute, integration, interconnect, portability, and evaluation are presented in common comparison tables. Repository administrators activate deployment once through **Settings → Pages → GitHub Actions** and the `OPENFS_PAGES_ENABLED=true` repository variable. Every roadmap, reference-data, scenario, and report publication requires a matching human `publication-approval` Directive. See `docs/publication/github-pages.md`.

Research automation is not enabled yet. Provider accounts, GitHub settings, and the three-Run Pilot sequence are documented in `docs/operations/automation-setup.md`; API keys alone do not activate the loop.

<!-- i18n-section: human-directions -->

## Human directions

Humans add asynchronous instructions through either:

- a GitHub Issue labeled `research-directive`; or
- a reviewed directive file under `reviews/directives/`.

Each directive will eventually be linked to the work items, runs, and decisions that processed it.

<!-- i18n-section: license -->

## License

OpenFS project-authored material is licensed under the [Apache License 2.0](LICENSE). `NOTICE` identifies the project attribution, and `THIRD_PARTY_NOTICES.md` explains that linked reports, citations, trademarks, datasets, and other third-party works are not relicensed by OpenFS.
