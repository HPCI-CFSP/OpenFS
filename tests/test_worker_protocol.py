from __future__ import annotations

import json
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from accept_worker_result import validate_result  # noqa: E402
from openfs_runtime import sha256_file, stable_digest  # noqa: E402
from prepare_worker_invocation import prepare  # noqa: E402


class WorkerProtocolTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.run_id = "RUN-WORKER-TEST"
        self.work_item_id = "WORK-000001"
        self.agent_id = "discovery-test"
        self.registry_ref = f"runs/{self.run_id}/inputs/config/agent-registry.json"
        self.permissions_ref = f"runs/{self.run_id}/inputs/config/role-permissions.json"
        self.skill_ref = f"runs/{self.run_id}/inputs/skills/discovery/SKILL.md"
        self.write(self.skill_ref, "# Pinned discovery procedure\n")
        self.registry = {
            "agents": [
                {
                    "agent_id": self.agent_id,
                    "enabled": True,
                    "role": "discovery",
                    "provider": "provider-a",
                    "model_family": "model-a",
                    "prompt_profile": "discovery-v1",
                    "network_access": "public-web",
                    "data_clearance": "public",
                }
            ]
        }
        self.write(self.registry_ref, self.registry)
        self.write(
            self.permissions_ref,
            {
                "roles": {
                    "discovery": {
                        "allowed_write_patterns": ["proposals/sources/**"]
                    }
                }
            },
        )
        self.write(
            f"runs/{self.run_id}/manifest.json",
            {
                "run_id": self.run_id,
                "status": "running",
                "mode": "production",
                "configuration_snapshots": {
                    "config/agent-registry.json": self.registry_ref,
                    "config/role-permissions.json": self.permissions_ref,
                },
            },
        )
        self.output_ref = f"proposals/sources/{self.run_id}/{self.work_item_id}.json"
        self.work_item = {
            "work_item_id": self.work_item_id,
            "run_id": self.run_id,
            "kind": "source-discovery",
            "required_role": "discovery",
            "status": "leased",
            "attempt": 1,
            "payload": {"query": "public HPC roadmap"},
            "output_paths": [self.output_ref],
            "skill": {
                "skill_id": "source-discovery",
                "version": "0.1.0",
                "snapshot_ref": self.skill_ref,
                "digest": sha256_file(self.root / self.skill_ref),
            },
            "lease": {
                "agent_id": self.agent_id,
                "acquired_at": "2026-08-24T05:00:00Z",
                "expires_at": "2026-08-24T06:00:00Z",
            },
        }
        self.write(
            f"queue/{self.run_id}/{self.work_item_id}.json", self.work_item
        )

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, ref, value):
        path = self.root / ref
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(value, str):
            path.write_text(value, encoding="utf-8")
        else:
            path.write_text(json.dumps(value), encoding="utf-8")

    def invocation(self):
        return prepare(
            self.root,
            run_id=self.run_id,
            work_item_id=self.work_item_id,
            agent_id=self.agent_id,
            prepared_at="2026-08-24T05:10:00Z",
        )

    def test_prepares_secret_free_pinned_invocation(self):
        invocation = self.invocation()
        self.assertEqual("public", invocation["constraints"]["information_plane"])
        self.assertEqual("provider-a", invocation["provider_binding"]["provider"])
        self.assertEqual(self.output_ref, invocation["constraints"]["output_paths"][0])
        self.assertEqual(64, len(invocation["invocation_digest"]))

    def test_disabled_agent_and_secret_like_payload_fail_closed(self):
        registry = deepcopy(self.registry)
        registry["agents"][0]["enabled"] = False
        self.write(self.registry_ref, registry)
        with self.assertRaisesRegex(RuntimeError, "disabled Agent"):
            self.invocation()

        self.write(self.registry_ref, self.registry)
        item = deepcopy(self.work_item)
        item["payload"]["api_key"] = "must-not-enter-artifact"
        self.write(f"queue/{self.run_id}/{self.work_item_id}.json", item)
        with self.assertRaisesRegex(ValueError, "secret-like"):
            self.invocation()

    def test_result_pins_provider_usage_and_output_digest(self):
        invocation = self.invocation()
        self.write(self.output_ref, {"public": "structured result"})
        core = {
            "schema_version": "0.1.0",
            "result_id": "WRES-AAAAAAAAAAAAAAAA",
            "invocation_id": invocation["invocation_id"],
            "invocation_digest": invocation["invocation_digest"],
            "agent_id": self.agent_id,
            "status": "completed",
            "completed_at": "2026-08-24T05:20:00Z",
            "provider": {
                "provider": "provider-a",
                "model_family": "model-a",
                "resolved_model_version": "model-a-202608",
                "request_id_digest": "a" * 64,
                "finish_reason": "stop",
            },
            "usage": {
                "input_tokens": 100,
                "output_tokens": 20,
                "cost_usd": 0.03,
                "measurement_note": "Provider usage response and price table v1.",
            },
            "output_refs": [self.output_ref],
            "output_digests": {
                self.output_ref: sha256_file(self.root / self.output_ref)
            },
        }
        result = {**core, "result_digest": stable_digest(core)}
        validate_result(self.root, invocation, result)

        self.write(self.output_ref, {"public": "changed after result"})
        with self.assertRaisesRegex(ValueError, "missing or changed"):
            validate_result(self.root, invocation, result)

    def test_result_outside_lease_or_after_work_item_change_is_rejected(self):
        invocation = self.invocation()
        self.write(self.output_ref, {"public": "structured result"})
        core = {
            "schema_version": "0.1.0",
            "result_id": "WRES-BBBBBBBBBBBBBBBB",
            "invocation_id": invocation["invocation_id"],
            "invocation_digest": invocation["invocation_digest"],
            "agent_id": self.agent_id,
            "status": "completed",
            "completed_at": "2026-08-24T06:00:01Z",
            "provider": {
                "provider": "provider-a",
                "model_family": "model-a",
                "resolved_model_version": None,
                "request_id_digest": None,
                "finish_reason": "stop",
            },
            "usage": {
                "input_tokens": 1,
                "output_tokens": 1,
                "cost_usd": 0.01,
                "measurement_note": "Measured.",
            },
            "output_refs": [self.output_ref],
            "output_digests": {self.output_ref: sha256_file(self.root / self.output_ref)},
        }
        result = {**core, "result_digest": stable_digest(core)}
        with self.assertRaisesRegex(ValueError, "outside the leased"):
            validate_result(self.root, invocation, result)

        core["completed_at"] = "2026-08-24T05:20:00Z"
        result = {**core, "result_digest": stable_digest(core)}
        changed_item = deepcopy(self.work_item)
        changed_item["payload"]["query"] = "changed after invocation"
        self.write(f"queue/{self.run_id}/{self.work_item_id}.json", changed_item)
        with self.assertRaisesRegex(ValueError, "changed after invocation"):
            validate_result(self.root, invocation, result)


if __name__ == "__main__":
    unittest.main()
