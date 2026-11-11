#!/usr/bin/env python3
"""Reduce verbose local command logs to error-focused, redacted context."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ERROR = re.compile(r'\b(?:fatal|error|failed|failure|exception|traceback|assertionerror|typeerror|syntaxerror|segmentation fault|panic|error TS\d+|E\d{4})\b', re.I)
WARNING = re.compile(r'\b(?:warn|warning|deprecated)\b', re.I)
SECRET = re.compile(r'\b(?:password|secret|token|api[_-]?key|authorization)\s*[=:]\s*\S+|-----BEGIN [^-]*PRIVATE KEY-----|\b(?:ghp_|sk_live_)[A-Za-z0-9_]+', re.I)


def compact(content: str, max_chars: int = 3500, context: int = 1, tail: int = 8) -> tuple[str, dict]:
    lines = content.splitlines()
    errors = [i for i, line in enumerate(lines) if ERROR.search(line)]
    warnings = [i for i, line in enumerate(lines) if WARNING.search(line)]
    focus = errors or warnings
    selected: set[int] = set()
    for idx in focus[:60]:
        for j in range(max(0, idx - context), min(len(lines), idx + context + 1)):
            selected.add(j)
    if not errors and not warnings:
        selected.update(range(max(0, len(lines) - tail), len(lines)))
    header = f'# Compact local log\nOriginal lines: {len(lines)}; error lines: {len(errors)}; warning lines: {len(warnings)}\n\n'
    if len(header) > max_chars:
        raise ValueError('Character budget smaller than log summary')
    chunks = [header]
    total = len(header)
    included = 0
    for idx in sorted(selected):
        line = lines[idx].replace('\x1b', '').replace('\r', '')
        line = '[REDACTED: potential credential]' if SECRET.search(line) else line[:270]
        entry = f'L{idx + 1}: {line}\n'
        if total + len(entry) > max_chars:
            break
        chunks.append(entry)
        total += len(entry)
        included += 1
    if not selected:
        note = '(Empty log or no diagnostic lines.)\n'
        chunks.append(note[:max(0, max_chars - total)])
    metrics = {'original_lines': len(lines), 'included_lines': included,
               'output_characters': len(''.join(chunks)),
               'note': 'Selective diagnostic log; review omitted lines when a failure needs more context.'}
    return ''.join(chunks), metrics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('file', nargs='?', default='-', help='File path or - for stdin')
    parser.add_argument('--max-chars', type=int, default=3500)
    parser.add_argument('--context-lines', type=int, default=1)
    parser.add_argument('--tail-lines', type=int, default=8)
    parser.add_argument('--max-input-kib', type=int, default=4096)
    parser.add_argument('--metrics', action='store_true')
    args = parser.parse_args()
    if args.max_chars < 150 or args.context_lines < 0 or args.tail_lines < 0 or args.max_input_kib < 1:
        parser.error('Invalid limits')
    try:
        if args.file == '-':
            data = sys.stdin.buffer.read(args.max_input_kib * 1024 + 1)
        else:
            with Path(args.file).open('rb') as handle:
                data = handle.read(args.max_input_kib * 1024 + 1)
    except OSError as exc:
        parser.error(f'Cannot read log: {exc}')
    truncated = len(data) > args.max_input_kib * 1024
    content = data[:args.max_input_kib * 1024].decode('utf-8', errors='replace')
    try:
        result, metrics = compact(content, args.max_chars, args.context_lines, args.tail_lines)
    except ValueError as exc:
        parser.error(str(exc))
    print(result, end='')
    if args.metrics:
        metrics['input_truncated'] = truncated
        print(json.dumps(metrics), file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
