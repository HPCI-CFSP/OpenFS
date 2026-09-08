# GPU-Centric AI for Science Configuration Candidate v0.2

## Status and boundary

This document defines the Candidate v0.2 implementation. It does not add a fourth
accepted scenario or alter the accepted three-option portfolio. A human-approved
manifest permits the visibly provisional planner to be published on GitHub Pages
after an authorized merge. The results are produced by one model and one agent,
have not passed the Consensus Gate, and are prohibited for procurement use.

本書はCandidate v0.2の設計・実装文書です。第4の採択済みシナリオは追加せず、既存3案も
変更しません。人が承認したマニフェストにより、権限を持つ人がPRをマージした後に限り、
暫定表示を維持した算定画面をGitHub Pagesへ公開できます。結果は単一のAIモデル・単一の
AIエージェントによる暫定情報で、Consensus Gateは未完了かつ調達利用禁止です。

## Three-layer model / 3層モデル

| Layer | Stable ID namespace | Responsibility |
|---|---|---|
| System planning policy / システム整備方針 | `POL-SYS-*` | Objectives, evaluation axes, deployment strategy, and risk posture. It preserves links to the existing three `SCN-HPCI-*` records without treating their architecture as fixed. |
| Reference architecture / 参照アーキテクチャ | `ARCH-*` | Reusable component roles, connections, procurement-unit types, constraints, redundancy bases, and vendor software profiles. `ARCH-GPU-CENTRIC-AI4S-001` is vendor-neutral at this layer. |
| Configuration estimate / 構成算定結果 | `CFGRESULT-*`; saved plans later use `SCN-HPCI-*` | A reproducible result for one policy, architecture, input request, product-catalog snapshot, availability assessment, and optional traceable cost input. |

`SCN-HPCI-*` is reserved for a concrete plan intentionally saved after combining
the three layers. An interactive calculation does not receive an `SCN-HPCI-*` ID.

## Impact inventory / 既存3案固定の影響範囲

The current accepted portfolio remains the public source of truth. The following
areas assume the three accepted scenario IDs and must be migrated only in a later,
separately approved publication change.

| Area | Files or components | Current dependency | Candidate treatment |
|---|---|---|---|
| Accepted contracts | `schemas/published-scenario-set.schema.json`, `schemas/system-scenario.schema.json`, `roadmaps/scenarios/accepted/hpci-p0-scenarios.json` | Accepted set contains exactly the reviewed three options. | Unchanged. New layers live under `proposals/`. |
| Budget and evidence | `config/budget-planning.json`, `knowledge/public/fs3-decision-evidence.json`, `knowledge/public/planning-evidence-readiness.json`, `knowledge/public/application-performance-forecasts.json` | Labels, selectors, and evidence summaries bind to accepted scenario IDs. | Unchanged; Candidate results are not inserted into accepted evidence. |
| Validators and generators | `tools/check_scenario_portfolio.py`, `tools/check_public_planning_surfaces.py`, `tools/build_consensus_review_package.py`, `tools/build_fs3_decision_evidence.py`, `tools/add_budget_architecture_options.py`, `tools/estimate_system_cost.py` | Enforce or render the existing scenario portfolio. | The new estimator is parallel and does not bypass these gates. |
| Pages | `site/planning.js`, `site/app.js`, `site/index.html`, `site/scenarios-index.html`, `site/roadmaps.js` | Render accepted public planning objects. | Production routes and navigation remain unchanged. |
| Tests | `tests/test_scenario_portfolio.py`, `tests/test_roadmap_assurance.py`, `tests/test_pages_site.py`, `tests/test_budget_ui.js`, `tests/test_fs3_decision_evidence.py`, `tests/test_public_planning_surfaces.py`, `tests/test_consensus_review_package.py` | Assert accepted IDs, counts, and publication provenance. | Existing assertions remain intact. Candidate tests are additive. |
| Immutable history | Old `reviews/directives/` and `reviews/consensus-packages/CRP-P0-ROADMAPS-*` | Record historical approvals and review snapshots. | Never rewritten. |

## Input and output contracts / 入出力仕様

The contracts intentionally separate facts with different update and review
cadences:

- `gpu-product-catalog.schema.json` stores technical identity, form factor,
  procurement units, dated product events, evidence check date, and Sources.
- `procurement-availability-assessment.schema.json` stores jurisdiction- and
  acceptance-date-specific sales, support, minimum-order, and delivery findings.
- `component-cost-input.schema.json` stores non-overlapping cost lines with
  optimistic, baseline, and conservative prices. Candidate production data must
  be itemized observations, vendor quotes, or validated estimates.
- `planning-request.schema.json` stores CAPEX, a separate TCO horizon, deployment
  mode, facility constraints, workload ratios and absolute demand, storage and
  inference requirements, and explicit objectives.
- `configuration-estimate.schema.json` stores integer configurations, the budget
  identity, constraint outcomes, a separate TCO, performance-model status,
  Coverage Gaps, and a Pareto result when comparison is supportable.

欠損値は0へ変換しません。価格、調達可能性、絶対需要、設備条件または性能根拠が
不足する場合、結果は`blocked`となり、「算定不能」「要ベンダー見積」と不足項目を
返します。

## NVIDIA and AMD BOM structure / BOM構造

Both vendor branches use the same accounting boundary but retain independent
product packages and prices. A package contains an integer `node`, `tray`, or
`rack` procurement unit and the following non-overlapping scopes:

1. GPU, host CPU, HBM, local NVMe, and the vendor-supported scale-up domain.
2. Scale-out NICs, switches, optics, cables, topology, and spare ports.
3. Fast shared storage, capacity storage, backup, and archive.
4. Login, management, monitoring, provisioning, scheduler, and authentication services.
5. Power, cooling, racks, facility work, installation, migration, and acceptance.
6. Software, maintenance, support, spares, staffing, hosting, energy, and decommissioning.

NVIDIA profiles retain CUDA and NCCL requirements; AMD profiles retain ROCm and
RCCL requirements. A price or capability from one branch is never silently used
for the other branch.

## Cost and TCO boundary / 費用範囲と責任分界

For each price case, the estimator finds the largest integer procurement-unit
count satisfying budget, confirmed IT power, confirmed cooling capacity, rack
count, storage requirements, redundancy, and delivery constraints.

```text
configuration cost + contingency + unused budget = CAPEX ceiling
```

Initial equipment and implementation costs form CAPEX. Electricity, recurring
maintenance, support, hosting, staffing, refresh, and decommissioning belong to
the multi-year TCO. A contract total divided by GPU count is not an admissible GPU
unit price. Shared facility contracts are not allocated until scope and overlap
are resolved. TCO is incomplete unless every required recurring scope has
traceable evidence.

## Performance and procurement eligibility / 性能予測と調達利用可否

The performance contract separates compute, memory, communication, and I/O time,
then records overlappable, non-overlappable, and synchronization time. Inference
uses a separate queueing record for concurrency, request rate, TTFT, TPOT, and a
quality target. Candidate benchmarks are HPL, HPL-MxP, HPCG, Graph500, OSU
Micro-Benchmarks, GROMACS, OpenFOAM, current pinned MLPerf Training and Inference
Datacenter suites, and MLPerf Storage.

A result may be considered for procurement scoring only after all of the
following are independently reviewed and accepted: reproducible measurements,
fixed benchmark and software versions, model error bounds, application coverage,
scaling efficiency, facility constraints, procurement availability, and price
scope. The current Candidate therefore sets `procurement_use` to `prohibited`.

## Candidate Pages view / Candidate画面

The default Pages build publishes the human-approved Candidate route at
`candidate/gpu-centric-ai4s/` and links to it from the system-planning pages.
`knowledge/public/gpu-planner-publication.json` pins five approved public
inputs by SHA-256; a source change therefore fails the build until it receives a
new review and publication record. The fifth input is an empty What-if template;
it contains no estimate. The view separates public-evidence mode from browser-local
What-if mode, compares independent NVIDIA and AMD BOMs, re-optimizes each of three
price cases, and exports the explicit inputs and results as JSON or CSV. It displays
blocked inputs, quantitative constraint shortfalls, and Coverage Gaps instead of
fabricated values.

The Candidate page deliberately contains no GA4 loader. Form values and computed
budgets, estimates, and configurations remain in the browser and are not sent to
GA4 or another external service.

## Evidence currently available / 現時点の公開根拠

- RIKEN's public RIKYU description and July 24, 2026 announcement establish that
  operation began on July 7, 2026, with an operational reference comprising 400
  water-cooled GB200 NVL4 compute nodes, four B200 GPUs and two Grace CPUs per
  node, XDR fabric, and all-NVMe Lustre storage.
- RIKEN public contract records establish a package total and separate network
  and facility contracts, but do not provide a non-overlapping component BOM,
  reusable GPU unit price, complete maintenance scope, or five-year TCO.
- Vendor primary sources establish NVIDIA Rubin and AMD MI400-family product
  milestones and selected product specifications. They do not establish Japanese
  public-procurement eligibility, project prices, support terms, or delivery lead
  times for a 2027 acceptance.

The default 100-oku-JPY, 2027, 4-MW public-evidence case is therefore correctly blocked
for both NVIDIA and AMD. They identify what must be obtained rather than producing
a false quantity.

## Staged implementation and acceptance / 段階実装と受入条件

1. **Candidate contracts and dual-mode planner:** validate the three-layer model,
   public-evidence/What-if separation, product/procurement separation, missing-value
   propagation, integer sizing, browser privacy, and production isolation. Candidate
   v0.2 implements this stage.
2. **Evidence-complete public Candidate BOMs:** obtain itemized and non-overlapping price
   intervals, delivery and support evidence, facility limits, and absolute demand;
   then run 10/30/100/300-oku-JPY and 2026–2032 matrices.
3. **Validated performance models:** pin benchmark versions and software, add
   reproducible measurements, scaling/error bounds, and inference queue tests.
4. **Independent review and promotion:** run falsification and Consensus Gates,
   obtain a separate human decision, and only then promote the Candidate status
   or save an `SCN-HPCI-*` plan. The current human Directive authorizes only the
   visibly provisional Pages publication.

Automated acceptance checks cover schema validation, blocked output for absent
evidence, the deterministic 100-oku-JPY/7-rack/504-GPU case, the 300-oku-JPY and
2-MW caps, price-case re-optimization, integer procurement units, budget identity,
monotonic GPU counts for an unchanged generation and constraint set, facility,
network, storage, demand and delivery constraints, separate CAPEX and TCO,
phase-overlap and inference-queue models, browser/Python parity, absence of
analytics and browser persistence on the Candidate route, digest-pinned inputs,
and unchanged accepted scenario counts.
