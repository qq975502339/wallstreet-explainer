#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""音乐候选试听与选定（A7）：python scripts/music_candidates.py <项目> [--pick N] [--gain-db -18]
列出 <项目>/music/candidates/ 下音频（时长/响度预估），打印试听命令；--pick 选定拷贝为 music/bed.<ext>
并在 music/SOURCES.md 追加一条待填许可记录（许可必须人工填全，否则 audit/人查拦）。
床相对人声约 -18 dB（咱们总响度 -14 LUFS 口径不变）；按拍点循环见 mix/bed 用法。"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    from local_bins import bin as tool
except ImportError:
    def tool(n): return n

ap = argparse.ArgumentParser()
ap.add_argument('project'); ap.add_argument('--pick', type=int); ap.add_argument('--gain-db', type=float, default=-18)
a = ap.parse_args()
proj = Path(a.project); cand = proj / 'music' / 'candidates'; cand.mkdir(parents=True, exist_ok=True)
files = sorted([p for p in cand.iterdir() if p.suffix.lower() in ('.wav', '.mp3', '.m4a', '.flac', '.ogg')])
if not files:
    print(f'{cand} 为空：先放 2–3 首可商用候选进来（许可记录写 music/SOURCES.md），再跑本脚本试听选定。'); sys.exit(0)
infos = []
for i, p in enumerate(files, 1):
    try:
        r = subprocess.run([tool('ffprobe'), '-v', 'error', '-show_entries', 'format=duration', '-of', 'json', str(p)], capture_output=True, text=True, check=True)
        dur = float(json.loads(r.stdout)['format']['duration'])
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError):
        dur = 0.0
    infos.append((i, p, dur))
    print(f'[{i}] {p.name}  {dur:.1f}s')
    print(f'    试听：ffplay -autoexit "{p}"   （或 ffmpeg -i "{p}" -f wav - | ffplay -autoexit -）')
print('选定后：python scripts/music_candidates.py <项目> --pick N  → 拷贝为 music/bed.<ext> 并登记 SOURCES.md（许可须人工填全）')
if a.pick:
    if not 1 <= a.pick <= len(files): sys.exit(f'--pick 超出 1..{len(files)}')
    i, p, dur = infos[a.pick - 1]
    bed = proj / 'music' / f'bed{p.suffix.lower()}'
    if bed.exists(): sys.exit(f'已存在，不覆盖：{bed}')
    shutil.copyfile(p, bed)
    src = proj / 'music' / 'SOURCES.md'
    old = src.read_text(encoding='utf-8') if src.exists() else '# 音乐来源与许可\n\n'
    old += f'- bed{p.suffix.lower()}：候选 {p.name}；时长 {dur:.1f}s；相对人声 {a.gain_db} dB；**许可/作者/页面待填**（填全前不得交片）\n'
    src.write_text(old, encoding='utf-8')
    print(f'✓ 选定 {bed}；SOURCES.md 已追加待填许可记录')
