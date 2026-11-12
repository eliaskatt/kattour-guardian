# Token benchmark harness (v0.9.0)

Run **the same tasks** with and without Kattour Guardian and record **provider-reported input/output token counts** from the same AI model. Ensure equal instructions, quality criteria, caching settings and retries. This tool does **not** contact providers, handle API keys, estimate billing costs, or prove its own savings.

Create private `paired-runs.json` (do not commit real conversation content or sensitive exports):

```json
{
  "runs": [
    {
      "task_id": "form-validation",
      "model": "same-model-id",
      "quality_before_pass": true,
      "quality_after_pass": true,
      "before": {"input_tokens": 10000, "output_tokens": 1200, "cached_input_tokens": 1000},
      "after": {"input_tokens": 6500, "output_tokens": 1100, "cached_input_tokens": 300}
    },
    {
      "task_id": "api-handler",
      "model": "same-model-id",
      "quality_before_pass": true,
      "quality_after_pass": true,
      "before": {"input_tokens": 9000, "output_tokens": 1500},
      "after": {"input_tokens": 7000, "output_tokens": 1300}
    },
    {
      "task_id": "ui-regression",
      "model": "same-model-id",
      "quality_before_pass": true,
      "quality_after_pass": true,
      "before": {"input_tokens": 8200, "output_tokens": 1600},
      "after": {"input_tokens": 7300, "output_tokens": 1400}
    }
  ]
}
```

```bash
python scripts/token_benchmark.py --input paired-runs.json --min-pairs 3 --output guardian-benchmark.json
```

Reports weighted and median per-task token changes and **excludes failed quality gates**, listing those exclusions explicitly. Default: at least three comparable task pairs. Positive percentages mean fewer reported tokens; negative percentages mean more. Cached input tokens remain included in input tokens; token changes are not fee changes. Underlying counters are **caller supplied and not audited**. For provider JSON normalization, see [TOKEN_USAGE.md](TOKEN_USAGE.md).
