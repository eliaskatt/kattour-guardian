# Compatibility and verification (v1.0.0)

Kattour Guardian provides a portable **Agent Skill** and a separate, optional
**local MCP stdio server**. Installing the Skill does not automatically launch
MCP or install anything permanently in ChatGPT.

## Offline checks

Requires Python 3.10+ and no model API key:

```bash
python scripts/compatibility_smoke.py --json
python scripts/validate.py
python -m unittest discover -s tests -v
```

The smoke test checks **five filesystem installation layouts** (Codex,
Claude Code, Cursor, GitHub Copilot and Gemini CLI), verifies relative skill
references and script availability, starts the real local MCP server using a
temporary authorized project, performs an MCP initialize handshake,
lists tools, calls a read-only tool and verifies a rejected path traversal.

It deliberately does **not** claim testing actual third-party agent products.
Check client documentation for current paths and versions. It does not certify
security, accessibility or measured token savings.

## Client installation paths checked

| Client | Project-local example |
| --- | --- |
| Codex | `.agents/skills/kattour-guardian/` |
| Claude Code | `.claude/skills/kattour-guardian/` |
| Cursor | `.cursor/skills/kattour-guardian/` |
| GitHub Copilot | `.github/skills/kattour-guardian/` |
| Gemini CLI | `.gemini/skills/kattour-guardian/` |

The checks run in GitHub Actions on Python 3.10 and 3.13 with read-only
permissions. See [MCP.md](MCP.md) for setup and [SECURITY.md](SECURITY.md)
for security reporting. Real compatibility in each agent still requires
testing in that agent.
