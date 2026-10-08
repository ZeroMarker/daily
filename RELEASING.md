# AI 新闻日报自动发版

日常发版由 `.github/workflows/daily.yml` 完成，无需人工写稿、提交或打标签。

1. 每天 UTC 00:30（北京时间 08:30）采集 RSS，自动筛选并生成 `content/<日期>/script.json` 和 `narration.zh.txt`。
2. 校验日期、必填字段、场景 id 和旁白分段。
3. 仅提交当天的内容文件到 `main`，创建 `<YYYY_MM_DD>-<semver>` 标签，原子推送提交和标签。
4. 直接调用可复用的 `release.yml`，检出该标签内容，生成配音、检查音画同步并渲染。
5. 校验视频同时包含音频与视频流，上传 GitHub Release。
6. `pages.yml` 在自动发行成功后更新杂志、日报和视频页面。

自动标签使用当日已有最高版本的下一个补丁版本，首次为 `1.0.0`。相同日期重跑会产生新版本，历史版本保留。

自动生成内容与配音失败时工作流失败，不会上传未经校验的视频。若内容已提交而渲染失败，可重跑 Auto publish daily，或用 `gh run rerun <run-id> --failed` 重新执行失败的发行任务。

GitHub 内置令牌推送不会再次触发普通 push 工作流，因此自动流程显式调用视频发行；Pages 通过 `workflow_run` 接续，不依赖二次 push 事件。

## 手动触发自动生产

```bash
gh workflow run daily.yml --ref main
```

该命令仍会自动完成采集、选题、文案、提交、配音、视频发行和 Pages 更新。

## 单独发行已有内容

兼容原有标签入口，适用于已有日报内容的重新渲染：

```bash
git tag 2026_10_08-1.0.1
git push origin 2026_10_08-1.0.1
```

此路径直接渲染标签中的内容，不重新抓取新闻。

产物为 `out/<日期>/news-daily-<日期>-<版本>.mp4`。提交源码、`script.json` 和 `narration.zh.txt`；候选、配音、实测时长、渲染视频与站点产物均不提交。
