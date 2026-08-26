from __future__ import annotations

import json
import unittest
from pathlib import Path
from urllib.parse import SplitResult

from tools.safe_web_fetch_broker import (
    FetchBlocked,
    FetchFailed,
    SafeWebFetchBroker,
    TransportResponse,
)


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_IP = "93.184.216.34"


def policy():
    return json.loads((ROOT / "config/research-web-security-policy.json").read_text())


class RecordingTransport:
    def __init__(self, responses: list[TransportResponse]):
        self.responses = responses
        self.calls: list[dict[str, object]] = []

    def __call__(
        self,
        parts: SplitResult,
        method: str,
        headers: dict[str, str],
        addresses: list[str],
        connect_timeout: float,
        total_timeout: float,
        capture_limit: int,
    ) -> TransportResponse:
        self.calls.append(
            {
                "url": parts.geturl(),
                "method": method,
                "headers": dict(headers),
                "addresses": list(addresses),
                "connect_timeout": connect_timeout,
                "total_timeout": total_timeout,
                "capture_limit": capture_limit,
            }
        )
        return self.responses.pop(0)


def response(
    status: int = 200,
    *,
    media_type: str = "text/html",
    body: bytes = b"public",
    peer_ip: str = PUBLIC_IP,
    location: str | None = None,
) -> TransportResponse:
    headers = {"content-type": media_type}
    if location:
        headers["location"] = location
    return TransportResponse(status, headers, body, peer_ip)


class SafeWebFetchBrokerTests(unittest.TestCase):
    def broker(self, resolver, transport):
        return SafeWebFetchBroker(
            policy(),
            security_profile_id="SEC-PROFILE-TEST",
            resolver=resolver,
            transport=transport,
        )

    def test_success_is_anonymous_and_emits_a_complete_receipt(self):
        transport = RecordingTransport([response()])
        result = self.broker(lambda host, port: [PUBLIC_IP], transport).fetch(
            "https://example.com/report", capture_limit=1024
        )
        self.assertEqual(b"public", result.body)
        self.assertEqual("allowed", result.receipt["policy_decision"])
        self.assertEqual(PUBLIC_IP, result.receipt["connection_ip"])
        self.assertFalse(result.receipt["credentials_forwarded"])
        sent_headers = {name.lower() for name in transport.calls[0]["headers"]}
        self.assertFalse({"authorization", "cookie", "proxy-authorization"} & sent_headers)

    def test_non_read_method_and_embedded_credentials_are_blocked(self):
        broker = self.broker(lambda host, port: [PUBLIC_IP], RecordingTransport([]))
        with self.assertRaises(FetchBlocked):
            broker.fetch("https://example.com", method="POST")
        with self.assertRaises(FetchBlocked):
            broker.fetch("https://user:secret@example.com")

    def test_local_hostname_and_nonstandard_or_mismatched_ports_are_blocked(self):
        broker = self.broker(lambda host, port: [PUBLIC_IP], RecordingTransport([]))
        for url in (
            "http://localhost/",
            "https://service.internal/data",
            "https://example.com:8443/",
            "http://example.com:443/",
        ):
            with self.subTest(url=url), self.assertRaises(FetchBlocked):
                broker.fetch(url)

    def test_private_reserved_and_mixed_dns_answers_are_blocked(self):
        transport = RecordingTransport([])
        for addresses in (
            ["127.0.0.1"],
            ["169.254.169.254"],
            ["192.168.1.2"],
            ["192.0.2.1"],
            [PUBLIC_IP, "10.0.0.2"],
            ["::ffff:127.0.0.1"],
        ):
            with self.subTest(addresses=addresses), self.assertRaises(FetchBlocked):
                self.broker(lambda host, port, values=addresses: values, transport).fetch(
                    "https://example.com"
                )
        self.assertEqual([], transport.calls)

    def test_excessive_dns_answers_are_blocked(self):
        addresses = [f"8.8.8.{index}" for index in range(1, 18)]
        with self.assertRaises(FetchBlocked):
            self.broker(lambda host, port: addresses, RecordingTransport([])).fetch(
                "https://example.com"
            )

    def test_redirect_target_is_resolved_and_rechecked(self):
        transport = RecordingTransport(
            [response(302, body=b"", location="http://metadata.internal/latest")]
        )

        def resolver(host: str, port: int):
            return [PUBLIC_IP] if host == "example.com" else ["169.254.169.254"]

        with self.assertRaises(FetchBlocked) as context:
            self.broker(resolver, transport).fetch("https://example.com/start")
        self.assertIn("blocked namespace", str(context.exception))
        self.assertEqual(1, len(transport.calls))

    def test_connection_peer_must_match_validated_dns_answer(self):
        transport = RecordingTransport([response(peer_ip="8.8.8.8")])
        with self.assertRaises(FetchBlocked) as context:
            self.broker(lambda host, port: [PUBLIC_IP], transport).fetch("https://example.com")
        self.assertIn("did not match", str(context.exception))

    def test_disallowed_media_type_and_oversized_injected_body_are_blocked(self):
        for transport in (
            RecordingTransport([response(media_type="application/octet-stream")]),
            RecordingTransport([response(body=b"12345")]),
        ):
            with self.subTest(), self.assertRaises(FetchBlocked):
                self.broker(lambda host, port: [PUBLIC_IP], transport).fetch(
                    "https://example.com", capture_limit=4
                )

    def test_dns_and_transport_failures_are_distinct_from_policy_blocks(self):
        def failed_resolver(host: str, port: int):
            raise OSError("resolver unavailable")

        with self.assertRaises(FetchFailed) as dns_context:
            self.broker(failed_resolver, RecordingTransport([])).fetch("https://example.com")
        self.assertEqual("allowed", dns_context.exception.receipt["policy_decision"])
        self.assertIsNotNone(dns_context.exception.receipt["retrieval_error"])

        def failed_transport(*args):
            raise TimeoutError("timed out")

        with self.assertRaises(FetchFailed) as transport_context:
            self.broker(lambda host, port: [PUBLIC_IP], failed_transport).fetch(
                "https://example.com"
            )
        self.assertIn("TimeoutError", transport_context.exception.receipt["retrieval_error"])


if __name__ == "__main__":
    unittest.main()
