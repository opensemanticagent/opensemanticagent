# Governance

## Today: founder-led
Open Semantic Agent was created by **Sangamesh Hiremath** (GitHub: `sangameshh`), who is currently the sole maintainer and makes final decisions on the spec and the MCP server.

## Roles
- **Contributors:** anyone who opens an issue, a discussion or a pull request.
- **Maintainers:** review and merge changes, triage issues, run releases. Contributors become maintainers by invitation after sustained, high-quality work.
- **Editors:** maintainers responsible for the wording of `spec/SPEC.md` and the schemas.

## How decisions are made
- **Editorial fixes** (typos, clarifications that change no rule): one maintainer approval.
- **Tooling changes** that don't change behavior defined by the spec: one maintainer approval and CI passing.
- **Normative changes** (any MUST/SHOULD/MAY, a schema change, or a change to a fixture's expected decisions) are decided in a pull request that says whether the change is additive (every envelope, manifest and record valid before stays valid, with the same meaning) or breaking.
  - **Early stage** (before 1.0 and while no implementation other than the maintainers' own is listed in `IMPLEMENTATIONS.md`): an additive change may be merged by a maintainer once CI passes, without a comment window. Comments are still welcome afterwards and can change the draft before its release.
  - **Breaking changes**, and every normative change once the early stage ends: the pull request stays open for comment for at least **14 days**, then is accepted by maintainer consensus.
  - The founder breaks ties until there are three or more maintainers.

## Path to neutral governance
1. Once there are three or more independent implementations (`IMPLEMENTATIONS.md`), form a steering group of at least three maintainers from different organizations.
2. Consider a standards or foundation home (for example a W3C Community Group or the Linux Foundation) once adoption justifies it.

## Licensing of contributions
By contributing you agree that your contribution is licensed under Apache-2.0 (see `LICENSE`). No CLA is required. Use the Developer Certificate of Origin by adding `Signed-off-by` to your commits (`git commit -s`).
