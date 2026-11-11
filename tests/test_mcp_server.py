"""Local MCP protocol, authorization, token-efficiency and scanner tests."""
from __future__ import annotations
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from mcp_server import Guardian, TOOLS

class MCPTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "src").mkdir()
        (self.root / "src/auth.py").write_text("def login(user):\n    return user\n")
        (self.root / "index.html").write_text('<html><head></head><body><img src="x"></body></html>')
        (self.root / ".env").write_text('password="SECRET_TEST_FIXTURE"')
        self.mcp = Guardian(self.root)

    def test_initialize_and_list(self):
        request = {"jsonrpc": "2.0", "id": 1, "method": "initialize",
                   "params": {"protocolVersion": "2025-11-25"}}
        self.assertEqual(self.mcp.handle(request)["result"]["protocolVersion"], "2025-11-25")
        response = self.mcp.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        self.assertEqual(len(response["result"]["tools"]), 7)
        for item in TOOLS:
            self.assertTrue(item["annotations"]["readOnlyHint"])

    def test_requires_initialize(self):
        response = self.mcp.handle({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
        self.assertEqual(response["error"]["code"], -32002)

    def test_map_budget_and_delta(self):
        first = self.mcp.call("guardian_context", {"task": "login", "max_chars": 500})
        second = self.mcp.call("guardian_context", {"task": "login", "max_chars": 500})
        self.assertIn("auth.py", first)
        self.assertLessEqual(len(first), 500)
        self.assertIn("unchanged omitted:", second)
        self.assertNotIn("SECRET_TEST_FIXTURE", first)
        self.assertGreater(self.mcp.usage["unchanged_files_omitted"], 0)

    def test_refresh_delta_on_change(self):
        self.mcp.call("guardian_context", {"task": "login"})
        (self.root / "src/auth.py").write_text("def login(user):\n    return user.lower()\n")
        self.assertIn("auth.py", self.mcp.call("guardian_context", {"task": "login"}))

    def test_security_scan_full_scope_even_if_result_capped(self):
        (self.root / "src/danger.py").write_text(("verify" + "=False\n") * 3)
        data = json.loads(self.mcp.call("guardian_security", {"max_findings": 1}))
        self.assertEqual(data["total_findings"], 3)
        self.assertEqual(len(data["findings"]), 1)
        self.assertTrue(data["findings_truncated"])

    def test_html_review(self):
        data = json.loads(self.mcp.call("guardian_a11y", {}))
        self.assertEqual(data["files_inspected"], 1)
        self.assertGreater(len(data["findings"]), 0)

    def test_log_best_effort_redaction(self):
        out = self.mcp.call("guardian_compact_log", {
            "log": "error failed\npassword=SECRETEXAMPLE\nwarning retry",
            "max_chars": 400})
        self.assertIn("error", out)
        self.assertNotIn("SECRETEXAMPLE", out)

    def test_path_and_symlink_restrictions(self):
        for path in ("../outside", "/etc/passwd"):
            with self.assertRaises(ValueError):
                self.mcp.path(path)
        (self.root / "link").symlink_to(self.root.parent, target_is_directory=True)
        with self.assertRaises(ValueError):
            self.mcp.path("link/elsewhere")

    def test_reject_unknown_and_invalid_arguments(self):
        with self.assertRaises(ValueError):
            self.mcp.call("guardian_context", {"task": "login", "max_chars": -10})
        with self.assertRaises(ValueError):
            self.mcp.call("guardian_context", {"task": "login", "reuse_unchanged": "yes"})
        with self.assertRaises(ValueError):
            self.mcp.call("guardian_usage", {"invalid": True})

    def test_browser_opt_in_origin_guard(self):
        from unittest.mock import patch
        with self.assertRaises(ValueError):
            self.mcp.call("guardian_browser", {"url": "http://127.0.0.1:3000/"})
        permitted = Guardian(self.root, browser_origin="http://127.0.0.1:3000")
        with self.assertRaises(ValueError):
            permitted.call("guardian_browser", {"url": "http://127.0.0.1:4000/"})
        with patch("mcp_server.browser_audit.run_audit", return_value={"findings": []}):
            data = json.loads(permitted.call("guardian_browser", {"url": "http://127.0.0.1:3000/"}))
            self.assertEqual(data["findings"], [])

    def test_supplied_token_comparison(self):
        data = json.loads(self.mcp.call("guardian_token_compare", {
            "before_input": 1000, "before_output": 200,
            "after_input": 600, "after_output": 200, "source": "provider_reported"}))
        self.assertEqual(data["difference_tokens"], 400)
        with self.assertRaises(ValueError):
            self.mcp.call("guardian_token_compare", {
                "before_input": -1, "before_output": 0, "after_input": 0, "after_output": 0})

    def test_usage_is_not_billing(self):
        self.mcp.call("guardian_context", {"task": "login"})
        data = json.loads(self.mcp.call("guardian_usage", {}))
        self.assertEqual(data["context_calls"], 1)
        self.assertIn("NOT provider API", data["warning"])

    def test_stdio_end_to_end(self):
        packets = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize",
             "params": {"protocolVersion": "2025-06-18"}},
            {"jsonrpc": "2.0", "method": "notifications/initialized"},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
            {"jsonrpc": "2.0", "id": 3, "method": "tools/call",
             "params": {"name": "guardian_context", "arguments": {"task": "auth"}}},
        ]
        run = subprocess.run(
            [sys.executable, str(ROOT / "mcp_server.py"), "--root", str(self.root)],
            input="\n".join(json.dumps(packet) for packet in packets) + "\n",
            text=True, capture_output=True, timeout=20)
        self.assertEqual(run.returncode, 0, run.stderr)
        messages = [json.loads(line) for line in run.stdout.splitlines()]
        self.assertEqual(len(messages), 3)
        self.assertEqual(messages[-1]["result"]["isError"], False)
        self.assertIn("auth.py", messages[-1]["result"]["content"][0]["text"])

if __name__ == "__main__":
    unittest.main()
