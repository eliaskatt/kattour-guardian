#!/usr/bin/env python3
"""Offline normalization of provider-reported token counters (no API calls)."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

PROVIDERS = ('openai', 'anthropic', 'gemini')
MAX_TOKENS = 10**12


def count(record, key, default=None):
    value = record.get(key, default)
    if value is None:
        return None
    if type(value) is not int or not 0 <= value <= MAX_TOKENS:
        raise ValueError('Invalid token counter: ' + key)
    return value


def identify(record, provider):
    if provider != 'auto':
        if provider not in PROVIDERS:
            raise ValueError('Unsupported provider')
        return provider
    if record.get('provider') in PROVIDERS:
        return record['provider']
    if isinstance(record.get('usageMetadata'), dict):
        return 'gemini'
    usage = record.get('usage', record)
    if not isinstance(usage, dict):
        raise ValueError('Missing usage object')
    if 'prompt_tokens' in usage or 'completion_tokens' in usage or record.get('object') in ('response', 'chat.completion'):
        return 'openai'
    if record.get('type') == 'message' or 'cache_read_input_tokens' in usage or 'cache_creation_input_tokens' in usage:
        return 'anthropic'
    raise ValueError('Ambiguous schema: specify --provider openai or anthropic')


def normalize(record, provider='auto'):
    if not isinstance(record, dict):
        raise ValueError('Usage record must be a JSON object')
    provider = identify(record, provider)
    u = record.get('usageMetadata') if provider == 'gemini' else record.get('usage', record)
    if not isinstance(u, dict):
        raise ValueError('Usage counters must be an object')
    if provider == 'openai':
        inp = count(u, 'input_tokens')
        out = count(u, 'output_tokens')
        inp = count(u, 'prompt_tokens') if inp is None else inp
        out = count(u, 'completion_tokens') if out is None else out
        details = u.get('input_tokens_details', u.get('prompt_tokens_details', {})) or {}
        if not isinstance(details, dict):
            raise ValueError('Malformed cache details')
        cached = count(details, 'cached_tokens', 0)
    elif provider == 'anthropic':
        inp, out = count(u, 'input_tokens'), count(u, 'output_tokens')
        cached = count(u, 'cache_read_input_tokens', 0)
        created = count(u, 'cache_creation_input_tokens', 0)
        inp = inp + cached + created if inp is not None else None
    else:
        inp, out = count(u, 'promptTokenCount'), count(u, 'candidatesTokenCount')
        cached = count(u, 'cachedContentTokenCount', 0)
    if inp is None or out is None:
        raise ValueError('Required input/output counters missing')
    total = count(u, 'totalTokenCount' if provider == 'gemini' else 'total_tokens', inp + out)
    if cached > inp or total < inp + out or max(inp, out, total) > MAX_TOKENS:
        raise ValueError('Inconsistent token counters')
    return {'provider': provider, 'input_tokens': inp, 'output_tokens': out,
            'total_tokens': total, 'cached_input_tokens': cached}


def aggregate(records, provider='auto'):
    if not isinstance(records, list) or not 1 <= len(records) <= 10000:
        raise ValueError('Expected between 1 and 10000 records')
    rows = [normalize(r, provider) for r in records]
    result = {'source': 'caller_supplied_provider_usage', 'records': len(rows),
              'providers': sorted({r['provider'] for r in rows})}
    for field in ('input_tokens', 'output_tokens', 'total_tokens', 'cached_input_tokens'):
        result[field] = sum(r[field] for r in rows)
    result['notice'] = 'Provider counters were supplied by caller, not verified against bills; no prompts or response bodies are returned.'
    return result


def compare(before, after):
    change = before['total_tokens'] - after['total_tokens']
    return {'before': before, 'after': after, 'difference_tokens': change,
            'reduction_percent': round(100 * change / before['total_tokens'], 2) if before['total_tokens'] else None,
            'warning': 'Compare equivalent tasks and identical models, quality targets and caching rules; token counts are not costs.'}


def load(path, jsonl=False):
    path = Path(path)
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 2_000_000:
        raise ValueError('Input must be a regular file (2 MB maximum, no symlinks)')
    payload = path.read_text(encoding='utf-8')
    if jsonl:
        return [json.loads(line) for line in payload.splitlines() if line.strip()]
    data = json.loads(payload)
    return data if isinstance(data, list) else [data]


def main():
    parser = argparse.ArgumentParser(description='Analyze local provider usage JSON / JSONL without network calls')
    parser.add_argument('--before', required=True, type=Path)
    parser.add_argument('--after', type=Path)
    parser.add_argument('--provider', choices=['auto', *PROVIDERS], default='auto')
    parser.add_argument('--jsonl', action='store_true')
    args = parser.parse_args()
    try:
        before = aggregate(load(args.before, args.jsonl), args.provider)
        result = compare(before, aggregate(load(args.after, args.jsonl), args.provider)) if args.after else before
        print(json.dumps(result, indent=2))
    except (ValueError, OSError, UnicodeError) as exc:
        parser.exit(2, 'Invalid usage data: ' + type(exc).__name__ + '\n')


if __name__ == '__main__':
    main()
