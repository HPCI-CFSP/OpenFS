# Consensus Policy

## Principle

Consensus is a deterministic eligibility check, not proof of truth. The gate evaluates assessments, agent independence, source-origin independence, publisher independence, primary-source support, schema validity, and objections.

## Independent assessment

Reviewers perform a blind first review. An assessment records its reviewer, agent independence group, verdict, confidence, checks, and objections. Registry data, not self-declared model text, is authoritative for independence groups in production.

For a commit-pinned review package, `reviewed_at` must fall after the package was
created and no later than the evaluator's clock, subject to the configured
one-minute clock-skew tolerance. A pre-package or future-dated review is
ineligible even when its content otherwise satisfies the gate. A future-dated
package is also invalid. Every review records `package_manifest_digest`, the
SHA-256 of the exact `manifest.json` bytes, so a review cannot be replayed after
review units, artifact lists, or package metadata are regenerated under the same
package ID and base commit.
The deterministic gate result records the same manifest digest. GitHub Pages
recomputes it and fails closed when either a gate result or an eligible review
targets different manifest bytes.
The gate also records the SHA-256 of every review file it evaluated. Pages
requires the assessment set and every byte digest to match, so adding, removing,
or editing a review always requires deterministic re-evaluation.

At Run creation, `tools/check_consensus_readiness.py` evaluates configured review
capacity before any research result exists. Reviewers in the Proposal author's
independence group may provide an assessment, but they cannot satisfy the
independent-support-group requirement. Unconfigured provider/model placeholders
and deterministic control-plane agents never count. An incomplete preflight
creates an Exception and permits only provisional research; it does not fabricate
quorum or stop ordinary public-information discovery.

Each Proposal is expanded into one reviewer-bound Work Item for every configured,
eligible `validator` or `critic` in the Run's pinned Agent Registry. A reviewer
cannot lease another reviewer's item. The Consensus Work Item is created only after
all scheduled first reviews finish, and it receives every Assessment reference.
Unconfigured reviewer templates are not scheduled.

The baseline policy needs three Assessments and support from at least two
independence groups outside the Proposal author's group. In the template Registry,
`validator-public-02` and `critic-public-01` are deliberately unconfigured. The
owner must bind them to approved, genuinely independent provider/model paths before
production; changing only an Agent ID does not create independence.

Center Profiles use the same gate. Their accepted status is projected from an
`accepted` Decision; editing `profile_status` alone cannot make a profile accepted.

## Source lineage

The number of URLs is not the number of independent sources. Proposals state their
`origin_group_ids`; derivative publications from one origin count once. New Claim
proposals also carry `publisher_group_ids`, derived from canonical Web authority.
Multiple original pages from one publisher do not satisfy the configured
cross-publisher threshold.

## Outcomes

- `accepted`: all configured requirements pass.
- `provisional`: useful support exists, but one or more non-critical thresholds are missing.
- `contested`: a material or critical objection remains unresolved.
- `rejected`: evidence or validation fails materially.

All assessments and dissent remain attached to the Decision. Policy thresholds are versioned in `config/consensus-policy.json` and must be calibrated against reviewed evaluation cases.

## Public Consensus Receipts

An accepted Finding may be labeled as Consensus-passed on GitHub Pages only
when it references a matching public Consensus Receipt. The Receipt is a
public-only projection of the accepted Decision and records the participating
model identities, Agent roles, voting independence groups, policy result,
harness repositories, Run IDs, and exact 40-character harness commit SHAs.

Publication requires at least two distinct voting model identities and two
voting independence groups. Multiple Agent IDs using one model do not satisfy
the public check. Missing or inconsistent Receipt data fails the Pages build;
the Finding remains provisional or Consensus-incomplete. Raw Assessments,
prompts, private logs, credentials, and non-public Run content are not included
in the Receipt.

## Additive research Topics

`research_topic` is a Consensus-controlled object type. An accepted Decision may authorize the narrowly scoped `topic-promotion` role to append the proposed Topic, Consensus-reviewed English title, and Query Plan. The rule requires multiple independent Agent Groups, multiple Source Origin Groups, primary evidence, and falsification review.

This automated authority is additive only. Existing Topic removal, merge, split, narrowing, retirement, policy changes, and evaluation-weight changes remain human-Directive decisions.
