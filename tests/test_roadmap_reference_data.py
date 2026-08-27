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
        cls.roadmap_by_id = {
            item["roadmap_id"]: item for item in cls.roadmaps
        }
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

    def test_reference_data_covers_high_value_comparisons(self):
        result = self.collect_fixture(self.payload)
        term_ids = [item["term_id"] for item in result["terms"]]
        comparison_ids = [item["comparison_id"] for item in result["comparison_sets"]]
        self.assertEqual(len(term_ids), len(set(term_ids)))
        self.assertEqual(len(comparison_ids), len(set(comparison_ids)))
        self.assertTrue(
            {
                "TERM-HPL",
                "TERM-HPCG",
                "TERM-MLPERF",
                "TERM-MEGATRON-LM",
                "TERM-DDN-EXASCALER",
                "TERM-AMD-MATRIX-CORE",
                "TERM-SPEC-CPU",
                "TERM-GFARM",
                "TERM-CEPH",
                "TERM-WEKA",
                "TERM-BENCHPARK",
                "TERM-BENCHKIT",
                "TERM-EEA1-GENESIS",
                "TERM-EEA1-SALMON",
                "TERM-EEA1-SCALE-LETKF",
                "TERM-EEA1-E-WAVE",
                "TERM-EEA1-FRONTFLOW-BLUE",
                "TERM-EEA1-LQCD-DWF-HMC",
            }.issubset(term_ids)
        )
        self.assertTrue(
            {
                "CMP-MEMORY-HIERARCHY",
                "CMP-ADVANCED-INTEGRATION",
                "CMP-COMPUTE-PLATFORMS",
                "CMP-INTERCONNECT-ROLES",
                "CMP-PORTABILITY-MODELS",
                "CMP-EVALUATION-METHODS",
                "CMP-AGENT-BENCHMARKS",
                "CMP-AGENT-EVALUATION-CONTROLS",
                "CMP-AGENT-BENCHMARK-IMPORTANCE",
                "CMP-BENCHMARK-IMPORTANCE",
                "CMP-AI-TRAINING-FRAMEWORKS",
                "CMP-STORAGE-DATA-PLATFORMS",
                "CMP-CONTINUOUS-BENCHMARKING",
                "CMP-EEA1-REPRODUCIBILITY",
            }.issubset(comparison_ids)
        )

    def test_benchmark_and_storage_comparisons_keep_required_evidence(self):
        result = self.collect_fixture(self.payload)
        comparisons = {
            item["comparison_id"]: item for item in result["comparison_sets"]
        }
        terms = {item["term_id"]: item for item in result["terms"]}

        benchmark_terms = {
            row["term_id"]
            for row in comparisons["CMP-BENCHMARK-IMPORTANCE"]["rows"]
        }
        self.assertIn("TERM-SPEC-CPU", benchmark_terms)
        self.assertEqual(
            {
                "SRC-WORK043",
                "SRC-WORK044",
            },
            {
                ref["source_id"]
                for ref in terms["TERM-SPEC-CPU"]["source_refs"]
                if ref["source_id"] in {"SRC-WORK043", "SRC-WORK044"}
            },
        )

        agent_terms = {
            row["term_id"]
            for row in comparisons["CMP-AGENT-BENCHMARK-IMPORTANCE"]["rows"]
        }
        self.assertEqual(
            {
                "TERM-HARNESS-BENCH",
                "TERM-HARNESSOPT-BENCH",
                "TERM-EVO-BENCH",
                "TERM-SWE-BENCH",
                "TERM-GAIA",
                "TERM-TAU-BENCH",
                "TERM-PAPERBENCH",
                "TERM-TUA-BENCH",
            },
            agent_terms,
        )

        control_rows = comparisons["CMP-AGENT-EVALUATION-CONTROLS"]["rows"]
        self.assertEqual(agent_terms, {row["term_id"] for row in control_rows})
        self.assertTrue(
            all(
                {cell["column_id"] for cell in row["cells"]}
                == {
                    "configuration",
                    "boundary",
                    "records",
                    "holdout",
                    "openfs-control",
                }
                for row in control_rows
            )
        )

        storage_terms = {
            row["term_id"]
            for row in comparisons["CMP-STORAGE-DATA-PLATFORMS"]["rows"]
        }
        self.assertTrue(
            {"TERM-GFARM", "TERM-CEPH", "TERM-WEKA"}.issubset(storage_terms)
        )

        continuous_terms = {
            row["term_id"]
            for row in comparisons["CMP-CONTINUOUS-BENCHMARKING"]["rows"]
        }
        self.assertEqual({"TERM-BENCHPARK", "TERM-BENCHKIT"}, continuous_terms)

        compute_terms = {
            row["term_id"]
            for row in comparisons["CMP-COMPUTE-PLATFORMS"]["rows"]
        }
        self.assertTrue(
            {"TERM-AMD-MATRIX-CORE", "TERM-CUSTOM-XPU"}.issubset(compute_terms)
        )

        eea1_terms = {
            row["term_id"]
            for row in comparisons["CMP-EEA1-REPRODUCIBILITY"]["rows"]
        }
        self.assertEqual(
            {
                "TERM-EEA1-GENESIS",
                "TERM-EEA1-SALMON",
                "TERM-EEA1-SCALE-LETKF",
                "TERM-EEA1-E-WAVE",
                "TERM-EEA1-FRONTFLOW-BLUE",
                "TERM-EEA1-LQCD-DWF-HMC",
            },
            eea1_terms,
        )

    def test_new_research_tracks_keep_observed_events_distinct_from_plans(self):
        portability = self.roadmap_by_id["RM-SSW-PORTABILITY"]
        self.assertIn(
            "PORT-AI-TRAINING",
            {track["track_id"] for track in portability["tracks"]},
        )
        megatron_milestones = {
            milestone["milestone_id"]: milestone
            for lane in portability["lanes"]
            if lane["lane_id"] == "LANE-PORT-MEGATRON"
            for milestone in lane["milestones"]
        }
        release = megatron_milestones["MS-PORT-MEGATRON-2026Q3"]
        self.assertEqual("published", release["maturity"])
        self.assertEqual("observed", release["timing_basis"])
        self.assertTrue(
            {"SRC-PORT030", "SRC-PORT034"}.issubset(release["source_ids"])
        )

        compute = self.roadmap_by_id["RM-HW-COMPUTE"]
        meta_announcement = next(
            milestone
            for lane in compute["lanes"]
            for milestone in lane["milestones"]
            if milestone["milestone_id"] == "MS-COMP-BROADCOM-META-2026Q2"
        )
        self.assertEqual("published", meta_announcement["maturity"])
        self.assertEqual("observed", meta_announcement["timing_basis"])

        jalapeno = next(
            milestone
            for lane in compute["lanes"]
            for milestone in lane["milestones"]
            if milestone["milestone_id"] == "MS-COMP-BROADCOM-JALAPENO-2026Q2"
        )
        self.assertEqual("Q2", jalapeno["quarter"])
        self.assertEqual("observed", jalapeno["timing_basis"])
        self.assertEqual(["SRC-COMP026"], jalapeno["source_ids"])

    def test_storage_and_agent_tracks_keep_primary_source_coverage(self):
        blueprint = self.roadmap_by_id["RM-X-BLUEPRINT"]
        self.assertIn(
            "BLUE-DATA-PLATFORMS",
            {track["track_id"] for track in blueprint["tracks"]},
        )
        self.assertIn(
            "BLUE-CENTER-LIFECYCLE",
            {track["track_id"] for track in blueprint["tracks"]},
        )
        self.assertIn(
            "LANE-BLUE-GFARM",
            {lane["lane_id"] for lane in blueprint["lanes"]},
        )
        infinia_baseline = next(
            milestone
            for lane in blueprint["lanes"]
            if lane["lane_id"] == "LANE-BLUE-DDN-INFINIA"
            for milestone in lane["milestones"]
            if milestone["milestone_id"] == "MS-BLUE-DDN-INFINIA-2026Q3"
        )
        self.assertEqual("observed", infinia_baseline["timing_basis"])
        self.assertEqual(["SRC-BLUE014", "SRC-BLUE015", "SRC-BLUE026"], infinia_baseline["source_ids"])
        vast_release = next(
            milestone
            for lane in blueprint["lanes"]
            if lane["lane_id"] == "LANE-BLUE-VAST"
            for milestone in lane["milestones"]
            if milestone["milestone_id"] == "MS-BLUE-VAST-2026Q3"
        )
        self.assertEqual("observed", vast_release["timing_basis"])
        self.assertIn("SRC-BLUE027", vast_release["source_ids"])
        exascaler_announcement = next(
            milestone
            for lane in blueprint["lanes"]
            if lane["lane_id"] == "LANE-BLUE-DDN-EXASCALER"
            for milestone in lane["milestones"]
            if milestone["milestone_id"] == "MS-BLUE-DDN-EXASCALER-2026Q1"
        )
        self.assertEqual("published", exascaler_announcement["maturity"])
        self.assertEqual(["SRC-BLUE025"], exascaler_announcement["source_ids"])
        gfarm_sources = {
            source_id
            for lane in blueprint["lanes"]
            if lane["lane_id"] == "LANE-BLUE-GFARM"
            for milestone in lane["milestones"]
            for source_id in milestone["source_ids"]
        }
        self.assertTrue({"SRC-BLUE021", "SRC-BLUE022"}.issubset(gfarm_sources))

        lifecycle_milestones = {
            milestone["milestone_id"]: milestone
            for lane in blueprint["lanes"]
            if lane["track_id"] == "BLUE-CENTER-LIFECYCLE"
            for milestone in lane["milestones"]
        }
        self.assertEqual(
            {
                "MS-BLUE-TSUKUBA-SIRIUS-2026Q1",
                "MS-BLUE-NAGOYA-FLOW2-2026Q4",
                "MS-BLUE-HOKKAIDO-GPU-2027Q2",
                "MS-BLUE-OSAKA-END-2027Q2",
                "MS-BLUE-HBW2-END-2029Q4",
            },
            set(lifecycle_milestones),
        )
        hokkaido = lifecycle_milestones["MS-BLUE-HOKKAIDO-GPU-2027Q2"]
        self.assertIn("32基", hokkaido["detail_ja"])
        self.assertNotIn("32 GPUノード", hokkaido["detail_ja"])
        self.assertIn("32 refers to GPUs", hokkaido["detail_en"])
        public_summaries = (
            ROOT / "knowledge" / "public" / "topic-summaries.json"
        ).read_text(encoding="utf-8")
        self.assertNotIn("32 GPUノード", public_summaries)
        self.assertNotIn("32-GPU-node", public_summaries)

        workloads = self.roadmap_by_id["RM-APP-WORKLOADS"]
        continuous_track = next(
            track for track in workloads["tracks"] if track["track_id"] == "WORK-CB"
        )
        self.assertIn("SRC-WORK045", continuous_track["source_ids"])
        continuous_sources = {
            source_id
            for lane in workloads["lanes"]
            if lane["lane_id"] == "LANE-WORK-CB"
            for milestone in lane["milestones"]
            for source_id in milestone["source_ids"]
        }
        self.assertTrue({"SRC-WORK008", "SRC-WORK045"}.issubset(continuous_sources))
        ai_track = next(
            track for track in workloads["tracks"] if track["track_id"] == "WORK-AI"
        )
        self.assertTrue(
            {"SRC-WORK034", "SRC-WORK035"}.issubset(ai_track["source_ids"])
        )
        mlperf_milestone_sources = {
            milestone["milestone_id"]: set(milestone["source_ids"])
            for lane in workloads["lanes"]
            if lane["lane_id"] == "LANE-WORK-MLPERF"
            for milestone in lane["milestones"]
        }
        self.assertIn("SRC-WORK035", mlperf_milestone_sources["MS-WORK-MLPERF-2026"])
        self.assertIn(
            "SRC-WORK034",
            mlperf_milestone_sources["MS-WORK-MLPERF-TRAIN-2026"],
        )
        self.assertIn(
            "WORK-AGENT",
            {track["track_id"] for track in workloads["tracks"]},
        )
        agent_sources = {
            source_id
            for lane in workloads["lanes"]
            if lane["track_id"] == "WORK-AGENT"
            for milestone in lane["milestones"]
            for source_id in milestone["source_ids"]
        }
        self.assertTrue(
            {
                "SRC-WORK036",
                "SRC-WORK037",
                "SRC-WORK038",
                "SRC-WORK039",
                "SRC-WORK040",
                "SRC-WORK041",
                "SRC-WORK042",
            }.issubset(agent_sources)
        )

        eea_track = next(
            track for track in workloads["tracks"] if track["track_id"] == "WORK-EEA"
        )
        self.assertTrue(
            {
                "SRC-WORK046",
                "SRC-WORK047",
                "SRC-WORK048",
                "SRC-WORK049",
                "SRC-WORK050",
                "SRC-WORK051",
            }.issubset(eea_track["source_ids"])
        )
        localized_owners = {
            lane["lane_id"]: (lane.get("owner_ja"), lane.get("owner_en"))
            for lane in workloads["lanes"]
            if lane["lane_id"]
            in {
                "LANE-WORK-EEA",
                "LANE-WORK-HPLMXP",
                "LANE-WORK-AGENT-HARNESS",
                "LANE-WORK-AGENT-TASKS",
                "LANE-WORK-AGENT-OPENFS",
                "LANE-WORK-MODEL",
                "LANE-WORK-HPCI",
            }
        }
        self.assertTrue(
            all(owner_ja and owner_en for owner_ja, owner_en in localized_owners.values())
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
