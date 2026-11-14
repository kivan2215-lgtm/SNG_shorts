from pathlib import Path
import subprocess,json,time,hashlib
P=Path(__file__).parent
for directory in ['tests','frames','models']:(P/directory).mkdir(parents=True,exist_ok=True)
kinds=['hero','question','dive','valve','flood','loss','sealed','depth','cable','dock','seal','drain','dry','open','transfer','rise','trips','saved','final']
codehash=hashlib.sha256((P/'scene3d.py').read_bytes()).hexdigest()
(P/'render_manifest.json').write_text(json.dumps({'source_sha256':codehash,'kinds':kinds,'started':time.time()},indent=2))
for k in kinds:
 print('START',k,flush=True)
 with (P/'tests'/f'{k}_render.log').open('w') as log:
  r=subprocess.run(['blender','-b','-t','4','--python',str(P/'scene3d.py'),'--',k,'render'],stdout=log,stderr=subprocess.STDOUT)
 if r.returncode or not (P/'frames'/k/'index.json').exists():raise RuntimeError(k)
 print('DONE',k,flush=True)
print('ALL COMPLETE',flush=True)
