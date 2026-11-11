#!/usr/bin/env python3
"""Compare caller-supplied provider token counters. No API or billing access."""
from __future__ import annotations
import argparse
import json


def compare(before_input: int, before_output: int, after_input: int, after_output: int,
            source: str = 'manual') -> dict:
    values = (before_input, before_output, after_input, after_output)
    if any(type(v) is not int or v < 0 or v > 10**12 for v in values):
        raise ValueError('Token counts must be nonnegative integers up to 1e12')
    if source not in ('manual', 'provider_reported'):
        raise ValueError('source must be manual or provider_reported')
    before, after = before_input + before_output, after_input + after_output
    return {
        'source': source,
        'before': {'input_tokens': before_input, 'output_tokens': before_output, 'total_tokens': before},
        'after': {'input_tokens': after_input, 'output_tokens': after_output, 'total_tokens': after},
        'difference_tokens': before - after,
        'reduction_percent': round((before - after) * 100 / before, 2) if before else None,
        'warning': 'Arithmetic on caller-supplied counts, not independently verified API usage or cost. Compare equivalent tasks, model, settings, and caching policy. Negative reduction means increased tokens.'
    }


def main() -> None:
    parser = argparse.ArgumentParser(description='Compare input and output token counts supplied by the caller')
    for field in ('before-input', 'before-output', 'after-input', 'after-output'):
        parser.add_argument('--' + field, type=int, required=True)
    parser.add_argument('--source', choices=('manual', 'provider_reported'), default='manual')
    args = parser.parse_args()
    try:
        print(json.dumps(compare(args.before_input, args.before_output,
                                 args.after_input, args.after_output, args.source), indent=2))
    except ValueError as exc:
        parser.exit(2, f'Error: {exc}\n')


if __name__ == '__main__':
    main()
