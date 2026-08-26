from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "reviews" / "consensus-packages" / "CRP-P0-ROADMAPS-V02"
sys.path.insert(0, str(ROOT / "tools"))

from evaluate_consensus_review_package import evaluate  # noqa: E402


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class ConsensusReviewPackageTests(unittest.TestCase):
    def setUp(self):
        self.manifest_path = PACKAGE / "manifest.json"
        self.assertTrue(self.manifest_path.exists(), "commit-pinned package must be generated")
        self.manifest = load_json(self.manifest_path)

    def _registered_reviewer(self, index, role="validator"):
        return {
            "agent_id": f"independent-reviewer-{index}",
            "enabled": True,
            "role": role,
            "provider": f"Provider-{index}",
            "model_family": f"Model-{index}",
            "prompt_profile": "independent-roadmap-review-v1",
            "agent_independence_group": f"independent-group-{index}",
            "review_origin_group": f"origin-reviewer-{index}",
            "harness_id": f"HAR-REVIEWER-{index}",
            "harness_repository_url": f"https://github.com/example/review-harness-{index}",
            "harness_commit": str(index) * 40,
            "network_access": "public-web",
            "data_clearance": "public",
            "write_scope": ["assessments", "runs"],
        }

    def _review(self, agent, registry_digest, verdict="support"):
        return {
            "schema_version": "0.1.0",
            "review_id": f"CRV-{agent['agent_id'].upper()}",
            "package_id": self.manifest["package_id"],
            "base_commit": self.manifest["base_commit"],
            "package_manifest_digest": hashlib.sha256(self.manifest_path.read_bytes()).hexdigest(),
            "reviewer": {
                "agent_id": agent["agent_id"],
                "role": agent["role"],
                "provider": agent["provider"],
                "model_family": agent["model_family"],
                "prompt_profile": agent["prompt_profile"],
                "independence_group": agent["agent_independence_group"],
                "origin_group": agent["review_origin_group"],
                "harness_id": agent["harness_id"],
                "harness_repository_url": agent["harness_repository_url"],
                "harness_commit": agent["harness_commit"],
            },
            "registry_snapshot_digest": registry_digest,
            "overall_verdict": verdict,
            "primary_source_checks": [
                {
                    "unit_id": unit["unit_id"],
                    "selector": requirement["selector"],
                    **requirement["source_options"][0],
                    "outcome": "supports",
                    "notes": "The registered primary source and cited roadmap claim were checked.",
                }
                for unit in self.manifest["review_units"]
                for requirement in unit["primary_source_requirements"]
            ],
            "unit_assessments": [
                {
                    "unit_id": unit["unit_id"],
                    "verdict": verdict,
                    "confidence": 0.8,
                    "checks": {check: "pass" for check in unit["required_checks"]},
                    "observations": ["Pinned artifacts and cited evidence were checked."],
                    "objections": [],
                }
                for unit in self.manifest["review_units"]
            ],
            "critical_objections": [],
            "reviewed_at": self.manifest["created_at"],
        }

    def _evaluate_synthetic(self, reviews, agents):
        artifact_digests = {
            artifact["path"]: artifact["sha256"]
            for artifact in self.manifest["artifact_manifest"]
        }
        registry_digest = artifact_digests["config/agent-registry.json"]
        registry = {"schema_version": "0.1.0", "registry_status": "active", "agents": agents}

        def fake_digest(_root, _commit, path):
            return artifact_digests.get(path)

        def fake_json(_root, _commit, path):
            if path == "config/agent-registry.json":
                return registry
            return load_json(ROOT / path)

        with tempfile.TemporaryDirectory(dir=ROOT) as tmp:
            root = Path(tmp)
            manifest_path = root / "manifest.json"
            manifest_path.write_bytes(self.manifest_path.read_bytes())
            assessment_dir = root / self.manifest["submission"]["assessment_directory"]
            assessment_dir.mkdir(parents=True)
            for index, review in enumerate(reviews):
                (assessment_dir / f"review-{index}.json").write_text(
                    json.dumps(review), encoding="utf-8"
                )
            with patch("evaluate_consensus_review_package.committed_digest", side_effect=fake_digest), patch(
                "evaluate_consensus_review_package.committed_json", side_effect=fake_json
            ):
                return evaluate(root, manifest_path)

    def test_package_covers_six_roadmaps_and_shared_review_units(self):
        units = self.manifest["review_units"]
        self.assertEqual(12, len(units))
        self.assertEqual(6, sum(unit["kind"] == "roadmap" for unit in units))
        self.assertIn(
            "CRU-ROADMAP-REFERENCE", {unit["unit_id"] for unit in units}
        )
        self.assertEqual(
            {"center-profile", "cross-roadmap", "coverage-gap", "scenario", "publication-assurance"},
            {unit["kind"] for unit in units if unit["kind"] != "roadmap"},
        )
        self.assertTrue(all(len(unit["required_checks"]) >= 4 for unit in units))
        self.assertTrue(all(unit["falsification_prompts_ja"] for unit in units))
        summary = self.manifest["portfolio_summary"]
        self.assertEqual(6, summary["roadmap_count"])
        self.assertGreaterEqual(summary["milestone_count"], 130)
        self.assertGreaterEqual(summary["source_count"], 91)
        self.assertGreaterEqual(summary["unique_source_url_count"], 80)
        self.assertEqual(
            summary["source_count"] - summary["unique_source_url_count"],
            summary["duplicate_source_registration_count"],
        )
        self.assertGreaterEqual(summary["coverage_gap_count"], 30)
        self.assertEqual(14, summary["dependency_count"])
        self.assertEqual(3, summary["scenario_count"])
        pinned_paths = {artifact["path"] for artifact in self.manifest["artifact_manifest"]}
        self.assertIn("knowledge/public/roadmap-reference-data.json", pinned_paths)
        self.assertIn("schemas/roadmap-reference-data.schema.json", pinned_paths)
        self.assertIn("knowledge/public/audits/roadmap-gap-queue.json", pinned_paths)
        self.assertIn("knowledge/public/audits/roadmap-source-triage.json", pinned_paths)
        self.assertIn("tools/run_controller.py", pinned_paths)
        self.assertIn(".github/workflows/weekly-coordinator.yml", pinned_paths)
        self.assertIn("config/roadmap-gap-query-overrides.json", pinned_paths)
        self.assertIn("config/monitors/MON-MEMORY-001.json", pinned_paths)

    def test_every_artifact_digest_matches_the_pinned_git_object(self):
        for artifact in self.manifest["artifact_manifest"]:
            result = subprocess.run(
                ["git", "show", f"{self.manifest['base_commit']}:{artifact['path']}"],
                cwd=ROOT,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(
                artifact["sha256"],
                hashlib.sha256(result.stdout).hexdigest(),
                artifact["path"],
            )

    def test_every_review_unit_uses_only_pinned_artifacts(self):
        pinned = {artifact["path"] for artifact in self.manifest["artifact_manifest"]}
        for unit in self.manifest["review_units"]:
            self.assertLessEqual(set(unit["artifact_paths"]), pinned, unit["unit_id"])

    def test_empty_review_set_is_honestly_incomplete(self):
        result = evaluate(ROOT, self.manifest_path)
        self.assertEqual("incomplete", result["status"])
        self.assertEqual([], result["integrity_errors"])
        self.assertEqual([], result["review_results"]["eligible_review_ids"])
        self.assertEqual({}, result["review_results"]["review_file_digests"])
        self.assertEqual(0, result["counts"]["assessments"])
        self.assertIn("minimum_assessments", result["unmet_requirements"])
        self.assertIn("falsification_review", result["unmet_requirements"])
        self.assertEqual(
            hashlib.sha256(self.manifest_path.read_bytes()).hexdigest(),
            result["package_manifest_digest"],
        )

    def test_author_group_is_explicitly_disallowed(self):
        independence = self.manifest["independence_requirements"]
        self.assertIn(independence["author_group"], independence["disallowed_as_independent"])
        self.assertTrue(self.manifest["consensus_policy"]["require_human_decision"])
        self.assertGreaterEqual(self.manifest["consensus_policy"]["minimum_model_families"], 3)
        self.assertGreaterEqual(self.manifest["consensus_policy"]["minimum_providers"], 2)
        self.assertGreaterEqual(self.manifest["consensus_policy"]["minimum_harnesses"], 2)

    def test_template_requires_a_primary_source_check_for_every_key_evidence_milestone(self):
        template = load_json(PACKAGE / "review-template.json")
        expected = {
            (unit["unit_id"], requirement["selector"])
            for unit in self.manifest["review_units"]
            for requirement in unit["primary_source_requirements"]
        }
        self.assertEqual(
            expected,
            {(check["unit_id"], check["selector"]) for check in template["primary_source_checks"]},
        )
        self.assertGreaterEqual(len(expected), 50)

    def test_roadmap_units_select_every_milestone(self):
        for unit in self.manifest["review_units"]:
            if unit["kind"] != "roadmap":
                continue
            path = next(path for path in unit["artifact_paths"] if path.startswith("knowledge/public/roadmaps/"))
            roadmap = load_json(ROOT / path)
            milestone_ids = {
                milestone["milestone_id"]
                for lane in roadmap["lanes"]
                for milestone in lane["milestones"]
            }
            self.assertLessEqual(milestone_ids, set(unit["selectors"]), unit["unit_id"])

    def test_four_registered_diverse_reviews_reach_only_human_decision(self):
        registry_digest = next(
            item["sha256"] for item in self.manifest["artifact_manifest"]
            if item["path"] == "config/agent-registry.json"
        )
        agents = [self._registered_reviewer(index, "critic" if index == 4 else "validator") for index in range(1, 5)]
        reviews = [
            self._review(agent, registry_digest, "uncertain" if agent["role"] == "critic" else "support")
            for agent in agents
        ]
        result = self._evaluate_synthetic(reviews, agents)
        self.assertEqual("ready-for-human-decision", result["status"])
        self.assertEqual([], result["integrity_errors"])
        self.assertEqual(3, result["counts"]["support"])
        self.assertEqual(3, result["counts"]["support_model_families"])
        self.assertEqual(3, result["counts"]["support_providers"])
        self.assertEqual(3, result["counts"]["support_harnesses"])
        self.assertEqual(4, len(result["review_results"]["eligible_review_ids"]))
        self.assertEqual(4, len(result["review_results"]["review_file_digests"]))
        self.assertEqual([], result["review_results"]["ineligible_reviews"])

    def test_tampered_primary_source_identity_invalidates_review(self):
        registry_digest = next(
            item["sha256"] for item in self.manifest["artifact_manifest"]
            if item["path"] == "config/agent-registry.json"
        )
        agents = [self._registered_reviewer(index, "critic" if index == 4 else "validator") for index in range(1, 5)]
        reviews = [self._review(agent, registry_digest) for agent in agents]
        reviews[0]["primary_source_checks"][0]["source_url"] = "https://example.invalid/tampered"
        result = self._evaluate_synthetic(reviews, agents)
        self.assertEqual("incomplete", result["status"])
        self.assertTrue(any("primary_source_identity_mismatch" in item for item in result["integrity_errors"]))
        self.assertEqual(3, len(result["review_results"]["eligible_review_ids"]))
        self.assertEqual(1, len(result["review_results"]["ineligible_reviews"]))

    def test_support_from_one_model_family_cannot_pass(self):
        registry_digest = next(
            item["sha256"] for item in self.manifest["artifact_manifest"]
            if item["path"] == "config/agent-registry.json"
        )
        agents = [self._registered_reviewer(index, "critic" if index == 4 else "validator") for index in range(1, 5)]
        for agent in agents[:3]:
            agent["provider"] = "Provider-shared"
            agent["model_family"] = "Model-shared"
        reviews = [
            self._review(agent, registry_digest, "uncertain" if agent["role"] == "critic" else "support")
            for agent in agents
        ]
        result = self._evaluate_synthetic(reviews, agents)
        self.assertEqual("incomplete", result["status"])
        self.assertIn("minimum_model_families", result["unmet_requirements"])
        self.assertIn("minimum_providers", result["unmet_requirements"])

    def test_support_from_one_harness_cannot_pass(self):
        registry_digest = next(
            item["sha256"] for item in self.manifest["artifact_manifest"]
            if item["path"] == "config/agent-registry.json"
        )
        agents = [self._registered_reviewer(index, "critic" if index == 4 else "validator") for index in range(1, 5)]
        for agent in agents[:3]:
            agent["harness_repository_url"] = "https://github.com/example/shared-harness"
        reviews = [
            self._review(agent, registry_digest, "uncertain" if agent["role"] == "critic" else "support")
            for agent in agents
        ]
        result = self._evaluate_synthetic(reviews, agents)
        self.assertEqual("incomplete", result["status"])
        self.assertEqual(1, result["counts"]["support_harnesses"])
        self.assertIn("minimum_harnesses", result["unmet_requirements"])

    def test_self_declared_origin_or_harness_cannot_spoof_registry(self):
        registry_digest = next(
            item["sha256"] for item in self.manifest["artifact_manifest"]
            if item["path"] == "config/agent-registry.json"
        )
        agent = self._registered_reviewer(1)
        review = self._review(agent, registry_digest)
        review["reviewer"]["origin_group"] = "forged-origin"
        review["reviewer"]["harness_commit"] = "f" * 40
        result = self._evaluate_synthetic([review], [agent])
        self.assertEqual([], result["review_results"]["eligible_review_ids"])
        self.assertTrue(
            any("reviewer_registry_provenance_mismatch" in item for item in result["integrity_errors"])
        )

    def test_reviewer_without_registry_pinned_harness_is_ineligible(self):
        registry_digest = next(
            item["sha256"] for item in self.manifest["artifact_manifest"]
            if item["path"] == "config/agent-registry.json"
        )
        agent = self._registered_reviewer(1)
        review = self._review(agent, registry_digest)
        del agent["harness_commit"]
        result = self._evaluate_synthetic([review], [agent])
        self.assertEqual([], result["review_results"]["eligible_review_ids"])
        self.assertTrue(
            any("reviewer_registry_provenance_unconfigured" in item for item in result["integrity_errors"])
        )

    def test_overall_support_cannot_hide_a_refuted_unit(self):
        registry_digest = next(
            item["sha256"] for item in self.manifest["artifact_manifest"]
            if item["path"] == "config/agent-registry.json"
        )
        agent = self._registered_reviewer(1)
        review = self._review(agent, registry_digest)
        review["unit_assessments"][0]["verdict"] = "refute"
        result = self._evaluate_synthetic([review], [agent])
        self.assertEqual([], result["review_results"]["eligible_review_ids"])
        self.assertTrue(
            any("support_verdict_has_non_support_units" in item for item in result["integrity_errors"])
        )

    def test_overall_support_requires_passing_checks_and_supporting_sources(self):
        registry_digest = next(
            item["sha256"] for item in self.manifest["artifact_manifest"]
            if item["path"] == "config/agent-registry.json"
        )
        agent = self._registered_reviewer(1)
        review = self._review(agent, registry_digest)
        first_check = next(iter(review["unit_assessments"][0]["checks"]))
        review["unit_assessments"][0]["checks"][first_check] = "fail"
        review["primary_source_checks"][0]["outcome"] = "contradicts"
        result = self._evaluate_synthetic([review], [agent])
        self.assertEqual([], result["review_results"]["eligible_review_ids"])
        self.assertTrue(
            any("support_verdict_has_non_passing_checks" in item for item in result["integrity_errors"])
        )
        self.assertTrue(
            any("support_verdict_has_non_supporting_sources" in item for item in result["integrity_errors"])
        )

    def test_review_before_package_creation_is_ineligible(self):
        registry_digest = next(
            item["sha256"] for item in self.manifest["artifact_manifest"]
            if item["path"] == "config/agent-registry.json"
        )
        agent = self._registered_reviewer(1)
        review = self._review(agent, registry_digest)
        review["reviewed_at"] = "2026-08-25T00:00:00Z"
        result = self._evaluate_synthetic([review], [agent])
        self.assertEqual([], result["review_results"]["eligible_review_ids"])
        self.assertTrue(
            any("review_before_package_created" in item for item in result["integrity_errors"])
        )

    def test_future_review_is_ineligible(self):
        registry_digest = next(
            item["sha256"] for item in self.manifest["artifact_manifest"]
            if item["path"] == "config/agent-registry.json"
        )
        agent = self._registered_reviewer(1)
        review = self._review(agent, registry_digest)
        review["reviewed_at"] = "2026-08-27T00:00:00Z"
        result = self._evaluate_synthetic([review], [agent])
        self.assertEqual([], result["review_results"]["eligible_review_ids"])
        self.assertTrue(
            any("review_after_evaluation_window" in item for item in result["integrity_errors"])
        )

    def test_review_time_requires_an_explicit_utc_offset(self):
        registry_digest = next(
            item["sha256"] for item in self.manifest["artifact_manifest"]
            if item["path"] == "config/agent-registry.json"
        )
        agent = self._registered_reviewer(1)
        review = self._review(agent, registry_digest)
        review["reviewed_at"] = "2026-08-26T00:00:00"
        result = self._evaluate_synthetic([review], [agent])
        self.assertEqual([], result["review_results"]["eligible_review_ids"])
        self.assertTrue(
            any("reviewed_at_invalid" in item for item in result["integrity_errors"])
        )

    def test_package_creation_cannot_be_after_evaluation(self):
        result = evaluate(
            ROOT,
            self.manifest_path,
            evaluated_at="2020-01-01T00:00:00Z",
        )
        self.assertIn(
            "package_created_after_evaluation_window",
            result["integrity_errors"],
        )

    def test_review_is_bound_to_exact_package_manifest_bytes(self):
        registry_digest = next(
            item["sha256"] for item in self.manifest["artifact_manifest"]
            if item["path"] == "config/agent-registry.json"
        )
        agent = self._registered_reviewer(1)
        review = self._review(agent, registry_digest)
        review["package_manifest_digest"] = "f" * 64
        result = self._evaluate_synthetic([review], [agent])
        self.assertEqual([], result["review_results"]["eligible_review_ids"])
        self.assertTrue(
            any("package_manifest_digest_mismatch" in item for item in result["integrity_errors"])
        )


if __name__ == "__main__":
    unittest.main()
