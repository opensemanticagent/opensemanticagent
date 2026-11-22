"""MCP server (stdio, JSON-RPC 2.0) for the Open Semantic Agent spec.

It lets an MCP client read the spec, fetch the JSON Schemas and conformance fixtures, and check documents
(envelopes, subscription manifests, audit records, stream messages) against the schemas.
Every tool is read-only: nothing is written, nothing leaves the machine.

Run: uvx open-semantic-agent   (or: python -m osa.mcp)
"""
from __future__ import annotations

import json
import sys

from . import SPEC_VERSION, __version__, spec

PROTOCOL_VERSIONS = ["2025-06-18", "2025-03-26", "2024-11-05"]
_KINDS = {"type": "string", "enum": list(spec.SCHEMA_NAMES)}

TOOLS = [
    {"name": "osa_list_sections",
     "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
     "description": "List the sections of the OSA specification with their ids (for example 6.3 or A.2) and titles.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "osa_get_section",
     "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
     "description": "Return the text of one spec section, by id (\"6.3\", \"§9.3\", \"A.1\") or by a word from its title.",
     "inputSchema": {"type": "object", "required": ["section"], "properties": {"section": {"type": "string"}}}},
    {"name": "osa_search_spec",
     "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
     "description": "Find lines in the spec that contain a phrase, with the section each one is in.",
     "inputSchema": {"type": "object", "required": ["query"],
                     "properties": {"query": {"type": "string"},
                                    "limit": {"type": "integer", "minimum": 1, "maximum": 100}}}},
    {"name": "osa_get_schema",
     "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
     "description": "Return an OSA JSON Schema: envelope, subscription (manifest), audit (record), stream (messages), "
                    "metrics (data of a metrics envelope) or alert (data of an alert envelope).",
     "inputSchema": {"type": "object", "required": ["name"], "properties": {"name": _KINDS}}},
    {"name": "osa_validate",
     "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
     "description": "Check a JSON document against an OSA schema and list every error with its path.",
     "inputSchema": {"type": "object", "required": ["kind", "document"],
                     "properties": {"kind": _KINDS, "document": {"description": "The JSON document to check"}}}},
    {"name": "osa_list_fixtures",
     "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
     "description": "List the conformance fixtures (routing test vectors) with their size and purpose.",
     "inputSchema": {"type": "object", "properties": {}}},
    {"name": "osa_get_fixture",
     "annotations": {"readOnlyHint": True, "destructiveHint": False, "idempotentHint": True, "openWorldHint": False},
     "description": "Return one conformance fixture: its subscriptions and the expected decision for each case.",
     "inputSchema": {"type": "object", "required": ["name"], "properties": {"name": {"type": "string"}}}},
]


def call(name: str, a: dict):
    if name == "osa_list_sections":
        return {"spec": SPEC_VERSION, "sections": [{k: s[k] for k in ("id", "title", "level")} for s in spec.sections()]}
    if name == "osa_get_section":
        s = spec.get_section(str(a["section"]))
        return {"id": s["id"], "title": s["title"], "text": s["text"]}
    if name == "osa_search_spec":
        return {"matches": spec.search(str(a["query"]), int(a.get("limit", 20)))}
    if name == "osa_get_schema":
        return spec.schema(a["name"])
    if name == "osa_validate":
        return spec.validate(a["kind"], a["document"])
    if name == "osa_list_fixtures":
        return {"fixtures": spec.fixtures()}
    if name == "osa_get_fixture":
        return spec.fixture(str(a["name"]))
    raise KeyError(name)


def handle(msg: dict) -> dict | None:
    mid, method, params = msg.get("id"), msg.get("method"), msg.get("params") or {}
    is_note = "id" not in msg

    def ok(result):
        return None if is_note else {"jsonrpc": "2.0", "id": mid, "result": result}

    def err(code, message):
        return None if is_note else {"jsonrpc": "2.0", "id": mid, "error": {"code": code, "message": message}}

    if method == "initialize":
        want = params.get("protocolVersion")
        return ok({"protocolVersion": want if want in PROTOCOL_VERSIONS else PROTOCOL_VERSIONS[0],
                   "capabilities": {"tools": {"listChanged": False}},
                   "serverInfo": {"name": "open-semantic-agent", "version": __version__},
                   "instructions": f"Open Semantic Agent spec {SPEC_VERSION}: read the spec, get schemas and "
                                   "fixtures, and validate documents. All tools are read-only."})
    if method in ("notifications/initialized", "notifications/cancelled"):
        return None
    if method == "ping":
        return ok({})
    if method == "tools/list":
        return ok({"tools": TOOLS})
    if method == "tools/call":
        name, args = params.get("name"), params.get("arguments") or {}
        if name not in {t["name"] for t in TOOLS}:
            return err(-32602, f"unknown tool {name!r}")
        try:
            result = call(name, args)
        except (KeyError, ValueError, TypeError) as e:
            return ok({"content": [{"type": "text", "text": f"{type(e).__name__}: {e}"}], "isError": True})
        return ok({"content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False)}],
                   "structuredContent": result, "isError": False})
    return err(-32601, f"method not found: {method}")


def serve(stdin=sys.stdin, stdout=sys.stdout):
    for line in stdin:
        line = line.strip()
        if not line:
            continue
        try:
            msg = json.loads(line)
        except ValueError:
            resp = {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "parse error"}}
        else:
            batch = msg if isinstance(msg, list) else [msg]
            out = [r for r in (handle(m) if isinstance(m, dict) else
                               {"jsonrpc": "2.0", "id": None, "error": {"code": -32600, "message": "invalid request"}}
                               for m in batch) if r is not None]
            resp = (out if isinstance(msg, list) else out[0]) if out else None
        if resp is not None:
            stdout.write(json.dumps(resp, ensure_ascii=False) + "\n")
            stdout.flush()


def main(argv=None):
    import argparse
    p = argparse.ArgumentParser(prog="open-semantic-agent", description=__doc__.splitlines()[0])
    p.add_argument("--version", action="version", version=f"open-semantic-agent {__version__} (spec {SPEC_VERSION})")
    p.parse_args(argv)
    serve()


if __name__ == "__main__":
    main()
