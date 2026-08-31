import copy
import json
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from apply_research_unit_update import audit_updates, profile_for, project, verify_applied, verify_pinned_input
from openfs_runtime import stable_digest


class ResearchUnitUpdateTests(unittest.TestCase):
    def setUp(self):
        self.baseline = json.loads((ROOT / "config/research-baseline.json").read_text())
        self.surface = json.loads((ROOT / "knowledge/public/topic-decision-support.json").read_text())
        topic = next(t for t in self.baseline["topics"] if t["topic_id"] == "SSW-05")
        profile = profile_for(self.surface, "SSW-05")
        # A separate synthetic update uses only existing public test inputs.
        section = copy.deepcopy(profile["sections"][0])
        section["section_id"] = "TDS-TEST-UNIT-UPDATE"
        for n, item in enumerate(section["items"]):
            item["item_id"] = f"TDI-TEST-UNIT-{n}"
        sources = {s["source_id"]: s for s in self.surface["sources"]}
        used = {sid for i in section["items"] for sid in i["source_ids"]}
        self.bundle = {
            "schema_version": "0.1.0", "update_id": "RUP-000001", "topic_id": "SSW-05",
            "created_at": "2026-08-31T02:00:00+09:00", "base_commit": "b223280aeb8338e8952ae1f0d222327385b86d0a",
            "before_profile_sha256": stable_digest(profile), "human_directive_id": "DIR-900015",
            "research_status": "provisional", "consensus_status": "incomplete",
            "execution": {"mode": "interactive-human-authorized", "agent_count": 1, "model_count": 1,
                          "provider": "test", "model_identity": "fixture; not a review",
                          "security_profile_id": "SEC-PROFILE-REPOSITORY-ONLY", "retrieval_capability": "managed-web"},
            "summary_ja": "テスト", "summary_en": "Test",
            "units": [{"unit_id": topic["research_units"][0]["unit_id"],
                       "before_sha256": stable_digest(topic["research_units"][0]),
                       "evidence_section_ids": [section["section_id"]]}],
            "sections": [section], "archive_section_ids": [],
            "source_checks": [{"source": copy.deepcopy(sources[sid]), "origin_group": "test-origin", "checked_at": "2026-08-31T01:00:00+09:00",
                               "locator": "fixture", "observation_ja": "テスト", "observation_en": "Test",
                               "result": "read-primary-single-model"} for sid in sorted(used)],
            "coverage_gaps": [{"gap_id": "GAP-TDS-999", "topic_ids": ["SSW-05"], "priority": "P1",
                               "question_ja": "未確認", "question_en": "Unconfirmed", "next_action_ja": "確認する",
                               "next_action_en": "Check", "status": "open"}],
            "remaining_work_ja": ["独立検証"], "remaining_work_en": ["Independent validation"]}
        # Do not collide with an actual applied bundle when testing future updates.
        profile.pop("research_updates", None)
        self.bundle["before_profile_sha256"] = stable_digest(profile)

    def apply(self):
        return project(ROOT, self.bundle, self.baseline, self.surface)

    def test_append_only_provisional_and_idempotent(self):
        before = copy.deepcopy(self.surface)
        b, s, changed = self.apply()
        self.assertTrue(changed)
        self.assertEqual(before, self.surface)
        profile = profile_for(s, "SSW-05")
        self.assertEqual(profile_for(before, "SSW-05")["sections"], profile["sections"][:-1])
        self.assertEqual("incomplete", profile["research_updates"][-1]["consensus_status"])
        self.assertFalse(project(ROOT, self.bundle, b, s)[2])
        verify_applied(self.bundle, b, s)

    def test_other_topics_untouched(self):
        b, s, _ = self.apply()
        self.assertEqual([t for t in self.baseline["topics"] if t["topic_id"] != "SSW-05"],
                         [t for t in b["topics"] if t["topic_id"] != "SSW-05"])
        self.assertEqual([p for p in self.surface["topic_profiles"] if p["topic_id"] != "SSW-05"],
                         [p for p in s["topic_profiles"] if p["topic_id"] != "SSW-05"])

    def prepare_initial_profile(self):
        profile = profile_for(self.surface, "SSW-05")
        self.bundle["initial_profile_metadata"] = {key: copy.deepcopy(profile[key])
            for key in ("hpci_decision_dimensions", "related_surface_ids")}
        self.surface["topic_profiles"].remove(profile)
        topic = next(t for t in self.baseline["topics"] if t["topic_id"] == "SSW-05")
        topic["status"] = "not-started"
        for unit in topic["research_units"]:
            unit.update(status="not-started", evidence_section_ids=[])
            unit.pop("latest_update_id", None)
            unit.pop("last_researched_at", None)
        self.bundle["before_profile_sha256"] = stable_digest(None)
        self.bundle["units"][0]["before_sha256"] = stable_digest(topic["research_units"][0])

    def test_correction_can_retain_existing_gaps_without_manufacturing_a_duplicate(self):
        self.bundle["coverage_gaps"] = []
        _, surface, _ = self.apply()
        self.assertEqual(self.surface["coverage_gaps"], surface["coverage_gaps"])
        self.assertEqual(profile_for(self.surface, "SSW-05")["coverage_gap_ids"],
                         profile_for(surface, "SSW-05")["coverage_gap_ids"])

    def test_initial_provisional_profile_must_identify_an_open_gap(self):
        self.prepare_initial_profile()
        self.bundle["coverage_gaps"] = []
        with self.assertRaisesRegex(ValueError, "open Coverage Gap"):
            self.apply()

    def test_retained_gaps_cannot_be_missing_or_belong_only_to_another_topic(self):
        profile = profile_for(self.surface, "SSW-05")
        foreign = next(g for g in self.surface["coverage_gaps"] if "SSW-05" not in g["topic_ids"])
        for gap_id in ("GAP-TDS-MISSING", foreign["gap_id"]):
            with self.subTest(gap_id=gap_id):
                profile["coverage_gap_ids"] = [gap_id]
                self.bundle["before_profile_sha256"] = stable_digest(profile)
                before = copy.deepcopy((self.baseline, self.surface))
                with self.assertRaisesRegex(ValueError, "must exist and cover"):
                    self.apply()
                self.assertEqual(before, (self.baseline, self.surface))

    def test_correction_cannot_rely_only_on_closed_gaps(self):
        self.bundle["coverage_gaps"] = []
        retained = set(profile_for(self.surface, "SSW-05")["coverage_gap_ids"])
        for gap in self.surface["coverage_gaps"]:
            if gap["gap_id"] in retained:
                gap["status"] = "closed"
        with self.assertRaisesRegex(ValueError, "open Coverage Gap"):
            self.apply()

    def test_initial_profile_is_explicit_provisional_and_replayable(self):
        self.prepare_initial_profile()
        before = copy.deepcopy(self.surface)
        baseline, surface, changed = self.apply()
        self.assertTrue(changed)
        self.assertEqual(before, self.surface)
        self.assertIsNone(profile_for(before, "SSW-05"))
        profile = profile_for(surface, "SSW-05")
        self.assertEqual(self.bundle["sections"], profile["sections"])
        self.assertEqual("incomplete", profile["research_updates"][0]["consensus_status"])
        topic = next(t for t in baseline["topics"] if t["topic_id"] == "SSW-05")
        self.assertEqual("partial", topic["research_units"][0]["status"])
        self.assertEqual("not-started", topic["research_units"][1]["status"])
        self.assertFalse(project(ROOT, self.bundle, baseline, surface)[2])
        verify_applied(self.bundle, baseline, surface)

    def test_missing_profile_cannot_be_initialized_implicitly(self):
        self.prepare_initial_profile()
        self.bundle.pop("initial_profile_metadata")
        with self.assertRaisesRegex(ValueError, "explicit initial metadata"):
            self.apply()

    def test_initial_profile_cannot_discard_prior_unit_evidence(self):
        self.prepare_initial_profile()
        topic = next(t for t in self.baseline["topics"] if t["topic_id"] == "SSW-05")
        topic["research_units"][1]["evidence_section_ids"] = ["TDS-OLD-EVIDENCE"]
        with self.assertRaisesRegex(ValueError, "discard existing"):
            self.apply()

    def test_initial_profile_cannot_replace_concurrent_work(self):
        self.prepare_initial_profile()
        self.surface["topic_profiles"].append({"topic_id": "SSW-05", "sections": []})
        with self.assertRaisesRegex(ValueError, "stale profile"):
            self.apply()

    def test_initial_metadata_is_audited(self):
        self.prepare_initial_profile()
        baseline, surface, _ = self.apply()
        profile_for(surface, "SSW-05")["hpci_decision_dimensions"][0]["question_en"] = "Changed"
        with self.assertRaisesRegex(ValueError, "initial profile metadata"):
            verify_applied(self.bundle, baseline, surface)

    def test_publication_uses_the_authorizing_directives_decision(self):
        self.bundle["update_id"] = "RUP-000005"
        self.bundle["human_directive_id"] = "DIR-900016"
        _, surface, _ = self.apply()
        self.assertEqual("PUBDEC-PROCUREMENT-RECONCILIATION-001",
                         surface["publication"]["publication_decision_id"])

    def test_concurrent_profile_edit_rejected(self):
        profile_for(self.surface, "SSW-05")["summary_en"] += " changed"
        with self.assertRaisesRegex(ValueError, "stale profile"):
            self.apply()

    def test_concurrent_unit_edit_rejected(self):
        topic = next(t for t in self.baseline["topics"] if t["topic_id"] == "SSW-05")
        topic["research_units"][0]["question_en"] += " changed"
        with self.assertRaisesRegex(ValueError, "stale research unit"):
            self.apply()

    def test_foreign_unit_rejected(self):
        self.bundle["units"][0]["unit_id"] = "APP-13-U01"
        with self.assertRaisesRegex(ValueError, "wrongly owned"):
            self.apply()

    def test_missing_source_check_rejected(self):
        self.bundle["source_checks"] = self.bundle["source_checks"][:1]
        self.bundle["sections"][0]["items"][0]["source_ids"] = ["SRC-NOT-CHECKED"]
        with self.assertRaisesRegex(ValueError, "checked primary"):
            self.apply()

    def test_source_id_reuse_rejected(self):
        self.bundle["source_checks"][0]["source"]["url"] += "?changed=1"
        with self.assertRaisesRegex(ValueError, "source metadata changed"):
            self.apply()

    def prepare_source_correction(self):
        old = {**self.surface["sources"][0], "source_id": "SRC-TEST-PRIOR"}
        old.pop("correction", None)
        self.surface["sources"].append(old)
        check = copy.deepcopy(self.bundle["source_checks"][0])
        check["source"] = {**old, "source_id": "SRC-TEST-CORRECTED", "source_class": "research-artifact",
                           "correction": {"supersedes_source_id": old["source_id"],
                                          "reason_ja": "公開メタデータの分類を訂正。",
                                          "reason_en": "Correct classification from public metadata."}}
        self.bundle["source_checks"].append(check)
        self.bundle["sections"][0]["items"][0]["source_ids"] = [check["source"]["source_id"]]
        return old, check

    def test_source_metadata_correction_is_append_only_and_idempotent(self):
        old, check = self.prepare_source_correction()
        before = copy.deepcopy(self.surface)
        baseline, surface, changed = self.apply()
        self.assertTrue(changed)
        self.assertEqual(before, self.surface)
        self.assertEqual(old, next(s for s in surface["sources"] if s["source_id"] == old["source_id"]))
        self.assertIn(check["source"], surface["sources"])
        self.assertFalse(project(ROOT, self.bundle, baseline, surface)[2])
        verify_applied(self.bundle, baseline, surface)

    def test_source_correction_cannot_name_an_unrecorded_predecessor(self):
        old, _ = self.prepare_source_correction()
        self.surface["sources"].remove(old)
        with self.assertRaisesRegex(ValueError, "pre-existing source"):
            self.apply()

    def test_new_claims_must_use_corrected_metadata(self):
        old, check = self.prepare_source_correction()
        old_check = {**check, "source": old}
        self.bundle["source_checks"].append(old_check)
        self.bundle["sections"][0]["items"][0]["source_ids"].append(old["source_id"])
        with self.assertRaisesRegex(ValueError, "new claims cannot use superseded"):
            self.apply()

    def test_correction_cannot_leave_active_claim_or_matrix_on_old_metadata(self):
        old, _ = self.prepare_source_correction()
        profile = next(p for p in self.surface["topic_profiles"] if p["topic_id"] != "SSW-05"
                       and not next(t for t in self.baseline["topics"] if t["topic_id"] == p["topic_id"]).get("retirement"))
        item = next(s for s in profile["sections"] if s["section_id"] not in profile.get("archived_section_ids", []))["items"][0]
        item["source_ids"].append(old["source_id"])
        with self.assertRaisesRegex(ValueError, "active claims still"):
            self.apply()
        item["source_ids"].remove(old["source_id"])
        self.surface["platform_matrix"]["platforms"][0]["source_ids"].append(old["source_id"])
        with self.assertRaisesRegex(ValueError, "active matrix or actor"):
            self.apply()

    def test_source_correction_reasons_must_be_nonblank_in_schema(self):
        from jsonschema import ValidationError
        _, check = self.prepare_source_correction()
        check["source"]["correction"]["reason_en"] = " \n "
        with self.assertRaises(ValidationError):
            self.apply()

    def test_archiving_live_unit_evidence_rejected(self):
        profile = profile_for(self.surface, "SSW-05")
        self.bundle["archive_section_ids"] = [profile["sections"][0]["section_id"]]
        topic = next(t for t in self.baseline["topics"] if t["topic_id"] == "SSW-05")
        topic["research_units"][1]["evidence_section_ids"] = self.bundle["archive_section_ids"]
        with self.assertRaisesRegex(ValueError, "archived evidence"):
            self.apply()

    def test_applied_bundle_cannot_be_rewritten(self):
        b, s, _ = self.apply()
        self.bundle["summary_en"] = "changed after application"
        with self.assertRaisesRegex(ValueError, "immutable"):
            project(ROOT, self.bundle, b, s)

    def test_false_consensus_rejected_by_schema(self):
        from jsonschema import ValidationError
        self.bundle["consensus_status"] = "accepted"
        with self.assertRaises(ValidationError):
            self.apply()

    def test_unapproved_target_rejected(self):
        self.bundle["update_id"] = "RUP-999999"
        with self.assertRaisesRegex(ValueError, "publication authorization"):
            self.apply()

    def test_repository_update_audit(self):
        self.assertEqual([], audit_updates(ROOT))

    def test_receipt_cannot_claim_consensus(self):
        b, s, _ = self.apply()
        profile_for(s, "SSW-05")["research_updates"][-1]["consensus_status"] = "accepted"
        with self.assertRaisesRegex(ValueError, "receipt mismatch"):
            verify_applied(self.bundle, b, s)

    def test_applied_gap_cannot_be_silently_closed(self):
        b, s, _ = self.apply()
        s["coverage_gaps"][-1]["status"] = "closed"
        with self.assertRaisesRegex(ValueError, "Coverage Gap"):
            verify_applied(self.bundle, b, s)

    def test_timestamp_and_summary_cannot_drift(self):
        b, s, _ = self.apply()
        profile_for(s, "SSW-05")["summary_en"] = "Unreviewed replacement"
        with self.assertRaisesRegex(ValueError, "summary drifted"):
            verify_applied(self.bundle, b, s)

    def test_predecessor_replay_does_not_require_intermediate_branch_commit(self):
        bundle = json.loads((ROOT / "proposals/research-unit-updates/RUP-000004.json").read_text())
        self.assertEqual("b223280aeb8338e8952ae1f0d222327385b86d0a", bundle["base_commit"])
        verify_pinned_input(ROOT, bundle)
        bundle["predecessor_updates"][0]["bundle_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "predecessor chain"):
            verify_pinned_input(ROOT, bundle)

    def test_cycle_in_predecessor_chain_is_rejected(self):
        bundle = json.loads((ROOT / "proposals/research-unit-updates/RUP-000004.json").read_text())
        bundle["predecessor_updates"][0]["update_id"] = bundle["update_id"]
        with self.assertRaisesRegex(ValueError, "cyclic"):
            verify_pinned_input(ROOT, bundle)

    def test_invalid_predecessor_is_rejected_before_git_or_file_lookup(self):
        from jsonschema import ValidationError
        bundle = json.loads((ROOT / "proposals/research-unit-updates/RUP-000004.json").read_text())
        bundle["predecessor_updates"][0]["update_id"] = "../../outside"
        with patch("apply_research_unit_update.subprocess.run") as git_read, \
                patch("apply_research_unit_update.read") as bundle_read:
            with self.assertRaises(ValidationError):
                verify_pinned_input(ROOT, bundle)
            git_read.assert_not_called()
            bundle_read.assert_not_called()

    def test_projection_does_not_share_mutable_bundle_payloads(self):
        b, s, _ = self.apply()
        expected = copy.deepcopy(self.bundle)
        s["coverage_gaps"][-1]["status"] = "closed"
        profile_for(s, "SSW-05")["sections"][-1]["items"][0]["name_en"] = "Changed"
        self.assertEqual(expected, self.bundle)


if __name__ == "__main__":
    unittest.main()
