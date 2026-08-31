#!/usr/bin/env python3
"""Generate Chinese narration clips with Edge TTS, measure real durations, concatenate.

按段生成旁白 → ffprobe 实测每段时长 → 合并为 narration.zh.mp3
→ 写出 segment-durations.json（时长数组，顺序与 narration.zh.txt 段落一一对应）。
"""
import json
import os
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VO = os.path.join(BASE, "public", "voiceover")
VOICE = "zh-CN-XiaoxiaoNeural"
RATE = os.environ.get("TTS_RATE", "+4%")

os.makedirs(VO, exist_ok=True)
with open(os.path.join(VO, "narration.zh.txt"), encoding="utf-8") as handle:
    paragraphs = [p.strip() for p in handle.read().split("\n\n") if p.strip()]

if not paragraphs:
    raise SystemExit("narration.zh.txt 为空：先运行 npm run news 生成今日文案。")

durations = []
for index, paragraph in enumerate(paragraphs, 1):
    segment = os.path.join(VO, f"seg{index}.mp3")
    subprocess.run(
        [sys.executable, "-m", "edge_tts", "--voice", VOICE, "--rate", RATE,
         "--text", paragraph, "--write-media", segment],
        check=True,
    )
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", segment],
        capture_output=True, check=True, text=True,
    )
    durations.append(float(probe.stdout.strip()))

concat_path = os.path.join(VO, "concat.txt")
with open(concat_path, "w", encoding="utf-8") as handle:
    for index in range(1, len(paragraphs) + 1):
        handle.write(f"file 'seg{index}.mp3'\n")

subprocess.run(
    ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_path,
     "-c", "copy", os.path.join(VO, "narration.zh.mp3")],
    check=True, capture_output=True,
)
with open(os.path.join(VO, "segment-durations.json"), "w", encoding="utf-8") as handle:
    json.dump(durations, handle, ensure_ascii=False, indent=2)

for index in range(1, len(paragraphs) + 1):
    os.remove(os.path.join(VO, f"seg{index}.mp3"))
os.remove(concat_path)
print(f"Generated {len(paragraphs)} segments, total {sum(durations):.2f}s")
