#!/usr/bin/env bash
# Render the active date's daily video into a date-named folder: out/<YYYY_MM_DD>/
set -euo pipefail

DATE="${RELEASE_DATE:-$(date +%Y_%m_%d)}"
FILENAME="news-daily-${DATE}${VERSION:+-${VERSION}}.mp4"

"$(dirname "$0")/sync_content.sh"

mkdir -p "out/${DATE}"
npx remotion render NewsDaily "out/${DATE}/${FILENAME}" "$@"
echo "Rendered out/${DATE}/${FILENAME}"
