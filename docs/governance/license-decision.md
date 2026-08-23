# OpenFS License Decision

## Recommendation

Use **Apache License 2.0** for the project-authored repository as the initial license, after confirming the copyright holder and authority to license contributions.

It permits academic, public-sector, and commercial use and modification, includes an explicit contributor patent license and patent-termination clause, supports contributions without forcing downstream products to open their own code, and can cover source code, configuration, schemas, and documentation in one repository-wide rule.

Add a boundary notice stating that the license applies only to material for which the project has licensing authority. Linked MEXT reports, vendor documents, quoted excerpts, trademarks, third-party data, and NDA material are not relicensed by OpenFS.

## Options

| Option | Advantages for OpenFS | Disadvantages / caution | Fit |
|---|---|---|---|
| Apache-2.0 | Permissive; explicit patent grant; modification and attribution notices; suitable for institutional and commercial reuse; one rule can cover code and documentation | Longer and more procedural than MIT; requires preserving notices; confirm who can grant contributor patent rights | **Recommended** |
| MIT | Very short, familiar, and permissive; low compliance burden | No explicit patent grant or patent-retaliation clause; less guidance for notices and institutional contributions | Good if absolute simplicity is the priority |
| BSD-3-Clause | Permissive and familiar in academia; explicit non-endorsement clause | No explicit patent grant; binary/source notice rules; no material benefit over Apache for this project | Acceptable, but weaker fit |
| MPL-2.0 | File-level copyleft returns modifications to covered files while allowing larger proprietary systems | More compliance complexity; less convenient for agents, schemas, generated site files, and mixed report content; can deter integration | Use only if returning modifications is a policy goal |
| Apache-2.0 code + CC BY 4.0 documentation/reports | Conventional license for reusable reports; clear attribution for original content; Apache retains software patent terms | Two path-based license regimes, more agent and contributor complexity, and careful exclusion of third-party content required | Consider later if report reuse needs a distinct content license |
| No license | Avoids granting reuse before ownership is settled | Public visibility does not grant open-source reuse; discourages contribution and adoption; ambiguous for generated outputs | Temporary only |

Creative Commons recommends using software-specific licenses rather than CC licenses for software. If OpenFS later dual-licenses original documentation or reports under CC BY 4.0, code, schemas, and tools should remain under a software license.

## Required human confirmation before adding `LICENSE`

1. Identify the copyright holder: HPCI-CFSP, RIKEN, individual contributors, or another authorized entity.
2. Confirm contributors and participating institutions are permitted to license their contributions under Apache-2.0.
3. Confirm whether project-authored reports should remain Apache-2.0 or use a separate CC BY 4.0 content license.
4. Approve the third-party-material boundary and preferred copyright notice.
5. Record the decision in a reviewed Directive, then add `LICENSE`, `NOTICE`, and `THIRD_PARTY_NOTICES.md` together.

Until these points are confirmed, the repository remains publicly visible but not open-source licensed.
