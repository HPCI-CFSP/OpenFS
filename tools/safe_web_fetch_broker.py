#!/usr/bin/env python3
"""Fetch anonymous public Web resources through a fail-closed policy boundary."""

from __future__ import annotations

import argparse
import hashlib
import http.client
import ipaddress
import json
import os
import secrets
import socket
import ssl
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence
from urllib.parse import SplitResult, urljoin, urlsplit, urlunsplit


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_POLICY = ROOT / "config" / "research-web-security-policy.json"
DEFAULT_USER_AGENT = "OpenFS Safe Web Fetch Broker/0.1 (+https://github.com/HPCI-CFSP/OpenFS)"
REDIRECT_STATUSES = {301, 302, 303, 307, 308}
SENSITIVE_HEADERS = {"authorization", "cookie", "proxy-authorization"}


@dataclass(frozen=True)
class TransportResponse:
    status: int
    headers: Mapping[str, str]
    body: bytes
    peer_ip: str
    body_truncated: bool = False


@dataclass(frozen=True)
class FetchResult:
    body: bytes
    receipt: dict[str, Any]


class FetchBrokerError(RuntimeError):
    """Base error carrying a redacted retrieval receipt."""

    def __init__(self, message: str, receipt: dict[str, Any]):
        super().__init__(message)
        self.receipt = receipt


class FetchBlocked(FetchBrokerError):
    """The request violated the configured fetch policy."""


class FetchFailed(FetchBrokerError):
    """The request passed policy checks but failed during retrieval."""


Resolver = Callable[[str, int], Sequence[str]]
Transport = Callable[
    [SplitResult, str, Mapping[str, str], Sequence[str], float, float, int],
    TransportResponse,
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _default_resolver(host: str, port: int) -> list[str]:
    answers = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
    return sorted({str(answer[4][0]) for answer in answers})


class _PinnedHTTPConnection(http.client.HTTPConnection):
    def __init__(self, host: str, port: int, connect_ip: str, timeout: float):
        super().__init__(host, port=port, timeout=timeout)
        self.connect_ip = connect_ip

    def connect(self) -> None:
        self.sock = socket.create_connection((self.connect_ip, self.port), self.timeout)


class _PinnedHTTPSConnection(http.client.HTTPSConnection):
    def __init__(self, host: str, port: int, connect_ip: str, timeout: float):
        super().__init__(host, port=port, timeout=timeout, context=ssl.create_default_context())
        self.connect_ip = connect_ip

    def connect(self) -> None:
        raw_socket = socket.create_connection((self.connect_ip, self.port), self.timeout)
        self.sock = self._context.wrap_socket(raw_socket, server_hostname=self.host)


def _default_transport(
    parts: SplitResult,
    method: str,
    headers: Mapping[str, str],
    addresses: Sequence[str],
    connect_timeout: float,
    total_timeout: float,
    capture_limit: int,
) -> TransportResponse:
    port = parts.port or (443 if parts.scheme == "https" else 80)
    path = urlunsplit(("", "", parts.path or "/", parts.query, ""))
    last_error: OSError | None = None
    deadline = time.monotonic() + total_timeout
    for address in addresses:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise TimeoutError("total retrieval timeout exceeded")
        timeout = min(connect_timeout, remaining)
        connection: http.client.HTTPConnection
        if parts.scheme == "https":
            connection = _PinnedHTTPSConnection(parts.hostname or "", port, address, timeout)
        else:
            connection = _PinnedHTTPConnection(parts.hostname or "", port, address, timeout)
        try:
            connection.request(method, path, headers=dict(headers))
            response = connection.getresponse()
            peer_ip = str(connection.sock.getpeername()[0]) if connection.sock else ""
            response_headers = {name.lower(): value for name, value in response.getheaders()}
            if method == "HEAD" or response.status in REDIRECT_STATUSES:
                body = b""
                truncated = False
            else:
                payload_parts: list[bytes] = []
                payload_size = 0
                while payload_size <= capture_limit:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        raise TimeoutError("total retrieval timeout exceeded")
                    if connection.sock:
                        connection.sock.settimeout(remaining)
                    chunk = response.read1(min(65536, capture_limit + 1 - payload_size))
                    if not chunk:
                        break
                    payload_parts.append(chunk)
                    payload_size += len(chunk)
                payload = b"".join(payload_parts)
                truncated = len(payload) > capture_limit
                body = payload[:capture_limit]
            return TransportResponse(
                status=response.status,
                headers=response_headers,
                body=body,
                peer_ip=peer_ip,
                body_truncated=truncated,
            )
        except (OSError, http.client.HTTPException, ssl.SSLError) as exc:
            last_error = exc
        finally:
            connection.close()
    if last_error:
        raise last_error
    raise OSError("no validated destination address was available")


class SafeWebFetchBroker:
    """Policy evaluator and pinned transport for anonymous public-Web reads."""

    def __init__(
        self,
        policy: Mapping[str, Any],
        *,
        security_profile_id: str,
        resolver: Resolver = _default_resolver,
        transport: Transport = _default_transport,
        clock: Callable[[], float] = time.monotonic,
    ):
        self.policy = policy
        self.fetch_policy = policy["capabilities"]["web_fetch"]
        self.boundaries = policy["network_boundaries"]
        self.security_profile_id = security_profile_id
        self.resolver = resolver
        self.transport = transport
        self.clock = clock
        self.blocked_networks = tuple(
            ipaddress.ip_network(cidr)
            for cidr in (
                *self.boundaries["blocked_ipv4_cidrs"],
                *self.boundaries["blocked_ipv6_cidrs"],
            )
        )
        self.metadata_addresses = {
            ipaddress.ip_address(address)
            for address in self.boundaries.get("cloud_metadata_addresses", [])
        }

    @classmethod
    def from_file(
        cls,
        policy_path: Path = DEFAULT_POLICY,
        **kwargs: Any,
    ) -> "SafeWebFetchBroker":
        return cls(json.loads(policy_path.read_text(encoding="utf-8")), **kwargs)

    def _receipt(
        self,
        *,
        requested_url: str,
        final_url: str,
        redirect_chain: Sequence[str],
        method: str,
        policy_decision: str,
        http_status: int | None = None,
        media_type: str | None = None,
        body: bytes = b"",
        body_truncated: bool = False,
        connection_ip: str | None = None,
        block_reason: str | None = None,
        retrieval_error: str | None = None,
    ) -> dict[str, Any]:
        retrieved_at = _utc_now()
        return {
            "schema_version": "0.1.0",
            "receipt_id": f"WEB-{secrets.token_hex(6).upper()}",
            "tool_name": "web_fetch",
            "security_profile_id": self.security_profile_id,
            "requested_url": requested_url,
            "final_url": final_url,
            "redirect_chain": list(redirect_chain),
            "method": method,
            "http_status": http_status,
            "media_type": media_type,
            "response_bytes": len(body),
            "retrieved_at": retrieved_at,
            "policy_decision": policy_decision,
            "block_reason": block_reason,
            "retrieval_error": retrieval_error,
            "content_sha256": hashlib.sha256(body).hexdigest() if body else None,
            "credentials_forwarded": False,
            "connection_ip": connection_ip,
            "body_truncated": body_truncated,
        }

    def _block(
        self,
        reason: str,
        *,
        requested_url: str,
        final_url: str,
        redirect_chain: Sequence[str],
        method: str,
        http_status: int | None = None,
        media_type: str | None = None,
        body: bytes = b"",
        connection_ip: str | None = None,
    ) -> FetchBlocked:
        return FetchBlocked(
            reason,
            self._receipt(
                requested_url=requested_url,
                final_url=final_url,
                redirect_chain=redirect_chain,
                method=method,
                http_status=http_status,
                media_type=media_type,
                body=body,
                connection_ip=connection_ip,
                policy_decision="blocked",
                block_reason=reason,
            ),
        )

    def _parse_and_validate_url(
        self,
        url: str,
        *,
        requested_url: str,
        redirect_chain: Sequence[str],
        method: str,
    ) -> tuple[SplitResult, list[str]]:
        try:
            parts = urlsplit(url)
            port = parts.port or (443 if parts.scheme == "https" else 80)
        except ValueError as exc:
            raise self._block(
                f"invalid URL: {exc}",
                requested_url=requested_url,
                final_url=url,
                redirect_chain=redirect_chain,
                method=method,
            ) from exc
        if parts.scheme.lower() not in self.fetch_policy["allowed_schemes"]:
            raise self._block(
                "URL scheme is not allowed",
                requested_url=requested_url,
                final_url=url,
                redirect_chain=redirect_chain,
                method=method,
            )
        if not parts.hostname or parts.username is not None or parts.password is not None:
            raise self._block(
                "URL must contain a hostname and must not contain user information",
                requested_url=requested_url,
                final_url=url,
                redirect_chain=redirect_chain,
                method=method,
            )
        if port not in self.fetch_policy.get("allowed_ports", [80, 443]):
            raise self._block(
                "destination port is not allowed",
                requested_url=requested_url,
                final_url=url,
                redirect_chain=redirect_chain,
                method=method,
            )
        expected_port = 443 if parts.scheme.lower() == "https" else 80
        if port != expected_port:
            raise self._block(
                "URL scheme and destination port do not match the permitted public-Web endpoint",
                requested_url=requested_url,
                final_url=url,
                redirect_chain=redirect_chain,
                method=method,
            )
        host = parts.hostname.rstrip(".").lower()
        if host in self.boundaries["blocked_hostnames"] or any(
            host.endswith(suffix) for suffix in self.boundaries["blocked_hostname_suffixes"]
        ):
            raise self._block(
                "hostname is inside a blocked namespace",
                requested_url=requested_url,
                final_url=url,
                redirect_chain=redirect_chain,
                method=method,
            )
        try:
            addresses = list(self.resolver(host, port))
        except (OSError, socket.gaierror) as exc:
            receipt = self._receipt(
                requested_url=requested_url,
                final_url=url,
                redirect_chain=redirect_chain,
                method=method,
                policy_decision="allowed",
                retrieval_error=f"DNS resolution failed: {type(exc).__name__}",
            )
            raise FetchFailed("DNS resolution failed", receipt) from exc
        if not addresses:
            receipt = self._receipt(
                requested_url=requested_url,
                final_url=url,
                redirect_chain=redirect_chain,
                method=method,
                policy_decision="allowed",
                retrieval_error="DNS resolution returned no addresses",
            )
            raise FetchFailed("DNS resolution returned no addresses", receipt)
        maximum_dns_answers = int(self.fetch_policy.get("maximum_dns_answers", 16))
        if len(addresses) > maximum_dns_answers:
            raise self._block(
                "DNS response exceeded the address-count limit",
                requested_url=requested_url,
                final_url=url,
                redirect_chain=redirect_chain,
                method=method,
            )
        for address_text in addresses:
            try:
                address = ipaddress.ip_address(address_text)
            except ValueError as exc:
                raise self._block(
                    "DNS returned an invalid IP address",
                    requested_url=requested_url,
                    final_url=url,
                    redirect_chain=redirect_chain,
                    method=method,
                ) from exc
            comparable = (
                address.ipv4_mapped or address
                if isinstance(address, ipaddress.IPv6Address)
                else address
            )
            if not comparable.is_global or comparable in self.metadata_addresses or any(
                comparable.version == network.version and comparable in network
                for network in self.blocked_networks
            ):
                raise self._block(
                    "DNS returned a blocked destination address",
                    requested_url=requested_url,
                    final_url=url,
                    redirect_chain=redirect_chain,
                    method=method,
                )
        return parts, addresses

    def fetch(self, url: str, *, method: str = "GET", capture_limit: int | None = None) -> FetchResult:
        method = method.upper()
        if method not in self.fetch_policy["allowed_methods"]:
            raise self._block(
                "HTTP method is not allowed",
                requested_url=url,
                final_url=url,
                redirect_chain=[],
                method=method,
            )
        maximum_bytes = int(self.fetch_policy["maximum_response_bytes"])
        if capture_limit is None:
            capture_limit = maximum_bytes
        if capture_limit < 0 or capture_limit > maximum_bytes:
            raise self._block(
                "capture limit exceeds the response-size policy",
                requested_url=url,
                final_url=url,
                redirect_chain=[],
                method=method,
            )
        requested_url = url
        current_url = url
        redirect_chain: list[str] = []
        started = self.clock()
        headers = {"User-Agent": DEFAULT_USER_AGENT, "Accept": ", ".join(self.fetch_policy["allowed_media_types"])}
        if SENSITIVE_HEADERS.intersection(name.lower() for name in headers):
            raise AssertionError("broker headers contain a prohibited credential field")

        while True:
            parts, addresses = self._parse_and_validate_url(
                current_url,
                requested_url=requested_url,
                redirect_chain=redirect_chain,
                method=method,
            )
            elapsed = self.clock() - started
            remaining = float(self.fetch_policy["total_timeout_seconds"]) - elapsed
            if remaining <= 0:
                receipt = self._receipt(
                    requested_url=requested_url,
                    final_url=current_url,
                    redirect_chain=redirect_chain,
                    method=method,
                    policy_decision="allowed",
                    retrieval_error="total retrieval timeout exceeded",
                )
                raise FetchFailed("total retrieval timeout exceeded", receipt)
            try:
                response = self.transport(
                    parts,
                    method,
                    headers,
                    addresses,
                    float(self.fetch_policy["connect_timeout_seconds"]),
                    remaining,
                    capture_limit,
                )
            except (OSError, TimeoutError, http.client.HTTPException, ssl.SSLError) as exc:
                receipt = self._receipt(
                    requested_url=requested_url,
                    final_url=current_url,
                    redirect_chain=redirect_chain,
                    method=method,
                    policy_decision="allowed",
                    retrieval_error=f"retrieval failed: {type(exc).__name__}",
                )
                raise FetchFailed("retrieval failed", receipt) from exc

            try:
                peer = ipaddress.ip_address(response.peer_ip)
                normalized_addresses = {str(ipaddress.ip_address(item)) for item in addresses}
            except ValueError as exc:
                raise self._block(
                    "transport reported an invalid connection address",
                    requested_url=requested_url,
                    final_url=current_url,
                    redirect_chain=redirect_chain,
                    method=method,
                    http_status=response.status,
                ) from exc
            if str(peer) not in normalized_addresses:
                raise self._block(
                    "connection destination did not match the validated DNS answers",
                    requested_url=requested_url,
                    final_url=current_url,
                    redirect_chain=redirect_chain,
                    method=method,
                    http_status=response.status,
                    connection_ip=str(peer),
                )

            if response.status in REDIRECT_STATUSES:
                location = response.headers.get("location")
                if not location:
                    raise self._block(
                        "redirect response omitted the Location header",
                        requested_url=requested_url,
                        final_url=current_url,
                        redirect_chain=redirect_chain,
                        method=method,
                        http_status=response.status,
                        connection_ip=str(peer),
                    )
                if len(redirect_chain) >= int(self.fetch_policy["maximum_redirects"]):
                    raise self._block(
                        "maximum redirect count exceeded",
                        requested_url=requested_url,
                        final_url=current_url,
                        redirect_chain=redirect_chain,
                        method=method,
                        http_status=response.status,
                        connection_ip=str(peer),
                    )
                current_url = urljoin(current_url, location)
                redirect_chain.append(current_url)
                continue

            media_type = response.headers.get("content-type", "").split(";", 1)[0].strip().lower()
            if media_type not in self.fetch_policy["allowed_media_types"]:
                raise self._block(
                    "response media type is not allowed",
                    requested_url=requested_url,
                    final_url=current_url,
                    redirect_chain=redirect_chain,
                    method=method,
                    http_status=response.status,
                    media_type=media_type or None,
                    body=response.body,
                    connection_ip=str(peer),
                )
            if len(response.body) > capture_limit:
                raise self._block(
                    "response exceeded the capture limit",
                    requested_url=requested_url,
                    final_url=current_url,
                    redirect_chain=redirect_chain,
                    method=method,
                    http_status=response.status,
                    media_type=media_type,
                    connection_ip=str(peer),
                )
            receipt = self._receipt(
                requested_url=requested_url,
                final_url=current_url,
                redirect_chain=redirect_chain,
                method=method,
                http_status=response.status,
                media_type=media_type,
                body=response.body,
                body_truncated=response.body_truncated,
                connection_ip=str(peer),
                policy_decision="allowed",
            )
            return FetchResult(response.body, receipt)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url")
    parser.add_argument("--method", choices=("GET", "HEAD"), default="GET")
    parser.add_argument("--capture-limit", type=int)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--profile-id", default=os.environ.get("OPENFS_SECURITY_PROFILE_ID"))
    parser.add_argument("--receipt-output", type=Path)
    parser.add_argument("--body-output", type=Path)
    args = parser.parse_args()
    if not args.profile_id:
        raise SystemExit("--profile-id or OPENFS_SECURITY_PROFILE_ID is required")
    broker = SafeWebFetchBroker.from_file(args.policy, security_profile_id=args.profile_id)
    try:
        result = broker.fetch(args.url, method=args.method, capture_limit=args.capture_limit)
        exit_code = 0
    except FetchBrokerError as exc:
        result = FetchResult(b"", exc.receipt)
        exit_code = 2
    receipt_text = json.dumps(result.receipt, ensure_ascii=False, indent=2) + "\n"
    if args.receipt_output:
        args.receipt_output.parent.mkdir(parents=True, exist_ok=True)
        args.receipt_output.write_text(receipt_text, encoding="utf-8")
    else:
        print(receipt_text, end="")
    if args.body_output and exit_code == 0:
        args.body_output.parent.mkdir(parents=True, exist_ok=True)
        args.body_output.write_bytes(result.body)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
