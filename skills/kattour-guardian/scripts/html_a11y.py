#!/usr/bin/env python3
"""Offline, basic HTML checks; does not evaluate rendered accessibility or UX."""
from __future__ import annotations

import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

SKIP_DIRS = {'.git', 'node_modules', '.next', 'dist', 'build', 'coverage', 'vendor', '.venv', 'venv'}


class PageInspector(HTMLParser):
    def __init__(self, filename: str) -> None:
        super().__init__(convert_charrefs=True)
        self.filename = filename
        self.findings: list[dict] = []
        self.has_html = False
        self.has_viewport = False
        self.had_head = False

    def add(self, rule: str, line: int, message: str) -> None:
        self.findings.append({'path': self.filename, 'line': line, 'rule': rule, 'severity': 'review', 'message': message})

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr = dict(attrs)
        line, _ = self.getpos()
        if tag == 'html':
            self.has_html = True
            if not (attr.get('lang') or '').strip():
                self.add('HTML_LANG_MISSING', line, 'Declare the document language on html')
        elif tag == 'img' and 'alt' not in attr:
            self.add('IMG_ALT_MISSING', line, 'Add meaningful alt text or alt="" for decorative images')
        elif tag == 'head':
            self.had_head = True
        elif tag == 'meta' and (attr.get('name') or '').lower() == 'viewport':
            self.has_viewport = True

    def finish(self) -> None:
        if self.has_html and self.had_head and not self.has_viewport:
            self.add('VIEWPORT_META_MISSING', 1, 'Review mobile viewport behavior')


def run(root: Path) -> dict:
    root = root.resolve()
    files = [root] if root.is_file() else sorted(root.rglob('*.html'))
    findings = []
    processed = 0
    for file in files:
        if file.is_symlink() or not file.is_file():
            continue
        rel = file.relative_to(root) if root.is_dir() else Path(file.name)
        if any(part in SKIP_DIRS for part in rel.parts[:-1]):
            continue
        try:
            if file.stat().st_size > 1_000_000:
                continue
            page = PageInspector(rel.as_posix())
            page.feed(file.read_text(encoding='utf-8', errors='replace'))
            page.finish()
            findings.extend(page.findings)
            processed += 1
        except (OSError, ValueError):
            continue
    return {
        'tool': 'Kattour Guardian basic static HTML review',
        'disclaimer': 'Partial HTML heuristics only. Browser, keyboard and assistive technology testing remain necessary.',
        'files_inspected': processed,
        'findings': findings,
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('path', nargs='?', default='.')
    p.add_argument('--format', choices=['markdown', 'json'], default='markdown')
    args = p.parse_args()
    path = Path(args.path)
    if not path.exists():
        p.error('Path does not exist')
    result = run(path)
    if args.format == 'json':
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        print('# Basic static HTML accessibility review\n')
        print(f"Files inspected: {result['files_inspected']}\n")
        print('**This is not a WCAG conformance evaluation.**\n')
        for item in result['findings']:
            print(f"- {item['path']}:{item['line']} — {item['rule']}: {item['message']}")
        if not result['findings']:
            print('No listed heuristic matches. Manual and rendered-browser testing still required.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
