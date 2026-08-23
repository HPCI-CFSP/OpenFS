# Research Baseline Source Corpus

## Handling rule

The source PDFs remain outside this public repository. OpenFS stores only metadata and hashes here so an agent can identify the exact local references without republishing them. A public marking on a document does not by itself grant redistribution rights.

The first four files below were supplied in the FS3.0 session `Materials` directory. The additional 26 PDFs were downloaded from the four official MEXT report pages on 2026-08-23. Hashes are SHA-256 over the original PDF bytes.

| Source ID | Document | Stated context | SHA-256 | Origin group |
|---|---|---|---|---|
| `FSBASE-SRC-001` | `20251203_FS3.0_Overview_jp.pdf` | FS3.0 overview, Japanese, v1.0, marked public | `2f9c268f57b5bd40c2954cf710d8360722b26c6fdbb67df3f6ac61f0891f8d0a` | `FSBASE-ORG-001` |
| `FSBASE-SRC-002` | `20251203_FS3.0 Overview_en-US.pdf` | English rendering of the FS3.0 overview | `eb727c368a810b207c4a268e1a28e282fb19113bdd024a17ecf72dc6d8d99d3e` | `FSBASE-ORG-001` |
| `FSBASE-SRC-004` | `20260316-18_HPC研究会_FS3.0.pdf` | Presentation at the 203rd HPC / 17th QS joint meeting, March 16-18, 2026, v1.0, marked public | `0c0b0b8c8ea1ac1bcbdbd985b9c10a99f943bdeaf829e20a8a7c1a4c452a4c26` | `FSBASE-ORG-003` |
| `FSBASE-SRC-005` | `20260216-20_MulticoreWorld2026.pdf` | MulticoreWorld 2026 presentation, February 16-20, 2026, v1.7, marked public | `fdf532a0255ec64eb971c03569d5f5e8f82caaa06d5b7ce249dfc8dc98f8ba2f` | `FSBASE-ORG-004` |

## Official MEXT FS2.0/FS3.0 report set

| Fiscal year | Official page | Registered sources | Teams covered |
|---|---|---|---|
| FY2022 / Reiwa 4 | [MEXT report page](https://www.mext.go.jp/b_menu/shingi/chousa/shinkou/067/mext_02883.html) | `FSBASE-SRC-006` to `FSBASE-SRC-011` | RIKEN system, Kobe system, Keio new computing principles, University of Tokyo operations |
| FY2023 / Reiwa 5 | [MEXT report page](https://www.mext.go.jp/b_menu/shingi/chousa/shinkou/067/mext_00008.html) | `FSBASE-SRC-012` to `FSBASE-SRC-019` | RIKEN system, Kobe system, Keio new computing principles, University of Tokyo operations |
| FY2024 / Reiwa 6 | [MEXT report page](https://www.mext.go.jp/b_menu/shingi/chousa/shinkou/067/mext_00015.html) | `FSBASE-SRC-020` to `FSBASE-SRC-025` | RIKEN system, Kobe system, Keio new computing principles, University of Tokyo operations |
| FY2025 / Reiwa 7 | [MEXT report page](https://www.mext.go.jp/a_menu/kaihatu/jouhou/mext_00020.html) | `FSBASE-SRC-026` to `FSBASE-SRC-031` | Program structure, operations organization, operations/security, RIKEN compute-system plan, Tohoku quantum hybrid |

The complete 26-file inventory, page counts, review role, and cross-report synthesis are in `fs2-fs3-corpus-review.md`. Exact URLs, filenames, hashes, origin groups, and page counts are machine-readable in `config/research-baseline.json`.

## Lineage cautions

- `FSBASE-SRC-001` and `FSBASE-SRC-002` are language variants of one overview and count as one origin, not independent corroboration.
- The overview and later presentations overlap substantially. They are useful for scope discovery but are not independent proof of a technology claim.
- One supplied proposal document was not registered because a public marking was not confirmed during this review. It remains outside the public baseline until classification is approved.
- FY2022-FY2024 reports form the official FS2.0 record used here. FY2025 reports form the official first-year FS3.0 record and include the related operation, security, and quantum-hybrid teams.
- Multiple parts of one team's annual report share one origin group. Annual reports from the same team are distinct publications but can still share methods, authors, or carried-forward text; reviewers must account for that correlation.
- The corpus still does not substitute for the FS1.0 record or current primary evidence from each HPCI center, vendor, standards body, and research project.
- Facts extracted from these sources still enter OpenFS as proposals and pass the normal evidence and claim gates before canonical promotion.

## Reproduction

To match a local file to this corpus, compute `shasum -a 256 <file>`. A mismatch means the document is a different version and must receive a new Source ID or explicit revision lineage.
