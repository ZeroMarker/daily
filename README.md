# AI 新闻日报

自动采集新闻、选题、生成摘要与旁白，制作中文竖版视频，并发布为 **杂志 → 日报 → 视频**。日常生产无需人工选题、撰稿、配音或打标签。

[在线阅读](https://zeromarker.github.io/daily/)

```text
每天定时 → RSS 采集 → 时间筛选 / 去重 / 来源分布 → 日报与旁白
         → 内容校验 → 自动提交与版本标签 → Edge TTS → 音画校验
         → Remotion 渲染 → GitHub Release → Pages 杂志 / 日报 / 视频
```

## 自动运行

`.github/workflows/daily.yml` 每天 UTC 00:30（北京时间 08:30）运行，也可在 Actions 中执行 **Auto publish daily**。GitHub 定时任务可能延迟，不保证准点。

- 默认选取近 48 小时内的 5 条中文新闻，优先科技与 AI，并兼顾来源分布。
- 无有效日期、未来新闻、重复链接及相似标题会被排除；不足 3 条则失败，不发布空日报或用过期新闻凑数。
- 摘要采用 RSS 原文摘取，清理推广尾文；旁白由标题、来源及摘要组成，不依赖 LLM 或额外 API 密钥。
- `script.json` 与 `narration.zh.txt` 从同一份内容生成，自动校验文本、数量和顺序。
- 自动提交当日内容到 `main`，创建 `<日期>-<semver>` 标签，复用视频发行工作流。重跑自动递增补丁版本。
- 视频发行成功后自动刷新 Pages。最新视频支持站内播放，历史版本可下载。

第一次启用后即可定时运行。仅需 GitHub Actions 的内置令牌具有工作流声明的 `contents: write` 权限，Pages 发布来源为 GitHub Actions。

## 本地运行

需要 Node.js 18+、Python 3.10+、FFmpeg / ffprobe。

```bash
npm install
python3 -m pip install requests edge-tts

# 一次完成采集、文案、配音、校验和渲染；不执行 Git 推送。
npm run daily

# 分步执行
npm run fetch
npm run news
npm run validate:content
npm run voiceover
npm run check
npm run validate
npm run render

# 内容自动化测试
npm run test:news

# 预览视频
npm run dev

# 构建杂志站点
npm run build:pages
python3 -m http.server 8080 --directory dist/pages
```

默认按北京时间确定日期。可通过环境变量覆盖，例如 `RELEASE_DATE=2026_10_08 npm run daily`。历史日期生成仅从本次 RSS 返回的候选中筛选，不提供历史新闻抓取服务。

## 内容与目录

```text
content/<YYYY_MM_DD>/     script.json、narration.zh.txt（自动生成并提交）
                         candidates.json、MP3、segment-durations.json（忽略）
public/voiceover/        活动工作区，由 sync_content.sh 同步（忽略）
src/                    Remotion 视频引擎：1080×1920、30fps、9:16
scripts/                采集、生成、校验、提交、配音、渲染、杂志构建
tests/                  内容自动化测试
site/                   杂志站点样式
out/<YYYY_MM_DD>/        渲染成片（忽略）
dist/pages/             静态站点产物（忽略）
```

`script.json` 是唯一内容契约：`items[]` 顺序 = 旁白空行分段顺序 = 实测音频时长顺序。场景时间轴由音频实际时长驱动。

`items` 包含开场、新闻和结尾。每条新闻的 `title` 是屏幕短标题，`articleTitle` 是完整标题，`text` 是旁白，`screenText` 是画面关键点，`summary` 是摘要，`source` / `sourceUrl` / `publishedAt` 保留出处与时间。文字日报展示原文链接。

## 环境变量

通过 shell 或 Actions 环境变量传入；`.env.example` 为配置参考，不会自动加载。

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `NEWS_TIMEZONE` | `Asia/Shanghai` | 日期与发布时间时区 |
| `RELEASE_DATE` | 当天 | `YYYY_MM_DD` 内容目录 |
| `CANDIDATES` | `40` | RSS 候选上限，兼顾各来源 |
| `NEWS_COUNT` | `5` | 目标新闻条数 |
| `NEWS_MIN_COUNT` | `3` | 最低发布条数 |
| `NEWS_MAX_AGE_HOURS` | `48` | 新闻新鲜度窗口 |
| `NEWS_LANGUAGE` | `zh` | 默认中文；`all` 可含英文原文 |
| `TTS_RATE` | `+4%` | 旁白语速 |
| `VERSION` | 无 | 本地渲染文件版本后缀 |
| `GH_TOKEN` | 无 | 站点构建读取发行列表；Actions 自动提供 |
| `RELEASES_FILE` | 无 | 本地发行列表 JSON 快照，可用 `[]` 离线构建无视频站点 |

新闻源在 `scripts/fetch.py` 的 `FEEDS` 中配置。单个源失败不影响其他来源；最终可用新闻不足则停止。

## 发布与站点

见 [RELEASING.md](./RELEASING.md)。自动流程完成后，Pages 将日期目录组织为杂志首页、文字日报、当日视频和历史归档。

`pages.yml` 在站点或内容更新、视频发行流程完成时发布，也可手动运行。构建时匹配 GitHub Releases，将每个日期最新的 MP4 随站点部署。
