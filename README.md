# AI 新闻日报

把当天新闻自动做成一条竖版（9:16 · 1080×1920）抖音短视频：RSS 抓取 → LLM 精选摘要 → Edge TTS 旁白 → Remotion 渲染。

采用「音频主时钟」同步：最终旁白音频实测时长驱动场景时间轴，杜绝用 `setTimeout`/`Date.now()`/手动 `audio.play()` 造成的漂移。方案与仓库外的 `~/video` 音画同步规范一致。

## 流水线

```text
scripts/news.py           RSS（国内外混合）→ 去重/24h → LLM 选 Top-K → 摘要成日报文案
                          → 写出 script.json（内容契约）+ narration.zh.txt（旁白分段）
scripts/gen_voiceover.py  Edge TTS 逐段 → ffprobe 实测时长 → 合并 narration.zh.mp3
                          → 写出 segment-durations.json
src/timing.ts             用实测分段时长累加生成场景时间轴（音频主时钟）
src/                       Remotion 1080×1920 · 30fps · 帧驱动动画，<Audio> 挂载旁白
```

`script.json` 是唯一内容契约：`items[]` 顺序 = `narration.zh.txt` 的 `\n\n` 分段顺序 = `segment-durations.json` 时长顺序。段落数与场景数不一致时 `timing.ts` 直接抛错，挡住错误渲染。

## 环境

- Node.js 18+，Python 3.10+
- FFmpeg / ffprobe
- `pip install edge-tts requests`

## 运行

```bash
# 1. 配置 LLM（复制 .env.example 为 .env，填 base_url + key）
cp .env.example .env

# 2. 安装前端依赖
npm install

# 3. 抓取并生成今日文案（需要 .env 里的 LLM key）
npm run news

# 4. 生成旁白 + 实测时长
npm run voiceover

# 5. 类型检查 + 同步校验
npm run check
npm run validate

# 6. Studio 试听（音画同步）
npm run dev

# 7. 渲染
npm run render            # 成片 out/news-daily.mp4
npm run render:draft      # 半分辨率草稿，快速预览
```

不填 LLM key 时，`news.py` 会失败；此时可手写 `public/voiceover/script.json`、`narration.zh.txt` 和 `segment-durations.json`（各 6 项），仅同步/渲染链路可独立运行。

## 内容契约

`public/voiceover/script.json`：

```json
{
  "date": "2026-08-31",
  "items": [
    {"id": "intro", "kind": "intro", "title": "AI 新闻日报",
     "text": "开场旁白…", "screenText": "今日 6 条热点"},
    {"id": "news-1", "kind": "news", "title": "≤12字屏幕大字", "source": "36氪",
     "category": "科技", "text": "旁白，60-90字…", "screenText": "关键数字…"},
    {"id": "outro", "kind": "outro", "title": "明天见",
     "text": "结语…", "screenText": "关注 · 每天与你 AI 读新闻"}
  ]
}
```

`title` 是屏幕大字，`text` 是旁白，`screenText` 是画面关键点，互不重复。

## 可调项

- `NEWS_COUNT`：每天新闻条数（默认 6）。
- `TTS_RATE`：旁白语速（默认 `+4%`）。
- `LLM_MODEL`：摘要模型（默认 `gpt-4o-mini`）。
- 新闻源在 `scripts/news.py` 的 `FEEDS` 列表，按 `（来源, 分类, RSS 地址）` 增删。
