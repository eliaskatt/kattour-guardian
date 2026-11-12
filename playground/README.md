# Kattour Guardian Playground

**An offline-first, professional software planning and prompt optimization workbench.**

[Open the live Playground](https://eliaskatt.github.io/kattour-guardian/) · [Project source](https://github.com/eliaskatt/kattour-guardian) · [Privacy](PRIVACY.md) · [Product growth plan](GROWTH.md)

The Playground is **not a landing page and not a hosted AI model**. It uses a transparent deterministic planning engine; it does not call OpenAI, Anthropic, Gemini or any other provider and does not require users to supply API keys.

## Workflows

- **Build feature:** implementation phases, files, priority backlog and acceptance tests for selected stacks.
- **Fix a bug:** reproduce → isolate → patch → regression proof.
- **Security review:** authorized scope → threat model → evidence-based findings → remediation. The generator is not itself a penetration test.
- **UI/UX improvement:** user journey → information architecture → responsive implementation → accessible task verification.
- **Performance review:** measure a baseline → isolate a bottleneck → implement a focused change → compare equivalent runs.

Each workflow supports six prompt targets (general, Codex, Claude Code, Cursor, GitHub Copilot and Gemini CLI) and three detail levels (Lean, Balanced and Thorough). Compatibility means **prompt guidance**, not a live connection or installation inside those agents.

## What's inside

- An implementation plan, framework-oriented file suggestions and a priority backlog.
- UI/UX recommendations, domain-specific acceptance criteria and open questions.
- Full versus optimized prompt comparison using **estimated** token counts (characters ÷ 4). Real billing savings depend on the provider, model, caching and quality.
- A local heuristic quality gate, including credential-pattern warnings.
- Local session history and templates; Markdown/JSON/prompt exports.
- **Workspace JSON import** to move a brief between browsers without an account.
- **Opt-in share links**: brief data is encoded in the URL fragment; anyone with the link can read it. The app does not submit the brief to a backend.
- Keyboard-accessible tabs and responsive desktop/mobile layouts.
- Links to GitHub Issues for real bug reports and feature suggestions. There are no fabricated star ratings or review counts.

## Local development

Requirements: Node.js 20+ for tests/build; no npm install is required. Optional Playwright + Chromium for browser smoke tests.

```sh
node playground/scripts/build.mjs
node playground/scripts/build.mjs --check
node --test playground/tests/engine.test.mjs
python playground/tests/browser-smoke.py
python playground/tests/growth-browser-smoke.py
```

The modular app is under `playground/src/`. The build script creates `playground/index.html`, a **single-file working offline app** from `src/index.html`, `src/styles.css`, `src/engine.mjs` and `src/app.js`. The generated file is committed and tested against source, preventing mismatched releases. GitHub Pages serves the generated app.

Opening `playground/index.html` locally is supported. Sharing links require the public HTTPS site. Import, plans, local storage and exports work offline.

## Important limits

All generated deliverables are **starting specifications**, not actual repository inspections, implemented features, security findings, certified WCAG evaluations or verified token consumption. Read and verify the outputs before giving them to an AI agent. Never paste secrets or personal data into prompts or shared links. Local browser storage is **not encrypted** and can be deleted by browser settings.

For verified security analysis, locally run and appropriately scope the [Kattour Guardian Agent Skill](../skills/kattour-guardian/SKILL.md) and MCP tools separately; the browser Playground does **not** execute the MCP server. See [PRIVACY.md](PRIVACY.md).
