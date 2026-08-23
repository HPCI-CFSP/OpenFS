# Incident Response

## Trigger examples

Credential exposure, suspected prompt-injection success, unauthorized write, NDA leakage, malicious dependency, unexplained canonical change, or sustained cost anomaly starts an incident.

## Immediate actions

1. disable scheduled and promotion workflows;
2. revoke or rotate affected credentials;
3. preserve relevant Run, Decision, workflow, and audit records;
4. quarantine affected proposals and canonical records;
5. identify downstream Claims, Findings, Roadmap Items, and reports;
6. notify the accountable repository and information-boundary owners.

## Recovery

Restore from the last known accepted Decision set, rerun validation, and reopen promotion only after the root cause and control changes are reviewed. Never delete incident evidence merely to make the repository appear clean.
