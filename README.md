# AI 新闻日报

把当天新闻做成一条竖版（9:16 · 1080×1920）抖音短视频。**内容（选题+摘要）由人工撰写**，自动管线只负责配音与渲染：

```text
人工：RSS 取材（可选 fetch）→ 挑选 → 写 script.json + narration.zh.txt
机器：Edge TTS 逐段 → 实测时长 → Remotion 渲染
```

采用「音频主时钟」同步：最终旁白音频实测时长驱动场景时间轴，杜绝用 `setTimeout`/`Date.now()`/手动 `audio.play()` 造成的漂移。方案与仓库外的 `~/video` 音画同步规范一致。

## 流水线

```text
scripts/fetch.py           RSS（国内外混合）→ 去重/24h → 写 candidates.json（供人工挑选，无 LLM）
人工撰写                   script.json（内容契约）+ narration.zh.txt（旁白分段）
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
npm install

# 1.（可选）抓当日候选新闻，供人工挑选取材
npm run fetch            # 写 public/voiceover/candidates.json

# 2. 人工撰写内容（无 LLM）
#    - 编辑 public/voiceover/script.json：items = intro + news-1..K + outro
#      title=屏幕大字(≤12字)、text=旁白(60-90字)、screenText=画面关键点
#    - 编辑 public/voiceover/narration.zh.txt：把每条 item.text 用空行 "\n\n" 分隔
#      段序必须与 script.json 的 items[] 顺序一致

# 3. 生成旁白 + 实测时长（每次改文案后必须重跑）
npm run voiceover

# 4. 类型检查 + 同步校验
npm run check
npm run validate

# 5. Studio 试听（音画同步）
npm run dev

# 6. 渲染
npm run render            # 成片 out/news-daily.mp4
npm run render:draft      # 半分辨率草稿，快速预览
```

`script.json` 与 `narration.zh.txt` 的段落数若与现有不一致，`voiceover` 后 `validate`/`timing.ts` 会在段数或顺序不匹配时阻止渲染。

## 内容契约

`public/voiceover/script.json`：

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
- `CANDIDATES`：fetch 输出的候选条数上限（默认 40）。
- 新闻源在 `scripts/fetch.py` 的 `FEEDS` 列表，按 `（来源, 分类, RSS 地址）` 增删。
