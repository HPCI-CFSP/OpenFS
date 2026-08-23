# OpenFS research automation setup

## Current status

As of 2026-08-23, the repository has policies, schemas, a deterministic Consensus Gate prototype, research catalogs, permission checks, tests, and guarded GitHub Pages publication. It does **not** yet have the production Run Controller, provider API clients, Work Item leases, or promotion pull-request workflow.

The weekly schedule and all automated research agents therefore remain disabled. Adding API keys alone does not start research. The first operational milestone is a manually dispatched `OFS-001` Pilot; the weekly schedule is enabled only after three reviewed manual Runs.

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

1. Merge the manual Pilot workflow and provider adapters with `OPENFS_RESEARCH_ENABLED=false`.
2. Add the two API secrets and the repository variables.
3. Run a secret-presence and budget preflight that makes no paid model call.
4. Set `OPENFS_RESEARCH_ENABLED=true` and manually dispatch `OFS-001` Run 1.
5. Review coverage, citations, dissent, false positives, cost, and generated pull-request paths.
6. Complete Run 2 with a changed source and Run 3 with a human Directive.
7. Enable the weekly schedule only if all three Runs pass review; otherwise keep Pilot mode and correct the harness.

Weekly operation should create proposal pull requests and exception Issues. It must not auto-merge canonical results or publish a scenario/report without the existing human publication Directive.

## Optional Codex automation

A Codex recurring task can monitor failed GitHub Actions Runs, summarize weekly Digests, or prepare maintenance pull requests. It is not a substitute for the provider-independent Consensus path because a single recurring Codex task is one correlated decision path.
