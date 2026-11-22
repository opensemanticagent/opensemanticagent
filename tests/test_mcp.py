import io
import json
import unittest

from osa import mcp, spec


def rpc(method, params=None, mid=1):
    return mcp.handle({"jsonrpc": "2.0", "id": mid, "method": method, "params": params or {}})


def tool(tool_name, **args):
    r = rpc("tools/call", {"name": tool_name, "arguments": args})["result"]
    return r


class McpTest(unittest.TestCase):
    def test_initialize_and_list(self):
        r = rpc("initialize", {"protocolVersion": "2025-06-18"})["result"]
        self.assertEqual(r["serverInfo"]["name"], "open-semantic-agent")
        tools = rpc("tools/list")["result"]["tools"]
        self.assertEqual(len(tools), 7)
        for t in tools:  # MCP directories require all four hints as booleans
            for h in ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint"):
                self.assertIsInstance(t["annotations"][h], bool, (t["name"], h))
            self.assertTrue(t["annotations"]["readOnlyHint"])

    def test_sections(self):
        ids = [s["id"] for s in tool("osa_list_sections")["structuredContent"]["sections"]]
        self.assertTrue({"1", "3", "6.3", "9.3", "A", "A.2"} <= set(ids), ids)
        s = tool("osa_get_section", section="§6.3")["structuredContent"]
        self.assertIn("Semantic dedupe", s["title"])
        self.assertEqual(tool("osa_get_section", section="dedupe")["structuredContent"]["id"], "6.3")
        whole = tool("osa_get_section", section="6")["structuredContent"]["text"]
        self.assertIn("### 6.8", whole)  # a top-level section includes its subsections
        self.assertTrue(tool("osa_get_section", section="nope-nothing")["isError"])

    def test_search(self):
        hits = tool("osa_search_spec", query="budget_tokens_per_hour")["structuredContent"]["matches"]
        self.assertTrue(hits and all(h["section"] for h in hits))

    def test_schemas_and_validation(self):
        self.assertIn("opensemanticagent.org", tool("osa_get_schema", name="envelope")["structuredContent"]["$id"])
        good = {"spec": "osa/0.3", "id": "e1", "source": "app://x", "time": "2026-11-21T10:00:00Z",
                "topic": "orders.placed", "data": {"n": 1}}
        self.assertTrue(tool("osa_validate", kind="envelope", document=good)["structuredContent"]["valid"])
        bad = tool("osa_validate", kind="envelope", document={"spec": "nope", "data": {}})["structuredContent"]
        self.assertFalse(bad["valid"])
        self.assertTrue(any("required" in e["message"] for e in bad["errors"]))
        self.assertTrue(tool("osa_validate", kind="unknown", document={})["isError"])

    def test_every_fixture_subscription_is_a_valid_manifest(self):
        names = [f["name"] for f in tool("osa_list_fixtures")["structuredContent"]["fixtures"]]
        self.assertIn("routing_v1", names)
        for n in names:
            for sub in tool("osa_get_fixture", name=n)["structuredContent"].get("subscriptions", []):
                r = spec.validate("subscription", sub)
                self.assertTrue(r["valid"], (n, sub.get("subscriber"), r["errors"]))

    def test_v0_3_schema_cases(self):
        fx = tool("osa_get_fixture", name="envelopes_v0_3")["structuredContent"]
        self.assertGreaterEqual(len(fx["cases"]), 16)
        for c in fx["cases"]:
            r = tool("osa_validate", kind=c["schema"], document=c["document"])["structuredContent"]
            self.assertEqual(r["valid"], c["valid"], (c["name"], r["errors"]))
        for h in fx["handling"]:  # handling cases must at least be valid envelopes
            self.assertTrue(spec.validate("envelope", h["envelope"])["valid"], h["name"])

    def test_v0_3_sections_and_schemas(self):
        ids = [s["id"] for s in tool("osa_list_sections")["structuredContent"]["sections"]]
        self.assertTrue({"6.9", "6.10", "B"} <= set(ids), ids)
        self.assertIn("Alerts", tool("osa_get_section", section="6.10")["structuredContent"]["title"])
        for k in ("metrics", "alert"):
            self.assertIn(k, tool("osa_get_schema", name=k)["structuredContent"]["$id"])

    def test_stdio(self):
        out = io.StringIO()
        mcp.serve(io.StringIO('{"jsonrpc":"2.0","id":1,"method":"ping"}\nnot json\n'), out)
        lines = [json.loads(x) for x in out.getvalue().splitlines()]
        self.assertEqual(lines[0]["result"], {})
        self.assertEqual(lines[1]["error"]["code"], -32700)


if __name__ == "__main__":
    unittest.main()
