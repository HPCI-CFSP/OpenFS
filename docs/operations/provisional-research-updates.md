# Bounded provisional research updates

## Authority and scope

This interactive maintainer workflow implements `DIR-900015`. It is not a
scheduled worker or a Consensus promotion. One model may update a named research
unit with primary-source checks, but the result remains `partial`, `provisional`,
and `consensus_status=incomplete`. Do not enable agents, monitors, publication
rights, scoring, or procurement decisions through this workflow.

## Procedure

1. Start from a committed input. Read the Topic's complete unit list, current
   profile, prior update bundles, linked roadmaps, and Coverage Gaps.
2. Select a bounded subset of existing units. Pin the base commit and SHA-256
   digest of the complete input profile and each selected unit.
3. Use managed public Web research. Record exact source URLs, original publisher
   groups, actual read timestamps, passage locators, and bilingual observations.
   A successful read is not independent validation. Failed retrievals must remain
   unresolved; do not refresh their verification dates or use a shell fallback.
4. Create a new `proposals/research-unit-updates/RUP-NNNNNN.json` under
   `schemas/research-unit-update.schema.json`. Append new section, item, source,
   and Gap IDs. Archive replaced sections without deleting their payloads. Every
   new section must be assigned to one of the selected units. Keep unselected
   units unchanged and state remaining research explicitly.
5. Check permissions and obtain the artifact-specific human publication Directive.
   Run the tool without `--apply` first, inspect the diff, then apply only under
   the explicit interactive maintainer authorization:

```sh
python3 tools/apply_research_unit_update.py proposals/research-unit-updates/RUP-NNNNNN.json
python3 tools/apply_research_unit_update.py proposals/research-unit-updates/RUP-NNNNNN.json --apply --human-authorized
python3 tools/apply_research_unit_update.py --audit
python3 tools/validate_json_schemas.py
```

6. Regenerate the catalog, source map, and affected roadmap assurance artifacts.
   Check JA/EN equivalence, current links, source dates, and all existing tests.
   For successive updates in one PR, retain the reachable base commit and list
   every intervening update in order in `predecessor_updates`, with its digest.
   The verifier replays that exact chain and checks the resulting input digests.
   Do not depend on an intermediate branch commit that a squash merge may remove.
   Review and publish through a PR; do not push to the protected default branch.

## Concurrency, history, and recovery

The projector checks the whole profile and selected units before changing either
document. A stale input must be rebased and researched again where necessary;
never solve a conflict by taking one agent's entire profile. Applied bundles and
their section payloads are immutable. Reapplying an unchanged bundle is idempotent;
an amended observation requires another ID and a new committed input.

The two projection files are written sequentially, not as an atomic filesystem
transaction. Keep unrelated work out of those files during application. If a
write is interrupted, the audit must fail. Inspect both files against the pinned
commit, preserve concurrent work, and repair the incomplete projection before
continuing. Do not run destructive checkout/reset commands automatically.

Current records cannot close a Gap or become reviewed through this tool. Closure
and acceptance require the applicable independent evidence and Consensus workflow.
The audit checks provenance consistency, not the truth or completeness of claims.

## 日本語要約

この手順は、人間が明示的に依頼した対話型の暫定調査に限ります。対象の調査単位、
入力コミット、更新前のハッシュ、一次情報の確認箇所を記録し、既存の根拠は削除せず
新しい版を追加します。競合時は更新を止め、他の変更を確認してから作り直します。
途中で書き込みが止まった場合は、2つの投影ファイルの整合性を確認して復旧します。
調査済みの項目も暫定のままであり、単一モデルによる確認をConsensusや独立検証と
表示してはいけません。未調査項目、取得に失敗した資料、未解決のCoverage Gapを
残し、無人運転や調達判断をこの手順から有効化しないでください。
