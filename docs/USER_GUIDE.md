# 使用教程 / User guide

本教程适用于 macOS 或其他提供 Python 3、FFmpeg 和兼容 shell 的环境。抖音抓取还需要系统 Google Chrome；安装脚本使用网络安装 Python 依赖。 / This guide assumes Python 3, FFmpeg and a compatible shell. Douyin fetching also needs Google Chrome. Setup installs Python dependencies over the network.

## 1. 下载与安装 / Clone and set up

```bash
git clone https://github.com/mor765504-gif/video_analyse.git
cd video_analyse
```

选择一个目录并运行安装脚本。 / Choose one directory and run setup:

```bash
cd skills/bilibili-video-teardown    # B 站 / Bilibili
# 或 / or: cd skills/douyin-video-teardown
bash scripts/setup.sh
```

每个 skill 使用独立的 `.venv`。安装包 `imageio-ffmpeg` 可以在没有系统 FFmpeg 时提供静态 FFmpeg。抖音版通过 Playwright 驱动系统 Chrome。 / Each skill has its own `.venv`. `imageio-ffmpeg` can supply a static FFmpeg when no system installation is available. The Douyin skill uses Playwright with system Chrome.

## 2. 获取视频 / Fetch a video

**B 站 / Bilibili** — 在 B 站 skill 目录中运行，`--out` 必须是新的或空目录；多 P 可在链接中使用 `?p=2`。 / From the Bilibili skill directory, use a new or empty output directory. For multipart videos use e.g. `?p=2`.

```bash
.venv/bin/python scripts/fetch.py 'https://www.bilibili.com/video/BV...' --out ./output
```

命令会打印实际视频文件名；通常为 `video.mp4`。仅有分离流时会下载无音频视频流。 / The command prints the actual filename, usually `video.mp4`. If only separate streams are available, it downloads a video-only stream.

**抖音 / Douyin** — 在抖音 skill 目录运行；`--comments` 可省略。 / From the Douyin skill directory; `--comments` is optional.

```bash
.venv/bin/python scripts/fetch.py 'https://v.douyin.com/...' --out ./output --comments
```

如需查看浏览器，可加 `--headed`。下载可能因平台限制、作品状态或网络失败。 / Add `--headed` to show the browser. Fetching can fail due to platform restrictions, video availability or network conditions.

## 3. 抽帧和报告 / Extract frames and create a report

在刚才使用的 skill 目录运行；将文件名替换为实际下载结果。最后的 `5` 表示每 5 秒抽一帧。 / Run from the same skill directory, replacing the filename with the actual download. `5` means one frame every five seconds.

```bash
bash scripts/frames.sh ./output/video.mp4 ./output 5
.venv/bin/python scripts/report.py ./output
```

也可以用本地视频作为 `frames.sh` 的第一个参数。 / An existing local video can also be used as the first argument to `frames.sh`.

| 文件 / File | 内容 / Contents |
|---|---|
| `frames/` | 单帧 / Individual frames |
| `sheets/` | 多帧分镜 / Contact sheets |
| `storyboard.jpg` | 全片分镜 / Overview storyboard |
| `meta.json` | 获取到的元数据 / Available metadata |
| `拆解.md` | 待填写的报告 / Report template to fill in |
| `comments.txt` | 抖音可选评论 / Optional Douyin comments |

先看总分镜，再检查相关分镜页。需要放大小字时，在 skill 目录执行： / Review the overview first, then relevant sheets. To enlarge a detail, run from the skill directory:

```bash
bash scripts/crop.sh ./output/video.mp4 21 60 150 1180 520 ./output/crop.jpg 2
# 视频、秒数、x、y、宽、高、输出、倍率 / video, seconds, x, y, width, height, output, scale
```

裁剪坐标需按原视频尺寸调整。按 `references/analysis-rubric.md` 填报告，并用时间码标注证据与推断。 / Adjust crop coordinates to the source dimensions. Fill the report using `references/analysis-rubric.md`, distinguishing evidence from inference and citing timestamps.

## 4. 常见问题 / Troubleshooting

- **安装失败 / Setup fails:** 检查 Python 和网络，然后重新运行 `bash scripts/setup.sh`。 / Check Python and network access, then rerun setup.
- **抖音抓取失败 / Douyin fetch fails:** 检查 Google Chrome，尝试 `--headed` 查看页面；更多细节见 [抖音说明](../skills/douyin-video-teardown/references/douyin-quirks.md)。 / Check Google Chrome and try `--headed`; see the linked notes.
- **B 站没有音频 / No Bilibili audio:** 当前分离流回退只下载视频轨，适合画面抽帧。 / The separate-stream fallback currently downloads video only for frame analysis.
- **文件名不同 / Different filename:** 抽帧时使用抓取命令打印的真实文件名。 / Pass the filename printed by the fetch command to the frame script.
- **报告内容为空 / Report is blank:** 这是正常的待填写模板。 / The report is intentionally a template to be filled in.

仅处理有权访问的内容；生成的视频、浏览器 profile、cookie 和个人资料应留在本地，不要提交到仓库。 / Process content you are authorized to access. Keep downloaded videos, browser profiles, cookies and personal data local and out of the repository.
