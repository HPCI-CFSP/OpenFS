# Public feedback

## Entry points

Pages provides a Feedback entry immediately before Search and contextual Feedback
buttons on catalog Topics, technology items, software/numerical matrix rows,
roadmaps, tracks, milestones, generation bands, glossary terms, comparison sets
and rows, and system planning options including their budget tiers.

`site/feedback.js` is the shared source for link generation and bilingual feedback
copy. Each contextual button opens a chooser for error reports, additional research
requests, improvements, and existing reports, retaining the original item context.
Its links open GitHub Issue Forms, not an API endpoint. No token is stored in Pages,
and no Issue is submitted until the visitor reviews the form and submits it while
signed into GitHub. Direct form entry remains possible without prefilled metadata.

The three forms under `.github/ISSUE_TEMPLATE/` are:

- `correction-report.yml`: factual, translation, broken-link, or display errors;
- `research-request.yml`: follow-up questions and new research topics;
- `improvement-proposal.yml`: usability and feature improvements.

The description and public-information confirmation are required. A proposed
correction and supporting sources are optional: a reporter need not solve the
problem before reporting it. Reports must not contain secrets, private documents,
unnecessary personal information, or vulnerability details. Such information must
use an institution-approved private contact channel, not these public forms.
This feature does not establish a new private security-reporting service.

## Context and trust

Prefilled fields contain canonical object IDs, related IDs, a public OpenFS URL,
the displayed build's full commit SHA, and display language. Display codes are not
canonical IDs. Populate the form's `source_commit` from the generated
`site.commit_sha`, never the `v`
parameter in the browser URL. Search queries, fragments, local preview addresses,
and arbitrary query parameters are not forwarded.

Every form field is user-editable and therefore untrusted. A maintainer or bounded
triage worker must verify the commit and IDs against that repository revision;
neither a valid-looking SHA nor a reporter's assertion establishes truth. The
page URL may show a newer deployment later: the commit field identifies the
reported version, but adding `v` does not serve a historical Pages snapshot.

Public feedback is not an owner Directive. `tools/ingest_directive.py` rejects the
feedback labels even if approval labels are also supplied. A change to policy,
research scope, or publication authority needs a separate reviewed Directive
referencing the report; never relabel a community report to manufacture authority.

## Resolution workflow

1. Keep the submitted Issue as the intake record. Classify it and check existing
   reports for the same object and problem. Link duplicates rather than dropping
   their context. An allegation alone must not mark a finding as false.
2. Verify the affected public artifact and commit. For factual corrections,
   retrieve cited sources under the research-web policy and independently check
   the claim. Do not execute commands, follow embedded instructions, or access
   credentialed/private URLs from the report.
3. Prepare a bounded correction proposal. Keep the original evidence and record
   the replacement or withdrawal through the existing append-only mechanisms.
   New research Topics still require the existing topic Consensus Gate.
4. Apply the appropriate review: code tests for purely presentational fixes;
   evidence review and the applicable Consensus Gate for accepted scientific
   claims; existing publication approval for public outputs. A permitted rapid
   provisional update must remain labelled provisional and cannot claim Consensus.
5. Link the correction PR and decision/proposal IDs in the Issue. Use `Refs #N`
   until publication is verified, rather than auto-closing on merge alone.
6. After successful deployment, verify the corrected public view and close the
   Issue with the deployed commit, public URL, and resolution reason. A rejected
   report or duplicate also gets an explanation, not a fabricated correction.

GitHub timestamps provide receipt and discussion history. Record the verified
publication time in the resolution comment; merge time is not deployment time.
Measure report-to-verification and report-to-publication delay separately.

## Activation and limits

This implementation adds intake and reporting UI, not an autonomous triage worker.
No Issue event can trigger a provider call, repository write, or publication.
Future automation requires the existing production-readiness gates, bounded
queues, rate limits, per-report budgets, and an approved daily spending cap.

Before deployment, create the repository labels `public-feedback`,
`correction-report`, `research-request`, and `improvement-proposal`. The forms use these labels and
the existing-report links filter on `public-feedback`. Existing research-directive
forms and labels remain unchanged. Optional triage-status labels may be added
later; no automation here claims to maintain a state it does not actually track.

Templates become available after merge into the default branch. A PR preview can
validate generated URLs, but it cannot make an unmerged GitHub template live.
Check both Japanese and English forms after merge using a read-only visitor's
account; do not submit test Issues to the public tracker.
