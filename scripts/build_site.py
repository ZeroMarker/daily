#!/usr/bin/env python3
"""Build the public magazine from committed daily scripts (stdlib only)."""
import json
import re
import shutil
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / 'dist' / 'pages'
REPO = 'https://github.com/ZeroMarker/daily'


def esc(value):
    return escape(str(value), quote=True)


def shell(title, body, prefix='./'):
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · AI 新闻日报</title><meta name="description" content="AI 新闻日报电子杂志：每天阅读科技、人工智能与世界新闻摘要。">
<link rel="stylesheet" href="{prefix}assets/style.css"></head>
<body><header class="masthead"><a class="brand" href="{prefix}index.html">AI 新闻日报<span>DAILY / 科技 · AI · 世界</span></a>
<nav aria-label="主导航"><a href="{prefix}index.html">杂志</a><a href="{prefix}archive.html">往期</a><a href="{REPO}/releases">视频</a></nav></header>
<main>{body}</main><footer><span>AI 新闻日报 · 每天读懂值得关注的变化</span><a href="{REPO}">项目源码 ↗</a><p>人工选题与编辑 · AI 配音与视频制作。来源名称见各条新闻。</p></footer></body></html>'''


def issue_link(issue, prefix='./'):
    return f'{prefix}issues/{issue["folder"]}.html'


def card(item, number, href=None):
    title = esc(item['title'])
    if href:
        title = f'<a href="{esc(href)}">{title}</a>'
    return f'''<article class="story" id="story-{number}"><div class="story-meta"><span>{number:02d} / {esc(item.get('category', '新闻'))}</span><span>{esc(item.get('source', '编辑部'))}</span></div>
<h2>{title}</h2><p class="keypoint">{esc(item.get('screenText', ''))}</p><p>{esc(item.get('summary') or item['text'])}</p></article>'''


def build():
    issues = []
    for path in sorted((ROOT / 'content').glob('*/script.json'), reverse=True):
        folder = path.parent.name
        if not re.fullmatch(r'\d{4}_\d{2}_\d{2}', folder):
            continue
        data = json.loads(path.read_text(encoding='utf-8'))
        if date.fromisoformat(data['date']).strftime('%Y_%m_%d') != folder:
            raise ValueError(f'Date mismatch: {path}')
        news = [item for item in data['items'] if item['kind'] == 'news']
        if not news:
            raise ValueError(f'No news in {path}')
        for item in news:
            if not item.get('title') or not item.get('text'):
                raise ValueError(f'Missing title or text in {path}')
        issues.append(dict(folder=folder, date=data['date'], news=news))
    if not issues:
        raise ValueError('No daily scripts found')
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    (OUTPUT / 'assets').mkdir(parents=True)
    (OUTPUT / 'issues').mkdir()
    shutil.copyfile(ROOT / 'site' / 'style.css', OUTPUT / 'assets' / 'style.css')
    (OUTPUT / '.nojekyll').touch()
    for issue in issues:
        contents = ''.join(f'<li><a href="#story-{n}">{esc(item["title"])}</a></li>' for n, item in enumerate(issue['news'], 1))
        stories = ''.join(card(item, n) for n, item in enumerate(issue['news'], 1))
        body = f'''<div class="eyebrow">DAILY EDITION / {esc(issue['date'])}</div><section class="issue-heading"><h1>今日新闻，<br>一页读完。</h1><div><p>{len(issue['news'])} 条精选 · 科技与世界的每日切片</p><a class="button secondary" href="{REPO}/releases">查看视频发行 ↗</a></div></section>
<div class="reading-layout"><aside><h2>本期目录</h2><ol>{contents}</ol><a href="../archive.html">浏览全部往期 →</a></aside><section class="stories" aria-label="本期新闻">{stories}</section></div>'''
        (OUTPUT / 'issues' / f'{issue["folder"]}.html').write_text(shell(issue['date'] + ' 电子杂志', body, '../'), encoding='utf-8')
    latest = issues[0]
    lead = latest['news'][0]
    cards = ''.join(card(item, n, issue_link(latest) + f'#story-{n}') for n, item in enumerate(latest['news'], 1))
    body = f'''<div class="eyebrow">THE DAILY MAGAZINE / 最新一期 · {esc(latest['date'])}</div>
<section class="cover"><div><div class="cover-label">每天一页，看见变化</div><h1>科技向前。<br>世界更新。</h1><p>从人工智能到日常科技，读懂今天值得关注的重要消息。</p><a class="button" href="{issue_link(latest)}">阅读本期杂志 <span>↗</span></a></div>
<div class="cover-story"><span class="edition">{esc(latest['date'].replace('-', ' / '))}</span><div class="cover-mark" aria-hidden="true">AI<span>DAILY</span></div><span class="eyebrow">本期焦点 / {esc(lead.get('category', '新闻'))}</span><h2>{esc(lead['title'])}</h2><p>{esc(lead.get('screenText', ''))}</p></div></section>
<div class="section-title"><h2>本期精选</h2><span>{len(latest['news']):02d} STORIES</span></div><section class="grid" aria-label="最新新闻">{cards}</section>
<div class="archive-cta"><p>每一天，都是新的一期。</p><a href="./archive.html">浏览历史杂志 →</a></div>'''
    (OUTPUT / 'index.html').write_text(shell('电子杂志', body), encoding='utf-8')
    rows = ''.join(f'''<a class="archive-row" href="{issue_link(issue)}"><time datetime="{esc(issue['date'])}">{esc(issue['date'])}</time><div><h2>{esc(issue['news'][0]['title'])}</h2><p>{len(issue['news'])} 条新闻 · {' / '.join(esc(c) for c in dict.fromkeys(item.get('category', '新闻') for item in issue['news']))}</p></div><span aria-hidden="true">↗</span></a>''' for issue in issues)
    (OUTPUT / 'archive.html').write_text(shell('往期杂志', f'<div class="eyebrow">THE ARCHIVE / {len(issues)} 期</div><h1 class="archive-heading">把每一天，<br>留在这里。</h1><section aria-label="历史期刊">{rows}</section>'), encoding='utf-8')
    print(f'Built {len(issues)} magazine issue(s) → {OUTPUT}')


if __name__ == '__main__':
    build()
