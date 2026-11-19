# -*- coding: utf-8 -*-
"""whisper 模型三级 fallback：WHISPER_DIR 本地目录 → HF 缓存快照（离线可用）→ 名字交给 faster-whisper 在线下载。
默认 small（上游有的地方写死 large-v3=3GB，本机缓存只有 small 完整）。国内在线下载设 HF_ENDPOINT=https://hf-mirror.com。"""
import os


def resolve():
    mdl = os.environ.get('WHISPER_DIR') or os.environ.get('WHISPER_MODEL') or 'small'
    if os.path.isdir(mdl):
        return mdl
    hub = os.path.join(os.environ.get('HF_HOME', os.path.join(os.path.expanduser('~'), '.cache', 'huggingface')), 'hub')
    snap = os.path.join(hub, f'models--Systran--faster-whisper-{mdl}', 'snapshots')
    if os.path.isdir(snap):
        cand = [os.path.join(snap, s) for s in os.listdir(snap) if os.path.exists(os.path.join(snap, s, 'model.bin'))]
        if cand:
            return cand[0]
    return mdl
