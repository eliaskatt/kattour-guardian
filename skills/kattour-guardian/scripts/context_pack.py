#!/usr/bin/env python3
"""Offline, bounded, task-oriented context selection for coding agents.

This is a deterministic prompt-size aid, NOT an AI tokenizer, secret scanner,
or a replacement for reading full files when required for correctness/security.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

SKIP_DIRS = {
    '.git', '.next', '.nuxt', '.output', '.turbo', '.venv', 'venv',
    'node_modules', 'vendor', 'dist', 'build', 'coverage', '__pycache__',
    '.idea', '.gradle', 'Pods', 'DerivedData', 'target', '.cache',
    '.pytest_cache', '.guardian-cache', '.kattour-cache',
}
EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs', '.php',
    '.rb', '.go', '.rs', '.java', '.kt', '.swift', '.dart', '.vue',
    '.svelte', '.html', '.css', '.scss', '.sass', '.less', '.sql',
    '.md', '.json', '.yml', '.yaml', '.toml', '.sh', '.bash',
}
SPECIAL_NAMES = {'Dockerfile', 'Makefile', 'Gemfile', 'Procfile', 'go.mod'}
SKIP_NAMES = {
    'package-lock.json', 'pnpm-lock.yaml', 'yarn.lock', 'Cargo.lock',
    'composer.lock', 'Gemfile.lock', 'poetry.lock', 'uv.lock',
    'bun.lock', 'bun.lockb', 'CHANGELOG.md',
}
SYMBOL_RE = re.compile(
    r'^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?'
    r'(?:def\s+|class\s+|function\s+|interface\s+|type\s+|'
    r'const\s+[a-zA-Z_$][\w$]*\s*=\s*(?:async\s*)?\(|'
    r'(?:pub\s+)?(?:fn|struct|enum|trait)\s+|'
    r'func\s+|@(?:app|router)\.|(?:GET|POST|PUT|DELETE)\s+)', re.I
)
SECRET_LINE = re.compile(
    r'-----BEGIN [^-]*PRIVATE KEY-----|\bAKIA[0-9A-Z]{16}\b|'
    r'\bgh[pousr]_[a-zA-Z0-9_]{20,}\b|\bsk_live_[a-zA-Z0-9]{12,}\b|'
    r'\bBearer\s+[A-Za-z0-9._~+/-]{16,}|'
    r'(?i:password|passwd|secret|private[_-]?key|api[_-]?key|access[_-]?token|refresh[_-]?token)'
    r'\s*[=:]\s*[\'\"][^\'\"]{4,}',
    re.I,
)
WORD_RE = re.compile(r'[a-zA-Z0-9_\u0600-\u06ff]+')
STOPWORDS = {
    'the', 'and', 'for', 'with', 'from', 'this', 'that', 'your', 'into',
    'have', 'using', 'work', 'make', 'file', 'files', 'improve', 'fix',
    'app', 'site', 'web', 'code', 'build', 'add', 'review',
    'على', 'في', 'من', 'الى', 'إلى', 'هذا', 'هذه', 'بدي', 'تحسين',
}


def terms(task: str) -> list[str]:
    return sorted({w.lower() for w in WORD_RE.findall(task) if len(w) >= 3 and w.lower() not in STOPWORDS})


def is_eligible(root: Path, path: Path, max_file_bytes: int) -> bool:
    if not path.is_file() or path.is_symlink():
        return False
    rel = path.relative_to(root)
    if any(part in SKIP_DIRS for part in rel.parts[:-1]):
        return False
    if any(part.startswith('.env') or part in {'secrets', '.ssh'} for part in rel.parts):
        return False
    if path.name in SKIP_NAMES or path.name.endswith(('.min.js', '.min.css', '.map', '.lock')):
        return False
    if path.suffix.lower() not in EXTENSIONS and path.name not in SPECIAL_NAMES:
        return False
    try:
        return path.stat().st_size <= max_file_bytes
    except OSError:
        return False


def get_git_changes(root: Path) -> set[str]:
    commands = [
        ['git', '-C', str(root), 'diff', '--name-only', '-z'],
        ['git', '-C', str(root), 'diff', '--cached', '--name-only', '-z'],
        ['git', '-C', str(root), 'ls-files', '--others', '--exclude-standard', '-z'],
    ]
    changed: set[str] = set()
    for command in commands:
        try:
            result = subprocess.run(command, capture_output=True, check=False, timeout=15)
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise ValueError(f'Git status unavailable: {exc}') from exc
        if result.returncode:
            raise ValueError('Unable to collect Git changes (is this a Git repository?)')
        changed.update(s.decode('utf-8', errors='replace') for s in result.stdout.split(b'\0') if s)
    return changed


def fingerprint(source: bytes) -> str:
    return hashlib.sha256(source).hexdigest()


def line_score(line: str, keywords: list[str]) -> int:
    low = line.lower()
    return sum(3 for word in keywords if word in low) + (1 if SYMBOL_RE.match(line) else 0)


def describe_file(path: str, source: str, keywords: list[str], mode: str, per_file_lines: int) -> str:
    lines = source.splitlines()
    if mode == 'map':
        symbols = [(n, s.strip()) for n, s in enumerate(lines, 1) if SYMBOL_RE.match(s)]
        selected = symbols[:min(per_file_lines, 8)]
        summary = ', '.join(f'L{n} {"[REDACTED: potential credential]" if SECRET_LINE.search(s) else s[:90]}' for n, s in selected)
        return f'- `{path}` ({len(lines)} lines)' + (f': {summary}' if summary else '')

    candidates = sorted(range(len(lines)), key=lambda i: (-line_score(lines[i], keywords), i))
    picks: set[int] = set()
    for i in candidates:
        if len(picks) >= per_file_lines:
            break
        if keywords and line_score(lines[i], keywords) <= 0:
            continue
        for j in (i - 1, i, i + 1):
            if 0 <= j < len(lines) and len(picks) < per_file_lines:
                picks.add(j)
    if not picks:
        picks = set(range(min(per_file_lines, len(lines))))
    payload = '\n'.join(f'{i + 1}: {"[REDACTED: potential credential]" if SECRET_LINE.search(lines[i]) else lines[i][:200]}' for i in sorted(picks))
    return f'### `{path}` ({len(lines)} lines)\n```text\n{payload}\n```'


def read_snapshot(path: Path, root: Path, task: str, mode: str) -> dict[str, str]:
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
    except (OSError, ValueError) as exc:
        raise ValueError(f'Cannot read snapshot: {exc}') from exc
    if data.get('schema') != 1 or data.get('root') != str(root) or data.get('task') != task or data.get('mode') != mode:
        raise ValueError('Snapshot scope does not match this repository, task and mode; start a fresh context bundle')
    hashes = data.get('hashes')
    if not isinstance(hashes, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in hashes.items()):
        raise ValueError('Malformed snapshot hash index')
    return hashes


def build_bundle(root: Path, task: str, mode: str, max_chars: int,
                 max_files: int, lines_per_file: int, changed: set[str] | None,
                 previous: dict[str, str]) -> tuple[str, dict, dict[str, str]]:
    keywords = terms(task)
    candidates = []
    scanned = 0
    source_chars = 0
    skipped_binary = 0
    unchanged_count = 0
    # Prune dependency/build directories before traversing them. This matters
    # for repositories with hundreds of thousands of generated files.
    paths = []
    for current, dirs, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS
                         and d not in {'secrets', '.ssh'}
                         and not d.startswith('.env')
                         and not (current_path / d).is_symlink())
        for filename in sorted(files):
            paths.append(current_path / filename)
    for path in paths:
        if not is_eligible(root, path, max_file_bytes=256 * 1024):
            continue
        rel = path.relative_to(root).as_posix()
        if changed is not None and rel not in changed:
            continue
        scanned += 1
        try:
            raw = path.read_bytes()
            if b'\0' in raw:
                skipped_binary += 1
                continue
            content = raw.decode('utf-8')
        except (OSError, UnicodeError):
            continue
        source_chars += len(content)
        digest = fingerprint(raw)
        if previous.get(rel) == digest:
            unchanged_count += 1
            continue
        path_score = sum(10 for keyword in keywords if keyword in rel.lower())
        content_score = sum(min(4, content.lower().count(keyword)) for keyword in keywords)
        score = path_score + content_score
        if path.name in {'package.json', 'pyproject.toml', 'requirements.txt', 'go.mod'}:
            score += 2
        candidates.append((score, rel, content, digest))

    candidates.sort(key=lambda item: (-item[0], item[1]))
    header = (
        '# Kattour Guardian — bounded project context\n'
        f'Task: {task}\nMode: {mode}; candidate files: {scanned}; '
        f'eligible source characters: {source_chars}; unchanged omitted: {unchanged_count}\n'
        'This is *selective context*, not a complete audit. Security validation must cover the full applicable scope.\n\n'
    )
    if len(header) > max_chars:
        raise ValueError('The character budget is too small to fit bundle metadata')
    chunks = [header]
    total = len(header)
    transmitted: dict[str, str] = {}
    for _, rel, content, digest in candidates[:max_files]:
        block = describe_file(rel, content, keywords, mode, lines_per_file) + '\n\n'
        if total + len(block) > max_chars:
            continue
        chunks.append(block)
        total += len(block)
        transmitted[rel] = digest
    if not transmitted:
        note = 'No additional files fit the budget or all selected files were unchanged. Increase --max-chars or reset the snapshot if needed.\n'
        chunks.append(note[:max(0, max_chars - total)])
        total = sum(len(p) for p in chunks)
    metrics = {
        'eligible_files': scanned,
        'eligible_source_characters': source_chars,
        'included_files': len(transmitted),
        'output_characters': total,
        'approximate_output_tokens': (total + 3) // 4,
        'unselected_or_truncated_files': len(candidates) - len(transmitted),
        'unchanged_omitted': unchanged_count,
        'skipped_binary_files': skipped_binary,
        'character_reduction_vs_eligible_source_percent':
            round(100 * (1 - total / source_chars), 1) if source_chars > 0 else None,
        'warning': 'Approximate tokens use a rough 4-characters/token estimate; real tokenizer usage and total savings vary by model and workflow.',
    }
    return ''.join(chunks), metrics, transmitted


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('path', nargs='?', default='.', help='Authorized local repository root')
    parser.add_argument('--task', required=True, help='Current task/question; used for relevance and cache scope')
    parser.add_argument('--mode', choices=('map', 'snippets'), default='map', help='Map (safer/smaller) or sanitized snippet mode')
    parser.add_argument('--max-chars', type=int, default=6000, help='Hard maximum output characters (not exact token limit)')
    parser.add_argument('--max-files', type=int, default=16)
    parser.add_argument('--lines-per-file', type=int, default=12)
    parser.add_argument('--changed-only', action='store_true', help='Inspect only Git modified/staged/untracked files')
    parser.add_argument('--snapshot-in', type=Path, help='Same-task snapshot from an earlier bundle (same live context only)')
    parser.add_argument('--snapshot-out', type=Path, help='Write hashes only; never source code')
    parser.add_argument('--metrics', action='store_true', help='Print measurable character counts to stderr (not model usage)')
    args = parser.parse_args()
    root = Path(args.path).resolve()
    if not root.is_dir():
        parser.error('Provide an existing local directory')
    if args.max_chars < 350 or args.max_files < 1 or args.lines_per_file < 1:
        parser.error('--max-chars >= 350, --max-files >= 1 and --lines-per-file >= 1 are required')
    try:
        changed = get_git_changes(root) if args.changed_only else None
        previous = read_snapshot(args.snapshot_in, root, args.task, args.mode) if args.snapshot_in else {}
        output, metrics, transmitted = build_bundle(root, args.task, args.mode, args.max_chars,
                                                    args.max_files, args.lines_per_file, changed, previous)
        if args.snapshot_out:
            if args.snapshot_out.is_symlink():
                raise ValueError('Refusing symlink snapshot destination')
            dest = args.snapshot_out.resolve()
            dest.parent.mkdir(parents=True, exist_ok=True)
            snapshot = {'schema': 1, 'root': str(root), 'task': args.task,
                        'mode': args.mode, 'hashes': {**previous, **transmitted}}
            dest.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    except ValueError as exc:
        parser.error(str(exc))
    print(output, end='')
    if args.metrics:
        print(json.dumps(metrics, ensure_ascii=False), file=sys.stderr)
    return 0


if __name__ == '__main__':
    sys.exit(main())
