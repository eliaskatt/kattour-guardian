#!/usr/bin/env python3
"""Offline paired benchmark: compare provider token counters for equivalent tasks.

No network calls, price estimates or unverified claims of billed savings.
"""
from __future__ import annotations
import argparse
import json
import statistics
import sys
from pathlib import Path

MAX_BYTES = 2_000_000
MAX_PAIRS = 500
MAX_COUNT = 10 ** 12


def usage(record: dict) -> dict:
    if not isinstance(record, dict):
        raise ValueError('Each usage entry must be an object')
    for field in ('input_tokens', 'output_tokens'):
        value = record.get(field)
        if type(value) is not int or not 0 <= value <= MAX_COUNT:
            raise ValueError('Invalid token counter: ' + field)
    cached = record.get('cached_input_tokens', 0)
    if type(cached) is not int or not 0 <= cached <= record['input_tokens']:
        raise ValueError('Invalid cache counter')
    return {'input_tokens': record['input_tokens'], 'output_tokens': record['output_tokens'],
            'cached_input_tokens': cached, 'total_tokens': record['input_tokens'] + record['output_tokens']}


def benchmark(records: list, min_pairs: int = 3) -> dict:
    if type(min_pairs) is not int or not 1 <= min_pairs <= MAX_PAIRS:
        raise ValueError('Invalid minimum pair count')
    if not isinstance(records, list) or not 1 <= len(records) <= MAX_PAIRS:
        raise ValueError('Require 1..500 paired runs')
    valid, excluded, seen = [], [], set()
    for index, pair in enumerate(records):
        if not isinstance(pair, dict):
            raise ValueError('Run must be object')
        name = pair.get('task_id')
        if not isinstance(name, str) or not 1 <= len(name) <= 100 or name in seen:
            raise ValueError('Task IDs must be unique, non-empty strings')
        seen.add(name)
        if not isinstance(pair.get('model'), str) or not pair['model']:
            raise ValueError('Specify a matching model for both runs')
        for sample in ('before', 'after'):
            raw_usage = pair.get(sample)
            if isinstance(raw_usage, dict) and raw_usage.get('model', pair['model']) != pair['model']:
                raise ValueError('Before/after model identifiers must match')
        before, after = usage(pair.get('before')), usage(pair.get('after'))
        good_before = pair.get('quality_before_pass')
        good_after = pair.get('quality_after_pass')
        if type(good_before) is not bool or type(good_after) is not bool:
            raise ValueError('Both quality pass flags must be explicit booleans')
        if not (good_before and good_after):
            excluded.append({'task_id': name, 'reason': 'quality_gate_failed'})
            continue
        if before['total_tokens'] == 0:
            excluded.append({'task_id': name, 'reason': 'zero_baseline'})
            continue
        delta = before['total_tokens'] - after['total_tokens']
        valid.append({'task_id': name, 'model': pair['model'],
                      'before_tokens': before['total_tokens'], 'after_tokens': after['total_tokens'],
                      'delta_tokens': delta, 'change_percent': round(100 * delta / before['total_tokens'], 4)})
    sufficient = len(valid) >= min_pairs
    total_before = sum(p['before_tokens'] for p in valid)
    total_after = sum(p['after_tokens'] for p in valid)
    return {'tool': 'kattour-guardian-token-benchmark',
            'status': 'comparable' if sufficient else 'insufficient_comparable_pairs',
            'pairs_submitted': len(records), 'pairs_comparable': len(valid),
            'minimum_comparable_pairs': min_pairs,
            'weighted_change_percent': round(100 * (total_before - total_after) / total_before, 4) if total_before else None,
            'median_pair_change_percent': round(statistics.median(p['change_percent'] for p in valid), 4) if valid else None,
            'total_before_tokens': total_before, 'total_after_tokens': total_after,
            'runs': valid, 'excluded': excluded,
            'limitations': ['Caller-supplied provider counters, not independently verified billing or cost savings.',
                            'Quality gates must use equivalent tasks and objective acceptance criteria.',
                            'Caching, hidden prompts, retries and model settings can change real token usage.']}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', required=True, type=Path)
    parser.add_argument('--min-pairs', type=int, default=3)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args(argv)
    try:
        if args.input.is_symlink() or not args.input.is_file() or args.input.stat().st_size > MAX_BYTES:
            raise ValueError('Expected a regular JSON file <=2MB')
        payload = json.loads(args.input.read_text(encoding='utf-8'))
        data = payload.get('runs') if isinstance(payload, dict) else payload
        report = benchmark(data, args.min_pairs)
        output = json.dumps(report, indent=2) + '\n'
        if args.output:
            args.output.write_text(output, encoding='utf-8')
        else:
            print(output, end='')
        return 0 if report['status'] == 'comparable' else 1
    except (OSError, ValueError, UnicodeError, TypeError) as exc:
        print('Invalid benchmark: ' + type(exc).__name__, file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
