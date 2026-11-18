#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成图（规矩 40）：只演拍不到的具体比喻物件（一枚币、一座楼、一条蛇吞大象）或中性纹理，
抠出来放进前后层、和真素材同光同调色；写实的在片子里标"AI生成"。不做电影感氛围大片当底。

  python gen_image.py "一枚金色硬币立在深蓝色细斜纹织物上，影棚柔光，写实产品摄影，暗背景" <片子>/assets/img/coin.png
  python gen_image.py "<prompt>" <out.png> [--model qwen-image-3.0-pro] [--size 1664*928] [--ref <图或url>]…

走 token-plan 网关的 qwen-image（和 OpenMontage 的 token_plan_image 同一条路）。key：local.json 的
qianwen_api_key 或环境变量 QIANWEN_API_KEY。--size 用 宽*高（默认 1664*928 即 16:9；写 none 用模型默认）。
--ref 给参考图（本地路径自动转 data URI，url 直传），可多个。
写侧车 <out>.json（prompt/模型/尺寸/AI生成标记），出处进 CREDITS.md；返回多张时其余存 <名>_2.png…。
生成图 URL 约 24 小时过期，拿到立刻下。生图按张计费，想好 prompt 再跑。
"""
import base64, json, mimetypes, os, sys, urllib.error, urllib.request
from pathlib import Path

BASE = 'https://token-plan.maas.qianwenaiapi.com/api/v1'
try: LOCAL = json.loads(Path(__file__).with_name('local.json').read_text('utf-8-sig'))
except Exception: LOCAL = {}


def opt(name, default=None):
    a = sys.argv
    return a[a.index(name) + 1] if name in a else default


def opt_all(name):
    a = sys.argv
    return [a[i + 1] for i, x in enumerate(a) if x == name and i + 1 < len(a)]


def key():
    k = os.environ.get('QIANWEN_API_KEY') or LOCAL.get('qianwen_api_key')
    if not k or k.startswith('#'):
        sys.exit('缺 QIANWEN_API_KEY：写进 scripts/local.json 的 "qianwen_api_key"，或设环境变量 QIANWEN_API_KEY')
    return k


def image_ref(v):
    if v.startswith(('http://', 'https://', 'data:')): return v
    p = Path(v)
    if not p.is_file(): sys.exit(f'参考图不存在：{v}')
    mime = mimetypes.guess_type(p.name)[0] or 'image/png'
    return f'data:{mime};base64,{base64.b64encode(p.read_bytes()).decode("ascii")}'


def main():
    a = sys.argv[1:]
    if len(a) < 2:
        print(__doc__)
        sys.exit(1)
    prompt, out = a[0], Path(a[1])
    model = opt('--model', 'qwen-image-3.0-pro')
    size = opt('--size', '1664*928')
    refs = opt_all('--ref')
    k = key()
    content = [{'image': image_ref(r)} for r in refs] + [{'text': prompt}]
    payload = {'model': model, 'input': {'messages': [{'role': 'user', 'content': content}]}}
    if size and size != 'none': payload['parameters'] = {'size': size}
    req = urllib.request.Request(BASE + '/services/aigc/multimodal-generation/generation',
                                 data=json.dumps(payload).encode('utf-8'),
                                 headers={'Authorization': f'Bearer {k}', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=300) as r:
            data = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f'HTTP {e.code}: {e.read()[:500].decode("utf-8", "replace").replace(k, "[key]")}')
    except (urllib.error.URLError, TimeoutError) as e:
        sys.exit(f'网络错误：{getattr(e, "reason", e)}')
    urls = [item['image'] for ch in data.get('output', {}).get('choices', [])
            for item in ch.get('message', {}).get('content', []) if item.get('image')]
    if not urls:
        sys.exit(f'网关没返回图：{json.dumps(data, ensure_ascii=False)[:500].replace(k, "[key]")}')
    out.parent.mkdir(parents=True, exist_ok=True)
    for i, url in enumerate(urls):
        if url.startswith('http://'): url = 'https://' + url[len('http://'):]
        dst = out if i == 0 else out.with_name(f'{out.stem}_{i + 1}{out.suffix}')
        with urllib.request.urlopen(url, timeout=120) as r:
            dst.write_bytes(r.read())
        meta = dict(provider='token_plan', model=model, prompt=prompt, size=size if size != 'none' else None,
                    refs=refs, ai_generated=True, credit=f'AI 生成（{model}）', usage=data.get('usage', {}))
        Path(str(dst) + '.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), 'utf-8')
        print(f'已存 {dst}\n  署名：{meta["credit"]}（规矩 40：写实的在片子里标"AI生成"，出处进 CREDITS.md）')
    print('提醒：只用来演拍不到的具体比喻或中性纹理；电影感氛围大片当底一眼假，不用。')


if __name__ == '__main__':
    main()
