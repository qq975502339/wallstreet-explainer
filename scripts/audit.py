# -*- coding: utf-8 -*-
"""成片像素质检：视频抽帧 vs 同时刻静帧，逐块比差。抓"静帧看着正常、视频里却坏了"
（字体回退成方框、图片解码竞态、worker 之间不一致、渐变字卡死）。

  python scripts/audit.py <片子目录> <video.mp4> [--step 2] [--thresh 38]

做法：ffmpeg 每 step 秒抽一帧 → render.mjs --stills 渲相同时刻 → 都缩到 960×540 求逐像素差 →
20×20 块均值里的最大值 > thresh 记一个 flag → 最坏的 8 帧拼"视频|静帧"并排图 out/audit/flagged.jpg。
退出码：0 = 无 flag 无缺帧；1 = 有（看 flagged.jpg，每条修掉或能解释）。
静帧正常不代表视频正常：交片前跑这一步（references/review.md）。
借自 xiaolin-explainer-packaging 的 audit.py，适配本项目 30fps 与 render.mjs 接口。"""
import json, os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
a = sys.argv[1:]
opt = lambda k, d: type(d)(a[a.index(k) + 1]) if k in a else d
if len(a) < 2:
    print(__doc__); sys.exit(1)
D, VID = a[0], a[1]
STEP, TH = opt('--step', 2.0), opt('--thresh', 38.0)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(D, 'out', 'audit'); V = os.path.join(OUT, 'v'); S = os.path.join(OUT, 's')
os.makedirs(V, exist_ok=True); os.makedirs(S, exist_ok=True)
for f in os.listdir(V): os.remove(os.path.join(V, f))
for f in os.listdir(S): os.remove(os.path.join(S, f))
dur = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', VID]))
times = [round(i * STEP, 2) for i in range(max(1, int(dur // STEP)))]   # 视频末帧在 dur-1/30，不取整秒端点
subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', VID, '-vf', f"select='not(mod(n\\,{int(round(STEP * 30))}))'",
                '-fps_mode', 'passthrough', os.path.join(V, 'v_%05d.png')], check=True)
subprocess.run(['node', os.path.join(ROOT, 'scripts', 'render.mjs'), '--dir', D, '--stills',
                ','.join(f'{t:.2f}' for t in times), '--out', S], check=True)
res = []
for k, t in enumerate(times):
    vp, sp = os.path.join(V, f'v_{k + 1:05d}.png'), os.path.join(S, f'still_{t:.2f}.png')
    if not (os.path.exists(vp) and os.path.exists(sp)):
        res.append((t, -1, -1)); continue
    A = np.asarray(Image.open(vp).convert('RGB').resize((960, 540)), np.float32)
    B = np.asarray(Image.open(sp).convert('RGB').resize((960, 540)), np.float32)
    d = np.abs(A - B).mean(2)
    blk = d[:540 // 20 * 20, :960 // 20 * 20].reshape(27, 20, 48, 20).mean((1, 3))
    res.append((t, float(d.mean()), float(blk.max())))
json.dump(res, open(os.path.join(OUT, 'audit.json'), 'w'))
miss = [r for r in res if r[1] < 0]
bad = sorted([r for r in res if r[2] > TH], key=lambda r: -r[2])
good = [r for r in res if r[1] >= 0]
print('frames', len(res), 'missing', len(miss), 'flagged', len(bad))
if good:
    print('mean diff median', round(float(np.median([r[1] for r in good])), 2),
          'block max p95', round(float(np.percentile([r[2] for r in good], 95)), 1))
for r in bad[:24]:
    print('flag', r[0], 's', round(r[1], 1), round(r[2], 1))
if bad:
    fnt = ImageFont.truetype('C:/Windows/Fonts/msyhbd.ttc', 16) if os.path.exists('C:/Windows/Fonts/msyhbd.ttc') else ImageFont.load_default()
    sh = Image.new('RGB', (960, 290 * min(8, len(bad))), 'black'); dr = ImageDraw.Draw(sh)
    for i, r in enumerate(bad[:8]):
        k = times.index(r[0])
        sh.paste(Image.open(os.path.join(V, f'v_{k + 1:05d}.png')).convert('RGB').resize((480, 270)), (0, i * 290))
        sh.paste(Image.open(os.path.join(S, f'still_{r[0]:.2f}.png')).convert('RGB').resize((480, 270)), (480, i * 290))
        dr.text((6, i * 290 + 272), f't={r[0]}s  video | still  blockmax {r[2]:.0f}', font=fnt, fill='yellow')
    sh.save(os.path.join(OUT, 'flagged.jpg'), quality=85)
    print('并排图 ->', os.path.join(OUT, 'flagged.jpg'))
sys.exit(1 if bad or miss else 0)
