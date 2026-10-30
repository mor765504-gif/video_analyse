#!/usr/bin/env python3
"""打印可用的 ffmpeg 绝对路径（给 shell 脚本用）。

顺序：$FFMPEG → PATH → 常见安装位 → 本 skill venv 里的 imageio-ffmpeg 静态版。
找不到则退出码 1。
"""
from __future__ import annotations

import os
import shutil
import sys

CANDIDATES = [
    "/opt/homebrew/bin/ffmpeg",
    "/usr/local/bin/ffmpeg",
    os.path.expanduser("~/.local/bin/ffmpeg"),
]


def main() -> int:
    env = os.environ.get("FFMPEG")
    if env and os.access(env, os.X_OK):
        print(env)
        return 0
    found = shutil.which("ffmpeg")
    if found:
        print(found)
        return 0
    for c in CANDIDATES:
        if os.access(c, os.X_OK):
            print(c)
            return 0
    try:
        import imageio_ffmpeg  # type: ignore

        exe = imageio_ffmpeg.get_ffmpeg_exe()
        if exe and os.access(exe, os.X_OK):
            print(exe)
            return 0
    except Exception:
        pass
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
