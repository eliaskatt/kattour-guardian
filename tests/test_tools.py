"""Smoke/regression tests using only Python's standard library."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SECURITY = ROOT / 'skills/kattour-guardian/scripts/security_scan.py'
A11Y = ROOT / 'skills/kattour-guardian/scripts/html_a11y.py'
VALIDATOR = ROOT / 'scripts/validate.py'


def invoke(script, *args):
    return subprocess.run([sys.executable, str(script), *map(str, args)],
                          capture_output=True, text=True, check=False)


class ScannerTests(unittest.TestCase):
    def test_secrets_detected_but_values_not_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            value = 'AKIA' + 'A' * 16
            (Path(tmp) / 'app.py').write_text('key = "' + value + '"\n', encoding='utf-8')
            p = invoke(SECURITY, tmp, '--format', 'json')
            self.assertEqual(p.returncode, 1)
            self.assertNotIn(value, p.stdout)
            report = json.loads(p.stdout)
            self.assertEqual(report['findings'][0]['rule'], 'POSSIBLE_AWS_KEY')
            self.assertEqual(report['findings'][0]['line'], 1)

    def test_review_level_pattern_does_not_fail_high_gate(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'component.jsx').write_text('const x = dangerouslySet' + 'InnerHTML;\n', encoding='utf-8')
            p = invoke(SECURITY, tmp, '--format', 'json', '--fail-on', 'high')
            self.assertEqual(p.returncode, 0)
            self.assertEqual(json.loads(p.stdout)['findings'][0]['severity'], 'medium')

    def test_skips_node_modules(self):
        with tempfile.TemporaryDirectory() as tmp:
            deps = Path(tmp) / 'node_modules'
            deps.mkdir()
            (deps / 'bad.js').write_text('key="' + 'AKIA' + 'B' * 16 + '"', encoding='utf-8')
            p = invoke(SECURITY, tmp, '--format', 'json')
            self.assertEqual(p.returncode, 0)
            self.assertEqual(json.loads(p.stdout)['files_inspected'], 0)

    def test_tls_verification_disabled_detected(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'client.py').write_text('requests.get(url, ' + 'verify' + '=False)', encoding='utf-8')
            p = invoke(SECURITY, tmp, '--format', 'json')
            self.assertEqual(p.returncode, 1)
            self.assertEqual(json.loads(p.stdout)['findings'][0]['rule'], 'TLS_VERIFICATION_DISABLED')

    def test_no_finding_is_not_a_certification(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'main.py').write_text('print("hello")', encoding='utf-8')
            p = invoke(SECURITY, tmp, '--format', 'json')
            self.assertEqual(p.returncode, 0)
            self.assertIn('does not mean secure', json.loads(p.stdout)['disclaimer'])

    def test_invalid_directory_returns_error(self):
        p = invoke(SECURITY, '/does-not-exist-kattour-guardian')
        self.assertNotEqual(p.returncode, 0)

    def test_html_checks(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / 'index.html').write_text('<html><head></head><body><img src="a.png"></body></html>', encoding='utf-8')
            p = invoke(A11Y, tmp, '--format', 'json')
            self.assertEqual(p.returncode, 0)
            rules = {x['rule'] for x in json.loads(p.stdout)['findings']}
            self.assertEqual(rules, {'IMG_ALT_MISSING', 'HTML_LANG_MISSING', 'VIEWPORT_META_MISSING'})

    def test_frontmatter_and_links_validate(self):
        p = invoke(VALIDATOR)
        self.assertEqual(p.returncode, 0, p.stdout + p.stderr)


if __name__ == '__main__':
    unittest.main()
