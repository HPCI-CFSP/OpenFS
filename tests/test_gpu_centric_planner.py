from __future__ import annotations

import copy
import json
import shutil
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from estimate_gpu_centric_configuration import evaluate  # noqa: E402


def load(path: str) -> dict:
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


class GpuCentricPlannerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.request = load("proposals/planning-requests/PLANREQ-GPUAI4S-2027-ONPREM-001.json")
        cls.architecture = load("proposals/reference-architectures/ARCH-GPU-CENTRIC-AI4S-001.json")
        cls.catalog = load("proposals/gpu-product-catalogs/GPUCAT-001.json")
        cls.availability = load("proposals/procurement-availability/AVAIL-2027-JP-001.json")
        cls.costs = load("tests/fixtures/gpu-planner-priced-components.json")

    def complete_request(self, budget=125, power=4):
        request = copy.deepcopy(self.request)
        request["vendor_mode"] = "compare"
        request["budget"]["capex_ceiling_oku_jpy"] = budget
        request["facility"].update(
            it_power_limit_mw=power,
            it_power_limit_status="confirmed",
            cooling_method="direct-liquid",
            cooling_capacity_mw=power,
            cooling_capacity_status="confirmed",
            rack_limit=40,
            floor_area_m2=500,
            floor_loading_kg_m2=2500,
        )
        request["workloads"]["absolute_demand"].update(
            hpc_jobs_per_year=10000,
            hpc_accelerator_hours_per_year=1000000,
        )
        request["storage"].update(
            shared_fast_capacity_pb=5,
            archive_capacity_pb=10,
            checkpoint_write_gb_s=1000,
            training_read_gb_s=2000,
        )
        return request

    def eligible_availability(self):
        availability = copy.deepcopy(self.availability)
        for item in availability["assessments"]:
            if item["product_id"] in {"GPU-NVIDIA-VERA-RUBIN", "GPU-AMD-MI430X"}:
                item.update(
                    availability_status="eligible",
                    latest_delivery_date="2027-09-30",
                    earliest_delivery_date="2027-06-30",
                    sales_channel_status="confirmed",
                    support_status="confirmed",
                )
        return availability

    def run_complete(self, budget=125, power=4, mode="compare"):
        request = self.complete_request(budget, power)
        request["vendor_mode"] = mode
        return evaluate(
            request,
            self.architecture,
            self.catalog,
            self.eligible_availability(),
            self.costs,
            "2026-09-07T00:00:00Z",
        )

    def test_public_reference_case_remains_blocked(self):
        result = evaluate(
            self.request,
            self.architecture,
            self.catalog,
            self.availability,
            generated_at="2026-09-07T00:00:00Z",
        )
        self.assertEqual("blocked", result["status"])
        self.assertEqual({"NVIDIA", "AMD"}, {item["vendor"] for item in result["vendor_candidates"]})
        for candidate in result["vendor_candidates"]:
            self.assertIn("GAP-GPUCFG-001", candidate["gap_ids"])
            self.assertIn("GAP-GPUCFG-002", candidate["gap_ids"])
            self.assertTrue(all(case["gpu_count"] is None for case in candidate["cases"]))
        self.assertNotIn("SCN-HPCI", json.dumps(result))

    def test_committed_deployment_cases_remain_candidate_and_blocked(self):
        for mode, suffix in (
            ("on-premises", "ONPREM"),
            ("external-hosting", "HOSTED"),
            ("hybrid", "HYBRID"),
        ):
            request = load(f"proposals/planning-requests/PLANREQ-GPUAI4S-2027-{suffix}-001.json")
            result = load(f"proposals/configuration-results/CFGRESULT-GPUAI4S-2027-{suffix}-001.json")
            self.assertEqual(mode, request["deployment_mode"])
            self.assertEqual("blocked", result["status"])
            self.assertEqual("incomplete", result["consensus_status"])
            self.assertEqual("prohibited", result["procurement_use"])

    def test_committed_results_are_reproducible(self):
        for suffix in ("ONPREM", "HOSTED", "HYBRID"):
            request = load(f"proposals/planning-requests/PLANREQ-GPUAI4S-2027-{suffix}-001.json")
            expected = load(f"proposals/configuration-results/CFGRESULT-GPUAI4S-2027-{suffix}-001.json")
            actual = evaluate(
                request,
                self.architecture,
                self.catalog,
                self.availability,
                generated_at="2026-09-07T00:00:00Z",
            )
            self.assertEqual(expected, actual)

    def test_candidate_cross_references_are_closed(self):
        policy_set = load("proposals/system-planning-policies/POLSET-SYSTEM-001.json")
        policies = {item["policy_id"] for item in policy_set["policies"]}
        products = {item["product_id"] for item in self.catalog["products"]}
        assessed = {item["product_id"] for item in self.availability["assessments"]}
        gaps = {item["gap_id"] for item in self.architecture["coverage_gaps"]}
        self.assertTrue(set(self.architecture["compatible_policy_ids"]) <= policies)
        self.assertEqual(products, assessed)
        for suffix in ("ONPREM", "HOSTED", "HYBRID"):
            request = load(f"proposals/planning-requests/PLANREQ-GPUAI4S-2027-{suffix}-001.json")
            result = load(f"proposals/configuration-results/CFGRESULT-GPUAI4S-2027-{suffix}-001.json")
            self.assertIn(request["policy_id"], policies)
            self.assertEqual(request["request_id"], result["request_id"])
            self.assertTrue(
                {
                    gap
                    for candidate in result["vendor_candidates"]
                    for gap in candidate["gap_ids"]
                }
                <= gaps
            )

    def test_candidate_source_references_resolve_to_existing_registers(self):
        source_map = load("knowledge/public/source-catalog-map.json")
        procurement = load("knowledge/public/procurement-cost-register.json")
        known_source_ids = {
            item["source_id"]
            for entry in source_map["entries"]
            for key in ("roadmap_source_refs", "catalog_source_refs")
            for item in entry[key]
        }
        known_source_ids.update(item["source_id"] for item in procurement["sources"])

        referenced_source_ids = set()

        def collect(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key == "source_ids":
                        referenced_source_ids.update(child)
                    else:
                        collect(child)
            elif isinstance(value, list):
                for child in value:
                    collect(child)

        collect(self.architecture)
        collect(self.catalog)
        collect(self.availability)
        self.assertTrue(referenced_source_ids)
        self.assertEqual(set(), referenced_source_ids - known_source_ids)

    def test_2027_assessment_is_not_reused_for_other_years(self):
        for year in range(2026, 2033):
            request = copy.deepcopy(self.request)
            request["schedule"]["acceptance_year"] = year
            request["schedule"]["required_acceptance_date"] = f"{year}-12-31"
            result = evaluate(request, self.architecture, self.catalog, self.availability)
            if year != 2027:
                self.assertTrue(
                    all(
                        item["availability_status"] == "not-assessed"
                        for item in result["vendor_candidates"]
                    )
                )

    def test_integer_sizing_budget_identity_and_separate_tco(self):
        result = self.run_complete()
        for candidate in result["vendor_candidates"]:
            case = candidate["cases"][1]
            self.assertIsInstance(case["compute_units"], int)
            self.assertIsInstance(case["gpu_count"], int)
            self.assertTrue(case["costs"]["identity_verified"])
            self.assertAlmostEqual(
                case["costs"]["budget_ceiling_jpy"],
                case["costs"]["configuration_cost_jpy"]
                + case["costs"]["contingency_jpy"]
                + case["costs"]["unused_budget_jpy"],
            )
            self.assertGreater(case["tco"]["total_tco_jpy"], case["tco"]["initial_capex_jpy"])
            self.assertEqual("prohibited", case["performance"]["procurement_use"])

    def test_budget_monotonicity_for_unchanged_generation(self):
        counts = []
        for budget in (10, 30, 100, 125, 300):
            result = self.run_complete(budget=budget, power=10)
            counts.append(result["vendor_candidates"][0]["cases"][1]["gpu_count"] or 0)
        self.assertEqual(counts, sorted(counts))

    def test_power_cap_can_reduce_integer_configuration(self):
        low = self.run_complete(power=0.5)["vendor_candidates"][0]["cases"][1]["gpu_count"]
        high = self.run_complete(power=4)["vendor_candidates"][0]["cases"][1]["gpu_count"]
        self.assertLess(low, high)

    def test_auto_mode_returns_candidates_not_a_single_winner(self):
        request = self.complete_request()
        request["vendor_mode"] = "auto-pareto"
        request["objectives"] = [
            {"metric": "total-hbm-gib", "direction": "maximize", "weight": None},
            {"metric": "capex-jpy", "direction": "minimize", "weight": None},
            {"metric": "it-power-kw", "direction": "minimize", "weight": None},
        ]
        result = evaluate(request, self.architecture, self.catalog, self.eligible_availability(), self.costs)
        self.assertEqual("computed", result["pareto_result"]["status"])
        self.assertGreaterEqual(len(result["pareto_result"]["candidate_refs"]), 1)
        self.assertNotIn("winner", result["pareto_result"]["reason_en"].lower())

    def test_browser_engine_contract(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is unavailable")
        result = subprocess.run(
            [node, "--test", "tests/gpu_planner_engine.test.cjs"],
            cwd=ROOT,
            text=True,
            capture_output=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_browser_and_python_engines_match_key_outputs(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node.js is unavailable")
        browser = subprocess.run(
            [node, "tests/gpu_planner_parity.cjs"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=True,
        )
        browser_values = json.loads(browser.stdout)
        python_result = self.run_complete()
        python_values = []
        for item in python_result["vendor_candidates"]:
            value = item["cases"][1]
            python_values.append(
                {
                    "vendor": item["vendor"],
                    "product_id": item["product_id"],
                    "compute_units": value["compute_units"],
                    "gpu_count": value["gpu_count"],
                    "rack_count": value["rack_count"],
                    "configuration_cost_jpy": value["costs"]["configuration_cost_jpy"],
                    "contingency_jpy": value["costs"]["contingency_jpy"],
                    "unused_budget_jpy": value["costs"]["unused_budget_jpy"],
                    "total_tco_jpy": value["tco"]["total_tco_jpy"],
                }
            )
        self.assertEqual(python_values, browser_values)


if __name__ == "__main__":
    unittest.main()
