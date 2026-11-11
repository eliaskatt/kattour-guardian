#!/usr/bin/env python3
"""Opt-in, local-only rendered UI audit with Playwright. Python 3.10+.

Heuristic observations, not visual AI analysis or WCAG certification.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit

VIEWPORTS = (("mobile", 390, 844), ("desktop", 1440, 900))
LOOPBACK = {"127.0.0.1", "::1", "localhost"}

# Return categories and counts, never page content, form values or element text.
DOM_PROBE = r"""() => {
  const visible = el => {
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none';
  };
  const named = el => Boolean(
    (el.getAttribute('aria-label') || '').trim() ||
    (el.getAttribute('aria-labelledby') || '').trim() ||
    (el.getAttribute('title') || '').trim() ||
    (el.getAttribute('alt') || '').trim() ||
    (el.labels && [...el.labels].some(label => (label.textContent || '').trim())) ||
    ((el.tagName === 'BUTTON' || el.tagName === 'A') && (el.textContent || '').trim()) ||
    (el.querySelector && el.querySelector('img[alt]:not([alt=""])'))
  );
  const selectors = [
    ['image_alt_missing', 'img:not([alt])'],
    ['input_name_missing', 'input:not([type="hidden"]),textarea,select'],
    ['button_name_missing', 'button'],
    ['link_name_missing', 'a[href]'],
    ['broken_image', 'img']
  ];
  const counts = {};
  for (const [kind, selector] of selectors) {
    counts[kind] = [...document.querySelectorAll(selector)].filter(el => {
      if (!visible(el)) return false;
      if (kind === 'image_alt_missing') return true;
      if (kind === 'broken_image') return el.complete && el.naturalWidth === 0;
      return !named(el);
    }).length;
  }
  const smallTargets = [...document.querySelectorAll('button,a[href],input:not([type="hidden"]),select')]
    .filter(visible).filter(el => {const r=el.getBoundingClientRect(); return r.width < 24 || r.height < 24;}).length;
  return {
    title_missing: !Boolean(document.title.trim()),
    lang_missing: !Boolean((document.documentElement.lang || '').trim()),
    viewport_meta_missing: !Boolean(document.querySelector('meta[name="viewport"]')),
    h1_missing: !Boolean(document.querySelector('h1')),
    horizontal_overflow_px: Math.max(0, Math.round(document.documentElement.scrollWidth - window.innerWidth)),
    small_target_count: smallTargets,
    counts
  };
}"""


def validate_target(url: str) -> str:
    if not isinstance(url, str) or len(url) > 500:
        raise ValueError('URL must be a string no longer than 500 characters')
    parsed = urlsplit(url)
    if (parsed.scheme != 'http' or parsed.hostname not in LOOPBACK or
            parsed.username is not None or parsed.password is not None or
            not parsed.netloc or parsed.fragment):
        raise ValueError('Only local HTTP loopback targets without credentials or fragments are allowed')
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError('Invalid local port') from exc
    if port is not None and not 1 <= port <= 65535:
        raise ValueError('Invalid local port')
    return url


def is_local_request(url: str, target: str | None = None) -> bool:
    parsed = urlsplit(url)
    if parsed.scheme in ('data', 'blob', 'about'):
        return True
    if parsed.scheme != 'http' or parsed.hostname not in LOOPBACK:
        return False
    if target is None:
        return True
    origin = urlsplit(validate_target(target))
    return (parsed.hostname == origin.hostname and parsed.port == origin.port)


def findings_from_signals(signals: dict, viewport: str) -> list[dict]:
    findings = []
    checks = [
        ('title_missing', 'missing_document_title', 'medium', 'Document title is missing'),
        ('lang_missing', 'missing_document_language', 'medium', 'HTML lang attribute is missing'),
        ('viewport_meta_missing', 'missing_viewport_meta', 'medium', 'Viewport meta tag is missing'),
        ('h1_missing', 'missing_primary_heading', 'review', 'No H1 was found'),
    ]
    for field, rule, severity, description in checks:
        if signals.get(field):
            findings.append({'viewport': viewport, 'rule': rule, 'severity': severity,
                             'count': 1, 'detail': description})
    overflow = max(0, int(signals.get('horizontal_overflow_px') or 0))
    if overflow > 2:
        findings.append({'viewport': viewport, 'rule': 'horizontal_overflow',
                         'severity': 'medium', 'count': 1, 'pixels': overflow,
                         'detail': 'Page content exceeds viewport width'})
    checks = {
        'image_alt_missing': ('image_alt_missing', 'medium', 'Visible images without alt attributes'),
        'input_name_missing': ('input_name_missing', 'medium', 'Visible form controls without accessible labels'),
        'button_name_missing': ('button_name_missing', 'medium', 'Visible buttons without accessible names'),
        'link_name_missing': ('link_name_missing', 'medium', 'Visible links without accessible names'),
        'broken_image': ('broken_image', 'review', 'Image did not load'),
    }
    for field, (rule, severity, description) in checks.items():
        count = max(0, int(signals.get('counts', {}).get(field) or 0))
        if count:
            findings.append({'viewport': viewport, 'rule': rule, 'severity': severity,
                             'count': count, 'detail': description})
    small = max(0, int(signals.get('small_target_count') or 0))
    if viewport == 'mobile' and small:
        findings.append({'viewport': viewport, 'rule': 'small_pointer_target', 'severity': 'review',
                         'count': small, 'detail': 'Targets below 24 CSS pixels; manually review applicable exceptions'})
    return findings


def run_audit(url: str, max_findings: int = 40,
              screenshot_dir: Path | None = None,
              chromium_executable: str | None = None) -> dict:
    validate_target(url)
    if type(max_findings) is not int or not 1 <= max_findings <= 100:
        raise ValueError('max_findings must be an integer between 1 and 100')
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:
        raise RuntimeError('Install optional browser tooling with: pip install playwright && playwright install chromium') from exc
    if screenshot_dir is not None:
        screenshot_dir = Path(screenshot_dir)
        screenshot_dir.mkdir(parents=True, exist_ok=True)
    findings, viewports = [], {}
    blocked_requests = 0
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, executable_path=chromium_executable)
        try:
            for name, width, height in VIEWPORTS:
                context = browser.new_context(viewport={'width': width, 'height': height},
                                              reduced_motion='reduce', service_workers='block')
                try:
                    page = context.new_page()
                    def guard(route):
                        nonlocal blocked_requests
                        if is_local_request(route.request.url, url):
                            route.continue_()
                        else:
                            blocked_requests += 1
                            route.abort()
                    page.route('**/*', guard)
                    try:
                        response = page.goto(url, wait_until='domcontentloaded', timeout=15000)
                        page.wait_for_timeout(200)
                        signals = page.evaluate(DOM_PROBE)
                        if screenshot_dir is not None:
                            page.screenshot(path=str(screenshot_dir / f'guardian-{name}.png'),
                                            full_page=True, animations='disabled', timeout=10000)
                    except Exception as exc:
                        raise RuntimeError(f'Browser audit failed for {name}; verify the local app is running') from exc
                    findings.extend(findings_from_signals(signals, name))
                    viewports[name] = {'width': width, 'height': height,
                                       'http_status': response.status if response else None,
                                       'horizontal_overflow_px': signals.get('horizontal_overflow_px', 0)}
                finally:
                    context.close()
        finally:
            browser.close()
    return {
        'version': '0.4.0', 'target_kind': 'local_http', 'viewports': viewports,
        'blocked_external_http_requests': blocked_requests,
        'total_findings': len(findings), 'findings_truncated': len(findings) > max_findings,
        'findings': findings[:max_findings],
        'limitations': 'Rendered DOM heuristics only, not a visual design score or complete accessibility audit. Browser routing is not a network sandbox. No page content is returned.'
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Review a running, authorized localhost app using Playwright')
    parser.add_argument('url', help='http://127.0.0.1:3000/')
    parser.add_argument('--max-findings', type=int, default=40)
    parser.add_argument('--screenshot-dir', type=Path, help='Opt-in screenshots; may contain private information')
    parser.add_argument('--chromium-executable')
    args = parser.parse_args()
    try:
        print(json.dumps(run_audit(args.url, args.max_findings,
                                   args.screenshot_dir, args.chromium_executable), indent=2))
    except (RuntimeError, ValueError) as exc:
        parser.exit(2, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
