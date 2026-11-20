#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""制作清单、镜头初稿、检查报告、章节与交付工具（A 层）。
不自动搜素材（见 fetch_footage.py）、不自动识别口型（只量音轨偏移与逐句偏差）、不自动验证事实。
所有时间以秒为单位；交片前仍按 references/review.md 逐镜逐声检查。
子命令：init / draft / audit / render-chapters / cover / share / aroll / marks
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

try:
    from local_bins import bin as tool
except ImportError:
    def tool(name): return name


def finding(status, message): return {'status': status, 'message': message}


# ---------- A3 接缝/弱口型覆盖门禁 ----------
def check_cuts(cuts, overlays, margin=.12):
    if not cuts: return [finding('review', '未提供接缝或弱口型标记，无法检查接缝覆盖。')]
    result = []
    for c in cuts:
        a = float(c.get('from', c.get('time', 0))); b = float(c.get('to', c.get('time', a)))
        if b < a: result.append(finding('fail', f'标记区间无效 {a}–{b}')); continue
        ok = any(o.get('coverage') == 'full' and float(o['from']) <= a - margin and float(o['to']) >= b + margin for o in overlays)
        result.append(finding('pass' if ok else 'fail', f'接缝/弱口型 {a:.2f}–{b:.2f}s ' + ('已标记全屏覆盖' if ok else '未标记足够的全屏覆盖（pip 不算）')))
    return result


# ---------- A4 数字与口播 ----------
NUM = re.compile(r'(?<![\d.])\d[\d,]*(?:\.\d+)?\s*(?:%|％|万亿|亿|万|千|美元|元)?')
CHINESE_NUMBER = re.compile(r'[零〇一二两三四五六七八九十百千万亿]+')
def numbers(text): return [re.sub(r'[\s,]', '', m.group()).replace('％', '%') for m in NUM.finditer(str(text))]
def check_numbers(rows):
    if not rows: return [finding('review', '未提供逐项上屏数字和对应口播，无法核对。')]
    out = []
    for i, r in enumerate(rows, 1):
        spoken = str(r.get('spoken', '')); screen = str(r.get('screen', '')); a = numbers(spoken); b = numbers(screen)
        if not spoken or not screen or not b: status = 'review'; msg = '缺口播、画面文字或可识别数字'
        elif all(x in a for x in b): status = 'pass'; msg = '数字字面一致，统计口径仍须人工核对'
        elif CHINESE_NUMBER.search(spoken): status = 'review'; msg = '中文读数或不同格式需人工核对'
        else: status = 'fail'; msg = '画面数字未在对应口播中找到'
        out.append(finding(status, f'数字 {i}：{msg}（口播：{spoken}；画面：{screen}）'))
    return out


# ---------- A4 素材单次使用/禁循环 ----------
def check_reuse(items):
    if not items: return [finding('review', '未提供素材使用区间，无法检查重复和循环。')]
    groups = {}; out = []
    for x in items:
        src = str(x.get('source', '')).strip()
        if x.get('loop'): out.append(finding('fail', f'{src or "未命名素材"} 标记为循环播放'))
        if not src: out.append(finding('review', '素材缺少来源标识')); continue
        if x.get('kind') == 'image':
            if src in groups: out.append(finding('fail', f'图片重复使用：{src}'))
            groups.setdefault(src, []).append((0, float('inf'))); continue
        try: a, b = float(x['start']), float(x['end'])
        except (KeyError, ValueError, TypeError): out.append(finding('review', f'{src} 缺少原片起止时间')); continue
        if a < 0 or b <= a: out.append(finding('fail', f'{src} 原片区间无效')); continue
        for start, end in groups.get(src, []):
            if max(a, start) < min(b, end) - 1e-9: out.append(finding('fail', f'{src} 原片区间重复：{start}–{end} 与 {a}–{b}'))
        groups.setdefault(src, []).append((a, b))
    return out or [finding('pass', '登记的素材区间没有重叠或循环；仍需人工核对素材身份与画面。')]


# ---------- A4/A5 章节 ----------
def check_chapters(chapters):
    if not chapters: return [finding('review', '未提供章节。')]
    out = []; seen = set(); spans = []
    for c in chapters:
        name = str(c.get('name', ''))
        if not re.fullmatch(r'[\w\-一-鿿]+', name) or name in seen: out.append(finding('fail', f'章节名称无效或重复：{name}'))
        seen.add(name)
        try: a, b = float(c['from']), float(c['to'])
        except (KeyError, ValueError, TypeError): out.append(finding('fail', f'{name} 缺少时间')); continue
        if a < 0 or b <= a: out.append(finding('fail', f'{name} 时间区间无效')); continue
        if any(max(a, x) < min(b, y) for x, y in spans): out.append(finding('fail', f'{name} 与其他章节重叠'))
        spans.append((a, b))
    return out or [finding('pass', '章节名称和时间区间有效。')]


# ---------- A6 分镜草稿（按 B 层 shot-grammar 12 句型 + 内容触发） ----------
def draft_shots(lines):
    out = []
    for i, line in enumerate(lines):
        text = str(line.get('text', '')); scene = 'statement'; kind = 'E'
        if i < 3: scene, kind = 'host', 'H'
        elif re.search(r'叫做|号称|被称作|史称|也叫|这叫|称为', text): scene, kind = 'statement', 'T'
        elif re.search(r'为什么|怎么|是否|？|\?', text): scene, kind = 'host', 'Q'
        elif re.search(r'因为|就会|导致|所以|然后', text) and len(re.findall(r'因为|就会|导致|所以|然后', text)) >= 2: scene, kind = 'chain', 'K'
        elif re.search(r'相比|对比|高于|低于|不是.*而是|而|但', text): scene, kind = 'compare', 'C'
        elif re.search(r'从.*到|翻倍|腰斩|涨到|跌到', text): scene, kind = 'change', 'N1'
        elif (NUM.search(text) or CHINESE_NUMBER.search(text)) and (len(text) <= 14 or re.search(r'涨到|跌到|翻倍|倍|%|相当于', text)): scene, kind = 'number', 'N1'
        elif len(NUM.findall(text)) >= 2 or re.search(r'走势|排名|几年|逐年', text): scene, kind = 'chart', 'N2'
        elif re.search(r'你看|比如|当时|有一次|例如', text): scene, kind = 'footage', 'S'
        elif re.search(r'所以说|其实|说白了|总之|我觉得', text): scene, kind = 'statement', 'E'
        elif re.search(r'第[一二三四五六七八九十\d]+[章条节]', text): scene, kind = 'agenda', 'CH'
        elif re.search(r'持股|投资|流向|供豆|管理费', text): scene, kind = 'network', '内容'
        elif re.search(r'步骤|产业链|循环|先.*再.*最后', text): scene, kind = 'flow', '内容'
        elif re.search(r'原文|条款|公报|逐字', text): scene, kind = 'docpage', '内容'
        elif re.search(r'拆解|分成|拆成', text): scene, kind = 'tree', '内容'
        elif re.search(r'如果你|测算|算一笔', text): scene, kind = 'calc', '内容'
        elif re.search(r'每\s*100|百个|百分之', text): scene, kind = 'grid', '内容'
        elif re.search(r'误区|以为|其实不是', text): scene, kind = 'bubble', '内容'
        elif re.search(r'产地|航线|运往|分布', text): scene, kind = 'map', '内容'
        out.append({'id': line.get('id'), 'spoken': text, 'scene': scene, 'kind': kind,
                    'needs_review': True, 'note': 'B 表句型/内容触发的候选；须人工核实语义、素材、时机与机位（shot-grammar.md）'})
    return out


# ---------- 媒体探针 ----------
def probe_media(path):
    r = subprocess.run([tool('ffprobe'), '-v', 'error', '-show_streams', '-show_format', '-of', 'json', str(path)], capture_output=True, text=True, check=True)
    return json.loads(r.stdout)


def inspect_file(path, require_audio=False, expected_frames=None, min_width=None, min_height=None):
    if not path.is_file(): return [finding('fail', f'文件不存在：{path}')]
    try:
        info = probe_media(path); streams = info.get('streams', []); v = next((x for x in streams if x.get('codec_type') == 'video'), None); audio = any(x.get('codec_type') == 'audio' for x in streams)
        if not v: return [finding('fail', f'无视频流：{path}')]
        is_image = path.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.tif', '.tiff')
        duration = float(info.get('format', {}).get('duration', 0) or 0)
        if duration <= 0 and not is_image: return [finding('fail', f'媒体时长无效：{path}')]
        fps = v.get('avg_frame_rate', '?'); frames = v.get('nb_frames')
        out = [finding('pass', f'{path.name}：{v.get("width")}×{v.get("height")}，' + ('静态图片' if is_image else f'帧率 {fps}，时长 {duration:.2f}s，音频：{"有" if audio else "无"}'))]
        if require_audio:
            cmd = [tool('ffmpeg'), '-v', 'error', '-i', str(path), '-map', '0:v:0']
            if audio: cmd.extend(['-map', '0:a:0'])
            cmd.extend(['-f', 'null', '-'])
            dec = subprocess.run(cmd, capture_output=True)
            out.append(finding('pass' if dec.returncode == 0 else 'fail', '成片音视频完整解码检查' + ('通过' if dec.returncode == 0 else '失败')))
        if min_width is not None and int(v.get('width', 0)) < int(min_width): out.append(finding('fail', f'{path.name} 宽度低于要求 {min_width}'))
        if min_height is not None and int(v.get('height', 0)) < int(min_height): out.append(finding('fail', f'{path.name} 高度低于要求 {min_height}'))
        if require_audio and not audio: out.append(finding('fail', '成片没有音轨'))
        if expected_frames is not None:
            if not frames or not str(frames).isdigit(): out.append(finding('review', '无法从文件读取帧数'))
            elif int(frames) != int(expected_frames): out.append(finding('fail', f'帧数 {frames} 与期望 {expected_frames} 不一致'))
            else: out.append(finding('pass', f'帧数符合期望：{frames}'))
        return out
    except (OSError, subprocess.CalledProcessError, ValueError, json.JSONDecodeError) as e:
        return [finding('fail', f'媒体检查失败：{path}：{e}')]


def measure_loudness(path, target=None, tolerance=1.0, peak_limit=None):
    if not path.is_file(): return [finding('review', '没有可测量的成片音频。')]
    try:
        r = subprocess.run([tool('ffmpeg'), '-hide_banner', '-nostats', '-i', str(path), '-filter_complex', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True, encoding='utf-8', errors='replace')
        if r.returncode: return [finding('review', '无法测量响度：可能没有音轨或 ffmpeg 不支持该滤镜。')]
        summary = r.stderr.rsplit('Summary:', 1)[-1]
        loud = re.search(r'\bI:\s*(-?\d+(?:\.\d+)?)\s*LUFS', summary)
        peak = re.search(r'\bPeak:\s*(-?\d+(?:\.\d+)?)\s*dBFS', summary)
        if not loud: return [finding('review', '未能解析响度；需人工检查。')]
        value = float(loud.group(1)); pv = float(peak.group(1)) if peak else None
        desc = f'综合响度 {value:.1f} LUFS' + (f'，真峰值 {pv:.1f} dBTP' if pv is not None else '，真峰值未读取')
        if target is None: return [finding('review', desc + '；未设置目标，需人工判断。')]
        ok = abs(value - float(target)) <= float(tolerance)
        if peak_limit is not None and pv is None: return [finding('review', desc + '；无法检查真峰值上限。')]
        if peak_limit is not None: ok = ok and pv <= float(peak_limit)
        return [finding('pass' if ok else 'fail', desc + f'；目标 {target} LUFS ± {tolerance}')]
    except (OSError, ValueError): return [finding('review', '响度测量失败，需人工检查。')]


# ---------- A7 流式单遍检查：冻帧/黑帧/静音 ----------
def stream_checks(path, freeze_sec=2.0, black_sec=0.5, silence_sec=3.0):
    if not path.is_file(): return [finding('review', '没有可检查的成片。')]
    try:
        has_audio = any(s.get('codec_type') == 'audio' for s in probe_media(path).get('streams', []))
        cmd = [tool('ffmpeg'), '-hide_banner', '-nostats', '-i', str(path),
               '-vf', f'freezedetect=n=-60dB:d={freeze_sec},blackdetect=d={black_sec}:pix_th=0.10']
        if has_audio: cmd += ['-af', f'silencedetect=n=-50dB:d={silence_sec}']
        cmd += ['-f', 'null', '-']
        r = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
        log = r.stderr
        out = []
        if not has_audio: out.append(finding('review', '成片没有音轨，静音检查跳过。'))
        freezes = re.findall(r'freeze_start:\s*([\d.]+)', log); blacks = re.findall(r'black_start:\s*([\d.]+)', log); sils = re.findall(r'silence_start:\s*([\d.]+)', log)
        out.append(finding('fail' if freezes else 'pass', f'冻帧（≥{freeze_sec}s 画面不动）：{len(freezes)} 处' + (f' @{freezes[:6]}' if freezes else '')))
        out.append(finding('fail' if blacks else 'pass', f'黑帧（≥{black_sec}s）：{len(blacks)} 处' + (f' @{blacks[:6]}' if blacks else '')))
        out.append(finding('review' if sils else 'pass', f'长静音（≥{silence_sec}s）：{len(sils)} 处' + (f' @{sils[:6]}；停顿是否有床/是否 intentional 须人听' if sils else '')))
        return out
    except (OSError, subprocess.CalledProcessError): return [finding('review', '流式检查不可用，需人工复核。')]


# ---------- C5 细痕：重复帧/掉帧/咔哒（A7 长阈值抓不到的一瞬坏） ----------
def detail_checks(path, dup_thr=0.5, drop_mult=8, click_thr=0.45):
    import numpy as np
    path = Path(path)
    if not path.is_file(): return [finding('review', '没有可检查的成片。')]
    out = []
    try:
        pr = probe_media(path); v = next(s for s in pr['streams'] if s.get('codec_type') == 'video')
        fa, fb = v['avg_frame_rate'].split('/'); fps = float(fa) / float(fb)
        r = subprocess.run([tool('ffmpeg'), '-nostdin', '-v', 'error', '-i', str(path), '-vf', 'scale=160:90,format=gray', '-f', 'rawvideo', '-'], capture_output=True, check=True)
        g = np.frombuffer(r.stdout, np.uint8); n = len(g) // (160 * 90)
        g = g[:n * 160 * 90].reshape(n, 90, 160).astype(np.float32)
        if n > 2:
            d = np.abs(g[1:] - g[:-1]).mean(axis=(1, 2))
            dups = [round((int(i) + 1) / fps, 2) for i in np.where(d < dup_thr)[0]]
            out.append(finding('fail' if dups else 'pass', f'重复帧（stutter，相邻帧差<{dup_thr}）：{len(dups)} 处' + (f' @{dups[:8]}' if dups else '')))
            med = float(np.median(d[d > 0])) if (d > 0).any() else 0.0
            drops = []
            if med > 0:
                for i in np.where(d > drop_mult * med)[0]:
                    if i + 1 < len(d) and d[i + 1] < 2 * med: drops.append(round((int(i) + 1) / fps, 2))
            out.append(finding('review' if drops else 'pass', f'疑似掉帧（单帧突跳后回落）：{len(drops)} 处' + (f' @{drops[:8]}；硬切也会突跳，须人复核区分' if drops else '')))
        else:
            out.append(finding('review', '帧数不足，未查重复/掉帧。'))
        has_a = any(s.get('codec_type') == 'audio' for s in pr['streams'])
        if has_a:
            ra = subprocess.run([tool('ffmpeg'), '-nostdin', '-v', 'error', '-i', str(path), '-map', '0:a:0', '-ac', '1', '-ar', '8000', '-f', 's16le', '-'], capture_output=True, check=True)
            x = np.frombuffer(ra.stdout, dtype='<i2').astype(np.float64) / 32768.0
            dx = np.abs(np.diff(x))
            clicks = [round(int(i) / 8000, 2) for i in np.where(dx > click_thr)[0]]
            out.append(finding('review' if clicks else 'pass', f'疑似咔哒（采样突跳>{click_thr}）：{len(clicks)} 处' + (f' @{clicks[:8]}；须人耳复核那几点' if clicks else '')))
        else:
            out.append(finding('review', '没有音轨，咔哒检查跳过。'))
        return out
    except (OSError, subprocess.CalledProcessError, ValueError, KeyError, StopIteration, json.JSONDecodeError) as e:
        return [finding('review', f'细痕检查不可用，需人工复核：{e}')]


# ---------- A3 音轨偏移（互相关，非口型） ----------
def check_audio_sync(video, reference, tolerance_ms=42, max_offset_seconds=2.0):
    """成片音轨 vs 按成片时间轴对齐的正式配音；不验证口型/画面。独立实现（思路参考 zenskill verify）。"""
    import math
    try:
        import numpy as np
    except ImportError:
        return {**finding('review', '缺少 numpy，未测量配音与成片的偏移。'), 'samples': []}
    video = Path(video); reference = Path(reference)
    if not video.is_file() or not reference.is_file():
        return {**finding('review', '成片或正式配音不存在，未测量同步。'), 'samples': []}
    try:
        tolerance_ms = float(tolerance_ms); max_offset_seconds = float(max_offset_seconds)
        if not (math.isfinite(tolerance_ms) and 0 <= tolerance_ms <= 5000 and math.isfinite(max_offset_seconds) and 0 < max_offset_seconds <= 5):
            raise ValueError('同步检查参数无效')
        vi = probe_media(video); rf = probe_media(reference)
        if not any(s.get('codec_type') == 'audio' for s in vi.get('streams', [])) or not any(s.get('codec_type') == 'audio' for s in rf.get('streams', [])):
            return {**finding('review', '成片或参考文件没有音轨，无法测量同步。'), 'samples': []}
        duration = min(float(vi['format']['duration']), float(rf['format']['duration']))
        if not math.isfinite(duration) or duration < 3:
            return {**finding('review', '可比对音频不足 3 秒，无法可靠判断同步。'), 'samples': []}
        length = min(6.0, duration); starts = sorted(set(round(max(0, min(duration - length, duration * q - length / 2)), 3) for q in (.1, .5, .9)))
        sr = 8000; samples = []; unavailable = []
        def read_window(path, start):
            r = subprocess.run([tool('ffmpeg'), '-nostdin', '-v', 'error', '-ss', str(start), '-t', str(length), '-i', str(path), '-map', '0:a:0', '-ac', '1', '-ar', str(sr), '-f', 's16le', '-'], capture_output=True, check=True)
            return np.frombuffer(r.stdout, dtype='<i2').astype(np.float64)
        for start in starts:
            a, b = read_window(video, start), read_window(reference, start); n = min(len(a), len(b))
            if n < sr or a[:n].std() < 30 or b[:n].std() < 30:
                unavailable.append(start); continue
            a = a[:n] - a[:n].mean(); b = b[:n] - b[:n].mean()
            size = 1 << (2 * n - 1).bit_length()
            corr = np.fft.irfft(np.fft.rfft(a, size) * np.conj(np.fft.rfft(b, size)), size)
            bound = min(int(max_offset_seconds * sr), n - 1); lags = np.arange(-bound, bound + 1)
            vals = np.abs(corr[lags % size]); k = int(np.argmax(vals)); lag = int(lags[k])
            aa = a[lag:] if lag >= 0 else a[:lag]; bb = b[:n - lag] if lag >= 0 else b[-lag:]
            denom = np.linalg.norm(aa) * np.linalg.norm(bb); confidence = float(vals[k] / denom) if denom else 0.0
            alternatives = vals[np.abs(lags - lag) > int(.02 * sr)]
            ambiguous = bool(len(alternatives) and np.max(alternatives) >= vals[k] * .97)
            if not math.isfinite(confidence) or confidence < .15 or ambiguous:
                unavailable.append(start); continue
            samples.append({'start_seconds': start, 'window_seconds': round(n / sr, 3), 'offset_ms': round(lag / sr * 1000, 1), 'correlation': round(confidence, 3)})
        if len(samples) < 2:
            return {**finding('review', f'可可靠比对的片段仅 {len(samples)} 个；静音、音乐遮盖或声音不匹配时需人工复核。'), 'samples': samples, 'unavailable_windows': unavailable}
        offsets = [s['offset_ms'] for s in samples]; ok = all(abs(x) <= tolerance_ms for x in offsets)
        details = ', '.join(f"{s['start_seconds']:.1f}s 起 {s['offset_ms']:+.1f}ms" for s in samples)
        msg = f'成片音轨相对参考配音：{details}（正数表示成片声音更晚；容差 ±{tolerance_ms:g} ms）；不验证人物口型或画面时间。'
        if unavailable: msg += f' {len(unavailable)} 个片段信号不足，需人工复核。'
        status = 'fail' if not ok else ('review' if unavailable else 'pass')
        return {**finding(status, msg), 'samples': samples, 'unavailable_windows': unavailable}
    except (OSError, KeyError, ValueError, TypeError, subprocess.CalledProcessError, json.JSONDecodeError) as e:
        return {**finding('review', f'同步测量不可用，需人工复核：{e}'), 'samples': []}


# ---------- A1 A-roll 体检 ----------
def gray_frames(path, n=3):
    import numpy as np
    r = subprocess.run([tool('ffmpeg'), '-nostdin', '-v', 'error', '-i', str(path), '-frames:v', str(n), '-vf', 'scale=480:270,format=gray', '-f', 'rawvideo', '-'], capture_output=True, check=True)
    a = np.frombuffer(r.stdout, np.uint8)
    return a.reshape(-1, 270, 480).astype(np.float32)


def gray_seq(path, fps_sample=6):
    import numpy as np
    r = subprocess.run([tool('ffmpeg'), '-nostdin', '-v', 'error', '-i', str(path), '-vf', f'fps={fps_sample},scale=480:270,format=gray', '-f', 'rawvideo', '-'], capture_output=True, check=True)
    a = np.frombuffer(r.stdout, np.uint8)
    n = len(a) // (480 * 270)
    return a[:n * 480 * 270].reshape(n, 270, 480).astype(np.float32)


def inspect_aroll(path, voice=None, fps=30, fix=None):
    """恒定帧率/首帧重复/配音vs帧数/硬切自动检测；--fix 出修正副本。"""
    import numpy as np
    path = Path(path)
    if not path.is_file(): return [finding('fail', f'文件不存在：{path}')], {}
    try:
        info = probe_media(path); v = next((x for x in info.get('streams', []) if x.get('codec_type') == 'video'), None)
        if not v: return [finding('fail', f'无视频流：{path}')], {}
        def frac(s):
            try:
                a, b = str(s).split('/'); return float(a) / float(b) if float(b) else 0.0
            except (ValueError, ZeroDivisionError): return 0.0
        avg, r = frac(v.get('avg_frame_rate')), frac(v.get('r_frame_rate'))
        frames = int(v.get('nb_frames') or 0); duration = float(info.get('format', {}).get('duration', 0) or 0)
        out = [finding('pass', f'{path.name}：{v.get("width")}×{v.get("height")}，{avg:.3f}fps，{frames} 帧，{duration:.2f}s')]
        meta = {'fps': avg, 'frames': frames, 'duration': duration, 'width': v.get('width'), 'height': v.get('height')}
        if abs(avg - r) > 0.01: out.append(finding('fail', f'可变帧率（avg {avg:.3f} ≠ r {r:.3f}）：时间轴会漂，请上游重出恒定帧率'))
        if abs(avg - fps) > 0.01: out.append(finding('fail', f'帧率 {avg:.3f} 与时间线 {fps} 不符：上游重出 {fps}fps，或 --fix 转换（会轻微顿挫）'))
        if abs(v.get('width', 0) / max(1, v.get('height', 1)) - 16 / 9) > 0.01: out.append(finding('review', '不是 16:9：铺满会裁边，确认构图'))
        if (v.get('height') or 0) < 1080: out.append(finding('review', f'只有 {v.get("height")}p：推近放大时会偏软'))
        g = gray_frames(path, 3)
        dup = len(g) >= 3 and np.abs(g[1] - g[0]).mean() < 0.05 and np.abs(g[2] - g[1]).mean() > 0.3
        meta['first_frame_dup'] = bool(dup)
        if dup: out.append(finding('fail', '首帧重复（帧0=帧1）：后续画面整体晚 1 帧；用 --fix 去掉'))
        if voice:
            vp = Path(voice)
            if not vp.is_file(): out.append(finding('fail', f'配音不存在：{vp}'))
            else:
                vd = float(probe_media(vp).get('format', {}).get('duration', 0) or 0)
                meta['voice_duration'] = vd
                expect = frames / fps if frames else duration
                if abs(vd - expect) > 1.0 / fps: out.append(finding('fail', f'配音 {vd:.3f}s 与画面 {expect:.3f}s 差超过 1 帧：口型会整体错'))
                else: out.append(finding('pass', f'配音与画面时长差 {abs(vd - expect) * 1000:.0f}ms（≤1 帧）'))
        seq = gray_seq(path, 6); cuts = []
        if len(seq) > 1:
            d = np.abs(seq[1:] - seq[:-1]).mean(axis=(1, 2))
            for i in np.where(d > 25)[0]:
                t = round((int(i) + 1) / 6.0, 2)
                if not cuts or t - cuts[-1] > 0.3: cuts.append(t)
        meta['hard_cuts'] = cuts[:200]
        out.append(finding('review' if cuts else 'pass', f'自动检测到 {len(cuts)} 个疑似硬切（6fps 灰度差>25）：{cuts[:12]}；须人工确认并登记覆盖'))
        if fix:
            fx = Path(fix)
            if fx.exists() or fx == path: out.append(finding('fail', f'--fix 输出已存在或与输入相同：{fx}'))
            else:
                vf = []
                if dup: vf.append("select='gt(n\\,0)',setpts=N/(%d*TB)" % fps)
                if abs(avg - fps) > 0.01: vf.append(f'fps={fps}')
                fx.parent.mkdir(parents=True, exist_ok=True)
                cmd = [tool('ffmpeg'), '-nostdin', '-v', 'error', '-y', '-i', str(path)]
                if vf: cmd += ['-vf', ','.join(vf)]
                cmd += ['-map', '0:v:0', '-c:v', 'libx264', '-crf', '18', '-pix_fmt', 'yuv420p', '-an', str(fx)]
                subprocess.run(cmd, check=True)
                out.append(finding('pass', f'已生成修正副本：{fx}（去首帧重复/转 {fps}fps）；用副本重新体检'))
        return out, meta
    except (OSError, subprocess.CalledProcessError, ValueError, json.JSONDecodeError) as e:
        return [finding('fail', f'A-roll 体检失败：{e}')], {}


def merge_marks(film):
    """aroll 硬切 + sync 逐句弱口型 → production.json cuts（不删人工、幂等）。"""
    film = Path(film)
    pp = film / 'production.json'
    data = read_json(pp) if pp.exists() else {'cuts': [], 'overlays': []}
    cuts = data.setdefault('cuts', [])
    added = []
    ar = film / 'build' / 'aroll.json'
    if ar.exists():
        for t in json.loads(ar.read_text(encoding='utf-8-sig')).get('hard_cuts', []):
            if not any(abs(float(c.get('from', c.get('time', -9))) - t) < .05 and abs(float(c.get('to', c.get('time', -9))) - t) < .05 for c in cuts):
                cuts.append({'from': t, 'to': t, 'origin': 'aroll-hard-cut'}); added.append(t)
    sb = film / 'build' / 'sync_beats.json'
    if sb.exists():
        for b in json.loads(sb.read_text(encoding='utf-8-sig')).get('beats', []):
            if b.get('median_ms') is None or abs(b['median_ms']) <= 70: continue
            a, z = float(b['start']), float(b['end'])
            if not any(abs(float(c.get('from', -9)) - a) < .05 and abs(float(c.get('to', -9)) - z) < .05 for c in cuts):
                cuts.append({'from': a, 'to': z, 'origin': 'weak-lip'}); added.append(f'{a}-{z}')
    write_json(pp, data)
    return added


# ---------- 报告 ----------
def make_report(data, root):
    checks = {}
    checks['接缝覆盖'] = check_cuts(data.get('cuts', []), data.get('overlays', []), float(data.get('cut_margin', .12)))
    checks['数字与口播'] = check_numbers(data.get('numbers', []))
    checks['素材重复'] = check_reuse(data.get('media_usage', []))
    checks['章节'] = check_chapters(data.get('chapters', []))
    media = data.get('media', [])
    checks['素材入库'] = sum((inspect_file(root / x['path'], min_width=x.get('min_width'), min_height=x.get('min_height')) for x in media), []) if media else [finding('review', '未登记待检查素材。')]
    for x in media:
        if not x.get('source') or not x.get('license'):
            checks['素材入库'].append(finding('fail', f'{x.get("path")} 缺少来源或许可登记（fetch_footage add/get 会写 credits.json；许可必须登记，缺=问题）'))
    final = data.get('final_video')
    checks['成片'] = inspect_file(root / final, True, data.get('expected_frames')) if final else [finding('review', '未指定成片，未检查播放、音轨与帧数。')]
    checks['音频响度'] = measure_loudness(root / final, data.get('loudness_target'), data.get('loudness_tolerance', 1.0), data.get('true_peak_limit')) if final else [finding('review', '未指定成片，未测量响度。')]
    checks['流式检查'] = stream_checks(root / final) if final else [finding('review', '未指定成片，未做冻帧/黑帧/静音检查。')]
    checks['细痕检查'] = detail_checks(root / final) if final else [finding('review', '未指定成片，未做重复帧/掉帧/咔哒检查。')]
    reference = data.get('sync_reference')
    checks['音画同步'] = [check_audio_sync(root / final, root / reference, data.get('sync_tolerance_ms', 42), data.get('sync_max_offset_seconds', 2.0))] if final and reference else [finding('review', '未同时提供成片和已对齐正式配音，未测量音频偏移。')]
    checks['人工审看'] = [finding('review', '字幕、口型、镜头、事实与版权许可仍须人工审看；音轨比对不能验证画面或口型同步。'), finding('review', '审片八问见 references/visual-checklist.md；节奏尺子见 shot-grammar.md。')]
    return {'checks': checks, 'summary': {s: sum(x['status'] == s for group in checks.values() for x in group) for s in ('pass', 'fail', 'review')}}


def write_json(path, data): path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
def read_json(path): return json.loads(path.read_text(encoding='utf-8-sig'))
def run_checked(cmd):
    print('执行：', ' '.join(str(x) for x in cmd), flush=True)
    subprocess.run([str(x) for x in cmd], check=True)


def main():
    p = argparse.ArgumentParser(description='制作清单、镜头初稿、检查报告、章节与交付工具（A 层）')
    sub = p.add_subparsers(dest='cmd', required=True)
    q = sub.add_parser('init'); q.add_argument('film')
    q = sub.add_parser('draft'); q.add_argument('film')
    q = sub.add_parser('audit'); q.add_argument('film'); q.add_argument('--manifest', default='production.json')
    q = sub.add_parser('render-chapters'); q.add_argument('film'); q.add_argument('--height', type=int, default=720)
    q = sub.add_parser('aroll'); q.add_argument('video'); q.add_argument('--voice'); q.add_argument('--fps', type=int, default=30); q.add_argument('--json'); q.add_argument('--fix')
    q = sub.add_parser('marks'); q.add_argument('film')
    q = sub.add_parser('cover'); q.add_argument('video'); q.add_argument('output'); q.add_argument('--at', type=float, default=0); q.add_argument('--portrait', action='store_true')
    q = sub.add_parser('share'); q.add_argument('video'); q.add_argument('output'); q.add_argument('--height', type=int, default=720); q.add_argument('--crf', type=int, default=24)
    args = p.parse_args()
    if args.cmd == 'init':
        film = Path(args.film).resolve(); film.mkdir(parents=True, exist_ok=True); out = film / 'production.json'
        if out.exists(): raise ValueError(f'文件已存在，不覆盖：{out}')
        write_json(out, {'cut_margin': .12, 'cuts': [], 'overlays': [], 'numbers': [], 'media_usage': [], 'media': [], 'chapters': [], 'final_video': None, 'sync_reference': None, 'sync_tolerance_ms': 42, 'sync_max_offset_seconds': 2.0, 'loudness_target': -14, 'loudness_tolerance': 1, 'true_peak_limit': -1.5})
        prog = film / 'PROGRESS.md'
        if not prog.exists(): prog.write_text('# 进度日志\n\n每完成一步追加一节（会话中断从这里续做，不重做已完成步骤）。\n\n## init\n- 已建 production.json\n', encoding='utf-8')
        print('已创建', out, '与 PROGRESS.md；请按 references/production-pipeline.md 填写清单。')
    elif args.cmd == 'draft':
        film = Path(args.film).resolve(); s = read_json(film / 'script.json'); out = film / 'draft_shots.json'
        if out.exists(): raise ValueError(f'文件已存在，不覆盖：{out}')
        write_json(out, {'shots': draft_shots(s.get('lines', []))}); print('已生成候选镜头（B 表句型/内容触发，全标 needs_review）：', out)
    elif args.cmd == 'audit':
        film = Path(args.film).resolve(); data = read_json(film / args.manifest); report = make_report(data, film); out = film / 'production-report.json'; write_json(out, report)
        md = ['# 制作检查报告', '', f"通过 {report['summary']['pass']} · 问题 {report['summary']['fail']} · 人工复核 {report['summary']['review']}", '']
        for title, rows in report['checks'].items():
            md.extend(['## ' + title, ''] + [f'- **{x["status"]}**：{x["message"]}' for x in rows] + [''])
        (film / 'production-report.md').write_text('\n'.join(md), encoding='utf-8'); print('\n'.join(md)); return 1 if report['summary']['fail'] else 0
    elif args.cmd == 'render-chapters':
        film = Path(args.film).resolve(); data = read_json(film / 'production.json'); chapters = data.get('chapters', []); issues = check_chapters(chapters)
        if not chapters or any(x['status'] == 'fail' for x in issues): raise ValueError('章节为空或无效，先检查 production.json')
        renderer = Path(__file__).resolve().parent / 'render.mjs'
        progress = film / 'out' / 'chapter-progress.json'; progress.parent.mkdir(parents=True, exist_ok=True)
        state = {'chapters': []}; write_json(progress, state)
        for c in chapters:
            dest = film / 'out' / 'chapters' / c['name']; dest.mkdir(parents=True, exist_ok=True)
            item = {'name': c['name'], 'from': c['from'], 'to': c['to'], 'status': 'rendering'}; state['chapters'].append(item); write_json(progress, state)
            try:
                run_checked(['node', renderer, '--dir', film, '--video', '--h', args.height, '--range', f"{c['from']}:{c['to']}", '--out', dest])
                video = dest / f'visual_{args.height}_range.mp4'
                if not video.is_file() or any(x['status'] == 'fail' for x in inspect_file(video)): raise ValueError(f'章节视频未通过检查：{video}')
                item.update(status='complete', file=str(video))
            except (ValueError, OSError, subprocess.CalledProcessError) as e:
                item.update(status='failed', error=str(e)); write_json(progress, state); raise
            write_json(progress, state)
    elif args.cmd == 'aroll':
        findings, meta = inspect_aroll(Path(args.video), args.voice, args.fps, args.fix)
        if args.json:
            jp = Path(args.json); jp.parent.mkdir(parents=True, exist_ok=True); write_json(jp, meta)
        for f in findings: print(f"**{f['status']}**：{f['message']}")
        return 1 if any(f['status'] == 'fail' for f in findings) else 0
    elif args.cmd == 'marks':
        added = merge_marks(Path(args.film)); print(f'自动标记 +{len(added)} 条进 production.json cuts：{added[:12]}'); return 0
    elif args.cmd in ('cover', 'share'):
        src = Path(args.video).resolve(); out = Path(args.output).resolve()
        if not src.is_file(): raise ValueError(f'输入文件不存在：{src}')
        if src == out or out.exists(): raise ValueError(f'输出文件已存在或与输入相同，不覆盖：{out}')
        out.parent.mkdir(parents=True, exist_ok=True)
        if args.cmd == 'cover':
            vf = 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920' if args.portrait else 'scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2'
            run_checked([tool('ffmpeg'), '-v', 'error', '-ss', args.at, '-i', src, '-frames:v', '1', '-vf', vf, '-n', out])
        else:
            if not 144 <= args.height <= 2160 or not 0 <= args.crf <= 51: raise ValueError('height 或 crf 超出范围')
            run_checked([tool('ffmpeg'), '-v', 'error', '-i', src, '-vf', f'scale=-2:{args.height}', '-c:v', 'libx264', '-crf', args.crf, '-c:a', 'aac', '-movflags', '+faststart', '-n', out])
        if not out.is_file() or out.stat().st_size == 0: raise ValueError(f'未生成有效输出：{out}')
        print('已生成：', out)
    return 0


if __name__ == '__main__':
    try: sys.exit(main())
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError, json.JSONDecodeError) as e:
        print(f'错误：{e}', file=sys.stderr); sys.exit(2)
