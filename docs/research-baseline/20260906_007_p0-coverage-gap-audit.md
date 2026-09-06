# P0 Coverage Gap execution audit

## Status

- Date: 2026-09-06 JST
- Scope: all 19 public roadmaps
- Research status: provisional
- Consensus status: incomplete

## Recount

The current roadmaps contain exactly 21 open P0 Coverage Gaps across seven roadmaps:

| Roadmap | Open P0 Gaps |
|---|---:|
| Compute nodes, processors, and accelerators | 3 |
| Interconnects, optics, and disaggregation | 2 |
| Memory hierarchy and data movement | 1 |
| Performance portability, compilers, and tuning | 4 |
| Reference architectures and center deployment | 6 |
| Storage and data platforms | 1 |
| Scientific workloads, benchmarks, and performance models | 4 |

The number 21 is therefore current rather than a stale carry-over. All 20 source-discovery
items have explicit bilingual query plans and closure criteria. The remaining item is assigned
to an independent Consensus review rather than to Web discovery.

## What closure requires

Closure methods overlap because one Gap can require more than one method.

| Closure method | P0 Gaps requiring it |
|---|---:|
| Evidence review | 12 |
| Reproducible measurement | 13 |
| Conformance test | 4 |
| Confirmation by the responsible authority | 6 |
| Independent Consensus quorum | 1 |

No P0 Gap can be closed by adding a Web citation alone. Public research can improve the
evidence base, but the item stays open until every declared criterion, two independent Origin
Groups, and the Consensus Gate are satisfied.

## Current-source spot check

`GAP-NET-003` remains correctly open. The CXL Consortium published CXL 4.0 on 2025-11-18,
but the current official implementation evidence registered by OpenFS still concerns CXL 3.x.
Montage Technology reported trial production of a CXL 3.2 memory-expander controller on
2026-07-31. These facts support the existing boundary: a published CXL 4.0 specification does
not establish CXL 4.0 switches, memory devices, management software, interoperability, or
HPCI-scale availability.

Primary sources:

- https://computeexpresslink.org/wp-content/uploads/2025/11/CXL_4.0-Specification-Release_FINAL_Website-Copy.pdf
- https://www.montage-tech.com/Press_Releases/20260731

## Harness outcome

The deterministic Gap-queue builder now derives the five closure-method counts from the
declared P0 criteria. The public evidence-assurance page displays them next to assignment and
monitor readiness, making it visible which work requires measurement, responsible-authority
input, or independent review rather than further Web searching.
