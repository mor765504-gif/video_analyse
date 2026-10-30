#!/usr/bin/env bash
# 抽帧 + 分镜拼图。用法：bash frames.sh <video.mp4> <outdir> [间隔秒=5]
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="$SKILL_DIR/.venv/bin/python"
[ -x "$PY" ] || PY="$(command -v python3)"

VIDEO="${1:?用法: frames.sh <video.mp4> <outdir> [间隔秒]}"
OUT="${2:?缺少 outdir}"
STEP="${3:-5}"

FF=$(FFMPEG="${FFMPEG:-}" "$PY" "$SKILL_DIR/scripts/ffbin.py" 2>/dev/null || true)
if [ -z "$FF" ]; then
  FF=$(command -v ffmpeg 2>/dev/null || true)
fi
[ -n "$FF" ] || { echo "缺 ffmpeg：先跑 bash $SKILL_DIR/scripts/setup.sh"; exit 1; }
[ -f "$VIDEO" ] || { echo "找不到 $VIDEO"; exit 1; }
mkdir -p "$OUT/frames" "$OUT/sheets"
rm -f "$OUT/frames/"*.jpg "$OUT/sheets/"*.jpg "$OUT/storyboard.jpg"

# 时长（macOS 常见静态 ffmpeg 没有 ffprobe，直接解析 -i 的 stderr）
DUR_RAW=$("$FF" -hide_banner -i "$VIDEO" 2>&1 | grep -m1 "Duration" | sed 's/.*Duration: \([0-9:.]*\).*/\1/' || true)
[ -z "${DUR_RAW:-}" ] && DUR_RAW="00:00:00.00"
IFS=: read -r HH MM SS <<<"$DUR_RAW"
DUR=$("$PY" -c "print(int('${HH:-0}')*3600+int('${MM:-0}')*60+int(float('${SS:-0}')))" 2>/dev/null || echo 0)

# 字体（没有就退化为不带时间码，绝不因此失败）
FONT=""
for f in "/System/Library/Fonts/Supplemental/Arial Bold.ttf" \
         "/System/Library/Fonts/Helvetica.ttc" \
         "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" \
         "/usr/share/fonts/TTF/DejaVuSans-Bold.ttf"; do
  if [ -f "$f" ]; then FONT="$f"; break; fi
done
DF=""
if [ -n "$FONT" ]; then
  # 注意：路径含空格必须单引号包住；前面的 drawtext= 不能省
  DF="drawtext=fontfile='${FONT}':text='%{pts\\:hms}':x=10:y=10:fontsize=26:fontcolor=yellow:box=1:boxcolor=black@0.6,"
fi

echo "[*] 时长 ${DUR}s，每 ${STEP}s 一帧"

# 一次成型：抽帧时就把时间码烧进画面（后面拼图直接复用，避免 drawtext+tile 打架）
"$FF" -hide_banner -loglevel error -i "$VIDEO" \
  -vf "fps=1/${STEP},scale=640:-1,${DF}null" -q:v 4 "$OUT/frames/f%03d.jpg"
N=$(ls "$OUT/frames" | wc -l | tr -d ' ')
echo "[✓] frames/ ${N} 张"

# 6 帧一张（3x2），从已带时间码的帧拼
"$FF" -hide_banner -loglevel error -framerate 1 -i "$OUT/frames/f%03d.jpg" \
  -vf "tile=3x2:padding=4:color=black" -fps_mode passthrough -q:v 3 "$OUT/sheets/sheet%02d.jpg" || true
S=$(ls "$OUT/sheets" 2>/dev/null | wc -l | tr -d ' ')
echo "[✓] sheets/ ${S} 张"

# 全片一屏：5 列
COLS=5
ROWS=$(( (N + COLS - 1) / COLS ))
[ "$ROWS" -lt 1 ] && ROWS=1
"$FF" -hide_banner -loglevel error -framerate 1 -i "$OUT/frames/f%03d.jpg" \
  -vf "scale=384:-1,tile=${COLS}x${ROWS}:padding=4:color=black" \
  -frames:v 1 -fps_mode passthrough -q:v 3 "$OUT/storyboard.jpg"
echo "[✓] storyboard.jpg  ${COLS}x${ROWS}"

cat <<EOF

下一步：
  1. 先看 $OUT/storyboard.jpg
  2. 需要读字的地方再裁剪：
     bash "$SKILL_DIR/scripts/crop.sh" "$VIDEO" <时间秒> <x> <y> <w> <h> "$OUT/crop.jpg" 2
  3. 出骨架："$PY" "$SKILL_DIR/scripts/report.py" "$OUT"
EOF
