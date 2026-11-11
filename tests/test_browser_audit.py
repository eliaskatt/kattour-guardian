"""Browser and token comparison tests; optional Chromium smoke test."""
import importlib.util
import json
import http.server
import shutil
import socketserver
import sys
import tempfile
import threading
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'skills' / 'kattour-guardian' / 'scripts'))
from browser_audit import validate_target, is_local_request, findings_from_signals, run_audit
from token_compare import compare


class TokenCompareTests(unittest.TestCase):
    def test_reduction(self):
        result = compare(1000, 200, 550, 150, 'provider_reported')
        self.assertEqual(result['difference_tokens'], 500)
        self.assertEqual(result['reduction_percent'], 41.67)
        self.assertIn('not independently verified', result['warning'])

    def test_increased_and_zero(self):
        self.assertIsNone(compare(0, 0, 0, 0)['reduction_percent'])
        self.assertEqual(compare(10, 0, 20, 0)['reduction_percent'], -100)
        for bad in (-1, True, 2.5, '4'):
            with self.assertRaises(ValueError):
                compare(bad, 1, 1, 1)

    def test_invalid_source(self):
        with self.assertRaises(ValueError):
            compare(1, 1, 1, 1, 'unverified')


class BrowserAuditTests(unittest.TestCase):
    def test_reject_unsafe_urls(self):
        for url in ('https://example.com', 'http://8.8.8.8/', 'file:///etc/passwd',
                    'http://169.254.169.254/', 'http://user:pass@localhost/',
                    'http://localhost:99999/', 'http://localhost/#fragment', '//localhost'):
            with self.subTest(url=url), self.assertRaises(ValueError):
                validate_target(url)
        self.assertEqual(validate_target('http://127.0.0.1:8888/page'),
                         'http://127.0.0.1:8888/page')

    def test_same_local_origin_only(self):
        target = 'http://127.0.0.1:3000/'
        self.assertTrue(is_local_request('http://127.0.0.1:3000/a', target))
        self.assertFalse(is_local_request('http://localhost:3000/a', target))
        self.assertFalse(is_local_request('http://127.0.0.1:3001/a', target))
        self.assertFalse(is_local_request('https://cdn.example.com/a', target))

    def test_rules_have_no_page_text(self):
        findings = findings_from_signals({
            'lang_missing': True, 'horizontal_overflow_px': 23,
            'counts': {'image_alt_missing': 2, 'button_name_missing': 1},
            'small_target_count': 4}, 'mobile')
        self.assertEqual([f['rule'] for f in findings], [
            'missing_document_language', 'horizontal_overflow',
            'image_alt_missing', 'button_name_missing', 'small_pointer_target'])
        self.assertNotIn('small_pointer_target', str(findings_from_signals(
            {'small_target_count': 4}, 'desktop')))

    def test_invalid_findings_limit(self):
        for bad in (0, 101, True):
            with self.assertRaises(ValueError):
                run_audit('http://127.0.0.1:3000/', bad)

    def test_rendered_dom_probe(self):
        if importlib.util.find_spec('playwright') is None:
            self.skipTest('Optional Playwright not installed')
        from playwright.sync_api import sync_playwright
        from browser_audit import DOM_PROBE
        executable = shutil.which('chromium') or shutil.which('google-chrome')
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(executable_path=executable)
            except Exception as exc:
                if "Executable doesn't exist" in str(exc):
                    self.skipTest('Chromium not installed')
                raise
            try:
                page = browser.new_page(viewport={'width': 390, 'height': 844})
                page.set_content('<html><head><title>Test</title></head><body><h1>Demo</h1>'
                                 '<button></button><img width="150" src="missing.png">'
                                 '<div style="width:1500px">Wide</div></body></html>')
                signals = page.evaluate(DOM_PROBE)
                self.assertTrue(signals['lang_missing'])
                self.assertEqual(signals['counts']['button_name_missing'], 1)
                self.assertEqual(signals['counts']['image_alt_missing'], 1)
                self.assertGreater(signals['horizontal_overflow_px'], 0)
            finally:
                browser.close()

    def test_local_chromium_smoke(self):
        if importlib.util.find_spec('playwright') is None:
            self.skipTest('Optional Playwright not installed')
        with tempfile.TemporaryDirectory() as folder:
            Path(folder, 'index.html').write_text(
                '<html><head><title>Test</title></head><body>'
                '<h1>Demo</h1><button></button><div style="width:1700px">Overflow</div>'
                '</body></html>', encoding='utf-8')
            class Handler(http.server.SimpleHTTPRequestHandler):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, directory=folder, **kwargs)
                def log_message(self, *args):
                    pass
            class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
                daemon_threads = True
            httpd = Server(('127.0.0.1', 0), Handler)
            thread = threading.Thread(target=httpd.serve_forever, daemon=True)
            thread.start()
            self.addCleanup(httpd.server_close)
            self.addCleanup(httpd.shutdown)
            try:
                result = run_audit(f'http://127.0.0.1:{httpd.server_port}/',
                                   max_findings=1,
                                   chromium_executable=shutil.which('chromium'))
            except Exception as exc:
                if 'Browser audit failed for mobile' in str(exc) and exc.__cause__ and 'ERR_BLOCKED_BY_ADMINISTRATOR' in str(exc.__cause__):
                    self.skipTest('Browser network sandbox prevents localhost navigation here')
                if "Executable doesn't exist" in str(exc):
                    self.skipTest('Chromium not installed')
                raise
            self.assertGreater(result['total_findings'], 1)
            self.assertTrue(result['findings_truncated'])
            self.assertEqual(len(result['findings']), 1)


if __name__ == '__main__':
    unittest.main()
