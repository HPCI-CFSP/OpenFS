# Consensus Policy

## Principle

Consensus is a deterministic eligibility check, not proof of truth. The gate evaluates assessments, agent independence, source-origin independence, primary-source support, schema validity, and objections.

## Independent assessment

Reviewers perform a blind first review. An assessment records its reviewer, agent independence group, verdict, confidence, checks, and objections. Registry data, not self-declared model text, is authoritative for independence groups in production.

At Run creation, `tools/check_consensus_readiness.py` evaluates configured review
capacity before any research result exists. Reviewers in the Proposal author's
independence group may provide an assessment, but they cannot satisfy the
independent-support-group requirement. Unconfigured provider/model placeholders
and deterministic control-plane agents never count. An incomplete preflight
creates an Exception and permits only provisional research; it does not fabricate
quorum or stop ordinary public-information discovery.

## Source lineage

The number of URLs is not the number of independent sources. Proposals state their `origin_group_ids`; derivative publications from one origin count once.

## Outcomes

- `accepted`: all configured requirements pass.
- `provisional`: useful support exists, but one or more non-critical thresholds are missing.
- `contested`: a material or critical objection remains unresolved.
- `rejected`: evidence or validation fails materially.

All assessments and dissent remain attached to the Decision. Policy thresholds are versioned in `config/consensus-policy.json` and must be calibrated against reviewed evaluation cases.

## Additive research Topics

`research_topic` is a Consensus-controlled object type. An accepted Decision may authorize the narrowly scoped `topic-promotion` role to append the proposed Topic, Consensus-reviewed English title, and Query Plan. The rule requires multiple independent Agent Groups, multiple Source Origin Groups, primary evidence, and falsification review.

This automated authority is additive only. Existing Topic removal, merge, split, narrowing, retirement, policy changes, and evaluation-weight changes remain human-Directive decisions.
