# Information Boundary Policy

## Public OpenFS

Public OpenFS may contain public-source metadata, permitted evidence excerpts, public claims, assessments, decisions, policies, prompts, and generated reports.

OpenFS research is public-information based. A user-provided statement or file that is intended for public disclosure must still be classified and explicitly approved before it becomes a Pages artifact.

It must not contain NDA information, private vendor documents, credentials, personal information unnecessary for research, private run logs, or hints that reveal protected identifiers or conclusions.

## Private research plane

RiVault and other approved private environments use separate storage, credentials, agents, registries, runs, and decisions. Public agents must not receive private context.

## Crossing the boundary

Information may move from the private plane to public OpenFS only through the NDA Export Protocol. Absence of a confidentiality marking is not evidence that publication is allowed.

When classification is uncertain, quarantine the artifact and create an exception. Do not publish a redacted guess.

## GitHub Pages publication confirmation

A Recommendation or Consensus Decision is not publication permission. Before a scenario or report first appears on GitHub Pages, a human must create or approve a `publication-approval` Directive that names every target artifact. The static-site builder rejects published artifacts without the matching Directive, public classification, Publication Decision ID, and Japanese/English public summaries.
