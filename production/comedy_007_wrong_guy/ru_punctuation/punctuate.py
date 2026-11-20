from pathlib import Path
import re,json
import numpy as np
from scipy.io import wavfile
import parselmouth as pm
from parselmouth.praat import call
from scipy.ndimage import uniform_filter1d
source=Path('..')
anchors=json.loads(Path('anchors.json').read_text())
blocks=[]; report=[]
def contour(x,sr,center,amount):
 lo=max(0,int((center-.28)*sr));hi=min(len(x),int((center+.28)*sr))
 part=x[lo:hi];snd=pm.Sound(part,sr);man=call(snd,'To Manipulation',.01,60,420)
 tier=call(man,'Extract pitch tier');points=call(tier,'Get number of points')
 if not points:return
 orig=[(call(tier,'Get time from index',i+1),call(tier,'Get value at index',i+1)) for i in range(points)]
 call(tier,'Remove points between',0,snd.duration)
 for time,p in orig:
  dt=time+lo/sr-center
  call(tier,'Add point',time,p*2**(amount*np.exp(-.5*(dt/.072)**2)/12))
 call([tier,man],'Replace pitch tier')
 y=call(man,'Get resynthesis (overlap-add)').values[0];n=min(len(y),len(part))
 blend=np.clip((.23-np.abs(np.arange(n)/sr+lo/sr-center))/.075,0,1)
 x[lo:lo+n]=part[:n]*(1-blend)+y[:n]*blend
for i,(text,row) in enumerate(zip(Path('ru.txt').read_text().strip().split('\n\n'),anchors)):
 words=text.split();sr,raw=wavfile.read(source/f'ru{i}.wav');x=raw.astype(float)/32768;assert len(words)==len(row)
 # Modelled pitch accents are centred on the stressed vowel inside the word.
 accents={'интернете':(6,1.65),'гай':(1,2.5),'да':(1,-1.65),'фамилия':(3,1.8),'нахуя':(4,1.3),'проверяли':(6,2.15),'рекомендации':(8,1.9),'телевизор':(5,-1.6)}
 for j,(w,a) in enumerate(zip(words,row)):
  w0=re.sub('[^а-яё]','',w.lower())
  if w0 in accents and (('?' in w) or (w0=='да' and (i in (1,4))) or (w0=='телевизор' and i==4)):
   idx,amount=accents[w0];contour(x,sr,a['letters'][idx],amount)
 env=np.sqrt(np.maximum(0,uniform_filter1d(x*x,int(.009*sr))))
 edits=[]
 for j,(w,a) in enumerate(zip(words,row)):
  if a is None or j==len(words)-1:continue
  n=next(h for h in row[j+1:] if h is not None)
  tail=w.strip('«»”"');ch=tail[-1]
  if ch not in '.,?!:':continue
  if words[j+1].lower().startswith('блядь'):continue
  gap={'?':.28,'!':.205,'.':.215,':':.145,',':.07}[ch]
  if (i,j) in [(1,21),(4,22),(4,25)]:gap=.32
  low=int(a['last']*sr); high=int(n['first']*sr)
  if high<=low+2:continue
  mid=(low+high)//2
  cut=low+np.argmin(env[low:high]+.003*np.abs(np.arange(low,high)-mid)/max(1,high-low))
  l=r=cut
  while l>low and env[l-1]<.014:l-=1
  while r<high and env[r]<.014:r+=1
  existing=(r-l)/sr; add=round((gap-existing)*sr)
  if add<0:
   trim=min(-add,max(0,r-l-int(.065*sr)));pos=(l+r-trim)//2;edits.append((pos,pos+trim,0))
  else:
   if env[cut]>.035:add=min(add,int(.09*sr))
   edits.append((cut,cut,add))
 pieces=[];prev=0
 for l,r,n in edits:
  part=x[prev:l].copy();fade=min(int(.003*sr),len(part))
  if fade:part[-fade:]*=np.linspace(1,0,fade)
  pieces.extend([part,np.zeros(n)]);x[r:r+fade]*=np.linspace(0,1,len(x[r:r+fade]));prev=r
 pieces.append(x[prev:]);out=np.concatenate(pieces);wavfile.write(f'ru{i}.wav',sr,np.int16(32767*np.clip(out,-1,1)))
 def adjust(t):return t+sum((n-(r-l))/sr for l,r,n in edits if r/sr<=t)
 times=[]
 for j,a in enumerate(row):
  s=a['first'] if a else next(h['first'] for h in row[j+1:] if h)-.06
  times.append(max(0,adjust(s)-.03))
 times[0]=0.;times=list(np.maximum.accumulate(times))+[len(out)/sr]
 blocks.append(dict(script=words,times=times,duration=len(out)/sr))
 report.append([len(edits),round((len(out)-len(x))/sr,3)])
Path('ru.json').write_text(json.dumps(blocks,ensure_ascii=False))
print(report)
