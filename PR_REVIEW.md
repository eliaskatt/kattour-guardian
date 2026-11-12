# Kattour Guardian v0.6.0 — Offline Pull Request review

The optional `Kattour Guardian PR review` GitHub Action inspects *added lines* from GitHub's PR file-patch metadata. It does not run code from the PR or require an AI model, API keys, or paid tokens. It uses Python's standard library only.

## What it detects

Heuristic indicators of hard-coded credentials, private keys, TLS verification bypasses, dynamic evaluation, shell execution, HTML injection sinks, images without an inline `alt` attribute, and clickable non-semantic elements. Findings show rule, file path and added-line number, **not code snippets, matched secrets, or raw diffs**.

The workflow displays a Markdown report in GitHub Actions **Job summary** and stores redacted findings in a short-lived JSON artifact. It does **not** write PR comments, modify code, automatically approve changes, or block merges by default. Its GitHub token has read-only permissions.

## Local test

```bash
python scripts/pr_review.py --input my-github-pr-files.json --format markdown
python scripts/pr_review.py --input my-github-pr-files.json --format json
python -m unittest discover -s tests -v
```

`my-github-pr-files.json` is a JSON array in the format returned by the GitHub `GET /repos/{owner}/{repo}/pulls/{number}/files` API; each entry contains `filename`, `status`, and optional `patch`.

To fetch an authorized PR's diff metadata explicitly, export a GitHub token with **read-only repository and pull request permissions** and call:

```bash
GITHUB_TOKEN=... python scripts/fetch_pr_files.py --repo OWNER/REPO --number 123 --out /tmp/pr-files.json
python scripts/pr_review.py --input /tmp/pr-files.json --format markdown
```

Never commit `/tmp/pr-files.json`, as it may contain sensitive added code. The CI workflow does not upload it as an artifact.

## Threat model and limitations

- Uses the trusted base branch's scanner, **not the potentially untrusted PR version**. No `pull_request_target`, code execution from the fork, or PR write permissions.
- Reads file changes via the GitHub API, with 500-file and per-page size limits. GitHub may omit patches for binary or very large files; these produce explicit coverage gaps. A failed fetch fails the job.
- Scans only added diff lines, not the full application, surrounding call chains, generated pages, external dependencies, runtime accessibility or real authorization behavior. All reported issues require verification.
- Findings do not include source code, but file paths can still contain sensitive filenames. Treat artifacts accordingly.
- PR review is a source-change triage aid, not a security certification. Use CodeQL, Semgrep, tests and human review in addition.
## New in v0.7.0: native GitHub Checks annotations

The workflow now calls `scripts/pr_annotations.py` on the **redacted JSON** result of the existing offline reviewer. It emits at most 30 `::warning` / `::error` / `::notice` commands using validated paths, line numbers, known rule IDs and **static messages**. It never emits code snippets, secrets, or free-form PR text. These are GitHub Actions annotations associated with changed lines, **not** PR conversation comments or reviews.

```bash
python scripts/pr_review.py --input /tmp/pr-files.json --format json > /tmp/guardian-pr.json
python scripts/pr_annotations.py --input /tmp/guardian-pr.json --max-annotations 30
```

Permissions remain `contents: read` and `pull-requests: read`; the workflow continues to check out the **trusted base commit**, not the untrusted PR head. The annotations may not be visible inline for all GitHub UI configurations. Do not automatically block a merge based on heuristic findings without human review.
