#!/usr/bin/env bash
set -euo pipefail
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
python3 -m venv "$DIR/.venv"
"$DIR/.venv/bin/python" -m pip install yt-dlp imageio-ffmpeg
printf '安装完成。\n'
