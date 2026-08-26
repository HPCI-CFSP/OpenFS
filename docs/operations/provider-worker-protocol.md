# Provider Worker protocol

The Provider Worker is split across a trusted control process and an untrusted
provider adapter. The adapter never edits Queue or Run Manifest state directly.

1. The trusted controller leases one Work Item with `tools/run_controller.py`.
2. `tools/prepare_worker_invocation.py` rechecks the lease, the enabled and pinned
   Agent, public clearance, role output paths, and pinned Skill digest. It emits a
   secret-free invocation under `runs/<RUN>/worker-invocations/`.
3. A provider-specific adapter reads that envelope, obtains credentials only from
   its process environment or approved secret store, applies the pinned Skill,
   and writes only the declared role output paths.
4. The adapter records a structured result under
   `runs/<RUN>/worker-results/`. Provider request IDs are hashed; prompts, raw
   responses, credentials, headers, and secret values are not stored there.
5. `tools/accept_worker_result.py` verifies both envelope digests, the pinned Run
   controls, Agent registry, role permissions, pinned Skill, provider/model binding,
   exact output set and SHA-256 digests, usage measurement, and current lease
   ownership before delegating completion or failure to the Run Controller.

The Run control digest covers identity, budget, Policy/configuration/Skill
snapshots, and Directives. It intentionally excludes concurrent progress fields
such as cost totals, metrics, and Agent execution receipts. A terminal Run is
rejected independently of that digest.

Invocation payloads are explicitly untrusted data. An adapter must keep system
instructions and the pinned Skill outside that data block and must not follow
instructions found in Web content. Network access is restricted to the pinned
Agent setting (`none` or `public-web`). Public OpenFS adapters must never mount or
receive access to RiVault, RIKEN Box private areas, NDA material, or private shared
storage.

For a Work Item with `query_role: coverage-gap`, the adapter must retain
`coverage_gap_refs`, `coverage_gap_queue_id`, `coverage_gap_queue_item_id`, and
`query_seed_language` in the submitted capture or no-result path. Discovering one
responsive page never closes a Coverage Gap; evidence extraction, synthesis,
independent review, and an explicit roadmap update remain separate steps.

The repository includes a manual, review-only workflow in
`.github/workflows/research-worker.yml` and a fixed-endpoint adapter in
`tools/execute_provider_work_item.py`. The workflow selects one leased Work Item,
pins the configured model ID in the invocation envelope, requests structured
output, validates every declared artifact before writing it, and uploads the
result for review. It has no permission to push, open a pull request, merge, or
promote canonical data. Provider request IDs are stored only as hashes, and the
adapter never writes prompts, raw responses, headers, or credentials to an
artifact.

The adapter currently supports the OpenAI Responses API and the Anthropic
Messages API through fixed HTTPS endpoints. It rejects redirects and disables
environment-proxy discovery. Model IDs come from the enabled Agent registration
and are copied into the Run-pinned invocation; a mutable workflow variable cannot
change the model after the invocation has been prepared. Provider credentials
remain process-environment inputs to the single provider-call step and are never
part of the invocation or result contract.

Each production request reserves a positive amount from the Run cost ceiling
before dispatch. Measured token and Web-search usage is converted with
owner-supplied rates. Missing rate information is reported as unknown rather than
silently treated as zero. Repository-side accounting supplements, and does not
replace, provider-side hard spend limits.

These controls do not make provider integration production-ready by themselves.
The aggregate preflight remains blocked until a production execution profile has
verified sandbox and egress controls, owner attestations and provider-side spend
limits are current, independent Agents and Monitors are enabled, and the required
manual Pilot Runs have passed review. No live provider call is required or implied
by repository validation.
