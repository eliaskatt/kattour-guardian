#!/usr/bin/env python3
"""Offline, bounded PR diff review. Heuristics, not security certification.

Accepts an array of GitHub pull-file objects, never executes PR code, and never
copies changed lines (including potential credentials) into its findings.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

VERSION = "0.6.0"
MAX_INPUT_BYTES = 2_000_000
MAX_FILES = 500
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
SECRET = re.compile(r"(?i)(?:api[_-]?key|client[_-]?secret|secret[_-]?key|password|access[_-]?token)\s*[:=]\s*['\"][A-Za-z0-9._/+=-]{12,}['\"]")
KEY = re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")
TLS = re.compile(r"(?i)(verify\s*=\s*False|rejectUnauthorized\s*:\s*false|NODE_TLS_REJECT_UNAUTHORIZED\s*=\s*['\"]?0)")
EVAL = re.compile(r"\b(?:eval|exec)\s*\(")
SHELL = re.compile(r"\bshell\s*=\s*True\b")
HTML = re.compile(r"\bdangerouslySetInnerHTML\b|\binnerHTML\s*=")
IMG = re.compile(r"<img\b[^>]*>", re.I)
DIV_CLICK = re.compile(r"<(?:div|span)\b[^>]*\bonClick\s*=", re.I)

RULES = {
    "KG-SEC-001": ("high", "Possible hard-coded credential", "Remove the secret from source, rotate it if exposed, and use a managed secret store."),
    "KG-SEC-002": ("high", "Private-key material may have been added", "Keep private keys out of source control and revoke exposed keys."),
    "KG-SEC-003": ("high", "TLS verification appears disabled", "Use certificate verification and document any test-only exceptions."),
    "KG-SEC-004": ("medium", "Dynamic evaluation needs review", "Avoid evaluating untrusted input; replace dynamic evaluation with explicit parsing."),
    "KG-SEC-005": ("medium", "Shell execution needs review", "Prefer argument arrays without shell=True; validate untrusted input."),
    "KG-SEC-006": ("medium", "HTML injection sink needs review", "Ensure untrusted HTML is not inserted without appropriate sanitization."),
    "KG-UX-001": ("medium", "Image may lack accessible text", "Provide meaningful alt text or alt=\"\" for decorative images."),
    "KG-UX-002": ("low", "Non-semantic click handler needs keyboard review", "Prefer a button or provide keyboard support, focusability, and semantics."),
}


def safe_path(value: str) -> str:
    """Encode untrusted names so reports cannot contain raw control/markdown text."""
    value = value[:250]
    return re.sub(r"[^a-zA-Z0-9_./+@-]", "_", value).lstrip("./") or "unknown"


def added_lines(patch: str):
    current = None
    for line in patch.splitlines():
        match = HUNK.match(line)
        if match:
            current = int(match.group(1))
        elif current is not None and line.startswith("+") and not line.startswith("+++"):
            yield current, line[1:]
            current += 1
        elif current is not None and line.startswith(" "):
            current += 1
        elif current is not None and line.startswith("-"):
            pass
        elif line.startswith("\\ No newline"):
            pass


def match_rules(line: str, path: str) -> list[str]:
    rules = []
    if SECRET.search(line) and not re.search(r"(?i)(example|placeholder|your[_-]?key|changeme|test[_-]?only)", line):
        rules.append("KG-SEC-001")
    if KEY.search(line):
        rules.append("KG-SEC-002")
    if TLS.search(line):
        rules.append("KG-SEC-003")
    if (path.endswith((".py", ".js", ".ts", ".jsx", ".tsx"))) and EVAL.search(line):
        rules.append("KG-SEC-004")
    if path.endswith(".py") and SHELL.search(line):
        rules.append("KG-SEC-005")
    if path.endswith((".js", ".jsx", ".ts", ".tsx", ".html")) and HTML.search(line):
        rules.append("KG-SEC-006")
    if path.endswith((".jsx", ".tsx", ".html", ".vue")):
        if any("alt=" not in tag.lower() for tag in IMG.findall(line)):
            rules.append("KG-UX-001")
        if DIV_CLICK.search(line) and not re.search(r"\brole\s*=", line):
            rules.append("KG-UX-002")
    return rules


def review(files: list[dict], max_findings: int = 60) -> dict:
    if not isinstance(files, list):
        raise ValueError("Expected a JSON array of changed-file records")
    if len(files) > MAX_FILES:
        raise ValueError(f"Too many changed files (limit {MAX_FILES})")
    findings = []
    no_patch = []
    changed = 0
    scanned = 0
    for entry in files:
        if not isinstance(entry, dict):
            raise ValueError("Each file record must be an object")
        path = safe_path(str(entry.get("filename", "unknown")))
        status = entry.get("status")
        if status == "removed":
            continue
        changed += 1
        patch = entry.get("patch")
        if not isinstance(patch, str):
            no_patch.append(path)
            continue
        scanned += 1
        for line_num, line in added_lines(patch):
            for rule in match_rules(line, path):
                severity, title, recommendation = RULES[rule]
                if len(findings) < max_findings:
                    findings.append({"rule_id": rule, "severity": severity, "confidence": "heuristic",
                                     "path": path, "line": line_num, "message": title,
                                     "recommendation": recommendation})
    findings.sort(key=lambda f: (0 if f["severity"] == "high" else 1 if f["severity"] == "medium" else 2,
                                 f["path"], f["line"], f["rule_id"]))
    return {"tool": "kattour-guardian-pr-review", "version": VERSION,
            "status": "partial" if no_patch else "completed",
            "counts": {"changed_files": changed, "patched_files": scanned, "unreviewed_files": len(no_patch),
                       "findings_returned": len(findings)},
            "unreviewed_paths": no_patch[:20],
            "findings": findings,
            "limitations": ["Added diff lines only; cannot establish exploitability or prove security.",
                            "No browser rendering, dependency audit, authorization analysis, or full-source context.",
                            "Missing GitHub patches (binary/large files) are unreviewed and require manual review.",
                            "Heuristic matches may be false positives; prioritize human verification."]}


def markdown(result: dict, max_chars: int = 8500) -> str:
    c = result["counts"]
    lines = ["## Kattour Guardian PR review (heuristic)", "",
             f"Status: **{result['status']}** | Files with patches: {c['patched_files']}/{c['changed_files']} | Findings: {c['findings_returned']}", "",
             "**Findings** (unverified; no secret values shown):", ""]
    if not result["findings"]:
        lines.append("No matches among supported added lines. This is not a clean security bill of health.")
    for f in result["findings"]:
        lines.append(f"- **{f['severity'].upper()} {f['rule_id']}** — `{f['path']}:{f['line']}`: {f['message']}. {f['recommendation']}")
    if c["unreviewed_files"]:
        lines.extend(["", f"**Coverage gap:** {c['unreviewed_files']} changed file(s) had no text patch; manual review required."])
    lines.extend(["", "**Not tested:** end-to-end behavior, runtime UI, dependency advisories, authorization semantics, and full codebase context."])
    text = "\n".join(lines) + "\n"
    if len(text) > max_chars:
        return text[:max_chars - 80].rsplit("\n", 1)[0] + "\n\n[Output truncated; use JSON artifact for full details.]\n"
    return text


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="-", help="GitHub PR files JSON path or '-' for stdin")
    parser.add_argument("--format", choices=("markdown", "json"), default="markdown")
    parser.add_argument("--max-findings", type=int, default=60)
    parser.add_argument("--max-output-chars", type=int, default=8500)
    args = parser.parse_args(argv)
    if not 1 <= args.max_findings <= 200 or not 500 <= args.max_output_chars <= 50000:
        parser.error("Invalid output limits")
    raw = sys.stdin.buffer.read(MAX_INPUT_BYTES + 1) if args.input == "-" else Path(args.input).read_bytes()
    if len(raw) > MAX_INPUT_BYTES:
        print("PR input exceeds size limit", file=sys.stderr)
        return 2
    try:
        result = review(json.loads(raw), max_findings=args.max_findings)
    except (ValueError, UnicodeError, TypeError) as exc:
        print(f"Invalid PR file data: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(result, indent=2))
    else:
        print(markdown(result, args.max_output_chars))
    return 0


if __name__ == "__main__":
    sys.exit(main())