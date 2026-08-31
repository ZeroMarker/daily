# AI 新闻日报发版

仿照 `~/video` 的「tag 触发 → 渲染 → 上传 GitHub Release」体系，`daily` 以**日期 + semver** 作为发版单元：tag 中的下划线日期同时是输出文件夹名。

## Tag 格式

```bash
git tag 2026_08_31-1.0.0
git push origin 2026_08_31-1.0.0
```

格式为 `<YYYY_MM_DD>-<semver>`，例如 `2026_08_31-1.0.0`。与 `~/video` 的 `<project_key>-<semver>` 同构，只是 project_key 改为下划线日期，并与当天内容所在提交一一对应。推送 tag 后 `.github/workflows/release.yml` 会：

1. 解析日期与版本（非法格式直接报错）；
2. 安装 Node.js 22 依赖（`npm ci`）与 FFmpeg；
3. 安装 `edge-tts` 并生成旁白（`npm run voiceover`）；
4. 类型检查（`npm run check`）；
5. 渲染到日期文件夹 `out/<日期>/news-daily-<日期>-<版本>.mp4`（`npm run render`）；
6. 校验 MP4 同时包含视频流与音频流；
7. 上传 GitHub Release。

## 日期对应文件夹

`2026_08_31-1.0.0` 对应文件夹 `out/2026_08_31/`：

```text
out/
└── 2026_08_31/
    └── news-daily-2026_08_31-1.0.0.mp4
```

`RELEASE_DATE`（`YYYY_MM_DD`）与 `VERSION` 环境变量可覆盖默认：不设置 `VERSION` 时文件名省略版本；不设置 `RELEASE_DATE` 时用 `date +%Y_%m_%d`（今天）。本地调试：

```bash
RELEASE_DATE=2026_08_31 VERSION=1.0.0 npm run render
```

## 提交约定

- **必须提交**：旁白文本、`script.json` 内容契约、`segment-durations.json`、项目源码。
- **不提交**（gitignore）：生成的 MP3、`candidates.json`、`out/`。

发版前先在当前日期提交当天内容，再打 `<日期>-<版本>` tag。

## 推送 tag 触发发版

```bash
git tag 2026_08_31-1.0.0
git push origin 2026_08_31-1.0.0
```

工作流在 GitHub Actions 上运行，完成后在对应日期文件夹下生成 Release，资产名为 `news-daily-<日期>-<版本>.mp4`。
