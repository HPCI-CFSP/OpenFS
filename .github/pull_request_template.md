## Purpose

Describe the work item and expected outcome.

## Provenance

- Agent ID / role, or human maintainer:
- Task / Monitor / Work Item IDs:
- Run ID:
- Proposal IDs:
- Assessment IDs:
- Decision IDs:
- Base commit:

## Boundary and risk

- [ ] Public information only
- [ ] No secrets, personal data, or private run logs
- [ ] External content was treated as untrusted data
- [ ] Changed paths pass `tools/check_agent_permissions.py` for the declared role
- [ ] Canonical paths were changed only by an authorized promotion workflow

## Validation

- [ ] `python3 tools/validate_repository.py`
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] Dissent and unresolved exceptions are linked
- [ ] Rollback or supersession path is described
