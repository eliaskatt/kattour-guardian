# Kattour Guardian — Provider token usage (v0.5)

The tool accepts **user-provided usage counters only**. It does not use API credentials, fetch private model conversations, contact vendors, or verify invoices.

## Local workflow

Save only `usage` or `usageMetadata` objects from your own authorized API responses, not the surrounding prompts or completions. Put those exports outside Git (or in ignored `.guardian-usage/`). The CLI reads a JSON object, a JSON array, or JSONL with `--jsonl` (max 2 MB and 10,000 records). The CLI never echoes source text; it prints numeric aggregates only.

```bash
python skills/kattour-guardian/scripts/provider_usage.py \
  --before .guardian-usage/before.json --after .guardian-usage/after.json --provider openai

# For JSONL input: add --jsonl
```

Examples of **counter-only** data (replace these synthetic numbers with your real authorized data):

```json
{"usage":{"prompt_tokens":800,"completion_tokens":150,"total_tokens":950}}
```

### Supported fields

| Provider | Fields | Notes |
| --- | --- | --- |
| OpenAI | `input_tokens`/`output_tokens` or `prompt_tokens`/`completion_tokens`, optional `total_tokens`, `input_tokens_details.cached_tokens` or `prompt_tokens_details.cached_tokens` | Cache is counted within input; provider-specific billed cost may differ. |
| Anthropic | `input_tokens`, `output_tokens`, optional `cache_read_input_tokens`, `cache_creation_input_tokens` | Input total includes both cache counters, which are separately reported by the API. |
| Gemini | `usageMetadata.promptTokenCount`, `candidatesTokenCount`, optional `totalTokenCount`, `cachedContentTokenCount` | Provider total can exceed input+output due to internal categories; honor the reported total. |

If a record with just `input_tokens` and `output_tokens` is ambiguous, use `--provider openai` or `--provider anthropic`. No secret values should be included. If you only have browser chat totals, do **not** assume these counters are available.

**Comparison discipline:** Same request and acceptance tests, same model, same generation settings, same task size and caching policy, with at least several samples. Evaluate response quality and rework, not only totals. Cache read/write rates, provider token categories, pricing tiers and retries can dominate actual invoice cost. The reported percentage is arithmetic on supplied token counts—not a measured reduction in money spent or a reproducible general benchmark.

## MCP alternative

Use `guardian_provider_usage` with `{ "provider": "openai", "usage": { "input_tokens": 800, "output_tokens": 150 } }` to normalize small numeric-only usage objects. It rejects unexpected fields (e.g. prompts or messages). The agent host still sends MCP tool arguments through its own model context, so keep data minimized.

## Quality triage

```bash
python skills/kattour-guardian/scripts/quality_report.py . --format markdown
python skills/kattour-guardian/scripts/quality_report.py . --format json --max-findings 30
```

The report lists only heuristic leads, with skipped/unreadable file counts and untested areas. It is **not** proof of security or accessibility conformance.
