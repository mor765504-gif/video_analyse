#!/usr/bin/env bash
# 环境体检 / 一次性安装。用法：bash setup.sh [--check]
set -u

CHECK=0
[ "${1:-}" = "--check" ] && CHECK=1
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$SKILL_DIR/.venv/bin/python"

ok()   { printf '  \033[32m✓\033[0m %s\n' "$1"; }
bad()  { printf '  \033[31m✗\033[0m %s\n' "$1"; }
note() { printf '    %s\n' "$1"; }

echo "== 依赖体检 =="

# ffmpeg：PATH → 常见目录 → venv 里的 imageio-ffmpeg
FF=""
if [ -n "${FFMPEG:-}" ] && [ -x "${FFMPEG}" ]; then FF="$FFMPEG"; fi
if [ -z "$FF" ]; then FF=$(command -v ffmpeg 2>/dev/null || true); fi
if [ -z "$FF" ]; then
  for c in /opt/homebrew/bin/ffmpeg /usr/local/bin/ffmpeg "$HOME/.local/bin/ffmpeg"; do
    [ -x "$c" ] && FF="$c" && break
  done
fi
if [ -z "$FF" ] && [ -x "$PY" ]; then
  FF=$("$PY" "$SKILL_DIR/scripts/ffbin.py" 2>/dev/null || true)
fi
if [ -n "$FF" ] && [ -x "$FF" ]; then ok "ffmpeg  $FF"; else bad "ffmpeg 未找到（setup 会自动装 imageio-ffmpeg 自带的静态版）"; fi

CHROME=""
for p in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
         "/Applications/Chromium.app/Contents/MacOS/Chromium" \
         "$(command -v google-chrome 2>/dev/null)" \
         "$(command -v chromium 2>/dev/null)"; do
  [ -n "$p" ] && [ -x "$p" ] && CHROME="$p" && break
done
if [ -n "$CHROME" ]; then ok "chrome  $CHROME"; else bad "Chrome/Chromium 未找到（要用真浏览器绕抖音反爬）"; fi

if command -v uv >/dev/null 2>&1; then ok "uv      $(command -v uv)"; else
  if command -v python3 >/dev/null 2>&1; then ok "python3 $(command -v python3)（无 uv，用 venv）"; else bad "uv 和 python3 都没有"; fi
fi

if [ -x "$PY" ] && "$PY" -c "import playwright" 2>/dev/null; then
  ok "playwright $("$PY" -c 'import importlib.metadata as m;print(m.version("playwright"))')"
else
  bad "playwright 未装（跑一次 bash setup.sh）"
fi

[ "$CHECK" = "1" ] && exit 0

echo "== 安装 =="
if command -v uv >/dev/null 2>&1; then
  uv venv "$SKILL_DIR/.venv" >/dev/null 2>&1 || true
  VIRTUAL_ENV="$SKILL_DIR/.venv" uv pip install playwright imageio-ffmpeg
else
  [ -d "$SKILL_DIR/.venv" ] || python3 -m venv "$SKILL_DIR/.venv"
  "$PY" -m pip install -q --upgrade pip
  "$PY" -m pip install -q playwright imageio-ffmpeg
fi

if [ -z "$FF" ]; then
  FF=$("$PY" "$SKILL_DIR/scripts/ffbin.py" 2>/dev/null || true)
  [ -n "$FF" ] && note "静态 ffmpeg: ${FF}（frames.sh 会自动找到，不用进 PATH）"
fi

echo "== 完成 =="
note "不下载 Playwright 自带浏览器，直接驱动系统 Chrome（channel=\"chrome\"）"
note "下一步：$SKILL_DIR/.venv/bin/python $SKILL_DIR/scripts/fetch.py \"<链接>\" --out ./片子"
