# Changelog

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
- Updated English/Arabic docs and ignored local snapshot cache directories.
- Clarified that token savings vary by model and are not measured billable-token guarantees.

## [0.1.0] — 2026-11-11

- Initial release: full-stack engineering, design, accessibility, evidence-led security guidance, local heuristic scanning, and CI.
