"""Portable skill and genuine local MCP transport smoke checks."""
import tempfile
import unittest
from pathlib import Path
from scripts import compatibility_smoke as smoke

ROOT = Path(__file__).resolve().parents[1]

class CompatibilitySmokeTests(unittest.TestCase):
    def test_installable_layouts_and_versions(self):
        result = smoke.package_check(ROOT)
        self.assertEqual(result["version"], "1.0.0")
        self.assertEqual(len(result["filesystem_layouts"]), 5)

    def test_real_local_mcp_process(self):
        result = smoke.mcp_check(ROOT)
        self.assertGreaterEqual(result["tools"], 9)
        self.assertTrue(result["path_traversal_rejected"])

    def test_missing_repository_files_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaisesRegex(ValueError, "Missing required"):
                smoke.package_check(Path(temp))

    def test_malformed_skill_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            (folder / "SKILL.md").write_text("---\nname: wrong\n---\nbody",encoding="utf-8")
            with self.assertRaises(ValueError):
                smoke.inspect_skill(folder)

if __name__ == "__main__":
    unittest.main()
