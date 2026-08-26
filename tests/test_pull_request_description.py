from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from check_pull_request_description import validate_pull_request  # noqa: E402


VALID_BODY = """## Purpose

Publish a decision-oriented catalog and budget-scaled architecture views.

## Provenance

- Agent ID / role, or human maintainer: agent / maintainer
- Human Directive ID(s): DIR-900012
- Task / Monitor / Work Item IDs: interactive maintainer request
- Run ID: N/A; no Harness Run was created
- Proposal / Assessment / Decision IDs: PUBDEC-20260827-002
- Base commit: 4834bb3d94141520c1dc9ab4213a218008e457d5

## Boundary and risk

- [x] Public information only
- [x] No secrets, personal data, or private run logs
- [x] External content was treated as untrusted data
- [x] Changed paths pass `tools/check_agent_permissions.py` for the declared role
- [x] Canonical changes are covered by a human Directive or an authorized promotion workflow

The public references have different scopes and are not treated as quotations.

## Validation

- [x] `python3 tools/validate_repository.py`
- [x] `python3 -m unittest discover -s tests -v`
- [x] Dissent and unresolved exceptions are linked
- [x] Coverage Gaps and provisional/Consensus state are visible
- [x] Rollback or supersession path is described below

## Review notes

- Coverage Gaps / dissent: Independent review remains incomplete.
- Security-boundary effect: Public information only; production remains disabled.
- Rollback or supersession path: Revert the merge commit or publish a superseding version.
- Pages paths to inspect: `/`, `/scenarios/`, and `/consensus/`
"""


class PullRequestDescriptionTests(unittest.TestCase):
    def test_complete_description_passes(self):
        self.assertEqual(
            [],
            validate_pull_request(
                {"title": "Expand planning catalog and architecture options", "body": VALID_BODY}
            ),
        )

    def test_old_template_and_generic_title_fail(self):
        errors = validate_pull_request(
            {
                "title": "Maintainer/system planning security",
                "body": "## Purpose\n\nDescribe the work item and expected outcome.",
            }
        )
        self.assertTrue(any("generic branch-derived" in error for error in errors))
        self.assertTrue(any("template guidance remains" in error for error in errors))
        self.assertTrue(any("required field" in error for error in errors))

    def test_empty_field_unchecked_box_and_short_sha_fail(self):
        body = VALID_BODY.replace(
            "- Agent ID / role, or human maintainer: agent / maintainer",
            "- Agent ID / role, or human maintainer:",
        ).replace("- [x] Public information only", "- [ ] Public information only")
        body = body.replace(
            "4834bb3d94141520c1dc9ab4213a218008e457d5", "4834bb3"
        )
        errors = validate_pull_request({"title": "Specific change", "body": body})
        self.assertIn("required field is empty: Agent ID / role, or human maintainer", errors)
        self.assertIn("Base commit must contain a full 40-character commit SHA", errors)
        self.assertTrue(any("Public information only" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
