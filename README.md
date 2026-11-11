# Kattour Guardian

**Portable Agent Skill for excellent apps, accessible UI/UX, maintainable architecture, evidence-based defensive security, and token-efficient AI coding workflows.**

[العربية / Arabic](README.ar.md) · [Security policy](SECURITY.md) · [Contributing](CONTRIBUTING.md)

> **Important:** No AI, scanner, or skill can guarantee that an app is 100% secure or fully accessible. Kattour Guardian promotes careful engineering and evidence-based verification, not security certification.

## What it does

- **Build & architecture:** Understand an existing repository, plan changes, review APIs and data boundaries, implement features and add tests.
- **UI/UX:** Review task flows, hierarchy, responsive layouts, keyboard navigation, semantics, localization and RTL.
- **Security:** Apply a defensive threat-modeling workflow informed by OWASP ASVS/MASVS; identify likely access-control, injection, secrets and supply-chain problems.
- **Quality & performance:** Recommend appropriate test coverage, check regressions and distinguish measured performance from hypotheses.
- **Release review:** Produce a structured list of findings, severity, confidence, evidence, corrections and untested areas.
- **Token Efficiency Engine (v0.3):** Use task-focused project maps, small redacted snippets, hard character budgets, Git-change targeting, and same-session SHA-256 delta snapshots to avoid repeatedly feeding unchanged source to an AI agent. Do not compromise testing or security scope.

## MCP tools server (new in v0.3)

In addition to the portable Agent Skill, this repository now includes a **local, read-only MCP stdio server** with five tools for bounded context selection, delta cache, defensive static checks, HTML accessibility hints, log compaction and local character metrics. It has no Python package dependencies or AI API keys. A compatible MCP host must explicitly configure it; installing the Skill alone does not start it. See [MCP.md](MCP.md) for supported tool names, setup, examples, and important privacy limitations.

```bash
python /absolute/path/to/kattour-guardian/mcp_server.py --root /absolute/path/to/authorized-project
```

This process waits for MCP JSON-RPC messages on stdin. It does not expose an HTTP server or automatically connect to every AI model.

## Install in an AI coding agent

After this repository has been published to GitHub, run inside a project (requires a compatible Node.js installation and the third-party `skills` CLI):

```bash
npx skills add eliaskatt/kattour-guardian --skill kattour-guardian
```

Select your agent in the interactive installer. To see options:

```bash
npx skills add eliaskatt/kattour-guardian --list
```

The `skills` CLI supports a wide range of agents, including Codex, Claude Code, Cursor, GitHub Copilot, Gemini CLI and others. **Compatibility is with agents that support skills, not every AI model or chat website.** Review any external installer before running it.

### Manual installation (works without the npm installer)

Copy the entire `skills/kattour-guardian/` directory (including `references/` and `scripts/`) into an appropriate project folder:

| Coding agent | Project skill folder |
| --- | --- |
| OpenAI Codex | `.agents/skills/kattour-guardian/` |
| Claude Code | `.claude/skills/kattour-guardian/` |
| GitHub Copilot / VS Code | `.github/skills/kattour-guardian/` |
| Cursor | `.cursor/skills/kattour-guardian/` or `.agents/skills/kattour-guardian/` |
| Gemini CLI | `.gemini/skills/kattour-guardian/` or `.agents/skills/kattour-guardian/` |

Keep all paths relative to `SKILL.md` intact. Exact discovery behavior depends on agent version and configuration. In chat interfaces without filesystem-based Skill support, you can manually paste relevant instructions, but automatic installation or tool execution cannot be assumed.

## Quick start

Ask your coding agent:

> Use kattour-guardian to inspect this app, improve the main mobile UX, review relevant security controls, add appropriate tests, and report what was actually verified. Do not touch production.

Other examples: [prompts/EXAMPLES.md](prompts/EXAMPLES.md).

## Save AI context tokens (v0.3.0)

**Goal:** Avoid wasted tokens—not promise an arbitrary reduction. The context packer reduces raw source text passed to the model by selecting only task-relevant files and symbols; **actual billed token savings depend on agent/model/caching behavior**. It cannot modify how a vendor bills tokens or automatically compress its hidden/system context.

```bash
# Start small: names and code symbols, not entire code files
python skills/kattour-guardian/scripts/context_pack.py . \
  --task "improve mobile checkout" --mode map --max-chars 3000 --metrics

# Read relevant code excerpts only when necessary
python skills/kattour-guardian/scripts/context_pack.py . \
  --task "improve mobile checkout" --mode snippets --max-chars 7000 --metrics

# Persist hashes only and send changed content on the NEXT turn of the SAME conversation
python skills/kattour-guardian/scripts/context_pack.py . \
  --task "improve mobile checkout" --mode snippets --max-chars 7000 \
  --snapshot-out .guardian-cache/checkout.json
python skills/kattour-guardian/scripts/context_pack.py . \
  --task "improve mobile checkout" --mode snippets --max-chars 7000 \
  --snapshot-in .guardian-cache/checkout.json --snapshot-out .guardian-cache/checkout.json

# Optional: target only Git changes
python skills/kattour-guardian/scripts/context_pack.py . \
  --task "fix checkout" --mode snippets --changed-only --max-chars 6000
```

For noisy test/build logs, run:

```bash
python skills/kattour-guardian/scripts/log_compact.py build.log --max-chars 2500
```

**Safety/correctness limitations:** `--max-chars` is a character limit, **not** a tokenizer-enforced token budget. Metrics are approximate; no fixed percentage is guaranteed. Snapshots are local path + hash indexes and must not be used to skip code in a new AI conversation. Snippet redaction cannot catch every secret or personal detail: **review output before sharing**. Run complete applicable security checks separately; a small context bundle is never an audit.

See [Token-efficient workflow](skills/kattour-guardian/references/token-efficiency.md) for agent behavior, cases, and a fair benchmark protocol.

## Local checks (Python 3.10+, no third-party Python packages)

The skill bundles two deliberately small **offline heuristics** plus a local context-packing utility:

```bash
# Potential secrets, TLS bypasses and a handful of risky coding patterns
python skills/kattour-guardian/scripts/security_scan.py . --format markdown --fail-on high

# HTML source-only accessibility hints (not a WCAG audit)
python skills/kattour-guardian/scripts/html_a11y.py . --format markdown

# Machine-readable output
python skills/kattour-guardian/scripts/security_scan.py . --format json --fail-on none
```

The security scanner exits 1 when it finds a rule at/above the selected threshold, 0 otherwise, and 2 for an argument error. It does not emit matched secret values, scan remote targets, or invoke network services. Results may contain false positives and miss serious vulnerabilities. The HTML checker does not render JavaScript and cannot test keyboard flows or screen readers.

To validate the Skill package itself:

```bash
python scripts/validate.py
python -m unittest discover -s tests -v
```

For serious projects, combine the Skill with scoped, authorized tooling such as CodeQL/Semgrep, Gitleaks, dependency advisories, browser-based accessibility checks and independent security review.

## Project layout

```text
kattour-guardian/
├── skills/kattour-guardian/
│   ├── SKILL.md
│   ├── references/
│   │   ├── architecture.md
│   │   ├── design.md
│   │   ├── security.md
│   │   ├── verification.md
│   │   ├── platforms.md
│   │   ├── reporting.md
│   │   └── token-efficiency.md
│   └── scripts/
│       ├── security_scan.py
│       ├── html_a11y.py
│       ├── context_pack.py
│       └── log_compact.py
├── mcp_server.py\n├── MCP.md\n├── scripts/validate.py
├── tests/test_mcp_server.py\n├── tests/test_tools.py
├── tests/test_context_pack.py
├── tests/test_log_compact.py
├── CHANGELOG.md
├── prompts/EXAMPLES.md
├── .github/workflows/ci.yml\n├── .github/workflows/mcp.yml
├── SECURITY.md
├── CONTRIBUTING.md
├── README.ar.md
└── LICENSE
```

## Source and verification

[Public GitHub repository](https://github.com/eliaskatt/kattour-guardian) · [GitHub Actions](https://github.com/eliaskatt/kattour-guardian/actions). Check CI results after release; local tests and syntax checks are not a guarantee of interoperability with every client.

## Design principles

- Portable, vendor-neutral, progressive disclosure with task-specific context and measured overhead.
- **Read-first** and permission-aware. No intrusive tests or deployment without authorization.
- Results must be reviewable and reproducible; no invented findings, scores or certificates.
- **Offline local scripts** by default, with optional deeper tools chosen by the user.

## License

MIT. Copyright © 2026 Kattour. See [LICENSE](LICENSE).

## References

- [Agent Skills specification](https://agentskills.io/specification)
- [GitHub Copilot Agent Skills documentation](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
- [Vercel skills CLI](https://github.com/vercel-labs/skills)
- [OWASP ASVS](https://owasp.org/www-project-application-security-verification-standard/)
- [OWASP MASVS](https://mas.owasp.org/MASVS/)
- [WCAG 2.2](https://www.w3.org/TR/WCAG22/)
