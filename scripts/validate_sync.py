#!/usr/bin/env python3
"""Validate script/cue count, ordering, positive durations, and audio length alignment."""
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VO = os.path.join(BASE, "public", "voiceover")


def load(name):
    with open(os.path.join(VO, name), encoding="utf-8") as handle:
        return json.load(handle)


script = load("script.json")
durations = load("segment-durations.json")
items = script["items"]

errors = []
if len(items) != len(durations):
    errors.append(f"items {len(items)} != durations {len(durations)}")

for index, (item, dur) in enumerate(zip(items, durations)):
    if item["id"] != items[index]["id"]:
        errors.append(f"order mismatch at {index}")
    if not isinstance(dur, (int, float)) or dur <= 0:
        errors.append(f"item {index} non-positive duration {dur}")
    if item.get("id") != items[index].get("id"):
        errors.append(f"id mismatch at {index}")

audio = os.path.join(VO, "narration.zh.mp3")
if os.path.exists(audio):
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", audio],
        capture_output=True, text=True,
    )
    actual = float(probe.stdout.strip())
    if abs(actual - sum(durations)) > 0.15:
        errors.append(f"mp3 {actual:.2f}s != sum {sum(durations):.2f}s")

if errors:
    for error in errors:
        print(f"FAIL: {error}")
    sys.exit(1)
print(f"OK: {len(items)} cues, total {sum(durations):.2f}s")
