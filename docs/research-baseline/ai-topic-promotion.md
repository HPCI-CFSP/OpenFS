# AI Research Topic Promotion

## Additive-only automated path

An AI agent may propose a new research Topic when current evidence reveals an HPCI-relevant question that the catalog does not cover. Automated promotion can only append a Topic. Removal, narrowing, merge, split, retirement, evaluation-weight changes, or policy changes still require a reviewed human Directive.

```text
Emerging-topic discovery
  -> Research Topic Proposal
  -> blind independent validators
  -> falsification critic
  -> deterministic Consensus Gate
  -> accepted Decision
  -> topic-promotion role
  -> research-baseline + MON-AUTO-TOPICS
  -> next Run discovery Work Items
```

`CROSS-17` is retained as historical lineage but is no longer shown as a public research
Topic. Discovery is a harness capability defined by
`config/monitors/MON-EMERGING-TOPICS-001.json`. The Monitor compares candidate signals
against every active Topic and the source Watch Registry, rather than researching its own
former Topic ID.

## Required proposal content

`schemas/research-topic-proposal.schema.json` requires:

- novelty and HPCI impact relative to current Topic IDs;
- Japanese and English Topic titles;
- why existing Topics are insufficient;
- at least two Source Origin Groups and primary evidence;
- research questions, expected evidence, outputs, and cadence;
- exactly one public catalog category from `config/catalog-taxonomy.json`;
- source classes, query families, languages, and freshness;
- explicit falsification queries.

The `research_topic` rule in `config/consensus-policy.json` requires three assessments, two supporting independent Agent Groups, two Source Origin Groups, primary evidence, a falsification review, and no critical objection.

## Deterministic promotion and dispatch

After producing an accepted Decision with `tools/consensus_gate.py`, the `topic-promotion` role runs:

```bash
python3 tools/promote_research_topic.py \
  --proposal proposals/research-topics/PRP-TOP-000001.json \
  --decision decisions/DEC-PRP-TOP-000001.json \
  --baseline config/research-baseline.json \
  --monitor config/monitors/MON-AUTO-TOPICS-001.json \
  --i18n config/publication-i18n.json \
  --taxonomy config/catalog-taxonomy.json \
  --output-baseline config/research-baseline.json \
  --output-monitor config/monitors/MON-AUTO-TOPICS-001.json \
  --output-i18n config/publication-i18n.json \
  --output-taxonomy config/catalog-taxonomy.json
```

The promotion tool verifies Decision acceptance, all policy checks, unique Topic ID, known source IDs, two actual Origin Groups, protected initial-catalog immutability, additive-only behavior, and a valid single category assignment. It records Proposal and Decision IDs on the Topic, registers the Consensus-reviewed English title in the Pages translation catalog, and appends the Topic ID to the selected taxonomy category.
It also assigns the next unused public display code under the selected category prefix.

The next scheduler Run expands active accepted Topics for other agents:

```bash
python3 tools/expand_topic_monitor.py \
  --monitor config/monitors/MON-AUTO-TOPICS-001.json \
  --baseline config/research-baseline.json \
  --run-id RUN-YYYYMMDD-001 \
  --output queue/RUN-YYYYMMDD-001/topic-work-items.json
```

`MON-AUTO-TOPICS-001` remains disabled until three end-to-end manual runs have been reviewed. This prevents an uncalibrated consensus configuration from autonomously expanding production scope.

## Scheduled initiation

`.github/workflows/emerging-topic-discovery.yml` checks for new signals every day when
`OPENFS_EMERGING_TOPICS_ENABLED=true`. It fails closed unless the Monitor is enabled,
the reviewed-run threshold is met, the Consensus capacity is ready, and the Research Web
security profile is approved. The workflow opens or updates a coordination Issue; provider
Workers still operate through the restricted research-worker protocol. No candidate can
edit the catalog or Pages directly.
