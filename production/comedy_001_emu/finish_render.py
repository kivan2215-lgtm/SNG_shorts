from pathlib import Path
import subprocess,time,os,json,concurrent.futures
P=Path(__file__).parent;PY='/workspace/SNG_shorts/.venv/bin/python'
while True:
 ready=all(all((P/'frames'/k/f'{i:04}.jpg').exists() for i in range(n)) for k,n in [('scatter',49),('truck',61)])
 if ready:
  meta=json.loads((P/'frames/truck/index.json').read_text())
  if meta.get('processed'):break
 time.sleep(5)
# A final preflight after models and graphics are complete.
subprocess.run([PY,str(P/'preflight.py')],check=True)
def run(lang):
 with (P/lang/'pipeline.log').open('w') as log:
  subprocess.run([PY,str(P/'build.py'),lang],env=dict(os.environ,RENDER_FINAL='1'),stdout=log,stderr=subprocess.STDOUT,check=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,['ru','en']))
with (P/'qc.log').open('w') as log:subprocess.run([PY,str(P/'qc.py')],stdout=log,stderr=subprocess.STDOUT,check=True)
print('Both full previews rendered and technical QC complete',flush=True)
