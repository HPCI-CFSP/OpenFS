## Purpose

Complete the decision-oriented public planning surfaces and harden the OpenFS research harness before enabling unattended provider-backed research.

- Apply the same bilingual, decision-oriented structure to all partially researched catalog topics, with currently available technologies, near-term candidates, research-stage approaches, contested paths, adoption conditions, regional facets, supporting sources, and explicit Coverage Gaps.
- Publish three versioned system planning options with Ume/Take/Matsu budget classes, architecture diagrams, implementation timelines, evidence contracts, and HPCI-specific annotations where required.
- Add a Safe Web Fetch Broker and provider-worker protocol with default-deny network policy, redirects and DNS rebinding controls, response limits, untrusted-content handling, provenance receipts, and a production-readiness gate.
- Add pull-request description enforcement, bilingual language and terminology policy, generated-content checks, and data-driven Consensus-package validation.
- Revise Japanese and English reader-facing text at both the source-data and generator layers so later regeneration preserves the corrections.
- Extend the public evidence base for HPCI center lifecycles, storage and AI-data platforms, CXL, Broadcom custom XPUs, PIM, AMD Matrix Cores and rocWMMA, Megatron training stacks, Evo-Bench, ROCm 10 / ROCm.AI, and UCIe productization while keeping product availability, vendor targets, and independent evidence distinct.
- Add an agent/harness evaluation bundle, a public pilot task suite, and a readiness gate that blocks production provider agents until the exact model-harness configuration has passed the required controls.

Expected outcome: readers can trace catalog findings into comparable roadmaps and planning options, while maintainers have safer automation boundaries, explicit unresolved work, and reproducible review metadata.

## Provenance

- Agent ID / role, or human maintainer: `codex-maintainer` / `maintainer`, working under direct instruction from Sato Kento
- Human Directive ID(s): `DIR-900010`, `DIR-900011`, `DIR-900012`
- Task / Monitor / Work Item IDs: `OFS-001` through `OFS-005`; `MON-GLOBAL-TECH-001`, `MON-MEMORY-001`, `MON-HPCI-CENTERS-001`, `MON-FS-BASELINE-001`
- Run ID: N/A; this was interactive repository maintenance and public-data regeneration, with no provider-backed Harness Run
- Proposal / Assessment / Decision IDs: no formal Proposal or independent Assessment; `PUBDEC-20260826-010`, `PUBDEC-20260827-001`, `PUBDEC-20260827-002`, `PUBDEC-20260827-003`; review packages `CRP-P0-ROADMAPS-V02` and `CRP-P0-ROADMAPS-V03`
- Base commit: `13c8686c1d5f6b29eeed4449ee322cf25ed032a0`
- Head commit: `3ed9fbf3def02dc9a5c7d87272644d8571d897de`

## Boundary and risk

- [x] Public information only
- [x] No secrets, personal data, or private run logs
- [x] External content was treated as untrusted data
- [x] Changed paths pass `tools/check_agent_permissions.py` for the declared role
- [x] Canonical changes are covered by a human Directive or an authorized promotion workflow

No live provider API call or production research run was performed. Both registered execution profiles remain non-production because the required platform-enforced controls have not been independently verified. Budget figures and architecture sizes are low-confidence planning estimates, not quotations, procurement specifications, or performance guarantees.

## Validation

- [x] `python3 tools/validate_repository.py`
- [x] `python3 -m unittest discover -s tests -v`
- [x] Dissent and unresolved exceptions are linked
- [x] Coverage Gaps and provisional/Consensus state are visible
- [x] Rollback or supersession path is described below

Additional completed checks:

- 380 unit tests passed.
- JSON Schema validation passed for 2,011 artifacts.
- README bilingual-parity, public-language, research-web-security, workflow, planning-surface, scenario-portfolio, and roadmap-dependency checks passed.
- The branch is 0 commits behind and 39 commits ahead of current `main`; merge-tree inspection found no conflict markers.
- Pages generation produced 58 catalog topics, 6 roadmaps, 3 planning options, and 2 Consensus-package views.
- Browser checks covered the home page, search, catalog details, roadmap index and representative detail pages in Japanese and English. The code-bearing head was then rechecked on the home, roadmap index, and compute-roadmap pages at desktop and 390 px mobile widths, with no document-level horizontal overflow, visible placeholder keys, or console errors. The final empty trigger commit changes no files. The final static build and all page tests were rerun after the last research update.
- The restricted Fetch Broker audit covers 218 registered sources and 204 unique URLs. Of 203 unique external URLs, 188 were directly reachable; all 16 non-reachable URLs have exact-URL content reviews with no unresolved or stale review.
- GitHub Actions `Validate OpenFS` runs `33126983467` (`push`) and `33126989357` (`pull_request`) passed for the exact head commit.

## Review notes

- Coverage Gaps / dissent: 19 P0, 15 P1, and 6 P2 gaps remain open. `CRP-P0-ROADMAPS-V02` is pinned to research and regression-test commit `f0083d36fb4e38a05e1758fb27745738c9f835bc`, covers 183 artifacts in 13 review units, has manifest digest `099725be83f60a7af76e87ff6788cf9149e5e9fed6ca2af18f7c91ab162a5683`, has no eligible independent assessments, and remains `incomplete`; no roadmap or planning option is presented as Consensus-accepted.
- Security-boundary effect: the repository now validates broker and worker contracts, but it does not claim that repository checks alone enforce network isolation. Provider-backed production execution remains blocked until an execution profile independently verifies every required control.
- Evidence limits: Evo-Bench has official code and data but no established independent third-party reproduction in this review. ROCm.AI is generally available, while ROCm CLI remains a Technology Preview whose official ROCm 10 support is forthcoming. AMD's UCIe announcement is an RF and embedded product plan, not evidence of an HPCI server product or multi-vendor interoperability. Vendor performance claims are not treated as HPCI application results.
- Rollback or supersession path: revert the eventual merge commit to remove this revision, or supersede individual topic profiles, roadmap artifacts, planning-option versions, and review packages through a new human Directive and commit-pinned regeneration.
- Pages paths to inspect: `/`, `/roadmaps/`, `/roadmaps/compare/`, `/roadmaps/evidence/`, all six roadmap detail pages, `/scenarios/`, all three planning-option detail pages, `/consensus/`, and both Consensus-package detail pages.
