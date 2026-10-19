"""Shared date/path settings for unattended daily production."""
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
TIMEZONE = ZoneInfo(os.environ.get('NEWS_TIMEZONE', 'Asia/Shanghai'))

# Credibility weight per outlet: original reporting > specialist media > aggregators/reposts.
SOURCE_WEIGHTS = {
    '澎湃新闻': 1.3, 'FT中文网': 1.3, '纽约时报中文网': 1.3, 'BBC中文': 1.2, 'BBC': 1.2, '卫报': 1.2,
    '机器之心': 1.1, '36氪': 1.0, '量子位': 1.0, 'InfoQ': 1.0, 'Solidot': 1.0, '钛媒体': 0.9,
    '虎嗅': 0.9, '爱范儿': 0.9, 'IT之家': 0.8, '少数派': 0.7, 'cnBeta': 0.6,
}


def source_weight(source):
    return SOURCE_WEIGHTS.get(source, 1.0)


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
