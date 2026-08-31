#!/usr/bin/env bash
# Render today's (or RELEASE_DATE) daily video into a date-named folder: out/<YYYY_MM_DD>/
set -euo pipefail

DATE="${RELEASE_DATE:-$(date +%Y_%m_%d)}"
FILENAME="news-daily-${DATE}${VERSION:+-${VERSION}}.mp4"

mkdir -p "out/${DATE}"
npx remotion render NewsDaily "out/${DATE}/${FILENAME}" "$@"
echo "Rendered out/${DATE}/${FILENAME}"
