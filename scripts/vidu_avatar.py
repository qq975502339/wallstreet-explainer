#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vidu S2-Avatar 非实时版数字主持人：1 张单人图 + 音频（或文本）→ 说话视频。
角上圆窗（host:'pip'）的默认路径；房间全屏/竖窗走 AutoDL H3（autodl_video.py --presenter）。
移植自 OpenMontage tools/avatar/vidu_s2_avatar.py，改本项目惯例：key 走 scripts/local.json 的
vidu_api_key（或环境变量 VIDU_API_KEY）、纯标准库、侧车记 task_id/时长/积分、结果 URL 24h 过期立即下载。

  python scripts/vidu_avatar.py --image <图|url> --audio <音频|url> --out <片段.mp4> [--resolution 720p] [--timeout 300]
  python scripts/vidu_avatar.py --image <图> --text "<台词>" [--voice 音色] --out <片段.mp4>
      （text 模式让 Vidu 另配音色；默认不要——旁白先用 tts_tokenplan.py 出，音色全片一致，把该段音频传 --audio）

要点：同一形象全片同一张图；本地素材自动 base64（解码后 ≤20MB，更大先传公网 URL）；
失败按 err_code 处理（换图/充值/降轮询），不擅自换服务；验收=整段听口型 + fps=6 抽帧查颈/肩/衣/背景 + 首末帧构图比对。
详见 references/ai-presenter.md。生成的是 AI 数字人，不得称真人（规矩见 rules.md）。
"""
import base64, json, mimetypes, os, sys, time, urllib.error, urllib.request
from pathlib import Path

BASE = os.environ.get('VIDU_API_BASE_URL', 'https://api.vidu.cn').rstrip('/')
try: LOCAL = json.loads(Path(__file__).with_name('local.json').read_text('utf-8-sig'))
except Exception: LOCAL = {}


def key():
    k = os.environ.get('VIDU_API_KEY') or LOCAL.get('vidu_api_key')
    if not k or k.startswith('#'):
        sys.exit('缺 VIDU_API_KEY：写进 scripts/local.json 的 "vidu_api_key"，或设环境变量 VIDU_API_KEY')
    return k


def media(v, kind):
    v = (v or '').strip()
    if v.startswith(('http://', 'https://', 'data:')): return v
    p = Path(v)
    if not p.is_file(): sys.exit(f'{kind} 不存在：{v}')
    raw = p.read_bytes()
    if len(raw) > 20 * 1024 * 1024:
        sys.exit(f'{kind} {len(raw)/1048576:.1f}MB 超 base64 上限 20MB：先传公网 URL 再传 url')
    mime = mimetypes.guess_type(p.name)[0] or ('image/png' if kind == 'image' else 'audio/mpeg')
    return f'data:{mime};base64,{base64.b64encode(raw).decode("ascii")}'


def req(method, url, body=None):
    k = key()
    r = urllib.request.Request(url, data=json.dumps(body).encode('utf-8') if body is not None else None,
                               headers={'Authorization': f'Token {k}', 'Content-Type': 'application/json'}, method=method)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp: return json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f'HTTP {e.code}: {e.read()[:400].decode("utf-8", "replace").replace(k, "[key]")}')
    except (urllib.error.URLError, TimeoutError) as e:
        sys.exit(f'网络错误：{getattr(e, "reason", e)}')


def opt(n, d=None):
    a = sys.argv
    return a[a.index(n) + 1] if n in a else d


def main():
    image, audio, text = opt('--image'), opt('--audio'), opt('--text')
    if not image or not (audio or text):
        print(__doc__); sys.exit(1)
    out = Path(opt('--out') or f'vidu_avatar_{int(time.time())}.mp4')
    body = {'model': 'vidu-s2', 'image': media(image, 'image'),
            'resolution': (opt('--resolution', '720p') or '720p').lower(), 'watermark': False}
    if audio:
        body['audio'] = media(audio, 'audio')
    else:
        body['text'] = text
        if opt('--voice'): body['voice'] = opt('--voice')
    tl = opt('--timeline')
    if tl:
        p = json.loads(tl)
        body['timeline'] = json.dumps({'actions': p} if isinstance(p, list) else p, ensure_ascii=False)
    d = req('POST', BASE + '/ent/s_avatar/offline', body)
    tid = d.get('task_id') or (d.get('data') or {}).get('task_id')
    if not tid: sys.exit(f'响应里没有 task_id：{json.dumps(d, ensure_ascii=False)[:300]}')
    print('task', tid)
    interval, timeout = 4.0, float(opt('--timeout', 300))
    deadline, last, task = time.time() + timeout, '?', {}
    while time.time() < deadline:
        t = req('GET', BASE + f'/ent/v2/tasks/{tid}/creations')
        task = t.get('data') or t
        last = str(task.get('state') or '').lower()
        if last == 'success': break
        if last == 'failed':
            sys.exit(f'failed err_code={task.get("err_code")} err_msg={task.get("err_msg")}'
                     '（ImageCheckFaceFailed/MultiFaceDetected 等换角色图；CreditInsufficient 充值；TooManyRequests 降轮询；不擅自换服务）')
        time.sleep(interval); interval = min(interval + 1, 8)
    else:
        sys.exit(f'{timeout}s 超时，最后状态 {last}；任务可能仍在跑：用同 task_id 复查，避免重复计费')
    url = (task.get('creations') or [{}])[0].get('url')
    if not url: sys.exit('success 但没有 creations url')
    out.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=120) as r: out.write_bytes(r.read())
    meta = dict(provider='vidu', model=task.get('model') or 'vidu-s2', task_id=tid,
                duration=task.get('duration'), credits=task.get('credits'), ai_generated=True,
                credit='AI 数字人（Vidu S2-Avatar）',
                image_source='url' if image.startswith(('http', 'data:')) else 'local')
    Path(str(out) + '.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), 'utf-8')
    print(f'已存 {out}\n  duration={meta["duration"]} credits={meta["credits"]}'
          '\n  验收：整段听口型 + ffmpeg fps=6 抽帧查颈/肩/衣/背景 + 首末帧构图比对（references/ai-presenter.md）')


if __name__ == '__main__':
    main()
