# Disaster Recovery

## Recovery sources

Git history is authoritative for policies, schemas, tasks, decisions, and accepted text records. External artifact or database services must have independent backup, retention, digest verification, and access recovery procedures before OpenFS depends on them.

## Recovery objective

Restore the last consistent set of accepted Decisions and canonical artifacts without replaying untrusted content through a privileged identity.

## Procedure

1. stop scheduling and promotion;
2. identify the last known consistent commit and Decision set;
3. restore external artifacts by immutable digest;
4. run repository, schema, reference, and dependency validation;
5. reconcile Runs that started but did not commit watermarks;
6. replay only failed or uncertain Work Items with new Run IDs;
7. obtain owner approval before re-enabling promotion and scheduling.

Recovery exercises should verify that an old model or unavailable connector does not prevent explanation of prior decisions.
