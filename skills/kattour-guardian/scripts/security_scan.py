#!/usr/bin/env python3
"""Offline, deliberately limited heuristic scanner. Not a security certification."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

SKIP_DIRS = {
    '.git', '.next', '.nuxt', '.output', '.turbo', '.venv', 'venv', 'node_modules',
    'vendor', 'dist', 'build', 'coverage', '__pycache__', '.idea', '.gradle',
    'Pods', 'DerivedData', 'target', '.cache', '.pytest_cache',
}
EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.php', '.rb', '.go',
    '.rs', '.java', '.kt', '.swift', '.dart', '.vue', '.svelte', '.html',
    '.yml', '.yaml', '.json', '.toml', '.ini', '.conf', '.sh', '.bash', '.sql',
    '.env', '.properties',
}
EXTRA_FILENAMES = {'Dockerfile', '.env', '.env.local', '.env.production', '.env.staging'}
SEVERITY = {'info': 0, 'low': 1, 'medium': 2, 'high': 3, 'critical': 4}

# These signatures are intentionally narrow. Each match is a *lead*, not proof.
RULES = [
    ('POSSIBLE_AWS_KEY', 'high', 'Possible AWS access key in source', r'\bAKIA[0-9A-Z]{16}\b'),
    ('POSSIBLE_GITHUB_TOKEN', 'high', 'Possible GitHub classic token in source', r'\bghp_[A-Za-z0-9]{36}\b'),
    ('POSSIBLE_STRIPE_LIVE_KEY', 'high', 'Possible Stripe live secret key in source', r'\bsk_live_[A-Za-z0-9]{16,}\b'),
    ('PRIVATE_KEY_HEADER', 'high', 'PEM private-key header present', r'-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----'),
    ('TLS_VERIFICATION_DISABLED', 'high', 'TLS certificate validation may be disabled', r'\bverify\s*=\s*False\b|\brejectUnauthorized\s*:\s*false\b'),
    ('SUBPROCESS_SHELL', 'medium', 'Shell invocation needs input-trust review', r'\bsubprocess\.(?:run|call|Popen|check_output|check_call)\s*\([^\n]*\bshell\s*=\s*True\b'),
    ('REACT_RAW_HTML', 'medium', 'Unescaped HTML rendering needs provenance review', r'\bdangerouslySetInnerHTML\b'),
    ('WEB_STORAGE_TOKEN', 'medium', 'Potential token stored in web storage', r'\blocalStorage\.setItem\s*\(\s*[\'\"](?:access_token|refresh_token|auth_token|jwt|token)[\'\"]'),
    ('DJANGO_CSRF_EXEMPT', 'medium', 'CSRF exemption needs endpoint review', r'\bcsrf_exempt\b'),
    ('PYTHON_DEBUG_ON', 'medium', 'Debug mode assignment needs environment review', r'^\s*DEBUG\s*=\s*True\b'),
]
COMPILED = [(name, level, message, re.compile(regex, re.IGNORECASE)) for name, level, message, regex in RULES]


def scan(root: Path, max_bytes: int = 1024 * 1024) -> dict:
    findings = []
    inspected = 0
    skipped = 0
    unreadable = []
    root = root.resolve()
    paths = [root] if root.is_file() else sorted(root.rglob('*'))
    for path in paths:
        if path.is_symlink() or not path.is_file():
            continue
        rel = path.relative_to(root) if root.is_dir() else Path(path.name)
        if any(part in SKIP_DIRS for part in rel.parts[:-1]):
            continue
        if path.name.endswith(('.min.js', '.min.css', '.map', '.lock')):
            continue
        if path.suffix.lower() not in EXTENSIONS and path.name not in EXTRA_FILENAMES:
            continue
        try:
            if path.stat().st_size > max_bytes:
                skipped += 1
                continue
            source = path.read_text(encoding='utf-8', errors='replace')
        except (OSError, UnicodeError):
            unreadable.append(str(rel))
            continue
        inspected += 1
        for lineno, line in enumerate(source.splitlines(), start=1):
            for rule, level, description, regex in COMPILED:
                if regex.search(line):
                    findings.append({
                        'rule': rule,
                        'severity': level,
                        'path': rel.as_posix(),
                        'line': lineno,
                        'message': description,
                        'status': 'unverified',
                    })
    findings.sort(key=lambda f: (-SEVERITY[f['severity']], f['path'], f['line'], f['rule']))
    return {
        'tool': 'Kattour Guardian offline heuristic security scan',
        'disclaimer': 'Findings require verification. No findings does not mean secure.',
        'files_inspected': inspected,
        'files_skipped_size': skipped,
        'unreadable_files': unreadable,
        'findings': findings,
    }


def as_markdown(result: dict) -> str:
    out = [
        '# Kattour Guardian — heuristic security scan', '',
        f"Files inspected: {result['files_inspected']}; size-skipped: {result['files_skipped_size']}; unreadable: {len(result['unreadable_files'])}",
        '', '**Not a security certification. Every match needs review.**', '',
        '| Severity | Rule | Location | Observation |',
        '| --- | --- | --- | --- |',
    ]
    for item in result['findings']:
        loc = f"{item['path']}:{item['line']}".replace('|', '\\|')
        out.append(f"| {item['severity'].upper()} | {item['rule']} | `{loc}` | {item['message']} |")
    if not result['findings']:
        out.append('| — | — | — | No heuristic matches; deeper verification is still required. |')
    if result['unreadable_files']:
        out.extend(['', 'Unreadable files: ' + ', '.join(result['unreadable_files'][:20])])
    return '\n'.join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='?', default='.', help='Path to authorized local source')
    parser.add_argument('--format', choices=['markdown', 'json'], default='markdown')
    parser.add_argument('--fail-on', choices=['none', 'low', 'medium', 'high', 'critical'], default='high')
    parser.add_argument('--max-file-kib', type=int, default=1024)
    args = parser.parse_args()
    root = Path(args.path)
    if not root.exists() or args.max_file_kib < 1:
        parser.error('An existing path and a positive file-size limit are required')
    report = scan(root, args.max_file_kib * 1024)
    print(json.dumps(report, indent=2, ensure_ascii=False) if args.format == 'json' else as_markdown(report))
    if args.fail_on != 'none' and any(SEVERITY[f['severity']] >= SEVERITY[args.fail_on] for f in report['findings']):
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
