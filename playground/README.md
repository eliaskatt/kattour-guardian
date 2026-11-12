# Kattour Guardian Playground

An English-language, offline-first interactive engineering workspace for the [Kattour Guardian](https://github.com/eliaskatt/kattour-guardian) Agent Skill. This is a **developer tool**, not a landing page.

## Try it

- **Quickest:** open `playground.html` in a modern browser (self-contained, no build step).
- **For reliable local session/template storage:** run `python3 -m http.server 8000` in this directory and open `http://127.0.0.1:8000/`.
- All logic is deterministic and runs in the browser. No AI API requests, account, or paid model is required.

## Main features

- Configure project type, framework, platform, requirements, and goal.
- Generate a project-specific architecture, four-stage plan, priority backlog, and practical UI/UX review.
- Optimize a self-contained AI prompt and compare it with the full draft side-by-side.
- Estimated tokens use `ceil(characters / 4)`; these are **not** actual billed or model-tokenizer counts.
- Context reuse must be explicitly marked as sent in the **same** conversation. The standalone prompt otherwise includes the shared engineering standard block.
- Eight local quality checks before copy or export, including a credentials-pattern warning and stale-workspace guard.
- Save sessions/templates to browser `localStorage` (no cloud sync). This data is private to that browser origin and can be cleared in the application.
- Download Markdown, JSON, or a plain text prompt.

## Source layout

- `index.html` — application layout and semantic controls
- `styles.css` — responsive wide-screen workbench styling
- `engine.mjs` — deterministic planning, optimization, QA, serialization
- `app.js` — browser UI, sessions, templates, export and navigation
- `playground.html` — single-file distributable bundle
- `tests/engine.test.mjs` — Node.js built-in test suite

## Verification

```bash
node --test tests/engine.test.mjs
node --check app.js
```

Optionally run `tests/browser-smoke.py` using Python Playwright and Chromium. Browser startup and sandbox availability depend on your environment. The smoke test uses an in-memory HTML document, avoiding external network calls.

## Security and honest limits

- There is **no** remote LLM reasoning. Plans are rule-based starting points requiring engineering review.
- The app does **not** assess a real repository or live website automatically. Kattour Guardian MCP tools are a separate integration.
- It cannot guarantee 100% application security or accessibility.
- Basic credential redaction is best-effort; do not put secrets into project briefs.
- Saved browser sessions are **not encrypted** or synchronized across devices. Avoid sensitive data.
- Token 'savings' estimate difference between a structured full draft and optimized prompt, *not* a verified reduction against a provider bill.
- Copy and export are disabled when the current brief has changed until regeneration, or when the quality gate fails.

## License

MIT — see the parent repository license.