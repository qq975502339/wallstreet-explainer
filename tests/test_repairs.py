import json, subprocess, sys, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import types
ROOT = Path(__file__).resolve().parents[1]
class Checks(unittest.TestCase):
 def test_facts_empty_is_failure(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d); (p/'facts.md').write_text('# empty',encoding='utf8'); (p/'film.js').write_text('const x = {};',encoding='utf8')
   r=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'scripts/facts_check.py'),d],capture_output=True)
   self.assertNotEqual(r.returncode,0)
 def test_sync_host_null_and_no_match_fails(self):
  import numpy
  src=(ROOT/'vendor/bighead-collage/scripts/verify.py').read_text(encoding='utf8').rsplit('\nmain()',1)[0]
  ns={'__file__':str(ROOT/'vendor/bighead-collage/scripts/verify.py'),'__name__':'test'}; exec(compile(src,ns['__file__'],'exec'),ns)
  class Model:
   def __init__(self,*a,**kw): pass
   def transcribe(self,*a,**kw): return ([],None)
  with tempfile.TemporaryDirectory() as d, patch.dict(sys.modules, {'librosa':types.ModuleType('librosa'),'faster_whisper':types.SimpleNamespace(WhisperModel=Model)}), patch.object(ns['subprocess'],'run') as run:
   (Path(d)/'timeline.json').write_text(json.dumps({'beats':[{'wav':None,'start':0,'chars':[['甲',0]]}]}),encoding='utf8')
   ns['check_sync'](d,src='movie.mp4')
   self.assertTrue(ns['fails']); self.assertEqual(run.call_count,1)
 def test_sync_host_null_without_from_fails_gracefully(self):
  src=(ROOT/'vendor/bighead-collage/scripts/verify.py').read_text(encoding='utf8').rsplit('\nmain()',1)[0]
  ns={'__file__':str(ROOT/'vendor/bighead-collage/scripts/verify.py'),'__name__':'test'}; exec(compile(src,ns['__file__'],'exec'),ns)
  with tempfile.TemporaryDirectory() as d:
   (Path(d)/'timeline.json').write_text(json.dumps({'beats':[{'id':'b01','wav':None,'start':0,'chars':[['甲',0]]}]}),encoding='utf8')
   ns['check_sync'](d)   # 无 --from、无 voice_track：应报缺 wav 指路，而不是 TypeError
   self.assertTrue(any('缺 wav' in f for f in ns['fails']))
 def test_host_low_confidence_fails(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d); (p/'script.json').write_text(json.dumps({'lines':[{'id':'a','text':'甲乙丙丁'}]}),encoding='utf8'); (p/'asr.json').write_text(json.dumps([{'text':'甲','words':[['甲',0,.2,1]]}]),encoding='utf8')
   r=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'scripts/host_timeline.py'),'x',str(p/'script.json'),str(p/'out.json'),'--asr',str(p/'asr.json')],capture_output=True)
   self.assertNotEqual(r.returncode,0); self.assertFalse((p/'out.json').exists())
if __name__ == '__main__': unittest.main()
