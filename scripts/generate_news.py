#!/usr/bin/env python3
"""Select fresh diverse stories and derive a source-backed daily script, no API key."""
import json
import os
import re
from collections import Counter
from datetime import datetime, time, timedelta
from difflib import SequenceMatcher
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from news_config import TIMEZONE, content_dir, release_date


def short(text, limit):
    text = ' '.join(text.split())
    if len(text) <= limit:
        return text
    prefix = text[:limit - 1]
    end = max(prefix.rfind(mark) for mark in '。！？；.!?')
    return prefix[:end + 1] if end >= limit // 2 else prefix.rstrip('，、；：,;: ') + '…'


def url_key(raw):
    url = urlsplit(raw)
    if url.scheme not in ('http', 'https') or not url.hostname:
        return ''
    query = [(key, value) for key, value in parse_qsl(url.query)
             if not key.lower().startswith('utm_') and key.lower() not in ('fbclid', 'gclid')]
    return urlunsplit((url.scheme.lower(), url.netloc.lower(), url.path.rstrip('/'), urlencode(sorted(query)), ''))


def similar(left, right):
    clean = lambda value: re.sub(r'[^\w\u4e00-\u9fff]', '', value.lower())
    return SequenceMatcher(None, clean(left), clean(right)).ratio() >= 0.78


def select(candidates, cutoff, hours=48, count=5, minimum=3, language='zh'):
    if hours <= 0 or count < minimum or minimum < 1:
        raise ValueError('NEWS_MAX_AGE_HOURS > 0 and NEWS_COUNT >= NEWS_MIN_COUNT >= 1 required')
    ranked = []
    for item in candidates:
        stamp = item.get('published', 0)
        if not isinstance(stamp, (int, float)) or not cutoff - hours * 3600 <= stamp <= cutoff:
            continue
        if not item.get('title') or not item.get('source') or not url_key(item.get('link', '')):
            continue
        if language == 'zh' and not re.search(r'[\u4e00-\u9fff]', item['title']):
            continue
        score = 4 * (1 - (cutoff - stamp) / (hours * 3600))
        score += 3 if re.search(r'[\u4e00-\u9fff]', item['title']) else 0
        score += 3 if item.get('category') == 'AI' else 2 if item.get('category') in ('科技', '数码') else 0
        ranked.append((score, stamp, item))
    ranked.sort(key=lambda row: (row[0], row[1], row[2]['link']), reverse=True)
    unique = []
    seen = set()
    seen_titles = []
    for _, _, item in ranked:
        key = url_key(item['link'])
        duplicate = key in seen or any(similar(item['title'], title) for title in seen_titles)
        seen.add(key)
        seen_titles.append(item['title'])
        if not duplicate:
            unique.append(item)
    chosen, sources = [], Counter()
    # First diversify sources, then fill remaining slots in ranked order.
    for limit in (1, count):
        for item in unique:
            if item in chosen or sources[item['source']] >= limit:
                continue
            chosen.append(item)
            sources[item['source']] += 1
            if len(chosen) == count:
                return chosen
    if len(chosen) < minimum:
        raise ValueError(f'仅 {len(chosen)} 条新鲜且不重复的新闻，少于最低 {minimum} 条；停止发布。')
    return chosen


def clean_summary(text):
    text = re.split(r'#?欢迎关注|查看全文|阅读全文|Continue reading|Read more', text, maxsplit=1, flags=re.I)[0]
    return text.strip().rstrip('.… ').strip()


def manifest(day, chosen):
    items = [dict(id='intro', kind='intro', title='AI 新闻日报',
                  text=f'今天是{day.month}月{day.day}日，这里是 AI 新闻日报。接下来，带你了解{len(chosen)}条值得关注的消息。',
                  screenText=f'今日 {len(chosen)} 条热点')]
    for index, candidate in enumerate(chosen, 1):
        headline = ' '.join(candidate['title'].split())
        summary = clean_summary(candidate.get('summary', ''))
        if not summary or similar(headline, summary):
            summary = headline
        # The headline carries the actual event; some RSS descriptions are slogans.
        description = headline if similar(headline, summary) else headline + '。' + summary
        narration = short(description, 130)
        if not narration.endswith(('。', '！', '？', '.', '!', '?', '…')):
            narration += '。'
        items.append(dict(id=f'news-{index}', kind='news', title=short(headline, 12),
                          articleTitle=headline, source=candidate['source'],
                          sourceUrl=candidate['link'], publishedAt=datetime.fromtimestamp(candidate['published'], TIMEZONE).isoformat(),
                          category=candidate.get('category', '新闻'),
                          text=f'{candidate["source"]}报道，{narration}',
                          screenText=short(headline, 28), summary=short(summary, 160)))
    items.append(dict(id='outro', kind='outro', title='明天见',
                      text='以上就是本期新闻日报。新闻原文链接见文字日报，关注我们，每天一起了解新的变化。',
                      screenText='关注 · 每天与你 AI 读新闻'))
    return dict(date=day.isoformat(), generation=dict(mode='rss-extractive', timezone=str(TIMEZONE)), items=items)


def main():
    day = release_date()
    now = datetime.now(TIMEZONE)
    if day > now.date():
        raise ValueError('不能生成未来日期的新闻日报')
    cutoff = min(now, datetime.combine(day + timedelta(days=1), time.min, TIMEZONE)).timestamp()
    directory = content_dir()
    candidates = json.loads((directory / 'candidates.json').read_text(encoding='utf-8'))
    chosen = select(candidates, cutoff, float(os.environ.get('NEWS_MAX_AGE_HOURS', '48')),
                    int(os.environ.get('NEWS_COUNT', '5')), int(os.environ.get('NEWS_MIN_COUNT', '3')),
                    os.environ.get('NEWS_LANGUAGE', 'zh'))
    data = manifest(day, chosen)
    # Both artifacts come from the same items; no separate narration editing step.
    (directory / 'script.json').write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (directory / 'narration.zh.txt').write_text('\n\n'.join(item['text'] for item in data['items']) + '\n', encoding='utf-8')
    print(f'Generated {len(chosen)} stories with source links → {directory}')


if __name__ == '__main__':
    main()
