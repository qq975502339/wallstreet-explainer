"""Compare two same-sized scene screenshots: python scripts/scene_diff.py BASELINE CURRENT [--threshold 2]."""
import argparse, sys
from PIL import Image, ImageChops, ImageStat
p=argparse.ArgumentParser(description=__doc__); p.add_argument('baseline'); p.add_argument('current'); p.add_argument('--threshold',type=float,default=2.0); a=p.parse_args()
try:
 with Image.open(a.baseline) as x, Image.open(a.current) as y:
  x=x.convert('RGB'); y=y.convert('RGB')
  if x.size != y.size: raise ValueError(f'image dimensions differ: {x.size} vs {y.size}')
  delta=sum(ImageStat.Stat(ImageChops.difference(x,y)).mean)/3
  print(f'mean absolute RGB difference: {delta:.3f} (threshold {a.threshold}); inspect differences visually')
  sys.exit(1 if delta>a.threshold else 0)
except (OSError, ValueError) as e: print(f'FAIL: {e}',file=sys.stderr); sys.exit(2)
