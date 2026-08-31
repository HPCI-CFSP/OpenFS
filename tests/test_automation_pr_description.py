from __future__ import annotations

import subprocess
import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from automation_pr_description import format_body, prepare_body
from check_pull_request_description import validate_pull_request


SUMMARY = {"affected_run_ids": ["RUN-1"], "accepted_handoff_refs": ["handoffs/RUN-1/WI-1.json"]}


class AutomationDescriptionTests(unittest.TestCase):
    def git_and_checks(self, args, **kwargs):
        self.assertNotIn("GITHUB_TOKEN", kwargs["env"])
        self.assertNotIn("OPENFS_PR_TEST_SENTINEL_SECRET", kwargs["env"])
        if args[0] == sys.executable:
            self.assertFalse(kwargs["capture_output"], "validation failures must remain visible in CI logs")
        self.commands.append(args)
        if args[:3] == ["git", "rev-parse", "HEAD"]:
            return SimpleNamespace(stdout="b" * 40)
        if args[:3] == ["git", "rev-parse", "--verify"]:
            return SimpleNamespace(stdout="b" * 40)
        if args[:3] == ["git", "diff", "--name-only"]:
            return SimpleNamespace(stdout="queue/RUN-1/WI-1.json\n")
        return SimpleNamespace(stdout="")

    def setUp(self):
        self.commands = []

    def test_actual_post_generation_checks_precede_complete_description(self):
        with patch.dict(os.environ, {"GITHUB_TOKEN": "test-only", "OPENFS_PR_TEST_SENTINEL_SECRET": "test-only"}), \
                patch("automation_pr_description.subprocess.run", side_effect=self.git_and_checks):
            title, body = prepare_body(ROOT, "control", SUMMARY, "a" * 40, "automation/handoff-control-1")
        self.assertEqual([], validate_pull_request({"title": title, "body": body}))
        self.assertIn([sys.executable, "tools/validate_repository.py"], self.commands)
        self.assertIn([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"], self.commands)

    def test_failed_validation_never_returns_a_completed_body(self):
        def fail_tests(args, **kwargs):
            if "unittest" in args:
                raise subprocess.CalledProcessError(1, args)
            return self.git_and_checks(args, **kwargs)
        with patch("automation_pr_description.subprocess.run", side_effect=fail_tests):
            with self.assertRaises(subprocess.CalledProcessError):
                prepare_body(ROOT, "control", SUMMARY, "a" * 40, "automation/handoff-control-1")

    def test_dirty_or_disallowed_changes_fail_before_tests(self):
        for failure in ("dirty", "path"):
            def fail(args, **kwargs):
                if failure == "dirty" and args[:2] == ["git", "status"]:
                    return SimpleNamespace(stdout=" M queue/RUN-1/WI-1.json")
                if failure == "path" and args[:3] == ["git", "diff", "--name-only"]:
                    return SimpleNamespace(stdout="config/role-permissions.json")
                return self.git_and_checks(args, **kwargs)
            with patch("automation_pr_description.subprocess.run", side_effect=fail):
                with self.subTest(failure=failure), self.assertRaises(ValueError):
                    prepare_body(ROOT, "control", SUMMARY, "a" * 40, "automation/handoff-control-1")
        self.assertFalse(any("unittest" in args for args in self.commands))

    def test_branch_changes_during_validation_require_a_rerun(self):
        revisions = iter(["b" * 40, "c" * 40])
        def change(args, **kwargs):
            if args[:3] == ["git", "rev-parse", "HEAD"]:
                return SimpleNamespace(stdout=next(revisions))
            return self.git_and_checks(args, **kwargs)
        with patch("automation_pr_description.subprocess.run", side_effect=change):
            with self.assertRaisesRegex(ValueError, "changed during validation"):
                prepare_body(ROOT, "control", SUMMARY, "a" * 40, "automation/handoff-control-1")

    def test_requested_pr_branch_must_be_the_checked_commit(self):
        def wrong_branch(args, **kwargs):
            if args[:3] == ["git", "rev-parse", "--verify"]:
                return SimpleNamespace(stdout="c" * 40)
            return self.git_and_checks(args, **kwargs)
        with patch("automation_pr_description.subprocess.run", side_effect=wrong_branch):
            with self.assertRaisesRegex(ValueError, "requested PR branch"):
                prepare_body(ROOT, "control", SUMMARY, "a" * 40, "automation/handoff-control-1")
        self.assertFalse(any("unittest" in args for args in self.commands))

    def test_push_cleanup_precedes_validation_with_no_token_in_git_config(self):
        for name in ("handoff-control", "claim-promotion"):
            workflow = (ROOT / ".github/workflows" / f"{name}.yml").read_text()
            cleanup = 'trap \'git remote set-url origin "https://github.com/${GITHUB_REPOSITORY}.git"\' EXIT'
            self.assertIn(cleanup, workflow)
            self.assertLess(workflow.index(cleanup), workflow.index('git remote set-url origin "https://x-access-token:'))

    def test_both_publishers_install_pinned_validators_before_running_tests(self):
        for name in ("handoff-control", "claim-promotion"):
            workflow = (ROOT / ".github/workflows" / f"{name}.yml").read_text()
            self.assertLess(workflow.index("--requirement requirements-validation.txt"),
                            workflow.index("python3 -m unittest discover"))

    def test_summary_values_cannot_inject_markdown_or_escape_repository(self):
        for summary in ({**SUMMARY, "affected_run_ids": ["RUN-1\n# 日本語"]},
                        {**SUMMARY, "accepted_handoff_refs": ["../private.json"]},
                        {**SUMMARY, "accepted_handoff_refs": ["handoffs/`bad`.json"]}):
            with self.assertRaises(ValueError):
                format_body("control", summary, "a" * 40)
        with self.assertRaises(ValueError):
            format_body("control", SUMMARY, "a" * 7)

    def test_empty_or_partially_documented_changes_cannot_claim_provenance(self):
        with self.assertRaises(ValueError):
            format_body("control", {**SUMMARY, "accepted_handoff_refs": []}, "a" * 40)
        for prepared in ([], [{"canonical_claim_id": "CLM-1", "proposal_ref": "proposals/PRP-1.json"}],
                         [{"canonical_claim_id": "CLM-1", "decision_ref": "decisions/DEC-1.json"}]):
            with self.subTest(prepared=prepared), self.assertRaises(ValueError):
                format_body("promotion", {"affected_run_ids": ["RUN-1"], "prepared": prepared}, "a" * 40)


if __name__ == "__main__":
    unittest.main()
