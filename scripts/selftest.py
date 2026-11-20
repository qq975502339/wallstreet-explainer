#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""环境自检（A7）：python scripts/selftest.py
核心项失败退出 1；可选项缺失只 warn。新环境部署后先跑这个。"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
fails, warns, oks = [], [], []


def ok(m): oks.append(m)
def warn(m): warns.append(m)
def fail(m): fails.append(m)


# node
node = shutil.which('node')
if not node: fail('node 不在 PATH')
else:
    v = subprocess.run([node, '--version'], capture_output=True, text=True).stdout.strip()
    major = int(v.lstrip('v').split('.')[0])
    (ok if major >= 18 else fail)(f'node {v}' + ('' if major >= 18 else '（需 ≥18）'))
# playwright + chromium
try:
    sys.path.insert(0, str(ROOT / 'scripts'))
    pw = None
    for cand in (ROOT / 'node_modules' / 'playwright',):
        if cand.exists(): pw = cand
    if not pw: fail('playwright 未安装：npm install && npm run setup')
    else:
        r = subprocess.run([node, '-e', "const {chromium}=require('playwright');console.log(chromium.executablePath())"], capture_output=True, text=True, cwd=str(ROOT))
        if r.returncode == 0 and Path(r.stdout.strip()).exists(): ok('playwright chromium 可执行')
        else: fail('chromium 未下载：npm run setup（npx playwright install chromium）')
except Exception as e: fail(f'playwright 检查失败：{e}')
# ffmpeg/ffprobe
try:
    from local_bins import bin
except ImportError:
    def bin(n): return n
for t in ('ffmpeg', 'ffprobe'):
    p = shutil.which(bin(t))
    (ok if p else fail)(f'{t}：{p or "不在 PATH（可在 scripts/local.json 配路径）"}')
# python deps
for mod, core in (('numpy', True), ('PIL', True), ('librosa', False), ('faster_whisper', False), ('edge_tts', False)):
    try:
        __import__(mod); ok(f'python {mod}')
    except ImportError:
        (fail if core else warn)(f'python {mod} 缺失' + ('' if core else '（可选：pip install -r requirements.txt）'))
# fonts
lj = ROOT / 'scripts' / 'local.json'
fonts = None
if lj.exists():
    try: fonts = json.loads(lj.read_text(encoding='utf-8-sig')).get('fonts_dir')
    except ValueError: warn('local.json 解析失败')
if fonts and Path(fonts).is_dir():
    need = ['BebasNeue-Regular.ttf', 'AlimamaShuHeiTi-Bold.ttf', 'MiSans-Regular.ttf', 'Montserrat-VF.ttf']
    missing = [f for f in need if not (Path(fonts) / f).exists()]
    (ok if not missing else fail)(f'字体目录 {fonts}' + (f' 缺 {missing}' if missing else ' 关键字体齐全'))
else:
    fail('fonts_dir 未配置或不存在（scripts/local.json；缺字体会退系统字改版式）')
# keys（可选）
if lj.exists():
    j = json.loads(lj.read_text(encoding='utf-8-sig'))
    for k in ('qianwen_api_key', 'vidu_api_key', 'autodl_token'):
        v = j.get(k)
        (ok if v and not str(v).startswith('#') else warn)(f'key {k}' + ('' if v and not str(v).startswith('#') else ' 未填（对应生成路径不可用）'))
# kit 文件
for f in ('kit/kit.js', 'kit/scenes.js', 'kit/scenes_plus.js', 'kit/host.js', 'scripts/render.mjs', 'scripts/video_pipeline.py', 'scripts/fetch_footage.py'):
    (ok if (ROOT / f).exists() else fail)(f'{f} 存在' if (ROOT / f).exists() else f'{f} 缺失')

print(f'自检：{len(oks)} 过 · {len(fails)} 失败 · {len(warns)} 提醒')
for m in fails: print('  FAIL', m)
for m in warns: print('  warn', m)
sys.exit(1 if fails else 0)
