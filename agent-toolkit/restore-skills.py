#!/usr/bin/env python3
"""Restore pinned shared skills with the official OpenAI installer; no overwrites."""
import argparse
import json
import pathlib
import shutil
import subprocess
import sys

base = pathlib.Path(__file__).resolve().parent
home = pathlib.Path.home()
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--apply', action='store_true', help='Actually install missing skills')
parser.add_argument('--installer', type=pathlib.Path, default=home / '.codex/skills/.system/skill-installer/scripts/install-skill-from-github.py')
args = parser.parse_args()
for item in json.loads((base / 'skills.lock.json').read_text()):
    names = item.get('names') or [pathlib.Path(p).name for p in item['paths']]
    for source, name in zip(item['paths'], names):
        target = home / '.agents/skills' / name
        if not target.exists():
            command = [sys.executable, str(args.installer), '--repo', item['repo'], '--ref', item['sha'], '--path', source, '--name', name, '--dest', str(target.parent), '--method', 'git']
            print('INSTALL', item['repo'], source, item['sha'])
            if args.apply:
                subprocess.run(command, check=True)
                if source == '.' and (target / '.git').is_dir():
                    shutil.rmtree(target / '.git')
                # The upstream description exceeds the Agent Skills 1024 character limit.
                if name == 'transitions-dev':
                    skill = target / 'SKILL.md'
                    text = skill.read_text()
                    _, front, body = text.split('---', 2)
                    # Preserve all other YAML fields and the complete instruction body.
                    import yaml
                    meta = yaml.safe_load(front)
                    meta['description'] = json.loads((base / 'skill-overrides.json').read_text())['transitions-dev']['description']
                    skill.write_text('---\n' + yaml.safe_dump(meta, allow_unicode=True, sort_keys=False) + '---' + body)
        else:
            print('KEEP', name)
        alias = home / '.claude/skills' / name
        if args.apply and target.exists() and not alias.exists() and not alias.is_symlink():
            alias.parent.mkdir(parents=True, exist_ok=True)
            alias.symlink_to(target, target_is_directory=True)
print('Codex、Pi、Gemini 使用 ~/.agents/skills；Claude 使用符號連結。重新啟動 Agent 後載入。')
