# video_analyse

从 AssistHub 提取的视频抽帧与分析 skill，包含抖音视频抓取、抽帧、分镜拼图和分析模板。

## 安装与使用

将 `skills/douyin-video-teardown` 放入支持 `SKILL.md` 的 agent 的 skills 目录，或在该目录运行：

```bash
cd skills/douyin-video-teardown
bash scripts/setup.sh
.venv/bin/python scripts/fetch.py '<抖音分享链接>' --out ./output --comments
bash scripts/frames.sh ./output/video.mp4 ./output 5
.venv/bin/python scripts/report.py ./output
```

详见 [skill 使用说明](skills/douyin-video-teardown/README.md) 和 [SKILL.md](skills/douyin-video-teardown/SKILL.md)。运行时依赖 Python、FFmpeg、Chrome 和 Playwright；请勿提交生成的视频、浏览器 profile 或 cookie。

## B 站视频

已新增 [B 站视频拆解 skill](skills/bilibili-video-teardown/SKILL.md)，支持公开链接下载、抽帧和报告骨架。需要 Python、yt-dlp 和 FFmpeg；支持本地视频。请按该 skill 的安装说明操作。

## 来源

提取自 [AssistHub](https://github.com/mor765504-gif/assisthub) 的 `deploy/hermes/skills/douyin-video-teardown`，来源版本 `93623841b9c5988f80bdbe5ed46106603a906b48`。原项目运行时发布流程不属于本仓库的安装步骤。
