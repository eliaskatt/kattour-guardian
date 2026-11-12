"""Optional offline Chromium smoke for Guardian Playground advanced workflows.

Renders the standalone HTML in-memory because some execution environments
explicitly block browser loopback/HTTP connections. Share URL encoding is
covered by the offline Node unit tests.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

ROOT=Path(__file__).resolve().parents[1]
def run(chromium=None):
    markup=(ROOT/'index.html').read_text(encoding='utf-8')
    with sync_playwright() as pw:
        browser=pw.chromium.launch(headless=True,executable_path=chromium)
        try:
            page=browser.new_page(viewport={'width':1480,'height':900},accept_downloads=True)
            errors=[];page.on('pageerror',lambda err:errors.append(str(err)))
            page.set_content(markup,wait_until='load')
            assert page.locator('#qaBadge').inner_text().startswith('READY')
            page.locator('#workMode').select_option('Security review')
            page.locator('#targetAgent').select_option('Cursor')
            page.locator('#detailLevel').select_option('Thorough')
            page.locator('#generateBtn').click()
            assert 'Security review' in page.locator('#promptPreview').input_value()
            page.locator('[data-tab=acceptance]').click()
            assert page.locator('.acceptance-item').count()==7
            assert 'authorized' in page.locator('#tabContent').inner_text().lower()
            page.locator('#optimizeBtn').click()
            assert 'Cursor' in page.locator('#promptPreview').input_value()
            # Arrow-key tab navigation supports keyboard users.
            page.locator('[data-tab=acceptance]').focus()
            page.keyboard.press('Home')
            assert page.locator('[data-tab=plan]').get_attribute('aria-selected')=='true'
            page.keyboard.press('End')
            assert page.locator('[data-tab=acceptance]').get_attribute('aria-selected')=='true'
            with page.expect_download() as download:page.locator('[data-export=json]').click()
            contents=json.loads(Path(download.value.path()).read_text(encoding='utf-8'))
            assert contents['input']['mode']=='Security review'
            assert len(contents['acceptance_criteria'])==7
            page.locator('#newBtn').click()
            assert page.locator('#projectGoal').input_value()==''
            page.locator('#importFile').set_input_files({'name':'guardian.json','mimeType':'application/json','buffer':json.dumps(contents).encode('utf-8')})
            expect(page.locator('#workMode')).to_have_value('Security review',timeout=5000)
            expect(page.locator('#targetAgent')).to_have_value('Cursor',timeout=5000)
            expect(page.locator('#projectGoal')).to_have_value(contents['input']['goal'],timeout=5000)
            secret='ghp_'+'A'*36
            page.locator('#projectGoal').fill('Build a checkout application '+secret)
            page.locator('#generateBtn').click()
            assert page.locator('#copyBtn').is_disabled()
            assert secret not in page.locator('#promptPreview').input_value()
            assert not errors,errors
            mobile=browser.new_page(viewport={'width':390,'height':844})
            mobile.set_content(markup,wait_until='load')
            mobile.locator('#workMode').select_option('Fix a bug')
            mobile.locator('#generateBtn').click()
            mobile.locator('[data-tab=acceptance]').click()
            assert mobile.locator('.acceptance-item').count()==7
            assert mobile.evaluate('document.documentElement.scrollWidth <= innerWidth')
            print('PASS: advanced modes, acceptance, keyboard tabs, JSON round-trip, secret guard, mobile')
        finally:browser.close()
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--chromium');args=parser.parse_args();run(args.chromium)
