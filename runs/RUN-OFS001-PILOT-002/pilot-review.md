# RUN-OFS001-PILOT-002 review

## Status

- Execution: completed, 37 of 37 Work Items completed.
- Declared-scope coverage: met for six Query families, including two
  falsification Queries.
- Sources: 12 unique Sources from 12 Origin Groups; Japanese and English;
  seven Source Classes; no failed Query or duplicate Source selection.
- Consensus: six Claim Decisions are `provisional`. Each has one correlated
  OpenAI GPT-5 Codex Assessment and zero independent Support Groups.
- Publication: prohibited. No Claim was promoted and no publication-approval
  Directive exists.

Meeting declared coverage means only that the versioned Monitor contract was
satisfied. It never means that the Web or the research field was searched
completely.

## Provisional research implications

1. Memory architecture should be represented as a multi-dimensional design
   space rather than a list of media names. Candidate dimensions include
   bandwidth, average and tail latency, capacity, cost, power, coherence,
   data-movement cost, device parallelism, interference, RAS, and placement
   policy.
2. CXL-attached memory cannot be modeled only as uniformly slower DRAM. The
   reviewed studies report device- and workload-dependent tail latency,
   parallelism limits, and interference with local DDR. The reported maximum
   DDR-bandwidth loss is experiment-specific and must not be generalized.
3. HBM4 and CXL describe different architecture dimensions. HBM4 vendor
   transfer rates do not answer capacity-tiering or fabric questions, while
   CXL link features do not establish local-memory application performance.
4. HBM evaluation needs package power delivery, thermal behavior, warpage,
   attainable application bandwidth, and configuration sensitivity in
   addition to peak transfer rate. The available application measurements in
   this Run are from an earlier HBM generation, not HBM4.
5. The Japanese high-bandwidth flash and MRAM integration results merit
   continuing coverage. Their public demonstrations target edge systems and
   do not yet establish HPCI suitability, production maturity, durability, or
   system-scale software behavior.
6. A roadmap should remain updateable as demand and maturity change. Weights,
   rankings, procurement choices, and adoption recommendations remain human
   Directive decisions.

## Harness feedback

- Query-level coverage, Source-class alternative groups, minimum unique
  Sources, minimum Origin Groups, languages, and falsification Queries are now
  evaluated separately.
- Runs pin full JSON snapshots of Policy, Agent Registry, Source Registry, and
  Monitor inputs. Later registry changes therefore cannot rewrite historical
  reviewer identity.
- Claim synthesis starts only after both Source slots for a Query have Evidence.
  It preserves Evidence IDs and Source Lineage IDs from both origins.
- Assessment identity is resolved from the pinned Agent Registry. Self-declared
  model names and independence groups are not trusted.
- Reviews from the proposal author's independence group remain in the audit
  trail but do not count as independent Support Groups.
- The first Validation attempt used an incorrect local fixture path. It was
  recorded as a retryable `input-path-error`; the retry completed successfully.

## Blocking gaps for the next Run

- Connect at least two genuinely independent Validator groups and one Critic
  group. Provider, model family, prompt profile, and independence group must be
  configured by the owner and pinned in the Run snapshot.
- Add blind-review dispatch so a Validator does not see other Assessments before
  submitting its first review.
- Calibrate Consensus thresholds and optional confidence values against a
  human-reviewed evaluation corpus. This Run intentionally records no numeric
  model confidence.
- Add Rights-Gate coverage for metadata-only and blocked Sources without
  scheduling impossible Evidence extraction.
- Record elapsed time, source-retrieval counts, model/token usage when available,
  and budget-stop reasons in the Run manifest.
- Add change detection so weekly Runs first compare Source fingerprints and
  avoid recreating unchanged Claims without a review reason.
