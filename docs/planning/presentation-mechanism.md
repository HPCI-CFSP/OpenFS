# Scenario Presentation Mechanism

## Views

OpenFS generates two synchronized views from one reviewed scenario set:

- `reports/drafts/system-scenarios.md`: human-readable overview, architecture/software/application details, center impacts, domestic technology, evaluation matrix, uncertainty, gates, and traceability.
- `reports/exports/system-scenarios.json`: machine-readable data for the annual report repository, a static site, or another approved presentation layer.

The generator never hides missing scores. With no approved weights it shows an unranked side-by-side comparison. With approved weights, a later implementation may add sensitivity-aware ranking, but the raw criteria and rationale remain visible.

## Review states

| State | Audience | Meaning |
|---|---|---|
| Illustrative example | developers | Exercises schemas and rendering; not evidence or advice |
| Candidate | research reviewers | Generated from labeled inputs; not accepted |
| Under review | independent agents and humans | Objections, alternatives, and traceability are being checked |
| Accepted | internal decision process | Passed policy gates and human approval for the stated scope/date |
| Published | approved audience | Exported with classification, version, as-of date, and supersession link |

## Human intervention

Weekly runs can update evidence and regenerate candidate views automatically. Humans review digests, add GitHub Issues or `reviews/directives/`, approve criteria and weights, resolve high-impact dissent, and authorize publication. A later Directive can request a new scenario objective without discarding previous scenarios or their review history.
