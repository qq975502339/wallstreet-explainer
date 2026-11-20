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


def nb_frames(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=nb_frames', '-of', 'csv=p=0', str(p)], capture_output=True, text=True, check=True)
    return int(r.stdout.strip())


def test_conform_speed_keeps_one_frame_per_source_frame(tmp_path):
    src = tmp_path / 'src.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc=size=320x180:rate=24:duration=2', '-c:v', 'libx264', str(src)], check=True)
    assert nb_frames(src) == 48
    dst = tmp_path / 'speed.mp4'
    r = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'footage.py'), 'conform', str(src), str(dst), 'speed'], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert nb_frames(dst) == 48  # 每源帧恰好一帧，不补不丢
    dup = tmp_path / 'dup.mp4'
    r = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'footage.py'), 'conform', str(src), str(dup), 'dup'], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    assert nb_frames(dup) == 60  # 补帧 12
    again = subprocess.run([sys.executable, str(ROOT / 'scripts' / 'footage.py'), 'conform', str(src), str(dst), 'speed'], capture_output=True, text=True)
    assert again.returncode != 0  # 防覆盖


def test_detail_checks_flag_stutter_and_click(tmp_path):
    src = tmp_path / 'src.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'testsrc=size=320x180:rate=30:duration=2', '-c:v', 'libx264', str(src)], check=True)
    f0 = tmp_path / 'f0.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', str(src), '-c', 'copy', '-frames:v', '1', str(f0)], check=True)
    lst = tmp_path / 'list.txt'
    lst.write_text(f"file '{f0.as_posix()}'\nfile '{src.as_posix()}'\n", encoding='utf8')
    vid = tmp_path / 'stutter.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(lst), '-c', 'copy', str(vid)], check=True)
    out = vp.detail_checks(vid)
    assert any(x['status'] == 'fail' and '重复帧' in x['message'] for x in out), out
    # 咔哒：正弦波里插一个全幅突跳
    sr = 8000; t = np.arange(sr * 3) / sr
    x = (0.3 * np.sin(2 * np.pi * 440 * t))
    x[int(sr * 1.5)] = 0.95; x[int(sr * 1.5) + 1] = -0.95
    wavp = tmp_path / 'click.wav'
    with wave.open(str(wavp), 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr); w.writeframes((x * 32767).astype('<i2').tobytes())
    v2 = tmp_path / 'click.mp4'
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-f', 'lavfi', '-i', 'color=c=blue:s=320x180:r=30:d=3', '-i', str(wavp), '-c:v', 'libx264', '-c:a', 'aac', '-shortest', str(v2)], check=True)
    out2 = vp.detail_checks(v2)
    assert any('咔哒' in x['message'] and '1.5' in x['message'] for x in out2), out2
