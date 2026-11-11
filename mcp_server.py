#!/usr/bin/env python3
"""Kattour Guardian: local, read-only MCP stdio adapter. Python 3.10+."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "skills" / "kattour-guardian" / "scripts"))
import context_pack
import security_scan
import html_a11y
import log_compact

VERSION = "0.3.0"
PROTOCOLS = ("2025-11-25", "2025-06-18", "2025-03-26", "2024-11-05")

def tool(name, description, props, required=()):
    return {"name": name, "description": description,
            "inputSchema": {"type": "object", "properties": props,
                            "required": list(required), "additionalProperties": False},
            "annotations": {"readOnlyHint": True, "destructiveHint": False, "openWorldHint": False}}

TOOLS = [
    tool("guardian_context", "Capped project map or redacted snippets. Same-session hash delta. Character reduction is not billed token savings.",
         {"task": {"type": "string"}, "mode": {"type": "string", "enum": ["map", "snippets"]},
          "max_chars": {"type": "integer", "minimum": 350, "maximum": 20000},
          "max_files": {"type": "integer", "minimum": 1, "maximum": 40},
          "lines_per_file": {"type": "integer", "minimum": 1, "maximum": 30},
          "changed_only": {"type": "boolean"}, "reuse_unchanged": {"type": "boolean"}}, ["task"]),
    tool("guardian_security", "Offline read-only heuristic security review. Unverified leads, not a comprehensive audit.",
         {"path": {"type": "string"}, "max_findings": {"type": "integer", "minimum": 1, "maximum": 100}}),
    tool("guardian_a11y", "Static HTML alt/lang/viewport hints, not a WCAG or rendered-browser review.",
         {"path": {"type": "string"}, "max_findings": {"type": "integer", "minimum": 1, "maximum": 100}}),
    tool("guardian_compact_log", "Redacted error-focused log excerpt; review raw logs and possible secrets before any AI disclosure.",
         {"log": {"type": "string"}, "max_chars": {"type": "integer", "minimum": 150, "maximum": 12000},
          "context_lines": {"type": "integer", "minimum": 0, "maximum": 5}}, ["log"]),
    tool("guardian_usage", "Approximate character usage, not API billing or verified token savings.", {}),
]

def num(args, name, default, lo, hi):
    value = args.get(name, default)
    if type(value) is not int or not lo <= value <= hi:
        raise ValueError(f"{name} must be integer {lo}..{hi}")
    return value

def boolean(args, name, default=False):
    value = args.get(name, default)
    if type(value) is not bool:
        raise ValueError(f"{name} must be boolean")
    return value

def string(args, name, default="", length=500):
    value = args.get(name, default)
    if not isinstance(value, str) or len(value) > length:
        raise ValueError(f"{name} must be a string of up to {length} characters")
    return value

class Guardian:
    def __init__(self, root):
        if not root.is_dir():
            raise ValueError("Root must be an existing local directory")
        self.root = root.resolve(strict=True)
        self.snapshots = {}
        self.usage = {"context_calls": 0, "eligible_source_characters": 0,
                      "context_output_characters": 0, "unchanged_files_omitted": 0}
        self.initialized = False

    def path(self, relative):
        if not relative or Path(relative).is_absolute():
            raise ValueError("Path must be relative to the authorized root")
        dest = self.root
        for part in Path(relative).parts:
            if part == "..":
                raise ValueError("Parent traversal forbidden")
            dest = dest / part
            if dest.is_symlink():
                raise ValueError("Symlinks forbidden")
        dest = dest.resolve()
        if not dest.is_relative_to(self.root) or not dest.exists():
            raise ValueError("Path must exist within authorized root")
        return dest

    def call(self, name, args):
        known = next((x for x in TOOLS if x["name"] == name), None)
        if not known:
            raise LookupError("Unknown tool")
        if not isinstance(args, dict):
            raise ValueError("Arguments must be an object")
        if set(args) - set(known["inputSchema"]["properties"]):
            raise ValueError("Unknown tool argument")
        if name == "guardian_context":
            task = string(args, "task").strip()
            if not task or context_pack.SECRET_LINE.search(task):
                raise ValueError("Supply a nonempty task without credentials")
            mode = string(args, "mode", "map", 16)
            if mode not in ("map", "snippets"):
                raise ValueError("Mode must be map or snippets")
            budget = num(args, "max_chars", 4000, 350, 20000)
            limit = num(args, "max_files", 12, 1, 40)
            lines = num(args, "lines_per_file", 10, 1, 30)
            changed_only = boolean(args, "changed_only")
            reuse = boolean(args, "reuse_unchanged", True)
            changes = context_pack.get_git_changes(self.root) if changed_only else None
            key = (task, mode, changed_only)
            previous = self.snapshots.get(key, {}) if reuse else {}
            output, metrics, hashes = context_pack.build_bundle(
                self.root, task, mode, budget, limit, lines, changes, previous)
            if reuse:
                self.snapshots[key] = {**previous, **hashes}
            self.usage["context_calls"] += 1
            self.usage["eligible_source_characters"] += metrics["eligible_source_characters"]
            self.usage["context_output_characters"] += metrics["output_characters"]
            self.usage["unchanged_files_omitted"] += metrics["unchanged_omitted"]
            return output
        if name in ("guardian_security", "guardian_a11y"):
            target = self.path(string(args, "path", "."))
            limit = num(args, "max_findings", 20, 1, 100)
            result = security_scan.scan(target) if name == "guardian_security" else html_a11y.run(target)
            total = len(result["findings"])
            result["findings"] = result["findings"][:limit]
            result["total_findings"] = total
            result["findings_truncated"] = total > limit
            result["scan_path"] = target.relative_to(self.root).as_posix()
            if "unreadable_files" in result:
                result["unreadable_files_count"] = len(result["unreadable_files"])
                result["unreadable_files"] = result["unreadable_files"][:15]
            return json.dumps(result, ensure_ascii=False)
        if name == "guardian_compact_log":
            data = string(args, "log", length=200000)
            max_chars = num(args, "max_chars", 3000, 150, 12000)
            context = num(args, "context_lines", 1, 0, 5)
            return log_compact.compact(data, max_chars=max_chars, context=context)[0]
        if name == "guardian_usage":
            return json.dumps({**self.usage,
                "approximate_output_tokens": (self.usage["context_output_characters"] + 3) // 4,
                "warning": "4 chars/token is a rough estimate; NOT provider API token usage or measured savings."})
        raise LookupError("Unknown tool")

    def handle(self, request):
        if not isinstance(request, dict) or request.get("jsonrpc") != "2.0":
            return {"jsonrpc": "2.0", "id": None,
                    "error": {"code": -32600, "message": "Invalid JSON-RPC request"}}
        if "id" not in request:
            return None
        rid = request["id"]
        method = request.get("method")
        params = request.get("params", {})
        def ok(value):
            return {"jsonrpc": "2.0", "id": rid, "result": value}
        def err(code, message):
            return {"jsonrpc": "2.0", "id": rid, "error": {"code": code, "message": message}}
        if not isinstance(params, dict):
            return err(-32602, "Params must be an object")
        if method == "initialize":
            self.initialized = True
            version = params.get("protocolVersion")
            return ok({"protocolVersion": version if version in PROTOCOLS else PROTOCOLS[0],
                       "capabilities": {"tools": {"listChanged": False}},
                       "serverInfo": {"name": "kattour-guardian", "version": VERSION}})
        if not self.initialized:
            return err(-32002, "Initialize first")
        if method == "ping":
            return ok({})
        if method == "tools/list":
            return ok({"tools": TOOLS})
        if method == "tools/call":
            name = params.get("name")
            if not isinstance(name, str):
                return err(-32602, "Missing tool name")
            try:
                output = self.call(name, params.get("arguments", {}))
                return ok({"content": [{"type": "text", "text": output}], "isError": False})
            except LookupError:
                return err(-32602, "Unknown tool")
            except (ValueError, OSError) as exc:
                msg = str(exc).replace(str(self.root), "<project>")[:450]
                return ok({"content": [{"type": "text", "text": "Tool error: " + msg}], "isError": True})
        return err(-32601, "Method not found")

def main():
    parser = argparse.ArgumentParser(description="Kattour Guardian local MCP stdio server")
    parser.add_argument("--root", required=True, type=Path, help="Authorized local project root")
    args = parser.parse_args()
    server = Guardian(args.root)
    max_bytes = 1_000_000
    while True:
        raw = sys.stdin.buffer.readline(max_bytes + 1)
        if not raw:
            break
        if len(raw) > max_bytes:
            while raw and not raw.endswith(b"\n"):
                raw = sys.stdin.buffer.readline(max_bytes + 1)
            response = {"jsonrpc": "2.0", "id": None, "error":
                        {"code": -32600, "message": "Request too large"}}
        else:
            try:
                response = server.handle(json.loads(raw))
            except (ValueError, UnicodeError):
                response = {"jsonrpc": "2.0", "id": None, "error":
                            {"code": -32700, "message": "Invalid JSON"}}
        if response is not None:
            sys.stdout.write(json.dumps(response, ensure_ascii=False, separators=(",", ":")) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
