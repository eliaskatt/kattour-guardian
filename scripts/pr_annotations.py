#!/usr/bin/env python3
"""Turn redacted PR review findings into GitHub Actions check annotations.

No GitHub write token, API calls, source snippets or untrusted PR code execution.
"""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

MAX_BYTES = 1_000_000
RULE = re.compile(r'^KG-(?:SEC|UX)-[0-9]{3}$')
PATH = re.compile(r'^[A-Za-z0-9_.@/+-]{1,240}$')
SEVERITIES = {'high': 'error', 'medium': 'warning', 'low': 'notice'}


def path_ok(path: object) -> bool:
    return isinstance(path, str) and bool(PATH.fullmatch(path)) and not path.startswith(('/', './')) and '..' not in path.split('/') and '\\' not in path


def escape(value: str, property_value: bool = False) -> str:
    value = value.replace('%', '%25').replace('\r', '%0D').replace('\n', '%0A')
    if property_value:
        value = value.replace(':', '%3A').replace(',', '%2C')
    return value


def render(data: object, limit: int = 30) -> tuple[list[str], dict]:
    if type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError('Annotation limit must be 1..100')
    if not isinstance(data, dict) or not isinstance(data.get('findings'), list):
        raise ValueError('Expected PR review result with findings array')
    output = []
    ignored = 0
    for finding in data['findings'][:500]:
        if not isinstance(finding, dict):
            ignored += 1
            continue
        path = finding.get('path')
        line = finding.get('line')
        rule = finding.get('rule_id')
        severity = finding.get('severity')
        if not path_ok(path) or type(line) is not int or not 1 <= line <= 10_000_000 or not isinstance(rule, str) or not RULE.fullmatch(rule) or severity not in SEVERITIES:
            ignored += 1
            continue
        if len(output) >= limit:
            ignored += 1
            continue
        # Do not reproduce caller-supplied message/recommendation: could contain a secret or injection.
        title = f'Kattour Guardian {rule}'
        msg = f'Potential {severity} severity issue detected by a heuristic rule; inspect this line and review the full redacted job report.'
        output.append(f'::{SEVERITIES[severity]} file={escape(path, True)},line={line},title={escape(title, True)}::{escape(msg)}')
    return output, {'annotations_emitted': len(output), 'findings_skipped': ignored,
                    'note': 'Annotations are unverified heuristics; no source content is emitted.'}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--max-annotations', type=int, default=30)
    args = parser.parse_args(argv)
    try:
        if args.input.is_symlink() or not args.input.is_file() or args.input.stat().st_size > MAX_BYTES:
            raise ValueError('Expected a regular JSON report of 1 MB or less')
        data = json.loads(args.input.read_text(encoding='utf-8'))
        lines, stats = render(data, args.max_annotations)
    except (ValueError, OSError, UnicodeError, json.JSONDecodeError) as exc:
        print('Invalid report: ' + type(exc).__name__, file=sys.stderr)
        return 2
    for line in lines:
        print(line)
    print(f'Guardian annotations: {stats["annotations_emitted"]} emitted, {stats["findings_skipped"]} skipped', file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
