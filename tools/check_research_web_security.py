#!/usr/bin/env python3
"""Validate Research Web capability separation without claiming platform enforcement."""

from __future__ import annotations

import argparse
import ipaddress
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
REQUIRED_CAPABILITIES = {
    "web_search",
    "web_fetch",
    "browser_read",
    "shell",
    "dependency_install",
    "git_publish",
}
REQUIRED_IPV4_BLOCKS = {
    "10.0.0.0/8",
    "127.0.0.0/8",
    "169.254.0.0/16",
    "172.16.0.0/12",
    "192.168.0.0/16",
}
REQUIRED_IPV6_BLOCKS = {"::1/128", "fc00::/7", "fe80::/10"}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(
    policy: dict[str, Any],
    profiles: dict[str, Any],
    *,
    require_production: bool = False,
    required_profile_id: str | None = None,
) -> dict[str, Any]:
    errors: list[str] = []
    if policy.get("default_decision") != "deny" or policy.get("fail_closed") is not True:
        errors.append("Research Web policy must default-deny and fail closed")

    capabilities = policy.get("capabilities", {})
    if set(capabilities) != REQUIRED_CAPABILITIES:
        errors.append(
            "capability set mismatch: "
            f"missing={sorted(REQUIRED_CAPABILITIES - set(capabilities))}, "
            f"extra={sorted(set(capabilities) - REQUIRED_CAPABILITIES)}"
        )
    search = capabilities.get("web_search", {})
    if search.get("unknown_public_domains_allowed") is not True:
        errors.append("web_search must support discovery beyond a fixed domain allowlist")
    if search.get("managed_tool_required") is not True or search.get("shell_fallback_allowed") is not False:
        errors.append("web_search must require a managed tool and forbid shell fallback")

    fetch = capabilities.get("web_fetch", {})
    if fetch.get("allowed_methods") != ["GET", "HEAD"]:
        errors.append("web_fetch methods must be exactly GET and HEAD")
    if set(fetch.get("allowed_schemes", [])) != {"https", "http"}:
        errors.append("web_fetch schemes must be HTTP and HTTPS only")
    for field in (
        "anonymous_public_access_only",
        "validate_dns_answers",
        "validate_each_redirect",
        "validate_connection_destination",
    ):
        if fetch.get(field) is not True:
            errors.append(f"web_fetch.{field} must be true")
    for field in (
        "forward_cookies",
        "forward_authorization",
        "forward_environment_credentials",
    ):
        if fetch.get(field) is not False:
            errors.append(f"web_fetch.{field} must be false")
    if not 0 < fetch.get("maximum_redirects", 0) <= 10:
        errors.append("web_fetch maximum_redirects must be between 1 and 10")
    if not 0 < fetch.get("maximum_response_bytes", 0) <= 50 * 1024 * 1024:
        errors.append("web_fetch maximum_response_bytes must be positive and at most 50 MiB")

    browser = capabilities.get("browser_read", {})
    for field in (
        "persistent_profile_allowed",
        "state_changing_actions_allowed",
        "file_upload_allowed",
        "credential_submission_allowed",
    ):
        if browser.get(field) is not False:
            errors.append(f"browser_read.{field} must be false")

    shell = capabilities.get("shell", {})
    for field in ("general_internet_access", "arbitrary_socket_egress", "proxy_bypass_allowed"):
        if shell.get(field) is not False:
            errors.append(f"shell.{field} must be false")
    if shell.get("hard_network_isolation_required") is not True:
        errors.append("shell hard network isolation must be required")
    if capabilities.get("dependency_install", {}).get("separate_capability") is not True:
        errors.append("dependency installation must use a separate capability")
    publish = capabilities.get("git_publish", {})
    if publish.get("separate_capability") is not True:
        errors.append("Git publication must use a separate capability")
    if publish.get("protected_default_branch_write") is not False:
        errors.append("Git publication must not write directly to the protected default branch")
    if publish.get("least_privilege_token_required") is not True:
        errors.append("Git publication must require a least-privilege token")

    boundaries = policy.get("network_boundaries", {})
    for cidr in boundaries.get("blocked_ipv4_cidrs", []):
        try:
            ipaddress.ip_network(cidr)
        except ValueError:
            errors.append(f"invalid blocked IPv4 network: {cidr}")
    for cidr in boundaries.get("blocked_ipv6_cidrs", []):
        try:
            ipaddress.ip_network(cidr)
        except ValueError:
            errors.append(f"invalid blocked IPv6 network: {cidr}")
    missing_v4 = REQUIRED_IPV4_BLOCKS - set(boundaries.get("blocked_ipv4_cidrs", []))
    missing_v6 = REQUIRED_IPV6_BLOCKS - set(boundaries.get("blocked_ipv6_cidrs", []))
    if missing_v4 or missing_v6:
        errors.append(
            f"network block coverage is incomplete: IPv4={sorted(missing_v4)}, IPv6={sorted(missing_v6)}"
        )

    if profiles.get("policy_id") != policy.get("policy_id"):
        errors.append("execution profiles reference a different Research Web policy")
    required_controls = set(profiles.get("required_verified_controls_for_production", []))
    profile_ids: set[str] = set()
    production_profiles: list[str] = []
    for profile in profiles.get("profiles", []):
        profile_id = profile.get("profile_id", "<missing>")
        if profile_id in profile_ids:
            errors.append(f"duplicate execution security profile: {profile_id}")
        profile_ids.add(profile_id)
        controls = profile.get("controls", {})
        if set(controls) != required_controls:
            errors.append(f"{profile_id}: control set does not match production requirements")
        verified = {name for name, status in controls.items() if status == "verified"}
        eligible = profile.get("production_eligible") is True
        if eligible and verified != required_controls:
            errors.append(f"{profile_id}: production eligibility claimed without verified controls")
        if eligible and not profile.get("verification_evidence"):
            errors.append(f"{profile_id}: production eligibility lacks verification evidence")
        if eligible:
            production_profiles.append(profile_id)
    if require_production and not production_profiles:
        errors.append("no execution security profile is eligible for production research")
    if required_profile_id and required_profile_id not in profile_ids:
        errors.append(f"requested execution security profile is not registered: {required_profile_id}")
    elif required_profile_id and required_profile_id not in production_profiles:
        errors.append(
            f"requested execution security profile is not production eligible: {required_profile_id}"
        )

    return {
        "policy_id": policy.get("policy_id"),
        "profile_count": len(profiles.get("profiles", [])),
        "production_profiles": production_profiles,
        "required_profile_id": required_profile_id,
        "errors": errors,
        "valid": not errors,
        "hard_enforcement_note": (
            "A valid repository policy does not prove network enforcement. "
            "Only a profile with every required control independently verified is production eligible."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--require-production-profile", action="store_true")
    parser.add_argument("--profile-id")
    args = parser.parse_args()
    result = evaluate(
        load_json(ROOT / "config/research-web-security-policy.json"),
        load_json(ROOT / "config/execution-security-profiles.json"),
        require_production=args.require_production_profile,
        required_profile_id=args.profile_id,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
