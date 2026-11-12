#!/usr/bin/env python3
"""Offline skill layout and local MCP stdio compatibility smoke checks."""
from __future__ import annotations
import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LAYOUTS = {
    "codex": ".agents/skills/kattour-guardian",
    "claude": ".claude/skills/kattour-guardian",
    "cursor": ".cursor/skills/kattour-guardian",
    "copilot": ".github/skills/kattour-guardian",
    "gemini": ".gemini/skills/kattour-guardian",
}
REQUIRED = (
    "mcp_server.py", "scripts/validate.py", "scripts/pr_review.py",
    "scripts/visual_compare.py", "scripts/token_benchmark.py",
    "skills/kattour-guardian/SKILL.md",
    "skills/kattour-guardian/scripts/context_pack.py",
    "skills/kattour-guardian/scripts/security_scan.py",
)

def inspect_skill(folder: Path) -> str:
    content = (folder / "SKILL.md").read_text(encoding="utf-8")
    if not content.startswith("---\n") or "\n---\n" not in content:
        raise ValueError("Missing SKILL.md frontmatter")
    front, body = content.split("\n---\n", 1)
    if not re.search(r"(?m)^name:\s*kattour-guardian\s*$", front):
        raise ValueError("Incorrect skill name")
    version = re.search(r'(?m)^\s*version:\s*["\x27]?(\d+\.\d+\.\d+)', front)
    if not version:
        raise ValueError("Missing skill version")
    if not body.strip():
        raise ValueError("Empty skill body")
    for path in re.findall(r"\]\((references/[^)\s#]+)", body):
        dest = (folder / path).resolve()
        if not dest.is_relative_to(folder.resolve()) or not dest.is_file():
            raise ValueError("Broken skill reference")
    return version.group(1)

def package_check(root: Path) -> dict:
    for file in REQUIRED:
        if not (root / file).is_file():
            raise ValueError("Missing required file: " + file)
    skill = root / "skills/kattour-guardian"
    if any(p.is_symlink() for p in skill.rglob("*")):
        raise ValueError("Skill contains symbolic links")
    version = inspect_skill(skill)
    source = (root / "mcp_server.py").read_text(encoding="utf-8")
    server_version = re.search(r'(?m)^VERSION\s*=\s*"(\d+\.\d+\.\d+)"', source)
    if not server_version or server_version.group(1) != version:
        raise ValueError("Skill and MCP versions do not match")
    if "[" + version + "]" not in (root / "CHANGELOG.md").read_text(encoding="utf-8"):
        raise ValueError("Release changelog entry missing")
    for agent, path in LAYOUTS.items():
        with tempfile.TemporaryDirectory() as temp:
            dest = Path(temp) / path
            shutil.copytree(skill, dest)
            if inspect_skill(dest) != version or not (dest / "scripts/context_pack.py").is_file():
                raise ValueError("Broken installation layout: " + agent)
    return {"version": version, "filesystem_layouts": list(LAYOUTS),
            "note": "Layout tests do not launch external agent clients."}

def mcp_check(root: Path) -> dict:
    with tempfile.TemporaryDirectory() as temp:
        packets = [
            {"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{}}},
            {"jsonrpc":"2.0","method":"notifications/initialized"},
            {"jsonrpc":"2.0","id":2,"method":"tools/list"},
            {"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"guardian_usage","arguments":{}}},
            {"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"guardian_security","arguments":{"path":"../outside"}}},
        ]
        proc = subprocess.run(
            [sys.executable,str(root / "mcp_server.py"),"--root",temp],
            input="\n".join(json.dumps(p) for p in packets) + "\n",
            text=True, capture_output=True, timeout=20, check=False)
    if proc.returncode or len(proc.stdout) > 250000:
        raise ValueError("MCP process failed")
    try:
        rows = [json.loads(line) for line in proc.stdout.splitlines()]
        messages = {row["id"]:row for row in rows}
        if len(rows) != 4 or set(messages) != {1,2,3,4}:
            raise ValueError("Unexpected JSON-RPC messages")
        if messages[1]["result"]["protocolVersion"] != "2025-06-18":
            raise ValueError("MCP handshake failed")
        tools = messages[2]["result"]["tools"]
        names = {item["name"] for item in tools}
        if not {"guardian_context","guardian_usage","guardian_security"} <= names:
            raise ValueError("MCP tools missing")
        if any("inputSchema" not in item for item in tools):
            raise ValueError("Tool schema missing")
        if messages[3]["result"]["isError"] or not messages[4]["result"]["isError"]:
            raise ValueError("MCP tool invocation or path guard failed")
    except (TypeError, KeyError, IndexError, json.JSONDecodeError) as exc:
        raise ValueError("Malformed MCP JSON-RPC") from exc
    if proc.stderr.strip():
        raise ValueError("MCP emitted unexpected stderr")
    return {"protocol":"2025-06-18","transport":"stdio","tools":len(tools),
            "path_traversal_rejected":True}

def run(root: Path) -> dict:
    root = root.resolve(strict=True)
    return {"status":"passed","skill":package_check(root),"mcp":mcp_check(root),
            "limits":["No third-party agent client was installed or run.",
                      "No security certification or measured billable token reduction."]}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root",type=Path,default=ROOT)
    parser.add_argument("--json",action="store_true")
    args = parser.parse_args()
    try:
        result = run(args.root)
    except (ValueError,OSError,subprocess.TimeoutExpired) as exc:
        parser.exit(1, "Compatibility smoke FAILED: " + str(exc)[:180] + "\n")
    print(json.dumps(result,indent=2) if args.json else "PASS: local skill layouts and MCP stdio")
