from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from estimate_gpu_centric_configuration import (  # noqa: E402
    evaluate,
    inference_performance,
)


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class GpuCentricPlannerV02Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = load(
            "proposals/planning-requests/PLANREQ-GPUAI4S-2027-ONPREM-001.json"
        )
        cls.architecture = load(
            "proposals/reference-architectures/ARCH-GPU-CENTRIC-AI4S-001.json"
        )
        cls.catalog = load("proposals/gpu-product-catalogs/GPUCAT-001.json")
        cls.availability = load(
            "proposals/procurement-availability/AVAIL-2027-JP-001.json"
        )
        cls.costs = load("tests/fixtures/gpu-planner-priced-components.json")

    def what_if_request(
        self, budget: float = 125, power: float = 4, rack_limit: int = 20
    ) -> dict:
        request = copy.deepcopy(self.request)
        request["run_mode"] = "what-if"
        request["vendor_mode"] = "compare"
        request["product_selection"] = {
            "nvidia": "GPU-NVIDIA-VERA-RUBIN",
            "amd": "GPU-AMD-MI455X",
        }
        request["budget"]["capex_ceiling_oku_jpy"] = budget
        request["facility"].update(
            it_power_limit_mw=power,
            it_power_limit_status="user-input",
            cooling_method="direct-liquid",
            cooling_capacity_mw=power,
            cooling_capacity_status="user-input",
            rack_limit=rack_limit,
            floor_area_m2=1000,
            floor_loading_kg_m2=2500,
            rack_density_kw=500,
            pue=1.1,
            power_redundancy="N+1",
            cooling_redundancy="N+1",
            facility_work_in_capex=True,
        )
        request["workloads"]["utilization_target_percent"] = 80
        request["workloads"]["headroom_percent"] = 10
        request["workloads"]["absolute_demand"].update(
            annual_accelerator_hours=100000,
            hpc_jobs_per_year=1000,
            hpc_accelerator_hours_per_year=16000,
            hpc_accelerators_per_job=8,
            hpc_mean_runtime_hours=2,
            concurrent_users=100,
        )
        request["storage"].update(
            shared_fast_capacity_pb=0,
            archive_capacity_pb=0,
            checkpoint_write_gb_s=0,
            training_read_gb_s=0,
            metadata_million_inodes=0,
            backup_copies=0,
            retention_years=1,
            rto_hours=24,
            local_nvme_tb_per_compute_unit=0,
        )
        return request

    def run_what_if(
        self,
        budget: float = 125,
        power: float = 4,
        rack_limit: int = 20,
        costs: dict | None = None,
        request: dict | None = None,
    ) -> dict:
        return evaluate(
            request or self.what_if_request(budget, power, rack_limit),
            self.architecture,
            self.catalog,
            self.availability,
            costs or self.costs,
            "2026-09-07T00:00:00Z",
        )

    def case(self, result: dict, vendor: str = "NVIDIA", price: str = "baseline"):
        candidate = next(
            item for item in result["vendor_candidates"] if item["vendor"] == vendor
        )
        return next(item for item in candidate["cases"] if item["price_case"] == price)

    def test_public_evidence_mode_preserves_unknowns_and_blocks_estimate(self):
        result = evaluate(
            self.request,
            self.architecture,
            self.catalog,
            self.availability,
            generated_at="2026-09-07T00:00:00Z",
        )
        self.assertEqual("blocked", result["status"])
        self.assertEqual("public-evidence", result["calculation_mode"])
        self.assertEqual("prohibited", result["procurement_use"])
        self.assertEqual("incomplete", result["consensus_status"])
        for candidate in result["vendor_candidates"]:
            gap_ids = {gap["gap_id"] for gap in candidate["gaps"]}
            self.assertIn("GAP-GPUCFG-001", gap_ids)
            self.assertIn("GAP-GPUCFG-002", gap_ids)
            self.assertTrue(
                all(case["quantities"] is None for case in candidate["cases"])
            )
        self.assertNotIn("SCN-HPCI", json.dumps(result))

    def test_exact_125_oku_acceptance_case(self):
        result = self.run_what_if()
        for vendor in ("NVIDIA", "AMD"):
            case = self.case(result, vendor)
            self.assertEqual("partial", case["status"])
            self.assertEqual(9, case["quantities"]["compute_units"])
            self.assertEqual(9, case["quantities"]["rack_count"])
            self.assertEqual(648, case["quantities"]["gpu_count"])
            self.assertEqual(10_500_000_000, case["costs"]["configuration_cost_jpy"])
            self.assertEqual(1_050_000_000, case["costs"]["contingency_jpy"])
            self.assertEqual(950_000_000, case["costs"]["unused_budget_jpy"])
            self.assertTrue(case["costs"]["identity_verified"])

    def test_300_oku_is_power_limited_to_ten_racks(self):
        case = self.case(self.run_what_if(budget=300))
        self.assertEqual(10, case["quantities"]["rack_count"])
        self.assertEqual(720, case["quantities"]["gpu_count"])
        self.assertEqual("pass", case["constraints"]["it_power"]["status"])

    def test_two_megawatt_limit_caps_five_racks(self):
        case = self.case(self.run_what_if(budget=300, power=2))
        self.assertEqual(5, case["quantities"]["rack_count"])
        self.assertEqual(360, case["quantities"]["gpu_count"])

    def test_budget_growth_never_reduces_gpu_count_for_fixed_generation(self):
        counts = [
            self.case(self.run_what_if(budget=value, power=20, rack_limit=100))[
                "quantities"
            ]["gpu_count"]
            if self.case(
                self.run_what_if(budget=value, power=20, rack_limit=100)
            )["quantities"]
            else 0
            for value in (10, 30, 100, 125, 300)
        ]
        self.assertEqual(counts, sorted(counts))

    def test_each_price_case_reoptimizes_integer_quantity(self):
        costs = copy.deepcopy(self.costs)
        for package in costs["packages"]:
            compute = next(
                line for line in package["cost_lines"] if line["category"] == "compute"
            )
            compute.update(
                optimistic_jpy=800_000_000,
                baseline_jpy=1_000_000_000,
                conservative_jpy=1_200_000_000,
            )
        result = self.run_what_if(costs=costs, power=20, rack_limit=100)
        counts = [
            self.case(result, price=price)["quantities"]["compute_units"]
            for price in ("optimistic", "baseline", "conservative")
        ]
        self.assertGreater(counts[0], counts[1])
        self.assertGreater(counts[1], counts[2])

    def test_network_storage_floor_delivery_and_demand_constraints_block(self):
        checks = []

        network = copy.deepcopy(self.costs)
        network["packages"][0]["network"]["max_switch_count"] = 0
        checks.append(("network_ports", self.run_what_if(costs=network)))

        storage = copy.deepcopy(self.costs)
        storage["packages"][0]["storage_capability"][
            "max_fast_storage_appliances"
        ] = 2
        request = self.what_if_request()
        request["storage"]["shared_fast_capacity_pb"] = 30
        checks.append(
            ("fast_storage_appliances", self.run_what_if(costs=storage, request=request))
        )

        request = self.what_if_request()
        request["facility"]["floor_area_m2"] = 1
        checks.append(("floor_area", self.run_what_if(request=request)))

        delivery = copy.deepcopy(self.costs)
        delivery["packages"][0]["procurement_assumption"][
            "latest_delivery_date"
        ] = "2028-01-01"
        checks.append(("delivery", self.run_what_if(costs=delivery)))

        request = self.what_if_request(budget=10)
        request["workloads"]["absolute_demand"][
            "annual_accelerator_hours"
        ] = 10_000_000_000
        checks.append(("demand", self.run_what_if(request=request)))

        for constraint_name, result in checks:
            with self.subTest(constraint=constraint_name):
                case = self.case(result)
                self.assertEqual("blocked", case["status"])
                self.assertIn(
                    case["constraints"][constraint_name]["status"],
                    {"fail", "unknown"},
                )

    def test_phase_model_separates_overlap_nonoverlap_and_sync(self):
        request = self.what_if_request()
        request["performance_model"]["phase_baseline"] = {
            "status": "provisional",
            "benchmark": "GROMACS",
            "measured_compute_units": 1,
            "compute_time_s": 100,
            "memory_time_s": 80,
            "communication_time_s": 40,
            "io_time_s": 20,
            "non_overlappable_time_s": 10,
            "synchronization_time_s": 5,
            "scaling_efficiency": {
                "optimistic": 0.9,
                "baseline": 0.8,
                "conservative": 0.7,
            },
            "error_percent": {
                "optimistic": 10,
                "baseline": 15,
                "conservative": 20,
            },
            "measured_configuration": "Synthetic measurement",
            "software_stack": ["test-stack"],
            "source_kind": "user-assumption",
            "source_ids": [],
        }
        case = self.case(self.run_what_if(request=request))
        prediction = case["performance"]["bounds"]["baseline"]
        self.assertAlmostEqual(
            prediction["predicted_time_s"],
            prediction["overlappable_phase_time_s"]
            + prediction["non_overlappable_time_s"]
            + prediction["synchronization_time_s"],
        )
        self.assertEqual("prohibited", case["performance"]["procurement_use"])

    def test_queue_model_responds_to_request_rate(self):
        request = self.what_if_request()
        quantities = {"gpu_count": 8}
        baseline = {
            "status": "provisional",
            "service_rate_rps_per_gpu": 10,
            "base_ttft_ms": 100,
            "base_tpot_ms": 20,
        }
        request["inference"]["request_rate_per_second"] = 10
        low = inference_performance(request, quantities, baseline)
        request["inference"]["request_rate_per_second"] = 70
        high = inference_performance(request, quantities, baseline)
        self.assertLess(low["utilization"], high["utilization"])
        self.assertLess(low["ttft_ms"]["p99"], high["ttft_ms"]["p99"])

    def test_auto_selection_returns_pareto_set_or_explicit_reason(self):
        request = self.what_if_request()
        request["vendor_mode"] = "auto-pareto"
        request["objectives"] = [
            {"metric": "capex-jpy", "direction": "minimize", "weight": None},
            {"metric": "it-power-kw", "direction": "minimize", "weight": None},
            {"metric": "portability-risk", "direction": "minimize", "weight": None},
        ]
        result = self.run_what_if(request=request)
        self.assertEqual("computed", result["pareto_result"]["status"])
        self.assertGreaterEqual(len(result["pareto_result"]["candidate_refs"]), 1)
        self.assertNotIn("winner", result["pareto_result"]["reason_en"].lower())

        request["objectives"] = [
            {"metric": "unsupported-objective", "direction": "minimize", "weight": None}
        ]
        result = self.run_what_if(request=request)
        self.assertEqual("not-evaluable", result["pareto_result"]["status"])
        self.assertIn("unsupported-objective", result["pareto_result"]["reason_en"])

    def test_committed_public_results_are_reproducible(self):
        for suffix in ("ONPREM", "HOSTED", "HYBRID"):
            request = load(
                f"proposals/planning-requests/PLANREQ-GPUAI4S-2027-{suffix}-001.json"
            )
            expected = load(
                f"proposals/configuration-results/CFGRESULT-GPUAI4S-2027-{suffix}-001.json"
            )
            actual = evaluate(
                request,
                self.architecture,
                self.catalog,
                self.availability,
                generated_at="2026-09-07T00:00:00Z",
            )
            self.assertEqual(expected, actual)

    def test_candidate_sources_and_cross_references_are_closed(self):
        policy_set = load("proposals/system-planning-policies/POLSET-SYSTEM-001.json")
        policies = {item["policy_id"] for item in policy_set["policies"]}
        products = {item["product_id"] for item in self.catalog["products"]}
        assessed = {item["product_id"] for item in self.availability["assessments"]}
        gaps = {item["gap_id"] for item in self.architecture["coverage_gaps"]}
        self.assertTrue(set(self.architecture["compatible_policy_ids"]) <= policies)
        self.assertEqual(products, assessed)
        self.assertIn("GAP-GPUCFG-011", gaps)

        source_map = load("knowledge/public/source-catalog-map.json")
        procurement = load("knowledge/public/procurement-cost-register.json")
        known = {
            item["source_id"]
            for entry in source_map["entries"]
            for key in ("roadmap_source_refs", "catalog_source_refs")
            for item in entry[key]
        }
        known.update(item["source_id"] for item in procurement["sources"])
        referenced = set()

        def collect(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key == "source_ids":
                        referenced.update(child)
                    else:
                        collect(child)
            elif isinstance(value, list):
                for child in value:
                    collect(child)

        collect(self.architecture)
        collect(self.catalog)
        collect(self.availability)
        self.assertEqual(set(), referenced - known)

    def test_browser_engine_and_python_engine_have_parity(self):
        node = shutil.which("node") or str(
            Path.home()
            / ".cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node"
        )
        if not Path(node).is_file():
            self.skipTest("Node.js is unavailable")
        env = os.environ.copy()
        browser_tests = subprocess.run(
            [node, "--test", "tests/gpu_planner_engine.test.cjs"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
        )
        self.assertEqual(
            0, browser_tests.returncode, browser_tests.stdout + browser_tests.stderr
        )
        browser = subprocess.run(
            [node, "tests/gpu_planner_parity.cjs"],
            cwd=ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=True,
        )
        browser_values = json.loads(browser.stdout)
        python_result = self.run_what_if()
        python_values = []
        for candidate in python_result["vendor_candidates"]:
            value = self.case(python_result, candidate["vendor"])
            python_values.append(
                {
                    "vendor": candidate["vendor"],
                    "product_id": candidate["product_id"],
                    "compute_units": value["quantities"]["compute_units"],
                    "gpu_count": value["quantities"]["gpu_count"],
                    "rack_count": value["quantities"]["rack_count"],
                    "configuration_cost_jpy": value["costs"][
                        "configuration_cost_jpy"
                    ],
                    "contingency_jpy": value["costs"]["contingency_jpy"],
                    "unused_budget_jpy": value["costs"]["unused_budget_jpy"],
                    "total_tco_jpy": value["tco"]["total_tco_jpy"],
                }
            )
        self.assertEqual(python_values, browser_values)


if __name__ == "__main__":
    unittest.main()
