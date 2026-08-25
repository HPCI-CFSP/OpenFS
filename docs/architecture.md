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

## Three kinds of independence

### Agent independence

`agent_independence_group` represents correlated model family, prompt profile, tools, and review strategy. Multiple processes from one group do not satisfy a cross-group quorum by themselves.

### Source independence

`origin_group` represents sources derived from one original publication, dataset, benchmark, announcement, or analysis. Reprints and summaries may improve discoverability but do not create independent corroboration.

An original Source must identify its canonical URL as the origin. A reprint,
summary, translation, derived analysis, or shared-dataset view must declare the
different canonical origin URL and is never counted as a primary Source for that
origin. Exact retrieved-content hashes assigned to different Origin Groups in one
Run fail validation and require lineage correction.

`publisher_group` represents the controlling Web authority that issued or hosts a
Source. It is derived conservatively from the canonical URL. Separate pages from
one publisher may be separate origins, but they do not satisfy cross-publisher
corroboration by themselves. Shared publishing platforms can under-count rather
than overstate independence; a human may review such conservative cases.

The configured Agent, Source Origin, and Publisher thresholds must all be satisfied
for an accepted Decision.

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
- Canonical state changes are append-only events under `knowledge/claim-status/`.
  They require a human `canonical-status` Directive naming exactly one Claim;
  the deterministic active view changes, while the promoted record does not.

## Common roadmap contract

Published roadmaps are projections of approved public evidence, not canonical
Claims or final HPCI recommendations. All domains use
`schemas/public-roadmap.schema.json`, which separates tracks, owner lanes,
milestones, dependencies, sources, and structured Coverage Gaps. The portfolio in
`config/roadmap-portfolio.json` owns stable roadmap IDs and slugs.

Quarter precision is evidence-constrained. A dated milestone may use Q1-Q4 only
when its cited source supports that precision; half-year and year-only statements
retain a null quarter, and missing public timing remains undated. OpenFS planning
gates are separate `hpci-evaluation` or `hpci-adoption` events with
`openfs-provisional-plan` timing. Pages generation fails closed when references,
portfolio mappings, timing semantics, publication approval, or the declared public
artifact set disagree.

### Portfolio review package

A multi-roadmap portfolio and its HPCI scenarios are a high-impact recommendation,
not a normal Claim. The author first commits a complete review target. The package
builder then reads those exact Git objects, records a SHA-256 for every roadmap,
audit, dependency register, scenario set, policy, schema, and publication
Directive, and creates review units with explicit falsification prompts.

Independent validators and critics submit one schema-valid assessment covering
every unit. The deterministic evaluator rejects digest drift, missing units,
duplicate reviewer identities, author-group votes, insufficient provider/origin
diversity, absent falsification, primary-source checks that do not match the
commit-pinned roadmap registry, and critical objections. The package also pins
its review schemas and evaluator implementation. Passing those mechanical
conditions yields only `ready-for-human-decision`; it cannot replace the human
decision required for a high-impact HPCI recommendation.

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
4. detect new, changed, unchanged, unavailable, and not-observed source observations;
5. create proposals;
6. obtain blind independent assessments and falsification review;
7. run the deterministic consensus gate;
8. prepare canonical promotion changes;
9. publish a digest and exception queue;
10. update watermarks only after durable completion.

The weekly Coordinator is implemented but remains variable-gated. It creates a
deduplicated control Issue and artifact without making model calls. The research
Worker and production Monitor remain disabled until independent provider capacity,
cost limits, and recovery behavior are owner-approved.

Production scheduling also has a deterministic readiness gate. It joins current
Monitor, budget, Agent-registry, and Consensus-policy state with digest-pinned human
reviews of the required manual Pilot Runs. Merely setting a Monitor to `enabled`
cannot bypass an uncalibrated policy, inadequate independent review capacity,
missing cost ceiling, or insufficient reviewed Runs. Pilot planning remains
available while production is blocked.

At Run creation, the controller pins the latest earlier completed Run with the same
Task and Monitor identity. Finalizing a completed or partial Run automatically
compares URL-and-query observations against that pinned predecessor and records
`runs/<RUN-ID>/changes.json`. A prior URL absent from the new selection is classified
as `not-observed`, never as proof that the source was withdrawn. This keeps weekly
change metrics reproducible even when multiple Runs overlap.

The same finalization step writes `runs/<RUN-ID>/dependency-impact.json`. It traces
changed and unavailable observations through Evidence bundles to Claim proposals,
Center Profiles, and Decisions. A recorded dependent blocks promotion pending
revalidation; a not-observed predecessor creates a reobservation gap without
asserting withdrawal. The report is append-only review input and never silently
rewrites a prior Claim or Decision.

`tools/promote_claim.py` is the narrow canonical path for non-Recommendation
Claims. It requires an accepted Decision with every check passing under the
Run-pinned calibrated Consensus Policy, recomputes Evidence and Source Lineage
references, and rejects any unresolved dependency-impact block. The resulting
append-only record in `knowledge/claims/` pins Proposal, Decision, Evidence, and
dependency-report digests. Recommendation Claims remain outside this automatic
path and require the human-accountable Recommendation Gate.

Run finalization also writes `promotion-readiness.json` when Claim Proposals exist.
It classifies each Claim as eligible, already promoted, Decision-blocked,
Policy-blocked, dependency-blocked, or Recommendation-Gate-bound. This preflight
is visible operational state; eligibility never auto-merges canonical knowledge.

All recurring discovery is worldwide in scope. The global horizon monitor searches across regions, organizations, and source languages; it gives technologies developed in Japan priority coverage to reduce local blind spots, then evaluates them against international alternatives using the same evidence and maturity rules.

## Center-aware scenario projection

Accepted knowledge is projected into multiple HPCI system scenarios rather than collapsed into one model answer. Each candidate joins architecture, system software, applications, center-specific impacts, worldwide technology options, priority coverage of technologies developed in Japan, uncertainty, and decision gates. `config/scenario-policy.json` defines common criteria, `schemas/center-profile.schema.json` and `schemas/system-scenario.schema.json` define durable inputs, and `tools/generate_scenario_views.py` emits synchronized Markdown and JSON views.

`config/hpci-center-registry.json` is the dated, official-source-anchored provider scope. A center Run snapshots it, expands two complementary searches for every provider, and records the assignment in each Source Receipt. Evidence from those searches is synthesized into provisional field-level Center Profiles. `tools/evaluate_center_profiles.py` reports missing, partial, stale, and non-accepted profiles separately; query execution never substitutes for profile Evidence.

Every new Center Profile is also a Consensus Proposal with source-origin lineage.
The Run Controller assigns blind reviews to each configured reviewer identity and
creates one deterministic Consensus batch only after all scheduled reviews finish.
The profile evaluator joins Decisions instead of trusting a mutable status label.
Pilot Runs created before proposal contract `0.2.0` remain auditable provisional
fixtures and are not retroactively promoted.

After a Center Run closes, `tools/generate_center_research_brief.py` measures
field-level gaps and `tools/generate_center_followup_plan.py` converts the most
planning-critical gaps into at most one bounded query per center. A later Run may
consume only the latest digest-matched plan, snapshots it under the new Run, and
records the originating Run ID. Gap-driven searches supplement the stable baseline
queries; they never turn missing public information into a factual claim.
Repeated unresolved gaps advance a recorded search generation: center-domain search,
then institution-wide procurement and annual-report search, then cross-domain primary
records. Each generation pins the preceding query digest so agents do not silently
repeat an ineffective search forever.

Worldwide Runs use the same closed-loop pattern. `tools/generate_global_followup_plan.py`
deduplicates unmet Coverage dimensions into bounded Source-class, region, technology,
maturity, result, or language queries. The Run Controller snapshots the latest
digest-matched plan and carries its Coverage targets into the assigned Work Items.
On finalization, `tools/evaluate_global_followup_effectiveness.py` records whether
each target gap was resolved, so ineffective search generations remain visible.
When no Coverage gaps remain, the planner writes a `no-followup-required` marker.
Run creation treats the newest marker as authoritative, so an older gap plan is not
replayed after its targets have been resolved.
If a resolved target is a recurring Coverage requirement, its successful query can
be promoted to the Monitor's `persistent_query_families`. Promotion records the
effective Run, effectiveness report, and Source Follow-up Query ID. Repository
validation rejects a persistent query without that machine-checkable provenance.
`tools/evaluate_followup_effectiveness.py` compares each consumed query's target
fields with the preceding profile and distinguishes stronger status, refreshed
Evidence at equal status, no change, and regression. This operational metric guides
the next search generation; it never promotes a finding.

Agent procedures are versioned in `skills/*/SKILL.md` and selected by
`config/skill-registry.json`. A Monitor-specific selector overrides the generic
Work Item-kind selector, so the worldwide technology Monitor receives its regional
and language coverage procedure without changing other Discovery Runs. Run creation
snapshots every registered Skill, records a SHA-256 digest in the manifest, binds
the applicable snapshot to each Work Item, and records that pinned digest in the
Agent execution. Later Work Item expansion resolves only the Run snapshot, even if
the live Skill changes or disappears.

Recurring Center Runs are cumulative at field level. A new draft prefers current-Run
Evidence when it is at least as strong as the preceding field. A stronger preceding
field may be inherited only while its dated Evidence remains inside the Monitor's
freshness window. The synthesis assignment records the predecessor profile digest and
all required earlier Evidence bundles; the proposal records inherited fields, Evidence
Run IDs, and bundle references. Unknown, stale, weaker, or silently modified predecessor
content is not carried forward. Every cumulative profile still enters Consensus as a
new provisional Proposal. At Run finalization, `tools/evaluate_profile_continuity.py`
independently compares still-current predecessor fields with the new profiles. A
regression opens an owner-action exception and blocks publication until reviewed.

The generator does not create authority. Missing center evidence remains visible, evaluation weights remain human-owned, and illustrative or candidate scenarios cannot bypass independent review, the Recommendation Gate, or promotion workflow.

## Research-scope expansion

Emerging-topic agents create additive Research Topic Proposals with Japanese/English titles, catalog-delta analysis, multiple Source Origin Groups, a Query Plan, and falsification queries. Independent validators and a critic assess the proposal, the deterministic Consensus Gate decides eligibility, and the `topic-promotion` role can update only the baseline, public title catalog, and automatic-topic monitor. The next Run expands accepted entries into Discovery Work Items for other agents.

## Public projection

`tools/build_pages_site.py` projects only approved public paths into a static GitHub Pages artifact. Candidate and illustrative scenarios, proposals, assessments, runs, reviews, and private/NDA paths are excluded. A published artifact also needs explicit public-classification metadata and a Publication Decision ID; only allowlisted fields are copied. Pages publication is a view over published artifacts, not a promotion mechanism.

## Planned repository areas

The initial design includes `skills/`, `queue/`, `proposals/`, `assessments/`, `decisions/`, `data/`, `knowledge/`, `roadmaps/`, `reports/`, `reviews/`, `runs/`, and `state/`. Areas are added to Git when they contain an implemented workflow, policy, sample, or accepted record; empty placeholder trees are avoided.
