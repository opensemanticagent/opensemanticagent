# Contributing to Open Semantic Agent

## Ways to help
- **Implement it.** Build a bus, a client library or a validator in any language, then open a pull request adding it to `IMPLEMENTATIONS.md` with the conformance level it meets (SPEC §10).
- **Add conformance cases.** These are the most valuable contribution, because they pin down what correct routing means. Fixtures live in `conformance/fixtures/`.
- **Review the spec.** Open an issue when a rule is unclear, untestable or missing.
- **Improve the MCP server** in `osa/`, which serves the spec, schemas and fixtures to AI assistants.

## Process
1. Open an issue that describes the problem before proposing a normative change.
2. **Normative changes** (any MUST/SHOULD/MAY in `spec/SPEC.md`, a schema change, or a change to expected decisions in a fixture) need a pull request that explains the motivation, the change and its effect on each conformance level, plus at least one new or updated fixture. See `GOVERNANCE.md` for how they are decided.
3. **Editorial changes** (wording, typos, examples that change no rule) just need a pull request.
4. Before pushing, run the checks CI runs:
   ```bash
   pip install "jsonschema>=4.20" markdown
   python -m unittest discover -s tests
   python tools/build_site.py && git diff --exit-code -- docs/
   ```
   The site in `docs/` is generated from `spec/SPEC.md` and `schemas/`; commit it together with the change.
5. Use made-up data in examples and fixtures. Never commit real personal data or secrets.
6. Add a line to `CHANGELOG.md` under "Unreleased".

## Versioning
The spec version appears in envelopes as `"spec": "osa/<major>.<minor>"` (SPEC §12). A minor version only adds features; a major version may break compatibility and needs a migration note. The `open-semantic-agent` package follows the spec's major and minor version and adds a patch number.

## Conduct, security and governance
- `CODE_OF_CONDUCT.md`: Contributor Covenant 3.0
- `SECURITY.md`: report vulnerabilities privately
- `GOVERNANCE.md`: how decisions are made; sign off your commits (`git commit -s`)
