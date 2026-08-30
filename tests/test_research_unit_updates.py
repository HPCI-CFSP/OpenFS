import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from apply_research_unit_update import audit_updates, profile_for, project, verify_applied
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


if __name__ == "__main__":
    unittest.main()
