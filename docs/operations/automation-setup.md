# OpenFS research automation setup

## Current status

As of 2026-08-24, the repository has a Run Controller, leased Work Items,
configuration snapshots, Rights Gate, source-change detection, coverage reporting,
Consensus-capacity preflight, deterministic Consensus decisions, weekly Digests,
review Briefs, sanitized Issue payloads, budgets, stop records, and guarded GitHub
Pages publication. Three `OFS-001` Pilot Runs are retained as auditable fixtures.

The weekly **control-plane** schedule is implemented in
`.github/workflows/weekly-coordinator.yml`. It validates the repository and prepares
one deduplicated coordination Issue. It makes no model call, performs no promotion,
and publishes no research result. Provider API clients and an unattended research
Worker are still intentionally disabled. Adding API keys alone does not start paid
research.

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
| `OPENFS_RESEARCH_ENABLED` | `false` | Kill switch for provider-calling jobs |
| `OPENFS_AUTOMATION_MODE` | `pilot` | Manual Pilot; not weekly operation |
| `OPENFS_MAX_COST_USD` | owner decision | Hard per-Run cost ceiling |
| `OPENFS_MAX_WORK_ITEMS` | `10` | Initial Pilot scope limit |
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
- dismiss stale approvals when new commits are pushed;
- require the `validate` and `enforce` checks;
- require conversation resolution;
- block force pushes and deletion;
- apply the rule to administrators where organization policy allows.

The scheduled agents must never push directly to `main`.

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
6. Configure at least two independent provider paths, approved model IDs, a cost
   ceiling, and provider-side alerts before adding the research Worker.
7. Keep `OPENFS_RESEARCH_ENABLED=false` until the Worker passes manual secret,
   budget, boundary, assignment, recovery, and Consensus-capacity tests.
8. Enable provider calls first in manual Pilot mode. Enable unattended production
   Runs only after owner review of cost, citations, dissent, false positives, and
   generated pull-request paths.

Weekly operation should create proposal pull requests and exception Issues. It must not auto-merge canonical results or publish a scenario/report without the existing human publication Directive.

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

## Optional Codex automation

A Codex recurring task can monitor failed GitHub Actions Runs, summarize weekly Digests, or prepare maintenance pull requests. It is not a substitute for the provider-independent Consensus path because a single recurring Codex task is one correlated decision path.
