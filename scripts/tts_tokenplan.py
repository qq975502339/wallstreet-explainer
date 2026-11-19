#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Token Plan 旁白：qwen-audio-3.0-tts-plus，默认音色 longanlingxin（主持人与主线旁白默认）。
移植自 OpenMontage tools/graphics/token_plan_media.py 的 TokenPlanTTS。key 复用 gen_image.py 的
qianwen_api_key（scripts/local.json）或环境变量 QIANWEN_API_KEY；不要把密钥写进命令/日志/素材。

  python scripts/tts_tokenplan.py "<台词>" <out.mp3|wav> [--voice longanlingxin] [--model qwen-audio-3.0-tts-plus]

out 写 .wav 时自动用 ffmpeg 转 48k 单声道（可直接喂 temp_voice.py --asr / host_timeline.py）。
数字主持人驱动音频：按句分段生成，把对应段音频传给 vidu_avatar.py --audio / autodl_video.py --ref-audio，
不要让 Vidu 用 text 另配一套声音。音频链接可能过期，立即下载；用前听一遍查台词/停顿/发音，按实际时长对齐。
"""
import json, os, subprocess, sys, urllib.error, urllib.request
from pathlib import Path
from local_bins import bin

BASE = 'https://token-plan.maas.qianwenaiapi.com/api/v1'
try: LOCAL = json.loads(Path(__file__).with_name('local.json').read_text('utf-8-sig'))
except Exception: LOCAL = {}


def key():
    k = os.environ.get('QIANWEN_API_KEY') or LOCAL.get('qianwen_api_key')
    if not k or k.startswith('#'):
        sys.exit('缺 QIANWEN_API_KEY：写进 scripts/local.json 的 "qianwen_api_key"，或设环境变量 QIANWEN_API_KEY')
    return k


def opt(n, d=None):
    a = sys.argv
    return a[a.index(n) + 1] if n in a else d


def main():
    a = [x for x in sys.argv[1:] if not x.startswith('--')]
    if len(a) < 2:
        print(__doc__); sys.exit(1)
    text, out = a[0], Path(a[1])
    k = key()
    payload = {'model': opt('--model', 'qwen-audio-3.0-tts-plus'),
               'input': {'text': text, 'voice': opt('--voice', 'longanlingxin'), 'format': 'mp3', 'sample_rate': 22050}}
    r = urllib.request.Request(BASE + '/services/audio/tts/SpeechSynthesizer',
                               data=json.dumps(payload).encode('utf-8'),
                               headers={'Authorization': f'Bearer {k}', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(r, timeout=180) as resp: data = json.load(resp)
    except urllib.error.HTTPError as e:
        sys.exit(f'HTTP {e.code}: {e.read()[:400].decode("utf-8", "replace").replace(k, "[key]")}')
    except (urllib.error.URLError, TimeoutError) as e:
        sys.exit(f'网络错误：{getattr(e, "reason", e)}')
    url = (data.get('output') or {}).get('audio', {}).get('url')
    if not url: sys.exit(f'网关没返回音频：{json.dumps(data, ensure_ascii=False)[:400].replace(k, "[key]")}')
    if url.startswith('http://'): url = 'https://' + url[len('http://'):]
    out.parent.mkdir(parents=True, exist_ok=True)
    mp3 = out if out.suffix.lower() == '.mp3' else out.with_suffix('.mp3')
    with urllib.request.urlopen(url, timeout=120) as r: mp3.write_bytes(r.read())
    if out.suffix.lower() == '.wav':
        subprocess.run([bin('ffmpeg'), '-v', 'error', '-y', '-i', str(mp3), '-ar', '48000', '-ac', '1', str(out)], check=True)
        mp3.unlink()
    meta = dict(provider='token_plan', model=payload['model'], voice=payload['input']['voice'],
                text=text, ai_generated=True, credit=f'AI 配音（{payload["model"]} / {payload["input"]["voice"]}）',
                usage=data.get('usage', {}))
    Path(str(out) + '.json').write_text(json.dumps(meta, ensure_ascii=False, indent=1), 'utf-8')
    print(f'已存 {out}\n  用前听一遍：台词/停顿/发音；按实际时长对齐镜头与字幕（不用估的时间线冒充）')


if __name__ == '__main__':
    main()
