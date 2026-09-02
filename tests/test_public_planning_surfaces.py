import copy
import json
import tempfile
import unittest
from pathlib import Path

from tests.test_performance_model_card import valid_card
from tools.check_public_planning_surfaces import (
    EXPECTED_INFRASTRUCTURE_DIMENSIONS, EXPECTED_SCALES, validate,
    validate_source_corrections, validate_topic_decision_support,
)


ROOT = Path(__file__).resolve().parents[1]


class SourceCorrectionTests(unittest.TestCase):
    def source(self, sid, previous=None):
        value = {"source_id": sid}
        if previous is not None:
            value["correction"] = {"supersedes_source_id": previous,
                                   "reason_ja": "書誌情報を訂正", "reason_en": "Correct metadata"}
        return value

    def test_append_only_linear_history(self):
        sources = [self.source("SRC-OLD"), self.source("SRC-NEW", "SRC-OLD"),
                   self.source("SRC-LATEST", "SRC-NEW")]
        before = copy.deepcopy(sources)
        self.assertEqual([], validate_source_corrections(sources))
        self.assertEqual(before, sources)

    def test_unknown_self_cycle_and_fork_rejected(self):
        for sources, message in (
            ([self.source("SRC-A", "SRC-MISSING")], "unknown source"),
            ([self.source("SRC-A", "SRC-A")], "cannot correct itself"),
            ([self.source("SRC-A", "SRC-B"), self.source("SRC-B", "SRC-A")], "cyclic"),
            ([self.source("SRC-A"), self.source("SRC-B", "SRC-A"), self.source("SRC-C", "SRC-A")], "forks"),
        ):
            with self.subTest(message=message):
                self.assertTrue(any(message in e for e in validate_source_corrections(sources)))

    def test_bilingual_nonblank_reasons_required(self):
        for value in (None, "", " \n "):
            source = self.source("SRC-NEW", "SRC-OLD")
            source["correction"]["reason_en"] = value
            self.assertTrue(any("bilingual" in e for e in validate_source_corrections(
                [self.source("SRC-OLD"), source])))

    def test_historical_metadata_may_remain_but_active_uses_fail(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for ref in ("config/research-baseline.json", "knowledge/public/topic-decision-support.json"):
                (root / ref).parent.mkdir(parents=True, exist_ok=True)
                (root / ref).write_text((ROOT / ref).read_text())
            path = root / "knowledge/public/topic-decision-support.json"
            surface = json.loads(path.read_text())
            old = {**surface["sources"][0], "source_id": "SRC-TEST-HISTORICAL"}
            new = {**old, **self.source("SRC-TEST-CORRECTED", old["source_id"])}
            surface["sources"].extend([old, new])
            profile = next(p for p in surface["topic_profiles"] if p.get("archived_section_ids"))
            historical = next(s for s in profile["sections"] if s["section_id"] in profile["archived_section_ids"])
            historical["items"][0]["source_ids"].append(old["source_id"])
            path.write_text(json.dumps(surface))
            self.assertEqual([], validate_topic_decision_support(root))
            active = next(s for s in profile["sections"] if s["section_id"] not in profile["archived_section_ids"])
            active["items"][0]["source_ids"].append(old["source_id"])
            path.write_text(json.dumps(surface))
            self.assertTrue(any("superseded source metadata" in e for e in validate_topic_decision_support(root)))


class PublicPlanningSurfaceTests(unittest.TestCase):
    def test_repository_surfaces_pass(self):
        self.assertEqual(validate(ROOT), [])

    def test_standard_scales_are_fixed(self):
        self.assertEqual(EXPECTED_SCALES, [1, 4, 32, 128, 1024, 10000])

    def test_calibration_candidates_are_measured_but_not_accepted(self):
        payload = json.loads(
            (
                ROOT
                / "knowledge/public/application-performance-forecasts.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual(2, len(payload["calibration_candidates"]))
        self.assertEqual(
            {"PMCAL-GENESIS-WEAK-001", "PMCAL-SALMON-WEAK-001"},
            {item["calibration_candidate_id"] for item in payload["calibration_candidates"]},
        )
        for candidate in payload["calibration_candidates"]:
            validation_ids = {
                item["observation_id"] for item in candidate["validation_results"]
            }
            self.assertFalse(
                set(candidate["calibration_observation_ids"]) & validation_ids
            )
            self.assertLess(candidate["maximum_relative_error"], 0.07)
            self.assertFalse(candidate["readiness"]["candidate_ready_for_consensus"])
            self.assertEqual("incomplete", candidate["consensus_status"])
            self.assertFalse(candidate["procurement_eligible"])

    def test_planning_evidence_readiness_is_complete_in_scope_but_provisional(self):
        payload = json.loads(
            (ROOT / "knowledge/public/planning-evidence-readiness.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            ["system-lifecycle", "operations", "five-year-cost", "application-performance", "quantitative-requirements"],
            [item["dimension_id"] for item in payload["dimensions"]],
        )
        dimensions = {item["dimension_id"]: item for item in payload["dimensions"]}
        self.assertEqual(9, dimensions["system-lifecycle"]["coverage"]["numerator"])
        self.assertEqual(11, dimensions["operations"]["coverage"]["numerator"])
        self.assertEqual(
            {"observed-start": 24, "any-lifecycle": 26},
            {
                item["coverage_id"]: item["numerator"]
                for item in dimensions["system-lifecycle"]["supporting_coverages"]
            },
        )
        self.assertEqual(
            {
                "utilization": 5,
                "power": 1,
                "availability-downtime": 4,
                "jobs-history": 6,
            },
            {
                item["coverage_id"]: item["numerator"]
                for item in dimensions["operations"]["supporting_coverages"]
            },
        )
        self.assertEqual(
            {"complete-tco": 0, "public-total": 7, "component-itemization": 0},
            {
                item["coverage_id"]: item["numerator"]
                for item in dimensions["five-year-cost"]["supporting_coverages"]
            },
        )
        self.assertEqual(3, len(payload["scenario_assessments"]))
        self.assertEqual("provisional", payload["research_status"])
        self.assertEqual("incomplete", payload["consensus_status"])

    def test_infrastructure_matrix_covers_every_application_and_dimension(self):
        payload = json.loads(
            (
                ROOT
                / "knowledge/public/application-performance-forecasts.json"
            ).read_text(encoding="utf-8")
        )
        matrix = payload["infrastructure_requirements_matrix"]
        self.assertEqual(
            EXPECTED_INFRASTRUCTURE_DIMENSIONS,
            [item["dimension_id"] for item in matrix["dimensions"]],
        )
        self.assertEqual(
            {item["application_id"] for item in payload["applications"]},
            {item["application_id"] for item in matrix["rows"]},
        )
        self.assertTrue(
            all(
                [item["dimension_id"] for item in row["cells"]]
                == EXPECTED_INFRASTRUCTURE_DIMENSIONS
                for row in matrix["rows"]
            )
        )

    def test_rejects_calibration_arithmetic_and_incomplete_matrix(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for relative in (
                "config/hpci-center-registry.json",
                "knowledge/public/hpci-system-inventory.json",
                "knowledge/public/application-performance-forecasts.json",
            ):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(
                    (ROOT / relative).read_text(encoding="utf-8"), encoding="utf-8"
                )
            path = root / "knowledge/public/application-performance-forecasts.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["calibration_candidates"][0]["validation_results"][0][
                "absolute_error"
            ] = 999
            payload["infrastructure_requirements_matrix"]["rows"][0]["cells"].pop()
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            errors = validate(root)
            self.assertTrue(any("inconsistent absolute error" in error for error in errors))
            self.assertTrue(
                any("must cover every dimension in order" in error for error in errors)
            )

    def test_eea1_code_availability_is_explicit(self):
        payload = json.loads(
            (
                ROOT
                / "knowledge/public/application-performance-forecasts.json"
            ).read_text(encoding="utf-8")
        )
        applications = {item["name"]: item for item in payload["applications"]}
        self.assertEqual(
            {
                "GENESIS",
                "SALMON",
                "SCALE-LETKF",
                "LQCD-DWF-HMC",
            },
            {
                name
                for name, item in applications.items()
                if item["code_availability"]["status"]
                == "public-source-confirmed"
            },
        )
        self.assertEqual(
            {"E-Wave", "FrontFlow/blue"},
            {
                name
                for name, item in applications.items()
                if item["code_availability"]["status"]
                == "unreleased-in-eea1-reference"
            },
        )
        self.assertTrue(
            all("GAP-PERF-005" in item["coverage_gap_refs"] for item in applications.values())
        )
        source_ids = {item["source_id"] for item in payload["sources"]}
        self.assertTrue(
            all(
                set(item["code_availability"]["source_ids"]).issubset(source_ids)
                for item in applications.values()
            )
        )

    def test_rejects_reused_calibration_data(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "config").mkdir()
            (root / "knowledge/public").mkdir(parents=True)
            for relative in (
                "config/hpci-center-registry.json",
                "knowledge/public/hpci-system-inventory.json",
                "knowledge/public/application-performance-forecasts.json",
            ):
                source = json.loads((ROOT / relative).read_text(encoding="utf-8"))
                (root / relative).write_text(
                    json.dumps(source, ensure_ascii=False), encoding="utf-8"
                )
            path = root / "knowledge/public/application-performance-forecasts.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["forecasts"] = [
                {
                    "forecast_id": "FORECAST-TEST-001",
                    "forecast_class": "validated",
                    "application_id": "APP-EEA1-GENESIS",
                    "candidate_system_id": "FUGAKUNEXT-PUBLIC-DESIGN-PROXY",
                    "fugaku_nodes": 4,
                    "scaling_mode": "strong-scaling",
                    "comparison_basis": "same-node-count",
                    "metric_id": "time-to-solution",
                    "estimate": {"lower": 1.0, "base": 2.0, "upper": 3.0, "unit": "s"},
                    "model_card_id": "PMCARD-OPENFS-ANALYTICAL-001",
                    "assumption_ids": ["ASM-PERF-GENESIS"],
                    "basis_source_ids": ["SRC-PERF001"],
                    "calibration_dataset_ids": ["DATA-SHARED"],
                    "validation_dataset_ids": ["DATA-SHARED"],
                    "confidence": "medium",
                    "consensus_status": "accepted",
                    "procurement_eligible": False,
                }
            ]
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            self.assertTrue(
                any("reuses calibration data" in error for error in validate(root))
            )
            self.assertTrue(
                any(
                    "not validated and Consensus-accepted" in error
                    for error in validate(root)
                )
            )

    def test_legacy_illustrations_are_complete_and_formal_forecasts_are_empty(self):
        payload = json.loads(
            (
                ROOT
                / "knowledge/public/application-performance-forecasts.json"
            ).read_text(encoding="utf-8")
        )
        self.assertEqual([], payload["forecasts"])
        self.assertEqual([], payload["validated_model_cards"])
        self.assertEqual(36, len(payload["illustrations"]))
        self.assertEqual(
            36,
            len({item["legacy_forecast_id"] for item in payload["illustrations"]}),
        )
        self.assertTrue(
            all(
                item["legacy_forecast_id"].replace("FORECAST-", "ILLUSTRATION-", 1)
                == item["illustration_id"]
                for item in payload["illustrations"]
            )
        )

    def test_accepts_forecast_backed_by_accepted_validated_model_card(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "config").mkdir()
            (root / "knowledge/public").mkdir(parents=True)
            for relative in (
                "config/hpci-center-registry.json",
                "knowledge/public/hpci-system-inventory.json",
                "knowledge/public/application-performance-forecasts.json",
            ):
                source = json.loads((ROOT / relative).read_text(encoding="utf-8"))
                (root / relative).write_text(
                    json.dumps(source, ensure_ascii=False), encoding="utf-8"
                )
            path = root / "knowledge/public/application-performance-forecasts.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            card = valid_card()
            card["status"] = "accepted"
            card["consensus_status"] = "accepted"
            payload["validated_model_cards"] = [card]
            payload["forecasts"] = [
                {
                    "forecast_id": "FORECAST-VALIDATED-TEST-001",
                    "forecast_class": "validated",
                    "application_id": "APP-EEA1-GENESIS",
                    "candidate_system_id": "FUGAKUNEXT-PUBLIC-DESIGN-PROXY",
                    "fugaku_nodes": 4,
                    "scaling_mode": "strong-scaling",
                    "comparison_basis": "same-node-count",
                    "metric_id": "time-to-solution",
                    "estimate": {"lower": 1.0, "base": 2.0, "upper": 3.0, "unit": "s"},
                    "model_card_id": "PMCARD-TEST-001",
                    "assumption_ids": ["ASM-PERF-GENESIS"],
                    "basis_source_ids": ["SRC-PERF001"],
                    "calibration_dataset_ids": ["DATA-CAL"],
                    "validation_dataset_ids": ["DATA-VAL-A"],
                    "confidence": "medium",
                    "consensus_status": "accepted",
                    "procurement_eligible": False,
                }
            ]
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            self.assertEqual([], validate(root))

    def test_rejects_unknown_code_availability_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for relative in (
                "config/research-baseline.json",
                "config/hpci-center-registry.json",
                "knowledge/public/hpci-system-inventory.json",
                "knowledge/public/application-performance-forecasts.json",
                "knowledge/public/topic-decision-support.json",
            ):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(
                    (ROOT / relative).read_text(encoding="utf-8"), encoding="utf-8"
                )
            path = root / "knowledge/public/application-performance-forecasts.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["applications"][0]["code_availability"]["source_ids"] = [
                "SRC-PERF999"
            ]
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            self.assertTrue(
                any("code availability has unknown sources" in error for error in validate(root))
            )

    def test_rejects_unknown_topic_decision_source(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for relative in (
                "config/research-baseline.json",
                "config/hpci-center-registry.json",
                "knowledge/public/hpci-system-inventory.json",
                "knowledge/public/application-performance-forecasts.json",
                "knowledge/public/topic-decision-support.json",
            ):
                target = root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(
                    (ROOT / relative).read_text(encoding="utf-8"), encoding="utf-8"
                )
            path = root / "knowledge/public/topic-decision-support.json"
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["actors"][0]["source_ids"] = ["SRC-UNKNOWN"]
            path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            self.assertTrue(
                any("unknown sources" in error for error in validate(root))
            )


if __name__ == "__main__":
    unittest.main()
