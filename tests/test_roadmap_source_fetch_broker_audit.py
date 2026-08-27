from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

from audit_roadmap_sources_via_fetch_broker import build_audit, check_source  # noqa: E402
from safe_web_fetch_broker import FetchBlocked, FetchResult  # noqa: E402


def receipt(**changes):
    value = {
        "receipt_id": "WEB-ABCDEF012345",
        "security_profile_id": "SEC-PROFILE-TEST",
        "final_url": "https://example.com/final",
        "http_status": 200,
        "media_type": "text/html",
        "policy_decision": "allowed",
        "body_truncated": False,
    }
    value.update(changes)
    return value


SOURCE = {
    "roadmap_id": "RM-TEST",
    "source_id": "SRC-TEST",
    "url": "https://example.com/start",
    "source_class": "vendor-official",
}


class StubBroker:
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error
        self.calls = []

    def fetch(self, url, *, method, capture_limit):
        self.calls.append(url)
        if self.error:
            raise self.error
        return self.result


class RoadmapSourceFetchBrokerAuditTests(unittest.TestCase):
    def test_reachable_result_preserves_fetch_provenance(self):
        result = check_source(SOURCE, StubBroker(FetchResult(b"ok", receipt())))
        self.assertEqual("reachable", result["status"])
        self.assertEqual("WEB-ABCDEF012345", result["retrieval_receipt_id"])
        self.assertEqual("SEC-PROFILE-TEST", result["security_profile_id"])

    def test_policy_block_is_reported_as_an_audit_error(self):
        blocked_receipt = receipt(
            http_status=None,
            media_type=None,
            policy_decision="blocked",
        )
        result = check_source(
            SOURCE,
            StubBroker(error=FetchBlocked("private destination", blocked_receipt)),
        )
        self.assertEqual("error", result["status"])
        self.assertEqual("policy-block", result["error_kind"])
        self.assertEqual("blocked", result["fetch_policy_decision"])

    def test_published_audit_keeps_per_source_results_without_raw_errors(self):
        blocked_receipt = receipt(
            http_status=None,
            media_type=None,
            policy_decision="blocked",
        )
        audit = build_audit(
            ROOT,
            StubBroker(error=FetchBlocked("private destination", blocked_receipt)),
            workers=2,
        )
        self.assertEqual(audit["summary"]["source_count"], len(audit["results"]))
        self.assertTrue(all("error_detail" not in item for item in audit["results"]))
        self.assertTrue(all(item["error_kind"] == "policy-block" for item in audit["results"]))

    def test_duplicate_urls_are_fetched_once_and_mapped_to_each_source(self):
        broker = StubBroker(FetchResult(b"ok", receipt()))
        audit = build_audit(ROOT, broker, workers=2)
        unique_urls = {item["url"] for item in audit["results"]}
        self.assertEqual(len(unique_urls), len(broker.calls))
        self.assertEqual(audit["summary"]["fetch_count"], len(unique_urls))
        self.assertEqual(len(broker.calls), len(set(broker.calls)))
        self.assertEqual(audit["summary"]["source_count"], len(audit["results"]))


if __name__ == "__main__":
    unittest.main()
