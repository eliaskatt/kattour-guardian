## Shipped in v0.6.0

- [x] Read-only automatic GitHub PR review of changed lines.
- [x] Bounded findings without source snippets or secret values.
- [ ] Cross-project precision benchmarks, opt-in PR comments, and deeper visual regression checks.

## Shipped in v0.5.0

- [x] Offline user-supplied OpenAI, Anthropic and Gemini usage counter normalization.
- [x] Read-only MCP tools for token counters and bounded quality triage.
- [x] CodeQL and community Semgrep source-scan workflows.
- [ ] Verify actual billed savings against equivalent real-world tasks.
- [ ] Larger-scale UI testing and human-reviewed accessibility/security studies.

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

**Shipped in v0.3.0:** local MCP stdio adapter with five read-only tools and scope restrictions. Compatibility smoke tests with individual desktop MCP clients and independently measured provider token usage are still pending.

The first release focuses on an auditable, portable Agent Skill. The roadmap is not a promise that the following capabilities currently exist.

## Next: richer deterministic checks
- Add adapters for supported package ecosystems and lockfile vulnerability advisories.
- Optional integrations with Gitleaks, Semgrep, CodeQL and browser axe-core with explicit user consent, documented versions and secure CI permissions.
- Test rule precision and false positives before raising security severity.

## Cross-agent interoperability
- [x] Local MCP stdio server shipping in v0.3.0; [ ] hosted authenticated MCP and cross-client integration tests.
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

## Delivered in v0.4.0

- Opt-in Playwright localhost DOM and layout heuristics with controlled screenshot output.
- MCP tool authorization for a pre-approved loopback origin.
- Comparison of caller-supplied usage counters, with honest measurement limitations.

## Planned next

- Better accessibility auditing using a dedicated accessibility engine.
- CI review summaries for authorized pull requests, without exposing secret values.
- Fair provider-usage benchmark harness supporting verified responses when integrations are explicitly configured.
