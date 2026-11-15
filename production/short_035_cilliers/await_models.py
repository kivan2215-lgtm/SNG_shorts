from pathlib import Path
import time,json,subprocess
p=Path(__file__).parent;deadline=time.monotonic()+1200
while True:
 f=p/'frames/descent/index.json'
 if f.exists():
  d=json.loads(f.read_text())
  if d.get('processed') and all((p/'frames/descent'/f'{i:04d}.jpg').exists() for i in range(61)) and (p/'frames/house/0000.jpg').exists():break
 if time.monotonic()>deadline:raise RuntimeError('Model render did not finish; inspect descent.log')
 time.sleep(5)
print('Model cache complete',flush=True)
