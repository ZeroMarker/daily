# AI 新闻日报发版

仿照 `~/video` 的「tag 触发 → 渲染 → 上传 GitHub Release」体系，`daily` 以**日期 + semver** 作为发版单元。**日期即实际路径**：tag 中的下划线日期同时是内容目录（提交）与输出目录。

## Tag 格式

```bash
git tag 2026_08_31-1.0.0
git push origin 2026_08_31-1.0.0
```

格式为 `<YYYY_MM_DD>-<semver>`，例如 `2026_08_31-1.0.0`。与 `~/video` 的 `<project_key>-<semver>` 同构，只是 project_key 改为下划线日期，并与当天内容所在提交一一对应。推送 tag 后 `.github/workflows/release.yml` 会：

1. 解析日期与版本（非法格式直接报错）；
2. 安装 Node.js 22 依赖（`npm ci`）与 FFmpeg；
3. 安装 `edge-tts` 并从 `content/<日期>/narration.zh.txt` 生成旁白（写入 `content/<日期>/`）；
4. `npm run check`：同步 `content/<日期>` → 活动工作区并 `tsc`；
5. `npm run render`：同步后渲染到 `out/<日期>/news-daily-<日期>-<版本>.mp4`；
6. 校验 MP4 同时包含视频流与音频流；
7. 上传 GitHub Release。

## 日期对应实际文件路径

```text
content/
└── 2026_08_31/                      ← 提交：当日内容清单
    ├── script.json
    ├── narration.zh.txt
    └── segment-durations.json
out/
└── 2026_08_31/
    └── news-daily-2026_08_31-1.0.0.mp4   ← 渲染产物
```

`RELEASE_DATE`（`YYYY_MM_DD`）与 `VERSION` 环境变量可覆盖默认：不设置 `RELEASE_DATE` 时用 `date +%Y_%m_%d`（今天）；不设置 `VERSION` 时文件名省略版本。本地调试：

```bash
RELEASE_DATE=2026_08_31 VERSION=1.0.0 npm run render
```

## 提交约定

- **必须提交**：`content/<日期>/` 下的旁白文本、`script.json`，以及项目源码。
- **不提交**（gitignore）：`public/voiceover/`（活动同步工作区）、`segment-durations.json`、生成的 MP3、`candidates.json`、`out/`。

发版前先在 `content/<日期>/` 提交当天内容，再打 `<日期>-<版本>` tag。

## 推送 tag 触发发版

```bash
git tag 2026_08_31-1.0.0
git push origin 2026_08_31-1.0.0
```

工作流在 GitHub Actions 上运行，完成后在对应日期目录下生成 Release，资产名为 `news-daily-<日期>-<版本>.mp4`。
