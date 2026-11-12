"""Optional offline Playwright smoke test using a document injected into Chromium.

Prerequisites: pip install playwright; an installed Chromium browser.
Run: python tests/browser-smoke.py [--chromium /usr/bin/chromium]
"""
from __future__ import annotations
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]

def run(executable: str | None) -> None:
    markup = (ROOT / 'playground.html').read_text(encoding='utf-8')
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True, executable_path=executable)
        try:
            page = browser.new_page(viewport={'width': 1500, 'height': 900}, accept_downloads=True)
            errors = []
            page.on('pageerror', lambda err: errors.append(str(err)))
            page.set_content(markup, wait_until='load')
            assert page.locator('#qaBadge').inner_text().startswith('READY')
            page.locator('[data-tab=files]').click()
            assert page.locator('.tree-row').count() >= 5
            page.locator('#saveBtn').click()
            page.locator('[data-view=sessions]').click()
            assert page.locator('#sessionList .library-card').count() == 1
            page.locator('#sessionList [data-open]').click()
            page.locator('#targetPlatform').select_option('iOS')
            page.locator('#projectType').select_option('API / backend')
            page.locator('#generateBtn').click()
            assert page.locator('#copyBtn').is_disabled()
            page.locator('#targetPlatform').select_option('Web')
            page.locator('#generateBtn').click()
            assert page.locator('#copyBtn').is_enabled()
            with page.expect_download() as download:
                page.locator('[data-export=json]').click()
            assert download.value.suggested_filename.endswith('.json')
            page.locator('#projectGoal').fill('Updated product brief that has not been regenerated.')
            assert page.locator('#copyBtn').is_disabled()
            mobile = browser.new_page(viewport={'width':390,'height':844})
            mobile.set_content(markup, wait_until='load')
            assert mobile.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
            assert not errors, errors
            print('PASS: browser navigation, saved sessions, quality guard, export, responsive layout')
        finally:
            browser.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--chromium')
    args = parser.parse_args()
    run(args.chromium)