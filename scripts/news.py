#!/usr/bin/env python3
"""Fetch mixed CN/EN news RSS, select + summarize with an OpenAI-compatible LLM,
and write public/voiceover/script.json + narration.zh.txt.

Script.json is the single content contract consumed by src/content.ts. The order of
items.items[] equals the order of \n\n-separated paragraphs in narration.zh.txt, which
drives the audio-master-clock scene timeline via segment-durations.json.
"""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import requests

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VO = os.path.join(BASE, "public", "voiceover")
os.makedirs(VO, exist_ok=True)


def load_env():
    env_path = os.path.join(BASE, ".env")
    if not os.path.exists(env_path):
        return
    with open(env_path, encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


load_env()

LLM_BASE_URL = os.environ.get("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_API_KEY = os.environ.get("LLM_API_KEY", "")
LLM_MODEL = os.environ.get("LLM_MODEL", "gpt-4o-mini")
K = int(os.environ.get("NEWS_COUNT", "6"))

FEEDS = [
    ("36氪", "科技", "https://36kr.com/feed"),
    ("虎嗅", "商业", "https://www.huxiu.com/rss/0.xml"),
    ("少数派", "数码", "https://sspai.com/feed"),
    ("爱范儿", "科技", "https://www.ifanr.com/feed"),
    ("机器之心", "AI", "https://www.jiqizhixin.com/rss"),
    ("BBC", "国际", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("卫报", "国际", "https://www.theguardian.com/world/rss"),
]

FETCH_TIMEOUT = 12

TAG_RE = re.compile(r"<[^>]+>")


def local_name(tag):
    return tag.split("}", 1)[-1] if "}" in tag else tag


def strip_html(text):
    return TAG_RE.sub("", text or "").strip()


def text_of(element, names):
    for child in element:
        if local_name(child.tag) in names:
            joined = " ".join("".join(child.itertext()).split())
            if joined:
                return joined
    return ""


def link_of(element):
    for child in element:
        if local_name(child.tag) == "link":
            href = child.get("href") or child.get("url")
            if href:
                return href.strip()
            joined = " ".join(child.itertext()).strip()
            if joined:
                return joined
    return text_of(element, ("guid",))


def parse_published(raw):
    if not raw:
        return 0
    try:
        return int(datetime.strptime(raw, "%a, %d %b %Y %H:%M:%S %z").timestamp())
    except ValueError:
        return 0


def parse_feed(url, source, category):
    response = requests.get(url, timeout=FETCH_TIMEOUT, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    text = response.text
    # Some feeds contain unescaped '&' (e.g. inside URLs); repair before parsing.
    text = re.sub(r"&(?!#\d+;|#x[0-9a-fA-F]+;|\w+;)", "&amp;", text)
    root = ET.fromstring(text.encode("utf-8"))
    entries = []
    for element in root.iter():
        if local_name(element.tag) not in ("item", "entry"):
            continue
        title = strip_html(text_of(element, ("title",)))
        link = link_of(element)
        summary = strip_html(text_of(element, ("description", "summary", "content")))
        published = parse_published(text_of(element, ("pubDate", "published", "updated")))
        if not title or not link:
            continue
        entries.append({
            "title": title,
            "link": link,
            "summary": summary[:220],
            "published": published,
            "source": source,
            "category": category,
        })
    return entries


def fetch_one(feed):
    source, category, url = feed
    try:
        return parse_feed(url, source, category)
    except Exception as exc:  # noqa: BLE001 - one bad feed must not break the run
        print(f"warn: {source} fetch failed: {exc}", file=sys.stderr)
        return []


def collect_candidates():
    with ThreadPoolExecutor(max_workers=len(FEEDS)) as pool:
        results = list(pool.map(fetch_one, FEEDS))
    candidates, seen = [], set()
    for entries in results:
        for entry in entries:
            key = re.sub(r"[^a-z0-9]+", "", entry["link"].lower())
            if not key or key in seen:
                continue
            seen.add(key)
            candidates.append(entry)
    candidates.sort(key=lambda item: item["published"], reverse=True)
    return candidates[:40]


SYSTEM = (
    "你是一位面向竖屏短视频的中文新闻主编。从候选新闻里挑选最有信息增量的 {k} 条，"
    "用口语化旁白改写，输出严格 JSON。不要输出 JSON 以外的任何文字。"
)

USER = """今天是 {date}。下面是今日候选新闻（编号. 来源 | 标题 | 摘要）：

{candidates}

请输出如下结构的 JSON（不要 markdown 代码块）：
{{
  "items": [
    {{"kind": "intro", "title": "AI 新闻日报", "text": "开场白，约25字，介绍今天",
      "screenText": "今日 {k} 条热点"}},
    {{"kind": "news", "title": "标题，不超过12字", "text": "旁白，2句话60-90字，口语化、适合朗读，",
      "screenText": "一个关键数字或要点的短句", "source": "候选来源", "category": "候选来源分类"}},
    ...
    {{"kind": "outro", "title": "明天见", "text": "结语，约25字", "screenText": "关注 · 每天与你 AI 读新闻"}}
  ]
}}

约束：
- news 恰好 {k} 条，其余字段照示例。
- title 是屏幕大字，≤12 字，用候选标题精简浓缩。
- text 是旁白，口语化、指标明确、可朗读，不要罗列全部信息。
- 首选最近 24 小时、信息增量高的新闻；同质化新闻只留一条。
"""


def llm_chat(system, user):
    if not LLM_API_KEY:
        raise SystemExit("未配置 LLM_API_KEY：在 .env 中设置 LLM_BASE_URL 与 LLM_API_KEY。")
    response = requests.post(
        f"{LLM_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"},
        json={
            "model": LLM_MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": 0.4,
        },
        timeout=60,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def parse_json_block(content):
    content = re.sub(r"^```(?:json)?\s*", "", content.strip())
    content = re.sub(r"\s*```$", "", content)
    return json.loads(content)


def main():
    candidates = collect_candidates()
    if not candidates:
        raise SystemExit("未抓到任何候选新闻，检查 RSS 源。")
    today = datetime.now().strftime("%Y-%m-%d")
    candidate_lines = "\n".join(
        f"{index}. {item['source']} | {item['title']} | {item['summary']}"
        for index, item in enumerate(candidates, 1)
    )
    content = llm_chat(
        SYSTEM.format(k=K),
        USER.format(date=today, k=K, candidates=candidate_lines),
    )
    script = parse_json_block(content)
    script["date"] = today
     # 归一化 id：intro / news-1..news-K / outro
    normalized = []
    news_counter = 0
    for item in script["items"]:
        kind = item.get("kind", "news")
        if kind == "news":
            news_counter += 1
            item["id"] = f"news-{news_counter}"
        elif kind == "intro":
            item["id"] = "intro"
        elif kind == "outro":
            item["id"] = "outro"
        normalized.append(item)
    script["items"] = normalized

    with open(os.path.join(VO, "script.json"), "w", encoding="utf-8") as handle:
        json.dump(script, handle, ensure_ascii=False, indent=2)

    narration = "\n\n".join(item["text"] for item in script["items"])
    with open(os.path.join(VO, "narration.zh.txt"), "w", encoding="utf-8") as handle:
        handle.write(narration + "\n")

    print(f"OK: {len(script['items'])} cues (news {news_counter}), date {today}")


if __name__ == "__main__":
    main()
