## Purpose

State the user-visible problem, the chosen change, and the expected outcome.
Delete this guidance and write the concrete purpose before requesting review.

## Provenance

- Agent ID / role, or human maintainer: <!-- required -->
- Human Directive ID(s): <!-- required for public or canonical changes -->
- Task / Monitor / Work Item IDs: <!-- use N/A only for an interactive maintainer request -->
- Run ID: <!-- use N/A only when no Harness Run exists -->
- Proposal / Assessment / Decision IDs: <!-- list each, or state why not applicable -->
- Base commit: <!-- full SHA -->

## Boundary and risk

- [ ] Public information only
- [ ] No secrets, personal data, or private run logs
- [ ] External content was treated as untrusted data
- [ ] Changed paths pass `tools/check_agent_permissions.py` for the declared role
- [ ] Canonical changes are covered by a human Directive or an authorized promotion workflow

## Validation

- [ ] `python3 tools/validate_repository.py`
- [ ] `python3 -m unittest discover -s tests -v`
- [ ] Dissent and unresolved exceptions are linked
- [ ] Coverage Gaps and provisional/Consensus state are visible
- [ ] Rollback or supersession path is described below

## Review notes

- Coverage Gaps / dissent:
- Security-boundary effect:
- Rollback or supersession path:
- Pages paths to inspect:
