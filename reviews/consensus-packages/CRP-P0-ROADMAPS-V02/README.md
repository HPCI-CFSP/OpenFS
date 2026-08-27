# CRP-P0-ROADMAPS-V02 independent review package

This package pins 6 P0 roadmaps, 200
milestone records, 7 synthesized generation bands,
and 207 source registrations representing
194 unique URLs,
14 cross-roadmap dependencies,
39 prioritized Coverage Gaps, and
3 provisional HPCI scenarios to commit `6fb09862268321fb0a3d3f6e980268f2da87cecf`.

## Review protocol

1. Check out exactly `6fb09862268321fb0a3d3f6e980268f2da87cecf`, verify every `artifact_manifest.sha256`, and
   record the SHA-256 of the exact `manifest.json` bytes as
   `package_manifest_digest` in the review. Do not reserialize the manifest
   before calculating this digest.
2. Review every `review_unit` independently. Inspect cited public primary sources;
   URL reachability alone is not evidence that a claim is correct.
   Record one conclusive primary-source check for every milestone or generation
   band listed in `primary_source_requirements`, using one of its registered
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
200マイルストーン、7世代帯、
207件の情報源登録
（重複除去194 URL）、
14相互依存、39件の優先度付きCoverage Gap、
HPCI整備計画3案をコミット `6fb09862268321fb0a3d3f6e980268f2da87cecf` に固定します。
各review unitを独立に検証し、`primary_source_requirements` に列挙された重要
マイルストーンまたは世代帯ごとに一次情報を照合して、反証を探索してください。URL到達性を内容の
正しさとみなさず、四半期を推定で補わないでください。同一会話のforkや作成モデルと同じ
independence groupは独立票に数えません。Reviewerは固定されたAgent Registryへ
有効なAgentとして登録され、支持票は3モデル系統、2プロバイダ、2つの異なるHarness
Repository以上を満たし、各実行のHarness commitを固定する必要があります。
Consensus成立後も最終採用には人の判断が必要です。
