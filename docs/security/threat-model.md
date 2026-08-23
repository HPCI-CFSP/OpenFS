# Threat Model

## Protected assets

- OpenAI and other provider credentials;
- GitHub write tokens and protected branches;
- public canonical research records;
- private or NDA material and its metadata;
- prompts, policies, agent registry, and evaluation cases;
- audit logs needed to explain decisions.

## Principal threats

- indirect prompt injection in Web pages, PDFs, issues, comments, and hidden markup;
- credential exfiltration through tools, logs, links, or generated artifacts;
- poisoned or correlated sources presented as independent corroboration;
- compromised dependencies or GitHub Actions;
- unauthorized promotion, policy changes, or quorum manipulation;
- accidental NDA or personal-data publication;
- model drift causing silent changes to accepted outcomes;
- denial of service or uncontrolled cost through recursive or repeated work.

## Required controls

- quarantine untrusted content before privileged processing;
- schema-bound data exchange between stages;
- least-privilege, stage-specific identities;
- no shared job containing both untrusted code and provider or write credentials;
- pinned and reviewed automation dependencies;
- budgets, timeouts, retry limits, concurrency limits, and kill switch;
- append-only provenance and alerting for protected-policy changes;
- trusted-base pull-request enforcement so proposed code cannot weaken its own role check;
- adversarial tests and incident-response exercises.

## Residual boundary

Repository instructions guide a cooperative agent; they are not an operating-system sandbox. A compromised process holding a human's GitHub credential could use a non-agent branch identity. Scheduled agents therefore require separate least-privilege bot identities, and protected branches must require trusted checks and human-owned CODEOWNERS review for policy, workflow, registry, and permission changes.
