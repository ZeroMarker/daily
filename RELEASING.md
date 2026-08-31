# AI 新闻日报发版

仿照 `~/video` 的「tag 触发 → 渲染 → 上传 GitHub Release」体系，`daily` 以**日期**作为发版单元：日期即 tag，也即输出文件夹。

## Tag 格式

```bash
git tag news-2026-08-31
git push origin news-2026-08-31
```

格式为 `news-<YYYY-MM-DD>`，与当天内容所在提交一一对应。推送 tag 后 `.github/workflows/release.yml` 会：

1. 解析日期（非法格式直接报错）；
2. 安装 Node.js 22 依赖（`npm ci`）与 FFmpeg；
3. 安装 `edge-tts` 并生成旁白（`npm run voiceover`）；
4. 类型检查（`npm run check`）；
5. 渲染到日期文件夹 `out/<日期>/news-daily-<日期>.mp4`（`npm run render`）；
6. 校验 MP4 同时包含视频流与音频流；
7. 上传 GitHub Release。

流程由 `~/video` 的 `render-release.yml` 改造而来，仅把「项目 key + semver」换成「日期」，并以仓库根为项目目录。

## 日期对应文件夹

每次发版的产物固定落在 `out/<日期>/`：

```text
out/
└── 2026-08-31/
    └── news-daily-2026-08-31.mp4
```

`RELEASE_DATE` 环境变量可覆盖默认日期；不设置时 `render` 使用 `date +%F`（今天）。本地调试可：

```bash
RELEASE_DATE=2026-08-31 npm run render
```

## 提交约定

- **必须提交**：旁白文本、`script.json` 内容契约、`segment-durations.json`、项目源码。
- **不提交**（gitignore）：生成的 MP3、`candidates.json`、`out/`。

发版前先在当前日期提交当天内容，再打 `news-<日期>` tag。

## 推送 tag 触发发版

```bash
git tag news-2026-08-31
git push origin news-2026-08-31
```

工作流在 GitHub Actions 上运行，完成后在该 tag 下生成 Release，资产名为 `news-daily-<日期>.mp4`。
