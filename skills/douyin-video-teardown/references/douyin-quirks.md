# 抖音抓取实测坑（2026-10 验证）

## 0. 短链必须换成规范页
直接让浏览器打开 `https://v.douyin.com/xxx/`，会 302 到 `www.iesdouyin.com/share/video/<id>/`，
那个分享壳页的客户端路由经常停在 **"视频数据加载中"**，永远不出流。
先用 urllib 跟一次 302，把 `video/(\d+)` 抠出来换成 `https://www.douyin.com/video/<id>`，成功率立刻正常。
（`fetch.py` 的 `canonical()` 就干这个。）

## 1. yt-dlp 抓不了抖音
`yt-dlp -F "https://v.douyin.com/xxx/"` 的结局：

```
[Douyin] 7701365852911214251: Downloading web detail JSON
ERROR: [Douyin] 7701365852911214251: Fresh cookies (not necessarily logged in) are needed
```

`--cookies-from-browser chrome` 也救不了（Chrome 里根本没有 douyin.com 的 ttwid）。
所以别在这上面浪费时间，直接走浏览器。

## 2. 分享页的 SSR 是空的
`https://www.iesdouyin.com/share/video/<id>/?from_ssr=1` 返回 200、32 KB HTML，
但 `window._SSR_DATA` 里 `"data":{}`，`_ROUTER_DATA` 根本不存在，页面里没有任何 `.mp4` 或 `play_addr`。
`m.douyin.com/share/video/<id>` 同理。**只能等 JS 跑起来。**

## 3. 直连 API 被 Argus 拦
```
https://www.iesdouyin.com/aweme/v1/web/aweme/detail/?aweme_id=...&aid=1128
→ Blocked by ArgusSecurityPlugin Uifid Not Found
```
需要 a_bogus/X-Bogus 签名 + ttwid + msToken，属于另一条战线，本 skill 不走。

## 4. 媒体流里混着加载动画
页面会请求 `lf-douyin-pc-web.douyinstatic.com/.../uuu_265.mp4`（加载动画，206 返回）。
真正的片子在 `v*-web.douyinvod.com/.../video/tos/cn/.../media-video-hvc1/`。
`score_url()` 靠 `media-video` + `br=` 参数排序，把动画过滤掉。

## 5. 抖音现在基本只给 HEVC
实测 3 分 44 秒、1280×720 的片子：
```
Video: hevc (Main) (hvc1), yuv420p(tv, bt709), 1280x720, 202 kb/s
```
ffmpeg 能解，`ffprobe` 常常没有（静态 ffmpeg 包不带），所以 `frames.sh` 用
`ffmpeg -i` 的 stderr 解析时长。QuickTime/预览可能打不开原片，别怀疑文件坏了。

## 6. 评论区要滚才出，且常常要登录
`[data-e2e='comment-item']` 首次渲染约 9 条，滚动后才加载更多。
没登录时列表会变空 —— 这时候 `page.png` 比继续爬更有用。
**但作者回复往往在首屏那几条里**，值得用 `--comments` 试一次：
实测拿到了"现场实机演示明天再发"这种片子不说的关键信息。

## 7. Playwright 的浏览器目录受沙箱限制
在受限沙箱里 `uvx`/`uv` 会报 `Could not create temporary file ... Operation not permitted`。
设 `UV_CACHE_DIR`、`TMPDIR`、`UV_TOOL_DIR` 到工作目录即可。
playwright 用 `channel="chrome"` 驱动系统 Chrome，**不需要** `playwright install` 下 200 MB 浏览器。

## 8. 别用 media 非空判断"抓到了"
页面一进来就请求 `uuu_265.mp4`（加载动画），所以候选列表一开始就非空。
判断标准必须是 `pick_best()` 有结果（按 `media-video` + `br=` 打分），否则轮询会立刻退出、
然后拿不到真正的流。这个 bug 我踩过一次，症状是"候选 1 个、标题对了、但没下到片"。

## 9. drawtext 的两个硬要求
- 必须写全 `drawtext=fontfile=...`，漏掉 `drawtext=` 会报 `No option name`；
- 字体路径带空格（macOS 的 `Arial Bold.ttf`）必须用单引号包住，否则 filter 解析直接断在空格处。
- `tile` 和 `drawtext` 同图混用时，先在抽帧那一遍把时间码烧进画面，拼图只负责 `tile`——两件事分开做，画面才不花。
