---
name: bilibili-video-teardown
description: B站视频链接或本地视频的抽帧、分镜和证据驱动分析。Bilibili video frame extraction, storyboards and evidence-based teardown.
---

# B 站视频抽帧拆解

把公开 B 站视频转换为带时间码的分镜及可填写的分析报告。与抖音 skill 共用抽帧、裁剪和分析思路，下载入口使用 yt-dlp。

## 安装

```bash
cd <本 skill 目录>
bash scripts/setup.sh
```

需要 Python 3 和网络；安装 yt-dlp 和 imageio-ffmpeg。仅处理公开可访问的视频，不绕过登录或付费限制。下载受平台接口变化、地域和视频可用性影响；失败时保留错误，不猜测内容。

## 获取并分析

```bash
.venv/bin/python scripts/fetch.py 'https://www.bilibili.com/video/BV...' --out ./output
# 抓取结果会打印实际文件名；通常是 video.mp4
bash scripts/frames.sh ./output/video.mp4 ./output 5
.venv/bin/python scripts/report.py ./output
```

输出目录必须为空；多 P 视频可用 URL 的 `?p=2` 指定分 P。下载器优先选择包含音视频的单一格式；若平台只提供分离流，则下载无音频的视频流用于抽帧。画质可能不是最高。若结果不是 MP4，请以打印的实际文件名作为抽帧输入。已取得的本地视频也可直接传给 `frames.sh`。

先看 `storyboard.jpg`，再看 `sheets/`，需要读小字时用 `bash scripts/crop.sh <视频> <秒> <x> <y> <宽> <高> <输出.jpg> [倍率]`。按照 `references/analysis-rubric.md` 填写 `拆解.md`，结论逐条附时间码，区分画面证据和推断。报告是骨架，不是自动生成的分析。评论不自动抓取。
