#!/usr/bin/env python3
"""Validate script/cue count, ordering, positive durations, and audio length alignment."""
import json
import os
import subprocess
import sys
import math
from validate_content import validate
from news_config import ROOT, release_date

BASE = str(ROOT)
DATE = release_date().strftime("%Y_%m_%d")
VO = os.path.join(BASE, "content", DATE)


def load(name):
    with open(os.path.join(VO, name), encoding="utf-8") as handle:
        return json.load(handle)


script = load("script.json")
durations = load("segment-durations.json")
with open(os.path.join(VO, "narration.zh.txt"), encoding="utf-8") as handle:
    items = validate(script, handle.read(), release_date())

errors = []
if len(items) != len(durations):
    errors.append(f"items {len(items)} != durations {len(durations)}")

for index, (item, dur) in enumerate(zip(items, durations)):
    if not isinstance(dur, (int, float)) or not math.isfinite(dur) or dur <= 0:
        errors.append(f"item {index} non-positive duration {dur}")

audio = os.path.join(VO, "narration.zh.mp3")
if os.path.exists(audio):
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", audio],
        capture_output=True, text=True, check=True,
    )
    actual = float(probe.stdout.strip())
    if not math.isfinite(actual) or abs(actual - sum(durations)) > 0.15:
        errors.append(f"mp3 {actual:.2f}s != sum {sum(durations):.2f}s")

else:
    errors.append("缺少 narration.zh.mp3")

if errors:
    for error in errors:
        print(f"FAIL: {error}")
    sys.exit(1)
print(f"OK: {len(items)} cues, total {sum(durations):.2f}s")
