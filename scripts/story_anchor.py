#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""给透明 PNG 剪纸写锚点 json（ACTS.person 读 img/<名>.json：size/feet/top）。
脚踩点 = 不透明区域底边中点；top = 不透明区域顶边。横屏竖屏通用。

  python scripts/story_anchor.py <png> [<png> ...]      # 写同目录 <名>.json
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image

for p in sys.argv[1:]:
    p = Path(p)
    im = Image.open(p).convert('RGBA')
    a = np.asarray(im)[:, :, 3]
    ys, xs = np.where(a > 40)
    if len(xs) == 0:
        sys.exit(f'{p} 全透明，没法量锚点')
    x0, x1, y0, y1 = xs.min(), xs.max(), ys.min(), ys.max()
    feet = [float((x0 + x1) / 2), float(y1)]
    meta = {'size': [im.width, im.height], 'feet': feet, 'top': float(y0)}
    p.with_suffix('.json').write_text(__import__('json').dumps(meta, ensure_ascii=False, indent=1), 'utf-8')
    print(f'{p.name}: size={meta["size"]} feet={feet} top={meta["top"]}')
