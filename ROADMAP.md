## Shipped in v0.2.0 — Token Efficiency Engine

- [x] Progressive project maps and task-focused snippets.
- [x] Exact context character budgets, plus clearly labeled *estimated* token metrics.
- [x] SHA-256-only delta snapshots scoped to the same repository/task/mode.
- [x] Optional Git changed-file targeting; fail explicitly when Git is unavailable.
- [x] Credential-pattern redaction in snippets, exclusions for common sensitive paths, and regression tests.
- [x] Error-focused local build/test log compaction with deterministic output limits.
- [ ] Live model-provider usage telemetry / tokenizer-specific verified budgeting.
- [ ] Agent-specific context-cache integration and benchmark harness with actual API token usage.

# Roadmap (proposals, not shipped features)

The first release focuses on an auditable, portable Agent Skill. The roadmap is not a promise that the following capabilities currently exist.

## Next: richer deterministic checks
- Add adapters for supported package ecosystems and lockfile vulnerability advisories.
- Optional integrations with Gitleaks, Semgrep, CodeQL and browser axe-core with explicit user consent, documented versions and secure CI permissions.
- Test rule precision and false positives before raising security severity.

## Cross-agent interoperability
- Optional **Model Context Protocol (MCP)** server exposing scoped offline inspection tools to compatible clients, including agents that do not natively discover `SKILL.md`.
- Avoid storing API keys or source files on a central service by default.
- Version and verify schemas, client compatibility and authorization boundaries before claiming support.

## Real UX validation
- Optional Playwright workflows for visual regression and keyboard interaction.
- Browser-rendered accessibility signals and guided manual validation, not fake compliance scores.
- Design token, mobile, RTL and interaction-state audits with before/after evidence.

## GitHub automation
- Least-privilege, opt-in PR review bot, no production deployments by default.
- Structured reports: finding ID, severity, confidence, evidence, remediation and retest status.
- Sensitive finding redaction and private security reporting.

## Quality bar
- Compatibility smoke tests across major coding agents.
- Measurable reduction in confirmed regressions and false positives.
- Regular review of OWASP ASVS/MASVS and WCAG references.
