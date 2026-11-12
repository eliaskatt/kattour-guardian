"""Offline regression tests for Guardian PR reviewer."""
import importlib.util
from pathlib import Path
import unittest

SRC = Path(__file__).resolve().parents[1] / "scripts" / "pr_review.py"
spec = importlib.util.spec_from_file_location("pr_review", SRC)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class ReviewTests(unittest.TestCase):
    def test_secret_is_redacted(self):
        secret = "topsecret_topsecret_12345"
        got = mod.review([{"filename": "config.py", "patch": "@@ -0,0 +1 @@\n+api_key = '" + secret + "'\n"}])
        self.assertEqual(got["findings"][0]["rule_id"], "KG-SEC-001")
        self.assertNotIn(secret, str(got))
        self.assertNotIn(secret, mod.markdown(got))

    def test_only_added_lines(self):
        patch = "@@ -2,2 +2,2 @@\n-api_key = 'old_secret_value_123'\n+safe = True\n eval(user_input)\n"
        self.assertFalse(mod.review([{"filename": "a.py", "patch": patch}])["findings"])

    def test_added_line_numbers(self):
        patch = "@@ -40,2 +40,3 @@\n context\n+verify" + "=False\n+other=True\n"
        got = mod.review([{"filename": "api.py", "patch": patch}])
        self.assertEqual(got["findings"][0]["line"], 41)

    def test_missing_patch_is_partial(self):
        got = mod.review([{"filename": "binary.png"}])
        self.assertEqual(got["status"], "partial")
        self.assertEqual(got["counts"]["unreviewed_files"], 1)

    def test_detect_jsx_ux(self):
        patch = '@@ -0,0 +1,2 @@\n+<img src="x" />\n+<div onClick={go}>Go</div>\n'
        got = mod.review([{"filename": "view.tsx", "patch": patch}])
        self.assertEqual({x["rule_id"] for x in got["findings"]}, {"KG-UX-001", "KG-UX-002"})

    def test_controls_in_untrusted_filename(self):
        patch = "@@ -0,0 +1 @@\n+verify" + "=False\n"
        got = mod.review([{"filename": "x\n## Fake.md", "patch": patch}])
        self.assertNotIn("\n## Fake", mod.markdown(got))

    def test_removed_file_ignored(self):
        self.assertEqual(mod.review([{"filename": "a.py", "status": "removed"}])["counts"]["changed_files"], 0)

    def test_empty_diff_not_certified(self):
        self.assertIn("not a clean security bill", mod.markdown(mod.review([])))

    def test_too_many_files(self):
        with self.assertRaises(ValueError): mod.review([{}] * 501)

    def test_invalid_input(self):
        with self.assertRaises(ValueError): mod.review({})

    def test_budget_truncates(self):
        patch = "@@ -0,0 +1,200 @@\n" + ("+verify" + "=False\n") * 100
        out = mod.markdown(mod.review([{"filename": "api.py", "patch": patch}]), max_chars=700)
        self.assertLessEqual(len(out), 700)
        self.assertIn("truncated", out)

    def test_placeholder_ignored(self):
        patch = "@@ -0,0 +1 @@\n+api_key = 'placeholderlongvalue12345'\n"
        self.assertFalse(mod.review([{"filename": "c.py", "patch": patch}])["findings"])


if __name__ == "__main__":
    unittest.main()
