from __future__ import annotations

import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from openfs_runtime import stable_digest  # noqa: E402
from record_claim_status import record  # noqa: E402
from validate_repository import validate_claim_status_events  # noqa: E402


class CanonicalClaimStatusTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.write_canonical("CLM-000001", "Original accepted statement.")
        self.directive_ref = "reviews/directives/DIR-000001.json"
        self.directive = {
            "schema_version": "0.1.0",
            "directive_id": "DIR-000001",
            "directive_type": "canonical-status",
            "title": "Withdraw a canonical Claim",
            "instruction": "Record the approved status change exactly as structured.",
            "priority": "high",
            "status": "approved",
            "submitted_by": "Human Reviewer",
            "submitted_at": "2026-08-24T03:00:00Z",
            "claim_targets": ["CLM-000001"],
            "canonical_status_action": "withdrawn",
            "canonical_status_reason": "Later public evidence disproved the statement.",
            "public_information_confirmed": True,
        }
        self.write(self.directive_ref, self.directive)

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, ref, value):
        path = self.root / ref
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value), encoding="utf-8")

    def write_canonical(self, claim_id, statement):
        claim = {
            "claim_id": claim_id,
            "statement": statement,
            "claim_kind": "observed_fact",
            "temporal_scope": "2026-08-24",
            "conditions": [],
            "evidence_ids": ["EVD-000001"],
            "source_lineage_ids": ["LIN-000001"],
            "status": "accepted",
        }
        provenance = {
            "proposal_ref": "proposals/claims/RUN/WORK.json",
            "decision_ref": "decisions/RUN/DEC.json",
        }
        canonical = {
            "canonical_claim_id": claim_id,
            "claim": claim,
            "provenance": provenance,
            "promoted_at": "2026-08-24T01:00:00Z",
            "promotion_digest": stable_digest(
                {"claim": claim, "provenance": provenance}
            ),
        }
        self.write(f"knowledge/claims/{claim_id}.json", canonical)

    def test_withdrawal_is_append_only_and_removes_claim_from_active_view(self):
        output, event = record(
            self.root,
            claim_id="CLM-000001",
            directive_ref=self.directive_ref,
            recorded_by="promotion-agent",
            recorded_at="2026-08-24T04:00:00Z",
        )
        self.assertTrue(output.is_file())
        self.assertEqual("withdrawn", event["action"])
        self.assertTrue((self.root / "knowledge/claims/CLM-000001.json").is_file())
        index = json.loads(
            (self.root / "knowledge/claims/index.json").read_text()
        )
        self.assertEqual(0, index["claim_count"])
        self.assertEqual(1, index["canonical_claim_count"])
        self.assertEqual("CLM-000001", index["inactive_claims"][0]["claim_id"])
        self.assertNotIn("Original accepted statement.", (self.root / "TBD.md").read_text())
        self.assertEqual([], validate_claim_status_events(self.root))

        repeated_output, repeated = record(
            self.root,
            claim_id="CLM-000001",
            directive_ref=self.directive_ref,
            recorded_by="retrying-promotion-agent",
            recorded_at="2026-08-25T04:00:00Z",
        )
        self.assertEqual(output, repeated_output)
        self.assertEqual(event, repeated)

    def test_supersession_requires_and_activates_existing_replacement(self):
        self.write_canonical("CLM-000002", "Corrected accepted statement.")
        directive = deepcopy(self.directive)
        directive["canonical_status_action"] = "superseded"
        directive["canonical_status_reason"] = "A reviewed correction replaces it."
        directive["replacement_claim_id"] = "CLM-000002"
        self.write(self.directive_ref, directive)

        _, event = record(
            self.root,
            claim_id="CLM-000001",
            directive_ref=self.directive_ref,
            recorded_by="promotion-agent",
            recorded_at="2026-08-24T04:00:00Z",
        )
        self.assertEqual("CLM-000002", event["replacement_claim_id"])
        index = json.loads(
            (self.root / "knowledge/claims/index.json").read_text()
        )
        self.assertEqual(["CLM-000002"], [item["claim_id"] for item in index["claims"]])

    def test_non_status_or_unapproved_directive_cannot_change_claim(self):
        directive = deepcopy(self.directive)
        directive["directive_type"] = "publication-approval"
        self.write(self.directive_ref, directive)
        with self.assertRaisesRegex(ValueError, "does not authorize"):
            record(
                self.root,
                claim_id="CLM-000001",
                directive_ref=self.directive_ref,
                recorded_by="promotion-agent",
            )

        directive = deepcopy(self.directive)
        directive["status"] = "proposed"
        self.write(self.directive_ref, directive)
        with self.assertRaisesRegex(ValueError, "not approved"):
            record(
                self.root,
                claim_id="CLM-000001",
                directive_ref=self.directive_ref,
                recorded_by="promotion-agent",
            )

    def test_rejects_claim_path_traversal_before_filesystem_lookup(self):
        with self.assertRaisesRegex(ValueError, "invalid format"):
            record(
                self.root,
                claim_id="../../outside",
                directive_ref=self.directive_ref,
                recorded_by="promotion-agent",
            )

    def test_validator_detects_event_or_directive_tampering(self):
        output, _ = record(
            self.root,
            claim_id="CLM-000001",
            directive_ref=self.directive_ref,
            recorded_by="promotion-agent",
            recorded_at="2026-08-24T04:00:00Z",
        )
        event = json.loads(output.read_text())
        event["reason"] = "Changed after approval."
        output.write_text(json.dumps(event), encoding="utf-8")
        errors = validate_claim_status_events(self.root)
        self.assertTrue(any("event digest differs" in error for error in errors))
        self.assertTrue(any("differs from Directive" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
