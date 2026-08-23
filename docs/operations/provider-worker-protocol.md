# Provider Worker protocol

The provider Worker is split across a trusted control process and an untrusted
provider adapter. The adapter never edits Queue or Run Manifest state directly.

1. The trusted controller leases one Work Item with `tools/run_controller.py`.
2. `tools/prepare_worker_invocation.py` rechecks the lease, enabled pinned Agent,
   public clearance, role output paths, and pinned Skill digest. It emits a
   secret-free invocation under `runs/<RUN>/worker-invocations/`.
3. A provider-specific adapter reads that envelope, obtains credentials only from
   its process environment or approved secret store, applies the pinned Skill,
   and writes only the declared role output paths.
4. The adapter records a structured result under
   `runs/<RUN>/worker-results/`. Provider request IDs are hashed; prompts, raw
   responses, credentials, headers, and secret values are not stored there.
5. `tools/accept_worker_result.py` verifies both envelope digests, the pinned Run
   Manifest, Agent registry, role permissions and Skill, provider/model binding,
   exact output set and SHA-256 digests, usage measurement, and current lease
   ownership before delegating completion or failure to the Run Controller.

Invocation payloads are explicitly untrusted data. An adapter must keep system
instructions and the pinned Skill outside that data block and must not follow
instructions found in Web content. Network access is restricted to the pinned
Agent setting (`none` or `public-web`). Public OpenFS adapters must never mount or
receive access to RiVault, RIKEN Box private areas, NDA material, or private shared
storage.

The contract does not make a provider integration production-ready by itself.
The repository still requires a reviewed `research-worker.yml`, provider-specific
adapter implementation, sandbox and egress tests, hard provider spend limits,
enabled independent Agent bindings, and successful manual Runs. The aggregate
production preflight continues to block until those components are present.
