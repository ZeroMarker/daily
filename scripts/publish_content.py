#!/usr/bin/env python3
"""Commit only validated daily inputs and atomically push main plus a version tag."""
import re
import subprocess
import os
from news_config import ROOT, release_date
from validate_content import main as validate


def git(*args, capture=False):
    return subprocess.run(['git', *args], cwd=ROOT, check=True, text=True,
                          capture_output=capture).stdout


def main():
    validate()
    if git('branch', '--show-current', capture=True).strip() != 'main':
        raise ValueError('Automatic publishing requires main')
    day = release_date().strftime('%Y_%m_%d')
    paths = [f'content/{day}/script.json', f'content/{day}/narration.zh.txt']
    if git('diff', '--cached', '--name-only', capture=True).strip():
        raise ValueError('Index must be empty before automatic publishing')
    git('add', '--', *paths)
    if git('diff', '--cached', '--name-only', capture=True).strip():
        git('commit', '-m', f'content: generate news daily {day}')
    versions = []
    for tag in git('tag', '--list', f'{day}-*', capture=True).splitlines():
        match = re.fullmatch(re.escape(day) + r'-(\d+)\.(\d+)\.(\d+)', tag)
        if match:
            versions.append(tuple(map(int, match.groups())))
    major, minor, patch = max(versions) if versions else (1, 0, -1)
    tag = f'{day}-{major}.{minor}.{patch + 1}'
    git('tag', tag)
    git('push', '--atomic', 'origin', 'HEAD:main', f'refs/tags/{tag}')
    if os.environ.get('GITHUB_OUTPUT'):
        with open(os.environ['GITHUB_OUTPUT'], 'a', encoding='utf-8') as output:
            output.write(f'tag={tag}\n')
    print(f'Published content: {tag}')


if __name__ == '__main__':
    main()
