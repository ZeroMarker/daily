# AI 新闻日报

把当天新闻做成一条竖版（9:16 · 1080×1920）抖音短视频。**内容（选题+摘要）由人工撰写**，自动管线只负责配音与渲染。**日期即文件路径**：每日内容清单提交在 `content/<YYYY_MM_DD>/`，成片输出到 `out/<YYYY_MM_DD>/`。

```text
人工：RSS 取材（可选 fetch）→ 挑选 → 写 content/<日期>/script.json + narration.zh.txt
机器：Edge TTS 逐段 → 实测时长 → Remotion 渲染 → out/<日期>
```

采用「音频主时钟」同步：最终旁白音频实测时长驱动场景时间轴，杜绝用 `setTimeout`/`Date.now()`/手动 `audio.play()` 造成的漂移。方案与仓库外的 `~/video` 音画同步规范一致。

## 目录结构

```text
content/2026_08_31/        ← 提交：script.json · narration.zh.txt（segment-durations.json / mp3 为生成物，忽略）
public/voiceover/          ← gitignored 活动工作区（引擎静态导入 + staticFile 读 mp3），
                             由 sync_content.sh 从 content/<日期> 同步，勿直接编辑
src/                       ← Remotion 渲染引擎（1080×1920 · 30fps · 帧驱动）
scripts/                   ← fetch / gen_voiceover / sync_content / render / validate
out/<日期>/                ← gitignored 渲染产物 news-daily-<日期>[-<版本>].mp4
```

`content/<日期>/script.json` 是唯一内容契约：`items[]` 顺序 = `narration.zh.txt` 的 `\n\n` 分段顺序 = `segment-durations.json` 时长顺序。段落数与场景数不一致时 `timing.ts` 直接抛错，挡住错误渲染。

## 环境

- Node.js 18+，Python 3.10+
- FFmpeg / ffprobe
- `pip install edge-tts requests`

## 运行

```bash
npm install

# 1.（可选）抓当日候选新闻，供人工挑选取材（写入 content/<日期>/candidates.json）
RELEASE_DATE=2026_08_31 npm run fetch

# 2. 人工撰写内容（无 LLM）
#    - content/<日期>/script.json：items = intro + news-1..K + outro
#      title=屏幕大字(≤12字)、text=旁白(60-90字)、screenText=关键点、summary=屏幕说明正文
#    - content/<日期>/narration.zh.txt：把每条 item.text 用空行 "\n\n" 分隔，段序与 items[] 一致

# 3. 生成旁白 + 实测时长到 content/<日期>（每次改文案后必须重跑）
RELEASE_DATE=2026_08_31 npm run voiceover

# 4. 同步内容到活动工作区 + 类型检查 + 同步校验
RELEASE_DATE=2026_08_31 npm run check
RELEASE_DATE=2026_08_31 npm run validate

# 5. Studio 试听（音画同步）
RELEASE_DATE=2026_08_31 npm run dev

# 6. 渲染（自动 sync 后渲染到 out/<日期>/）
RELEASE_DATE=2026_08_31 npm run render          # 成片 out/<日期>/news-daily-<日期>.mp4
RELEASE_DATE=2026_08_31 npm run render:draft    # 半分辨率草稿
```

`RELEASE_DATE`（`YYYY_MM_DD`）决定读取/写入哪个日期目录；不传则用今天。`VERSION` 可附加到文件名（`release` 时由 workflow 传入）。

## 内容契约

`content/<日期>/script.json`：

```json
{
  "date": "2026-08-31",
  "items": [
    {"id": "intro", "kind": "intro", "title": "AI 新闻日报",
     "text": "开场旁白…", "screenText": "今日 4 条热点"},
    {"id": "news-1", "kind": "news", "title": "≤12字屏幕大字", "source": "36氪",
     "category": "科技", "text": "旁白，60-90字…", "screenText": "关键数字…",
     "summary": "屏幕说明正文，2-3 句，与旁白不重复…"},
    {"id": "outro", "kind": "outro", "title": "明天见",
     "text": "结语…", "screenText": "关注 · 每天与你 AI 读新闻"}
  ]
}
```

`title` 是屏幕大字，`text` 是旁白（配音），`screenText` 是画面关键点，`summary` 是屏幕说明正文（区别于旁白，负责结构化补充）。

## 可调项

- `TTS_RATE`：旁白语速（默认 `+4%`，可在 `.env` 覆盖）。
- `RELEASE_DATE`：目标日期目录（默认今天）。
- `CANDIDATES`：fetch 输出的候选条数上限（默认 40）。
- 新闻源在 `scripts/fetch.py` 的 `FEEDS` 列表，按 `（来源, 分类, RSS 地址）` 增删。

## 发版

见 [RELEASING.md](./RELEASING.md)：tag `<YYYY_MM_DD>-<semver>` 触发 GitHub Actions，从 `content/<日期>/` 渲染到 `out/<日期>/` 并上传 Release。
