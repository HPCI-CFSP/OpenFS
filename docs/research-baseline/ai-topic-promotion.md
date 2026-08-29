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

The next scheduler Run expands active accepted Topics for other agents:

```bash
python3 tools/expand_topic_monitor.py \
  --monitor config/monitors/MON-AUTO-TOPICS-001.json \
  --baseline config/research-baseline.json \
  --run-id RUN-YYYYMMDD-001 \
  --output queue/RUN-YYYYMMDD-001/topic-work-items.json
```

`MON-AUTO-TOPICS-001` remains disabled until three end-to-end manual runs have been reviewed. This prevents an uncalibrated consensus configuration from autonomously expanding production scope.
