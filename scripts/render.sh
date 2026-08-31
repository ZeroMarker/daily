#!/usr/bin/env bash
# Render today's (or RELEASE_DATE) daily video into a date-named folder: out/<date>/news-daily-<date>.mp4
set -euo pipefail

DATE="${RELEASE_DATE:-$(date +%F)}"
mkdir -p "out/${DATE}"

npx remotion render NewsDaily "out/${DATE}/news-daily-${DATE}.mp4" "$@"
echo "Rendered out/${DATE}/news-daily-${DATE}.mp4"
