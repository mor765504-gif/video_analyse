#!/usr/bin/env python3
"""抓抖音/网页视频：真 Chrome 打开页面 → 拦截媒体流 → 带 cookie 下载。

用法:
  python fetch.py "<分享链接|视频页URL|直链.mp4>" --out ./片子 [--headed] [--comments] [--timeout 60]

产出: video.mp4 / detail.json / meta.json / comments.txt
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
from urllib.parse import urlparse, parse_qs

JUNK = ("uuu_265", "loading", "heic", "animation", "placeholder", "cover")


def log(msg: str) -> None:
    print(msg, flush=True)


def score_url(url: str) -> float:
    """挑码率最高的真实视频流；过滤加载动画/封面。"""
    low = url.lower()
    if any(j in low for j in JUNK):
        return -1
    s = 0.0
    if "media-video" in low:
        s += 300
    if "douyinvod" in low or "douyin" in low:
        s += 100
    try:
        q = parse_qs(urlparse(url).query)
        s += float(q.get("br", ["0"])[0]) / 10.0
    except Exception:
        pass
    if "avc1" in low:
        s += 50
    if "hvc1" in low or "265" in low:
        s += 10
    return s


def pick_best(urls: list[str]) -> str | None:
    ranked = sorted(((score_url(u), u) for u in urls), key=lambda x: x[0], reverse=True)
    return ranked[0][1] if ranked and ranked[0][0] > 0 else None


def flatten_detail(raw: str) -> dict:
    try:
        d = json.loads(raw)
    except Exception:
        return {}
    a = d.get("aweme_detail") or d.get("aweme_list", [{}])[0] or {}
    st = a.get("statistics") or {}
    vid = a.get("video") or {}
    return {
        "aweme_id": a.get("aweme_id"),
        "desc": a.get("desc"),
        "author": (a.get("author") or {}).get("nickname"),
        "author_id": (a.get("author") or {}).get("unique_id"),
        "create_time": a.get("create_time"),
        "duration_ms": vid.get("duration"),
        "digg": st.get("digg_count"),
        "comment": st.get("comment_count"),
        "share": st.get("share_count"),
        "collect": st.get("collect_count"),
        "music": (a.get("music") or {}).get("title"),
    }


def canonical(url: str, timeout: int = 20) -> str:
    """短链 v.douyin.com/xxx → 带 id 的规范页。

    直接用短链开浏览器会落到 iesdouyin 的分享壳页，客户端路由常常停在
    "视频数据加载中"；改用解析出来的 https://www.douyin.com/video/<id> 才稳。
    """
    if "/video/" in url and "douyin.com" in url:
        return url
    try:
        import urllib.request

        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            final = r.geturl()
    except Exception as e:
        log(f"[!] 短链解析失败：{e}（按原链接继续）")
        return url
    m = re.search(r"/video/(\d+)", final)
    if m:
        return f"https://www.douyin.com/video/{m.group(1)}"
    return final


async def fetch(url: str, out: str, headed: bool, want_comments: bool, timeout: int) -> int:
    from playwright.async_api import async_playwright

    os.makedirs(out, exist_ok=True)
    if url.lower().split("?")[0].endswith((".mp4", ".m4v")):
        return await fetch_direct(url, out, timeout)

    url = canonical(url)
    log(f"[*] 规范页：{url}")

    media: list[str] = []
    details: list[str] = []

    async with async_playwright() as p:
        kwargs = dict(
            user_data_dir=os.path.join(out, ".chrome-profile"),
            headless=not headed,
            viewport={"width": 1400, "height": 1000},
            args=["--disable-blink-features=AutomationControlled", "--no-first-run"],
        )
        try:
            ctx = await p.chromium.launch_persistent_context(channel="chrome", **kwargs)
        except Exception as e:
            log(f"[!] 系统 Chrome 起不来（{e}），改用 Playwright 自带 chromium")
            ctx = await p.chromium.launch_persistent_context(**kwargs)

        page = ctx.pages[0] if ctx.pages else await ctx.new_page()

        async def on_resp(r):
            u = r.url
            ct = (r.headers or {}).get("content-type", "")
            if ct.startswith("video/") or ".mp4" in u.split("?")[0]:
                if u not in media:
                    media.append(u)
            if "aweme/detail" in u and r.status == 200:
                try:
                    details.append(await r.text())
                except Exception:
                    pass

        page.on("response", on_resp)

        log(f"[*] 打开 {url}")
        try:
            await page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
        except Exception as e:
            log(f"[!] 导航超时/失败：{e}（继续等媒体流）")

        # 轮询等真正的媒体流（注意：加载动画 uuu_265.mp4 也会进候选，不能用 media 非空就退出）
        reloaded = 0
        for i in range(40):
            await page.wait_for_timeout(1000)
            if pick_best(media):
                break
            if reloaded < 2 and i >= 8 + reloaded * 10:
                try:
                    stuck = await page.locator("text=视频数据加载中").count()
                except Exception:
                    stuck = 0
                if stuck:
                    reloaded += 1
                    log(f"[*] 卡在'视频数据加载中'，reload（第 {reloaded} 次）")
                    try:
                        await page.reload(wait_until="domcontentloaded", timeout=timeout * 1000)
                    except Exception:
                        pass

        # <video> 已出 src 也算候选
        try:
            src = await page.evaluate(
                "() => { const v=document.querySelector('video'); return v ? (v.currentSrc || v.src || '') : ''; }"
            )
        except Exception:
            src = ""
        if src.startswith("http") and src not in media:
            media.append(src)

        title = await page.title()
        log(f"[*] 标题：{title[:120]}")

        if want_comments:
            await grab_comments(page, out)

        await page.screenshot(path=os.path.join(out, "page.png"))

        if details:
            with open(os.path.join(out, "detail.json"), "w", encoding="utf-8") as f:
                f.write(details[0])
            meta = flatten_detail(details[0])
            with open(os.path.join(out, "meta.json"), "w", encoding="utf-8") as f:
                json.dump({"title": title, "url": page.url, **meta}, f, ensure_ascii=False, indent=2)

        best = pick_best(media)
        if not best:
            log(f"[x] 没抓到视频流（候选 {len(media)} 个）。常见原因：需要登录、图文作品、或页面没自动播放。")
            log(f"    截图已存 {out}/page.png，可以 --headed 手看一次。")
            await ctx.close()
            return 2

        log(f"[*] 选中流：{best[:140]}")
        r = await page.request.get(best, headers={"Referer": "https://www.douyin.com/"})
        body = await r.body() if r.ok else b""
        await ctx.close()

    if not body:
        log("[x] 下载失败（cookie/Referer 被拒）")
        return 3
    path = os.path.join(out, "video.mp4")
    with open(path, "wb") as f:
        f.write(body)
    if not is_mp4(path):
        log("[!] 下回来的不是标准 MP4（可能是 m3u8 分片），先别抽帧")
        return 4
    size_mb = len(body) / 1e6
    log(f"[✓] {path}  {size_mb:.1f} MB")
    if size_mb < 0.5:
        log("[!] 文件偏小，可能是封面或片段")
    return 0


async def fetch_direct(url: str, out: str, timeout: int) -> int:
    import urllib.request

    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.douyin.com/"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = r.read()
    with open(os.path.join(out, "video.mp4"), "wb") as f:
        f.write(data)
    log(f"[✓] {out}/video.mp4  {len(data)/1e6:.1f} MB")
    return 0 if is_mp4(os.path.join(out, "video.mp4")) else 4


def is_mp4(path: str) -> bool:
    try:
        with open(path, "rb") as f:
            head = f.read(12)
        return b"ftyp" in head
    except OSError:
        return False


async def grab_comments(page, out: str) -> None:
    """评论区往往比片子诚实：作者自己会说'实机演示明天再发'之类。"""
    for label in ("全部评论", "评论"):
        try:
            await page.click(f"text={label}", timeout=2500)
            break
        except Exception:
            continue
    await page.wait_for_timeout(2500)
    for _ in range(6):
        await page.mouse.wheel(0, 900)
        await page.wait_for_timeout(600)
    items = await page.query_selector_all("[data-e2e='comment-item']")
    lines = []
    for el in items:
        try:
            lines.append((await el.inner_text()).replace("\n", " | "))
        except Exception:
            pass
    if lines:
        with open(os.path.join(out, "comments.txt"), "w", encoding="utf-8") as f:
            f.write("\n----\n".join(lines))
        log(f"[✓] comments.txt  {len(lines)} 条")
    else:
        log("[!] 没取到评论（要登录），可手看 page.png")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("url")
    ap.add_argument("--out", default="./video")
    ap.add_argument("--headed", action="store_true", help="开有头浏览器（调试/验证码时用）")
    ap.add_argument("--comments", action="store_true", help="顺带抓评论区")
    ap.add_argument("--timeout", type=int, default=60)
    a = ap.parse_args()
    try:
        return asyncio.run(fetch(a.url, a.out, a.headed, a.comments, a.timeout))
    except KeyboardInterrupt:
        return 130


if __name__ == "__main__":
    sys.exit(main())
