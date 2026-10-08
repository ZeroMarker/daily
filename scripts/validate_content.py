#!/usr/bin/env python3
"""Validate the content contract before committing or synthesizing narration."""
import json
from news_config import content_dir, release_date


def validate(script, narration, day):
    errors = []
    items = script.get('items', [])
    if script.get('date') != day.isoformat():
        errors.append('script.date 与目标日期不一致')
    if len(items) < 3 or items[0].get('kind') != 'intro' or items[-1].get('kind') != 'outro':
        errors.append('内容必须包含开场、新闻和结尾')
    ids = [item.get('id') for item in items]
    if any(not id for id in ids) or len(set(ids)) != len(ids):
        errors.append('场景 id 必须非空且唯一')
    for item in items:
        if any(not isinstance(item.get(key), str) or not item[key].strip() for key in ('title', 'text', 'screenText')):
            errors.append(f'{item.get("id")} 缺少标题、旁白或关键点')
    expected = [item.get('text', '').strip() for item in items]
    actual = [p.strip() for p in narration.split('\n\n') if p.strip()]
    if expected != actual:
        errors.append('旁白分段与 items[].text 的数量、顺序或文本不一致')
    if errors:
        raise ValueError('\n'.join(errors))
    return items


def main():
    folder = content_dir()
    items = validate(json.loads((folder / 'script.json').read_text(encoding='utf-8')),
                     (folder / 'narration.zh.txt').read_text(encoding='utf-8'), release_date())
    print(f'OK: {len(items)} scenes and exact narration alignment')


if __name__ == '__main__':
    main()
