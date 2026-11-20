import importlib.util
import json
import os
import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

ROOT = Path(__file__).parents[1]
spec = importlib.util.spec_from_file_location('video_pipeline', ROOT / 'scripts' / 'video_pipeline.py')
vp = importlib.util.module_from_spec(spec); spec.loader.exec_module(vp)


def test_cut_requires_full_cover_not_pip():
    findings = vp.check_cuts([{'time': 3}], [{'from': 2.9, 'to': 3.1, 'coverage': 'full'}], .2)
    assert any(x['status'] == 'fail' for x in findings)
    assert vp.check_cuts([{'time': 3}], [{'from': 2.7, 'to': 3.3, 'coverage': 'full'}], .2)[0]['status'] == 'pass'
    assert vp.check_cuts([{'time': 3}], [{'from': 2, 'to': 4, 'coverage': 'pip'}], .2)[0]['status'] == 'fail'


def test_numbers_and_missing_inputs_are_not_silent_pass():
    assert vp.check_numbers([])[0]['status'] == 'review'
    assert vp.check_numbers([{'spoken': '跌了12%', 'screen': '跌了1.2%'}])[0]['status'] == 'fail'
    assert vp.check_numbers([{'spoken': '跌了12%', 'screen': '12%'}])[0]['status'] == 'pass'
    assert vp.check_numbers([{'spoken': '跌了百分之十二', 'screen': '12%'}])[0]['status'] == 'review'


def test_duplicate_source_ranges_and_loop():
    items = [{'source': 'a', 'start': 0, 'end': 2}, {'source': 'a', 'start': 1.9, 'end': 3}, {'source': 'b', 'start': 0, 'end': 2, 'loop': True}]
    failures = vp.check_reuse(items)
    assert len([x for x in failures if x['status'] == 'fail']) == 2
    assert vp.check_reuse([{'source': 'a', 'start': 0, 'end': 1}, {'source': 'a', 'start': 1, 'end': 2}])[0]['status'] == 'pass'
    assert vp.check_reuse([{'source': 'a'}])[0]['status'] == 'review'


def test_chapters_reject_unsafe_and_overlap():
    assert any(x['status'] == 'fail' for x in vp.check_chapters([{'name': '../x', 'from': 0, 'to': 2}]))
    assert any(x['status'] == 'fail' for x in vp.check_chapters([{'name': 'a', 'from': 0, 'to': 3}, {'name': 'b', 'from': 2, 'to': 4}]))


def test_draft_uses_B_table_kinds():
    rows = vp.draft_shots([{'id': 'h1', 'text': '开场第一句。'}, {'id': 'h2', 'text': '开场第二句。'}, {'id': 'h3', 'text': '开场第三句。'},
                           {'id': 'b1', 'text': '为什么黄金跌了？'}, {'id': 'b2', 'text': '因为利率升高，所以资金流出，导致金价下跌。'},
                           {'id': 'b3', 'text': '这叫"荷兰病"。'}, {'id': 'b4', 'text': '四家一年砸七千多亿。'}])
    assert rows[0]['kind'] == 'H'  # 前 3 句归开场钩子（规则本意）
    assert rows[3]['scene'] == 'host' and rows[3]['kind'] == 'Q'
    assert rows[4]['scene'] == 'chain'
    assert rows[5]['scene'] == 'statement' and rows[5]['kind'] == 'T'
    assert rows[6]['scene'] == 'number'
    assert all(x['needs_review'] for x in rows)


def test_end_to_end_report_and_delivery(tmp_path):
    cli = ROOT / 'scripts' / 'video_pipeline.py'
    env = {**os.environ, 'PYTHONIOENCODING': 'utf-8'}
    film = tmp_path / 'film'; film.mkdir()
    video = film / 'sample.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'testsrc=size=320x180:r=10:d=1', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=1', '-c:v', 'libx264', '-c:a', 'aac', '-shortest', str(video)], check=True)
    manifest = {'final_video': 'sample.mp4', 'expected_frames': 10, 'media': [{'path': 'sample.mp4', 'source': 'generated', 'license': 'test'}]}
    (film / 'production.json').write_text(json.dumps(manifest), encoding='utf8')
    audit = subprocess.run([sys.executable, str(cli), 'audit', str(film)], capture_output=True, text=True, encoding='utf8', env=env)
    assert audit.returncode == 0, audit.stderr
    report = json.loads((film / 'production-report.json').read_text(encoding='utf8'))
    assert report['summary']['review'] > 0 and report['summary']['fail'] == 0
    assert any('10' in x['message'] for x in report['checks']['成片'])
    assert any('完整解码检查通过' in x['message'] for x in report['checks']['成片'])
    assert any('LUFS' in x['message'] for x in report['checks']['音频响度'])
    assert '流式检查' in report['checks']
    for cmd, out in [('cover', film / 'cover.png'), ('share', film / 'share.mp4')]:
        result = subprocess.run([sys.executable, str(cli), cmd, str(video), str(out)], capture_output=True, text=True, encoding='utf8', env=env)
        assert result.returncode == 0, result.stderr
        assert out.stat().st_size > 0
        retry = subprocess.run([sys.executable, str(cli), cmd, str(video), str(out)], capture_output=True, text=True, encoding='utf8', env=env)
        assert retry.returncode != 0


def test_audio_sync_detects_delays_and_insufficient_evidence(tmp_path):
    rng = np.random.default_rng(42); sr = 8000
    samples = (rng.normal(0, 3500, sr * 12)).clip(-32768, 32767).astype('<i2')
    reference = tmp_path / 'voice.wav'
    with wave.open(str(reference), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(samples.tobytes())
    videos = []
    for name, delay in [('aligned', 0), ('late', 250)]:
        video = tmp_path / (name + '.mp4')
        subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=s=320x180:r=10:d=12', '-i', str(reference), '-af', f'adelay={delay}|{delay}', '-t', '12', '-c:v', 'libx264', '-c:a', 'aac', str(video)], check=True)
        videos.append(video)
    aligned = vp.check_audio_sync(videos[0], reference)
    late = vp.check_audio_sync(videos[1], reference)
    assert aligned['status'] == 'pass', aligned
    assert late['status'] == 'fail', late
    assert all(abs(x['offset_ms'] - 250) < 20 for x in late['samples']), late
    report = vp.make_report({'final_video': 'late.mp4', 'sync_reference': 'voice.wav', 'sync_tolerance_ms': 42}, tmp_path)
    assert report['checks']['音画同步'][0]['status'] == 'fail'
    assert report['summary']['fail'] >= 1
    silence = tmp_path / 'silence.wav'
    with wave.open(str(silence), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(bytes(sr * 12 * 2))
    assert vp.check_audio_sync(videos[0], silence)['status'] == 'review'
    assert vp.check_audio_sync(videos[0], tmp_path / 'missing.wav')['status'] == 'review'
    unrelated = tmp_path / 'unrelated.wav'
    with wave.open(str(unrelated), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes(rng.normal(0, 3500, sr * 12).clip(-32768, 32767).astype('<i2').tobytes())
    assert vp.check_audio_sync(videos[0], unrelated)['status'] == 'review'
    early = tmp_path / 'early.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=s=320x180:r=10:d=12', '-i', str(reference), '-af', 'atrim=start=0.25,asetpts=PTS-STARTPTS,apad', '-t', '12', '-c:v', 'libx264', '-c:a', 'aac', str(early)], check=True)
    measured = vp.check_audio_sync(early, reference)
    assert measured['status'] == 'fail', measured
    assert all(abs(x['offset_ms'] + 250) < 20 for x in measured['samples']), measured


def test_periodic_audio_is_not_trusted(tmp_path):
    tone = tmp_path / 'tone.wav'
    subprocess.run(['ffmpeg', '-v', 'error', '-f', 'lavfi', '-i', 'sine=frequency=400:duration=12', '-ar', '8000', str(tone)], check=True)
    assert vp.check_audio_sync(tone, tone)['status'] == 'review'


def test_report_without_reference_does_not_claim_sync(tmp_path):
    report = vp.make_report({}, tmp_path)
    assert report['checks']['音画同步'][0]['status'] == 'review'


def test_stream_checks_flag_black_and_freeze(tmp_path):
    v = tmp_path / 'black.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=black:s=320x180:r=10:d=3', '-c:v', 'libx264', str(v)], check=True)
    out = vp.stream_checks(v)
    assert any(x['status'] == 'fail' and '黑帧' in x['message'] for x in out)
    assert any(x['status'] == 'fail' and '冻帧' in x['message'] for x in out)
