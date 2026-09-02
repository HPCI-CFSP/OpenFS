"""Regression boundaries for the human-authorized September 1 research batch."""
from datetime import datetime
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
TOPICS = {
    "SSW-01", "SSW-03", "SSW-04", "SSW-06", "SSW-08", "SSW-09", "SSW-10", "SSW-16",
    "APP-01", "APP-02", "APP-05", "APP-11", "ARCH-13", "APP-12", "APP-13", "APP-14", "APP-15",
    "ARCH-06", "ARCH-10", "SSW-11", "SSW-12", "SSW-14", "SSW-15", "CROSS-03", "CROSS-05",
    "CROSS-06", "CROSS-14", "CROSS-16", "CROSS-10", "CROSS-15", "ARCH-07", "CROSS-08", "CROSS-11",
}


def read(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class CrossDomainResearchRoundTests(unittest.TestCase):
    def test_first_pass_covers_exactly_53_existing_units_without_consensus(self):
        actual_topics, actual_units = set(), set()
        stop = datetime.fromisoformat("2026-09-01T06:30:00+09:00")
        for number in range(33, 66):
            update = read(f"proposals/research-unit-updates/RUP-{number:06d}.json")
            with self.subTest(update=update["update_id"]):
                self.assertEqual("DIR-900019", update["human_directive_id"])
                self.assertEqual("provisional", update["research_status"])
                self.assertEqual("incomplete", update["consensus_status"])
                self.assertEqual(1, update["execution"]["agent_count"])
                self.assertEqual(1, update["execution"]["model_count"])
                self.assertEqual("managed-web", update["execution"]["retrieval_capability"])
                created = datetime.fromisoformat(update["created_at"])
                self.assertLess(created, stop)
                for check in update["source_checks"]:
                    self.assertLessEqual(datetime.fromisoformat(check["checked_at"]), created)
                    self.assertEqual("read-primary-single-model", check["result"])
                actual_topics.add(update["topic_id"])
                actual_units.update(unit["unit_id"] for unit in update["units"])
        self.assertEqual(TOPICS, actual_topics)
        self.assertEqual(53, len(actual_units))

    def test_every_target_unit_has_visible_evidence(self):
        profiles = {p["topic_id"]: p for p in read("knowledge/public/topic-decision-support.json")["topic_profiles"]}
        units = []
        for topic in read("config/research-baseline.json")["topics"]:
            if topic["topic_id"] not in TOPICS:
                continue
            profile = profiles[topic["topic_id"]]
            visible = {s["section_id"] for s in profile["sections"]} - set(profile.get("archived_section_ids", []))
            for unit in topic["research_units"]:
                with self.subTest(unit=unit["unit_id"]):
                    units.append(unit["unit_id"])
                    self.assertTrue(unit["evidence_section_ids"])
                    self.assertTrue(set(unit["evidence_section_ids"]) <= visible)
                    self.assertNotEqual("not-started", unit["status"])
        self.assertEqual(53, len(units))

    def test_vendor_specific_cells_do_not_assign_other_vendors_products(self):
        matrix = read("knowledge/public/topic-decision-support.json")["platform_matrix"]
        entries = {e["entry_id"]: e for c in matrix["capabilities"] for e in c["entries"]}
        for entry_id, platform in {
            "SWC-NCCL": "PLAT-NVIDIA-GPU", "SWC-RCCL": "PLAT-AMD-GPU",
            "SWC-INTEL-MATH-EXT": "PLAT-INTEL-XEON", "SWC-AMD-MATH-EXT": "PLAT-AMD-EPYC",
            "SWC-FUJITSU-MATH-EXT": "PLAT-FUJITSU-A64FX", "SWC-NVPL-MATH-EXT": "PLAT-NVIDIA-GRACE",
        }.items():
            self.assertEqual([platform], entries[entry_id]["platform_ids"])
        self.assertNotIn("SWC-NCCL-RCCL", entries)
        self.assertNotIn("SWC-CPU-MATH-EXT", entries)
        self.assertEqual("partial", entries["SWC-MPI-GPU"]["support_level"])

    def test_suite_component_and_emulation_conditions_remain_explicit(self):
        surface = read("knowledge/public/topic-decision-support.json")
        entries = {e["entry_id"]: e for c in surface["platform_matrix"]["capabilities"] for e in c["entries"]}
        self.assertIn("bundles NVPL 25.11", entries["SWC-NVPL"]["version_note"])
        self.assertIn("Standalone NVPL 26.5", entries["SWC-NVPL"]["version_note"])
        self.assertIn("rocBLAS 5.6.0", entries["SWC-ROCBLAS"]["version_note"])
        self.assertIn("SRC-CDS085", entries["SWC-INTEL-COMPILER"]["source_ids"])
        self.assertIn("SRC-CDS086", entries["SWC-AMD-AOCC"]["source_ids"])
        implementations = {i["implementation_id"]: i for m in surface["numerical_method_matrix"]["methods"] for i in m["implementations"]}
        cuda = implementations["NMI-GEMM-CUDA"]
        self.assertNotIn("TF32", cuda["precision"]["input"])
        self.assertIn("TF32", cuda["precision"]["compute"])
        self.assertIn("FP64", cuda["precision"]["emulation"])
        self.assertIn("not IEEE-754", cuda["precision"]["emulation"])
        self.assertIn("SRC-CDS027", cuda["source_ids"])

    def test_new_fiscal_windows_are_not_fabricated_calendar_quarters(self):
        blue = read("knowledge/public/roadmaps/reference-blueprint-centers.json")
        milestones = {m["milestone_id"]: m for lane in blue["lanes"] for m in lane["milestones"]}
        genkai = milestones["MS-BLUE-GENKAI-D-FY2027"]
        self.assertEqual((2027, "Q2", 2028, "Q1"),
                         (genkai["year"], genkai["quarter"], genkai["end_year"], genkai["end_quarter"]))
        self.assertEqual("quarter-range", genkai["timing_precision"])
        self.assertEqual("project-target", genkai["timing_basis"])
        port = read("knowledge/public/roadmaps/portability-compilers-tuning.json")
        milestone = next(m for lane in port["lanes"] for m in lane["milestones"] if m["milestone_id"] == "MS-PORT-FNAUTO-2026")
        self.assertEqual((2026, "Q2", 2027, "Q1"),
                         (milestone["year"], milestone["quarter"], milestone["end_year"], milestone["end_quarter"]))


    def test_terminal_bench_is_shared_by_all_agent_comparisons(self):
        reference = read("knowledge/public/roadmap-reference-data.json")
        terms = {t["term_id"] for t in reference["terms"]}
        expected = {"TERM-TERMINAL-BENCH", "TERM-TERMINAL-BENCH-SCIENCE"}
        self.assertTrue(expected <= terms)
        comparisons = {c["comparison_id"]: c for c in reference["comparison_sets"]}
        for comparison in ("CMP-AGENT-BENCHMARKS", "CMP-AGENT-EVALUATION-CONTROLS",
                           "CMP-AGENT-BENCHMARK-IMPORTANCE"):
            self.assertTrue(expected <= {r["term_id"] for r in comparisons[comparison]["rows"]})
        self.assertEqual("incomplete", reference["consensus_status"])
        self.assertEqual("DIR-900021", reference["publication"]["human_approval_directive_id"])

    def test_eea1_comparison_preserves_implementation_and_access_limits(self):
        reference = read("knowledge/public/roadmap-reference-data.json")
        comparison = next(c for c in reference["comparison_sets"] if c["comparison_id"] == "CMP-EEA1-REPRODUCIBILITY")
        rows = {r["term_id"]: " ".join(c["text_en"] for c in r["cells"]) for r in comparison["rows"]}
        self.assertEqual(6, len(rows))
        for term, fragments in {
            "TERM-EEA1-GENESIS": ("coarse-grained", "75%", "exceptions"),
            "TERM-EEA1-SALMON": ("initialization", "checkpoints", "2.3"),
            "TERM-EEA1-SCALE-LETKF": ("retrieval failed", "March", "assimilation"),
            "TERM-EEA1-LQCD-DWF-HMC": ("without mixed precision", "FLOP"),
        }.items():
            for fragment in fragments:
                self.assertIn(fragment, rows[term])
        update = read("proposals/research-unit-updates/RUP-000081.json")
        item = next(i for s in update["sections"] for i in s["items"] if i["item_id"] == "TDI-CD3-SALMON-DC-MEASUREMENT")
        self.assertIn("not end-to-end or GPU speedup", item["statement_en"])
        self.assertIn("512 Fugaku nodes", item["statement_en"])
        self.assertEqual("incomplete", item["consensus_status"])

    def test_tariff_research_keeps_units_and_document_conflicts(self):
        update = read("proposals/research-unit-updates/RUP-000082.json")
        text = " ".join(i["statement_en"] for s in update["sections"] for i in s["items"])
        for fragment in ("virtual", "HPCI", "reporting"):
            self.assertIn(fragment, text)
        self.assertEqual("incomplete", update["consensus_status"])
        self.assertTrue(any(i["stage"] == "contested" for s in update["sections"] for i in s["items"]))

    def test_inference_release_does_not_imply_vendor_qualification(self):
        update = read("proposals/research-unit-updates/RUP-000083.json")
        items = {i["item_id"]: i for s in update["sections"] for i in s["items"]}
        release = items["TDI-CD3-VLLM-UPSTREAM-VENDOR-VERSIONS"]["statement_en"]
        self.assertIn("0.28.0", release)
        self.assertIn("0.27.0", release)
        self.assertIn("neither proves", release)
        self.assertIn("unknown", items["TDI-CD3-VLLM-FEATURE-COMPOSITION"]["statement_en"])
        self.assertIn("not evidence of multi-node support", items["TDI-CD3-VLLM-XPU-PIPELINE-BOUNDARY"]["statement_en"])

    def test_followup_receipts_remain_within_the_authorized_window(self):
        directive = read("reviews/directives/DIR-900019.json")
        stop = datetime.fromisoformat("2026-09-01T06:30:00+09:00")
        updates = [read(str(path.relative_to(ROOT))) for path in
                   (ROOT / "proposals/research-unit-updates").glob("RUP-*.json")]
        for update in updates:
            if update["human_directive_id"] != directive["directive_id"]:
                continue
            with self.subTest(update=update["update_id"]):
                self.assertIn(update["update_id"], directive["publication_targets"])
                self.assertIn(update["topic_id"], TOPICS)
                self.assertEqual("provisional", update["research_status"])
                self.assertEqual("incomplete", update["consensus_status"])
                created = datetime.fromisoformat(update["created_at"])
                self.assertLess(created, stop)
                for check in update["source_checks"]:
                    self.assertLessEqual(datetime.fromisoformat(check["checked_at"]), created)
                    self.assertEqual("read-primary-single-model", check["result"])

    def test_service_trial_endpoints_are_not_shipment_or_shutdown_claims(self):
        blue = read("knowledge/public/roadmaps/reference-blueprint-centers.json")
        milestones = {m["milestone_id"]: m for lane in blue["lanes"] for m in lane["milestones"]}
        trial = milestones["MS-BLUE-RED-ONION-TRIAL-2026Q4"]
        self.assertEqual((2026, "Q4", "target", "project-target"),
                         (trial["year"], trial["quarter"], trial["maturity"], trial["timing_basis"]))
        production = milestones["MS-BLUE-RED-ONION-PRODUCTION-UNDATED"]
        self.assertEqual("undated", production["timing_precision"])
        self.assertIsNone(production["year"])
        aoba = milestones["MS-BLUE-AOBA-S3-2027Q1"]
        self.assertIn("does not confirm production, extension or a deletion date", aoba["detail_en"])
        port = read("knowledge/public/roadmaps/portability-compilers-tuning.json")
        items = {m["milestone_id"]: m for lane in port["lanes"] for m in lane["milestones"]}
        self.assertEqual("undated", items["MS-PORT-EESSI-ENABLEMENT-UNDATED"]["timing_precision"])
        self.assertIn("not a confirmed service shutdown", items["MS-PORT-EPICURE-PERIOD-2028Q1"]["detail_en"])

    def test_backend_and_benchmark_examples_do_not_become_calibration(self):
        deepmd = read("proposals/research-unit-updates/RUP-000086.json")
        items = {i["item_id"]: i for s in deepmd["sections"] for i in s["items"]}
        self.assertIn("does not identify the input ABI", items["TDI-CD2-DEEPMD-MODEL-CONTRACT"]["statement_en"])
        self.assertIn("no code was executed", items["TDI-CD2-DEEPMD-MANUAL-SCOPE"]["statement_en"])
        update = read("proposals/research-unit-updates/RUP-000088.json")
        items = {i["item_id"]: i for s in update["sections"] for i in s["items"]}
        self.assertIn("not CPU/GPU or GPU-generation comparisons", items["TDI-CD2-SQUID-SOFTWARE-SPEEDUP"]["statement_en"])
        self.assertIn("does not prove", items["TDI-CD2-SQUID-EXAMPLE-NOT-MEASUREMENT"]["statement_en"])

    def test_goodput_denominator_does_not_silently_include_unsent_requests(self):
        update = read("proposals/research-unit-updates/RUP-000105.json")
        items = {i["item_id"]: i for s in update["sections"] for i in s["items"]}
        text = items["TDI-CD4-AIPERF-GOODPUT-ATTAINMENT"]["statement_en"]
        for fragment in ("per second", "request_count plus error_request_count",
                         "does not establish that pre-send skips enter the denominator"):
            self.assertIn(fragment, text)
        self.assertIn("TDS-CD2-APP-13-U03", update["archive_section_ids"])

    def test_site_power_settings_and_research_software_are_not_general_guarantees(self):
        power = read("proposals/research-unit-updates/RUP-000106.json")
        text = power["sections"][0]["items"][0]["statement_en"]
        for fragment in ("module at 680W", "100W", "300W", "not whole-node consumption"):
            self.assertIn(fragment, text)
        for number, item_id in ((108, "TDI-CD4-PARAS-COMPILER-SCOPE"),
                                (109, "TDI-CD3-CLAP-BACKEND-BOUNDARIES"),
                                (110, "TDI-CD7-TORCH-PARAS-FALLBACK")):
            update = read(f"proposals/research-unit-updates/RUP-{number:06d}.json")
            item = next(i for s in update["sections"] for i in s["items"] if i["item_id"] == item_id)
            self.assertEqual("research", item["stage"])
            self.assertEqual("incomplete", item["consensus_status"])

    def test_gpu_communication_proposal_is_not_a_ratified_standard(self):
        update = read("proposals/research-unit-updates/RUP-000113.json")
        items = {i["item_id"]: i for s in update["sections"] for i in s["items"]}
        self.assertIn("not a permanent restriction", items["TDI-CD4-OPENMPI-CUDA-API-BOUNDARIES"]["statement_en"])
        self.assertIn("not standard MPI", items["TDI-CD4-OPENMPI-ROCM-LAYERED-CHECKS"]["statement_en"])
        proposed = items["TDI-CD4-GPU-OPENSHMEM-AUXILIARY-PROPOSAL"]
        self.assertEqual("research", proposed["stage"])
        self.assertIn("not evidence of a ratified standard", proposed["statement_en"])
        port = read("knowledge/public/roadmaps/portability-compilers-tuning.json")
        milestone = next(m for lane in port["lanes"] for m in lane["milestones"]
                         if m["milestone_id"] == "MS-PORT-GPU-OPENSHMEM-PROPOSAL-2026Q3")
        self.assertEqual((2026, "Q3", "research", "published", "observed"),
                         (milestone["year"], milestone["quarter"], milestone["event_type"],
                          milestone["maturity"], milestone["timing_basis"]))

    def test_local_mcp_does_not_imply_local_inference_or_job_cancellation(self):
        update = read("proposals/research-unit-updates/RUP-000117.json")
        text = " ".join(i["statement_en"] for s in update["sections"] for i in s["items"])
        for fragment in ("unofficial community port", "sent to a cloud model",
                         "server-side isolation to future work", "not cancellation"):
            self.assertIn(fragment, text)
        self.assertEqual("incomplete", update["consensus_status"])

    def test_reservations_and_center_plans_retain_access_constraints(self):
        reservation = read("proposals/research-unit-updates/RUP-000118.json")
        center = read("proposals/research-unit-updates/RUP-000119.json")
        for update in (reservation, center):
            self.assertEqual("incomplete", update["consensus_status"])
            self.assertTrue(update["remaining_work_en"])
        blue = read("knowledge/public/roadmaps/reference-blueprint-centers.json")
        sources = {s["source_id"]: s for s in blue["sources"]}
        self.assertIn("sokuho223.pdf", sources["SRC-BLUE052"]["url"])
        sources = {s["source"]["source_id"]: s["source"] for s in center["source_checks"]}
        self.assertEqual("2026-02-19 (printed issue date)", sources["SRC-CDX036"]["published_or_updated"])
        self.assertNotEqual("2026-09-14", sources["SRC-CDX037"]["published_or_updated"])

    def test_salmon_refresh_preserves_history_and_does_not_calibrate_forecasts(self):
        update = read("proposals/research-unit-updates/RUP-000120.json")
        self.assertIn("TDS-CD2-APP-01-U02", update["archive_section_ids"])
        items = {i["item_id"]: i for s in update["sections"] for i in s["items"]}
        release = items["TDI-CD3-SALMON-230-ANNOUNCEMENT"]["statement_en"]
        self.assertIn("historical observation", release)
        self.assertIn("tarball/tag identity", release)
        self.assertIn("remain unverified", release)
        self.assertIn("without OpenACC", items["TDI-CD3-SALMON-230-SCIENCE-AND-BUILDS"]["statement_en"])
        self.assertIn("old checkpoints", items["TDI-CD3-SALMON-230-RESTART-SEMANTICS"]["statement_en"])
        forecast = read("knowledge/public/application-performance-forecasts.json")
        source = next(s for s in forecast["sources"] if s["source_id"] == "SRC-PERF015")
        self.assertEqual("https://github.com/SALMON-TDDFT/SALMON2", source["url"])
        app = next(a for a in forecast["applications"] if a["application_id"] == "APP-EEA1-SALMON")
        self.assertIn("SRC-PERF015", app["code_availability"]["source_ids"])
        for result in forecast["illustrations"]:
            self.assertNotIn("SRC-PERF015", result["basis_source_ids"])
        self.assertEqual([], forecast["forecasts"])

    def test_porting_measurements_keep_cmg_and_study_version_boundaries(self):
        update = read("proposals/research-unit-updates/RUP-000121.json")
        items = {i["item_id"]: i for s in update["sections"] for i in s["items"]}
        nicam = items["TDI-CD5-NICAM-KOKKOS-CMG-BASELINE"]
        for fragment in ("one A64FX CMG with 12 cores", "mp_nsw6", "excluding I/O",
                         "not speedups over one Fugaku node or for full NICAM"):
            self.assertIn(fragment, nicam["statement_en"])
        self.assertTrue(any("33%" in c and "29%" in c for c in nicam["adoption_conditions_en"]))
        self.assertIn("unmeasured is not evidence of failure",
                      items["TDI-CD5-PORTABILITY-COHORT-METRIC"]["statement_en"])
        self.assertIn("page-update date is not a new measurement date",
                      items["TDI-CD5-PORTABILITY-STUDY-VERSION-SCOPE"]["statement_en"])
        self.assertEqual("incomplete", update["consensus_status"])
        self.assertEqual([], update["archive_section_ids"])
        corrected = read("proposals/research-unit-updates/RUP-000122.json")
        self.assertIn("単一のAIモデル", corrected["summary_ja"])
        self.assertEqual(update["summary_en"], corrected["summary_en"])
        self.assertEqual(["TDS-CD5-SSW-01-U04"], corrected["archive_section_ids"])
        self.assertEqual(
            [{k: v for k, v in i.items() if k != "item_id"} for i in update["sections"][0]["items"]],
            [{k: v for k, v in i.items() if k != "item_id"} for i in corrected["sections"][0]["items"]],
        )

    def test_legacy_what_if_values_are_explicitly_uncalibrated(self):
        forecast = read("knowledge/public/application-performance-forecasts.json")
        self.assertEqual("0.4.0", forecast["schema_version"])
        self.assertEqual(36, len(forecast["illustrations"]))
        self.assertEqual([], forecast["forecasts"])
        self.assertEqual(
            "legacy-what-if-illustration",
            forecast["model_contract"]["output_class"],
        )
        self.assertTrue(
            all(
                item["legacy_forecast_id"].startswith("FORECAST-")
                for item in forecast["illustrations"]
            )
        )
        self.assertEqual("incomplete", forecast["consensus_status"])
        self.assertIn("not a measured fraction", forecast["model_contract"]["limitations_en"])
        self.assertIn("neither a statistical confidence interval", forecast["model_contract"]["interval_method_en"])
        for assumption in forecast["assumptions"]:
            self.assertIn("未校正", assumption["basis_ja"])
            self.assertIn("uncalibrated inputs", assumption["basis_en"])
            self.assertIn("do not measure these fractions", assumption["basis_en"])

    def test_resumed_portability_evidence_keeps_three_layers_separate(self):
        update = read("proposals/research-unit-updates/RUP-000124.json")
        self.assertEqual(["TDS-CD7-SSW-01-U04"], update["archive_section_ids"])
        self.assertEqual("incomplete", update["consensus_status"])
        self.assertIn("単一のAIモデル", update["summary_ja"])
        items = {
            item["item_id"]: item
            for section in update["sections"]
            for item in section["items"]
        }
        layered = items["TDI-CD8-SSW01-PORTABILITY-LAYERED-EVALUATION"]
        for source_id in ("SRC-CDS011", "SRC-CDS124", "SRC-CDS125"):
            self.assertIn(source_id, layered["source_ids"])
        self.assertIn("three complementary validation layers", layered["statement_en"])
        self.assertTrue(
            any("GAP-TDS-005 remains open" in item for item in update["remaining_work_en"])
        )

    def test_nicam_reference_code_does_not_become_a_reproduced_port(self):
        update = read("proposals/research-unit-updates/RUP-000125.json")
        sources = {
            check["source"]["source_id"]: check["source"]
            for check in update["source_checks"]
        }
        self.assertEqual(
            "https://github.com/hisashiyashiro/nicam_dckernel_2016",
            sources["SRC-CDS126"]["url"],
        )
        item = update["sections"][0]["items"][0]
        self.assertIn("managed-Web cache miss", item["statement_en"])
        self.assertIn("does not establish exact identity", item["statement_en"])
        self.assertTrue(
            any("GAP-TDS-050 remains open" in value for value in update["remaining_work_en"])
        )
        self.assertEqual("incomplete", update["consensus_status"])


if __name__ == "__main__":
    unittest.main()
