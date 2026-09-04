# Planning evidence consolidation, round 1

## Status

- As of: 2026-09-04
- Research status: provisional
- Consensus: incomplete; one model and one agent
- Publication decision: `PUBDEC-PLANNING-EVIDENCE-20260904-001`
- Human directive: `DIR-900100`
- Intended review path: one pull request directly against `main`

This round consolidates pending planning evidence onto a branch based directly on `main`. It does not constitute a procurement recommendation, a complete five-year cost model, or a validated future-performance forecast.

## HPCI system evidence

The Institute of Statistical Mathematics FY2024 annual report states that its two-system HPE Superdome Flex data-assimilation supercomputer was introduced in March 2023 and that one system is provided through HPCI. The introduction event is now linked to the lifecycle timeline. The exact HPCI availability date remains unresolved and is not inferred.

The AIST ABCI operating-information page reports a system-wide outage from 10:19 to 20:30 on March 4, 2025. OpenFS records 611 minutes of unplanned downtime. The subsequent degraded operation of ABCI 3.0 at 219 of 766 nodes until 14:42 on March 5 is preserved in the evidence note but is not added to downtime.

Coverage changes:

| Measure | Before | After |
| --- | ---: | ---: |
| Systems with introduction, operation, or trial-operation evidence | 24 / 27 | 25 / 27 |
| Systems with any lifecycle evidence | 26 / 27 | 27 / 27 |
| Systems with any public operational evidence | 11 / 27 | 12 / 27 |
| Systems with availability or downtime evidence | 4 / 27 | 5 / 27 |
| Systems with future retirement, refresh, or expansion timing | 9 / 27 | 9 / 27 |

Primary sources:

- [Institute of Statistical Mathematics FY2024 annual report](https://www.ism.ac.jp/editsec/Nenpou/R6nenpou.pdf)
- [ABCI operating information](https://abci.ai/ja/about_abci/info.html)

## Procurement and cost evidence

The register now separates four Fugaku annual observations:

| Contract | Public amount | Established period | OpenFS treatment |
| --- | ---: | --- | --- |
| FY2024 maintenance | JPY 6,261,801,700 | Not established by the registered disclosure | Annual observation only |
| FY2025 maintenance and operations support | JPY 6,259,572,132 | 2025-04-01 to 2026-03-31 | Annual observation only |
| FY2025 system overhaul and network-switch replacement | JPY 1,586,200,000 | 2025-04-01 to 2026-03-31 | Refresh observation; no item-price derivation |
| FY2026 maintenance and operations support | JPY 5,958,583,928 | 2026-04-01 to 2027-03-31 | Annual observation only |

The amounts are not summed into a five-year series. Tax treatment, itemization, contract overlap, future refresh conditions, electricity, cooling, shared facilities, and staffing remain unresolved. The register therefore contains 11 cases, only one of which supports 60-month contractual arithmetic; complete five-year TCO remains 0 of 11.

Primary sources:

- [FY2024 Fugaku maintenance contract notice](https://www.jetro.go.jp/gov_procurement/national/articles/310658/2024042200670107.html)
- [FY2025 Fugaku maintenance contract notice](https://www.jetro.go.jp/gov_procurement/national/articles/357318/2025060200860081.html)
- [RIKEN single-source contract results through March 2026](https://choutatsu.riken.jp/r-world/info/procurement/docs/infofile/file/ic000004218.PDF/id/000000169)

## EEA1 reproducibility evidence

OpenFS now records immutable code-version candidates for GENESIS, SALMON2, SCALE-LETKF, and LQCD-DWF-HMC. GENESIS also has a pinned public benchmark-input candidate. These records are candidates for building reproducible Fugaku baselines, not completed EEA1 packages.

| Application | Code candidate | Input candidate | Blocking condition |
| --- | --- | --- | --- |
| GENESIS | v2.1.6.1, `025e9eb` | v1.0.0, `498091f` | EEA1 match and input redistribution terms unverified |
| SALMON | v.2.3.0, `30ba646` | None | EEA1 input and build conditions absent |
| SCALE-LETKF | 5.5.5-v2, `9d25a29` | None | Initial conditions, ensemble, and SCALE-RM version absent |
| E-Wave | None | None | EEA1 code and input package unreleased |
| FrontFlow/blue | None | None | EEA1 code and standard mesh package unreleased |
| LQCD-DWF-HMC | main snapshot, `c5b1b6c` | None | Release tag, EEA1 lattice, and convergence conditions absent |

Benchpark commit `30d698d` is recorded as a harness candidate. Because no package has a verified EEA1 input match, `BMSTAGE-BASELINE-PACKAGE` remains blocked with zero completed applications. Matched-input measurements, independent validation, and validated future-performance forecasts also remain zero.

## Publication verification

Production Pages publication is assessed separately from a local preview. At the time this note was written, the Pages workflow for the current `main` commit from PR #44 was still running its unit-test step; production deployment was therefore not claimed. This consolidation has a successful local Pages build and must pass the pull-request checks before merge.

## Remaining P0 gaps

- Verify formal starts for the two Furo-II resources and the HPCI availability date for the ISM system.
- Align operational periods, denominators, maintenance exclusions, and power boundaries across providers.
- Obtain public contract scope and itemization without inferring component prices or double counting.
- Build redistributable, input-matched EEA1 packages and obtain application-owner approval.
- Measure identical inputs on candidate configurations, reserve separate validation data, and complete independent Consensus review.
