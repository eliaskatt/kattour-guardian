# Token-efficient engineering (without compromising correctness)

## Objective and limits

Reduce **unnecessary model input and output** without concealing evidence. No Agent Skill can guarantee an 80%, 90% or other token reduction across models/tasks: actual token accounting depends on tokenizer, framework-provided context, cache semantics, iteration count, and tool calls.

Treat token efficiency as **total cost to a correct, verified result**, not as the number of tokens in one short answer. Repeated failed edits are not economical.

## Mandatory efficiency protocol

1. **Task contract first:** identify scope, constraints and completion checks in no more than a few lines. Do not re-explain static project background every turn.
2. **Progressive disclosure:** start with the smallest relevant reference file, project map and filenames; expand only the needed code ranges. Do not load every reference by default.
3. **Targeted retrieval:** use filename/symbol search, grep, or local `context_pack.py`; read a full file only when dependencies, logic flow, or debugging require it.
4. **One canonical plan:** avoid duplicating specifications and running summaries. Keep a short decision log if useful; update only changes.
5. **Patch-first modifications:** produce minimal diffs; never reprint complete unchanged files. Preserve existing conventions.
6. **Batch deterministic checks:** prefer local tests/linters/typecheck/scanners over repeatedly prompting the model about the same trivial pattern. Summarize failures with relevant lines instead of complete logs.
7. **Evidence gating:** do not claim tests, fixes or security validations that did not happen. Never cut required security or accessibility checks to meet a token budget.
8. **Stop conditions:** once acceptance criteria pass, deliver a concise report: changed files, tests/results, unresolved risks and next steps only.

## Offline context packer

From the project root (after installing the Skill):

```bash
# Low-input overview: safe default, paths and symbol signatures only
python .agents/skills/kattour-guardian/scripts/context_pack.py . \
  --task "fix checkout layout on mobile" --mode map --max-chars 3000 --metrics

# Include relevant source snippets when implementation requires it
python .agents/skills/kattour-guardian/scripts/context_pack.py . \
  --task "fix checkout layout on mobile" --mode snippets --max-chars 7000 --metrics

# Reuse within SAME active agent conversation/task only
python .agents/skills/kattour-guardian/scripts/context_pack.py . \
  --task "fix checkout layout on mobile" --mode snippets --max-chars 7000 \
  --snapshot-out .guardian-cache/checkout.json
# After modifying files, show only context not present in that same conversation:
python .agents/skills/kattour-guardian/scripts/context_pack.py . \
  --task "fix checkout layout on mobile" --mode snippets --max-chars 7000 \
  --snapshot-in .guardian-cache/checkout.json --snapshot-out .guardian-cache/checkout.json
```

Agent folder paths vary; adjust to the installed location. The tool is offline and uses Python standard library. `--changed-only` (optional) focuses on Git changed/staged/untracked files, and fails explicitly outside a Git repository. The snapshot stores **file paths and SHA-256 hashes**, not code; never use a snapshot to skip context across a new conversation where the earlier bundle is not available to the agent. The snapshot can store the task string, so do not put secrets in `--task`.

The `--max-chars` cap is exact for stdout; token counts printed by `--metrics` use a rough estimate and are **not** API-reported tokens. Content is selectively truncated; the output is **not** a complete project audit. Before submitting snippet output to a third-party model, inspect for sensitive data. The script attempts narrow credential redaction but cannot guarantee removal of secrets/PII.

## Condense verbose test/build logs

After running commands, give the agent only actionable diagnostic lines (and open additional logs if needed):

```bash
python skills/kattour-guardian/scripts/log_compact.py build.log --max-chars 2500
# Or when using Bash with pipefail enabled to preserve the test exit code:
set -o pipefail
npm test 2>&1 | python skills/kattour-guardian/scripts/log_compact.py - --max-chars 2500
```

Do not discard the original logs when debugging. The utility picks error/warning lines and nearby context, limits the output, and masks a few common credential patterns. It is **not** a complete secret redactor and does not change a test's actual status.

## Which mode?

| Situation | Context | Verification |
| --- | --- | --- |
| New project orientation | map, 2–4K chars | Check framework/config and selected entry points |
| Small isolated code fix | snippets, 4–8K chars | Targeted tests + relevant build checks |
| UX review | map, then scoped components/styles | Keyboard, viewport, contrast, responsive checks |
| Security audit / authentication fix | map for orientation; expand all relevant trust boundaries | Full applicable security test scope, independent of prompt budget |
| Broad architecture refactor | progressive modules, larger budget when necessary | Integration tests and real regression evidence |

## Measuring savings accurately

For an apples-to-apples benchmark, execute the same task with and without this Skill on the same model and repository state. Record actual provider or agent **input tokens, output tokens, cache-hit tokens if available, number of retries, wall-clock time, test pass rate and final review findings**. Compare only runs that meet the same acceptance/security criteria. Raw source characters avoided are useful diagnostic data but **not a promised token or monetary saving**.
