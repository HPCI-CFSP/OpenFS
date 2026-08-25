# Independent roadmap portfolio review

This procedure reviews the six P0 roadmaps, their assurance artifacts,
cross-roadmap dependencies, Coverage Gaps, and three HPCI scenarios without
allowing the authoring model to certify its own work.

## Author handoff

1. Finish and validate the full portfolio, then commit it. Do not build a package
   from an uncommitted worktree.
2. Build the package from the immutable artifact commit:

   ```bash
   python3 tools/build_consensus_review_package.py \
     --base-commit <40-hex-artifact-commit>
   ```

3. Commit the generated package separately. This makes the package point backward
   to a stable review target rather than trying to refer to its own commit.
   Preserve both commits when the pull request is merged. Prefer a merge commit
   for a package-bearing branch. A squash or rebase merge changes commit
   identity; if either is used, rebuild the package, manifest digest, gate result,
   and public view from commits reachable on the destination branch before
   assigning reviews.
4. Before building the package, register and enable each intended validator or
   critic in `config/agent-registry.json`. Their provider, model family, prompt
   profile, role, independence group, review-origin group, Harness ID, Harness
   repository and commit, public-Web access, public clearance, and `assessments`
   write scope are checked against the pinned registry. Set
   `review_origin_group`, `harness_id`, `harness_repository_url`, and
   `harness_commit` before enabling a reviewer; review-file self-declarations do
   not establish independence.
5. Assign at least four blind reviews that can satisfy the current
   `high_impact_recommendation` rule. The author group and same-conversation forks
   are ineligible as independent votes. The supporting set must span at least
   three registered model families, two providers, and two distinct Harness
   repositories. Each execution still pins its exact Harness commit.
6. Give every reviewer the package commit, not only the `base_commit`. The former
   identifies the exact `manifest.json`; the latter identifies the artifact set
   to inspect.

## Reviewer procedure

1. Check out the package commit, calculate SHA-256 over the exact
   `manifest.json` bytes, and record it as `package_manifest_digest`. Do not
   reserialize JSON before hashing. Then check out the package's `base_commit`
   and verify every artifact digest.
2. Read `manifest.json` before any prior assessment. Review all units and every
   required check; do not sample only favored technologies or one scenario.
3. Follow the falsification prompts and search for contradictory primary sources,
   later schedule changes, product cancellations, unsupported quarter precision,
   omitted alternatives, and infeasible dependencies or fallbacks.
4. For every milestone listed in a roadmap unit's
   `primary_source_requirements`, record one conclusive primary-source check
   using one of that milestone's registered `source_options`. The source ID,
   URL, and class must match the exact milestone citation in the package's
   pinned commit; reachability alone and secondary summaries do not satisfy
   this requirement. A `ROADMAP-SOURCE-TRIAGE-001` entry establishes only that
   one model could retrieve the exact official URL and cited text; it is not an
   independent primary-source check and cannot be copied as a review conclusion.
   OpenFS provisional gates and undated gaps remain in the
   unit assessment but are not presented as externally verified events.
   Set `registry_snapshot_digest` to the SHA-256 of the exact
   `config/agent-registry.json` Git object at `base_commit`.
5. Copy `review-template.json` to
   `assessments/CRP-P0-ROADMAPS-V02/<review-id>.json`, replace all
   placeholders, remove `_template_notice`, and record the exact model, provider,
   prompt profile, independence/origin groups, harness repository, and harness
   commit exactly as pinned in the Agent Registry.
6. Use `uncertain` when evidence is insufficient. Do not infer dates or convert a
   Coverage Gap into a negative fact.
7. Set `reviewed_at` to an RFC 3339 time with an explicit UTC offset. It must not
   predate package creation or be later than the gate evaluation time, apart from
   the one-minute clock-skew allowance.
8. Submit only the assigned assessment path from a reviewer-specific branch. A
   second Agent must not edit another reviewer's file or reuse its conclusions as
   a blind review.

## Deterministic gate

Run:

```bash
python3 tools/evaluate_consensus_review_package.py \
  reviews/consensus-packages/CRP-P0-ROADMAPS-V02/manifest.json \
  --output reviews/consensus-packages/CRP-P0-ROADMAPS-V02/gate-result.json
python3 tools/validate_json_schemas.py
```

Run the evaluator again after any review file is added, removed, or edited. The
gate result binds the exact manifest digest, the complete set of evaluated review
IDs, and each review file's SHA-256. GitHub Pages recomputes those digests and
fails closed on a stale gate result.

`incomplete` preserves provisional publication. `ready-for-human-decision` means
only that independent-review thresholds and package integrity passed. A reviewed
human Directive is still required before an HPCI recommendation can be accepted.
An eligible `support` review must support every review unit and every required
primary-source check, pass every required check, and contain no major or critical
objection. The falsification review is an additional independent assessment; it
does not need to manufacture support.

## Current limitation

The repository's agent registry does not yet enable enough genuinely independent
validator and critic groups with pinned Harness provenance. The package is
therefore a ready handoff mechanism, not evidence that Consensus has already been
achieved.
