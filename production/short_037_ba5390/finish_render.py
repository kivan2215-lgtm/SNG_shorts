from pathlib import Path
import time,json,subprocess,concurrent.futures
P=Path(__file__).parent
while True:
 ready=True
 for k,n in [('window',37),('bolts',61)]:
  f=P/'frames'/k/'index.json'
  if not f.exists() or not json.loads(f.read_text()).get('processed'):ready=False;break
  if any(not (f.parent/f'{i:04}.jpg').exists() for i in range(n)):ready=False;break
 if ready:break
 time.sleep(10)
print('Native model frame caches complete',flush=True)
def build(lang):
 with (P/lang/'build.log').open('w') as f:subprocess.run(['/workspace/SNG_shorts/.venv/bin/python',str(P/'build.py'),lang],stdout=f,stderr=subprocess.STDOUT,check=True)
 return lang
with concurrent.futures.ThreadPoolExecutor(max_workers=2) as e:print(list(e.map(build,['ru','en'])),flush=True)
with (P/'qc.log').open('w') as f:subprocess.run(['/workspace/SNG_shorts/.venv/bin/python',str(P/'qc.py')],stdout=f,stderr=subprocess.STDOUT,check=True)
print('Both renders and technical QC complete',flush=True)
