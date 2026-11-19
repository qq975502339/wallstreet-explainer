#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""AutoDL 托管 ComfyUI 视频（两条路一个客户端）：
  默认 = H3 文生视频（AI 生成视频路径），workflow minimax_h3_b99_001；
  --presenter = 数字主持人大画幅路径（房间全屏/竖窗），workflow minimax_h3_image_audio_to_video_v2_15s，
  参考图 + 参考音频 + 逐段提示词，每次 5–15 秒整数。
移植自 OpenMontage tools/video/autodl_comfyui_video.py。key：scripts/local.json 的 autodl_token
（或环境变量 AUTODL_COMFYUI_TOKEN），权限组须绑定目标工作流（如 H3），否则 401/403。

  python scripts/autodl_video.py --prompt "<描述>" --out clip.mp4 [--duration 5] [--resolution 736p横] [--workflow <id>]
      （resolution 是工作流严格枚举：横 480p/720p/736p/1080p/2K + 竖同档；736p横=1280×736 H3 原生，默认；
       报 RequestParameterIsWrong 时按目标工作流页面的 options 改，不要猜）
  python scripts/autodl_video.py --presenter --prompt "<含硬约束的提示词>" --ref-image <url> --ref-audio <url> --duration 5..15 --out clip.mp4

--presenter 写提示词前必读 references/h3-prompt/（base-en/ref-en）与 references/ai-presenter.md 的
「口播镜头硬约束」：镜头/人体禁止项逐条写进 prompt。参考素材必须是工作流可访问的 URL，本机路径不行。
提交 POST /comfyui_workflow/{id} → task_id；轮询 GET /comfyui_workflow/result/{task_id} → SUCCESS 取
results[0].url（短效，立即下载）；FAILED 报 message。单次失败≠服务不可用：先查已有任务避免重复计费。
生成物是 AI 视频/AI 数字人：标"AI生成"、不得冒充真人或真实证据（rules.md）。
"""
import base64, json, mimetypes, os, sys, time, urllib.error, urllib.request
from pathlib import Path

BASE = os.environ.get('AUTODL_COMFYUI_BASE_URL', 'https://autodl.art/api/v1/comfyui').rstrip('/')
T2V_WORKFLOW = 'minimax_h3_b99_001'
PRESENTER_WORKFLOW = 'minimax_h3_image_audio_to_video_v2_15s'
try: LOCAL = json.loads(Path(__file__).with_name('local.json').read_text('utf-8-sig'))
except Exception: LOCAL = {}


def key():
    k = os.environ.get('AUTODL_COMFYUI_TOKEN') or LOCAL.get('autodl_token')
    if not k or k.startswith('#'):
        sys.exit('缺 AUTODL_COMFYUI_TOKEN：写进 scripts/local.json 的 "autodl_token"（权限组绑定目标工作流），或设环境变量')
    return k


def req(method, url, body=None):
    k = key()
    r = urllib.request.Request(url, data=json.dumps(body).encode('utf-8') if body is not None else None,
                               headers={'Authorization': k, 'Content-Type': 'application/json'}, method=method)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp: data = json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f'HTTP {e.code}: {e.read()[:400].decode("utf-8", "replace").replace(k, "[key]")}')
    except (urllib.error.URLError, TimeoutError) as e:
        sys.exit(f'网络错误：{getattr(e, "reason", e)}')
    if data.get('code') != 'Success':
        sys.exit(f'AutoDL 拒绝（code={data.get("code")}）：{data.get("msg") or data}')
    return data.get('data') or {}


def opt(n, d=None):
    a = sys.argv
    return a[a.index(n) + 1] if n in a else d


def media(v):
    """参考素材以流的方式进 body：url/data: 直传；本地文件读字节编 base64 data URI（不需要公网上传去处）。"""
    v = (v or '').strip()
    if v.startswith(('http://', 'https://', 'data:')): return v
    p = Path(v)
    if not p.is_file(): sys.exit(f'参考素材不存在：{v}')
    raw = p.read_bytes()
    mime = mimetypes.guess_type(p.name)[0] or 'application/octet-stream'
    return f'data:{mime};base64,{base64.b64encode(raw).decode("ascii")}'


ENUMS = {   # 修缺陷4：付费提交前预检枚举（实测/上游文档确认的值；未知工作流跳过枚举检查）
    T2V_WORKFLOW: ['480p横', '720p横', '736p横', '1080p横', '2K横', '480p竖', '720p竖', '736p竖', '1080p竖', '2K竖'],
    PRESENTER_WORKFLOW: ['768p横', '480p横', '768p竖', '480p竖'],
}


def main():
    # 修缺陷5：--resume <task_id> 只轮询+下载旧任务，不重新提交（超时后先查旧单，避免重复计费）
    if opt('--resume'):
        tid = opt('--resume')
        wf = opt('--workflow') or T2V_WORKFLOW
        out = Path(opt('--out') or f'autodl_{int(time.time())}.mp4')
        interval, timeout = float(opt('--poll', 10)), float(opt('--timeout', 600))
        deadline, last = time.time() + timeout, '?'
        while time.time() < deadline:
            p = req('GET', BASE + f'/comfyui_workflow/result/{tid}')
            last = p.get('status')
            if last == 'SUCCESS':
                results = p.get('results') or []
                if not results: sys.exit(f'SUCCESS 但无 results：{p}')
                url = results[0].get('url'); break
            if last == 'FAILED': sys.exit(f'FAILED：{p.get("message") or p}')
            time.sleep(interval)
        else:
            sys.exit(f'{timeout}s 仍 {last}；继续等或去 AutoDL 控制台看 task {tid}')
        out.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url, timeout=180) as r: out.write_bytes(r.read())
        print('resume 下载完成', out); return
    prompt = opt('--prompt')
    if not prompt:
        print(__doc__); sys.exit(1)
    presenter = '--presenter' in sys.argv
    wf = opt('--workflow') or (PRESENTER_WORKFLOW if presenter else T2V_WORKFLOW)
    out = Path(opt('--out') or f'autodl_{int(time.time())}.mp4')
    duration = int(opt('--duration', 5))
    resolution = opt('--resolution', '768p横' if presenter else '736p横')
    # 修缺陷4：预检（枚举/时长/素材），不合格不花钱提交；--force 跳过枚举检查
    if wf in ENUMS and resolution not in ENUMS[wf] and '--force' not in sys.argv:
        sys.exit(f'resolution「{resolution}」不在 {wf} 的已知枚举 {ENUMS[wf]}；改值或 --force（会花一次提交尝试）')
    if not (5 <= duration <= 15) if presenter else not (1 <= duration <= 30):
        sys.exit(f'duration {duration} 超范围（presenter 5–15 / t2v 1–30）')
    if presenter and not (opt('--ref-image') and opt('--ref-audio')):
        sys.exit('--presenter 需要 --ref-image 和 --ref-audio（url 或本地文件自动 base64 流）')
    for k in ('--ref-image', '--ref-audio'):
        v = opt(k)
        if v and not v.startswith(('http://', 'https://', 'data:')) and not Path(v).is_file():
            sys.exit(f'{k} 文件不存在：{v}')
    body = {'prompt': prompt, 'duration': duration, 'resolution': resolution}
    if opt('--ref-image'): body['ref_image_0'] = media(opt('--ref-image'))
    if opt('--ref-audio'): body['ref_audio_0'] = media(opt('--ref-audio'))
    if opt('--body'): body.update(json.loads(opt('--body')))   # 工作流额外字段透传
    d = req('POST', BASE + f'/comfyui_workflow/{wf}', body)
    tid = d.get('task_id')
    if not tid: sys.exit(f'响应里没有 task_id：{d}')
    print('task', tid, 'workflow', wf)
    interval, timeout = float(opt('--poll', 10)), float(opt('--timeout', 600))
    deadline, last = time.time() + timeout, '?'
    while time.time() < deadline:
        p = req('GET', BASE + f'/comfyui_workflow/result/{tid}')
        last = p.get('status')
        if last == 'SUCCESS':
            results = p.get('results') or []
            if not results: sys.exit(f'SUCCESS 但无 results：{json.dumps(p, ensure_ascii=False)[:300]}')
            url = results[0].get('url')
            break
        if last == 'FAILED':
            sys.exit(f'FAILED：{p.get("message") or p}')
        time.sleep(interval)
    else:
        sys.exit(f'{timeout}s 超时，最后状态 {last}；任务可能仍在跑：用 --resume {tid} 查旧单下载，不要直接重提（避免重复计费）')
    out.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url, timeout=180) as r: out.write_bytes(r.read())
    meta = dict(provider='autodl', workflow_id=wf, task_id=tid, prompt=prompt, duration=duration,
                resolution=body['resolution'], ai_generated=True,
                credit=f'AI 生成（AutoDL ComfyUI {wf}）',
                operation='presenter_image_audio' if presenter else 'text_to_video')
    Path(str(out) + '.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), 'utf-8')
    print(f'已存 {out}\n  验收：presenter 逐部位查颈/喉/下巴/肩/衣/麦/背景 + 口型对台词 + 首末帧构图；'
          't2v 按空镜/气氛镜用，标 AI生成，不当真实证据（references/ai-presenter.md）')


if __name__ == '__main__':
    main()
