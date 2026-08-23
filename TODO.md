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

- [x] Add a GitHub Issue template for the `research-directive` intake path.
- [x] Add first-run Agent onboarding and default-deny role/path permissions.
- [x] Enforce registered Agent branch permissions during pull-request validation.
- [x] Add trusted-base PR path enforcement that does not execute proposed checker code.
- [x] Implement structured Directive ingestion with public-boundary confirmation and stable provenance.
- [x] Implement Pilot Run and Work Item creation with leases, expiry recovery, idempotency keys, retries, dead-letter exceptions, and a kill switch.
- [ ] Configure branch protection, CODEOWNERS, and required status checks.
- [x] Enforce immutable action SHAs in every workflow.

## Phase 2: proposal and independent assessment

- [x] Add versioned, Run-pinned Skills for worldwide and general Discovery, Evidence extraction, synthesis, validation, and falsification.
- [ ] Connect provider-backed discovery and extraction Skills; deterministic Source registration, Rights Gate, Prompt Injection quarantine, and Evidence extraction are implemented.
- [x] Implement source-lineage grouping and duplicate-origin detection.
- [x] Implement blind validator and falsification roles.
- [x] Resolve agent independence groups from the registry rather than trusting assessment input.
- [ ] Calibrate consensus thresholds on reviewed evaluation cases.
- [x] Add the official FS2.0 and FY2025 FS3.0 report set and map inherited and added research topics.
- [ ] Add the missing FS1.0 final report and map inherited, revised, and retired research topics.
- [ ] Complete current primary-source profiles for every in-scope HPCI center.
- [ ] Exercise the AI-proposed emerging-topic monitor through three manual runs.

## Phase 3: canonical promotion

- [x] Implement Decision-to-canonical promotion for accepted non-Recommendation Claims.
- [ ] Extend canonical promotion to Findings and reviewed Center Profiles.
- [x] Generate dependency-impact promotion blocks for changed or unavailable Sources without treating search omission as withdrawal.
- [x] Enforce unresolved dependency-impact blocks in Claim promotion.
- [ ] Generate indexes and `TBD.md` from accepted records.
- [ ] Promote reviewed center profiles and generate the first evidence-backed HPCI scenario set.
- [ ] Add promotion pull requests and rollback support.

## Phase 4: recurring autonomous loop

- [x] Add a production-readiness gate for reviewed manual Runs, budget approval, policy calibration, and independent Consensus capacity.
- [ ] Enable the first weekly monitor after three successful manual runs.
- [ ] Complete production cost accounting and provider-side budget enforcement; local retry, dead-letter, Work Item limits, and the repository kill switch are implemented.
- [x] Generate Weekly Digests and grouped exception Issues through a variable-gated, low-privilege review workflow.
- [ ] Process asynchronous human directives in the next or an ad-hoc run.
