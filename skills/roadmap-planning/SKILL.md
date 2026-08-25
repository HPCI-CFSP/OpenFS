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
   date. Keep half-year and year-only statements at `quarter: null`; use an
   undated milestone when no public date exists. Do not interpolate between
   announced generations.
4. Separate factual events from OpenFS planning. Only HPCI evaluation or adoption
   gates may use `timing_basis: openfs-provisional-plan`.
5. Link each track, milestone, and dependency to source IDs. Declare dependencies
   against stable roadmap IDs and distinguish evidence-backed relations from
   OpenFS assessment.
6. Put every unresolved source, vendor, center, cost, performance, or later-horizon
   question in `coverage_gaps`, including its decision impact and next action.
   Missing evidence remains a gap and never becomes a forecast.
7. Mark important cross-roadmap events `comparison_priority: key`; keep supporting
   releases and context as `supporting`.
8. Before handoff, run JSON Schema validation, repository validation, unit tests,
   Pages generation, and desktop/mobile visual checks. The public export remains
   `research_status: provisional` and `consensus_status: incomplete` until the
   configured independent-model Consensus Gate supplies an accepted receipt.
