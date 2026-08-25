from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from evaluate_center_profiles import evaluate, record  # noqa: E402
from evaluate_profile_continuity import (  # noqa: E402
    evaluate as evaluate_continuity,
    record as record_continuity,
)
from propose_center_profile import merge_with_predecessor, propose  # noqa: E402
from run_controller import create_run  # noqa: E402
from openfs_runtime import stable_digest  # noqa: E402


class CenterProfileCoverageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        for relative in (
            "config/acquisition-policy.json",
            "config/agent-registry.json",
            "config/autonomy-policy.json",
            "config/budgets.json",
            "config/consensus-policy.json",
            "config/role-permissions.json",
            "config/skill-registry.json",
            "config/source-registry.json",
            "config/hpci-center-registry.json",
            "config/monitors/MON-HPCI-CENTERS-001.json",
        ):
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / relative, target)
        for source in (ROOT / "skills").glob("*/SKILL.md"):
            target = self.root / source.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, target)
        (self.root / "reviews" / "directives").mkdir(parents=True)
        create_run(
            self.root,
            run_id="RUN-CENTER-PROFILES",
            task_id="OFS-003",
            monitor_id="MON-HPCI-CENTERS-001",
            pilot=True,
        )
        self.registry = json.loads(
            (self.root / "config" / "hpci-center-registry.json").read_text(
                encoding="utf-8"
            )
        )

    def tearDown(self):
        self.temporary.cleanup()

    def profile(
        self,
        center,
        *,
        status="provisional",
        partial_field=None,
        run_id="RUN-CENTER-PROFILES",
    ):
        proposal_number = self.registry["centers"].index(center) + 1
        profile = {
            "schema_version": "0.1.0",
            "proposal_contract_version": "0.2.0",
            "proposal_id": f"PRP-CTR-{proposal_number:06d}",
            "object_type": "center_profile",
            "run_id": run_id,
            "center_id": center["center_id"],
            "name_ja": center["name_ja"],
            "name_en": center["name_en"],
            "profile_status": status,
            "evidence_as_of": "2026-08-24",
            "evidence_refs": ["EVD-TEST"],
            "origin_group_ids": ["ORG-TEST-A", "ORG-TEST-B"],
            "has_primary_source": True,
            "unknowns": [],
            "created_by_agent_id": "synthesis-public-01",
            "created_at": "2026-08-24T00:00:00Z",
        }
        for field in self.registry["default_profile_fields"]:
            field_status = "partial" if field == partial_field else "verified"
            profile[field] = {
                "status": field_status,
                "summary": f"Test {field}",
                "as_of": "2026-08-24",
                "evidence_refs": ["EVD-TEST"],
            }
        return profile

    def write_profile(self, profile):
        output = (
            self.root
            / "proposals"
            / "center-profiles"
            / "RUN-CENTER-PROFILES"
            / f"{profile['center_id']}.json"
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(profile), encoding="utf-8")

    def write_accepted_decision(self, profile):
        output = (
            self.root
            / "decisions"
            / "RUN-CENTER-PROFILES"
            / f"{profile['proposal_id']}.json"
        )
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(
                {
                    "proposal_id": profile["proposal_id"],
                    "outcome": "accepted",
                }
            ),
            encoding="utf-8",
        )

    def test_partial_provisional_profile_remains_incomplete(self):
        self.write_profile(self.profile(self.registry["centers"][0], partial_field="power"))
        report = evaluate(
            self.root,
            run_id="RUN-CENTER-PROFILES",
            evaluated_at="2026-08-24T12:00:00Z",
        )
        self.assertEqual("incomplete", report["profile_coverage_status"])
        self.assertEqual(14, len(report["gaps"]["missing_profiles"]))
        self.assertEqual(1, len(report["gaps"]["non_accepted_profiles"]))
        self.assertEqual(
            ["power"], report["gaps"]["field_gaps"][0]["partial_fields"]
        )
        manifest = record(self.root, report)
        self.assertEqual(
            "incomplete", manifest["metrics"]["center_profile_coverage"]["status"]
        )

    def test_all_current_accepted_profiles_meet_registry_scope(self):
        for center in self.registry["centers"]:
            profile = self.profile(center, status="accepted")
            self.write_profile(profile)
            self.write_accepted_decision(profile)
        report = evaluate(
            self.root,
            run_id="RUN-CENTER-PROFILES",
            evaluated_at="2026-08-24T12:00:00Z",
        )
        self.assertEqual("accepted-current", report["profile_coverage_status"])
        self.assertEqual(15, report["observed"]["accepted_current_count"])
        self.assertFalse(any(report["gaps"].values()))

    def test_date_only_profile_accepts_one_day_timezone_rollover(self):
        profile = self.profile(self.registry["centers"][0], status="accepted")
        self.write_profile(profile)
        self.write_accepted_decision(profile)
        report = evaluate(
            self.root,
            run_id="RUN-CENTER-PROFILES",
            evaluated_at="2026-08-23T20:00:00Z",
        )
        observed = report["observed"]["profiles"][0]
        self.assertEqual(0, observed["profile_age_days"])
        self.assertTrue(observed["field_evidence_complete"])
        self.assertNotIn(
            profile["center_id"],
            {item["center_id"] for item in report["gaps"]["stale_profiles"]},
        )

    def _prepare_continuity(self, predecessor_profile, current_profile):
        previous_run = "RUN-CENTER-PREVIOUS"
        previous_manifest = {
            "run_id": previous_run,
            "task_id": "OFS-003",
            "monitor_id": "MON-HPCI-CENTERS-001",
            "status": "completed",
        }
        previous_manifest_path = self.root / "runs" / previous_run / "manifest.json"
        previous_manifest_path.parent.mkdir(parents=True, exist_ok=True)
        previous_manifest_path.write_text(json.dumps(previous_manifest), encoding="utf-8")
        current_manifest_path = (
            self.root / "runs" / "RUN-CENTER-PROFILES" / "manifest.json"
        )
        current_manifest = json.loads(current_manifest_path.read_text(encoding="utf-8"))
        current_manifest["followup_plan"] = {"base_run_id": previous_run}
        current_manifest_path.write_text(json.dumps(current_manifest), encoding="utf-8")
        for run_id, profile in (
            (previous_run, predecessor_profile),
            ("RUN-CENTER-PROFILES", current_profile),
        ):
            path = (
                self.root
                / "proposals"
                / "center-profiles"
                / run_id
                / f"{profile['center_id']}.json"
            )
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(profile), encoding="utf-8")

    def test_continuity_blocks_loss_of_current_predecessor_field(self):
        center = self.registry["centers"][0]
        predecessor = self.profile(center, run_id="RUN-CENTER-PREVIOUS")
        current = self.profile(center, partial_field="power")
        self._prepare_continuity(predecessor, current)

        report = evaluate_continuity(
            self.root,
            run_id="RUN-CENTER-PROFILES",
            evaluated_at="2026-08-24T12:00:00Z",
        )

        self.assertEqual("failed", report["status"])
        self.assertTrue(report["publication_blocked"])
        self.assertEqual(1, report["regression_count"])
        self.assertEqual("power", report["regressions"][0]["field"])
        manifest = record_continuity(self.root, report)
        self.assertEqual(
            "failed", manifest["metrics"]["profile_continuity"]["status"]
        )
        exception = json.loads(
            (
                self.root
                / "reviews"
                / "exceptions"
                / "RUN-CENTER-PROFILES"
                / "PROFILE-CONTINUITY.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual("open", exception["status"])

    def test_continuity_passes_when_current_profile_preserves_strength(self):
        center = self.registry["centers"][0]
        predecessor = self.profile(
            center,
            partial_field="power",
            run_id="RUN-CENTER-PREVIOUS",
        )
        current = self.profile(center)
        self._prepare_continuity(predecessor, current)

        report = evaluate_continuity(
            self.root,
            run_id="RUN-CENTER-PROFILES",
            evaluated_at="2026-08-24T12:00:00Z",
        )

        self.assertEqual("passed", report["status"])
        self.assertFalse(report["publication_blocked"])
        self.assertEqual(0, report["regression_count"])

    def test_profile_proposal_preserves_unknowns_and_rejects_unassigned_evidence(self):
        center = self.registry["centers"][0]
        draft = {
            "evidence_as_of": "2026-08-24",
            "fields": {},
            "unknowns": ["power requires direct center confirmation"],
        }
        for field in self.registry["default_profile_fields"]:
            draft["fields"][field] = {
                "status": "unknown",
                "summary": "",
                "as_of": None,
                "evidence_refs": [],
            }
        draft["fields"]["current_system"] = {
            "status": "verified",
            "summary": "The official resource page identifies the current system.",
            "as_of": "2026-08-24",
            "evidence_refs": ["EVD-CENTER-A"],
        }
        bundle = {
            "object_type": "evidence",
            "run_id": "RUN-CENTER-PROFILES",
            "origin_group_ids": ["ORG-CENTER-A"],
            "has_primary_source": True,
            "evidence_candidates": [
                {
                    "evidence_id": "EVD-CENTER-A",
                    "source_lineage_id": "LIN-CENTER-A",
                }
            ],
        }
        profile = propose(
            [bundle],
            bundle_refs=["proposals/evidence/RUN/WORK.json"],
            center_id=center["center_id"],
            draft=draft,
            run_id="RUN-CENTER-PROFILES",
            agent_id="synthesis-public-01",
            agent_registry=json.loads(
                (self.root / "config" / "agent-registry.json").read_text(
                    encoding="utf-8"
                )
            ),
            center_registry=self.registry,
            created_at="2026-08-24T00:00:00Z",
        )
        self.assertEqual("provisional", profile["profile_status"])
        self.assertEqual("center_profile", profile["object_type"])
        self.assertRegex(profile["proposal_id"], r"^PRP-CTR-[0-9]{6}$")
        self.assertEqual(["ORG-CENTER-A"], profile["origin_group_ids"])
        self.assertTrue(profile["has_primary_source"])
        self.assertEqual("verified", profile["current_system"]["status"])
        self.assertIn("power", profile["unknowns"])
        draft["fields"]["power"] = {
            "status": "verified",
            "summary": "Unsupported",
            "as_of": "2026-08-24",
            "evidence_refs": ["EVD-NOT-ASSIGNED"],
        }
        with self.assertRaisesRegex(ValueError, "outside assigned bundles"):
            propose(
                [bundle],
                bundle_refs=["proposals/evidence/RUN/WORK.json"],
                center_id=center["center_id"],
                draft=draft,
                run_id="RUN-CENTER-PROFILES",
                agent_id="synthesis-public-01",
                agent_registry=json.loads(
                    (self.root / "config" / "agent-registry.json").read_text(
                        encoding="utf-8"
                    )
                ),
                center_registry=self.registry,
            )

    def test_profile_inherits_only_stronger_current_predecessor_fields(self):
        center = self.registry["centers"][0]
        fields = {}
        predecessor = {
            "run_id": "RUN-CENTER-PREVIOUS",
            "center_id": center["center_id"],
        }
        for field in self.registry["default_profile_fields"]:
            fields[field] = {
                "status": "unknown",
                "summary": "",
                "as_of": None,
                "evidence_refs": [],
            }
            predecessor[field] = {
                "status": "unknown",
                "summary": "",
                "as_of": None,
                "evidence_refs": [],
            }
        fields["current_system"] = {
            "status": "verified",
            "summary": "New current-system Evidence.",
            "as_of": "2026-08-24",
            "evidence_refs": ["EVD-CURRENT"],
        }
        predecessor["current_system"] = {
            "status": "partial",
            "summary": "Older weaker system Evidence.",
            "as_of": "2026-08-20",
            "evidence_refs": ["EVD-PREVIOUS-WEAK"],
        }
        predecessor["facility"] = {
            "status": "verified",
            "summary": "Previous facility Evidence remains current.",
            "as_of": "2026-08-20",
            "evidence_refs": ["EVD-PREVIOUS"],
        }
        predecessor["power"] = {
            "status": "verified",
            "summary": "Stale power Evidence.",
            "as_of": "2025-01-01",
            "evidence_refs": ["EVD-STALE"],
        }
        draft = merge_with_predecessor(
            {"evidence_as_of": "2026-08-24", "fields": fields},
            predecessor,
            evidence_as_of="2026-08-24",
            maximum_age_days=90,
        )
        self.assertEqual(["facility"], draft["inheritance"]["inherited_fields"])
        self.assertEqual("verified", draft["fields"]["current_system"]["status"])
        self.assertEqual("unknown", draft["fields"]["power"]["status"])
        current_bundle = {
            "object_type": "evidence",
            "run_id": "RUN-CENTER-CURRENT",
            "origin_group_ids": ["ORG-CURRENT"],
            "has_primary_source": True,
            "evidence_candidates": [{"evidence_id": "EVD-CURRENT"}],
        }
        previous_bundle = {
            "object_type": "evidence",
            "run_id": "RUN-CENTER-PREVIOUS",
            "origin_group_ids": ["ORG-PREVIOUS"],
            "has_primary_source": True,
            "evidence_candidates": [{"evidence_id": "EVD-PREVIOUS"}],
        }
        profile = propose(
            [current_bundle, previous_bundle],
            bundle_refs=["current.json", "previous.json"],
            center_id=center["center_id"],
            draft=draft,
            run_id="RUN-CENTER-CURRENT",
            agent_id="synthesis-public-01",
            agent_registry=json.loads(
                (self.root / "config" / "agent-registry.json").read_text(encoding="utf-8")
            ),
            center_registry=self.registry,
            predecessor_profile=predecessor,
            predecessor_ref="proposals/center-profiles/RUN-CENTER-PREVIOUS/profile.json",
            predecessor_digest=stable_digest(predecessor),
            created_at="2026-08-24T00:00:00Z",
        )
        self.assertEqual(["facility"], profile["predecessor"]["inherited_fields"])
        self.assertEqual(
            ["RUN-CENTER-CURRENT", "RUN-CENTER-PREVIOUS"],
            profile["evidence_run_ids"],
        )
        self.assertEqual(["ORG-CURRENT", "ORG-PREVIOUS"], profile["origin_group_ids"])


if __name__ == "__main__":
    unittest.main()
