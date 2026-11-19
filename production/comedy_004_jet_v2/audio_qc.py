from pathlib import Path
from scipy.io.wavfile import read
import numpy as np,json,subprocess,re
from pacing import tighten
stats=[]
for f in sorted(Path('.').glob('ru?.wav')):
 sr,a=read(f);a=a.astype('f')/32768
 cleaned,_=tighten(a,[],sr)
 stats.append(dict(block=f.stem,raw_s=round(len(a)/sr,3),retained_s=round(len(cleaned)/sr,3),clipped_samples=int((abs(a)>=.9999).sum())))
for l in ['RU','EN']:
 f=f'SNG_COMEDY_004_JET_{l}_V2.mp4'
 log=subprocess.run(['ffmpeg','-hide_banner','-nostats','-i',f,'-af','loudnorm=I=-16:TP=-1.5:LRA=10:print_format=json','-vn','-f','null','-'],capture_output=True,text=True,check=True).stderr
 d=json.loads(log[log.rfind('{'):log.rfind('}')+1])
 assert float(d['input_tp'])<0 and -21<float(d['input_i'])<-12
 stats.append(dict(version=l,LUFS=d['input_i'],true_peak_dBTP=d['input_tp']))
Path('audio-check.json').write_text(json.dumps(stats,indent=2))
