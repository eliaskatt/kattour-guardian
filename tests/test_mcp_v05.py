"""Regression coverage for v0.5 MCP provider counters and quality triage."""
import json
import tempfile
import unittest
from pathlib import Path
from mcp_server import Guardian, TOOLS, VERSION

class GuardianV05Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.guardian = Guardian(Path(self.temp.name))

    def test_version_and_tools(self):
        names = {tool["name"] for tool in TOOLS}
        self.assertEqual(VERSION, "0.5.0")
        self.assertIn("guardian_provider_usage", names)
        self.assertIn("guardian_quality_report", names)

    def test_usage_counts(self):
        report = json.loads(self.guardian.call("guardian_provider_usage", {
            "provider": "openai", "usage": {
                "input_tokens": 100, "output_tokens": 20,
                "input_tokens_details": {"cached_tokens": 50}}}))
        self.assertEqual(report["total_tokens"], 120)
        self.assertEqual(report["cached_input_tokens"], 50)

    def test_reject_messages(self):
        with self.assertRaises(ValueError):
            self.guardian.call("guardian_provider_usage", {
                "provider": "openai", "usage": {
                    "input_tokens": 10, "output_tokens": 2, "messages": ["private text"]}})

    def test_quality_stays_within_scope(self):
        result = json.loads(self.guardian.call("guardian_quality_report", {"max_findings": 1}))
        self.assertIn("not_tested", result)
        self.assertEqual(result["summary"]["total_findings"], 0)
        with self.assertRaises(ValueError):
            self.guardian.call("guardian_quality_report", {"path": "../other"})

if __name__ == "__main__":
    unittest.main()
