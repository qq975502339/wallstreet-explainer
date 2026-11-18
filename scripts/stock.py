#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""免费图库 Pexels / Pixabay：搜片搜图 → 下载 → 记出处。只用来做空镜、气氛镜、通用画面，
不当当事人/当事公司的证据（优先级和规矩见 references/sourcing.md）。

  python stock.py search pexels "city night aerial" [-n 8] [--orientation landscape] [--min-dur 5] [--max-dur 20] [--page 1]
  python stock.py search pixabay "money" --photo [--category business] [--type photo] [--color blue]
  python stock.py get pexels <id或页面url> <输出.mp4> [--4k]                 # 视频默认挑 ≤1080p 的 hd；--4k 挑最大
  python stock.py get pexels <id或页面url> <输出.jpg> --photo [--size original|large2x|large|medium]
  python stock.py get pixabay <id或页面url> <输出.mp4> [--quality large|medium|small|tiny]
  python stock.py get pixabay <id或页面url> <输出.jpg> --photo

key（免费）：https://www.pexels.com/api/ 和 https://pixabay.com/api/docs/ 申请后写进 scripts/local.json：
  {"pexels_api_key": "...", "pixabay_api_key": "..."}   # 或环境变量 PEXELS_API_KEY / PIXABAY_API_KEY
get 写侧车 <输出>.json（作者/许可/页面/现成中文署名行），署名抄进片子 CREDITS.md / 简介（规矩 16：不上屏）。
视频下完接 footage.py 的 sheet / scenes / extract 挑入点、抽帧。

已知限制和坑：
- Pixabay 下载链接带会过期的 token，搜到就立刻下；per_page 只收 3–200（脚本自动夹住）。
- Pixabay 标准 API 图片最大 1280px，视频通常 1080p（个别有 4K 的 large）；Pexels 图片可 --size original、视频可 --4k。
- 限流：Pexels 约 200 次/小时，Pixabay 约 100 次/分钟；429/5xx 自动退避重试。
- 英文关键词结果多；候选看一遍再挑，别闭眼拿第一条（第一条大家都用，容易撞画面）。
- 两家许可都免费商用、无需署名，但禁止原样转售、禁止暗示画面里的人/品牌代言；出处照样写进简介。
"""
import json, os, re, sys, time, urllib.error, urllib.parse, urllib.request
from pathlib import Path

UA = 'wallstreet-explainer/1.0 (stock sourcing)'
try: LOCAL = json.loads(Path(__file__).with_name('local.json').read_text('utf-8-sig'))
except Exception: LOCAL = {}


def opt(name, default=None, cast=str):
    a = sys.argv
    return cast(a[a.index(name) + 1]) if name in a else default


def key(provider):
    env = {'pexels': 'PEXELS_API_KEY', 'pixabay': 'PIXABAY_API_KEY'}[provider]
    k = os.environ.get(env) or LOCAL.get(env.lower())
    if not k:
        site = 'https://www.pexels.com/api/' if provider == 'pexels' else 'https://pixabay.com/api/docs/'
        sys.exit(f'缺 {provider} 的 API key：去 {site} 免费申请，写进 scripts/local.json 的 "{env.lower()}"，或设环境变量 {env}')
    return k


def http(url, headers=None, timeout=120, tries=3):
    for i in range(tries):
        req = urllib.request.Request(url, headers={'User-Agent': UA, **(headers or {})})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and i < tries - 1:
                wait = (10 if e.code == 429 else 2) * (i + 1)
                print(f'HTTP {e.code}，等 {wait} 秒重试…', flush=True)
                time.sleep(wait)
                continue
            sys.exit(f'HTTP {e.code}: {url.split("?")[0]}\n{e.read()[:300].decode("utf-8", "replace")}')
        except (urllib.error.URLError, TimeoutError) as e:
            if i < tries - 1:
                time.sleep(2 * (i + 1))
                continue
            sys.exit(f'网络错误：{getattr(e, "reason", e)}')


def api(provider, path, params):
    k = key(provider)
    if provider == 'pexels':
        return json.loads(http('https://api.pexels.com' + path + '?' + urllib.parse.urlencode(params),
                               headers={'Authorization': k}))
    return json.loads(http('https://pixabay.com/api' + path + '?' + urllib.parse.urlencode({'key': k, **params})))


def rows_pexels(data, kind):
    out = []
    for it in data.get('videos' if kind == 'video' else 'photos', []):
        if kind == 'video':
            best = max(it.get('video_files', []), key=lambda f: f.get('width') or 0)
            w, h, dur, author = best.get('width'), best.get('height'), it.get('duration'), (it.get('user') or {}).get('name', '?')
            title = ''
        else:
            w, h, dur, author, title = it.get('width'), it.get('height'), None, it.get('photographer', '?'), it.get('alt') or ''
        out.append(dict(id=it['id'], dur=dur, w=w, h=h, author=author, title=title, page=it.get('url', '')))
    return out


def rows_pixabay(data):
    out = []
    for it in data.get('hits', []):
        vids = it.get('videos') or {}
        best = vids.get('large') or vids.get('medium') or {}
        out.append(dict(id=it['id'], dur=it.get('duration'), w=best.get('width') or it.get('imageWidth'),
                        h=best.get('height') or it.get('imageHeight'), author=it.get('user', '?'),
                        title=it.get('tags', ''), page=it.get('pageURL', '')))
    return out


def search(provider, query, kind, n, page):
    orient, cat, typ, color = opt('--orientation'), opt('--category'), opt('--type'), opt('--color')
    if provider == 'pexels':
        params = dict(query=query, per_page=max(1, min(n * 2, 80)), page=page)
        if orient: params['orientation'] = orient
        if color and kind == 'photo': params['color'] = color
        if cat or typ: print('提醒：--category / --type 只有 pixabay 支持，pexels 忽略')
        data = api(provider, '/videos/search' if kind == 'video' else '/v1/search', params)
        rows, total = rows_pexels(data, kind), data.get('total_results', 0)
    else:
        params = dict(q=query[:100], per_page=max(3, min(n * 2, 200)), page=page, safesearch='true')
        if cat: params['category'] = cat
        if typ: params['video_type' if kind == 'video' else 'image_type'] = typ
        if kind == 'photo':
            if orient: params['orientation'] = {'landscape': 'horizontal', 'portrait': 'vertical'}.get(orient, orient)
            if color: params['colors'] = color
        elif orient:
            print('提醒：pixabay 视频不支持 --orientation，忽略')
        data = api(provider, '/videos/' if kind == 'video' else '/', params)
        rows, total = rows_pixabay(data), data.get('total', 0)
    lo, hi = opt('--min-dur', 0, float), opt('--max-dur', 1e9, float)
    rows = [r for r in rows if kind == 'photo' or lo <= (r['dur'] or 0) <= hi][:n]
    for i, r in enumerate(rows):
        dur = f"{r['dur']}s | " if kind == 'video' else ''
        print(f"[{i}] {provider} {kind} {r['id']} | {dur}{r['w']}x{r['h']} | {r['author']}")
        if r['title']: print(f"    {r['title'][:90]}")
        print(f"    {r['page']}")
    if not rows:
        print('没有结果：换英文关键词、放宽时长/方向过滤，或换一家（pexels ↔ pixabay）')
    else:
        print(f'共约 {total} 条。下载：python stock.py get {provider} <id> <输出文件>' + (' --photo' if kind == 'photo' else ''))


def parse_id(s):
    if s.isdigit(): return s
    m = re.findall(r'\d+', urllib.parse.urlparse(s).path)
    if not m: sys.exit(f'从 {s} 里解析不出 id：给数字 id 或页面 URL')
    return m[-1]


def get(provider, ident, out, kind):
    id = parse_id(ident)
    if provider == 'pexels':
        it = api(provider, ('/videos/videos/' if kind == 'video' else '/v1/photos/') + id, {})
        if kind == 'video':
            files = sorted(it.get('video_files', []), key=lambda f: f.get('width') or 0, reverse=True)
            pool = [f for f in files if f.get('quality') == 'hd'] or files
            if '--4k' not in sys.argv:
                pool = [f for f in pool if (f.get('height') or 0) <= 1080] or pool
            if not pool: sys.exit('这条视频没有可下载的文件')
            sel = pool[0]
            url, w, h, dur, fps = sel['link'], sel.get('width'), sel.get('height'), it.get('duration'), sel.get('fps')
            author = (it.get('user') or {}).get('name', '?')
        else:
            size = opt('--size', 'large2x')
            src = it.get('src', {})
            url = src.get(size) or src.get('large2x') or src.get('original')
            if not url: sys.exit('这条照片没有可下载的文件')
            w, h, dur, fps, author = it.get('width'), it.get('height'), None, None, it.get('photographer', '?')
        page, credit = it.get('url', ''), f"{author} / Pexels"
        lic = 'Pexels License（免费商用、无需署名；禁止原样转售、禁止暗示代言）'
    else:
        hits = api(provider, '/videos/' if kind == 'video' else '/', {'id': id}).get('hits', [])
        if not hits: sys.exit(f'{provider} 找不到 {kind} {id}')
        it = hits[0]
        if kind == 'video':
            vids = it.get('videos', {})
            pref = opt('--quality', 'large')
            order = [pref] + [q for q in ('large', 'medium', 'small', 'tiny') if q != pref]
            sel = next((vids[q] for q in order if vids.get(q)), None)
            if not sel: sys.exit('这条视频没有可下载的文件')
            url, w, h, dur, fps = sel['url'], sel.get('width'), sel.get('height'), it.get('duration'), None
        else:
            url = it.get('largeImageURL') or it.get('webformatURL')
            if not url: sys.exit('这条图片没有可下载的文件')
            w, h, dur, fps = it.get('imageWidth'), it.get('imageHeight'), None, None
        author, page, credit = it.get('user', '?'), it.get('pageURL', ''), f"{it.get('user', '?')} / Pixabay"
        lic = 'Pixabay Content License（免费商用、无需署名；禁止原样转售、禁止暗示代言）'
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(http(url, timeout=300))   # Pixabay 链接带过期 token，拿到立刻下
    if kind == 'photo':
        try:
            from PIL import Image
            with Image.open(out) as im: w, h = im.size
        except Exception: pass
    meta = dict(provider=provider, kind=kind, id=int(id), author=author, license=lic, credit=credit,
                page=page, width=w, height=h, duration=dur, fps=fps, query=opt('--query'))
    Path(str(out) + '.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), 'utf-8')
    print(f'已存 {out}\n  署名：{credit}\n  许可：{lic}\n  页面：{page}')
    if kind == 'video':
        print(f'接下来：python footage.py sheet {out} 挑镜头 → scenes 查切点 → extract 抽帧')


if __name__ == '__main__':
    a = sys.argv[1:]
    if len(a) >= 2 and a[0] in ('search', 'get') and a[1] in ('pexels', 'pixabay'):
        kind = 'photo' if '--photo' in a else 'video'
        if a[0] == 'search':
            if len(a) < 3: sys.exit(__doc__)
            search(a[1], a[2], kind, opt('-n', 8, int), opt('--page', 1, int))
        else:
            if len(a) < 4: sys.exit('用法：stock.py get <pexels|pixabay> <id或页面url> <输出文件> [--photo]')
            get(a[1], a[2], a[3], kind)
    else:
        print(__doc__)
        sys.exit(1)
