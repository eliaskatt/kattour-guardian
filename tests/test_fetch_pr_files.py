"""Fail fast on invalid PR retrieval input, without any network activity."""
import importlib.util
from pathlib import Path
import unittest

SRC = Path(__file__).resolve().parents[1] / "scripts" / "fetch_pr_files.py"
spec = importlib.util.spec_from_file_location("fetch_pr_files", SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class FetchTests(unittest.TestCase):
    def test_invalid_repo(self):
        for name in ("../repo", "owner/repo/extra", "https://github.com/o/r"):
            with self.assertRaises(ValueError): mod.get_files(name, 1, "dummy")

    def test_invalid_number(self):
        with self.assertRaises(ValueError): mod.get_files("owner/repo", 0, "dummy")

    def test_missing_token(self):
        with self.assertRaises(ValueError): mod.get_files("owner/repo", 10, "")

if __name__ == "__main__":
    unittest.main()
