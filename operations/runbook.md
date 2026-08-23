# OpenFS Operations Runbook

## Current mode

The recurring schedule and agent registry are disabled. Phase 0 supports repository validation and deterministic consensus-gate tests only.

## Manual validation

```bash
python3 tools/validate_repository.py
python3 -m unittest discover -s tests -v
```

## Before enabling a monitor

1. assign task, policy, security, and operational owners;
2. configure real agents without committing credentials;
3. approve source scope, budgets, and retrieval terms;
4. pass Golden, Adversarial, and Replay evaluations;
5. complete the three manual `OFS-001` Runs;
6. configure branch protection and required checks;
7. exercise the kill switch and rollback procedure.

## Stopping operation

The future scheduler must check `state/STOP` before dispatching work and before promotion. During an incident, disable scheduled and promotion workflows in GitHub in addition to setting the repository control.
