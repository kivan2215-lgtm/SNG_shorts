from pathlib import Path
import subprocess,os,json,concurrent.futures,time
P=Path(__file__).parent;PY='/workspace/SNG_shorts/.venv/bin/python'
while not (P/'frames/orbit/index.json').exists():time.sleep(5)
subprocess.run([PY,str(P/'preflight.py')],check=True)
def run(l):
 with (P/l/'pipeline.log').open('w') as log:subprocess.run([PY,str(P/'build.py'),l],env=dict(os.environ,RENDER_FINAL='1'),stdout=log,stderr=subprocess.STDOUT,check=True)
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:list(ex.map(run,['ru','en']))
with (P/'qc.log').open('w') as log:subprocess.run([PY,str(P/'qc.py')],stdout=log,stderr=subprocess.STDOUT,check=True)
print('Both previews and technical QA complete',flush=True)
