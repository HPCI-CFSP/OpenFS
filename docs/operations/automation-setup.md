# OpenFS research automation setup

## Current status

As of 2026-08-27, the repository has a Run Controller, leased Work Items,
configuration snapshots, Rights Gate, pinned automatic source-change detection, coverage reporting,
Consensus-capacity preflight, deterministic Consensus decisions, weekly Digests,
review Briefs, sanitized Issue payloads, budgets, stop records, and guarded GitHub
Pages publication. The repository retains 18 auditable Pilot Run manifests across
memory (`OFS-001`), HPCI center (`OFS-003`), and worldwide technology (`OFS-005`)
scopes: 13 completed and five deliberately cancelled while the harness was being
corrected. The latest worldwide Run, `RUN-OFS005-PILOT-010`, completed 49 Work
Items over 16 Sources, met its declared coverage scope, passed temporal-integrity
checks, and produced eight provisional Claim proposals. They remain provisional
because independent provider/model Consensus capacity is not configured; Pilot
completion must not be read as formal research acceptance.

The public roadmap portfolio also has a deterministic Coverage Gap queue at
`knowledge/public/audits/roadmap-gap-queue.json`. It assigns every open Gap to a
specific Monitor or the independent Consensus package. P0 source-discovery items
are scheduled for weekly reconsideration, but the queue records them as
`staged-monitor-disabled` while production readiness is incomplete. The weekly
Review workflow regenerates this assignment artifact, so an open Gap cannot silently
fall out of the review loop merely because it is already visible on GitHub Pages.
The Coordinator includes the selected Monitor's weekly P0 Gap IDs and query-seed
count in its cycle plan. When a Run is created, the Run Controller expands those
seeds into ordinary leased `source-discovery` Work Items, records the originating
Gap on every item, and snapshots the queue beside the other Run inputs. Disabled
Monitors still require an explicit Pilot or a passed production-readiness gate.
P0 query and closure plans are curated in
`config/roadmap-gap-query-overrides.json`. Each P0 source-discovery plan states
the minimum number of independent Origin Groups, requires a Consensus Gate, and
lists concrete bilingual closure criteria. A newly added Gap remains assignable
through deterministic generated query and closure defaults, while the queue
exposes `query_plan_origin`, `closure_plan_origin`, and `closure_state` so reviewers
can replace those defaults with domain-specific contracts. The current 13 P0
source-discovery Gaps all have explicit plans; the fourteenth P0 item is the
Consensus review assignment itself. A responsive result, a source count, or one
model's judgment cannot change an open Gap: every criterion must be verified and
the independent-origin and Consensus requirements must pass.

The weekly **control-plane** schedule is implemented in
`.github/workflows/weekly-coordinator.yml`. It validates the repository and prepares
one deduplicated coordination Issue. It makes no model call, performs no promotion,
and publishes no research result. Provider API clients and an unattended research
Worker are still intentionally disabled. Adding API keys alone does not start paid
research.

## Responsiveness target

The worldwide Monitor has a one-day maximum unchecked interval. This is an
internal operational target, not a promise that every Topic changes every day.
When production execution is enabled, the coordinator should prioritize newly
detected official releases, security corrections, procurement notices, standards
updates, and roadmap changes ahead of routine queries. The fast lane may publish
only a visibly provisional update after source, retrieval, boundary, schema, and
human-publication checks; independent verification and Consensus continue on the
normal lane.

The repository currently provides the weekly control-plane workflow, but the
production worker and verified safe-fetch path remain disabled. Until those gates
pass, the one-day target is a declared service objective rather than an active
unattended guarantee. Public Pages therefore shows the last reflected update,
verification state, and open Coverage Gaps instead of promising a fixed cadence.

The existing roadmap URL audit still uses direct Python HTTP for local development.
The scheduled Review now fails closed before that step and cannot become
production-ready until it is replaced by
`audit_roadmap_sources_via_fetch_broker.py` backed by a verified safe-fetch
service. Registering a profile without changing that execution path is
insufficient.

## Recommended provider arrangement

Use at least two independently administered model-provider paths for formal Consensus:

- OpenAI: public-web discovery and one blind assessment path;
- Anthropic: an independent blind assessment and falsification path.

The roles should be rotated across Runs so that one provider is not permanently the proposer or validator. Two executions of the same model, prompt, and tool configuration count as one independence group. If only one provider is configured, useful proposals may be generated, but they remain `provisional` and cannot pass the formal cross-group quorum.

OpenFS is public-information-only. Provider jobs must never receive NDA, confidential, credential, personal, or unclassified internal material.

## Settings the repository owner prepares

### 1. Provider projects and API keys

Create separate provider projects or workspaces for OpenFS, enable billing, and set provider-side usage limits and alerts. Create least-privilege API keys dedicated to this repository.

Do not put keys in repository files, Issues, Directives, pull requests, or chat. After the Pilot workflow is merged, add these repository secrets at:

**Repository → Settings → Secrets and variables → Actions → Secrets → New repository secret**

| Secret | Purpose |
|---|---|
| `OPENAI_API_KEY` | OpenAI Responses API and public Web search |
| `ANTHROPIC_API_KEY` | Independent Claude assessment and falsification |

Provider references:

- OpenAI API quickstart: <https://platform.openai.com/docs/quickstart/make-your-first-api-request>
- Anthropic API documentation: <https://docs.anthropic.com/en/docs/welcome>

### 2. Repository variables

After the Pilot workflow defines and validates these names, add them at:

**Repository → Settings → Secrets and variables → Actions → Variables → New repository variable**

| Variable | Initial value | Meaning |
|---|---:|---|
| `OPENFS_COORDINATOR_ENABLED` | `false` | Enables scheduled weekly plan/Issue creation only |
| `OPENFS_HANDOFF_CONTROL_ENABLED` | `false` | Enables daily Handoff validation and control-PR preparation |
| `OPENFS_REVIEW_ENABLED` | `false` | Enables weekly internal Digest artifacts and grouped exception Issue updates |
| `OPENFS_PROMOTION_ENABLED` | `false` | Enables reviewed Claim-promotion PR preparation; never auto-merges |
| `OPENFS_RESEARCH_ENABLED` | `false` | Kill switch for provider-calling jobs |
| `OPENFS_SECURITY_PROFILE_ID` | leave unset | Set only to a reviewed `production_eligible` profile after the production security check passes |
| `OPENFS_AUTOMATION_MODE` | `pilot` | Manual Pilot; not weekly operation |
| `OPENFS_MAX_COST_USD` | owner decision | Hard per-Run cost ceiling |
| `OPENFS_MAX_WORK_ITEMS` | `10` | Initial Pilot scope limit; increase only after inspecting the generated plan |
| `OPENFS_OPENAI_MODEL` | owner-approved model ID | Resolved and recorded in the Run manifest |
| `OPENFS_ANTHROPIC_MODEL` | owner-approved model ID | Resolved and recorded in the Run manifest |

Keep `OPENFS_RESEARCH_ENABLED=false` while the runner is absent or while a problem is under investigation. The repository `state/STOP` file is the second kill switch once the Run Controller is implemented.

### 3. GitHub Actions permissions

At **Repository → Settings → Actions → General**:

1. Allow GitHub-authored actions. OpenFS pins external actions to full commit SHAs.
2. Keep the default `GITHUB_TOKEN` permission restricted where organization policy permits; each workflow declares only the permissions it needs.
3. Enable **Allow GitHub Actions to create and approve pull requests** only when the promotion workflow is ready. OpenFS will use this capability to create a branch and pull request, never to approve its own result.

If organization policy forbids that combined checkbox, use a dedicated GitHub App with narrowly scoped `Contents: write` and `Pull requests: write` permissions instead. Do not use a maintainer's personal token as the normal unattended identity.

GitHub reference: <https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository>

### 4. Protect `main`

Create a branch ruleset or branch-protection rule for `main`:

- require a pull request before merge;
- require at least one human approval;
- require review from Code Owners for protected control-plane paths;
- dismiss stale approvals when new commits are pushed;
- require the `validate` and `enforce` checks;
- require conversation resolution;
- block force pushes and deletion;
- apply the rule to administrators where organization policy allows.

The scheduled agents must never push directly to `main`.
The repository CODEOWNERS file currently assigns these paths to `@kento`. Replace
that owner with a write-enabled HPCI-CFSP maintainer team when the team exists;
do not remove the protected path set merely to reduce review friction. Proposal,
Assessment, and Handoff paths are intentionally outside CODEOWNERS so ordinary
multi-Agent research can proceed without making every artifact a human bottleneck.

GitHub reference: <https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches>

### 5. Owner decisions needed before the first paid Run

Record these decisions in a reviewed pull request or Directive:

- approved OpenAI and Anthropic model IDs;
- maximum cost per Run and provider-side monthly limits;
- whether source retrieval may use provider Web-search tools, direct HTTP retrieval, or both;
- retention period for provider responses, GitHub artifacts, and search receipts;
- the people who may approve high-impact recommendations and public release;
- the initial Pilot scope, recommended as `OFS-001` only.

## Activation sequence

1. Merge the weekly Coordinator while both enable variables remain `false`.
2. Manually dispatch **OpenFS Weekly Coordinator** with `monitor_id` set to
   `MON-MEMORY-001`, `pilot=true`, and `publish_issue=false`.
3. Download and inspect the `openfs-weekly-cycle` artifact. This is a no-cost
   control-plane test.
4. Dispatch again with `publish_issue=true` and verify that a second dispatch for
   the same ISO week reuses the same Issue.
5. Set the repository variable `OPENFS_COORDINATOR_ENABLED=true` to enable the
   Monday 00:17 UTC schedule. This still makes no model call.
6. Manually run **Process OpenFS Agent Handoffs** with `publish_pr=false` after a
   test Handoff is merged. Inspect its artifact, then test `publish_pr=true`.
   Set `OPENFS_HANDOFF_CONTROL_ENABLED=true` only after branch protection accepts
   its control PR and prevents direct merge without review.
7. Manually run **Review OpenFS Weekly Results** with `publish_issues=false` and
   inspect the internal Digest and grouped Issue payload artifact. Repeat with
   `publish_issues=true`, verify that a second run updates rather than duplicates
   the same managed Issues, then set `OPENFS_REVIEW_ENABLED=true`.
   Before publishing, create repository labels `openfs-weekly-cycle`,
   `openfs-exception`, and `needs-owner-action`; publication fails closed if a
   required label is absent. The scheduled Review summarizes the preceding
   completed ISO week by default, while manual dispatch may select another week.
8. Bind `validator-public-02` and `critic-public-01` in
   `config/agent-registry.json` to approved reviewer models. The baseline needs
   three reviewer executions and at least two support groups independent of the
   synthesis author. Run `tools/check_consensus_readiness.py` after configuration.
9. Configure a cost ceiling and provider-side alerts before adding the research
   Worker. A full 15-center cycle can require about 127 Work Items with three
   reviewers; the repository ceiling is 200, while each Run should request the
   smallest limit that fits its inspected plan.
10. Keep `OPENFS_RESEARCH_ENABLED=false` until the Worker passes manual secret,
   budget, boundary, assignment, recovery, and Consensus-capacity tests. Run
   `python3 tools/check_research_web_security.py --require-production-profile`
   and set `OPENFS_SECURITY_PROFILE_ID` only after the deployed platform evidence
   has been reviewed.
11. Enable provider calls first in manual Pilot mode. Enable unattended production
   Runs only after owner review of cost, citations, dissent, false positives, and
   generated pull-request paths.
12. After accepted non-Recommendation Claims exist, manually run **Prepare OpenFS
    Claim Promotions** with `publish_pr=false` and inspect its artifact and diff.
    Then test `publish_pr=true` and confirm branch protection requires human review.
    Set `OPENFS_PROMOTION_ENABLED=true` only after this succeeds. The Tuesday
    schedule prepares at most one open promotion PR and never merges it.
13. Before relying on correction handling, create a test `canonical-status`
    Directive for a disposable accepted Claim and run
    `tools/record_claim_status.py` on a branch. Confirm the original record
    remains, the active index excludes it, the status history names the human
    Directive, a retry is idempotent, and branch protection requires review.

Weekly operation should create proposal pull requests and exception Issues. It must not auto-merge canonical results or publish a scenario/report without the existing human publication Directive.

Approved `research-instruction` Directives are snapshotted into the next matching
Run. The default `application_mode` is `once`; its applied receipt prevents silent
weekly replay. Use `application_mode: recurring` only with an explicit
`expires_at`. A recurring Directive is included in each matching Run until that
instant. Create a new Directive ID for a revised instruction instead of editing an
already applied record.

Production Work Item completion is fail-closed on cost accounting: every completion
must report `cost_usd` plus a non-empty measurement note. The controller reevaluates
the Run cap immediately after each completion, including the final Work Item, and
stops the Run on an overage. Pilot Runs may retain `unreported` cost for harness
testing, but Digests display it as unknown rather than zero. Provider-side hard
spend limits remain an independent owner setup requirement.

### Production readiness gate

Use the aggregate procedure in `docs/operations/production-readiness.md` before
enabling any unattended Worker. It distinguishes repository checks from
expiring owner attestations for GitHub and provider settings.

An enabled Monitor is not sufficient to start unattended production. The weekly
Coordinator runs `tools/evaluate_monitor_readiness.py` and blocks the cycle unless:

- the Monitor is enabled;
- the budget configuration is owner-approved and has a positive per-Run cost cap;
- the Consensus policy is calibrated and the live Agent registry has sufficient
  enabled, independent validator and critic capacity;
- at least `manual_run_requirement` completed Pilot Runs have passed Coverage,
  temporal integrity, and formal Consensus, and each has a digest-pinned human
  record under `reviews/run-approvals/`.

A Pilot Run approval confirms calibration review only. It does not accept a Claim,
Finding, Recommendation, scenario, or report. If the approved Run manifest or Brief
changes, the digest check invalidates that approval and blocks production.
Use `tools/prepare_run_approval.py --run-id <RUN-ID>` to create a default-deny
review draft with pinned digests; it deliberately leaves every human check false.

The Weekly Digest groups open Exceptions that share the same kind, unmet
requirements, and publication-blocking state into one Owner Action. Every original
Exception reference remains listed, but repeated Consensus-capacity failures do not
create a separate review decision for each Run.
Sanitized GitHub Issue payloads use the same grouping key, so a recurring owner
action updates one stable deduplication marker instead of opening one Issue per Run.

### Coordinator versus Worker

- The **Coordinator** is the GitHub Actions schedule. It validates control data,
  selects eligible Monitors, records prior Run IDs and pending Directives, and
  emits a stable Issue trigger.
- A **Worker** is a separately credentialed Codex, OpenAI API, Claude, or local
  model execution path. It claims a cycle, creates a branch, and processes leased
  Work Items through the Run Controller.
- The Coordinator never receives provider secrets. A discovery or validation
  Worker never receives publication authority. Promotion remains a separate pull
  request path.
- The **Handoff Controller** runs daily when enabled. It accepts merged,
  digest-verified Agent outputs, expands deterministic follow-up Work Items, and
  opens one control-state pull request. If a prior control PR is still open, new
  Handoffs wait for the next cycle instead of creating a conflicting PR.
- The **Weekly Review** research job has no model-provider secret, Issue-write
  permission, or Git publication authority. It runs only with a selected,
  production-eligible Research Web security profile and emits internal artifacts
  plus sanitized Issue payloads. A separate downstream job receives only those
  payloads and may create or update managed GitHub Issues.
- The same job rebuilds the P0 roadmap source and freshness audits. One stable
  managed Issue lists only `critical` and `high` freshness attention, is updated
  rather than duplicated, and is closed when that priority queue is empty. The
  lower-priority audit remains available in the workflow artifact and on Pages.

## Optional Codex automation

A Codex recurring task can monitor failed GitHub Actions Runs, summarize weekly Digests, or prepare maintenance pull requests. It is not a substitute for the provider-independent Consensus path because a single recurring Codex task is one correlated decision path.
