# Changelog

## Unreleased
- **Spec 0.5 draft** (additive): notifications. `delivery.notify` in the subscription manifest (§4): channels (Web Push, APNs, FCM, email) to `contact://` recipients, rules (minimum severity, states, cooldown, hourly cap, quiet hours with a critical override), content limits and escalation. Notification records (§6.12, `application/vnd.osa.notification+json`): sent, failed, acknowledged or expired, with the person's answer. Notification delivery (§9.4): once per condition change, minimal payloads, no secrets, no content except over end-to-end encrypted channels when allowed, never a command, critical and strict alerts never wait on a model or budget, and an exact Web Push binding (RFC 8030, 8291, 8292). New schema `notification`, `subscription` and `envelope` updated, new fixture `envelopes_v0_5`. Proposal: issue #15.

## 0.4.0 (package), 2026-11-23
The package serves spec 0.4 (draft), which includes everything from 0.3. Package 0.3.0 was never released.
- Governance: before 1.0 and while no outside implementation is listed, additive normative changes may merge without the 14-day comment window; breaking changes always keep it.
- **Spec 0.4 draft** (additive): recommendations (§6.11) with `content_type: application/vnd.osa.recommendation+json`, topic `recommendation.<kind>`, `correlation.parent` = the envelope answered; ranked actions with expected effect, effort, reversibility and an optional command that consumers never run without confirmation; evidence, provenance and a lifecycle (open, done, dismissed, expired). New schema `recommendation`, envelope schema checks recommendation data, new fixture `envelopes_v0_4`. Package 0.4.0.
- **Spec 0.3 draft** (all additive): `subject`, `correlation` and `labels.sensitivity` on the envelope (§3); metrics envelopes with batched samples, UCUM units, gauge, counter and delta kinds, and rollups (§6.9); alerts with severity, state and dedupe key (§6.10); stream resume with `delivery.replay_window` (§9.3); read-only `history` and `metrics_query` MCP tools and required tool annotations (§9.1); OpenTelemetry mapping (Appendix B).
- New schemas `metrics` and `alert`; `envelope`, `subscription` and `stream` updated. New fixture `envelopes_v0_3` with schema and handling cases.
- MCP server: `osa_get_schema` and `osa_validate` cover metrics and alerts; envelope validation checks metrics and alert data; cross-schema references resolve locally.
- MCP tool annotations are written out on each tool, so static scanners (M8ven) can read them. Same values, same behavior.

## 0.2.3 (package), 2026-11-21
- OpenSSF Best Practices passing badge (project 16976).
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
