# OpenFS Architecture

## Purpose

OpenFS is a recurring, evidence-first research system for building reviewable HPCI findings, scenarios, roadmaps, and reports from public information. It minimizes routine human intervention without delegating high-impact policy judgment to a single model.

## Processing model

```text
GitHub Issue / reviewed Directive
             +
Task + Monitor + Policy + Budget
             |
             v
        Run Controller
             |
     +-------+--------+
     |                |
Discovery agents  Extraction agents
     |                |
     +------ Proposals+
             |
   Independent validators
             |
     Falsification agents
             |
      Assessments and dissent
             |
  Deterministic Consensus Gate
             |
     Decisions by object ID
             |
       Promotion workflow
             |
Canonical data -> Knowledge -> Roadmaps -> Reports
             |
      Digest and exceptions
```

Each scheduled execution is a new immutable Run. Continuity is stored in versioned records and scheduler state, not assumed from chat history.

## Four review gates

1. **Evidence Gate** verifies source identity, excerpt fidelity, retrieval time, and origin lineage.
2. **Claim Gate** verifies an atomic statement with its scope, date, conditions, and evidence.
3. **Finding Gate** evaluates a synthesis of accepted claims and preserves contrary evidence.
4. **Recommendation Gate** applies human-owned HPCI criteria, scenario assumptions, constraints, and risk classification.

The first three gates may be automated when policy conditions are met. A high-impact Recommendation remains a human-accountable decision even when agents prepare and review it.

## Two kinds of independence

### Agent independence

`agent_independence_group` represents correlated model family, prompt profile, tools, and review strategy. Multiple processes from one group do not satisfy a cross-group quorum by themselves.

### Source independence

`origin_group` represents sources derived from one original publication, dataset, benchmark, announcement, or analysis. Reprints and summaries may improve discoverability but do not create independent corroboration.

Both thresholds must be satisfied for an accepted Decision.

## Artifact states

```text
candidate
  -> under_independent_review
  -> accepted | provisional | contested | rejected
  -> superseded | withdrawn
```

- `accepted` meets the configured deterministic policy.
- `provisional` has useful support but lacks enough independent evidence or review.
- `contested` has unresolved material objections.
- `rejected` fails evidence or policy checks.
- `superseded` and `withdrawn` preserve history and trigger dependent-record review.

## Trust and information boundaries

### Public plane

Public-web agents operate only on public information and public OpenFS records. Fetch and extraction roles have no repository write credential or promotion authority.

### NDA plane

RiVault or another approved private environment has separate agents, runs, proposals, assessments, decisions, credentials, and logs. Information may cross to public OpenFS only as an approved, DLP-checked Export Package. Public IDs must not expose private identifiers unless policy explicitly permits it.

### Promotion plane

The promotion identity receives accepted Decision artifacts, not arbitrary web content. It can modify canonical paths through a reviewable pull request and cannot read model-provider secrets used by research jobs.

## Storage boundaries

Git stores policies, tasks, schemas, small structured records, decisions, directives, and reviewable generated text. Full web captures, large logs, embeddings, binary documents, and search indexes belong in a controlled artifact or database service with retention and access policy.

## Recurring operation

The planned weekly cycle is:

1. ingest reviewed directives;
2. expand active monitors into work items;
3. search public sources and record coverage;
4. detect new, changed, withdrawn, and failed sources;
5. create proposals;
6. obtain blind independent assessments and falsification review;
7. run the deterministic consensus gate;
8. prepare canonical promotion changes;
9. publish a digest and exception queue;
10. update watermarks only after durable completion.

The schedule remains disabled until the `OFS-001` monitor completes three manual runs: initial collection, a changed-source run, and a directive-driven run.

## Center-aware scenario projection

Accepted knowledge is projected into multiple HPCI system scenarios rather than collapsed into one model answer. Each candidate joins architecture, system software, applications, center-specific impacts, domestic technology, uncertainty, and decision gates. `config/scenario-policy.json` defines common criteria, `schemas/center-profile.schema.json` and `schemas/system-scenario.schema.json` define durable inputs, and `tools/generate_scenario_views.py` emits synchronized Markdown and JSON views.

The generator does not create authority. Missing center evidence remains visible, evaluation weights remain human-owned, and illustrative or candidate scenarios cannot bypass the Recommendation Gate or promotion workflow.

## Research-scope expansion

Emerging-topic agents create additive Research Topic Proposals with Japanese/English titles, catalog-delta analysis, multiple Source Origin Groups, a Query Plan, and falsification queries. Independent validators and a critic assess the proposal, the deterministic Consensus Gate decides eligibility, and the `topic-promotion` role can update only the baseline, public title catalog, and automatic-topic monitor. The next Run expands accepted entries into Discovery Work Items for other agents.

## Public projection

`tools/build_pages_site.py` projects only approved public paths into a static GitHub Pages artifact. Candidate and illustrative scenarios, proposals, assessments, runs, reviews, and private/NDA paths are excluded. A published artifact also needs explicit public-classification metadata and a Publication Decision ID; only allowlisted fields are copied. Pages publication is a view over published artifacts, not a promotion mechanism.

## Planned repository areas

The initial design includes `skills/`, `queue/`, `proposals/`, `assessments/`, `decisions/`, `data/`, `knowledge/`, `roadmaps/`, `reports/`, `reviews/`, `runs/`, and `state/`. Areas are added to Git when they contain an implemented workflow, policy, sample, or accepted record; empty placeholder trees are avoided.
