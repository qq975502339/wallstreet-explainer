import importlib.util
import json
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location('video_pipeline', ROOT / 'scripts' / 'video_pipeline.py')
vp = importlib.util.module_from_spec(spec); spec.loader.exec_module(vp)
fspec = importlib.util.spec_from_file_location('fetch_footage', ROOT / 'scripts' / 'fetch_footage.py')
ff = importlib.util.module_from_spec(fspec); fspec.loader.exec_module(ff)


def make_video(path, parts, fps=30):
    ins, filt = [], []
    for i, (color, dur) in enumerate(parts):
        ins += ['-f', 'lavfi', '-i', f'color=c={color}:s=320x180:r={fps}:d={dur}']
        filt.append(f'[{i}:v]')
    subprocess.run(['ffmpeg', '-v', 'error', '-y', *ins, '-filter_complex',
                    ''.join(filt) + f'concat=n={len(parts)}:v=1:a=0', '-c:v', 'libx264', str(path)], check=True)


def test_aroll_detects_first_frame_dup_and_hard_cut(tmp_path):
    # 真实 concat demuxer 的 dup = 同一编码包复制两次（比特级相同 diff=0）；
    # 用 -c copy 抽首包 + concat demuxer 流复制构造；重编码的"近似重复"(diff≈0.5)不该被判 dup，阈值 0.05 保守正确。
    src = tmp_path / 'src.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc=size=320x180:rate=30:duration=2', '-c:v', 'libx264', str(src)], check=True)
    f0 = tmp_path / 'f0.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-c', 'copy', '-frames:v', '1', str(f0)], check=True)
    lst = tmp_path / 'list.txt'
    lst.write_text(f"file '{f0.as_posix()}'\nfile '{src.as_posix()}'\n", encoding='utf8')
    dup = tmp_path / 'dup.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-c', 'copy', str(dup)], check=True)
    findings, meta = vp.inspect_aroll(dup, fps=30)
    assert meta['first_frame_dup'] is True
    assert any(x['status'] == 'fail' and '首帧重复' in x['message'] for x in findings)
    cutvid = tmp_path / 'cut.mp4'; make_video(cutvid, [('red', 1), ('blue', 1)])
    f2, m2 = vp.inspect_aroll(cutvid, fps=30)
    assert m2['first_frame_dup'] is False
    assert any(abs(t - 1.03) < .25 for t in m2['hard_cuts']), m2['hard_cuts']
    fixed = tmp_path / 'fixed.mp4'
    vp.inspect_aroll(dup, fps=30, fix=fixed)
    assert fixed.is_file()
    f3, m3 = vp.inspect_aroll(fixed, fps=30)
    assert m3['first_frame_dup'] is False


def test_aroll_voice_length_mismatch_fails(tmp_path):
    v = tmp_path / 'v.mp4'; make_video(v, [('red', 2)])
    w = tmp_path / 'voice.wav'
    with wave.open(str(w), 'wb') as h:
        h.setnchannels(1); h.setsampwidth(2); h.setframerate(8000); h.writeframes(bytes(8000 * 3 * 2))
    findings, meta = vp.inspect_aroll(v, voice=w, fps=30)
    assert any(x['status'] == 'fail' and '差超过 1 帧' in x['message'] for x in findings)


def test_marks_merge_dedupes_and_keeps_manual(tmp_path):
    film = tmp_path / 'film'; (film / 'build').mkdir(parents=True)
    (film / 'production.json').write_text(json.dumps({'cuts': [{'from': 5, 'to': 5}], 'overlays': []}), encoding='utf8')
    (film / 'build' / 'aroll.json').write_text(json.dumps({'hard_cuts': [1.0, 5.0]}), encoding='utf8')
    (film / 'build' / 'sync_beats.json').write_text(json.dumps({'beats': [
        {'id': 'b1', 'start': 8, 'end': 9, 'median_ms': 120}, {'id': 'b2', 'start': 9, 'end': 10, 'median_ms': 10}]}), encoding='utf8')
    added = vp.merge_marks(film)
    cuts = json.loads((film / 'production.json').read_text(encoding='utf8'))['cuts']
    assert len(cuts) == 3 and len(added) == 2
    assert any(c.get('origin') == 'weak-lip' and c['from'] == 8 for c in cuts)
    assert vp.merge_marks(film) == []  # 幂等


def test_missing_license_is_fail_not_review(tmp_path):
    report = vp.make_report({'media': [{'path': 'x.mp4'}]}, tmp_path)
    assert any(x['status'] == 'fail' and '许可' in x['message'] for x in report['checks']['素材入库'])


def test_fetch_license_gate():
    assert ff.lic_ok('CC BY-SA 4.0') and ff.lic_ok('Pexels License') and ff.lic_ok('CC0')
    assert not ff.lic_ok('CC BY-NC 4.0') and not ff.lic_ok('CC BY-ND 4.0') and not ff.lic_ok('Editorial use only')
