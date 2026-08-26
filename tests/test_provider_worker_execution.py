from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from execute_provider_work_item import (  # noqa: E402
    ProviderExecutionError,
    materialize_provider_response,
)
from openfs_runtime import stable_digest  # noqa: E402


class ProviderWorkerExecutionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        shutil.copytree(ROOT / "schemas", self.root / "schemas")
        self.output_ref = "assessments/ASM-000001.json"
        core = {
            "schema_version": "0.1.0",
            "invocation_id": "WINV-AAAAAAAAAAAAAAAA",
            "run_id": "RUN-TEST",
            "work_item_id": "WORK-000001",
            "attempt": 1,
            "agent_id": "validator-test",
            "role": "validator",
            "kind": "validation",
            "prepared_at": "2026-08-27T00:00:00Z",
            "provider_binding": {
                "provider": "OpenAI",
                "model_family": "test-family",
                "requested_model_id": "test-model-2026-08-01",
                "prompt_profile": "validation-v1",
                "network_access": "none",
                "data_clearance": "public",
            },
            "task": {"payload": {}, "untrusted_input": True},
            "skill": {
                "skill_id": "source-validation",
                "version": "0.1.0",
                "snapshot_ref": "runs/RUN-TEST/inputs/skills/validation/SKILL.md",
                "digest": "a" * 64,
            },
            "constraints": {
                "information_plane": "public",
                "secret_transport": "environment-only-not-artifact",
                "lease_expires_at": "2026-08-27T01:00:00Z",
                "output_paths": [self.output_ref],
            },
            "provenance": {
                "work_item_ref": "queue/RUN-TEST/WORK-000001.json",
                "work_item_digest": "b" * 64,
                "manifest_ref": "runs/RUN-TEST/manifest.json",
                "manifest_control_digest": "c" * 64,
                "agent_registry_ref": "runs/RUN-TEST/inputs/config/agent-registry.json",
                "agent_registry_digest": "d" * 64,
                "role_permissions_ref": "runs/RUN-TEST/inputs/config/role-permissions.json",
                "role_permissions_digest": "e" * 64,
            },
        }
        self.invocation = {**core, "invocation_digest": stable_digest(core)}
        self.assessment = {
            "schema_version": "0.1.0",
            "assessment_id": "ASM-000001",
            "proposal_id": "PRP-TEST",
            "reviewer_agent_id": "validator-test",
            "agent_independence_group": "test-independent",
            "reviewer_identity": {
                "provider": "OpenAI",
                "model_family": "test-family",
                "prompt_profile": "validation-v1",
                "role": "validator",
            },
            "agent_registry_digest": "d" * 64,
            "run_id": "RUN-TEST",
            "work_item_id": "WORK-000001",
            "verdict": "uncertain",
            "checks": {"citation_entailment": "unknown"},
            "objections": [{"severity": "major", "message": "Independent evidence is incomplete."}],
            "reviewed_at": "2026-08-27T00:30:00Z",
        }
        self.metadata = {
            "resolved_model_version": "test-model-2026-08-01",
            "request_id": "request-public-id",
            "finish_reason": "completed",
            "input_tokens": 100,
            "output_tokens": 20,
            "web_search_requests": 0,
        }
        self.rates = {
            "OPENFS_INPUT_USD_PER_MILLION_TOKENS": "1.0",
            "OPENFS_OUTPUT_USD_PER_MILLION_TOKENS": "2.0",
            "OPENFS_PER_REQUEST_USD": "0",
            "OPENFS_PER_WEB_SEARCH_USD": "0.01",
        }

    def tearDown(self):
        self.temporary.cleanup()

    def materialize(self, bundle, *, require_cost=True):
        with patch.dict(os.environ, self.rates, clear=True):
            return materialize_provider_response(
                self.root,
                self.invocation,
                bundle,
                self.metadata,
                completed_at="2026-08-27T00:30:00Z",
                require_cost=require_cost,
            )

    def test_valid_artifact_is_written_and_result_is_digest_bound(self):
        result = self.materialize(
            {"artifacts": [{"path": self.output_ref, "content": self.assessment}]}
        )
        self.assertEqual("completed", result["status"])
        self.assertEqual([self.output_ref], result["output_refs"])
        self.assertGreater(result["usage"]["cost_usd"], 0)
        result_payload = dict(result)
        digest = result_payload.pop("result_digest")
        self.assertEqual(digest, stable_digest(result_payload))
        self.assertEqual(
            self.assessment,
            json.loads((self.root / self.output_ref).read_text(encoding="utf-8")),
        )

    def test_wrong_path_contract_secret_and_overwrite_fail_closed(self):
        cases = [
            {"artifacts": [{"path": "assessments/ASM-999999.json", "content": self.assessment}]},
            {"artifacts": [{"path": self.output_ref, "content": {"not": "an assessment"}}]},
            {
                "artifacts": [
                    {
                        "path": self.output_ref,
                        "content": {**self.assessment, "api_key": "must-not-persist"},
                    }
                ]
            },
        ]
        for bundle in cases:
            with self.subTest(bundle=bundle), self.assertRaises(ProviderExecutionError):
                self.materialize(bundle)
        path = self.root / self.output_ref
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("existing", encoding="utf-8")
        with self.assertRaisesRegex(ProviderExecutionError, "already exists"):
            self.materialize(
                {"artifacts": [{"path": self.output_ref, "content": self.assessment}]}
            )

    def test_cost_is_never_silently_reported_as_zero_when_rates_are_missing(self):
        with patch.dict(os.environ, {}, clear=True):
            with self.assertRaisesRegex(ProviderExecutionError, "cost measurement"):
                materialize_provider_response(
                    self.root,
                    self.invocation,
                    {"artifacts": [{"path": self.output_ref, "content": self.assessment}]},
                    self.metadata,
                    completed_at="2026-08-27T00:30:00Z",
                    require_cost=True,
                )


if __name__ == "__main__":
    unittest.main()
