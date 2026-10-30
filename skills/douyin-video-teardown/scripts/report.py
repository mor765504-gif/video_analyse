#!/usr/bin/env python3
"""生成 拆解.md 骨架：元数据 + 时间轴 + 嵌入分镜 + 八问清单。

用法: python report.py <项目目录> [--step 30]
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone, timedelta


def load_meta(d: str) -> dict:
    p = os.path.join(d, "meta.json")
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except Exception:
            pass
    # 回退：手工抓的目录可能只有 detail.json
    p = os.path.join(d, "detail.json")
    if os.path.exists(p):
        try:
            raw = json.load(open(p, encoding="utf-8"))
            a = raw.get("aweme_detail") or raw
            st = a.get("statistics") or {}
            v = a.get("video") or {}
            return {
                "desc": a.get("desc"),
                "author": (a.get("author") or {}).get("nickname"),
                "author_id": (a.get("author") or {}).get("unique_id"),
                "create_time": a.get("create_time"),
                "duration_ms": v.get("duration"),
                "digg": st.get("digg_count"),
                "comment": st.get("comment_count"),
                "share": st.get("share_count"),
                "collect": st.get("collect_count"),
            }
        except Exception:
            pass
    return {}


def fmt_dur(ms) -> str:
    if not ms:
        return "?"
    s = int(ms) // 1000
    return f"{s // 60}:{s % 60:02d}"


def fmt_time(ts) -> str:
    if not ts:
        return "?"
    return datetime.fromtimestamp(int(ts), timezone(timedelta(hours=8))).strftime("%Y-%m-%d %H:%M")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--step", type=int, default=30, help="时间轴粒度（秒）")
    a = ap.parse_args()
    d = a.dir
    m = load_meta(d)
    frames = sorted(os.listdir(os.path.join(d, "frames"))) if os.path.isdir(os.path.join(d, "frames")) else []
    dur_s = int((m.get("duration_ms") or 0) / 1000)

    rows = []
    for t in range(0, max(dur_s, a.step), a.step):
        rows.append(f"| {t//60:02d}:{t%60:02d} |  |  |")

    shots = []
    if os.path.exists(os.path.join(d, "storyboard.jpg")):
        shots.append("![全片分镜](storyboard.jpg)")
    for s in sorted(os.listdir(os.path.join(d, "sheets"))) if os.path.isdir(os.path.join(d, "sheets")) else []:
        shots.append(f"![{s}](sheets/{s})")

    title = (m.get("desc") or m.get("title") or "").splitlines()
    title = (title[0] if title else "").strip()[:120] or "（未取到标题，看 meta.json）"

    md = f"""# 拆解 · {m.get('author') or '未知作者'}

| 项 | 值 |
|---|---|
| 标题 | {title} |
| 作者 | {m.get('author') or '?'} ({m.get('author_id') or '-'}) |
| 发布 | {fmt_time(m.get('create_time'))} |
| 时长 | {fmt_dur(m.get('duration_ms'))}（{dur_s}s） |
| 数据 | 赞 {m.get('digg')} / 评 {m.get('comment')} / 转 {m.get('share')} / 藏 {m.get('collect')} |
| 抽帧 | {len(frames)} 帧 / 每 5s 一张 |
| 原链接 | {m.get('url') or '-'} |

## 一、时间轴

| 时间 | 画面 | 它声称什么 |
|---|---|---|
{chr(10).join(rows)}

## 二、分镜

{chr(10).join(shots)}

## 三、八问

1. **它声称什么**（抄原话，别转述）
   -
2. **画面证明了什么**（哪个是实机、哪个是设计稿/CG）
   -
3. **数字从哪来**（有源的标源，没源的标"叙事"）
   -
4. **流程完整吗**（有没有加载/失败/权限确认/成本）
   -
5. **约束与合规**（品牌、数据、审批、隐私）
   -
6. **作者自己怎么说**（comments.txt 里的原话）
   -
7. **它缺什么 / 我补得上什么**
   -
8. **可复用的方法论**
   -

## 四、结论

（先给判断：虚/实、能/不能落地，再给证据链。）
"""
    out = os.path.join(d, "拆解.md")
    with open(out, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"[✓] {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
