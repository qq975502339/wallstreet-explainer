# -*- coding: utf-8 -*-
"""本机工具路径：scripts/local.json 里写 yt_dlp / ffmpeg / ffprobe（exe 路径或所在目录都行），没写就用 PATH。
yt-dlp 指到目录时取目录里的 yt-dlp.exe：它的便携配置（yt-dlp.conf）和 cookies 放在 exe 同目录会自动生效。
local.json 只放本机配置，不进仓库。"""
import json, os
from pathlib import Path

_L = {}
try:
    _L = json.loads(Path(__file__).with_name('local.json').read_text(encoding='utf-8'))
except Exception:
    pass

_KEY = {'yt-dlp': 'yt_dlp', 'ffmpeg': 'ffmpeg', 'ffprobe': 'ffprobe'}


def bin(name):
    v = _L.get(_KEY.get(name, name))
    if not v:
        return name
    p = Path(v)
    if p.is_dir():
        exe = p / (name + ('.exe' if os.name == 'nt' else ''))
        return str(exe) if exe.exists() else name
    return str(p)
