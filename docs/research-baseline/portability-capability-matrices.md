# Portability Capability Matrices

`GAP-PORT-001` asks whether OpenMP and SYCL features needed by HPCI applications
are usable across GCC, LLVM, Fujitsu, Intel, NVIDIA, and AMD toolchains. A vendor
version page is evidence about one implementation, not a comparable implementation
rate.

Candidates use `schemas/portability-capability-matrix.schema.json` and are stored
under `proposals/portability-capability-matrices/`. Every matrix must:

- define one common set of OpenMP or SYCL features before collecting results;
- cover all six required toolchain vendors exactly once;
- distinguish vendor documentation from compile, conformance, and application tests;
- pin tested results to a reproducible artifact and a commit-pinned environment;
- use at least two test environments from two origin groups; and
- preserve unsupported and partial results instead of dropping them.

Run:

```bash
python3 tools/check_portability_capability_matrix.py proposals/portability-capability-matrices/<matrix>.json
```

A passing matrix is only eligible for independent Consensus review. It does not
prove full standards conformance, close the Coverage Gap, or rank a compiler or
hardware backend for procurement.
