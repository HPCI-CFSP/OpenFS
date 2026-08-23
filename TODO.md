# TODO

## Phase 0: design contracts

- [x] Define the architecture and trust boundaries.
- [x] Define Claim and Source Lineage as first-class records.
- [x] Separate evidence, claim, finding, and recommendation gates.
- [x] Add initial consensus, autonomy, source-retention, model-change, and NDA-export policies.
- [x] Add Golden and Adversarial evaluation fixtures.
- [x] Add a deterministic consensus-gate prototype and repository validation.
- [x] Add an initial FS-derived research baseline with explicit source and coverage gaps.
- [x] Register and review all 26 official FY2022-FY2025 FS2.0/FS3.0 PDFs while preserving the initial 30 topics.
- [x] Add center-profile and multi-scenario contracts plus deterministic Markdown/JSON view generation.
- [x] Add worldwide technology-horizon scope with priority coverage for Japan and a weekly coverage monitor.
- [x] Add additive AI Topic proposal, Consensus, promotion, and Work Item expansion flow.
- [x] Add a GitHub Pages-ready public view and guarded deployment workflow.
- [x] Document license options and adopt Apache-2.0 for project-authored material.
- [x] Add Japanese/English switching and bilingual publication validation to GitHub Pages.
- [x] Require a matching human publication Directive before a scenario or report reaches Pages.
- [x] Document repository-owner setup and the three-Run automation activation sequence.
- [ ] Add full JSON Schema Draft 2020-12 instance validation; the current validator checks structure and JSON syntax only.
- [x] Select and add the Apache-2.0 project license.
- [ ] Review institutional copyright and contribution authority before accepting external contributions.
- [ ] Confirm repository visibility and member access policy.
- [ ] Confirm the authoritative HPCI evaluation criteria and their owners.

## Phase 1: Git collaboration harness

- [ ] Add GitHub Issue templates and the `research-directive` label.
- [x] Add first-run Agent onboarding and default-deny role/path permissions.
- [x] Enforce registered Agent branch permissions during pull-request validation.
- [x] Add trusted-base PR path enforcement that does not execute proposed checker code.
- [ ] Implement Directive ingestion and schema validation.
- [ ] Implement Run and Work Item creation with leases and idempotency keys.
- [ ] Configure branch protection, CODEOWNERS, and required status checks.
- [ ] Add immutable action SHAs and an approved-action policy.

## Phase 2: proposal and independent assessment

- [ ] Implement source discovery and evidence extraction skills.
- [ ] Implement source-lineage grouping and duplicate-origin detection.
- [ ] Implement blind validator and falsification roles.
- [ ] Resolve agent independence groups from the registry rather than trusting assessment input.
- [ ] Calibrate consensus thresholds on reviewed evaluation cases.
- [x] Add the official FS2.0 and FY2025 FS3.0 report set and map inherited and added research topics.
- [ ] Add the missing FS1.0 final report and map inherited, revised, and retired research topics.
- [ ] Complete current primary-source profiles for every in-scope HPCI center.
- [ ] Exercise the AI-proposed emerging-topic monitor through three manual runs.

## Phase 3: canonical promotion

- [ ] Implement Decision-to-canonical promotion.
- [ ] Implement dependency invalidation for updated or withdrawn sources.
- [ ] Generate indexes and `TBD.md` from accepted records.
- [ ] Promote reviewed center profiles and generate the first evidence-backed HPCI scenario set.
- [ ] Add promotion pull requests and rollback support.

## Phase 4: recurring autonomous loop

- [ ] Enable the first weekly monitor after three successful manual runs.
- [ ] Add retry, dead-letter, budget, and kill-switch handling.
- [ ] Generate Weekly Digests and exception Issues.
- [ ] Process asynchronous human directives in the next or an ad-hoc run.
