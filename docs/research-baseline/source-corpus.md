# Research Baseline Source Corpus

## Handling rule

The source PDFs remain outside this public repository. OpenFS stores only metadata and hashes here so an agent can identify the exact local references without republishing them. A public marking on a document does not by itself grant redistribution rights.

The files below were supplied in the FS3.0 session `Materials` directory. Hashes are SHA-256 over the original PDF bytes.

| Source ID | Document | Stated context | SHA-256 | Origin group |
|---|---|---|---|---|
| `FSBASE-SRC-001` | `20251203_FS3.0_Overview_jp.pdf` | FS3.0 overview, Japanese, v1.0, marked public | `2f9c268f57b5bd40c2954cf710d8360722b26c6fdbb67df3f6ac61f0891f8d0a` | `FSBASE-ORG-001` |
| `FSBASE-SRC-002` | `20251203_FS3.0 Overview_en-US.pdf` | English rendering of the FS3.0 overview | `eb727c368a810b207c4a268e1a28e282fb19113bdd024a17ecf72dc6d8d99d3e` | `FSBASE-ORG-001` |
| `FSBASE-SRC-004` | `20260316-18_HPC研究会_FS3.0.pdf` | Presentation at the 203rd HPC / 17th QS joint meeting, March 16-18, 2026, v1.0, marked public | `0c0b0b8c8ea1ac1bcbdbd985b9c10a99f943bdeaf829e20a8a7c1a4c452a4c26` | `FSBASE-ORG-003` |
| `FSBASE-SRC-005` | `20260216-20_MulticoreWorld2026.pdf` | MulticoreWorld 2026 presentation, February 16-20, 2026, v1.7, marked public | `fdf532a0255ec64eb971c03569d5f5e8f82caaa06d5b7ce249dfc8dc98f8ba2f` | `FSBASE-ORG-004` |

## Lineage cautions

- `FSBASE-SRC-001` and `FSBASE-SRC-002` are language variants of one overview and count as one origin, not independent corroboration.
- The overview and later presentations overlap substantially. They are useful for scope discovery but are not independent proof of a technology claim.
- One supplied proposal document was not registered because a public marking was not confirmed during this review. It remains outside the public baseline until classification is approved.
- The corpus represents current FS3.0 planning and related FugakuNEXT-era explanations. It does not substitute for the complete FS1.0 or FS2.0 record.
- Facts extracted from these sources still enter OpenFS as proposals and pass the normal evidence and claim gates before canonical promotion.

## Reproduction

To match a local file to this corpus, compute `shasum -a 256 <file>`. A mismatch means the document is a different version and must receive a new Source ID or explicit revision lineage.
