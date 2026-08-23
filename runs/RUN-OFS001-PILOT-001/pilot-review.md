# RUN-OFS001-PILOT-001 review

## Status

- Execution: completed, 8 of 8 Work Items completed.
- Research status: coverage-incomplete.
- Formal Consensus: not attempted. Discovery and extraction used one correlated
  OpenAI Codex path and cannot supply independent validation votes.
- Publication status: not publishable as an accepted Finding or recommendation.

## Provisional observations

1. `SRC-961CB55A90CD`: the CXL Consortium reported that CXL 4.0 raises
   link speed to 128 GT/s and adds bundled ports and memory RAS enhancements.
2. `SRC-95713A2AC318`: a PNNL-authored MEMSYS paper reports that CXL
   topology choices can produce workload-dependent performance differences and
   that switch overhead and routing complexity matter for HPC and LLM inference.
3. `SRC-40DE69D7FA8D`: SK hynix reported HBM4 readiness with 2,048 I/O
   terminals, greater than 10 Gbit/s pin speed, and improved power efficiency.
   These remain vendor-reported product claims until independently assessed.
4. `SRC-CD3528F6164E`: a 2025 preprint proposes an FPGA CXL emulation
   platform with configurable latency and bandwidth regions and argues that
   simulation-only evaluation has fidelity and scale limitations. Peer-review
   status was not established by this Run.

## Working implications for OFS-001

- HBM and CXL-attached capacity tiers address different parts of the design
  space. A roadmap should not compare them only as interchangeable memory labels.
- Architecture exploration should parameterize bandwidth, latency, capacity,
  topology, page-migration cost, profiling resolution, power, and RAS behavior.
- gem5 remains useful for broad design-space exploration, but selected points
  should be cross-checked with real CXL devices or FPGA-based emulation before a
  high-impact recommendation.
- Workload classification should connect measurable application behavior to
  these continuous parameters rather than rely only on discrete motifs.

## Coverage gaps that block promotion

- no Japanese-language Source was registered;
- no `independent-analysis` Source was registered;
- the Monitor requests `official-primary`, while the standards-body and vendor
  primary classes used by this Run are more specific and do not satisfy that
  literal class requirement;
- one research source is a preprint;
- no independent model/provider validation or falsification assessment exists;
- no contradictory or negative-result search was run;
- performance claims use different workloads, baselines, and system conditions
  and must not be combined into a common score.

## Harness feedback

- The CXL 4.0 specification download path presents clickthrough terms that
  restrict AI processing of specification content. The specification body was
  therefore excluded; only a public press release was used for Evidence.
- Run execution completion and research sufficiency are separate states. The
  manifest now records `status: completed` and
  `research_status: coverage-incomplete` independently.
- Future Runs must pin the Agent Registry, Source Registry, and Acquisition
  Policy hashes in addition to the original Policy set.
