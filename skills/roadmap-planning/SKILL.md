---
name: roadmap-planning
description: Build or update a comparable public HPCI roadmap from approved evidence without inventing timing or hiding coverage gaps.
---

# Roadmap Planning

Use this Skill only after source validation and evidence extraction. Write a public
roadmap export only when the Work Item permits synthesis and the artifact has a
matching human publication Directive. A roadmap planner does not accept its own
research or claim that Consensus is complete.

1. Use `schemas/public-roadmap.schema.json` and the matching family in
   `config/roadmap-portfolio.json`. Preserve the stable `roadmap_id`, slug, and
   bilingual fields.
2. Prefer official vendor, standards-body, government, research-organization,
   and project sources. Use academic primary literature where it supplies the
   original result. Do not turn a secondary summary into a vendor commitment.
3. Record Q1-Q4 only when the cited source supports that quarter or a narrower
   date. Keep half-year and year-only statements at `quarter: null`; set
   `half: H1` or `half: H2` for supported half-year timing. Use an undated
   milestone when no public date exists. The renderer spans half-year entries
   across two quarters and year-only entries across Q1-Q4 as uncertainty windows,
   not durations. Do not interpolate between announced generations.
4. Add `generation_bands` only when a track has meaningful generations and the
   overview improves an HPCI decision. Keep standards-body and vendor lanes
   separate below it. Every band must preserve independent boundary precision,
   cite registered sources, state phase, confidence, and Consensus status, and
   allow overlapping generations. Use `openfs-synthesis` for a combined view;
   never infer an exclusive replacement date. With
   `extend-to-latest-dated-evidence`, later dated evidence extends the display
   horizon, while undated gaps and open-ended bands do not.
5. Separate factual events from OpenFS planning. Only HPCI evaluation or adoption
   gates may use `timing_basis: openfs-provisional-plan`.
6. Link each track, milestone, generation band, and dependency to source IDs. Declare dependencies
   against stable roadmap IDs and distinguish evidence-backed relations from
   OpenFS assessment.
7. Put every unresolved source, vendor, center, cost, performance, or later-horizon
   question in `coverage_gaps`, including its decision impact and next action.
   Missing evidence remains a gap and never becomes a forecast. Assign `P0` only
   when the answer can change an HPCI architecture, facility, procurement,
   migration, or scenario decision; assign `P1` to material comparison gaps and
   `P2` to useful context. Revisit priority when dependencies change.
8. Mark important cross-roadmap events `comparison_priority: key`; keep supporting
   releases and context as `supporting`.
9. Put reusable bilingual definitions and high-value comparison matrices only in
   `knowledge/public/roadmap-reference-data.json`. Validate it with
   `schemas/roadmap-reference-data.schema.json`, cite roadmap source IDs for every
   term and comparison row, and reference it from generated pages. Add comparisons
   for material compute, packaging, interconnect, software, workload, and
   evaluation choices as well as memory, but only when the common axes improve an
   HPCI decision.
10. For the reference-blueprint roadmap, connect the FY-specific public resource
    list through `knowledge/public/hpci-system-inventory.json`. Label annual HPCI
    call availability as such; never reinterpret it as procurement, commissioning,
    guaranteed service, retirement, or refresh timing. For the workload roadmap,
    use `knowledge/public/application-performance-forecasts.json` and the standard
    1, 4, 32, 128, 1,024, and about 10,000 Fugaku-node scales. Separate strong,
    weak, and throughput/ensemble comparisons, keep achieved FLOP/s secondary, and
    leave numerical forecasts empty when public calibration and independent
    validation are missing. Run `tools/check_public_planning_surfaces.py` after
    changing either artifact.
11. Before handoff, run JSON Schema validation, repository validation, unit tests,
   both roadmap audit generators, Pages generation, and desktop/mobile visual
   checks. The public export remains
   `research_status: provisional` and `consensus_status: incomplete` until the
   configured independent-model Consensus Gate supplies an accepted receipt.
12. For a six-roadmap portfolio or an HPCI scenario recommendation, first commit the
   complete review target. Then run
   `tools/build_consensus_review_package.py --base-commit <40-hex-commit>` and
   distribute that pinned package to blind reviewers. Reviewers must inspect every
   review unit, seek counterevidence, record at least one conclusive registered
   primary-source check for every roadmap, record provider/model/prompt/harness identity,
   and submit schema-valid assessments. Do not count this planner's own review,
   same-conversation forks, or shared-conclusion reviewers as independent.
13. Run `tools/evaluate_consensus_review_package.py <manifest>`. A
    `ready-for-human-decision` result is not acceptance; high-impact adoption still
    requires the human decision required by policy.
