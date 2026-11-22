# Roadmap

| Milestone | Target | Contents |
|---|---|---|
| **0.2** | Nov 2026 | Idempotent publish, confidence edges and budget-exhaustion policy, streaming delivery (SSE, WebSocket), deployment guidance (Appendix A); JSON Schemas; conformance fixtures; `open-semantic-agent` MCP server on PyPI and the MCP Registry |
| **0.3** (current draft) | Dec 2026 | Metrics envelopes with batched samples, units and rollups; alerts; subject, correlation and sensitivity on the envelope; stream resume; OpenTelemetry mapping; 0.3 conformance fixtures |
| **0.3.x** | Q1 2027 | Conformance runner that any implementation can use against the fixtures; L2 fixtures for schema mediation, digests and dead-letter repair; first external implementation listed |
| **0.4** | Q2 2027 | Transport bindings (Kafka, NATS, Redis Streams, SQS) as informative annexes; multi-tenant budgets; signed audit records |
| **1.0** | late 2027 | Stability freeze, three independent implementations, neutral governance (see `GOVERNANCE.md`) |

Open questions are tracked as issues labelled `spec` and in GitHub Discussions.
