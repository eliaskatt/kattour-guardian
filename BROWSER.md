# Kattour Guardian browser and token checks (v0.4.0)

Kattour Guardian can optionally test **a running authorized localhost web app** at mobile (390×844) and desktop (1440×900) viewports with Playwright.

The checker reports rendered-DOM and layout hints such as horizontal overflow, missing title/language/viewport/H1, visible unlabeled inputs/buttons/links, missing image alt text, broken images, and small mobile pointer targets. **It does not judge visual design quality, calculate WCAG compliance, or replace screen-reader and manual UX checks.**

## Install browser dependencies (optional)

Core Skill and other MCP tools require only Python 3.10+. Browser audit is opt-in:

```bash
python -m pip install playwright
python -m playwright install chromium
```

## Audit your local app

Start your own application on localhost, then run:

```bash
python skills/kattour-guardian/scripts/browser_audit.py http://127.0.0.1:3000/
```

Screenshots are *off by default* and may include private information:

```bash
python skills/kattour-guardian/scripts/browser_audit.py http://127.0.0.1:3000/ --screenshot-dir ./guardian-browser-evidence
```

Only local HTTP loopback targets are accepted, and ordinary cross-origin HTTP requests are blocked. This is **not** a complete browser network sandbox: browser APIs and scripts may have side effects. Test only your own authorized local service, with disposable accounts and data. No production websites, remote network scanning, credentials, cookies, DOM text, or screenshots are returned by the MCP tool.

To enable MCP access explicitly:

```bash
python mcp_server.py --root /absolute/path/to/your-project --browser-origin http://127.0.0.1:3000
```

`guardian_browser` then accepts only the configured origin. MCP mode never takes screenshots.

## Token comparison with supplied measurements

```bash
python skills/kattour-guardian/scripts/token_compare.py \
  --before-input 12000 --before-output 2000 \
  --after-input 7000 --after-output 1800 --source provider_reported
```

This computes an arithmetic difference only: **it does not query AI providers or verify billable tokens**. Compare equivalent tasks with matching model, settings, caching, input data, and output requirements. A lower character count is not the same as lower billed cost.

## Tests

```bash
python scripts/validate.py
python -m unittest discover -s tests -v
```

The optional live browser test requires Chromium and a loopback-capable environment. It can be skipped in restricted environments, even when static tests pass.
