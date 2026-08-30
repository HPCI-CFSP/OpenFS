# Catalog ownership and continuous maintenance

## Revision 5

The user approved this editorial restructuring in `DIR-900014`. The migration
retains all existing canonical IDs, prior research questions, Evidence IDs, and
Consensus references. It does not constitute a new primary-source review or
independent Consensus. Public results remain provisional. The generated
[current catalog](../research-baseline/current-catalog.md) contains every active
scope and a complete old-to-new table; `config/catalog-migration.json` is its
machine-readable lineage source. Preserve this revision when recording a later
migration instead of silently replacing its history.

## Research ownership

- Architecture covers node and system organization, semiconductor processes and
  packaging, memory, interconnects, specialized hardware, and storage systems.
  Storage combines devices, protocols, filesystems, data management, and integrated
  products. Compare candidates at matching layers, not SSDs against filesystems.
- Memory standards belong to memory; bonding belongs to semiconductor packaging;
  CXL belongs to interconnects; PIM belongs to specialized hardware. Other Topics
  reference those records for composition decisions instead of copying claims.
- Programming environments own models, languages, compilers, SDKs, and development
  tools. Numerical libraries own implementation support; application numerical
  validity owns scientific error and convergence criteria. Optimization mechanisms
  remain separate from AI-assisted coding practices.
- Scientific workflows retain non-AI execution and experimental integration.
  AI frameworks own training, serving, and agent runtimes. Resource management
  owns scheduler/OS/container mechanisms, not application workload requirements.
- Needs and evaluation are paired separately for scientific simulation, AI, and
  experimental/real-time processing. The shared methodology may be reused, but
  accuracy, throughput, tail latency, and deadline compliance are not interchangeable.
- Data technology and I/O architecture belong to storage. Service continuity,
  retention, migration responsibility, and transitions between system generations
  belong to the operations Topic. Development profiling and operational telemetry
  likewise have distinct owners.
- Software sustainability remains a research Topic because maintainer capacity,
  funding, dependencies, support lifetimes, licensing, and exit options affect
  long-term procurement and operation. It covers commercial and open-source software.
- Country-specific adoption is a cross-domain view over the same technical
  records. Global supply risks remain distinct from Japanese industrial deployment.

## Work assignment and completion

1. Resolve a legacy Topic through its structured successors. A split needs an
   explicit choice of one or more relevant successors, not an arbitrary redirect.
2. Select concrete `research_units` and read their questions, unresolved inherited
   questions in the migration table, related Topics, and linked evidence sections.
3. Record the selected canonical Topic and unit IDs in the Work Item's scope and
   declared outputs. Consult the Watch Registry and generated source map; roadmap
   family membership is a discovery lead, not proof of claim-level relevance.
4. Research worldwide within the approved budget and security profile. Prioritize
   Japanese-origin technologies without restricting scope or assuming superiority.
5. Preserve `not-started` for uncovered units and `partial` for incomplete or
   unverified evidence. Merging several partial records never completes a Topic.
   Unit-level `reviewed` is currently blocked until a unit-bound independent
   Consensus receipt contract is implemented. Do not weaken this gate to publish.
6. AI-proposed Topics continue through `OFS-004` and the research-topic Consensus
   gate. An accepted additive Topic without a unit breakdown remains an unstarted
   scope assignment; decompose it before claiming research completion.

## Harness and output transfers

`CROSS-18` worldwide monitoring is a Harness responsibility, not a separate
technical research result. Continue `OFS-005`, the Global Technology Monitor,
the Watch Registry, and Consensus-based emerging-topic discovery. Use active
Topics for substantive results. Do not enable disabled production agents or
monitors as a side effect of this reorganization.

`CROSS-02` continuous benchmarking supplies the three evaluation Topics. Retain
repeatable measurement, source/version/configuration pinning, calibration versus
independent validation, regression detection, and the existing benchmark gates.

`CROSS-13` planning generation is maintained by the scenario-generation workflow
and its output pages. Procurement research remains in its active Topic. No
automatic ranking, budget assumption, or adoption authorization follows from
reclassification.

## Compatibility and validation

For an explicitly human-authorized single-model update, use the
[bounded provisional update procedure](provisional-research-updates.md). It pins
the input commit, preserves prior sections, and leaves Consensus incomplete.

The legacy `tools/expand_topic_decision_support.py` whole-profile bootstrap is
blocked for revision 5 onward: its former topic-to-track map would undo ownership
and overwrite item history. It is not a recurring research worker. Use scoped
proposals, existing promotion gates, and versioned research-unit updates instead.

Historical Run, Proposal, Finding, Assessment, Decision, and commit-pinned review
packages are immutable inputs. Pages adds current `catalog_topic_ids` separately
from historical `topic_ids`; only justified narrow routes are carried forward.
Legacy links show successor choices. Retired public codes cannot be reused.
Publication dates and research as-of dates are not refreshed by an editorial move.

After a scope edit, run:

```sh
python3 tools/build_catalog_reference.py
python3 tools/build_source_catalog_map.py
python3 tools/check_catalog_migration.py
python3 tools/validate_repository.py
python3 tools/validate_json_schemas.py
python3 tools/validate_readme_i18n.py
python3 -m unittest discover -s tests -v
```

Test every active Topic, legacy link, category, roadmap backlink, both languages,
search, and narrow/mobile layouts. Confirm that no claim or source disappeared,
no historical Consensus was relabeled, and no unsupported research progress was
introduced. Technical correctness of the migration is not scientific validation.
