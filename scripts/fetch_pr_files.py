#!/usr/bin/env python3
"""Read pull-request changed-file patches via GitHub API, for offline PR review.

Only fetches metadata and patch text. Does not execute PR code or transmit local files.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen

MAX_FILES = 500
MAX_PAGE_BYTES = 2_000_000


def get_files(repo: str, number: int, token: str) -> list[dict]:
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_.-]*/[a-zA-Z0-9][a-zA-Z0-9_.-]*", repo):
        raise ValueError("Invalid repository slug")
    if number < 1:
        raise ValueError("Invalid PR number")
    if not token:
        raise ValueError("GITHUB_TOKEN is required")
    files = []
    for page in range(1, 7):
        url = f"https://api.github.com/repos/{repo}/pulls/{number}/files?per_page=100&page={page}"
        request = Request(url, headers={"Authorization": f"Bearer {token}",
                                        "Accept": "application/vnd.github+json",
                                        "X-GitHub-Api-Version": "2022-11-28",
                                        "User-Agent": "Kattour-Guardian-PR-Review"})
        with urlopen(request, timeout=20) as response:
            raw = response.read(MAX_PAGE_BYTES + 1)
        if len(raw) > MAX_PAGE_BYTES:
            raise ValueError("GitHub PR page exceeds safe response size")
        entries = json.loads(raw)
        if not isinstance(entries, list):
            raise ValueError("Unexpected GitHub PR response")
        files.extend({"filename": entry.get("filename", "unknown"),
                      "status": entry.get("status", "modified"),
                      "patch": entry.get("patch")}
                     for entry in entries if isinstance(entry, dict))
        if len(files) > MAX_FILES:
            raise ValueError("PR has too many files for this bounded reviewer")
        if len(entries) < 100:
            return files
    raise ValueError("Unable to retrieve a complete bounded PR file list")


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--number", type=int, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        entries = get_files(args.repo or "", args.number, os.environ.get("GITHUB_TOKEN", ""))
        args.out.write_text(json.dumps(entries, ensure_ascii=True), encoding="utf-8")
    except (ValueError, OSError, json.JSONDecodeError) as exc:
        print(f"PR metadata retrieval failed: {type(exc).__name__}", file=sys.stderr)
        return 2
    print(f"Retrieved {len(entries)} changed-file entries (patches remain local)")
    return 0

if __name__ == "__main__":
    sys.exit(main())