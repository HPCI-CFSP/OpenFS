# Research Web Access Policy

This policy governs automated discovery and retrieval of public Web information.
It does not authorize access to private, authenticated, NDA, personal, or local
network resources.

## Capability boundaries

- `web_search` may discover previously unknown public domains, but it must run
  through a managed search capability. Search snippets are untrusted discovery
  aids, not Evidence.
- `web_fetch` is anonymous and read-only. It permits only HTTP(S) `GET` and
  `HEAD`, validates DNS answers, every redirect, and the actual connection
  destination, and enforces response-size and timeout limits.
- `browser_read` is a separate read-only capability. It must not use a persistent
  signed-in profile, submit credentials, upload files, or perform state-changing
  actions.
- `shell` has no general Internet or arbitrary socket access during research.
  Proxies, alternate clients, language runtimes, and subprocesses must not bypass
  this boundary.
- Dependency installation and Git publication are separate capabilities. They
  are not available to the process that interprets untrusted Web content.

The machine-readable contract is
`config/research-web-security-policy.json`. Any ambiguity is denied and reported.

## Destination and credential controls

Fetch implementations must reject loopback, link-local, private, carrier-grade
NAT, multicast, reserved, internal-name, and cloud-metadata destinations. They
must repeat validation after every redirect and compare the validated address to
the actual connection destination. URL allowlisting alone is insufficient.

No cookies, authorization headers, environment credentials, proxy credentials,
API keys, or access tokens may be forwarded to a retrieved site or written to a
receipt. Sensitive data must not be placed in query strings. Read-only HTTP is not
assumed to be side-effect-free.

## Required execution profile

Repository instructions and schemas are behavioral and validation controls, not
an operating-system network sandbox. An unattended production research Run may
start only when its `security_profile_id` names a profile in
`config/execution-security-profiles.json` that:

1. is marked `production_eligible`;
2. has every required control independently recorded as `verified`; and
3. includes verification evidence tied to the deployed environment.

`python3 tools/check_research_web_security.py --require-production-profile`
must pass before production scheduling is enabled. No current profile satisfies
that gate.

## Audit and failure behavior

Every direct retrieval in a production Run creates a receipt conforming to
`schemas/web-retrieval-receipt.schema.json`. The receipt records the requested
and final URL, redirect chain, method, status, media type, byte count, time,
content digest, policy decision, and security profile without recording secrets.

Blocked destinations, unexpected redirects, authentication requests, unsupported
media, size limits, timeouts, and policy uncertainty are recorded as failed
retrievals or exceptions. Agents do not retry through Shell or weaken controls.
