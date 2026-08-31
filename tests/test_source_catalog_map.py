from __future__ import annotations

import json
import copy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_source_catalog_map import build, read_json, WATCH_REGISTRY_PATH  # noqa: E402
from validate_repository import validate_source_watch_registry  # noqa: E402


class SourceCatalogMapTests(unittest.TestCase):
    def test_added_analytical_and_roadmap_hubs_have_bounded_roles(self):
        registry = json.loads((ROOT / "config/source-watch-registry.json").read_text())
        by_id = {item["watch_id"]: item for item in registry["targets"]}
        expected = {
            "WATCH-SEMIANALYSIS": ("https://semianalysis.com/", "discovery-lead"),
            "WATCH-SEMIANALYSIS-ARCHIVE": ("https://newsletter.semianalysis.com/archive", "discovery-lead"),
            "WATCH-IEEE-ROADMAPS": ("https://roadmaps.ieee.org/roadmaps/", "roadmap-context"),
            "WATCH-IEEE-IRDS": ("https://irds.ieee.org/", "roadmap-context"),
            "WATCH-IEEE-HIR": ("https://eps.ieee.org/technology/heterogeneous-integration-roadmap/", "roadmap-context"),
        }
        self.assertEqual([], validate_source_watch_registry(ROOT))
        for watch_id, (url, role) in expected.items():
            with self.subTest(watch_id=watch_id):
                target = by_id[watch_id]
                self.assertEqual(url, target["canonical_url"])
                self.assertEqual("public-anonymous-only", target["usage_policy"]["access"])
                self.assertEqual(role, target["usage_policy"]["evidence_role"])
                self.assertTrue(target["usage_policy"]["notes_ja"])
                self.assertTrue(target["usage_policy"]["notes_en"])
                self.assertTrue(target["change_policy"]["candidate_requires_primary_evidence"])
                self.assertTrue(target["change_policy"]["consensus_required_for_catalog_update"])

    def test_analysis_cannot_claim_primary_status_or_authenticated_access(self):
        from jsonschema import Draft202012Validator
        schema = json.loads((ROOT / "schemas/source-watch-registry.schema.json").read_text())
        original = json.loads((ROOT / "config/source-watch-registry.json").read_text())
        validator = Draft202012Validator(schema)
        self.assertEqual([], list(validator.iter_errors(original)))
        for change in ("role", "access", "missing-policy", "missing-consensus"):
            registry = copy.deepcopy(original)
            target = next(t for t in registry["targets"] if t["watch_id"] == "WATCH-SEMIANALYSIS")
            if change == "role":
                target["usage_policy"]["evidence_role"] = "roadmap-context"
            elif change == "access":
                target["usage_policy"]["access"] = "authenticated"
            elif change == "missing-policy":
                del target["usage_policy"]
            else:
                del target["change_policy"]["consensus_required_for_catalog_update"]
            with self.subTest(change=change):
                self.assertTrue(list(validator.iter_errors(registry)))

    def test_watch_registration_alone_does_not_create_evidence(self):
        sources = json.loads((ROOT / "config/source-registry.json").read_text())
        self.assertFalse(next(c for c in sources["source_classes"] if c["class_id"] == "independent-analysis")["default_primary"])
        def without_watches(path):
            value = read_json(path)
            if path == ROOT / WATCH_REGISTRY_PATH:
                value["targets"] = []
            return value
        with patch("build_source_catalog_map.read_json", side_effect=without_watches):
            without = build(ROOT)
        with_watches = build(ROOT)
        for entry in with_watches["entries"]:
            entry["watch_ids"] = []
        self.assertEqual(without, with_watches)

    def test_checked_in_map_is_deterministic(self):
        expected = json.loads(
            (ROOT / "knowledge/public/source-catalog-map.json").read_text(encoding="utf-8")
        )
        self.assertEqual(expected, build(ROOT))

    def test_every_mapping_reaches_a_catalog_topic_and_registered_evidence(self):
        result = build(ROOT)
        self.assertGreater(len(result["entries"]), 200)
        for entry in result["entries"]:
            with self.subTest(url=entry["canonical_url"]):
                self.assertTrue(entry["topic_links"])
                self.assertTrue(
                    entry["roadmap_source_refs"] or entry["catalog_source_refs"]
                )

    def test_every_topic_decision_source_is_mapped_as_direct_evidence(self):
        decision_support = json.loads(
            (ROOT / "knowledge/public/topic-decision-support.json").read_text(
                encoding="utf-8"
            )
        )
        entries_by_url = {
            entry["canonical_url"]: entry for entry in build(ROOT)["entries"]
        }
        result = build(ROOT)
        mapped_source_ids = {
            ref["source_id"]
            for entry in result["entries"]
            for ref in entry["catalog_source_refs"]
        }
        all_source_ids = {source["source_id"] for source in decision_support["sources"]}
        self.assertEqual(
            all_source_ids,
            mapped_source_ids | set(result["unmapped_catalog_source_ids"]),
        )
        self.assertFalse(
            mapped_source_ids & set(result["unmapped_catalog_source_ids"])
        )
        for entry in entries_by_url.values():
            direct_topics = {
                link["topic_id"]
                for link in entry["topic_links"]
                if link["mapping_basis"] == "direct-topic-evidence"
            }
            for catalog_ref in entry["catalog_source_refs"]:
                self.assertTrue(catalog_ref["topic_ids"])
                self.assertTrue(
                    set(catalog_ref["topic_ids"]).issubset(direct_topics)
                )

    def test_mext_committee_is_a_watch_target_not_inferred_evidence(self):
        registry = json.loads(
            (ROOT / "config/source-watch-registry.json").read_text(encoding="utf-8")
        )
        committee = next(
            item for item in registry["targets"]
            if item["watch_id"] == "WATCH-MEXT-HPCI-COMMITTEE"
        )
        self.assertIn("CROSS-10", committee["topic_ids"])
        self.assertTrue(committee["change_policy"]["consensus_required_for_catalog_update"])


if __name__ == "__main__":
    unittest.main()
