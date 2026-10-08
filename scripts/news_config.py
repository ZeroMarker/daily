"""Shared date/path settings for unattended daily production."""
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
TIMEZONE = ZoneInfo(os.environ.get('NEWS_TIMEZONE', 'Asia/Shanghai'))


def release_date():
    raw = os.environ.get('RELEASE_DATE', datetime.now(TIMEZONE).strftime('%Y_%m_%d'))
    parsed = datetime.strptime(raw, '%Y_%m_%d').date()
    if parsed.strftime('%Y_%m_%d') != raw:
        raise ValueError('RELEASE_DATE must be YYYY_MM_DD')
    return parsed


def content_dir():
    return ROOT / 'content' / release_date().strftime('%Y_%m_%d')


if __name__ == '__main__':
    print(release_date().strftime('%Y_%m_%d'))
