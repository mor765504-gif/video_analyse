# douyin-video-teardown

把一条抖音分享链接变成可读的片子：原片 + 分镜 + 关键帧放大 + 一页拆解结论。

这是 `deploy/hermes/skills/` 下的**可执行型 skill**（与 `share-intake` 这类纯提示词 skill 不同，它带脚本）。
`SKILL.md` 是给模型看的流程；`scripts/` 是给人/agent 直接跑的落地件。

## 为什么不复用 `share-intake`

`share-intake` 负责"把链接变成文件"，拿到的通常是 HTML 页面或原片，不做逐帧分析。
本 skill 从"已经有链接"开始，负责把片子拆成可判断的证据：分镜、时间码、UI 放大、评论原话。

## 装

```bash
bash scripts/setup.sh            # 建本地 .venv：playwright + imageio-ffmpeg
bash scripts/setup.sh --check    # 体检：ffmpeg / chrome / uv / playwright
```

要点：

- **不下载** Playwright 自带浏览器，直接驱动系统 Chrome（`channel="chrome"`）。
- 系统没有 ffmpeg 也不影响：`imageio-ffmpeg` 会带一个静态版，`scripts/ffbin.py` 自动定位。
- `.venv/` 是本地缓存（约 180 MB），已在 `.gitignore` 里，不要提交。

## 跑

```bash
.venv/bin/python scripts/fetch.py "<分享链接>" --out ./片子 --comments
bash scripts/frames.sh ./片子/video.mp4 ./片子 5
bash scripts/crop.sh ./片子/video.mp4 21 60 150 1180 520 ./片子/grid21.jpg 2
.venv/bin/python scripts/report.py ./片子
```

产物：`video.mp4` / `meta.json` / `comments.txt` / `frames/` / `sheets/` / `storyboard.jpg` / `拆解.md`。

实测（2026-10-29，金鹰 omni 路演片 3′44″）：抓片 32 s、15.9 MB、45 帧、8 张 sheet、一屏分镜。

## 坑

见 [references/douyin-quirks.md](references/douyin-quirks.md)：短链壳页不出流、yt-dlp 抓不了、
SSR 是空的、Argus 拦直连、加载动画混进候选、HEVC、drawtext 与 tile 打架。

