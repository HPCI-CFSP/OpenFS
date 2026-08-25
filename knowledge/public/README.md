# Public Research Summaries

This directory contains human-approved, public-only projections of OpenFS research. These files are display artifacts, not canonical Claims or accepted HPCI recommendations.

Each summary must retain its research, coverage, and Consensus status. Source links must be public, and publication requires a matching `publication-approval` Directive.

`memory-technology-roadmap.json` is a bilingual, human-approved public display
artifact for the memory technology watch. It separates observed commercial
milestones, samples, standards, vendor targets, concepts, and publicly undated
items. Empty future years mean that no dated product milestone was confirmed in
the reviewed official sources; they do not mean that development has stopped.

`consensus-receipts.json` is the public proof layer for findings that passed the
Consensus Gate. A Receipt lists only approved public metadata: the accepted
Decision, participating AI models and agent roles, independence groups, policy
result, harness repository, Run ID, and the exact 40-character harness commit
SHA. Raw Assessments, prompts, private logs, secrets, and non-public Run content
must never be copied into a Receipt.

At least two distinct voting model identities (`provider` plus `model_family`)
and two voting independence groups are required. Multiple Agent IDs backed by
one model identity do not qualify as public Consensus.

An accepted public Finding must reference a matching Receipt. Provisional or
Consensus-incomplete Findings must not reference one. The Pages builder fails
closed when the status, Finding ID, Receipt, model independence, or harness
commit does not match.
