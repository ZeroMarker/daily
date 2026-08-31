#!/usr/bin/env python3
"""Fetch mixed CN/EN news RSS and dump today's candidates for human review.

No LLM. The human selects and rewrites the daily script manually, writing
public/voiceover/script.json + narration.zh.txt before running the pipeline.
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

CANDIDATE_LIMIT = int(os.environ.get("CANDIDATES", "40"))

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


def main():
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
    candidates = candidates[:CANDIDATE_LIMIT]
    out = os.path.join(VO, "candidates.json")
    with open(out, "w", encoding="utf-8") as handle:
        json.dump(candidates, handle, ensure_ascii=False, indent=2)
    print(f"Fetched {len(candidates)} candidates -> {out}")
    print("人工挑选后写 script.json 与 narration.zh.txt，然后：npm run voiceover && npm run render")


if __name__ == "__main__":
    main()
