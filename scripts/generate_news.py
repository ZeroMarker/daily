#!/usr/bin/env python3
"""Select fresh diverse stories and derive a source-backed daily script, no API key."""
import json
import math
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


MARKETING = re.compile(
    r'优惠|折扣|限时|秒杀|领券|优惠券|低至|到手价|促销|直降|特价|首发价|券后|抽奖|福利|赞助|广告|推广|'
    r'好物|种草|值得买|开箱|限免|团购|包邮|官方旗舰店|京东|天猫|拼多多|双(11|十一|12)|618|黑五|'
    r'招聘|报名|直播预告|课程|训练营|峰会|大会议程|白皮书下载|扫码|添加微信|点击|立即(购买|抢购|预约)|'
    r'¥\s*\d|\d+\s*元起|元/月|亿元补贴|\bsponsored\b|\bdeal(s)?\b|\bsale\b', re.I)
DIGEST = re.compile(r'早报|晚报|午报|日报|周报|周刊|一周|盘点|汇总|速览|快讯合集|8点1氪|今日要闻|\d+\s*条|Newsletter|Briefing', re.I)
HYPE_PREFIX = re.compile(r'^(?:[【\[［][^】\]］]{1,12}[】\]］]|(?:突发|重磅|独家|刚刚|震惊|快讯|最新|官宣)[！!｜|:：\s]+)+')
# Features, opinion and clickbait read like stories, not today's events.
FEATURE = re.compile(r'背后|你不知道|的故事|线索|揭秘|谜团|太甚|一文|看懂|深度|专访|对话|观察|评论|随笔|为什么|为何|如何|怎么|[？?]|吗$', re.I)
HYPE = re.compile(r'斩杀|吊打|炸裂|封神|杀疯|史上最|颠覆|震撼|王炸|逆天|太强了|一切$')
MIN_SUMMARY = 15
SUMMARY_BUDGET = 100
DATELINE = re.compile(r'^[^，,。]{0,20}?\d{1,2}\s*月\s*\d{1,2}\s*日(?:消息|电|讯)?[，,：:\s]*')


def clean_title(title):
    title = HYPE_PREFIX.sub('', ' '.join(title.split())).strip(' ！!｜|')
    # Drop hype clauses ("超级性价比斩杀一切") but keep the factual clause.
    parts = [part for part in re.split(r'(?<=[，,！!])', title) if not HYPE.search(part)]
    return ''.join(parts).strip(' ，,！!') or title


def brief(headline, limit=20):
    """Screen headline: the leading clause, never cut inside a number like 4.5%."""
    lead = re.split(r'[：:｜|，,]', headline)[0].strip()
    if len(lead) < 6:
        lead = headline
    out = ''
    for word in lead.split():
        if len(out) + len(word) + 1 > limit:
            break
        out = f'{out} {word}'.strip()
    if len(out) >= 6:
        return out
    return lead if len(lead) <= limit else lead[:limit - 1] + '…'


def is_marketing(item):
    title = item.get('title', '')
    return bool(MARKETING.search(title) or DIGEST.search(title) or FEATURE.search(title)
                or len(MARKETING.findall(item.get('summary', '')[:300])) >= 2)


def features(item):
    text = (clean_title(item['title']) + ' ') * 2 + clean_summary(item.get('summary', ''))[:200]
    text = text.lower()
    bag = Counter()
    for run in re.findall(r'[\u4e00-\u9fff]+', text):
        bag.update(run[i:i + 2] for i in range(len(run) - 1))
    bag.update(word for word in re.findall(r'[a-z][a-z0-9.+-]{1,}|\d{2,}', text))
    return bag


def similarity_graph(items):
    bags = [features(item) for item in items]
    df = Counter(term for bag in bags for term in bag)
    total = len(items)
    vectors = []
    for bag in bags:
        # Very common grams ("发布", "公司") carry no event identity.
        vec = {term: count * math.log((1 + total) / (1 + df[term])) for term, count in bag.items() if df[term] <= max(3, total * 0.2)}
        norm = math.sqrt(sum(v * v for v in vec.values())) or 1
        vectors.append({term: v / norm for term, v in vec.items()})
    sims = [[0.0] * total for _ in range(total)]
    for i in range(total):
        for j in range(i + 1, total):
            left, right = vectors[i], vectors[j]
            if len(left) > len(right):
                left, right = right, left
            sims[i][j] = sims[j][i] = sum(v * right.get(term, 0) for term, v in left.items())
    return sims


def pagerank(sims, items, prior, damping=0.85, threshold=0.12, rounds=60):
    """Weighted PageRank: a story is important when stories from *other* outlets echo it."""
    n = len(items)
    weights = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j and sims[i][j] >= threshold:
                weights[i][j] = sims[i][j] * (1.0 if items[i]['source'] != items[j]['source'] else 0.25)
    out = [sum(row) for row in weights]
    total_prior = sum(prior) or 1
    teleport = [p / total_prior for p in prior]
    rank = teleport[:]
    for _ in range(rounds):
        dangling = sum(rank[i] for i in range(n) if not out[i])
        rank = [(1 - damping) * teleport[j] + damping * (
                    dangling * teleport[j] + sum(rank[i] * weights[i][j] / out[i] for i in range(n) if out[i] and weights[i][j]))
                for j in range(n)]
    return rank


def select(candidates, cutoff, hours=48, count=5, minimum=3, language='zh'):
    if hours <= 0 or count < minimum or minimum < 1:
        raise ValueError('NEWS_MAX_AGE_HOURS > 0 and NEWS_COUNT >= NEWS_MIN_COUNT >= 1 required')
    pool, seen = [], set()
    for item in candidates:
        stamp = item.get('published', 0)
        if not isinstance(stamp, (int, float)) or not cutoff - hours * 3600 <= stamp <= cutoff:
            continue
        if not item.get('title') or not item.get('source') or not url_key(item.get('link', '')):
            continue
        if language == 'zh' and not re.search(r'[\u4e00-\u9fff]', item['title']):
            continue
        key = url_key(item['link'])
        if key in seen or is_marketing(item):
            continue
        seen.add(key)
        pool.append(item)
    if not pool:
        raise ValueError(f'仅 0 条新鲜且不重复的新闻，少于最低 {minimum} 条；停止发布。')
    prior = [1 + 1.5 * (1 - (cutoff - item['published']) / (hours * 3600))
             + (0.5 if item.get('category') == 'AI' else 0) for item in pool]
    sims = similarity_graph(pool)
    rank = pagerank(sims, pool, prior)
    order = sorted(range(len(pool)), key=lambda i: (rank[i], pool[i]['published'], pool[i]['link']), reverse=True)
    # Collapse each event into one cluster; coverage breadth across outlets lifts the event.
    assigned, clusters = set(), []
    for i in order:
        if i in assigned:
            continue
        members = [j for j in order if j not in assigned and (j == i or sims[i][j] >= 0.3
                   or similar(clean_title(pool[i]['title']), clean_title(pool[j]['title'])))]
        assigned.update(members)
        outlets = {pool[j]['source'] for j in members}
        score = sum(rank[j] for j in members) * (1 + 0.6 * (len(outlets) - 1))
        # Link the top-ranked report, but borrow the most informative summary in the cluster.
        best = max((clean_summary(pool[j].get('summary', '')) for j in members), key=len)
        if len(best) < MIN_SUMMARY:
            continue  # Title-only items (e.g. "点击查看原文") cannot be narrated or cross-checked.
        clusters.append((score, pool[i]['published'], dict(pool[i], summary=best, outlets=sorted(outlets))))
    clusters.sort(key=lambda row: (row[0], row[1], row[2]['link']), reverse=True)
    chosen, sources = [], Counter()
    for limit in (1, 2, count):
        for _, _, item in clusters:
            if item in chosen or sources[item['source']] >= limit:
                continue
            chosen.append(item)
            sources[item['source']] += 1
            if len(chosen) == count:
                break
        if len(chosen) == count:
            break
    if len(chosen) < minimum:
        raise ValueError(f'仅 {len(chosen)} 条新鲜且不重复的新闻，少于最低 {minimum} 条；停止发布。')
    # Keep ranking order (not diversification-pass order) for the broadcast.
    rank_of = {id(row[2]): index for index, row in enumerate(clusters)}
    return sorted(chosen, key=lambda item: rank_of[id(item)])


def clean_summary(text):
    text = re.split(r'#?欢迎关注|查看全文|阅读全文|点击查看|Continue reading|Read more', text, maxsplit=1, flags=re.I)[0]
    text = DATELINE.sub('', text.strip())
    return text.strip().rstrip('.… ').strip()


def overlaps(sentence, headline, ratio=0.5):
    grams = lambda text: {text[i:i + 2] for i in range(len(text) - 1)}
    left, right = grams(re.sub(r'\W', '', sentence)), grams(re.sub(r'\W', '', headline))
    # Share of the headline's lead clause that the sentence merely restates.
    return bool(right) and len(left & right) / len(right) >= ratio


def lead_sentences(text, limit=SUMMARY_BUDGET, headline=''):
    """Whole sentences (or a whole leading clause) that add to the headline."""
    sentences = [x.strip() for x in re.findall(r'[^。！？!?]+[。！？!?]?', text) if x.strip()]
    sentences = [x for x in sentences if not (headline and overlaps(x, brief(headline), 0.4))]
    out = ''
    for sentence in sentences:
        if len(out) + len(sentence) > limit:
            break
        out += sentence if sentence[-1] in '。！？!?' else sentence + '。'
    if not out and sentences:
        first = sentences[0]
        cuts = [i for i, ch in enumerate(first) if ch in '，,；;' and 12 <= i <= limit]
        out = first[:cuts[-1]] + '。' if cuts else ''
    return out


def speakable(text):
    """Make TTS-friendly: drop ASCII-only asides, round big numbers."""
    text = re.sub(r'\s*[（(][\x20-\x7e]+[）)]\s*', '', text)
    # Headlines often use spaces as clause breaks; TTS needs a pause there.
    text = re.sub(r'(?<=[\u4e00-\u9fff])\s+(?=[\u4e00-\u9fff])|(?<=%)\s+', '，', text)

    def number(match):
        value = float(match.group().replace(',', ''))
        if value < 1e4:
            return str(int(value))
        if value >= 1e8:
            return f'约{value / 1e8:.3g}亿'
        return f'约{value / 1e4:.2g}万'
    return re.sub(r'(?<![\d.])\d{1,3}(?:,\d{3})+(?![\d.])|(?<![\d.,])\d{5,}(?![\d.,])', number, text)


def manifest(day, chosen):
    weekday = '一二三四五六日'[day.weekday()]
    headlines = [clean_title(candidate['title']) for candidate in chosen]
    shorts = [brief(headline) for headline in headlines]
    ordinals = '一二三四五六七八九十'
    items = [dict(id='intro', kind='intro', title='每日头条',
                  text=f'每日头条。今天是北京时间{day.month}月{day.day}日，星期{weekday}。',
                  screenText=f'{len(chosen)} 条头条', headlines=shorts)]
    for index, (candidate, headline) in enumerate(zip(chosen, headlines), 1):
        summary = clean_summary(candidate.get('summary', ''))
        if similar(headline, summary):
            summary = ''
        narration = speakable(headline + '。' + lead_sentences(summary, headline=headline))
        outlets = candidate.get('outlets') or [candidate['source']]
        items.append(dict(id=f'news-{index}', kind='news', title=shorts[index - 1],
                          articleTitle=headline, source=candidate['source'], outlets=outlets,
                          sourceUrl=candidate['link'], publishedAt=datetime.fromtimestamp(candidate['published'], TIMEZONE).isoformat(),
                          category=candidate.get('category', '新闻'),
                          text=f'第{ordinals[index - 1] if index <= 10 else index}条，{narration.rstrip()}',
                          screenText=f'{len(outlets)} 家媒体报道' if len(outlets) > 1 else candidate['source'],
                          summary=short(summary or headline, 150)))
    return dict(date=day.isoformat(), generation=dict(mode='rss-pagerank-extractive', timezone=str(TIMEZONE)), items=items)


def main():
    day = release_date()
    now = datetime.now(TIMEZONE)
    if day > now.date():
        raise ValueError('不能生成未来日期的每日头条')
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
