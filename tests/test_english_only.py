"""Enforce English-only repository source and documentation.

Checks Unicode Arabic script ranges, not arbitrary non-ASCII symbols or the
legitimate accessibility support for international user interfaces.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCAN_EXTENSIONS = {".md", ".py", ".yml", ".yaml", ".toml", ".txt", ".json"}
IGNORE_DIRS = {".git", ".venv", "venv", "__pycache__", ".guardian-cache",
               ".kattour-cache", ".mypy_cache", ".pytest_cache", "node_modules"}


class EnglishOnlyRepositoryTests(unittest.TestCase):
    def test_no_localized_readme(self):
        self.assertFalse((ROOT / "README.ar.md").exists())
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertNotIn("README.ar.md", readme)
        self.assertNotIn("git init", readme)

    def test_no_arabic_script_in_source_or_docs(self):
        unexpected = []
        for file in ROOT.rglob("*"):
            if not file.is_file() or set(file.relative_to(ROOT).parts) & IGNORE_DIRS:
                continue
            if file.suffix not in SCAN_EXTENSIONS:
                continue
            try:
                source = file.read_text(encoding="utf-8")
            except UnicodeError:
                continue
            if any(0x0600 <= ord(char) <= 0x06FF for char in source):
                unexpected.append(str(file.relative_to(ROOT)))
        self.assertEqual(unexpected, [], f"Unexpected non-English script: {unexpected}")

    def test_no_temporary_import_assets(self):
        self.assertFalse((ROOT / ".import").exists())
        self.assertFalse((ROOT / ".github/workflows/import-v04.yml").exists())


if __name__ == "__main__":
    unittest.main()
