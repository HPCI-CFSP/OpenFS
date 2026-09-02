# Procurement Cost Evidence and Budget Planning

## Contract register / 調達実績台帳

`knowledge/public/procurement-cost-register.json` is the single public register.
Link the announcement, draft/final specification, corrections, award, contract,
deployed configuration, and related construction or support contracts by case ID.
Requirements in a tender are not proof of the installed bill of materials.
Preserve the prior version in Git and explain corrections in a reviewable PR.

同じ台帳で公告、仕様書、訂正、落札・契約結果、実導入構成、関連工事を対応付けます。
要求仕様と実導入構成を区別し、推定内訳を実際の契約内訳として記載しません。
原資料の全文は保存せず、URL、参照箇所、確認日、取得状況を保存します。

## Public access / 公開範囲

Use managed anonymous research only. Record inaccessible specifications as
`not-obtained`, `expired`, `registration-required`, or `confidentiality-required`.
Do not submit identity forms, accept confidentiality terms, retrieve credentials,
or bypass access controls. A public announcement does not make its specifications
public. Restricted content must never enter this register, including summaries.

交付条件付きの仕様書は取得・公開を代行せず、公開可能性が確認できた資料だけを利用します。
秘密保持対象は要約も含めて取り込まず、公開公告に記された交付条件のみ記録します。

## Price decomposition / 内訳の推定

1. Separate program budgets, planned prices, awards, and contract totals.
2. Keep original currency, tax treatment, date, purchase/lease terms, monthly/total
   basis, covered period, and included maintenance. Never assume an academic discount.
3. Use observed itemization first; preserve an unallocated residual. Never subtract
   a related contract from another total without an evidenced inclusion relation.
4. Estimate component intervals only from comparable scope, generation, quantities,
   terms, and dates. A package divided by its GPU count is NOT a GPU purchase price.
5. Calibrate and independently test on different procurement cases; publish errors,
   excluded cases, provenance, assumptions, and unresolved gaps. Do not invent a
   confidence interval or call an arithmetic subtotal a validated estimate.
6. Require independent Consensus and the applicable human decision before using
   model results for procurement scoring or declaring a system feasible.

公表内訳、推定内訳、内訳不明を分けます。計算機一式の総額をGPU数で割った値を
GPU単価として扱いません。異なる調達案件で校正と検証を分離し、費用モデルの誤差を
確認するまで、ノード数や調達可能性を確定しません。

## Five budget levels / 五つの予算水準

`config/budget-planning.json` owns numeric budget ceilings and three independent
planning profiles. Current levels and shares are provisional comparison assumptions,
not a fit to the distribution of procurement prices and not evaluation weights.
All views use constant 2026 JPY excluding tax. Future deployment years do not imply
price deflation, a product generation, availability, or facility feasibility.

The initial envelope includes equipment, integration, required facility work, and
contingency. Five-year TCO additionally needs maintenance, licenses, energy, and
staffing without counting bundled support twice. Unknown values stay null, never 0.
The present public register has no matched component-price calibration or holdout
validation. Therefore Pages shows allocation envelopes and topology, not invented
node counts, capacity, power, or TCO. The previous fixed `SIZES` are superseded.

初期整備予算と実際の推定費用は別です。仮配分額は構成の検討枠を示すものであり、
購入できる数量を保証しません。施設条件、保守、電力、人件費が未確認の間は、
5年間TCOも未算出とします。過去の固定ノード数は価格推定の根拠に使用しません。

## Five-year TCO evidence matrix / 5年間TCOの証拠マトリクス

Every case is checked against the same 12 non-overlapping scopes: compute and
accelerators; interconnect; storage; software and licenses; installation and
integration; maintenance and support; electricity; cooling; shared facilities;
staffing; refresh and expansion; and decommissioning and migration. A row is
`observed-contract-scope` only when a checked public source explicitly places it
inside or outside the contract, `reported-unitemized` when it is reported only as
part of an inseparable package, and `unknown` otherwise.

This matrix measures evidence coverage, not cost allocation. `unknown` never means
zero, and `reported-unitemized` cannot be converted to a component price. A
five-year amount may be shown as a `known-contractual-floor` only when the public
billing unit and covered 60-month period support deterministic arithmetic. Even
then, `complete_tco` remains false unless every scope has an evidenced value and
the scopes do not overlap. The 2026-09-02 audit finds seven public totals among
eight cases, no evidence-backed component itemization, and no complete five-year
TCO. The supporting audit is
[`20260902_001_center-tco-evidence-round1.md`](../research-baseline/20260902_001_center-tco-evidence-round1.md).

各案件を、計算機・アクセラレータ、インターコネクト、ストレージ、ソフトウェア・
ライセンス、設置・統合、保守・支援、電力、冷却、共用施設、要員、更新・増設、
撤去・移行の12費目で確認します。公開資料が契約への包含または除外を明示する場合は
`observed-contract-scope`、一式に含まれることだけが分かり分離できない場合は
`reported-unitemized`、それ以外は`unknown`とします。

この表は根拠の充足状況を示すもので、費用配分表ではありません。`unknown`をゼロと
みなさず、`reported-unitemized`から機器単価を算出しません。公開された支払単位と
60か月の対象期間から機械的に再計算できる場合だけ、契約上の既知費用下限として表示
します。それでも、12費目すべての値と非重複性が確認されるまで完全なTCOとはしません。

## Commands and follow-up / 検証と継続調査

```bash
python3 tools/check_procurement_costs.py
python3 tools/check_public_planning_surfaces.py
python3 tools/estimate_system_cost.py --budget-oku-jpy 30 --deployment-year 2030
python3 tools/add_budget_architecture_options.py
```

The offline estimator also accepts `--cost-lines <JSON>` for explicit initial and
annual lower/central/upper cost intervals. Each line identifies its evidence,
tax-exclusive basis, and disjoint scope IDs. This is arithmetic, not calibration;
missing terms block TCO and passing arithmetic never grants procurement authority.

For the next research loop, search official university/agency award notices and
itemized server, storage, network, and facility tenders. Track changed versions,
failed retrievals, price dates, and explicit scope. Keep all listed PCG gaps
open until their stated evidence requirements are met; a new URL or another model's
agreement alone does not close them. No unattended Run is enabled by this update.

### Billing and configuration checks / 支払単位と構成の照合

Match buyer, title, tender date cited by the award, and opening/award date before
connecting documents. Similar names in different procurement years are not a match.
The 2025 Tsukuba award cites the 2025-03-11 tender, not the similar 2024 tender.
A `contract_window` preserves the evidenced tender or contract period; it is not
an operational lifecycle event. `lease_period_total` is generated arithmetic only:
unchanged monthly rate times whole calendar months, in the original tax basis.
Do not infer a payment unit from the magnitude of a number. Keep unknown billing
units unknown. Unmatched configurations cannot calibrate component prices.

発注機関、件名、落札公示が参照する公告日、開札・落札日で照合します。同名の別年度
案件を混同しません。月額一定の期間合計は機器購入費でもTCOでもなく、元の税区分の
単純計算です。借入期間と稼働期間を区別し、公開構成は予定／稼働中の別と照合上の
未確認事項を残します。仕様変更や資料間の差を推測で解消しません。
