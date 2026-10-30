---
name: douyin-video-teardown
description: 抖音/短视频链接 → 下载原片、抽帧、分镜拼图、逐段技术拆解。用于"帮我抽帧看看这个作品/这个视频技术实现怎么样"。Douyin share link → download, keyframe extraction, storyboard sheets, claim-vs-evidence teardown.
version: 1.0.0
metadata:
  hermes:
    tags: [AssistHub, douyin, video, teardown, frames]
---

# 抖音视频抽帧拆解

把一条分享链接变成"可读的片子"：原片 + 分镜 + 关键帧放大 + 一页拆解结论。

适用：抖音 `v.douyin.com` 短链、`www.douyin.com/video/<id>`、以及任何能被 Chrome 播出来的网页视频。
不适用：纯图文作品、需要登录才能看的私密作品（会明确报错，不要硬猜内容）。

## 0. 环境（只做一次）

```bash
bash scripts/setup.sh            # 建 .venv：playwright + imageio-ffmpeg
bash scripts/setup.sh --check    # 只体检：ffmpeg / chrome / uv / playwright
```

三件依赖：`ffmpeg`（抽帧/拼图）、`Google Chrome`（绕抖音反爬）、`uv` 或 `python3`（建 venv）。
**ffmpeg 没有也能跑**：setup 会装 `imageio-ffmpeg` 自带的静态版，`ffbin.py` 自动找到它，不用进 PATH。

## 1. 抓片

```bash
.venv/bin/python scripts/fetch.py "<分享链接或视频URL>" --out ./<项目名> [--comments] [--headed]
```

产出（都在 `--out` 目录）：

| 文件 | 内容 |
|---|---|
| `video.mp4` | 原片（自动选高码率；抖音多为 HEVC，ffmpeg 能解，QuickTime 可能不能） |
| `detail.json` | 作品元数据原文：标题、作者、发布时间、赞/评/转/藏、时长 |
| `meta.json` | 上面的扁平摘要（report.py 用它） |
| `comments.txt` | 评论区（含作者回复，最有信息量的部分，`--comments` 才有） |
| `.chrome-profile/` | 浏览器 profile；第二次起复用 cookie，快很多 |

耗时约 30–45 秒/条（其中 8–10 秒是等播放器出流）。冷 profile 偶尔卡在"视频数据加载中"，脚本会自动 reload，最多两次。

**不要用 yt-dlp**：抖音要 fresh cookies，十次九次报 `Fresh cookies are needed`，`--cookies-from-browser` 也救不了。
正确做法是让真 Chrome 打开页面，拦截网络层里的 `media-video-*` 媒体流，再用页面上下文下载（自带 cookie 与 Referer）。

## 2. 抽帧 + 分镜

```bash
bash scripts/frames.sh ./<项目名>/video.mp4 ./<项目名> [间隔秒=5]
```

产出 `frames/`（单帧，时间码已烧进画面）、`sheets/`（6 帧一张 3x2）、`storyboard.jpg`（全片一屏，5 列）。
默认 5 秒一格：3–4 分钟的片子约 45 帧，正好一屏看完不丢信息。

**看图的正确顺序**（省 token，也是这个 skill 的关键）：

1. 先读 `storyboard.jpg` —— 建立整片结构与章节；
2. 再读 1–2 张 `sheets/*.jpg` —— 看细节段落（UI、字幕、图表）；
3. 最后只对"要读文字的地方"裁剪放大：

```bash
bash scripts/crop.sh ./<项目名>/video.mp4 21.0 60 150 1180 520 ./<项目名>/grid21.jpg 2
#                            时间   x   y    w    h   输出            放大倍数
```

不要逐张读 45 个单帧——同一信息读两遍就是浪费。UI 小字（命题卡、图标名、角标）只能靠裁剪读，缩略图一定糊。

## 3. 拆解

```bash
.venv/bin/python scripts/report.py ./<项目名>
```

生成 `拆解.md` 骨架（元数据表 + 每 30 秒一行的时间轴 + 已嵌入的分镜 + 待填的八问）。
然后按 `references/analysis-rubric.md` 填：

1. **它声称什么**（字幕/口播/PPT，逐条抄原话）
2. **画面证明了什么**（哪个镜头是实机、哪个是设计稿/CG）
3. **数字从哪来**（有数据源的标源；没有的标"叙事"）
4. **流程是否完整**（有没有加载/失败/权限确认/成本——没有就是演的结果帧）
5. **约束与合规**（品牌、数据、审批、隐私）
6. **作者自己怎么说的**（评论区原话，往往比片子诚实）
7. **它缺什么**（你补得上的是什么）
8. **可复用的是什么**（方法论/结构，而不是片子）

## 4. 交付

- 正文放 2–4 张图：`storyboard.jpg` + 1–2 张关键帧 + 1 张放大裁剪；
- `present` 两个文件：`拆解.md` 和 `storyboard.jpg`；
- 结论先给判断（虚/实、能/不能落地），再给证据；每个判断挂时间码，别按剧情顺序复述。

## 5. 验收（跑完自查）

```bash
head -c 12 ./<项目名>/video.mp4 | xxd | head -1   # 应含 ftyp
ls ./<项目名>/frames | wc -l                      # ≈ 时长/间隔
```

`frames` 数量对、`storyboard.jpg` 每格有时间码、`meta.json` 有 author 和 duration_ms —— 三条齐了才算抓到。

## 常见坑

`references/douyin-quirks.md` 记了实测踩过的九条（分享页 SSR 是空的、Argus 拦直连、HEVC、加载动画混进候选、短链壳页卡加载、评论要滚动、多码率择优）。动手前扫一眼，能省 20 分钟。

## 边界

只分析已公开发布的视频；不碰私密作品、不绕登录墙、不把原片搬去二次发布。抽帧产物留在本地工作目录。

> `.venv/`（~180 MB，playwright）是本地缓存，跟着项目复制时删掉，第一次用跑一次 `setup.sh` 重建即可。
