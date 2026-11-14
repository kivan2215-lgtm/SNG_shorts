"""Render PBR mechanisms; interpolate rigid motion to 30fps, native 30fps people."""
from pathlib import Path
import subprocess,json,time,hashlib,shutil,numpy as np,os
P=Path(__file__).parent
BLENDER=os.environ.get('BLENDER','/workspace/tools/blender-4.3.2-linux-x64/blender')
kinds=['hero','question','dive','valve','flood','loss','sealed','depth','cable','dock','seal','drain','dry','open','transfer','rise','trips','saved','final']
hashes={n:hashlib.sha256((P/n).read_bytes()).hexdigest() for n in ['scene3d.py','human_model.py','render_style.py']}
manifest={'source_sha256':hashes,'kinds':kinds,'started':time.time(),'engine':'EEVEE_NEXT','render_resolution':[720,1280],'delivery_resolution':[1080,1920],'delivery_fps':30,'articulated_transfer_native_fps':30,'other_mechanics_native_fps':15}
(P/'render_manifest.json').write_text(json.dumps(manifest,indent=2))
for k in kinds:
 out=P/'frames'/k
 if (out/'index.json').exists() and json.loads((out/'index.json').read_text()).get('processed'):
  print('CACHED',k,flush=True);continue
 print('START',k,flush=True)
 with (P/'tests'/f'{k}_render.log').open('w') as log:
  r=subprocess.run([BLENDER,'-b','-t','4','--python',str(P/'scene3d.py'),'--',k,'render'],stdout=log,stderr=subprocess.STDOUT)
 if r.returncode or not (out/'index.json').exists():raise RuntimeError(k)
 meta=json.loads((out/'index.json').read_text());n=meta['count']
 if meta['render_fps']==15 and n>2:
  raw=P/'raw_frames'/k;raw.parent.mkdir(exist_ok=True)
  if raw.exists():shutil.rmtree(raw)
  out.rename(raw);out.mkdir();nn=2*n-1
  cmd=['ffmpeg','-v','error','-y','-threads','2','-framerate','15','-i',str(raw/'%04d.jpg'),'-vf','tpad=stop_mode=clone:stop_duration=0.4,minterpolate=fps=30:mi_mode=mci:mc_mode=aobmc:me_mode=bidir:vsbmc=1:scd=none','-frames:v',str(nn),'-q:v','2','-start_number','0',str(out/'%04d.jpg')]
  subprocess.run(cmd,check=True)
  assert len(list(out.glob('*.jpg')))==nn,(k,nn)
  old=meta['anchors'];anchors=[]
  for i in range(nn):
   j=i//2;jj=min(n-1,j+1);a=.5 if i%2 else 0
   anchors.append({name:((1-a)*np.array(old[j][name])+a*np.array(old[jj][name])).tolist() for name in old[j]})
  meta.update(count=nn,anchors=anchors,source_frames=n,motion_interpolation='ffmpeg MCI; graphics overlays rendered separately at 30fps')
 meta['processed']=True;(out/'index.json').write_text(json.dumps(meta))
 print('DONE',k,meta['count'],flush=True)
manifest['completed']=time.time();(P/'render_manifest.json').write_text(json.dumps(manifest,indent=2));print('ALL COMPLETE',flush=True)
