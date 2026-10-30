# Video Analyse · 视频抽帧分析

**将公开的 B 站、抖音视频整理成分镜和可填写的分析报告。**  
Turn public Bilibili and Douyin videos into storyboards and an analysis report template.

[使用教程 / User guide](docs/USER_GUIDE.md) · [B 站 skill](skills/bilibili-video-teardown/SKILL.md) · [抖音 skill](skills/douyin-video-teardown/SKILL.md)

## 功能 / What it does

| 功能 / Feature | B 站 / Bilibili | 抖音 / Douyin |
|---|---|---|
| 获取公开视频 / Fetch public video | yt-dlp；可指定分 P / Select a part | Chrome + Playwright |
| 抽帧与分镜 / Frames and storyboards | ✓ | ✓ |
| 局部放大 / Crop details | ✓ | ✓ |
| 分析报告骨架 / Report template | ✓ | ✓ |
| 评论 / Comments | 暂不抓取 / Not fetched | 可选抓取 / Optional |

报告是供人或 agent 填写的骨架，不会自动生成事实判断。B 站若只提供分离流，当前下载的视频可能没有音频。平台接口和访问条件变化可能导致抓取失败。

The report is a template for a person or agent to fill in; it does not automatically generate factual conclusions. Bilibili downloads may be video-only when streams are separate. Platform changes and access restrictions can affect fetching.

## 快速开始 / Quick start

克隆仓库并进入所需 skill： / Clone the repository and choose a skill:

```bash
git clone https://github.com/mor765504-gif/video_analyse.git
cd video_analyse/skills/bilibili-video-teardown   # B 站 / Bilibili
# 或 / or: cd video_analyse/skills/douyin-video-teardown
bash scripts/setup.sh
```

然后按 [中英文使用教程](docs/USER_GUIDE.md) 获取视频、抽帧和生成报告。支持 `SKILL.md` 的 agent 也可以将对应 skill 目录安装到它的 skills 目录；具体位置由所用 agent 决定。

Follow the [bilingual user guide](docs/USER_GUIDE.md) to fetch a video, extract frames and create a report. For an agent that supports `SKILL.md`, install the relevant skill directory in that agent’s skills directory.

## 作者与来源 / Account and provenance

维护账号 / Maintainer: [@mor765504-gif](https://github.com/mor765504-gif)。抖音 skill 提取自 [AssistHub](https://github.com/mor765504-gif/assisthub)，来源版本 `93623841b9c5988f80bdbe5ed46106603a906b48`；B 站版在其抽帧与分析流程上改造。

The Douyin skill was extracted from AssistHub at the revision above; the Bilibili skill adapts its frame extraction and analysis workflow.
