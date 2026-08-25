# OpenFS Operations Runbook

## Current mode

The recurring schedule and provider-backed agents remain disabled. The local Pilot
control plane supports idempotent Run creation, approved Directive selection,
leased Work Items, lease-expiry recovery, bounded retries, dead-letter exception
records, output hashing, and deterministic finalization. This does not enable paid
model calls or canonical promotion.

## Manual validation

```bash
python3 tools/validate_repository.py
python3 -m unittest discover -s tests -v
```

Create a disabled-monitor Pilot Run without calling a provider:

```bash
python3 tools/run_controller.py start \
  --run-id RUN-PILOT-001 \
  --task-id OFS-001 \
  --monitor-id MON-MEMORY-001 \
  --pilot
```

Pilot workers may lease a Work Item only with the explicit
`--allow-disabled-pilot-agent` flag. Production mode rejects disabled Monitors and
Agents. A completed Work Item must name a declared output path that exists; the
controller records its SHA-256 digest.

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
