#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 bighead-collage 做好的人物故事段落（16:9 横屏）收进 wallstreet 主片，整屏穿插。
主片里这段用 kit 的 footage 场景全屏放，字幕走 bite 的分句 parts（主片字幕风格贯穿全片）。
做法见 references/bighead_insert.md。

  python insert_bighead.py <bighead工程目录> <主片目录> <片段名> [--from 0] [--to 段尾] [--gain 0]

bighead 工程要先按它自己的 skill 做完并交片：script.json 写 "aspect": "16:9"，final.mp4 是 1920×1080、
带声音、verify.py 过；段落里不加 captions()（字幕由主片出）。竖屏的 final.mp4 会被拒：回 bighead 改 aspect 重渲。
产物（都在主片目录里，渲染服务器根目录就是主片目录，../ 会 404）：
  assets/clips/<名>/0001.jpg…   30fps、1920×1080 帧序列（footage 场景用）
  assets/clips/counts.json      帧数登记（漏登记会黑屏）
  assets/bite/<名>.wav          段落声音
  assets/clips/<名>.json        交接侧车：来源工程、时长、文案、SOURCES.txt、AI生成标记
bite 的 parts 按 bighead timeline.json 逐句生成：[wav, 句入点, 句长, 句文字, 增益]，句间静音用空字幕 part 垫住
（parts 连续铺满整段，插段总长 = 段落长，画面音频不脱节）——主片字幕在插段期间逐句显示这段话。
"""
import json, subprocess, sys
from pathlib import Path
from local_bins import bin


def opt(name, default=None, cast=str):
    a = sys.argv
    return cast(a[a.index(name) + 1]) if name in a else default


def probe(f):
    out = subprocess.check_output([bin('ffprobe'), '-v', 'error', '-select_streams', 'v:0',
                                   '-show_entries', 'stream=width,height', '-show_entries', 'format=duration',
                                   '-of', 'json', str(f)])
    d = json.loads(out)
    return d['streams'][0]['width'], d['streams'][0]['height'], float(d['format']['duration'])


def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    if len(a) < 3:
        print(__doc__)
        sys.exit(1)
    BH, FILM, NAME = Path(a[0]).resolve(), Path(a[1]).resolve(), a[2]
    final = BH / 'final.mp4'
    if not final.exists():
        sys.exit(f'{final} 不存在：先按 bighead-collage 的 skill 把段落做完交片（references/bighead_insert.md）')
    w, h, dur = probe(final)
    if (w, h) != (1920, 1080):
        sys.exit(f'final.mp4 是 {w}x{h}，穿插段要 1920x1080 横屏：bighead 工程 script.json 写 "aspect": "16:9" 重渲（不要裁竖屏）')
    t0, t1 = opt('--from', 0.0, float), opt('--to', dur, float)
    seg = t1 - t0
    if seg <= 0: sys.exit('--to 要在 --from 后面')

    clips = FILM / 'assets' / 'clips' / NAME
    clips.mkdir(parents=True, exist_ok=True)
    for p in clips.glob('*.jpg'): p.unlink()
    subprocess.run([bin('ffmpeg'), '-v', 'error', '-y', '-ss', f'{t0:.3f}', '-t', f'{seg:.3f}', '-i', str(final),
                    '-vf', 'fps=30,scale=1920:1080:flags=lanczos', '-q:v', '3', str(clips / '%04d.jpg')], check=True)
    n = len(list(clips.glob('*.jpg')))
    cp = FILM / 'assets' / 'clips' / 'counts.json'
    counts = json.loads(cp.read_text('utf-8')) if cp.exists() else {}
    counts[NAME] = n
    cp.write_text(json.dumps(counts, indent=1), 'utf-8')

    bite = FILM / 'assets' / 'bite'
    bite.mkdir(parents=True, exist_ok=True)
    wav = bite / f'{NAME}.wav'
    subprocess.run([bin('ffmpeg'), '-v', 'error', '-y', '-ss', f'{t0:.3f}', '-t', f'{seg:.3f}', '-i', str(final),
                    '-vn', '-ac', '2', '-ar', '48000', str(wav)], check=True)

    gain = opt('--gain', '0')
    wavrel = f'assets/bite/{NAME}.wav'
    tl = BH / 'timeline.json'
    parts, lines = [], []
    if tl.exists():
        cur = 0.0
        for b in json.loads(tl.read_text('utf-8')).get('beats', []):
            s, e = b['start'] - t0, b['end'] - t0
            if e <= 0 or s >= seg: continue
            s, e = max(0.0, s), min(seg, e)
            if s > cur + .02:   # 句间静音也要占时间：空字幕 part 垫住，插段总长才等于段落长
                parts.append([wavrel, round(cur, 3), round(s - cur, 3), '', gain])
            parts.append([wavrel, round(s, 3), round(e - s, 3), b.get('text', ''), gain])
            lines.append(b.get('text', ''))
            cur = e
        if cur < seg - .02:
            parts.append([wavrel, round(cur, 3), round(seg - cur, 3), '', gain])
    if not parts:
        parts = [[wavrel, 0, round(seg, 3), '', gain]]
        sj = BH / 'script.json'
        if sj.exists(): lines = [ln.get('text', '') for ln in json.loads(sj.read_text('utf-8')).get('lines', [])]
        print('提醒：bighead 工程没有 timeline.json，bite 只生成整段一个 part（字幕要自己按句拆）')
    sources = (BH / 'SOURCES.txt').read_text('utf-8') if (BH / 'SOURCES.txt').exists() else ''
    meta = dict(source=str(BH), name=NAME, from_sec=t0, to_sec=t1, duration=round(seg, 3), frames=n,
                size=[1920, 1080], lines=lines, sources=sources, ai_generated=True,
                note='段落由 bighead-collage 制作（16:9 穿插）；SOURCES.txt 和 AI生成标记要并进主片 CREDITS.md')
    Path(str(clips) + '.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), 'utf-8')

    print(f'收好 {NAME}：{n} 帧（{seg:.2f}s，1920x1080）→ {clips}\n  声音 → {wav}\n  侧车 → {clips}.json')
    print(f'\nscript.json：铺垫句（比如 s05）后面插这段，parts 逐句带字幕（主片字幕风格贯穿全片）：')
    print(f'  {{"id": "s05", "text": "……铺垫句……", "gap": 0.4,')
    print(f'   "bite": {{"pre": 0.1, "post": 0.5, "parts": [')
    for p in parts: print(f'     {json.dumps(p, ensure_ascii=False)},')
    print(f'   ]}}}}')
    print(f'\nfilm.js：铺垫镜演到插段开口，footage 镜全屏放到下一句（时刻已对齐）：')
    print(f'  {{scene: "profile", …, until: "@bite_s05", says: "铺垫：要看懂这笔账，先看懂这个人"}},')
    print(f'  {{scene: "footage", clip: "{NAME}", until: "@s06", says: "……", badge: {{name: "……", color: "steel", at: "@bite_s05"}}}},')
    print(f'\n提醒：badge 把上一镜的人带进穿插段；收回镜接住段落里留下的东西；出处并进 CREDITS.md；重跑 timeline_stub / temp_voice 再 --check。')


if __name__ == '__main__':
    main()
