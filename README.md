# Open Semantic Agent (OSA)

**An open spec for publish/subscribe that routes messages by what they mean.**

Website: **https://opensemanticagent.org** · Spec: [`spec/SPEC.md`](spec/SPEC.md)

OSA sits on top of the message transport you already run (Kafka, NATS, Redis Streams, SQS) and works with whichever model you choose. Each message goes through three checks in order: a free topic match, a cheap similarity check, and an AI judge only when the first two are unsure, under token budgets. Every decision is audited and replayable.

| Conventional broker | Open Semantic Agent |
|---|---|
| String topics | Semantic subscriptions: subscribe by meaning |
| Payload delivered as-is | Schema mediation: each subscriber gets its own contract |
| Dedupe by message ID | Semantic dedupe: 40 alerts about one incident become 1 |
| Static priority | Reasoned urgency, with a recorded rationale |
| Slow consumer → lag or drop | Backlog summarization: a digest instead of a loss |
| Dead-letter queue | Self-healing DLQ: diagnose, repair, retry or escalate |
| Replay the raw log | Briefings: "catch me up on order 123 since Monday" |
| One reply | Consensus fan-in: ask N agents, reconcile the answers |
| Per-topic ACLs | Per-subscriber redaction by clearance |
| Opaque routing | Every decision audited and replayable |


## Use it from an AI assistant

The spec ships as a small MCP server, so any MCP client (Claude, Cursor, VS Code and others) can read it and check documents against it:

```bash
uvx open-semantic-agent          # or: pip install open-semantic-agent
```

Tools, all read-only: `osa_list_sections`, `osa_get_section`, `osa_search_spec`, `osa_get_schema`, `osa_validate` (envelope, subscription manifest, audit record, stream message), `osa_list_fixtures`, `osa_get_fixture`. It is listed in the MCP Registry as `io.github.opensemanticagent/opensemanticagent`.

<!-- mcp-name: io.github.opensemanticagent/opensemanticagent -->

## What's here

| Path | What it is |
|---|---|
| `spec/SPEC.md` | The specification (0.2, draft) |
| `schemas/` | JSON Schemas for the envelope, subscription manifest, audit record and stream messages. Each `$id` resolves on the website. |
| `conformance/fixtures/` | Routing test vectors that implementations run against |
| `osa/`, `tests/` | The MCP server and its tests. The package bundles the spec, schemas and fixtures. |
| `tools/build_site.py`, `docs/` | The website. `pip install markdown && python3 tools/build_site.py` rebuilds `docs/`, which GitHub Pages serves. |

## Implementations

Building one? Open an issue and we'll list it here.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Spec changes go through a pull request against `spec/SPEC.md`; changes that affect routing add or update fixtures in `conformance/fixtures/`. Questions and ideas go to [Discussions](https://github.com/opensemanticagent/opensemanticagent/discussions). Security issues: see [SECURITY.md](SECURITY.md).

If you cite the spec, use [CITATION.cff](CITATION.cff).

## License

Apache-2.0.
