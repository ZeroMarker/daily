---
format: 1080x1920
duration: 53s
message: "DeepSeek V4.1 Flash-1017：同价同接口，Agent 与编程能力全面跃升，更快更省"
arc: Hook → 不变的 → 编程/Agent 跃升 → 推理/视觉 → 更快更省 → 同日搜索 API → CTA
audience: 关注 AI 模型的中文开发者与科技观众
mode: autonomous
music: confident minimal electronic tech underscore, light pulse
---

## Video direction

- **palette** — cobalt-grid from `frame.md`: warm cream `paper` ground with the permanent graph-paper grid; cobalt `ink` is the only ink (type, bars, rules); `ink-soft` for the "before" (old V4.1) values, full `ink` for the "after" (1017) values; `paper-2` for card fills. No other hues.
- **type** — all copy Simplified Chinese; display roles use Newsreader + Noto Serif CJK SC, labels Hanken Grotesk + Noto Sans CJK SC, numbers/model ids in DM Mono with tabular-nums. Hero lines ≤ 8 CJK chars.
- **motion grammar** — long-tail eases (power3 out), smooth not bouncy. VO-paced reveal: each number / label appears when the narration names it; never front-load. Bars grow and numbers count-up on their cue. During holds nothing breathes or floats.
- **rhythm** — Frames 1, 3, 4, 6 reveal on the VO; Frame 2 and Frame 7 are calm held cards (breathers before the data block and as the landing).
- **chrome** — top + bottom cobalt hairlines and a small mono tag "DEEPSEEK · 2026.10.17" top-left on every frame; a small "官方数据 / Source: DeepSeek Change Log" mono note on every frame showing benchmark numbers.
- **caption keep-out** — content stays in the top ~83% (above y≈1590); centered heroes anchor near y≈806.
- **negative list** — no purple/blue AI gradients, no bokeh, no fake logos, no invented numbers (only those in `capture/extracted/visible-text.txt`), no slideshow front-load-then-freeze, no screensaver floating.

## Frame 1 — 开场：1017 来了

- scene: 巨大的 "V4.1 Flash" 衬线字压在网格上，下方 mono 字 "-1017" 逐字打出，右侧像素故障列切入
- voiceover: "DeepSeek V4.1 Flash，刚刚升级——1017 版本，来了。"
- caption: "DeepSeek V4.1 Flash，刚刚升级——1017 版本，来了。"
- duration: 5.112s
- transition_in: cut
- status: animated
- src: compositions/frames/01-hook.html
- type: hook
- persuasion: Bold claim / news peg
- beat: anticipation
- blueprint: kinetic-type-beats (Adapt)
- focal: hero wordmark "V4.1 Flash" + "-1017" mono suffix
- roles: graph grid = background · pixel-glitch column right edge = supporting · "DEEPSEEK" micro label above = supporting
- sfx: impact-soft

narrativeRole: 抛出新闻钩子——同名模型迎来一次日期版升级。
keyMessage: DeepSeek V4.1 Flash 有了 1017 新版本。

Scene 1 (0.0–1.6s): "DEEPSEEK" micro label fades up at upper third; "V4.1" slams in at display-hero size centered y≈700 on "DeepSeek V4.1 Flash".
Scene 2 (1.6–3.2s): "Flash" slides up beneath "V4.1"; on "刚刚升级" the pixel-glitch column wipes in from the right edge.
Scene 3 (3.2–5.0s): on "1017 版本" a mono "-1017" types character by character under the wordmark inside a cobalt outlined pill; on "来了" the pill fills cobalt (text flips to paper) and holds.

## Frame 2 — 不变的：接口与价格

- scene: 三张堆叠卡片依次落下："调用方式 不变" "价格 不变" "deepseek-flash"，最后一行小字"官网 · APP 同步更新"
- voiceover: "调用方式不变，价格不变，模型名还是 deepseek-flash；官网和 APP 已同步更新。"
- caption: "调用方式不变，价格不变，模型名还是 deepseek-flash；官网和 APP 已同步更新。"
- duration: 6.696s
- transition_in: push-slide UP
- status: animated
- src: compositions/frames/02-unchanged.html
- type: product_intro
- persuasion: Risk reversal (nothing to migrate)
- beat: reassurance
- blueprint: grid-card-assemble (Adapt)
- focal: vertical stack of three cards
- roles: cards = foreground subject · grid = background · "官网 · APP 同步更新" line = supporting
- sfx: tick

narrativeRole: 先消除顾虑——升级零迁移成本。
keyMessage: 不用改代码，也不用多花钱。

Scene 1 (0.0–1.8s): vertical stack, upper two-thirds. Card 1 "调用方式 · 不变" drops in on "调用方式不变" with a cobalt check mark.
Scene 2 (1.8–3.6s): Card 2 "价格 · 不变" drops in on "价格不变"; Card 3 shows mono `model: "deepseek-flash"` typed in on "deepseek-flash".
Scene 3 (3.6–6.0s): on "官网和 APP" a hairline rule draws under the stack and "官网 · APP 同步更新" fades up; hold still.

## Frame 3 — 编程与 Agent：大幅跃升

- scene: 两组前后对比横条：Terminal-Bench 4.0 31.2→42.3，ProgramBench 20.3→29.1，新值数字滚动上涨并亮出增幅
- voiceover: "重点在 Agent 和编程：Terminal-Bench 4.0，从 31.2 涨到 42.3；ProgramBench，从 20.3 涨到 29.1。"
- caption: "重点在 Agent 和编程：Terminal-Bench 4.0，从 31.2 涨到 42.3；ProgramBench，从 20.3 涨到 29.1。"
- duration: 10.032s
- transition_in: push-slide UP
- status: animated
- src: compositions/frames/03-agent-coding.html
- type: feature_showcase
- persuasion: Before/after contrast
- beat: surprise
- blueprint: dataviz-countup (Adapt)
- focal: two before/after bar pairs with count-up numbers
- roles: bars = foreground subject · topbar-rule header "Agent · 编程" = supporting · grid = background · source note = supporting
- sfx: whoosh-soft, tick

narrativeRole: 用最大的两项涨幅证明这不是小修小补。
keyMessage: 终端 Agent 与真实编程任务提升最多（+11.1 / +8.8）。

Scene 1 (0.0–1.5s): topbar-rule header "Agent · 编程" draws in at top; full-width stacked bands layout begins.
Scene 2 (1.5–5.0s): band 1 label "Terminal-Bench 4.0"; on "31.2" an ink-soft bar grows to 31.2 with its number; on "42.3" a full-ink bar grows past it, number counts up to 42.3, a "+11.1" mono badge pops.
Scene 3 (5.0–9.0s): band 2 "ProgramBench": on "20.3" ink-soft bar; on "29.1" ink bar counts up, "+8.8" badge pops; source note "官方数据 · V4.1 (09-10) → 1017" fades at bottom of content area; hold.

## Frame 4 — 推理与视觉：全线上涨

- scene: 一个 ledger 表格逐行填入：HLE 36.8→42.6、DeepSWE 74.2→77.0、Automation-Bench 54.8→60.5、BabyVision 89.6→92.5
- voiceover: "推理、工具和视觉也全线上涨：HLE 42.6，DeepSWE 77.0，Automation-Bench 60.5，BabyVision 92.5。"
- caption: "推理、工具和视觉也全线上涨：HLE 42.6，DeepSWE 77.0，Automation-Bench 60.5，BabyVision 92.5。"
- duration: 10.92s
- transition_in: push-slide UP
- status: animated
- src: compositions/frames/04-ledger.html
- type: benefit_highlight
- persuasion: Accumulation / breadth proof
- beat: momentum
- blueprint: grid-card-assemble (Adapt)
- focal: four-row ledger table (name · old · new · delta)
- roles: ledger rows = foreground subject · header row = supporting · grid = background
- sfx: tick

narrativeRole: 证明提升是全面的，不止编程。
keyMessage: 推理、工具使用、视觉理解都有进步。

Scene 1 (0.0–1.5s): topbar-rule "全线上涨" + ledger header row (基准 · 旧 · 1017 · Δ) draws in, full-width strip layout.
Scene 2 (1.5–8.0s): one row per spoken name — HLE 36.8 → 42.6 (+5.8); DeepSWE v1.1 74.2 → 77.0 (+2.8); Automation-Bench 54.8 → 60.5 (+5.7); BabyVision 89.6 → 92.5 (+2.9). Each row slides in, new value counts up, delta in ink.
Scene 3 (8.0–10.0s): small note "HLE 为无工具 · BabyVision 为带工具 · 官方数据" fades under the table; hold.

## Frame 5 — 更快，更省

- scene: 两个向下的箭头指标："任务耗时 ↓" "输出长度 ↓"，汇聚成大字"更快 · 更省"
- voiceover: "而且，任务耗时和输出长度都降了——更快，也更省。"
- caption: "而且，任务耗时和输出长度都降了——更快，也更省。"
- duration: 4.872s
- transition_in: crossfade
- status: animated
- src: compositions/frames/05-efficiency.html
- type: benefit_highlight
- persuasion: Twist / and-also
- beat: relief
- blueprint: kinetic-type-beats (Adapt)
- focal: hero line "更快 · 更省"
- roles: two down-arrow chips = supporting · hero line = foreground subject · grid = background
- sfx: whoosh-soft

narrativeRole: 能力涨了，成本反而降了——反直觉的亮点。
keyMessage: 新版本跑任务更快、token 更少。

Scene 1 (0.0–2.4s): stacked top/bottom: chip "任务耗时 ↓" on "任务耗时", chip "输出长度 ↓" on "输出长度"; arrows draw downward.
Scene 2 (2.4–5.0s): chips shrink up; "更快" then "更省" punch in at display-chapter size centered y≈806 on their words; hold.

## Frame 6 — 同日：开放自研搜索 API

- scene: 一个搜索框中打出"search"，下方两个大数字："数亿次 / 每日请求" "数千亿 / 索引网页"，再出过滤标签
- voiceover: "同一天，DeepSeek 还开放了自研搜索 API：每天处理数亿次请求，索引数千亿网页，过滤 SEO 垃圾和低质 AI 内容。"
- caption: "同一天，DeepSeek 还开放了自研搜索 API：每天处理数亿次请求，索引数千亿网页，过滤 SEO 垃圾和低质 AI 内容。"
- duration: 10.392s
- transition_in: cut
- status: animated
- src: compositions/frames/06-search-api.html
- type: feature_showcase
- persuasion: Bonus reveal
- beat: delight
- blueprint: prompt-type-submit-generate (Adapt)
- focal: search box + two stacked stat blocks
- roles: search box = foreground subject · stat blocks = foreground · filter tags = supporting · qr-block corner = supporting · grid = background
- sfx: tick, impact-soft

narrativeRole: 同日第二条新闻，扩展到生态。
keyMessage: DeepSeek 自研搜索能力开放给开发者。

Scene 1 (0.0–2.5s): label "同日发布 · 2026.10.17" then a cobalt-outlined search box at upper third; caret types "自研搜索 API" on "自研搜索 API".
Scene 2 (2.5–6.5s): stacked stat blocks below: "数亿次" + "每日请求" on its cue; "数千亿" + "索引网页" on its cue.
Scene 3 (6.5–10.0s): three strike-through tags pop in a row: "SEO 垃圾" "GEO 操纵" "低质 AI 内容" each crossed by a cobalt line on "过滤…"; hold.

## Frame 7 — 收尾：现在就试

- scene: 中央大字 "deepseek-flash" mono 字样在代码卡片中，上方"现在可用"，下方小字"推荐 DeepSeek Harness 0.2.1-rc.1+"
- voiceover: "现在，调用 deepseek-flash 就能体验 1017 新版本。"
- caption: "现在，调用 deepseek-flash 就能体验 1017 新版本。"
- duration: 4.896s
- transition_in: crossfade
- status: animated
- src: compositions/frames/07-cta.html
- type: cta
- persuasion: Clear next step
- beat: confidence
- blueprint: titlecard-reveal (Adapt)
- focal: code card with `deepseek-flash`
- roles: code card = foreground subject · "现在可用" headline = supporting · harness note + qr-block = supporting · grid = background
- sfx: impact-soft

narrativeRole: 给出唯一行动——调用模型名。
keyMessage: 直接用 deepseek-flash 即可。

Scene 1 (0.0–2.0s): headline "现在可用" slide-up crossfade at upper third; paper-2 code card with mono `model = "deepseek-flash"` reveals centered y≈806 on "deepseek-flash".
Scene 2 (2.0–5.0s): note "推荐搭配 DeepSeek Harness 0.2.1-rc.1+" and "V4.1-Flash-1017 · 2026.10.17" fade up; qr-block corner punctuation; hold still.
