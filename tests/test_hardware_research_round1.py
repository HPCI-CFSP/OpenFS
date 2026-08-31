"""Protect the scope and provisional boundaries of the hardware research batch."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOPICS = {"ARCH-01", "ARCH-02", "ARCH-03", "ARCH-04", "ARCH-05", "ARCH-12", "SSW-05"}


def read(path):
    return json.loads((ROOT / path).read_text())


class HardwareResearchRoundTests(unittest.TestCase):
    def test_every_planned_unit_retains_visible_evidence_and_partial_status(self):
        baseline = read("config/research-baseline.json")
        surface = read("knowledge/public/topic-decision-support.json")
        profiles = {profile["topic_id"]: profile for profile in surface["topic_profiles"]}
        units = []
        for topic in baseline["topics"]:
            if topic["topic_id"] not in TOPICS:
                continue
            profile = profiles[topic["topic_id"]]
            visible = {section["section_id"] for section in profile["sections"]
                       if section["section_id"] not in profile.get("archived_section_ids", [])}
            for unit in topic["research_units"]:
                with self.subTest(unit=unit["unit_id"]):
                    units.append(unit["unit_id"])
                    self.assertEqual("partial", unit["status"])
                    self.assertTrue(set(unit["evidence_section_ids"]) <= visible)
                    self.assertTrue(any(s.startswith(("TDS-HW1-", "TDS-HW2-", "TDS-HW3-"))
                                        for s in unit["evidence_section_ids"]))
        self.assertEqual(20, len(units))
        self.assertEqual(20, len(set(units)))

    def test_batch_receipts_cannot_be_confused_with_independent_consensus(self):
        units = set()
        for number in range(19, 33):
            update = read(f"proposals/research-unit-updates/RUP-{number:06d}.json")
            self.assertEqual("provisional", update["research_status"])
            self.assertEqual("incomplete", update["consensus_status"])
            self.assertEqual(1, update["execution"]["agent_count"])
            self.assertEqual(1, update["execution"]["model_count"])
            self.assertTrue(all(check["result"] == "read-primary-single-model"
                                for check in update["source_checks"]))
            units.update(unit["unit_id"] for unit in update["units"])
        self.assertEqual(20, len(units))

    def test_hardware_gaps_stay_open_and_wording_corrections_preserve_history(self):
        surface = read("knowledge/public/topic-decision-support.json")
        gaps = {gap["gap_id"]: gap for gap in surface["coverage_gaps"]}
        for number in range(54, 61):
            self.assertEqual("open", gaps[f"GAP-TDS-{number:03d}"]["status"])
        for topic_id, old_id, new_id in [
            ("ARCH-03", "TDS-HW1-ARCH-03-U01", "TDS-HW3-ARCH-03-U01"),
            ("ARCH-05", "TDS-HW2-ARCH-05-U01", "TDS-HW3-ARCH-05-U01"),
        ]:
            profile = next(p for p in surface["topic_profiles"] if p["topic_id"] == topic_id)
            self.assertIn(old_id, profile["archived_section_ids"])
            self.assertNotIn(new_id, profile["archived_section_ids"])
            section_ids = {s["section_id"] for s in profile["sections"]}
            self.assertTrue({old_id, new_id} <= section_ids)


if __name__ == "__main__":
    unittest.main()
