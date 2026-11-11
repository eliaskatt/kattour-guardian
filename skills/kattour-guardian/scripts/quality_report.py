#!/usr/bin/env python3
"""Offline quality triage built from bounded, unverified local static checks."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import security_scan
import html_a11y

PRIORITY = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'info': 4, 'review': 5}
NOT_TESTED = ['Dynamic authentication and authorization', 'Browser and keyboard workflows',
              'Dependency advisories and supply-chain provenance', 'Manual penetration testing',
              'App-specific business logic, privacy and performance']


def review(root: Path, max_findings: int = 30) -> dict:
    if type(max_findings) is not int or not 1 <= max_findings <= 100:
        raise ValueError('max_findings must be from 1 to 100')
    root = root.resolve()
    if not root.exists():
        raise ValueError('Project path not found')
    sec = security_scan.scan(root)
    a11y = html_a11y.run(root)
    findings = [dict(f, domain='security', confidence='unverified') for f in sec['findings']]
    findings += [dict(f, domain='accessibility', confidence='unverified') for f in a11y['findings']]
    findings.sort(key=lambda f: (PRIORITY.get(f['severity'], 9), f['path'], f['line']))
    return {
        'schema': 'kattour-guardian-quality-v1', 'version': '0.5.0',
        'status': 'review_high_priority' if any(f['severity'] in ('critical', 'high') for f in findings) else 'manual_verification_required',
        'summary': {'security_files': sec['files_inspected'], 'html_files': a11y['files_inspected'],
                    'security_skipped_large': sec['files_skipped_size'], 'security_unreadable': len(sec['unreadable_files']),
                    'security_findings': len(sec['findings']), 'a11y_findings': len(a11y['findings']),
                    'total_findings': len(findings), 'returned_findings': min(len(findings), max_findings),
                    'truncated': len(findings) > max_findings},
        'findings': findings[:max_findings], 'not_tested': NOT_TESTED,
        'disclaimer': 'Heuristics are unverified leads, not a security or accessibility certificate. A clean result cannot prove safety.'}


def markdown(result: dict) -> str:
    s = result['summary']
    lines = ['# Kattour Guardian quality triage', '',
             f"Status: **{result['status']}**",
             f"Security: {s['security_findings']} leads / {s['security_files']} files; HTML accessibility: {s['a11y_findings']} leads / {s['html_files']} files.",
             f"Skipped large files: {s['security_skipped_large']}; unreadable: {s['security_unreadable']}.",
             f"Showing {s['returned_findings']} / {s['total_findings']} findings (truncated: {str(s['truncated']).lower()}).", '',
             '| Domain | Severity | Rule | Location | Observation |', '| --- | --- | --- | --- | --- |']
    for finding in result['findings']:
        fields = [finding['domain'], finding['severity'], finding['rule'],
                  f"{finding['path']}:{finding['line']}", finding['message']]
        lines.append('| ' + ' | '.join(str(v).replace('|', '\\|').replace('\n', ' ') for v in fields) + ' |')
    if not result['findings']:
        lines.append('| - | - | - | - | No heuristic findings. Manual verification still required. |')
    lines += ['', '## Not tested', ''] + [f'- {item}' for item in result['not_tested']]
    lines += ['', '**Caution:** ' + result['disclaimer']]
    return '\n'.join(lines)


def main():
    p = argparse.ArgumentParser(description='Offline source and HTML quality triage')
    p.add_argument('path', nargs='?', default='.')
    p.add_argument('--format', choices=('json', 'markdown'), default='markdown')
    p.add_argument('--max-findings', type=int, default=30)
    p.add_argument('--fail-on-high', action='store_true')
    args = p.parse_args()
    try:
        report = review(Path(args.path), args.max_findings)
    except ValueError as exc:
        p.error(str(exc))
    print(json.dumps(report, indent=2) if args.format == 'json' else markdown(report))
    raise SystemExit(1 if args.fail_on_high and report['status'] == 'review_high_priority' else 0)


if __name__ == '__main__':
    main()
