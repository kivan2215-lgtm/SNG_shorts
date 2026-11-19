"""Use the earlier clear take of the approximate amount; exact cents stay on screen."""
from pathlib import Path
from scipy.io.wavfile import read,write
from scipy.signal import resample_poly
from math import gcd
import numpy as np,json
def fix(blocks):
 b=blocks[3];prev=Path('/workspace/jet')
 if 'хвостиком.' in b['script']:return blocks
 old=json.loads((prev/'ru.json').read_text())[3]
 src=Path('ru3.wav');sr,x=read(src);so,y=read(prev/'ru3.wav')
 if sr!=so:y=resample_poly(y.astype('float64'),sr//gcd(sr,so),so//gcd(sr,so))
 l,r=old['times'][10],old['times'][15]
 a,c=b['times'][29],b['times'][35];seg=y[round(l*sr):round(r*sr)].astype(float)
 xx=x.astype(float);left=xx[:round(a*sr)].copy();right=xx[round(c*sr):].copy()
 fade=np.linspace(0,1,round(.009*sr)); left[-len(fade):]*=fade[::-1];seg[:len(fade)]*=fade;seg[-len(fade):]*=fade[::-1];right[:len(fade)]*=fade
 out=np.concatenate([left,seg,right]);write(src,sr,np.int16(np.clip(out,-32767,32767)))
 b['script']=b['script'][:29]+['семьсот','тысяч','долларов','с','хвостиком.']+b['script'][35:]
 b['times']=b['times'][:29]+[a+t-l for t in old['times'][10:15]]+[t+(r-l)-(c-a) for t in b['times'][35:]]
 b['duration']=len(out)/sr
 f=Path('ru.txt');f.write_text(f.read_text().replace('семьсот тысяч восемь долларов пятьдесят центов','семьсот тысяч долларов с хвостиком'))
 Path('ru.json').write_text(json.dumps(blocks,ensure_ascii=False));return blocks
