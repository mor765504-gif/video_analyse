#!/usr/bin/env python3
"""Download a public Bilibili video and save metadata for report.py."""
import argparse
import json
import pathlib
import sys
from urllib.parse import urlparse


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url', help='Bilibili video or b23.tv URL; use ?p= for a part')
    parser.add_argument('--out', required=True, help='new or empty output directory')
    args = parser.parse_args()
    parsed = urlparse(args.url)
    host = (parsed.hostname or '').lower()
    if parsed.scheme not in ('http', 'https') or not (host == 'b23.tv' or host == 'bilibili.com' or host.endswith('.bilibili.com')):
        parser.error('Expected an http(s) bilibili.com or b23.tv URL')
    out = pathlib.Path(args.out).resolve()
    if out.exists() and any(out.iterdir()):
        parser.error('output directory must be empty to prevent overwriting files')
    out.mkdir(parents=True, exist_ok=True)
    try:
        import yt_dlp
    except ImportError:
        parser.error('yt-dlp missing: run bash scripts/setup.sh')
    options = {
        'noplaylist': True,
        # Fall back to video-only when Bilibili exposes separate DASH streams.
        'format': 'best[ext=mp4][vcodec!=none][acodec!=none]/best[vcodec!=none][acodec!=none]/bestvideo[ext=mp4]/bestvideo',
        'outtmpl': str(out / 'video.%(ext)s'),
        'restrictfilenames': True,
    }
    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(args.url, download=True)
            filename = pathlib.Path(ydl.prepare_filename(info))
        duration = info.get('duration')
        meta = {'title': info.get('title'), 'desc': info.get('title'),
                'author': info.get('uploader') or info.get('channel'),
                'author_id': info.get('uploader_id'), 'create_time': info.get('timestamp'),
                'duration_ms': int(duration * 1000) if duration is not None else None,
                'digg': info.get('like_count'), 'comment': info.get('comment_count'),
                'url': info.get('webpage_url') or args.url, 'video_file': filename.name}
        (out / 'meta.json').write_text(json.dumps(meta, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        print(f'Video: {filename}\nMetadata: {out / "meta.json"}')
        return 0
    except Exception as exc:
        print(f'Download failed: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
