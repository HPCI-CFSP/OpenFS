from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from estimate_system_cost import (
    allocate_budget,
    contract_breakdown,
    estimate_configuration,
    five_year_known_cost_floor,
    lease_period_total,
    normalize_amount,
)
from check_procurement_costs import validate_register
from audit_roadmap_sources_via_fetch_broker import reconcile_offline
from build_roadmap_freshness_audit import build as build_freshness
from build_pages_site import collect_procurement_costs
from validate_json_schemas import Draft202012Validator, schema_registry


def read(path):
    return json.loads((ROOT / path).read_text())


class ProcurementCostTests(unittest.TestCase):
    def setUp(self):
        self.config = read("config/budget-planning.json")
        self.register = read("knowledge/public/procurement-cost-register.json")

    def test_current_register_retains_unknown_breakdowns(self):
        validate_register(self.register, self.config)
        case = self.register["cases"][0]
        result = contract_breakdown(case)
        self.assertEqual(6731406000, result["unallocated_jpy"])
        self.assertEqual(0, result["itemized_jpy"])
        jss4 = next(c for c in self.register["cases"] if c["case_id"] == "PROC-JAXA-JSS4-2025")
        self.assertIsNone(contract_breakdown(jss4)["observed_total_jpy"])
        self.assertTrue(all(c["aggregation_status"] != "cleared" for c in self.register["cases"]))

    def test_itemization_needs_observed_evidence_and_matching_tax(self):
        case = self.register["cases"][0]
        case["itemized_costs"] = [{"line_id": "TEST", "value_jpy": 100,
                                   "basis": "observed", "source_refs": ["TEST"],
                                   "tax_basis": "including-tax"}]
        self.assertEqual(6731405900, contract_breakdown(case)["unallocated_jpy"])
        for field, value in [("basis", "estimated"), ("tax_basis", "excluding-tax"),
                             ("source_refs", []), ("value_jpy", 6731406001)]:
            changed = copy.deepcopy(case)
            changed["itemized_costs"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                contract_breakdown(changed)

    def test_only_explicit_price_normalization_is_allowed(self):
        amount = {"kind": "contract", "value_jpy": 110, "payment_basis": "monthly",
                  "period_months": 60, "tax_basis": "including-tax", "tax_rate": 0.1}
        self.assertEqual(6000, normalize_amount(amount))
        for field, value in [("tax_rate", None), ("period_months", None),
                             ("kind", "program-budget"), ("tax_basis", "unknown"),
                             ("value_jpy", float("inf")), ("value_jpy", -1), ("value_jpy", None)]:
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                normalize_amount({**amount, field: value})

    def test_lease_arithmetic_is_not_purchase_price(self):
        case = next(c for c in self.register["cases"] if c["case_id"] == "PROC-TSUKUBA-UNIFIED-MEMORY-2025")
        result = lease_period_total(case)
        self.assertEqual(855360000, result["value_jpy"])
        self.assertEqual(72, result["months"])
        self.assertEqual("tender-period", result["window_basis"])
        self.assertIsNone(contract_breakdown(case)["observed_total_jpy"])
        self.assertEqual("unconfirmed", case["configuration_match"])
        for patch_value in [{"end": "2031-02-28"}, {"start": "2026-03-27"}, {"end": "2026-02-28"}]:
            changed = copy.deepcopy(case)
            changed["contract_window"].update(patch_value)
            with self.subTest(patch_value=patch_value), self.assertRaises(ValueError):
                lease_period_total(changed)

    def test_five_year_known_cost_floor_is_not_complete_tco(self):
        case = next(c for c in self.register["cases"] if c["case_id"] == "PROC-TSUKUBA-UNIFIED-MEMORY-2025")
        result = five_year_known_cost_floor(case)
        self.assertEqual(712800000, result["value_jpy"])
        self.assertEqual(60, result["months"])
        self.assertFalse(result["tco_complete"])
        self.assertIn("electricity", result["excluded_costs"])
        self.assertEqual(
            1,
            sum(five_year_known_cost_floor(item) is not None for item in self.register["cases"]),
        )

        shorter = copy.deepcopy(case)
        shorter["amount"]["period_months"] = 59
        self.assertIsNone(five_year_known_cost_floor(shorter))

    def test_every_case_has_a_complete_tco_scope_audit(self):
        scope_ids = [item["scope_id"] for item in self.register["tco_scope_catalog"]]
        self.assertEqual(12, len(scope_ids))
        self.assertEqual(12, len(set(scope_ids)))
        self.assertEqual(
            0,
            sum(
                case["five_year_cost_assessment"]["complete_tco"]
                for case in self.register["cases"]
            ),
        )
        for case in self.register["cases"]:
            assessment = case["five_year_cost_assessment"]
            self.assertEqual(
                scope_ids,
                [item["scope_id"] for item in assessment["scope_coverage"]],
            )
            for item in assessment["scope_coverage"]:
                self.assertEqual(
                    item["evidence_status"] == "unknown",
                    not item["source_refs"],
                )

    def test_tco_scope_audit_fails_closed(self):
        case = self.register["cases"][0]
        case["five_year_cost_assessment"]["scope_coverage"].pop()
        with self.assertRaisesRegex(ValueError, "complete catalog"):
            validate_register(self.register, self.config)

        self.setUp()
        case = self.register["cases"][0]
        case["five_year_cost_assessment"]["scope_coverage"][0][
            "evidence_status"
        ] = "observed-contract-scope"
        case["five_year_cost_assessment"]["scope_coverage"][0]["source_refs"] = []
        with self.assertRaisesRegex(ValueError, "requires source"):
            validate_register(self.register, self.config)

        self.setUp()
        sirius = next(
            item
            for item in self.register["cases"]
            if item["case_id"] == "PROC-TSUKUBA-UNIFIED-MEMORY-2025"
        )
        sirius["five_year_cost_assessment"]["known_cost_floor_jpy"] += 1
        with self.assertRaisesRegex(ValueError, "disagrees"):
            validate_register(self.register, self.config)

    def test_unknown_payment_basis_cannot_be_normalized(self):
        case = next(c for c in self.register["cases"] if c["case_id"] == "PROC-NAGOYA-FURO-NEXT-2025")
        self.assertIsNone(lease_period_total(case))
        self.assertIsNone(contract_breakdown(case)["observed_total_jpy"])
        with self.assertRaises(ValueError):
            normalize_amount(case["amount"])

    def test_reported_contract_total_requires_checked_contract_evidence(self):
        case = next(c for c in self.register["cases"] if c["case_id"] == "PROC-TSUKUBA-UNIFIED-MEMORY-2025")
        self.assertEqual(855360000, case["reported_period_total"]["value_jpy"])
        self.assertEqual("2025-06-12", case["contract_date"])
        validate_register(self.register, self.config)
        for refs in ([], ["PCS-TSUKUBA-AWARD-2025"], ["UNKNOWN"]):
            changed = copy.deepcopy(self.register)
            item = next(c for c in changed["cases"] if c["case_id"] == case["case_id"])
            item["reported_period_total"]["source_refs"] = refs
            with self.subTest(refs=refs), self.assertRaises(ValueError):
                validate_register(changed, self.config)
        source = next(s for s in self.register["sources"] if s["source_id"] == "PCS-TSUKUBA-CONTRACT-2025Q1")
        source["retrieval_status"] = "not-retrieved"
        with self.assertRaises(ValueError):
            validate_register(self.register, self.config)

    def test_reported_total_cannot_silently_disagree_with_monthly_arithmetic(self):
        for field, value in (("value_jpy", 855360001), ("period_months", 60),
                             ("period_months", None), ("period_months", True),
                             ("tax_basis", "excluding-tax"), ("tax_rate", 0.08),
                             ("payment_basis", "monthly")):
            changed = copy.deepcopy(self.register)
            case = next(c for c in changed["cases"] if c["case_id"] == "PROC-TSUKUBA-UNIFIED-MEMORY-2025")
            case["reported_period_total"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_register(changed, self.config)

    def test_reported_total_schema_requires_a_known_period(self):
        schemas, registry = schema_registry(ROOT)
        validator = Draft202012Validator(schemas["procurement-cost-register.schema.json"], registry=registry)
        case = next(c for c in self.register["cases"] if c["case_id"] == "PROC-TSUKUBA-UNIFIED-MEMORY-2025")
        case["reported_period_total"]["period_months"] = None
        self.assertTrue(list(validator.iter_errors(self.register)))

    def test_known_month_count_checks_do_not_depend_on_calendar_dates(self):
        case_id = "PROC-TSUKUBA-UNIFIED-MEMORY-2025"
        case = next(c for c in self.register["cases"] if c["case_id"] == case_id)
        del case["contract_window"]
        validate_register(self.register, self.config)
        for field, value in (("value_jpy", 855360001), ("period_months", 60),
                             ("tax_basis", "excluding-tax")):
            changed = copy.deepcopy(self.register)
            item = next(c for c in changed["cases"] if c["case_id"] == case_id)
            item["reported_period_total"][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                validate_register(changed, self.config)

    def test_reported_total_can_stand_alone_without_inferred_billing(self):
        case = next(c for c in self.register["cases"] if c["case_id"] == "PROC-TSUKUBA-UNIFIED-MEMORY-2025")
        del case["contract_window"]
        case["amount"] = None
        case["five_year_cost_assessment"].update({
            "status": "not-computable",
            "known_cost_floor_jpy": None,
            "tax_basis": None,
        })
        validate_register(self.register, self.config)
        self.assertIsNone(lease_period_total(case))
        self.assertIsNone(five_year_known_cost_floor(case))
        self.assertEqual(855360000, case["reported_period_total"]["value_jpy"])

    def test_capacity_ids_are_unique_across_procurements(self):
        source_case = next(c for c in self.register["cases"] if c.get("storage_capacity_observations"))
        other_case = next(c for c in self.register["cases"] if c["case_id"] != source_case["case_id"])
        other_case["storage_capacity_observations"] = [copy.deepcopy(source_case["storage_capacity_observations"][0])]
        with self.assertRaisesRegex(ValueError, "duplicate observation_id"):
            validate_register(self.register, self.config)

    def test_contract_date_cannot_be_inferred_from_an_award(self):
        case = next(c for c in self.register["cases"] if c["case_id"] == "PROC-TSUKUBA-UNIFIED-MEMORY-2025")
        case["contract_date_source_refs"] = ["PCS-TSUKUBA-AWARD-2025"]
        with self.assertRaises(ValueError):
            validate_register(self.register, self.config)

    def test_omitting_contract_date_references_cannot_bypass_provenance(self):
        case = next(c for c in self.register["cases"] if c["case_id"] == "PROC-NAGOYA-FURO-NEXT-2025")
        case["contract_date"] = case["award_date"]
        with self.assertRaisesRegex(ValueError, "contract date"):
            validate_register(self.register, self.config)

    def test_legacy_contract_date_requires_checked_contract_amount_source(self):
        validate_register(self.register, self.config)
        case = self.register["cases"][0]
        self.assertEqual("contract", case["amount"]["kind"])
        self.assertNotIn("contract_date_source_refs", case)
        case["documents"] = [d for d in case["documents"] if d["kind"] != "contract-result"]
        with self.assertRaisesRegex(ValueError, "contract date"):
            validate_register(self.register, self.config)

    def test_storage_capacity_observations_keep_scope_and_basis(self):
        nagoya = next(c for c in self.register["cases"] if c["case_id"] == "PROC-NAGOYA-FURO-NEXT-2025")
        observations = nagoya["storage_capacity_observations"]
        self.assertEqual({(45, "unspecified"), (48.4, "physical"), (37.44, "effective"), (48, "unspecified")},
                         {(o["value"], o["capacity_basis"]) for o in observations})
        self.assertTrue(all(o["configuration_status"] == "planned" for o in observations))
        for refs in ([], ["UNKNOWN"]):
            changed = copy.deepcopy(self.register)
            case = next(c for c in changed["cases"] if c["case_id"] == nagoya["case_id"])
            case["storage_capacity_observations"][0]["source_refs"] = refs
            with self.subTest(refs=refs), self.assertRaises(ValueError):
                validate_register(changed, self.config)
        observations.append(copy.deepcopy(observations[0]))
        with self.assertRaises(ValueError):
            validate_register(self.register, self.config)

    def test_matching_and_amount_need_checked_public_evidence(self):
        self.register["cases"][0]["configuration_match"] = "confirmed"
        with self.assertRaises(ValueError):
            validate_register(self.register, self.config)
        self.register["cases"][0]["configuration_match"] = "unconfirmed"
        self.register["sources"][0]["retrieval_status"] = "not-retrieved"
        with self.assertRaises(ValueError):
            validate_register(self.register, self.config)

    def test_cost_intervals_require_complete_non_overlapping_scope(self):
        first = {"line_id": "CAPEX", "scope_ids": ["machine"], "phase": "initial",
                 "cost_jpy": {"lower": 80, "central": 100, "upper": 120},
                 "tax_basis": "excluding-tax", "basis": "estimated", "source_refs": ["TEST"]}
        annual = {**first, "line_id": "OPEX", "scope_ids": ["annual-operations"], "phase": "annual"}
        result = estimate_configuration([first, annual])
        self.assertEqual({"lower": 480, "central": 600, "upper": 720}, result["tco_jpy"])
        self.assertFalse(result["procurement_ready"])
        self.assertIsNone(estimate_configuration([first])["tco_jpy"])
        self.assertIsNone(estimate_configuration([first, {**annual, "cost_jpy": None}])["tco_jpy"])
        for changes in [{"scope_ids": ["machine"]}, {"scope_ids": []},
                        {"scope_ids": ["a", "a"]}, {"line_id": "CAPEX"},
                        {"cost_jpy": {"lower": 120, "central": 100, "upper": 80}}]:
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                estimate_configuration([first, {**annual, **changes}])

    def test_five_budgets_and_custom_budgets_never_imply_quantities(self):
        for profile in self.config["profiles"]:
            for budget in self.config["budget_ceilings_oku_jpy"] + [27.5]:
                result = allocate_budget(self.config, profile["scenario_id"], budget, 2030)
                self.assertAlmostEqual(budget, sum(r["allocation_oku_jpy"] for r in result["allocations"]))
                self.assertTrue(all(r["quantity"] is None and r["estimated_cost_oku_jpy"] is None for r in result["allocations"]))
                self.assertIsNone(result["tco_oku_jpy"])
                self.assertEqual("unverified", result["feasibility_status"])
                next_year = allocate_budget(self.config, profile["scenario_id"], budget, 2031)
                self.assertEqual(result["allocations"], next_year["allocations"])
        for value in (0, -1, float("nan"), float("inf"), True, 100001):
            with self.subTest(value=value), self.assertRaises(ValueError):
                allocate_budget(self.config, self.config["profiles"][0]["scenario_id"], value, 2030)
        self.config["profiles"][0]["shares_percent"]["storage"] += 1
        with self.assertRaises(ValueError):
            validate_register(self.register, self.config)

    def test_schema_and_publication_boundaries_fail_closed(self):
        schemas, registry = schema_registry(ROOT)
        validator = Draft202012Validator(schemas["procurement-cost-register.schema.json"], registry=registry)
        self.assertFalse(list(validator.iter_errors(self.register)))
        changed = copy.deepcopy(self.register)
        changed["cases"][0]["restricted_document_body"] = "not allowed"
        self.assertTrue(list(validator.iter_errors(changed)))
        changed = copy.deepcopy(self.register)
        changed["cases"][0]["amount"]["source_refs"] = ["UNKNOWN"]
        with self.assertRaises(ValueError):
            validate_register(changed, self.config)
        policy = read("config/publication-policy.json")
        with patch("build_pages_site.approved_publication_directives", return_value={}):
            with self.assertRaises(ValueError):
                collect_procurement_costs(ROOT, policy)

    def test_offline_reconciliation_does_not_forge_a_fetch(self):
        previous = read("knowledge/public/audits/roadmap-source-audit.json")
        old = copy.deepcopy(previous)
        previous["results"] = [r for r in previous["results"] if r["source_id"] != "SRC-MEM042"]
        result = reconcile_offline(ROOT, previous)
        self.assertEqual(old["checked_at"], result["checked_at"])
        self.assertEqual(old["summary"]["fetch_count"], result["summary"]["fetch_count"])
        entry = next(r for r in result["results"] if r["source_id"] == "SRC-MEM042")
        self.assertEqual("not-audited", entry["error_kind"])
        self.assertIsNone(entry["http_status"])
        self.assertNotIn("retrieval_receipt_id", entry)
        self.assertEqual(result, reconcile_offline(ROOT, result))

    def test_nvhbm_is_announced_not_shipped(self):
        memory = read("knowledge/public/roadmaps/memory-data-movement.json")
        lane = next(l for l in memory["lanes"] if l["lane_id"] == "LANE-HBM-NVIDIA-NVHBM")
        event, shipment = lane["milestones"]
        self.assertEqual((2026, "Q3", "observed"), (event["year"], event["quarter"], event["timing_basis"]))
        self.assertIsNone(shipment["year"])
        self.assertEqual("no-public-date", shipment["timing_basis"])
        reference = read("knowledge/public/roadmap-reference-data.json")
        self.assertEqual(1, sum(t["term_id"] == "TERM-NVHBM" for t in reference["terms"]))

    def test_unattempted_http_check_is_not_described_as_a_connection_failure(self):
        def load_with_pending_audit(path):
            payload = json.loads(path.read_text())
            if path.name == "roadmap-source-audit.json":
                for result in payload["results"]:
                    if result["source_id"] in {"SRC-MEM042", "SRC-MEM043"}:
                        result.update(status="error", error_kind="not-audited", http_status=None)
            return payload
        with patch("build_roadmap_freshness_audit.load_json", side_effect=load_with_pending_audit):
            audit = build_freshness(ROOT)
        entries = [e for e in audit["attention_items"] if e["object_id"] in {"SRC-MEM042", "SRC-MEM043"}]
        self.assertEqual(2, len(entries))
        self.assertTrue(all(e["reason"] == "source-not-audited" for e in entries))

    def test_short_labels_keep_full_titles_and_public_ids(self):
        taxonomy = read("config/catalog-taxonomy.json")
        self.assertEqual(["ハードウェア", "システムソフト", "アプリ", "運用・調達", "制度・運営", "分野横断"],
                         [c["short_title_ja"] for c in taxonomy["categories"]])
        for script in ("site/app.js", "site/roadmaps.js"):
            text = (ROOT / script).read_text()
            self.assertIn("short_title_", text)
            self.assertIn('"aria-label"', text)

    def test_budget_ui_events_offline(self):
        node = os.environ.get("OPENFS_NODE") or shutil.which("node")
        if not node:
            self.skipTest("Node.js is required for UI event tests")
        subprocess.run([node, "--test", "tests/test_budget_ui.js"], cwd=ROOT,
                       check=True, capture_output=True, text=True)


if __name__ == "__main__":
    unittest.main()
