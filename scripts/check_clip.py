"""Validate a generated video clip: python scripts/check_clip.py FILE [--width N --height N --duration SECONDS --tolerance 0.15]."""
import argparse, json, subprocess, sys
from local_bins import bin
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('file'); p.add_argument('--width',type=int); p.add_argument('--height',type=int); p.add_argument('--duration',type=float); p.add_argument('--tolerance',type=float,default=.15)
a=p.parse_args()
try:
 r=subprocess.run([bin('ffprobe'),'-v','error','-show_streams','-show_format','-of','json',a.file],capture_output=True,text=True,check=True)
 data=json.loads(r.stdout); v=next(s for s in data['streams'] if s['codec_type']=='video'); dur=float(data['format']['duration'])
 if a.width and v['width'] != a.width: raise ValueError(f"width {v['width']} != {a.width}")
 if a.height and v['height'] != a.height: raise ValueError(f"height {v['height']} != {a.height}")
 if a.duration is not None and abs(dur-a.duration)>a.tolerance: raise ValueError(f'duration {dur:.2f} != {a.duration:.2f}')
 subprocess.run([bin('ffmpeg'),'-v','error','-i',a.file,'-map','0:v:0','-f','null','-'],check=True)
 print(f"OK: {v['width']}x{v['height']}, {dur:.2f}s; content and lip sync require review")
except (subprocess.CalledProcessError, OSError, KeyError, StopIteration, ValueError, json.JSONDecodeError) as e:
 print(f'FAIL: {e}',file=sys.stderr); sys.exit(1)
