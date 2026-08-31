#!/usr/bin/env bash
# Sync the active date's content (content/<YYYY_MM_DD>/) into public/voiceover/,
# which the Remotion engine imports and staticFile() reads at render time.
set -euo pipefail

DATE="${RELEASE_DATE:-$(date +%Y_%m_%d)}"
SRC="content/${DATE}"

if [[ ! -f "$SRC/script.json" || ! -f "$SRC/narration.zh.txt" ]]; then
  echo "缺少 content/${DATE} 的源内容：script.json / narration.zh.txt" >&2
  echo "请先人工撰写当日内容，或设置 RELEASE_DATE 指向已有日期目录。" >&2
  exit 1
fi

if [[ ! -f "$SRC/segment-durations.json" ]]; then
  echo "缺少 content/${DATE}/segment-durations.json（生成物）：请先运行 npm run voiceover。" >&2
  exit 1
fi

mkdir -p public/voiceover
cp -f "$SRC/script.json" "$SRC/narration.zh.txt" "$SRC/segment-durations.json" public/voiceover/
if [[ -f "$SRC/narration.zh.mp3" ]]; then
  cp -f "$SRC/narration.zh.mp3" public/voiceover/
fi
echo "Synced content/${DATE} -> public/voiceover/"
