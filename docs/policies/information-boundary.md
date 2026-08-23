# Information Boundary Policy

## Public OpenFS

Public OpenFS may contain public-source metadata, permitted evidence excerpts, public claims, assessments, decisions, policies, prompts, and generated reports.

It must not contain NDA information, private vendor documents, credentials, personal information unnecessary for research, private run logs, or hints that reveal protected identifiers or conclusions.

## Private research plane

RiVault and other approved private environments use separate storage, credentials, agents, registries, runs, and decisions. Public agents must not receive private context.

## Crossing the boundary

Information may move from the private plane to public OpenFS only through the NDA Export Protocol. Absence of a confidentiality marking is not evidence that publication is allowed.

When classification is uncertain, quarantine the artifact and create an exception. Do not publish a redacted guess.
