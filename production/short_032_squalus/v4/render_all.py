"""Render ray-traced mechanisms at native 30 fps; reuse only unchanged states."""
from pathlib import Path
import subprocess,json,time,hashlib,shutil,numpy as np,os
P=Path(__file__).parent
(P/'tests').mkdir(exist_ok=True)
try:previous=json.loads((P/'render_manifest.json').read_text())
except (OSError,ValueError):previous={}
BLENDER=os.environ.get('BLENDER','/workspace/tools/blender-4.3.2-linux-x64/blender')
kinds=['hero','question','dive','valve','flood','loss','sealed','depth','cable','dock','seal','drain','dry','open','transfer','rise','trips','saved','final']
hashes={n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ['scene3d.py','human_model.py','render_style.py','region_cache.py']}
manifest={'source_sha256':hashes,'kinds':kinds,'started':time.time(),'engine':'CYCLES','render_resolution':[720,1280],'delivery_resolution':[1080,1920],'delivery_fps':30,'articulated_transfer_native_fps':30,'other_mechanics_native_fps':30}
(P/'render_manifest.json').write_text(json.dumps(manifest,indent=2))
for k in kinds:
 out=P/'frames'/k
 if previous.get('final_source_sha256',previous.get('source_sha256'))==hashes and (out/'index.json').exists() and json.loads((out/'index.json').read_text()).get('processed'):
  print('CACHED',k,flush=True);continue
 print('START',k,flush=True)
 with (P/'tests'/f'{k}_render.log').open('w') as log:
  r=subprocess.run([BLENDER,'-b','-t','4','--python-exit-code','1','--python',str(P/'scene3d.py'),'--',k,'render'],stdout=log,stderr=subprocess.STDOUT)
 if r.returncode or not (out/'index.json').exists():raise RuntimeError(k)
 meta=json.loads((out/'index.json').read_text());n=meta['count']
 if not meta.get('processed') or any(not (out/f'{i:04d}.jpg').exists() for i in range(n)):raise RuntimeError(f'{k}: incomplete frame sequence')
 meta['processed']=True;(out/'index.json').write_text(json.dumps(meta))
 print('DONE',k,meta['count'],flush=True)
manifest['completed']=time.time();(P/'render_manifest.json').write_text(json.dumps(manifest,indent=2));print('ALL COMPLETE',flush=True)
