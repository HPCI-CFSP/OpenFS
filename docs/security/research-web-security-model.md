# Research Web Security Model

## Purpose

OpenFS needs broad discovery of public information while preventing a research
agent from turning untrusted content into unrestricted network or publication
authority. The design therefore separates discovery, retrieval, local execution,
dependency setup, and Git publication.

## Three control layers

| Layer | What OpenFS provides | What it does not prove |
|---|---|---|
| Behavioral | `AGENTS.md`, Skills, and human-owned Policies tell cooperative agents what is permitted. | Process isolation or blocked sockets |
| Repository validation | Schemas and deterministic checks reject invalid policies, unsafe capability declarations, and unsupported production claims. | That a deployed runner matches its declared profile |
| Platform enforcement | A managed search service, safe fetch broker, network-disabled research runtime, separate dependency job, and restricted publication identity enforce boundaries. | This layer exists only after deployment evidence is reviewed |

The current repository contains the first two layers. It deliberately registers
no production-eligible execution profile yet.

The legacy `tools/audit_roadmap_sources.py` performs direct HTTP checks and is
retained only for local development. Production readiness requires the weekly
workflow to replace it with the declared safe-fetch-broker adapter; the readiness
policy checks for that migration and blocks scheduled execution meanwhile.

## Capability architecture

```text
untrusted query
  -> managed Web search
  -> candidate URL
  -> anonymous safe-fetch broker
       - GET/HEAD only
       - DNS, redirect, and connection-destination validation
       - private/metadata destination block
       - no credential forwarding
       - size and timeout limits
  -> immutable retrieval receipt + bounded public content
  -> network-disabled research process
  -> proposal/assessment artifacts
  -> deterministic validation and Consensus
  -> separate least-privilege Git publication job
```

Dependency installation occurs before research execution in a separate,
explicitly configured job. The research process does not gain registry access or
general network access as a side effect of needing a package.

## Deployment requirements

A platform owner must provide and verify all of the following before unattended
production research is enabled:

1. a managed broad-search capability that does not expose provider credentials to
   the research process;
2. a fetch broker that enforces the policy at DNS resolution, redirect, and
   connection time;
3. an OS, container, namespace, or equivalent boundary blocking every Shell and
   subprocess socket path, including proxy bypasses;
4. separate dependency egress with pinned inputs and no overlap with untrusted
   content processing;
5. a Git identity limited to the OpenFS repository and non-default branches, with
   protected-branch review still required; and
6. logs and test evidence that demonstrate each required control without exposing
   secrets.

The owner records this evidence in `config/execution-security-profiles.json`.
Self-assertion by the research agent is not sufficient.

## Residual risks

- A public `GET` may trigger analytics or other server-side behavior, so agents
  must avoid sensitive query data and unnecessary requests.
- DNS rebinding, redirect chains, IPv4/IPv6 representation tricks, and cloud
  metadata endpoints require enforcement in the fetch implementation, not only
  preflight URL parsing.
- Browser automation has a larger state and interaction surface than fetch. It is
  excluded from unattended production unless an equally constrained read-only
  profile is verified.
- Correlated or poisoned sources remain a research-integrity risk even when
  network isolation succeeds. Source lineage and Consensus controls remain
  independently necessary.

## Verification

`tools/check_research_web_security.py` checks the declared policy and refuses a
production claim unless all controls and verification evidence are present. CI
runs the repository-level check. Platform-specific integration tests must be
added beside a future eligible profile and must cover private-address blocking,
redirect revalidation, credential isolation, Shell socket denial, and restricted
Git publication.
