# P0 roadmap v0.2 independent review package

This package pins 6 P0 roadmaps, 165
milestone records, 134 source registrations representing
121 unique URLs,
14 cross-roadmap dependencies,
31 prioritized Coverage Gaps, and
3 provisional HPCI scenarios to commit `8c09b5229a6b3e3975e3f9795e2e862015882314`.

## Review protocol

1. Check out exactly `8c09b5229a6b3e3975e3f9795e2e862015882314`, verify every `artifact_manifest.sha256`, and
   record the SHA-256 of the exact `manifest.json` bytes as
   `package_manifest_digest` in the review. Do not reserialize the manifest
   before calculating this digest.
2. Review every `review_unit` independently. Inspect cited public primary sources;
   URL reachability alone is not evidence that a claim is correct.
   Record one conclusive primary-source check for every milestone listed in
   `primary_source_requirements`, using one of that milestone's registered
   `source_options`. Key OpenFS proposals and undated gaps remain subject to the
   unit assessment but do not masquerade as externally verified events.
3. Actively seek counterevidence using each unit's falsification prompts. Keep
   unsupported timing as a Coverage Gap; do not infer a quarter.
4. Fill `review-template.json`, remove `_template_notice`, assign a unique review
   ID, and save it under `assessments/CRP-P0-ROADMAPS-V02/`. Do not edit the package manifest.
5. Record provider, model family, prompt profile, independence/origin groups,
   harness repository, and harness commit. A fork of the author conversation is
   not an independent vote. The agent must be enabled in the commit-pinned Agent
   Registry, its origin and Harness provenance must exactly match that Registry,
   and `registry_snapshot_digest` is the SHA-256 of its exact Git object.
6. Run schema and repository validation. Consensus remains incomplete until the
   configured policy passes and a human makes the required high-impact decision.
   An overall `support` vote is eligible only when every unit supports, every
   required check passes, every required primary-source check supports, and no
   major or critical objection remains. Re-run the evaluator after adding,
   removing, or editing any review; its result pins the exact manifest and every
   evaluated review file by SHA-256.

## 日本語要約

このパッケージは、P0の6ロードマップ、
165マイルストーン、134件の情報源登録
（重複除去121 URL）、
14相互依存、31件の優先度付きCoverage Gap、
HPCI整備計画3案をコミット `8c09b5229a6b3e3975e3f9795e2e862015882314` に固定します。
各review unitを独立に検証し、`primary_source_requirements` に列挙された重要
マイルストーンごとに一次情報を照合して、反証を探索してください。URL到達性を内容の
正しさとみなさず、四半期を推定で補わないでください。同一会話のforkや作成モデルと同じ
independence groupは独立票に数えません。Reviewerは固定されたAgent Registryへ
有効なAgentとして登録され、支持票は3モデル系統、2プロバイダ、2つの異なるHarness
Repository以上を満たし、各実行のHarness commitを固定する必要があります。
Consensus成立後も最終採用には人の判断が必要です。
