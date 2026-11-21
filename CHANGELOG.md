# Changelog

## Unreleased
- CI runs ruff (lint and security checks) and CodeQL; workflows default to a read-only token; CONTRIBUTING requires tests for new behavior.
- Zenodo DOI 10.5281/zenodo.24417032 in CITATION.cff and the README.

## 0.2.2 (package), 2026-11-21
- Community files: contributing guide, code of conduct, security policy, governance, roadmap, implementations list, citation metadata, issue and pull request templates.
- SPEC §10 and "Changes in 0.2" no longer point to a results file outside this repo.

## 0.2.1 (package), 2026-11-21
- Wire identifiers are `osa`: `"spec": "osa/0.2"`, the `osa` envelope key, and the `osa.v0.2` WebSocket subprotocol.
- `open-semantic-agent` MCP server: `osa_list_sections`, `osa_get_section`, `osa_search_spec`, `osa_get_schema`, `osa_validate`, `osa_list_fixtures`, `osa_get_fixture`. All read-only. Published on PyPI and the MCP Registry as `io.github.opensemanticagent/opensemanticagent`.
- Website at https://opensemanticagent.org.

## Spec 0.2
All additive over 0.1; implementations accept both `osa/0.1` and `osa/0.2` envelopes.
- §3: idempotent publish by envelope `id`, with a `duplicate` audit record.
- §4, §5: `match.accept_above`, `match.min_confidence`, calibration guidance, and `model_policy.on_budget_exhausted`.
- §5: Tier 0 guidance on source-side topics.
- §9.1: `consume`. §9.3: streaming delivery with SSE and WebSocket bindings.
- Appendix A (informative): deployment next to request/response APIs, and wired devices through a phone.

## Spec 0.1
- Envelope, subscription manifest, three-tier decision engine (topic match, embeddings, AI judge under budgets), capabilities, adapter interfaces, audit records, MCP and A2A agent interfaces, conformance levels L0 to L2.
