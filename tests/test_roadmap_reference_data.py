from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from build_pages_site import (  # noqa: E402
    collect_roadmap_reference_data,
    collect_roadmaps,
)


class RoadmapReferenceDataTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = json.loads(
            (ROOT / "config" / "publication-policy.json").read_text(encoding="utf-8")
        )
        cls.roadmaps = collect_roadmaps(ROOT, cls.policy, False)
        cls.payload = json.loads(
            (ROOT / "knowledge" / "public" / "roadmap-reference-data.json").read_text(
                encoding="utf-8"
            )
        )

    def collect_fixture(self, payload):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            artifact = root / self.policy["included_public_roadmap_reference_data"]
            artifact.parent.mkdir(parents=True)
            artifact.write_text(json.dumps(payload), encoding="utf-8")
            directive = root / "reviews" / "directives" / "DIR-900008.json"
            directive.parent.mkdir(parents=True)
            directive.write_text(
                (ROOT / "reviews" / "directives" / "DIR-900008.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            return collect_roadmap_reference_data(
                root, self.policy, self.roadmaps, False
            )

    def test_reference_data_covers_six_high_value_comparisons(self):
        result = self.collect_fixture(self.payload)
        self.assertEqual(34, len(result["terms"]))
        self.assertEqual(
            {
                "CMP-MEMORY-HIERARCHY",
                "CMP-ADVANCED-INTEGRATION",
                "CMP-COMPUTE-PLATFORMS",
                "CMP-INTERCONNECT-ROLES",
                "CMP-PORTABILITY-MODELS",
                "CMP-EVALUATION-METHODS",
            },
            {item["comparison_id"] for item in result["comparison_sets"]},
        )

    def test_unknown_source_reference_fails_closed(self):
        payload = copy.deepcopy(self.payload)
        payload["terms"][0]["source_refs"][0]["source_id"] = "SRC-NOT-REGISTERED"
        with self.assertRaisesRegex(ValueError, "unknown source"):
            self.collect_fixture(payload)

    def test_alias_collision_fails_closed(self):
        payload = copy.deepcopy(self.payload)
        payload["terms"][1]["aliases"].append(payload["terms"][0]["aliases"][0])
        with self.assertRaisesRegex(ValueError, "is shared by"):
            self.collect_fixture(payload)

    def test_comparison_cells_must_match_declared_columns(self):
        payload = copy.deepcopy(self.payload)
        payload["comparison_sets"][0]["rows"][0]["cells"].pop()
        with self.assertRaisesRegex(ValueError, "cells do not match columns"):
            self.collect_fixture(payload)

    def test_comparison_cannot_reference_unknown_term(self):
        payload = copy.deepcopy(self.payload)
        payload["comparison_sets"][0]["rows"][0]["term_id"] = "TERM-NOT-REGISTERED"
        with self.assertRaisesRegex(ValueError, "unknown term"):
            self.collect_fixture(payload)


if __name__ == "__main__":
    unittest.main()
