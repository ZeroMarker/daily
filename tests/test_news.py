import json
import sys
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from fetch import parse_published, parse_feed
from generate_news import select, manifest, main, clean_summary
from validate_content import validate
import publish_content

CUTOFF = 1791420000


def candidate(title, source='测试新闻源', stamp=CUTOFF - 60, url=None):
    return dict(title=title, source=source, published=stamp, category='科技',
                summary='公司发布了新产品，并公布了相关技术信息。',
                link=url or 'https://example.com/' + title)


class NewsTests(unittest.TestCase):
    def test_rss_and_atom_dates(self):
        self.assertEqual(parse_published('Thu, 08 Oct 2026 00:00:00 GMT'),
                         parse_published('2026-10-08T08:00:00+08:00'))
        self.assertEqual(parse_published('unknown'), 0)
        response = unittest.mock.Mock(text='''<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>科技动态</title><link href="https://example.com/news"/><updated>2026-10-08T00:00:00Z</updated><summary>&lt;p&gt;产品更新&lt;/p&gt;</summary></entry></feed>''')
        with patch('fetch.requests.get', return_value=response):
            entries = parse_feed('https://example.com/feed', '来源', '科技')
        self.assertEqual(entries[0]['summary'], '产品更新')
        self.assertGreater(entries[0]['published'], 0)

    def test_excludes_stale_future_undated_and_invalid_links(self):
        rows = [candidate('有效新闻报道'), candidate('过期新闻', stamp=CUTOFF - 49*3600),
                candidate('未来新闻', stamp=CUTOFF+1), candidate('无日期新闻', stamp=0),
                candidate('坏链接新闻', url='javascript:alert(1)')]
        self.assertEqual([x['title'] for x in select(rows, CUTOFF, count=1, minimum=1)], ['有效新闻报道'])
        with self.assertRaises(ValueError):
            select(rows[1:], CUTOFF)

    def test_dedup_tracking_and_similar_headlines(self):
        rows = [candidate('苹果宣布发布新手机', url='https://example.com/news?utm_source=rss'),
                candidate('不同标题同一网址', url='https://example.com/news'),
                candidate('苹果宣布发布新手机！', url='https://other.com/news')]
        self.assertEqual(len(select(rows, CUTOFF, count=3, minimum=1)), 1)

    def test_source_diversity_and_chinese_default(self):
        rows = [candidate('微软发布系统更新', source='甲'), candidate('苹果公布财务数据', source='甲'),
                candidate('航天任务成功发射', source='乙'), candidate('芯片工艺技术突破', source='丙'),
                candidate('English only news', source='丁')]
        chosen = select(rows, CUTOFF, count=3)
        self.assertEqual({x['source'] for x in chosen}, {'甲', '乙', '丙'})
        self.assertEqual(len(select(rows, CUTOFF, count=5, language='all')), 5)

    def test_contract_catches_reordered_narration_and_duplicate_ids(self):
        day = date(2026, 10, 8)
        data = manifest(day, [candidate('一条新闻')])
        narration = '\n\n'.join(x['text'] for x in data['items'])
        self.assertEqual(len(validate(data, narration, day)), 3)
        with self.assertRaises(ValueError):
            validate(data, '\n\n'.join(reversed(narration.split('\n\n'))), day)
        data['items'][1]['id'] = 'intro'
        with self.assertRaises(ValueError):
            validate(data, narration, day)

    def test_automatic_files_share_exact_narration(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)
            rows = [candidate('微软发布新系统'), candidate('汽车厂商公布新品'), candidate('科学家发现新材料')]
            (path / 'candidates.json').write_text(json.dumps(rows))
            with patch('generate_news.content_dir', return_value=path), patch('generate_news.release_date', return_value=date(2026,10,8)):
                main()
            data = json.loads((path / 'script.json').read_text())
            narration = (path / 'narration.zh.txt').read_text()
            validate(data, narration, date(2026,10,8))
            self.assertTrue(all(x.get('sourceUrl') for x in data['items'] if x['kind']=='news'))

    def test_publisher_pushes_only_daily_files_and_next_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / 'work'
            remote = Path(tmp) / 'remote.git'
            subprocess.run(['git', 'init', '--bare', '-q', str(remote)], check=True)
            subprocess.run(['git', 'init', '-q', '-b', 'main', str(root)], check=True)
            def git(*args):
                return subprocess.run(['git', *args], cwd=root, check=True, text=True, capture_output=True).stdout.strip()
            git('config', 'user.name', 'Test'); git('config', 'user.email', 'test@example.com')
            git('remote', 'add', 'origin', str(remote))
            (root / 'README.md').write_text('Base')
            git('add', 'README.md'); git('commit', '-qm', 'Base')
            git('tag', '2026_10_08-1.0.9')
            folder = root / 'content' / '2026_10_08'; folder.mkdir(parents=True)
            (folder / 'script.json').write_text('{}')
            (folder / 'narration.zh.txt').write_text('Narration')
            (root / 'unrelated.txt').write_text('Do not publish')
            with patch('publish_content.ROOT', root), patch('publish_content.release_date', return_value=date(2026,10,8)), patch('publish_content.validate'):
                publish_content.main()
            self.assertIn('2026_10_08-1.0.10', git('ls-remote', '--tags', 'origin'))
            self.assertEqual(git('status', '--short'), '?? unrelated.txt')
            self.assertEqual(set(git('diff-tree', '--no-commit-id', '--name-only', '-r', 'HEAD').splitlines()),
                             {'content/2026_10_08/script.json', 'content/2026_10_08/narration.zh.txt'})

    def test_promotion_removed_and_title_limits(self):
        self.assertEqual(clean_summary('新品发布。 #欢迎关注公众号'), '新品发布。')
        data = manifest(date(2026,10,8), [candidate('这是一个超过十二个字的科技新闻完整标题')])
        self.assertLessEqual(len(data['items'][1]['title']), 12)
        self.assertNotIn('欢迎关注', data['items'][1]['text'])


if __name__ == '__main__':
    unittest.main()
