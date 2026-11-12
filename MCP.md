# Kattour Guardian MCP Server — v1.0.0

An optional **read-only, local stdio MCP server** for coding assistants that support user-defined MCP tools. It makes the existing offline token-context selector, heuristic security scan, HTML accessibility hints and log compressor callable via MCP. No AI model API keys or external Python dependencies are required.

**Requirements:** Python 3.10+, a complete checkout of this repository, a local MCP-compatible client, and an explicit *authorized* project directory.

## Client configuration

Example configuration for MCP clients that accept a JSON `mcpServers` block (the exact configuration filename and format depend on the client):

```json
{
  "mcpServers": {
    "kattour-guardian": {
      "command": "python3",
      "args": [
        "/absolute/path/to/kattour-guardian/mcp_server.py",
        "--root",
        "/absolute/path/to/your-project"
      ]
    }
  }
}
```

Example for clients using a TOML MCP server configuration, such as supported Codex versions:

```toml
[mcp_servers.kattour-guardian]
command = "python3"
args = ["/absolute/path/to/kattour-guardian/mcp_server.py", "--root", "/absolute/path/to/your-project"]
```

Windows users may need `python` instead of `python3`. Restart the coding assistant after registering the server.

You can run `python mcp_server.py --root /path/to/project` manually, but it will **wait for MCP JSON-RPC input on stdin**, not display a chat UI. An MCP host starts and controls the server process.

## Tools

| Tool | What it does |
| --- | --- |
| `guardian_context` | Task-focused project map or redacted snippets, hard character budget, in-memory delta cache for unchanged files. |
| `guardian_security` | Read-only heuristic source security review; uncapped scanning with a bounded number of returned findings. |
| `guardian_a11y` | Static HTML checks for language, image alt attributes and viewport metadata. |
| `guardian_compact_log` | Extracts relevant diagnostic lines from text logs with best-effort credential redaction. |
| `guardian_browser` | Optional local Playwright layout and rendered accessibility hints. Requires explicitly configured `--browser-origin` and Playwright Chromium; no screenshots via MCP. |
| `guardian_token_compare` | Before/after arithmetic on supplied input/output token counts, not provider billing verification. |
| `guardian_usage` | Counts local eligible/output characters and computes a **rough** 4-characters/token approximation. |

## Efficient and safe workflow

Start with `guardian_context` using `mode=map` and `max_chars=2000`–`4000`. Request targeted `snippets` only when required. Same-session SHA-256 reuse reduces re-sending unchanged file content, but if a new conversation no longer contains the earlier source, call with `reuse_unchanged=false`.

The server never calls model-provider APIs and **cannot measure billed tokens**. It cannot guarantee any percentage reduction in actual token charges. Its secret filtering is best-effort; do not pass raw sensitive logs or source to any AI service without reviewing disclosure risks.

The MCP process only accesses its authorized project root (relative paths, no symlink traversal). It does not execute arbitrary shell commands, modify files, call URLs, or expose an HTTP endpoint. Use only with trusted MCP clients. The host ultimately controls what tool output is sent to an AI model.

Security findings are leads requiring verification. A clean report is **not** a security certification, and the HTML tool is **not** a complete WCAG or rendered-browser evaluation. For comprehensive security, add authorized dependency/secret/CodeQL/Semgrep and manual reviews independently.

## Local validation

```bash
python scripts/validate.py
python -m unittest discover -s tests -v
python skills/kattour-guardian/scripts/security_scan.py . --fail-on high
```

Further reference: [MCP specification](https://modelcontextprotocol.io/specification/2025-11-25).

## Optional browser and token tools (v0.4)

See [BROWSER.md](BROWSER.md). Install Playwright and Chromium on the MCP host. Start the server with `--browser-origin http://127.0.0.1:3000`; this opts in to that exact local origin. Browser scripting and network routing are not a complete sandbox; use a trusted local test application and disposable data. Browser screenshots are not returned to MCP clients.

`guardian_token_compare` uses four caller-supplied numeric counters; it does not query an AI provider and cannot establish actual billable cost savings.

## New tools in v0.5

- `guardian_provider_usage` accepts a provider name (`openai`, `anthropic`, or `gemini`) and a numeric-only `usage` object. Unknown fields (e.g. messages) are rejected. It does not use credentials or vendor APIs, and its counters are not independently verified.
- `guardian_quality_report` creates a bounded, read-only triage report using static code security and HTML accessibility checks inside the authorized project root. Unverified findings and omitted checks are explicitly identified.

For opt-in, offline before/after JSON comparisons, read [TOKEN_USAGE.md](TOKEN_USAGE.md). Never pass full provider responses, private messages, secrets, or invoices into tool arguments.


## Compatibility verification (v1.0.0)

Run `python scripts/compatibility_smoke.py --json` from the repository. It checks the local MCP stdio initialize handshake, tool listing, a read-only tool invocation, and rejection of a parent-directory path. This test does not start or authenticate external MCP clients. See [COMPATIBILITY.md](COMPATIBILITY.md).
