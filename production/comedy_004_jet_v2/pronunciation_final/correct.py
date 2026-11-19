from pathlib import Path
import subprocess,json,sys
import numpy as np,pyworld as pw
from scipy.ndimage import gaussian_filter1d, map_coordinates
from scipy.signal import butter,sosfilt,resample_poly
from scipy.io.wavfile import read,write
from math import gcd
P=Path('/workspace/jet_v2')
data=json.loads(Path('anchors.json').read_text());keys=list(data);stresses=[2,3,1,5,4,1,4]
def wav(p,sr):
 ar,x=read(p);g=gcd(ar,sr)
 return resample_poly(x.astype(float)/32768,sr//g,ar//g)
def analyze(x,sr):
 f,t=pw.dio(x,sr,f0_floor=60,f0_ceil=520,frame_period=5)
 f=pw.stonemask(x,f,t,sr);s=pw.cheaptrick(x,f,t,sr,f0_floor=60);ap=pw.d4c(x,f,t,sr,fft_size=2*(s.shape[1]-1))
 return t,f,s,ap
def interp_matrix(t,vals,points):
 idx=np.interp(points,t,np.arange(len(t)));lo=idx.astype(int);hi=np.minimum(len(t)-1,lo+1);w=(idx-lo)[:,None]
 return np.ascontiguousarray(vals[lo]*(1-w)+vals[hi]*w)
def editword(x,ref,sr,A,R,k,n):
 # Refine local durations between CTC letter landmarks. The target vowel gains time
 # inside the word; the external word/shot boundaries remain fixed.
 start=int(round((A[0]-.10)*sr));end=int(round((A[-1]+.10)*sr));start=max(0,start);end=min(len(x),end)
 old=x[start:end].copy();off=start/sr;A=np.array(A)-off;R=np.array(R)
 t,f,s,ap=analyze(old,sr);rt,rf,rs,_=analyze(ref,sr)
 # Use both spread and energy to mark lexical stress; soften the other nuclei.
 vowels=[j+1 for j,ch in enumerate(k) if ch in 'аеёиоуыэюя'];peak=n+1
 anchors=np.r_[0,A,len(old)/sr]; lens=np.diff(anchors)
 weights=np.ones_like(lens)
 for j in vowels:
  weights[j:j+2]*=1.40 if j==peak else .87
 lengths=lens[1:-1]*weights[1:-1];lengths*=sum(lens[1:-1])/sum(lengths)
 new=np.r_[0,A[0],A[0]+np.cumsum(lengths),len(old)/sr]
 old_t=np.interp(t,new,anchors);target_t=np.interp(old_t,A,R)
 vo=np.interp(old_t,t,f)>50;of=np.interp(old_t,t[f>50],f[f>50]);rpit=np.interp(target_t,rt[rf>50],rf[rf>50]);active=(t>=A[0])&(t<=A[-1])
 rfmed=np.median(rpit[active]);fbase=np.median(of[active]);pitch=of.copy();pitch[active]=(of[active]**.45)*(fbase*(rpit[active]/rfmed)**.9)**.55
 spectra=interp_matrix(t,np.log(np.maximum(s,1e-13)),old_t)
 rspec=interp_matrix(rt,np.log(np.maximum(rs,1e-13)),target_t)
 refnorm=rspec-rspec.mean(1,keepdims=True);srcnorm=spectra-spectra.mean(1,keepdims=True)
 frequencies=np.linspace(0,sr/2,s.shape[1]);band=np.exp(-((frequencies-1500)/1700)**2)
 for j in vowels:
  center=new[j+1];width=max(.027,min(.085,(new[j+2]-new[j])*.31))
  h=np.exp(-.5*((t-center)/width)**2)*active
  pitch*=2**(h*(2.7 if j==peak else -1.5)/12)
  spectra+=h[:,None]*((.62 if j==peak else -.48)+.48*band*np.clip(refnorm-srcnorm,-2.6,2.6))
 y=pw.synthesize(np.ascontiguousarray(pitch*vo),np.exp(spectra),interp_matrix(t,ap,old_t),sr,frame_period=5)[:len(old)]
 # Smooth transitions around the edit and retain exterior samples verbatim.
 u=np.arange(len(old))/sr
 blend=np.clip((u-A[0]+.015)/.028,0,1)*np.clip((A[-1]-u+.018)/.030,0,1)
 out=old*(1-blend)+y*blend
 x[start:end]=out
sr=24000
mixsr=48000
_,base=read(P/'rumix.wav');master=base.astype(float)/32767;offset=0
for b in range(5):
 raw=wav(P/f'ru{b}.wav',sr);changed=raw.copy()
 for i,k in enumerate(keys):
  item=data[k]
  if item['block']==b:editword(changed,wav(f'ref{i}.wav',sr),sr,item['actual'],item['reference'],k,stresses[i])
 # Use the exact old pause mask, old gain, and frame count.
 orig=np.frombuffer(subprocess.check_output(['ffmpeg','-v','error','-i',str(P/f'ru{b}.wav'),'-ar','48000','-ac','1','-f','f32le','-']),np.float32)
 frame=480;trim=(len(orig)//frame)*frame;silent=np.max(np.abs(orig[:trim].reshape(-1,frame)),axis=1)<.006
 mask=np.ones(len(orig),bool)
 for lo,hi in np.flatnonzero(np.diff(np.r_[False,silent,False])).reshape(-1,2):
  if hi-lo>=34:mask[lo*frame+(0 if lo==0 else 6240):hi*frame-(2640 if lo==0 else 5760)]=False
 filt=butter(2,65,fs=48000,btype='highpass',output='sos');ov=sosfilt(filt,orig[mask]);gain=np.clip(.13/np.sqrt(np.mean(ov[np.abs(ov)>.018]**2)),.84,1.20)
 diff=resample_poly(changed-raw,2,1)[:len(orig)];delta=sosfilt(filt,diff[mask])*gain
 master[offset:offset+len(delta)]+=delta;offset+=len(delta)+6000
assert abs(offset-len(master))<2
write('corrected.wav',48000,(np.clip(master,-.98,.98)*32767).astype(np.int16))
