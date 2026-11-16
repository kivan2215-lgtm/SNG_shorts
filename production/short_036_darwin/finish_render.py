from pathlib import Path
import time,json,subprocess,concurrent.futures
P=Path(__file__).parent
last=0
while True:
 f=P/'frames/passage/index.json'
 if f.exists():
  d=json.loads(f.read_text())
  if d.get('processed') and all((P/'frames/passage'/f'{i:04d}.jpg').exists() for i in range(91)):break
 if time.time()-last>60:print('Waiting for native model frames:',len(list((P/'frames/passage').glob('patch_*.jpg'))),flush=True);last=time.time()
 time.sleep(5)
python='/workspace/SNG_shorts/.venv/bin/python'
def render(l):
 with (P/l/'build.log').open('w') as out:subprocess.run([python,str(P/'build.py'),l],stdout=out,stderr=subprocess.STDOUT,check=True)
 print('Rendered',l,flush=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(render,['ru','en']))
subprocess.run([python,str(P/'make_plan.py')],check=True)
with (P/'qc.log').open('w') as out:subprocess.run([python,str(P/'qc.py')],stdout=out,stderr=subprocess.STDOUT,check=True)
print('Both renders and technical QC complete',flush=True)
