# Security Policy

Open Semantic Agent routes messages, sometimes through AI models, so a flaw in the spec can leak data or let a message steer the bus.

## In scope
- **Spec rules that are unsafe as written:** for example, a way for a message's content to change routing, redaction or budgets (prompt injection), or for redacted fields or `strict` topics to reach a model (SPEC §6.8, §11).
- **The `open-semantic-agent` MCP server** in `osa/`: anything that lets a caller read files outside the bundled spec data, run code, or crash the server with a crafted document.
- **Schemas** that accept documents the spec forbids, where that has security consequences.

## Reporting
Please **don't open a public issue**. Use GitHub's private vulnerability reporting (*Security → Report a vulnerability*). We'll acknowledge within 5 working days and agree a fix and disclosure date with you.

## Supported versions
Only the latest minor version of the spec and the latest release of `open-semantic-agent` get fixes.
