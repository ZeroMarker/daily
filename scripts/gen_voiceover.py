#!/usr/bin/env python3
"""Generate Chinese narration clips with Edge TTS, measure durations, concatenate.

Reads content/<YYYY_MM_DD>/narration.zh.txt and writes the concatenated mp3 and
segment-durations.json back into that date directory.
"""
import json
import os
import subprocess
import sys
import time
from validate_content import main as validate_content
from news_config import ROOT, release_date

BASE = str(ROOT)
DATE = release_date().strftime("%Y_%m_%d")
CONTENT = os.path.join(BASE, "content", DATE)
VOICE = "zh-CN-XiaoxiaoNeural"
RATE = os.environ.get("TTS_RATE", "+4%")

validate_content()
os.makedirs(CONTENT, exist_ok=True)
with open(os.path.join(CONTENT, "narration.zh.txt"), encoding="utf-8") as handle:
    paragraphs = [p.strip() for p in handle.read().split("\n\n") if p.strip()]

if not paragraphs:
    raise SystemExit(f"content/{DATE}/narration.zh.txt 为空：先运行 npm run fetch && npm run news。")

durations = []
for index, paragraph in enumerate(paragraphs, 1):
    segment = os.path.join(CONTENT, f"seg{index}.mp3")
    for attempt in range(3):
        try:
            subprocess.run(
                [sys.executable, "-m", "edge_tts", "--voice", VOICE, "--rate", RATE,
                 "--text", paragraph, "--write-media", segment],
                check=True,
            )
            break
        except subprocess.CalledProcessError:
            if attempt == 2:
                raise
            time.sleep(3 * (attempt + 1))
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", segment],
        capture_output=True, check=True, text=True,
    )
    durations.append(float(probe.stdout.strip()))

concat_path = os.path.join(CONTENT, "concat.txt")
with open(concat_path, "w", encoding="utf-8") as handle:
    for index in range(1, len(paragraphs) + 1):
        handle.write(f"file 'seg{index}.mp3'\n")

subprocess.run(
    ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_path,
     "-c", "copy", os.path.join(CONTENT, "narration.zh.mp3")],
    check=True, capture_output=True,
)
with open(os.path.join(CONTENT, "segment-durations.json"), "w", encoding="utf-8") as handle:
    json.dump(durations, handle, ensure_ascii=False, indent=2)

for index in range(1, len(paragraphs) + 1):
    os.remove(os.path.join(CONTENT, f"seg{index}.mp3"))
os.remove(concat_path)
print(f"Generated {len(paragraphs)} segments for {DATE}, total {sum(durations):.2f}s")
