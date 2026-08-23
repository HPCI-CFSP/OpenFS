from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from generate_knowledge_views import build_index, generate, render_tbd  # noqa: E402


class KnowledgeViewTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, ref, value):
        path = self.root / ref
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def canonical(self):
        return {
            "canonical_claim_id": "CLM-000001",
            "claim": {
                "claim_id": "CLM-000001",
                "statement": "Accepted canonical statement.",
                "claim_kind": "observed_fact",
                "temporal_scope": "2026-08-24",
                "conditions": [],
                "evidence_ids": ["EVD-000001"],
                "source_lineage_ids": ["LIN-000001"],
                "status": "accepted",
            },
            "provenance": {
                "proposal_ref": "proposals/claims/RUN/WORK.json",
                "decision_ref": "decisions/RUN/DEC.json",
            },
            "promoted_at": "2026-08-24T01:00:00Z",
            "promotion_digest": "a" * 64,
        }

    def test_views_include_only_canonical_accepted_claims(self):
        self.write("knowledge/claims/CLM-000001.json", self.canonical())
        self.write(
            "proposals/claims/RUN/WORK.json",
            {"claim_candidate": {"statement": "Provisional text must not appear."}},
        )

        index = build_index(self.root)
        rendered = render_tbd(index)

        self.assertEqual(1, index["claim_count"])
        self.assertEqual("2026-08-24T01:00:00Z", index["as_of"])
        self.assertIn("Accepted canonical statement.", rendered)
        self.assertNotIn("Provisional text", rendered)

    def test_empty_view_is_explicit_and_generation_is_deterministic(self):
        first = build_index(self.root)
        second = build_index(self.root)
        self.assertEqual(first, second)
        self.assertIn("No canonical Claims", render_tbd(first))

        index_path, tbd_path, generated = generate(self.root)
        self.assertTrue(index_path.is_file())
        self.assertTrue(tbd_path.is_file())
        self.assertEqual(first, generated)


if __name__ == "__main__":
    unittest.main()
