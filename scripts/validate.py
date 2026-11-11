#!/usr/bin/env python3
"""Validate bundled Agent Skills frontmatter and local reference links without dependencies."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS_DIR = ROOT / 'skills'
NAME_RE = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
LINK_RE = re.compile(r'\[[^\]]+\]\((references/[^)#]+)(?:#[^)]*)?\)')


def validate(skill_file: Path) -> list[str]:
    errors = []
    text = skill_file.read_text(encoding='utf-8')
    if not text.startswith('---\n'):
        return [f'{skill_file}: missing YAML frontmatter']
    pieces = text.split('\n---\n', 1)
    if len(pieces) != 2:
        return [f'{skill_file}: missing frontmatter closing ---']
    block, body = pieces
    values = {}
    for line in block.splitlines()[1:]:
        if line and not line.startswith((' ', '\t')) and ':' in line:
            k, v = line.split(':', 1)
            values[k.strip()] = v.strip().strip('"\'')
    name = values.get('name', '')
    description = values.get('description', '')
    if not NAME_RE.fullmatch(name) or len(name) > 64 or name != skill_file.parent.name:
        errors.append(f'{skill_file}: invalid name or name does not match directory')
    if not 1 <= len(description) <= 1024:
        errors.append(f'{skill_file}: description length invalid')
    if 'use when' not in description.lower():
        errors.append(f'{skill_file}: description should explain when to use skill')
    if not body.strip():
        errors.append(f'{skill_file}: instructions empty')
    for reference in LINK_RE.findall(body):
        if not (skill_file.parent / reference).is_file():
            errors.append(f'{skill_file}: missing reference {reference}')
    return errors


def main() -> int:
    files = sorted(SKILLS_DIR.glob('*/SKILL.md'))
    if not files:
        print('ERROR: No skills found')
        return 1
    all_errors = [err for skill in files for err in validate(skill)]
    for error in all_errors:
        print('ERROR:', error)
    if all_errors:
        return 1
    print(f'Validated {len(files)} Agent Skill(s): ' + ', '.join(p.parent.name for p in files))
    return 0


if __name__ == '__main__':
    sys.exit(main())
