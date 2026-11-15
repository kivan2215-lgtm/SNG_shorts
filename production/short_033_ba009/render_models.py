from pathlib import Path
import subprocess,sys,json,time
P=Path(__file__).parent;B='/workspace/tools/blender-4.3.2-linux-x64/blender'
for k in ['deposit','clear','glide']:
 print('START',k,flush=True)
 with (P/'tests'/f'{k}.log').open('w') as f:r=subprocess.run([B,'-b','-t','4','--python-exit-code','1','--python',str(P/'scene3d.py'),'--',k,'render'],stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError(k)
 print('DONE',k,flush=True)
print('MODELS COMPLETE',flush=True)
