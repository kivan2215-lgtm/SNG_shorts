from pathlib import Path
from scipy.io.wavfile import read
from scipy.signal import stft
import numpy as np,json,subprocess,re
oldvideo='/workspace/sng-publish/SNG_COMEDY_004_JET_RU_FINAL.mp4';newvideo='SNG_COMEDY_004_JET_RU_FINAL_V2.mp4'
def vhash(f):return subprocess.check_output(['ffmpeg','-v','error','-i',f,'-map','0:v:0','-c','copy','-f','hash','-']).decode().strip()
assert vhash(oldvideo)==vhash(newvideo)
ms=[read(p)[1].astype(float) for p in ['/workspace/jet_v2/rumix.wav','/workspace/jet_stress/corrected.wav','mix.wav']]
def shape(sig):
 f,t,s=stft(sig,48000,nperseg=768,noverlap=576)
 p=np.mean(abs(s)**2,axis=1);bands=np.array([p[(f>=lo)&(f<hi)].sum() for lo,hi in zip([180,400,800,1600,2500,4000],[400,800,1600,2500,4000,8000])])
 return 10*np.log10(bands/bands.sum()+1e-12)
ix=np.flatnonzero(abs(ms[1]-ms[0])>8)
scores=[]
for g in np.split(ix,np.flatnonzero(np.diff(ix)>4320)+1):
 if len(g)<100:continue
 a,b=g[0],g[-1]+1
 v=[shape(m[a:b]) for m in ms]
 scores.append([round(np.sqrt(np.mean((v[j]-v[0])**2)),2) for j in (1,2)])
assert len(scores)==7
p=Path('verification.json');info=json.loads(p.read_text());info.update(encoded_video_hash=vhash(newvideo),spectral_deviation_db_previous_and_new=scores,full_decode=True,auditory_review=False)
p.write_text(json.dumps(info,ensure_ascii=False,indent=2));print(scores)
