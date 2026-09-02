# Planning Evidence Integration

## Purpose

`knowledge/public/planning-evidence-readiness.json` connects five evidence
dimensions to the published system planning options without turning incomplete
public data into a recommendation:

1. system lifecycle and migration constraints;
2. utilization, power, and actual use;
3. public procurement and five-year cost;
4. EEA1 measurements and performance models; and
5. quantitative application requirements.

The artifact is a public, provisional decision-support view. It remains
Consensus-incomplete and cannot authorize procurement, a budget request, or a
ranking.

## Evidence boundaries

- A provider-published refresh target is not a contract or formal service date.
- Utilization values are comparable only when the period, denominator,
  maintenance exclusions, and system boundary are aligned.
- A contractual known-cost floor is not complete total cost of ownership (TCO).
  Unknown electricity, facilities, staffing, maintenance, amendments, and
  expansion costs must not be treated as zero.
- A measured performance envelope is not a validated future forecast.
- A published measurement scale or scientific target is not a human-approved
  acceptance requirement.

Coverage numerators and denominators are recomputed by
`tools/check_public_planning_surfaces.py`. The validator fails when the public
readiness view no longer matches its source artifacts.

## Planning use

Each system planning option receives an evidence implication, a commitment
boundary, and the dimensions that still block commitment. The three options
remain unranked. Resource ratios and quantities stay unknown until common
benchmarks, facility constraints, complete cost evidence, and accountable human
requirements are available.

## 日本語

`knowledge/public/planning-evidence-readiness.json` は、次の5種類の根拠を、
公開中のシステム整備計画案へ接続します。

1. システム更新時期・移行制約
2. 稼働率・電力・利用実態
3. 公開調達額・5年間費用
4. EEA1実測・性能モデル
5. アプリケーション定量要件

この成果物は、公開情報に基づく暫定的な判断支援資料です。独立した
モデル・エージェントによる合意判定は未完了であり、調達、予算要求、
推奨順位を決定するものではありません。

公開された更新予定は契約日や正式サービス開始日ではありません。
稼働率は、対象期間、分母、保守停止の扱い、システム境界が一致した場合に
限って比較します。契約上の既知費用下限は完全なTCOではなく、電力、施設、
人員、保守、契約変更、増設の未確認費用をゼロとして扱いません。実測範囲は
検証済みの将来予測ではなく、公開された測定規模や科学目標も、人が承認した
受入要件とは区別します。

`tools/check_public_planning_surfaces.py` は、各項目の充足数を元データから
再計算します。元データと公開用監査結果が一致しない場合は検証を失敗させます。
