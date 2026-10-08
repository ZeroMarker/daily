#!/usr/bin/env python3
"""Build the public magazine from committed daily scripts (stdlib only)."""
import json
import os
import re
import shutil
from datetime import date
from html import escape
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / 'dist' / 'pages'
REPO = 'https://github.com/ZeroMarker/daily'


def esc(value):
    return escape(str(value), quote=True)


def shell(title, body, prefix='./', folder=''):
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · AI 新闻日报</title><meta name="description" content="AI 新闻日报电子杂志：每天阅读科技、人工智能与世界新闻摘要。">
<link rel="stylesheet" href="{prefix}assets/style.css"></head>
<body><header class="masthead"><a class="brand" href="{prefix}index.html">AI 新闻日报<span>DAILY / 科技 · AI · 世界</span></a>
<nav aria-label="主导航"><a href="{prefix}index.html">杂志</a><a href="{prefix}issues/{folder}.html">日报</a><a href="{prefix}videos/{folder}.html">视频</a></nav></header>
<main>{body}</main><footer><span>AI 新闻日报 · 每天读懂值得关注的变化</span><a href="{REPO}">项目源码 ↗</a><p>人工选题与编辑 · AI 配音与视频制作。来源名称见各条新闻。</p></footer></body></html>'''


def issue_link(issue, prefix='./'):
    return f'{prefix}issues/{issue["folder"]}.html'


def card(item, number, href=None):
    title = esc(item['title'])
    if href:
        title = f'<a href="{esc(href)}">{title}</a>'
    return f'''<article class="story" id="story-{number}"><div class="story-meta"><span>{number:02d} / {esc(item.get('category', '新闻'))}</span><span>{esc(item.get('source', '编辑部'))}</span></div>
<h2>{title}</h2><p class="keypoint">{esc(item.get('screenText', ''))}</p><p>{esc(item.get('summary') or item['text'])}</p></article>'''


def load_releases():
    """Fetch published release assets; allow a local snapshot for offline builds."""
    snapshot = os.environ.get('RELEASES_FILE')
    if snapshot:
        return json.loads(Path(snapshot).read_text(encoding='utf-8'))
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'daily-magazine'}
    if os.environ.get('GH_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
    releases = []
    page = 1
    while True:
        request = Request(f'https://api.github.com/repos/ZeroMarker/daily/releases?per_page=100&page={page}', headers=headers)
        with urlopen(request, timeout=30) as response:
            batch = json.load(response)
        releases.extend(batch)
        if len(batch) < 100:
            return releases
        page += 1


def videos_for(issue, releases):
    videos = []
    for release in releases:
        if release.get('draft') or release.get('prerelease'):
            continue
        tag = release['tag_name']
        match = re.fullmatch(re.escape(issue['folder']) + r'-(\d+)\.(\d+)\.(\d+)', tag)
        if match:
            version = tuple(int(part) for part in match.groups())
            label = '.'.join(match.groups())
        elif tag == 'news-' + issue['date']:
            version, label = (-1, -1, -1), '早期版本'
        else:
            continue
        for asset in release.get('assets', []):
            if asset['name'].endswith('.mp4'):
                videos.append(dict(version=version, label=label, name=asset['name'],
                                   url=asset['browser_download_url'], release=release['html_url']))
    return sorted(videos, key=lambda video: (video['version'], video['name']), reverse=True)


def breadcrumbs(issue, video=False):
    daily = f'<a href="../issues/{issue["folder"]}.html">{esc(issue["date"])} 日报</a>' if video else f'<span aria-current="page">{esc(issue["date"])} 日报</span>'
    end = '<span aria-hidden="true">→</span><span aria-current="page">视频</span>' if video else ''
    return f'<nav class="breadcrumbs" aria-label="阅读路径"><a href="../index.html">杂志</a><span aria-hidden="true">→</span>{daily}{end}</nav>'


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
    releases = load_releases()
    latest = issues[0]
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    (OUTPUT / 'assets').mkdir(parents=True)
    (OUTPUT / 'issues').mkdir()
    (OUTPUT / 'videos').mkdir()
    (OUTPUT / 'media').mkdir()
    shutil.copyfile(ROOT / 'site' / 'style.css', OUTPUT / 'assets' / 'style.css')
    (OUTPUT / '.nojekyll').touch()
    for issue in issues:
        contents = ''.join(f'<li><a href="#story-{n}">{esc(item["title"])}</a></li>' for n, item in enumerate(issue['news'], 1))
        stories = ''.join(card(item, n) for n, item in enumerate(issue['news'], 1))
        body = f'''{breadcrumbs(issue)}<div class="eyebrow">DAILY EDITION / {esc(issue['date'])}</div><section class="issue-heading"><h1>今日新闻，<br>一页读完。</h1><div><p>{len(issue['news'])} 条精选 · 科技与世界的每日切片</p><a class="button secondary" href="../videos/{issue['folder']}.html">观看当日日报视频 →</a></div></section>
<div class="reading-layout"><aside><h2>本期目录</h2><ol>{contents}</ol><a href="../archive.html">浏览历史日报 →</a></aside><section class="stories" aria-label="本期新闻">{stories}</section></div>'''
        (OUTPUT / 'issues' / f'{issue["folder"]}.html').write_text(shell(issue['date'] + ' 日报', body, '../', issue['folder']), encoding='utf-8')
        videos = videos_for(issue, releases)
        if videos:
            video = videos[0]
            # Serve the latest MP4 from Pages: Release attachment redirects can
            # be blocked when a browser loads them inside a video element.
            request = Request(video['url'], headers={'User-Agent': 'daily-magazine'})
            with urlopen(request, timeout=30) as response:
                with (OUTPUT / 'media' / f'{issue["folder"]}.mp4').open('wb') as destination:
                    shutil.copyfileobj(response, destination)
            versions = ''.join(f'<li><span>{esc(v["label"])}</span><a href="{esc(v["url"])}">下载 MP4</a><a href="{esc(v["release"])}">发行详情 ↗</a></li>' for v in videos)
            player = f'''<section class="video-layout"><div class="player"><video controls playsinline preload="none" aria-label="{esc(issue['date'])} 日报视频"><source src="../media/{issue['folder']}.mp4" type="video/mp4">请使用下方链接下载视频。</video></div><div><h2>最新版本 · {esc(video['label'])}</h2><p>与当日日报对应的竖版新闻视频。</p><a class="button" href="{esc(video['url'])}">下载视频 MP4 ↗</a><p><a href="{esc(video['release'])}">打开发行页面 ↗</a></p><h2>全部视频版本</h2><ul class="versions">{versions}</ul></div></section>'''
        else:
            player = '<section class="empty-state"><h2>当日视频尚未发布</h2><p>可以先阅读日报，视频发布后会显示在这里。</p><a href="../issues/' + issue['folder'] + '.html">返回当日日报 →</a></section>'
        video_body = f'''{breadcrumbs(issue, video=True)}<div class="eyebrow">DAILY VIDEO / {esc(issue['date'])}</div><h1 class="video-heading">把日报，<br>听给你看。</h1>{player}'''
        (OUTPUT / 'videos' / f'{issue["folder"]}.html').write_text(shell(issue['date'] + ' 视频', video_body, '../', issue['folder']), encoding='utf-8')
    lead = latest['news'][0]
    rows = ''.join(f'''<a class="archive-row" href="{issue_link(issue)}"><time datetime="{esc(issue['date'])}">{esc(issue['date'])}</time><div><h2>{esc(issue['news'][0]['title'])}</h2><p>{len(issue['news'])} 条新闻 · 阅读当日日报</p></div><span aria-hidden="true">↗</span></a>''' for issue in issues)
    body = f'''<div class="eyebrow">THE DAILY MAGAZINE / 最新一期 · {esc(latest['date'])}</div>
<section class="cover"><div><div class="cover-label">每天一页，看见变化</div><h1>科技向前。<br>世界更新。</h1><p>从人工智能到日常科技，读懂今天值得关注的重要消息。</p><a class="button" href="{issue_link(latest)}">阅读最新日报 <span>↗</span></a></div>
<div class="cover-story"><span class="edition">{esc(latest['date'].replace('-', ' / '))}</span><div class="cover-mark" aria-hidden="true">AI<span>DAILY</span></div><span class="eyebrow">本期焦点 / {esc(lead.get('category', '新闻'))}</span><h2>{esc(lead['title'])}</h2><p>{esc(lead.get('screenText', ''))}</p></div></section>
<div class="section-title"><h2>日报目录</h2><span>{len(issues):02d} DAILY EDITIONS</span></div><section aria-label="日报目录">{rows}</section>
<div class="archive-cta"><p>每一天，都是新的一期。</p><a href="./archive.html">浏览历史日报 →</a></div>'''
    (OUTPUT / 'index.html').write_text(shell('电子杂志', body, folder=latest['folder']), encoding='utf-8')
    rows = ''.join(f'''<a class="archive-row" href="{issue_link(issue)}"><time datetime="{esc(issue['date'])}">{esc(issue['date'])}</time><div><h2>{esc(issue['news'][0]['title'])}</h2><p>{len(issue['news'])} 条新闻 · {' / '.join(esc(c) for c in dict.fromkeys(item.get('category', '新闻') for item in issue['news']))}</p></div><span aria-hidden="true">↗</span></a>''' for issue in issues)
    (OUTPUT / 'archive.html').write_text(shell('历史日报', f'<div class="eyebrow">THE ARCHIVE / {len(issues)} 期</div><h1 class="archive-heading">把每一天，<br>留在这里。</h1><section aria-label="历史日报">{rows}</section>', folder=latest['folder']), encoding='utf-8')
    print(f'Built {len(issues)} magazine issue(s) → {OUTPUT}')


if __name__ == '__main__':
    build()
