#!/usr/bin/env bash
# 定点裁剪放大：读 UI 小字/角标/水印的唯一正确姿势。
# 用法：bash crop.sh <video> <时间秒> <x> <y> <w> <h> <out.jpg> [放大倍数=2]
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$SKILL_DIR/.venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3)"

VIDEO="${1:?video}"; T="${2:?时间秒}"; X="${3:?x}"; Y="${4:?y}"; W="${5:?w}"; H="${6:?h}"; OUT="${7:?out.jpg}"; S="${8:-2}"

FF=$(FFMPEG="${FFMPEG:-}" "$PY" "$SKILL_DIR/scripts/ffbin.py" 2>/dev/null || true)
[ -n "$FF" ] || FF=$(command -v ffmpeg 2>/dev/null || true)
[ -n "$FF" ] || { echo "缺 ffmpeg：先跑 bash $SKILL_DIR/scripts/setup.sh"; exit 1; }

"$FF" -hide_banner -loglevel error -ss "$T" -i "$VIDEO" -frames:v 1 \
  -vf "crop=${W}:${H}:${X}:${Y},scale=iw*${S}:-1" -q:v 2 "$OUT"

echo "[✓] $OUT  (t=${T}s  ${W}x${H} @ ${X},${Y}  x${S})"
