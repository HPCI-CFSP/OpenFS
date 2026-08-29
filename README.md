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
  -> Roadmaps and system planning options
  -> Reports
```

<!-- i18n-section: status -->

## Status

This repository currently provides the Phase 0 design baseline, a replayable pilot of the end-to-end public-web research workflow, deterministic Consensus Gate logic, a controlled path for promoting AI-proposed research topics, the official inventory of FY2022-FY2025 FS reports, a deterministic generator for multiple system planning options, a review-gated path for promoting claims into canonical data, and a deployed bilingual GitHub Pages site.

The first six provisional roadmaps use a common format and cover compute, memory, interconnect, performance portability, scientific workloads, and the HPCI reference blueprint. The public site provides quarterly detail views and a cross-roadmap comparison. Scheduled provider-backed research and production report generation are not enabled; their workflows remain disabled by default until the repository owner completes the documented readiness drills.

The first implemented research workflow, `OFS-001`, repeatedly investigates memory-hierarchy candidates for HPCI in the 2030s. `OFS-002` maintains the FS-derived research baseline. `OFS-003` uses a dated HPCI provider registry and center profiles with field-level public evidence to build center-aware planning options. `OFS-004` promotes AI-proposed research topics accepted by the Consensus Gate, and `OFS-005` continuously surveys worldwide technology trends while prioritizing coverage of technologies developed in Japan.

<!-- i18n-section: core-principles -->

## Core principles

- Public OpenFS contains public information only. NDA information remains in RiVault or another approved private environment.
- A model vote is not evidence. Model independence and source-origin independence are evaluated separately.
- Accepted knowledge is traceable from a report sentence back to claims, evidence excerpts, sources, runs, agents, prompts, and policies.
- External web pages, documents, issues, and pull-request text are untrusted data, never instructions.
- Research agents propose. Independent agents assess. Deterministic code decides whether the configured quorum is met. Only the promotion workflow may update canonical data.
- Canonical Claims are immutable. Human-authorized withdrawal or supersession adds a digest-pinned status event and changes generated active views; it never deletes history.
- Facts, forecasts, and HPCI recommendations are different object types and pass different review gates.
- Routine processing is automated. Humans receive digests and intervene for exceptions, high-impact recommendations, policy changes, or the transfer of NDA information between approved environments.
- Public-web discovery, anonymous read-only retrieval, local shell execution, dependency installation, and GitHub publication are separate capabilities. Repository rules do not prove network isolation; unattended production research remains disabled until a verified execution profile passes `python3 tools/check_research_web_security.py --require-production-profile`.

<!-- i18n-section: repository-map -->

## Repository map

| Path | Purpose |
|---|---|
| `AGENTS.md` | Common rules for Codex and other repository agents |
| `docs/agent-onboarding.md` | First-run checklist, stop conditions, and role routing |
| `docs/architecture.md` | End-to-end architecture, states, and trust boundaries |
| `docs/policies/` | Human-owned decision and governance rules |
| `docs/policies/language-and-terminology.md` | Bilingual writing, terminology, and single-source rules for public content |
| `docs/security/research-web-security-model.md` | Web-research capability boundaries, deployment controls, and residual risks |
| `docs/tasks/` | Research tasks and their expected outputs |
| `docs/research-baseline/` | Human-readable FS-derived topic catalog, source corpus, and known gaps |
| `docs/planning/` | University-center inputs, multi-scenario generation, and presentation rules |
| `docs/publication/` | GitHub Pages activation and public-output boundaries |
| `docs/operations/` | Owner setup, pilot activation, and recurring-operation procedures |
| `config/` | Machine-readable agent, monitor, budget, consensus, and dated HPCI provider-scope settings |
| `config/execution-security-profiles.json` | Declared platform controls and production-eligibility evidence; no current profile is eligible |
| `schemas/` | JSON Schemas for durable research artifacts |
| `skills/` | Versioned discovery, extraction, synthesis, validation, and falsification procedures pinned into each run |
| `evals/` | Golden-path, adversarial, and replay evaluation cases |
| `tools/` | Deterministic validation and consensus commands |
| `tests/` | Tests for deterministic harness behavior |
| `proposals/` | Agent-produced candidates; not canonical data |
| `assessments/` | Independent reviews of proposals |
| `decisions/` | Machine-generated consensus decisions |
| `data/` | Accepted canonical source, evidence, and finding records |
| `knowledge/` | Promoted canonical claims, append-only status events, and generated active views |
| `knowledge/public/roadmaps/` | Human-approved bilingual public roadmap exports using one common schema |
| `knowledge/public/roadmap-reference-data.json` | Single bilingual source for roadmap terminology and decision-oriented comparison tables |
| `knowledge/public/hpci-system-inventory.json` | FY-specific public HPCI resource and machine-specification baseline; call availability is distinct from system lifecycle |
| `knowledge/public/application-performance-forecasts.json` | EEA1 multi-scale forecast contract, readiness matrix, and validated numerical forecasts when available |
| `knowledge/public/source-catalog-map.json` | Generated exact-URL map to canonical Topics, roadmap families, and roadmap tracks |
| `config/catalog-taxonomy.json` | Canonical six-category assignment and public display code for every active Topic and roadmap; Pages filters are generated from this file |
| `config/source-watch-registry.json` | Stable recurring official pages to monitor and their affected Topics, roadmaps, and Monitors |
| `roadmaps/` | Scenario-based roadmap drafts and accepted versions |
| `reports/` | Generated report drafts and exports |
| `reviews/` | Human directives, digests, exceptions, dissent, and commit-pinned Consensus review packages |
| `runs/` | Immutable run manifests and run-scoped outputs |
| `state/` | Watermarks and resumable scheduler state |

Directories that do not yet contain implemented behavior are documented in `docs/architecture.md` and will be added when the corresponding workflow is implemented. `config/skill-registry.json` deterministically selects and snapshots the procedure for each supported work-item kind.

<!-- i18n-section: research-baseline -->

## Research baseline

New research tasks and monitors should select topics from `config/research-baseline.json`. `FSBASE-002` preserves 60 canonical Topic IDs: the protected 30-topic initial catalog, 27 additions from all 26 PDFs linked by MEXT for FY2022-FY2025, and three human-requested additions for worldwide technology monitoring, agentic-workload CPU and node architecture, and LLM inference serving. Six Topics have been retired with explicit successor lineage because their concerns were merged into another Topic or moved into the Harness or planning outputs; 54 active Topics appear on Pages. `config/catalog-taxonomy.json` assigns each active Topic and every roadmap to exactly one of six public categories and gives active Topics category-based public display codes without changing canonical IDs.

The manually maintained Watch Registry separates recurring official index and release pages from exact evidence documents. `tools/build_source_catalog_map.py` generates the URL-to-Topic/Roadmap/Track map from registered public evidence. A changed Watch page is only a signal: a semantic change must be confirmed in an exact primary source and pass the applicable Consensus Gate before publication. Emerging-topic discovery can be initiated daily by `.github/workflows/emerging-topic-discovery.yml`; it remains fail-closed until the reviewed pilot, security-profile, budget, and Consensus-capacity gates are ready.

OpenFS research is worldwide. `config/global-technology-scope.json` requires regionally broad discovery, review of sources in their original languages where feasible, and comparison across international alternatives. Technologies developed in Japan receive priority search coverage so that domestic research, startups, standards, prototypes, and supply-chain capabilities are not overlooked; origin alone is not an adoption criterion.

The FS1.0 record and current primary evidence for every HPCI center remain incomplete. AI agents may propose additional topics through `OFS-004`; independent review, the Consensus Gate, and deterministic promotion are required, and the automated path cannot remove or modify existing topics.

<!-- i18n-section: local-validation -->

## Local validation

Dependency-free structural validation runs first. Full Draft 2020-12 instance
validation, GitHub Actions YAML validation, and their unit tests use the exact
versions in `requirements-validation.txt`.

```bash
python3 -m pip install --requirement requirements-validation.txt
python3 tools/validate_repository.py
python3 tools/check_research_web_security.py
python3 tools/check_public_language.py
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
still requires a human Directive that has been reviewed and approved. For every
roadmap unit, each reviewer must record a conclusive primary-source check against
the commit-pinned artifacts. See
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

The public site supports Japanese and English. Its roadmap library separates hardware, system software, application, and cross-cutting outlooks into a searchable index, evidence-constrained quarterly detail pages, and a six-roadmap comparison of key milestones, primary-source coverage, coverage gaps, and dependencies. Year-only and half-year timing is shown as a Q1-Q4 or two-quarter uncertainty window, not as an invented quarter or event duration. Where generations materially affect a decision, a source-backed OpenFS synthesis appears above standards-body and vendor lanes; generations may overlap, and open-ended bands do not invent a replacement date. The initial display extends at least through approximately 2032, and later dated evidence automatically extends the detail and comparison columns. Relevant terms open centrally maintained definitions and supporting sources, while high-value choices across memory, compute, integration, interconnect, portability, and evaluation are presented in common comparison tables. The reference-blueprint detail page also compares the FY2026 public HPCI resource inventory and nominal machine specifications, explicitly separating annual call availability from service lifecycle. The workload detail page maps six EEA1 applications to reference scales equivalent to 1, 4, 32, 128, 1,024, and about 10,000 Fugaku nodes and displays low-confidence provisional numerical forecasts derived from public information. Until calibration and independent validation are complete, these forecasts cannot support procurement evaluation or performance guarantees. Repository administrators activate deployment once through **Settings → Pages → GitHub Actions** and the `OPENFS_PAGES_ENABLED=true` repository variable. Publication of any roadmap, reference data, public supplement, scenario, or report requires a matching human-approved directive with the `publication-approval` action. See `docs/publication/github-pages.md`.

Research automation is not enabled yet. Provider accounts, GitHub settings, and the sequence of three manual pilot runs are documented in `docs/operations/automation-setup.md`; API keys alone do not activate the loop.

The repository now includes a policy-enforcing Safe Web Fetch Broker and a review-only Provider Worker workflow for the OpenAI and Anthropic APIs. Their presence does not make unattended research production-ready: the execution profile, provider-side spending limits, owner attestations, enabled Monitors, and reviewed pilot runs must still pass the aggregate readiness gate.

Before unattended public-web research is enabled, a platform owner must verify managed search, safe anonymous fetch, DNS and redirect SSRF protection, shell socket isolation, separate dependency egress, and restricted GitHub publication. The current repository profiles intentionally fail the production-profile check until that enforcement evidence exists; see `docs/security/research-web-security-model.md`.

<!-- i18n-section: human-directions -->

## Human directions

Humans add asynchronous instructions through either:

- a GitHub Issue labeled `research-directive`; or
- a reviewed directive file under `reviews/directives/`.

Each directive is linked to the work items, runs, and decisions that process it.

<!-- i18n-section: license -->

## License

OpenFS project-authored material is licensed under the [Apache License 2.0](LICENSE). `NOTICE` identifies the project attribution, and `THIRD_PARTY_NOTICES.md` explains that linked reports, citations, trademarks, datasets, and other third-party works are not relicensed by OpenFS.
