#!/usr/bin/env python3
"""Fetch dated RSS/Atom candidates for automatic daily selection."""
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape

from news_config import content_dir

import requests

VO = str(content_dir())
os.makedirs(VO, exist_ok=True)

CANDIDATE_LIMIT = int(os.environ.get("CANDIDATES", "40"))

FEEDS = [
    ("36氪", "科技", "https://36kr.com/feed"),
    ("虎嗅", "商业", "https://www.huxiu.com/rss/0.xml"),
    ("少数派", "数码", "https://sspai.com/feed"),
    ("爱范儿", "科技", "https://www.ifanr.com/feed"),
    ("机器之心", "AI", "https://www.jiqizhixin.com/rss"),
    ("IT之家", "科技", "https://www.ithome.com/rss/"),
    ("Solidot", "科技", "https://www.solidot.org/index.rss"),
    ("量子位", "AI", "https://www.qbitai.com/feed"),
    ("BBC", "国际", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("卫报", "国际", "https://www.theguardian.com/world/rss"),
]

FETCH_TIMEOUT = 12
TAG_RE = re.compile(r"<[^>]+>")


def local_name(tag):
    return tag.split("}", 1)[-1] if "}" in tag else tag


def strip_html(text):
    text = re.sub(r"<(script|style)\b[^>]*>.*?</\1>", "", text or "", flags=re.I | re.S)
    return " ".join(unescape(TAG_RE.sub(" ", text)).split())


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
        parsed = parsedate_to_datetime(raw)
    except (TypeError, ValueError):
        try:
            parsed = datetime.fromisoformat(raw.replace('Z', '+00:00'))
        except ValueError:
            return 0
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return int(parsed.timestamp())


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
            "summary": summary[:1000],
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


def main():
    with ThreadPoolExecutor(max_workers=len(FEEDS)) as pool:
        results = list(pool.map(fetch_one, FEEDS))
    candidates, seen = [], set()
    for entries in results:
        for entry in entries:
            key = entry["link"].split("#", 1)[0]
            if not key or key in seen:
                continue
            seen.add(key)
            candidates.append(entry)
    if not candidates:
        raise SystemExit("所有新闻源均无可用内容；停止生成，避免发布空日报。")
    candidates.sort(key=lambda item: item["published"], reverse=True)
    # Keep several stories from every source; a busy feed must not crowd out others.
    groups = {}
    for item in candidates:
        groups.setdefault(item['source'], []).append(item)
    candidates = []
    while groups and len(candidates) < CANDIDATE_LIMIT:
        for source in list(groups):
            candidates.append(groups[source].pop(0))
            if not groups[source]:
                del groups[source]
            if len(candidates) == CANDIDATE_LIMIT:
                break
    out = os.path.join(VO, "candidates.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(candidates, handle, ensure_ascii=False, indent=2)
    print(f"Fetched {len(candidates)} candidates -> {out}")
    print("下一步：npm run news 生成选题、摘要与旁白。")


if __name__ == "__main__":
    main()
