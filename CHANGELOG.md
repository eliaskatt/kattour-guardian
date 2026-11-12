# Changelog

## [0.9.0] — 2026-11-12

- Added a paired task token benchmark with explicit quality gates, excluded trials and weighted/median comparisons.
- Reports only caller-supplied usage counters, not verified billing or cost savings.

## [0.8.0] — 2026-11-12

- Added optional local PNG visual regression for mobile/desktop screenshots and strict file limits.
- Added tests with optional Pillow and ensured no screenshots are included in tool output.

## [0.7.0] — 2026-11-12

- Added redacted, bounded native GitHub Checks annotations from existing PR review findings.
- Preserved base-branch scanner, read-only token, no fork code execution, and no PR write access.
- Added injection/traversal and output-budget regression tests.

## [0.6.0] — 2026-11-12

- Added deterministic Pull Request diff security and UI/UX triage.
- Added least-privilege GitHub Actions summaries and short-lived redacted JSON artifacts.
- Added regression tests for redaction, file coverage, line numbering, and malicious names.
- No model tokens, PR code execution, automatic approvals, or PR write permissions during review.


## [0.5.0] — 2026-11-11

- Added offline OpenAI, Anthropic and Gemini provider usage counter normalization.
- Added source and static HTML quality triage with explicit coverage gaps.
- Added two read-only MCP tools and regression tests.
- Added CodeQL and community Semgrep workflows with local rules.
- Kept English-only project documentation; provider counts are not verified billing.


## [0.4.0] — 2026-11-11

- Added opt-in localhost Playwright rendered UI and accessibility heuristics at two viewport sizes.
- Added model token usage arithmetic on caller-supplied before/after counters; no provider API calls or billable-cost claims.
- Added `guardian_browser` and `guardian_token_compare` to the MCP server, with explicit local-origin authorization.
- Added browser regression tests and an optional Chromium GitHub Actions workflow.
- Consolidated project documentation in English and removed the obsolete repository-creation guidance.

## [0.3.0] — 2026-11-11

- New local, read-only stdio MCP server with five bounded tools and explicit project-root scope.
- Same-session SHA-256 delta context selection and local character estimates via MCP (not billed token metrics).
- Offline security, HTML heuristic checks and log compaction exposed to compatible MCP clients.
- MCP setup guide, protocol tests and GitHub Actions workflow.
- No HTTP endpoint, credentials, arbitrary shell execution, or third-party Python runtime packages.


## [0.2.0] — 2026-11-11

- Added a token-aware workflow and selective context-loading reference.
- Added offline `context_pack.py`: project map, targeted snippets, hard character limits, optional Git changed-file filters, SHA-256 delta snapshots, and approximate token metrics.
- Added `log_compact.py` for error-focused summaries of large build/test logs.
- Added extensive tests for redaction, budget enforcement, changed-only mode, and snapshot safety.
- Updated documentation and ignored local snapshot cache directories.
- Clarified that token savings vary by model and are not measured billable-token guarantees.

## [0.1.0] — 2026-11-11

- Initial release: full-stack engineering, design, accessibility, evidence-led security guidance, local heuristic scanning, and CI.
